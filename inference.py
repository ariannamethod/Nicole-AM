# Welcome to Arianna Method

from argparse import ArgumentParser
from typing import List, Dict
import torch
from transformers import AutoModelForCausalLM
import PIL.Image

from Nicole.models import (
    NicoleVLV2Processor as NicoleProcessor,
    NicoleVLV2ForCausalLM as NicoleForCausalLM,
)
from Nicole.serve.app_modules.utils import parse_ref_bbox


def load_pil_images(conversations: List[Dict[str, str]]) -> List[PIL.Image.Image]:
    """
    Args:
        conversations (List[Dict[str, str]]): the conversations with a list of messages. An example is :
            [
                {
                    "role": "User",
                    "content": "<image>\nExtract all information from this image and convert them into markdown format.",
                    "images": ["./examples/table_datasets.png"]
                },
                {"role": "Assistant", "content": ""},
            ]
    Returns:
        pil_images (List[PIL.Image.Image]): the list of PIL images.
    """
    pil_images = []

    for message in conversations:
        if "images" not in message:
            continue

        for image_path in message["images"]:
            pil_img = PIL.Image.open(image_path)
            pil_img = pil_img.convert("RGB")
            pil_images.append(pil_img)

    return pil_images


def main(args):

    dtype = torch.bfloat16

    # specify the path to the model
    model_path = args.model_path
    nicole_chat_processor: NicoleProcessor = NicoleProcessor.from_pretrained(model_path)
    tokenizer = nicole_chat_processor.tokenizer

    nicole_gpt: NicoleForCausalLM = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=dtype
    )
    nicole_gpt = nicole_gpt.cuda().eval()

    # multiple images conversation example
    # Please note that <|grounding|> token is specifically designed for the grounded caption feature. It is not needed for normal conversations.
    conversation = [
        {
            "role": "<|User|>",
            "content": "<image>\n<image>\n<|grounding|>In the first image, an object within the red rectangle is marked. Locate the object of the same category in the second image.",
            "images": [
                "images/incontext_visual_grounding_1.jpeg",
                "images/icl_vg_2.jpeg"
            ],
        },
        {"role": "<|Assistant|>", "content": ""},
    ]

    # load images and prepare for inputs
    pil_images = load_pil_images(conversation)
    print(f"len(pil_images) = {len(pil_images)}")

    prepare_inputs = nicole_chat_processor.__call__(
        conversations=conversation,
        images=pil_images,
        force_batchify=True,
        system_prompt=""
    ).to(nicole_gpt.device, dtype=dtype)

    with torch.no_grad():

        if args.chunk_size == -1:
            inputs_embeds = nicole_gpt.prepare_inputs_embeds(**prepare_inputs)
            past_key_values = None
        else:
            # incremental_prefilling when using 40G GPU for nicole-small
            inputs_embeds, past_key_values = nicole_gpt.incremental_prefilling(
                input_ids=prepare_inputs.input_ids,
                images=prepare_inputs.images,
                images_seq_mask=prepare_inputs.images_seq_mask,
                images_spatial_crop=prepare_inputs.images_spatial_crop,
                attention_mask=prepare_inputs.attention_mask,
                chunk_size=args.chunk_size
            )

        # run the model to get the response
        outputs = nicole_gpt.generate(
            inputs_embeds=inputs_embeds,
            input_ids=prepare_inputs.input_ids,
            images=prepare_inputs.images,
            images_seq_mask=prepare_inputs.images_seq_mask,
            images_spatial_crop=prepare_inputs.images_spatial_crop,
            attention_mask=prepare_inputs.attention_mask,
            past_key_values=past_key_values,

            pad_token_id=tokenizer.eos_token_id,
            bos_token_id=tokenizer.bos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            max_new_tokens=512,

            do_sample=True,
            temperature=0.4,
            top_p=0.9,
            repetition_penalty=1.1,

            use_cache=True,
        )

        answer = tokenizer.decode(outputs[0][len(prepare_inputs.input_ids[0]):].cpu().tolist(), skip_special_tokens=False)
        print(f"{prepare_inputs['sft_format'][0]}", answer)

        vg_image = parse_ref_bbox(answer, image=pil_images[-1])
        if vg_image is not None:
            vg_image.save("./vg.jpg", format="JPEG", quality=85)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True,
                        default="ariannamethod/nicole",
                        help="model name or local path to the model")
    parser.add_argument("--chunk_size", type=int, default=-1,
                        help="chunk size for the model for prefiiling. "
                             "When using 40G gpu for nicole-small, set a chunk_size for incremental_prefilling."
                             "Otherwise, default value is -1, which means we do not use incremental_prefilling.")
    args = parser.parse_args()
    main(args)
