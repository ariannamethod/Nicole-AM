from typing import Dict

import torch
from transformers import PreTrainedModel, PreTrainedTokenizer


def genesis_nicole(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    initial_prompt: str,
    *,
    iterations: int = 3,
    temperature: float = 0.8,
    max_new_tokens: int = 150,
    resonance_threshold: float = 0.7,
) -> Dict[str, float]:
    """Apply a recursive resonance loop to refine Nicole's response."""

    messages = [{"role": "user", "content": initial_prompt}]
    resonances = []
    prev_output = None
    sim = 0.0
    for layer in range(iterations):
        prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
        input_ids = torch.tensor([prompt]).to(model.device)
        completion = model.generate(
            input_ids=input_ids,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            eos_token_id=tokenizer.eos_token_id,
        )[0]
        output = tokenizer.decode(completion, skip_special_tokens=True)
        resonances.append(output)

        if prev_output is not None:
            embed = model.get_input_embeddings()
            vec_prev = embed(
                torch.tensor(tokenizer.encode(prev_output)).to(model.device)
            ).mean(0)
            vec_curr = embed(
                torch.tensor(tokenizer.encode(output)).to(model.device)
            ).mean(0)
            sim = torch.cosine_similarity(vec_prev, vec_curr, dim=0).item()
            if sim > resonance_threshold:
                break

        mutate_prompt = f"{initial_prompt}\nPrevious echo: {output}\nResonate deeper: Rethink with paradox/glitch twist."
        messages = [{"role": "user", "content": mutate_prompt}]
        prev_output = output

    return {
        "final_resonance": resonances[-1],
        "layers": len(resonances),
        "evolution": sim,
    }
