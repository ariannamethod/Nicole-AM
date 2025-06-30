# Copyright (c) 2025 Arianna Method

# check if python version is above 3.10
import sys

if sys.version_info >= (3, 10):
    print("Python version is above 3.10, patching the collections module.")
    # Monkey patch collections
    import collections
    import collections.abc

    for type_name in collections.abc.__all__:
        setattr(collections, type_name, getattr(collections.abc, type_name))
