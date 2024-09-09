import asyncio
import json

import pandas as pd
import polib
import tiktoken
from dotenv import load_dotenv
from loguru import logger
from openai import AsyncOpenAI, RateLimitError
from typing_extensions import Self

from prompt import translator_prompt

def get_client(openai_key: str):
    client = AsyncOpenAI(api_key=openai_key)
    return client

class Translator:
    token_usage_prompt: int
    token_usage_generated: int
    n_api_requests: int

    def __init__(
        self,
        client: AsyncOpenAI,
        model: str = "gpt-4o-mini",
        prompt: str = translator_prompt,
        spreadsheet_path: str = "https://docs.google.com/spreadsheets/d/1Uu2dv8W4mKegu_EswaXOhtIkOURv5Ixn/export?gid=827914249&format=csv",
    ):
        
        self.model = model
        self.prompt = prompt
        self.glossary = self._set_glossary(spreadsheet_path)
        self.max_retry = 3
        self.lock = asyncio.Lock()
        self.client = client

    def _set_glossary(self, glossary_path: str):
        glossary = (
            pd.read_csv(glossary_path, index_col=0, usecols=[0, 1])
            .dropna()
            .to_string(formatters={"UKR": "- {}".format})
        )
        self.glossary = glossary

    def __enter__(self) -> Self:
        self.token_usage_prompt = 0
        self.token_usage_generated = 0
        self.n_api_requests = 0
        return self

    def __exit__(self, *args):
        logger.info(
            f"Requests made: {self.n_api_requests}, \
            Tokens read: {self.token_usage_prompt}, \
            Tokens generated: {self.token_usage_generated}"
        )

    async def translate(self, text: str) -> None | str:
        print("got text ",text)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self.prompt.format(glossary=self.glossary),
                },
                {"role": "user", "content": text},
            ],
            temperature=0.3,
            max_tokens=300
        )
        print(text, "\n",response.choices[0].message.content, "\n$$$$$$$$$$$$$$$$$$$")
        self.n_api_requests += 1
        self.token_usage_prompt += response.usage.prompt_tokens
        self.token_usage_generated += response.usage.completion_tokens
        try:
            return response.choices[0].message.content
        except:
            logger.error(f"FAILED TO GET RESPONSE. \nInput: {text} \nContent: {response}")
        return None

    async def translate_entry(self, entry: polib.POFile):
        text = entry.msgid
        for _ in range(self.max_retry):
            try:
                if (translated_text := await self.translate(text)) is not None:
                    entry.msgstr = translated_text
                    return entry
            except RateLimitError:
                logger.warning("Rate limit exceeded. Sleeping...")
                async with self.lock:
                    await asyncio.sleep(30)

            logger.warning("Retry.")
        logger.error("Retry limit exceeded")
        entry.msgstr = "ERROR"
        return entry

    def estimate_usage(self, entry: polib.POFile):
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



