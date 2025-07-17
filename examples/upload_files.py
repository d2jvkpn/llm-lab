#!/usr/bin/env python3

import gradio as gr


def chat_fn(user_input, history, files):
    print(f"~~~ user_input={user_input}, history={history}, files={files}")
    return user_input


chat = gr.ChatInterface(
    fn=chat_fn,
    multimodal=True,
    additional_inputs=[
        gr.File(
            label="Upload files",
            file_types=[".pdf", ".txt"],
            file_count="multiple",
            visible=True,
        ),
    ],
    additional_inputs_accordion="📎 Attachments",
)

chat.launch()
