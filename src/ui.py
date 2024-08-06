import gradio as gr
from read_pot import translate_pofile, estimate_pofile
from os import environ, path


async def process_file(api_key, input_file):
    environ["OPENAI_API_KEY"] = api_key
    output_path = path.join(path.split(input_file)[0], "UA_translated_" + path.split(input_file)[-1])
    tokens = await translate_pofile(input_file, output_path)
    return output_path, tokens

#TODO: add button to count prompt tokens
#TODO: fix prompt
#TODO: README


input_file = gr.File()
output_file = gr.File()
api_key = gr.Text(label="OpenAI API Key", type="password")
tokens_used = gr.Textbox(label="Token usage: ")

file_for_estimate = gr.File()
estimated_tokens = gr.Textbox(label="Estimated prompt usage: ")


demo = gr.Interface(
    fn=process_file,
    inputs=[api_key, input_file],
    outputs=[output_file, tokens_used],
)


demo.launch(server_name="0.0.0.0")