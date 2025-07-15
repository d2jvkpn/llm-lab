#!/usr/bin/env python3

import gradio as gr

def update_text(choice):
    mapping = {
        "选项A": "你选择了 A，这是对应的文本内容。",
        "选项B": "这是 B 的说明，内容不同。",
        "选项C": "C 是最后一个选项，祝你好运！"
    }
    return mapping.get(choice, "未知选项")


with gr.Blocks() as demo:
    dropdown = gr.Dropdown(choices=["选项A", "选项B", "选项C"], label="请选择一个选项")
    textbox = gr.Textbox(label="显示内容", interactive=True)

    dropdown.change(fn=update_text, inputs=dropdown, outputs=textbox)


demo.launch()
