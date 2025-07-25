# Copyright (c) ARIANNA METHOD

from threading import Thread
from typing import List
from PIL import Image

try:
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore

try:
    import transformers
except Exception:  # pragma: no cover
    transformers = None  # type: ignore

try:
    from transformers import (
        AutoModelForCausalLM,
        StoppingCriteria,
        StoppingCriteriaList,
        TextIteratorStreamer,
    )
except Exception:  # pragma: no cover
    AutoModelForCausalLM = StoppingCriteria = StoppingCriteriaList = TextIteratorStreamer = object  # type: ignore

from Nicole.models import NicoleVLV2Processor as NicoleProcessor, NicoleVLV2ForCausalLM as NicoleForCausalLM
from Nicole.models.conversation import Conversation


def load_model(model_path, dtype=torch.bfloat16):
    vl_chat_processor = NicoleProcessor.from_pretrained(model_path)
    tokenizer = vl_chat_processor.tokenizer

    vl_gpt: NicoleForCausalLM = AutoModelForCausalLM.from_pretrained(
        model_path, trust_remote_code=True, torch_dtype=dtype
    )
    vl_gpt = vl_gpt.cuda().eval()
    return tokenizer, vl_gpt, vl_chat_processor


def convert_conversation_to_prompts(conversation: Conversation):
    conv_prompts = []

    last_image: Image | None = None

    messages = conversation.messages
    for i in range(0, len(messages), 2):

        if isinstance(messages[i][1], tuple):  # type: ignore[misc]
            text, images = messages[i][1]
            if images:
                last_image = images[-1]
        else:
            text = messages[i][1]
            images: List[Image] = []

        prompt = {
            "role": messages[i][0],
            "content": text,
            "images": images
        }
        response = {"role": messages[i + 1][0], "content": messages[i + 1][1]}
        conv_prompts.extend([prompt, response])

    return conv_prompts, last_image


class StoppingCriteriaSub(StoppingCriteria):
    def __init__(self, stops=[], encounters=1):
        super().__init__()
        self.stops = [stop.to("cuda") for stop in stops]

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs
    ):
        for stop in self.stops:
            if input_ids.shape[-1] < len(stop):
                continue
            if torch.all((stop == input_ids[0][-len(stop) :])).item():
                return True

        return False


@torch.inference_mode()
def nicole_generate(
    conversations: list,
    vl_gpt: torch.nn.Module,
    vl_chat_processor: NicoleProcessor,
    tokenizer: transformers.PreTrainedTokenizer,
    stop_words: list,
    max_length: int = 256,
    temperature: float = 1.0,
    top_p: float = 1.0,
    repetition_penalty: float = 1.1,
    chunk_size: int = -1
):
    pil_images = []
    for message in conversations:
        if "images" not in message:
            continue
        pil_images.extend(message["images"])

    prepare_inputs = vl_chat_processor.__call__(
        conversations=conversations,
        images=pil_images,
        inference_mode=True,
        force_batchify=True,
        system_prompt=""
    ).to(vl_gpt.device)

    return generate(
        vl_gpt,
        tokenizer,
        prepare_inputs,
        max_gen_len=max_length,
        temperature=temperature,
        repetition_penalty=repetition_penalty,
        top_p=top_p,
        stop_words=stop_words,
        chunk_size=chunk_size
    )


@torch.inference_mode()
def generate(
    vl_gpt,
    tokenizer,
    prepare_inputs,
    max_gen_len: int = 256,
    temperature: float = 0,
    repetition_penalty=1.1,
    top_p: float = 0.95,
    stop_words: List[str] = [],
    chunk_size: int = -1
):
    """Stream the text output from the multimodality model with prompt and image inputs."""
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True)

    stop_words_ids = [
        torch.tensor(tokenizer.encode(stop_word)) for stop_word in stop_words
    ]
    stopping_criteria = StoppingCriteriaList(
        [StoppingCriteriaSub(stops=stop_words_ids)]
    )

    if chunk_size != -1:
        inputs_embeds, past_key_values = vl_gpt.incremental_prefilling(
            input_ids=prepare_inputs.input_ids,
            images=prepare_inputs.images,
            images_seq_mask=prepare_inputs.images_seq_mask,
            images_spatial_crop=prepare_inputs.images_spatial_crop,
            attention_mask=prepare_inputs.attention_mask,
            chunk_size=chunk_size
        )
    else:
        inputs_embeds = vl_gpt.prepare_inputs_embeds(**prepare_inputs)
        past_key_values = None

    generation_config = dict(
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
        max_new_tokens=max_gen_len,
        do_sample=True,
        use_cache=True,
        streamer=streamer,
        stopping_criteria=stopping_criteria,
    )

    if temperature > 0:
        generation_config.update(
            {
                "do_sample": True,
                "top_p": top_p,
                "temperature": temperature,
                "repetition_penalty": repetition_penalty,
            }
        )
    else:
        generation_config["do_sample"] = False

    thread = Thread(target=vl_gpt.generate, kwargs=generation_config)
    thread.start()

    yield from streamer
