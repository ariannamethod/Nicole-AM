# Copyright (c) ARIANNA METHOD

import json
from typing import Dict, List

import PIL.Image
import torch
from transformers import AutoModelForCausalLM


def load_pretrained_model(model_path: str):

    from Nicole.models.processing_nicole import NicoleProcessor
    from Nicole.models.modeling_nicole import NicoleForCausalLM

    vl_chat_processor = NicoleProcessor.from_pretrained(model_path)
    tokenizer = vl_chat_processor.tokenizer

    vl_gpt: NicoleForCausalLM = AutoModelForCausalLM.from_pretrained(
        model_path, trust_remote_code=True
    )
    vl_gpt = vl_gpt.to(torch.bfloat16).cuda().eval()

    return tokenizer, vl_chat_processor, vl_gpt


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


def load_json(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
        return data
