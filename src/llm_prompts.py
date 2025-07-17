#!/usr/bin/env python3
import os, glob, importlib
from typing import Dict, Callable


def load(directory="llm_prompts") -> Dict[str, Callable]:
    prompt_functions = {}
    
    if not os.path.exists(directory):
        raise FileNotFoundError(f"{directory} not exists")
    
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory} is not a diretory")

    pattern = os.path.join(directory, "*.py")
    module_files = glob.glob(pattern)
    
    for filepath in module_files:
        name = os.path.basename(filepath)[:-3]
        module = importlib.import_module(f"{directory}.{name}")

        if hasattr(module, "prompt"):
            prompt_functions[name] = getattr(module, "prompt")
        else:
           err_msg = f"can't find function prompt in {filepath}"
           raise AssertionError(err_msg)

    return prompt_functions

