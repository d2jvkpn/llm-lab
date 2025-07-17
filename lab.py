#!/usr/bin/env python3
import os, argparse # json, logging
# from datetime import datetime
from pathlib import Path
os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = "True"

from src.loggers import LabLogger
from src import llm_prompts
# from src.website import webpage_brochure

import yaml, litellm
import gradio as gr


#### 1.
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


#### 2.
# print("~~~ llm:", llm)
system_prompt = "You are a helpful assistant that responds in markdown."
model_choices = [f"{v['provider']}/{v['model']}" for v in config['llm_models']]
print(f"--> Model choices: {model_choices}")

parameters = """
temperature: 0.7
max_tokens: 1000
"""

prompt_funcs = llm_prompts.load("llm_prompts")
prompt_funcs['default'] = lambda user_input: user_input.strip()

prompt_funcs_keys = list(prompt_funcs.keys())
prompt_funcs_keys.remove("default")
prompt_funcs_keys.insert(0, "default")
print(f"--> Imported prompt_funcs: {prompt_funcs_keys}")


#### 3.
def call_llm(selected_model, messages, parameters):
    provider, model = selected_model.split("/", 1)
    print("--> call_llm: provider={}, model={}, parameters={}, content: {}".format(
        provider, model, parameters, repr(messages[-1]['content']),
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
        num_retries=3, timeout=60, stream=True, **parameters,
        #max_tokens=parameters['max_tokens'], temperature=parameters['temperature'],
    )

    return response


# company_brochure: https://www.apple.com/
def message_gpt(system_prompt, selected_model, yaml_text, fn, user_input):
    system_prompt = system_prompt.strip()
    user_input = user_input.strip()

    if not user_input:
        yield "no input!"
        return

    try:
        parameters = yaml.safe_load(yaml_text)
    except Exception as e:
        yield f"read parameters error: {e}"
        return

    messages = []
    if system_prompt:
        messages.append({ "role": "system", "content": system_prompt })

    try:
        prompt = prompt_funcs[fn.strip()](user_input)
    except Exception as e:
        yield f"generate prompt error: {e}"
        return

    messages.append({ "role": "user", "content": prompt })

    try:
        response = call_llm(selected_model, messages, parameters)
    except Exception as e:
        yield f"call llm error: {e}"
        return

    reply_content = ""

    for chunk in response:
        delta = chunk.choices[0].delta.content or ""
        reply_content += delta
        yield reply_content

    return


### 4.
view = gr.Interface(
    title="LLM Lab: A Web UI Built with Gradio",
    #description="......",
    fn=message_gpt,
    inputs=[
        gr.Textbox(label="System prompt", value=system_prompt, lines=6, max_lines=10),
        gr.Dropdown(model_choices, label="Select a model", value=model_choices[0]),
        gr.Textbox(
            label="LLM parameters(yaml format)", value=parameters.strip(),
            lines=4, max_lines=8,
        ),
        gr.Dropdown(
            prompt_funcs_keys, label="User prompt(llm_prompts/*.py)",
            value=prompt_funcs_keys[0],
        ),
        gr.Textbox(label="Input", lines=2, max_lines=8),
    ],
    outputs=[
        gr.Textbox(label="Response", lines=28),
    ],
    flagging_mode="manual",         # never, auto, manual
    flagging_options=["No", "Yes"], # only when flagging_mode == "mannual"
    flagging_callback=LabLogger(keys=[
        "system_prompt", "selected_model", "yaml_text", "fn",
        "user_input", "reply",
    ]),
)

# https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600^&display=swap
# https://cdnjs.cloudflare.com/ajax/libs/iframe-resizer/4.3.1/iframeResizer.contentWindow.min.js
view.launch(share=False, server_name=args.host, server_port=args.port)
