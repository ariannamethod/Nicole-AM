import sys
import types

# Provide stubs for missing heavy dependencies
if "torch" not in sys.modules:
    torch_stub = types.ModuleType("torch")

    class DummyTensor:
        def __init__(self, data):
            self.data = data

        def to(self, device):
            return self

        def mean(self, dim=0):
            return self

        def item(self):
            return 0.0

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
    sys.modules["torch"] = torch_stub

if "transformers" not in sys.modules:
    transformers_stub = types.ModuleType("transformers")

    class PreTrainedModel:
        pass

    class PreTrainedTokenizer:
        pass

    transformers_stub.PreTrainedModel = PreTrainedModel
    transformers_stub.PreTrainedTokenizer = PreTrainedTokenizer
    sys.modules["transformers"] = transformers_stub

import importlib.util
from pathlib import Path

conversation_path = (
    Path(__file__).resolve().parents[1] / "Nicole" / "models" / "conversation.py"
)
spec = importlib.util.spec_from_file_location("conversation", conversation_path)
conversation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conversation)
Conversation = conversation.Conversation


def test_apply_genesis_filter_updates_message(monkeypatch):
    conv = Conversation(name="test", roles=["user", "assistant"])
    conv.messages = [["user", "hello"], ["assistant", "reply"]]

    called = {}

    def fake_genesis(model, tokenizer, message, **kwargs):
        called["args"] = (model, tokenizer, message)
        return {"final_resonance": "filtered", "layers": 1, "evolution": 0.0}

    monkeypatch.setattr(conversation, "genesis_nicole", fake_genesis)

    model = object()
    tokenizer = object()

    result = conv.apply_genesis_filter(model, tokenizer, iterations=1)
    assert result["final_resonance"] == "filtered"
    assert conv.messages[-1][1] == "filtered"
    assert called["args"] == (model, tokenizer, "reply")
