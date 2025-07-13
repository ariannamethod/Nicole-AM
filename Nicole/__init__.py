# Copyright (c) 2025 Arianna Method

"""Nicole package initialization.

This module ensures compatibility with Python 3.10+ by patching the
``collections`` module so that legacy names continue to be available.
The patch is applied only once per interpreter session. Set the environment
variable ``NICOLE_DEBUG_PATCH`` to ``1`` to receive a warning when the patch
is executed.
"""

import os
import sys
import warnings

if sys.version_info >= (3, 10):
    import collections
    import collections.abc

    if not getattr(collections, "_nicole_patched", False):
        for type_name in collections.abc.__all__:
            setattr(collections, type_name, getattr(collections.abc, type_name))
        setattr(collections, "_nicole_patched", True)
        if os.getenv("NICOLE_DEBUG_PATCH"):
            warnings.warn(
                "Python >= 3.10 detected; patched the collections module for backward compatibility.",
                stacklevel=2,
            )
