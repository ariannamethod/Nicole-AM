import sys
import types

# Stub out heavy dependencies if they are unavailable
if 'torch' not in sys.modules:
    torch_stub = types.ModuleType('torch')

    class DummyTensor:
        def __init__(self, data):
            self.data = data

        def to(self, device):
            return self

        def mean(self, dim=0):
            return self

        def item(self):
            return 0.0

        def unsqueeze(self, dim):
            return self

        def __getitem__(self, idx):
            if isinstance(self.data, list):
                return self.data[idx]
            return self.data

    def tensor(data):
        return DummyTensor(data)

    def cosine_similarity(a, b, dim=0):
        return DummyTensor(1.0)

    torch_stub.tensor = tensor
    torch_stub.cosine_similarity = cosine_similarity
    sys.modules['torch'] = torch_stub

if 'transformers' not in sys.modules:
    transformers_stub = types.ModuleType('transformers')

    class PreTrainedModel:
        pass

    class PreTrainedTokenizer:
        pass

    transformers_stub.PreTrainedModel = PreTrainedModel
    transformers_stub.PreTrainedTokenizer = PreTrainedTokenizer
    sys.modules['transformers'] = transformers_stub

import torch
from Nicole.utils.genesis_nicole import genesis_nicole

class DummyEmbed:
    def __call__(self, ids):
        return torch.tensor(ids)

class DummyModel:
    def __init__(self):
        self.device = 'cpu'

    def generate(self, input_ids, max_new_tokens, temperature, eos_token_id):
        return torch.tensor([[1, 2, 3]])

    def get_input_embeddings(self):
        return DummyEmbed()

class DummyTokenizer:
    eos_token_id = 0

    def apply_chat_template(self, messages, add_generation_prompt=True):
        return ' '.join(m["content"] for m in messages)

    def decode(self, tokens, skip_special_tokens=True):
        return "decoded"

    def encode(self, text):
        return [1, 2, 3]

def test_genesis_nicole_output_structure():
    model = DummyModel()
    tokenizer = DummyTokenizer()
    result = genesis_nicole(model, tokenizer, "hi", iterations=2)
    assert isinstance(result, dict)
    assert set(result.keys()) == {"final_resonance", "layers", "evolution"}
