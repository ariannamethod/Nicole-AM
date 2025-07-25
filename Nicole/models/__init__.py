try:
    from .processing_nicole_vl_v2 import NicoleVLV2Processor
    from .modeling_nicole_vl_v2 import NicoleVLV2ForCausalLM
    from .modeling_nicole import NicoleV2ForCausalLM
except Exception:  # pragma: no cover
    NicoleVLV2Processor = NicoleVLV2ForCausalLM = NicoleV2ForCausalLM = object  # type: ignore

__all__ = [
    "NicoleVLV2Processor",
    "NicoleVLV2ForCausalLM",
    "NicoleV2ForCausalLM",
]
