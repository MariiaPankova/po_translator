from os import environ, path

import gradio as gr
from loguru import logger

from read_pot import estimate_pofile, translate_pofile, translate_text_entry


async def process_file(api_key: str, input_file: str):
    output_path = path.join(
        path.split(input_file)[0], "UA_translated_" + path.split(input_file)[-1]
    )
    tokens = await translate_pofile(input_file, output_path, api_key)
    logger.info("File finished!")
    return output_path, tokens


async def process_text(api_key: str, input_text: str):
    environ["OPENAI_API_KEY"] = api_key
    translation, tokens = await translate_text_entry(input_text, api_key)
    if translation is None:
        raise gr.Error("Error occured. Please retry.")
    return translation, tokens


with gr.Blocks() as demo:
    with gr.Tab(label="Translate .po file"):
        api_key = gr.Text(label="OpenAI API Key", type="password")
        input_file = gr.File()
        translate_po_button = gr.Button(value="Translate")
        output_file = gr.File()
        tokens = gr.Textbox(label="Tokens Used")

        translate_po_button.click(
            process_file, inputs=[api_key, input_file], outputs=[output_file, tokens]
        )

        estimate_button = gr.Button(value="Estimate")
        estimated_tokens = gr.Text(label="Estimated read usage")
        estimate_button.click(
            estimate_pofile, inputs=[api_key, input_file], outputs=[estimated_tokens]
        )

    with gr.Tab(label="Translate text chunck"):
        api_key = gr.Text(label="OpenAI API Key", type="password")
        input_text = gr.Text(label="Input text for translation")

        translate_text_button = gr.Button(value="Translate")

        output_text = gr.Textbox()
        tokens = gr.Textbox(label="Tokens Used")
        translate_text_button.click(
            process_text, inputs=[api_key, input_text], outputs=[output_text, tokens]
        )


demo.launch(server_name="0.0.0.0")
