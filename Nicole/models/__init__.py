try:
    from .modeling_nicole_vl_v2 import NicoleVLV2ForCausalLM
    from .processing_nicole_vl_v2 import NicoleVLV2Processor
except Exception:  # pragma: no cover
    NicoleVLV2Processor = NicoleVLV2ForCausalLM = object  # type: ignore

__all__ = [
    "NicoleVLV2Processor",
    "NicoleVLV2ForCausalLM",
]
