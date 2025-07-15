#!/usr/bin/env python3
import os, argparse, json # logging
from datetime import datetime
from pathlib import Path
os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = "True"

from src.json_logger import JSONLogger
from src.load_prompts import load_prompt_funcs

# from src.website import webpage_brochure

import yaml, litellm
import gradio as gr

parser = argparse.ArgumentParser(
    description="parse commandline arguments",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument("--config", help="config path", default=Path("configs") / "local.yaml")

parser.add_argument("--host", help="http listening host", default="127.0.0.1")
parser.add_argument("--port", help="http listening port", type=int, default=7871)
#parser.add_argument("--share", help="gradio share", action="store_true")
args = parser.parse_args()


with open(args.config, 'r') as f:
    config = yaml.safe_load(f)

#logging.basicConfig(level=logging.DEBUG)

# print("~~~ llm:", llm)
system_prompt = "You are a helpful assistant that responds in markdown."
model_choices = [f"{v['provider']}/{v['model']}" for v in config['llm_models']]
print(f"--> Model choices: {model_choices}")

parameters = """
temperature: 0.7
max_tokens: 1000
"""

def chat(user_input):
    return user_input.strip()

prompt_funcs = load_prompt_funcs("prompts")
prompt_funcs['chat'] = chat

prompt_funcs_keys = list(prompt_funcs.keys())
prompt_funcs_keys.remove("chat")
prompt_funcs_keys.insert(0, "chat")
print(f"--> Imported prompt_funcs: {prompt_funcs_keys}")


def call_llm(selected_model, messages, parameters):
    provider, model = selected_model.split("/", 1)

    print("--> call_llm: provider={}, model={}, temperature={}, max_tokens={}".format(
        provider, model, parameters['temperature'], parameters['max_tokens'],
    ))

    found = next(
        (v for v in config['llm_models'] if v['provider'] == provider and v['model'] == model),
        None,
    )

    if found.get("hosted_vllm", False) is True:
        provider = "hosted_vllm"

    response = litellm.completion(
        custom_llm_provider=provider, model=model,
        api_base=found['api_base'], api_key=found.get('api_key'),
        messages=messages,
        num_retries=3, timeout=60, stream=True,
        #max_tokens=parameters['max_tokens'], temperature=parameters['temperature'],
        **parameters,
    )

    return response


# company_brochure: https://www.apple.com/
def message_gpt(parameters, system_prompt, selected_model, fn, user_input):
    system_prompt, user_input = system_prompt.strip(), user_input.strip()
    if not user_input:
        yield "No input!"
        return

    try:
        parameters = yaml.safe_load(parameters)
    except Exception as e:
        yield f"Read parameters error: {e}"
        return

    messages = []
    if system_prompt != "":
        messages.append({ "role": "system", "content": system_prompt })

    try:
        prompt = prompt_funcs[fn.strip()](user_input)
    except Exception as e:
        yield f"Generate prompt error: {e}"
        return

    messages.append({ "role": "user", "content": prompt })

    try:
        response = call_llm(selected_model, messages, parameters)
    except Exception as e:
        yield f"Call llm error: {e}"
        return

    reply_content = ""

    for chunk in response:
        delta = chunk.choices[0].delta.content or ""
        reply_content += delta
        yield reply_content

    return


view = gr.Interface(
    title="LLM Lab: A Web UI Built with Gradio",
    #description="......",
    fn=message_gpt,
    inputs=[
        gr.Textbox(
            label=f"LLM parameters(yaml format)", value=parameters.strip(),
            lines=5, max_lines=8,
        ),
        gr.Textbox(label=f"System prompt", value=system_prompt, lines=5, max_lines=8),
        gr.Dropdown(model_choices, label="Select a model", value=model_choices[0]),
        gr.Dropdown(prompt_funcs_keys, label="Function to call", value=prompt_funcs_keys[0]),
        gr.Textbox(label=f"Input", lines=3, max_lines=8),
    ],
    outputs=[
        gr.Textbox(label="Response", lines=30),
    ],
    flagging_mode="manual",         # never, auto, manual
    flagging_options=["No", "Yes"], # only when flagging_mode == "mannual"
    flagging_callback=JSONLogger(keys=[
        "parameters", "system_prompt", "selected_model", "fn",
        "user_input", "reply",
    ]),
)

# https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600^&display=swap
# https://cdnjs.cloudflare.com/ajax/libs/iframe-resizer/4.3.1/iframeResizer.contentWindow.min.js
view.launch(share=False, server_name=args.host, server_port=args.port)
