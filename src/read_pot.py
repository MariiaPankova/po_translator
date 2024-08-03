import polib
from openai import AsyncOpenAI
from prompt import translator_prompt
from dotenv import load_dotenv
import asyncio
import json
import tiktoken
import pandas as pd

load_dotenv()

async def translate_pofile(filepath: str, output_path: str) -> int:
    translator = Translator()
    source_pofile = polib.pofile(filepath)

    translated_pofile = polib.POFile()
    translated_pofile.metadata = source_pofile.metadata

    translated_pofile.extend(
        (
            await asyncio.gather(
                *(translator.translate_entry(entry) for entry in source_pofile)
            )
        )
    )
    translated_pofile.save(output_path)
    return {
        "read_tokens": translator.token_usage_prompt,
        "gen_tokens": translator.token_usage_generated,
    }


class Translator:
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        prompt: str = translator_prompt,
        spreadsheet_path: str = "https://docs.google.com/spreadsheets/d/1Uu2dv8W4mKegu_EswaXOhtIkOURv5Ixn/export?gid=827914249&format=csv",
    ):
        self.client = AsyncOpenAI()
        self.model = model
        self.prompt = prompt
        self.token_usage_prompt = 0
        self.token_usage_generated = 0
        self.glossary = self._set_glossary(spreadsheet_path)
        self.max_retry = 2

    def _set_glossary(self, glossary_path):
        glossary = (
            pd.read_csv(glossary_path, index_col=0, usecols=[0, 1])
            .dropna()
            .to_string(formatters={"UKR": "- {}".format})
        )
        self.glossary = glossary

    async def translate_entry(self, entry):
        text = entry.msgid
        for _ in range(self.max_retry):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.prompt.format(glossary=self.glossary),
                    },
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
            translate = json.loads(response.choices[0].message.content)
            if translate.get("final_translation") is not None:
                break
            print("None occured, retry")
            entry.msgstr = translate.get("final_translation")
        self.token_usage_prompt += response.usage.prompt_tokens
        self.token_usage_generated += response.usage.completion_tokens
        return entry

    def estimate_usage(self, entry):
        encoding = tiktoken.encoding_for_model(self.model)
        text = entry.msgstr
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": text},
        ]
        tokens_per_message = 4
        tokens_per_name = 1
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens


if __name__ == "__main__":
    # print(asyncio.run(get_translation("If we want this pattern to continue (and we do!), then $5^0$ must be $1$.")))
    print(
        asyncio.run(
            translate_pofile(
                "data/worst_cases.po",
                "data/test_translate2.po",
            )
        )
    )
    translator = Translator()
    # translator.estimate_usage()
