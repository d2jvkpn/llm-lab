#!/usr/bin/env python3
import os, glob, importlib
from typing import Dict, List

def load(directory="llm_tools") -> Dict[str, List]:
    tool_functions = {}
    
    if not os.path.exists(directory):
        raise FileNotFoundError(f"{directory} not exists")
    
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory} is not a diretory")

    pattern = os.path.join(directory, "*.py")
    module_files = glob.glob(pattern)
    
    for filepath in module_files:
        name = os.path.basename(filepath)[:-3]

        module = importlib.import_module(f"{directory}.{name}")

        if hasattr(module, "definiton") and hasattr(module, "assistant"):
            definiton = getattr(module, "definiton")
            assistant = getattr(module, "assistant")
            tool_functions[name] = (definiton, assistant)
        else:
           err_msg = f"can't find function definiton and assistant in {filepath}"
           raise AssertionError(err_msg)

    return tool_functions
