import asyncio
import json
from typing import List
import pandas as pd
import polib
import tiktoken
from dotenv import load_dotenv
from loguru import logger
from openai import AsyncOpenAI, RateLimitError
from typing_extensions import Self
from prompt import translator_prompt
import time


def get_client(openai_key: str):
    client = AsyncOpenAI(api_key=openai_key)
    return client


class Translator:
    token_usage_prompt: int
    token_usage_generated: int
    n_api_requests: int
    MAX_TOKENS_PER_REQUEST: int = 4096
    time: int

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

        logger.info(f"Translator initialized with model: {self.model}")

    def _set_glossary(self, glossary_path: str):
        logger.info(f"Loading glossary from {glossary_path}")
        glossary = (
            pd.read_csv(glossary_path, index_col=0, usecols=[0, 1])
            .dropna()
            .to_string(formatters={"UKR": "- {}".format})
        )
        self.glossary = glossary
        logger.info("Glossary loaded successfully")

    def __enter__(self) -> Self:
        self.token_usage_prompt = 0
        self.token_usage_generated = 0
        self.n_api_requests = 0
        self.time = time.time()
        logger.info("Translation session started")
        return self

    def __exit__(self, *args):
        logger.info(
            f"Translation session ended. Requests made: {self.n_api_requests}, "
            f"Tokens read: {self.token_usage_prompt}, "
            f"Tokens generated: {self.token_usage_generated}"
            f"Time taken: {(time.time()-self.time):2f} seconds"
        )
        
    async def translate(self, text: str) -> None | str:
        print("got text ",text)
        messages = [
            {"role": "system", "content": self.prompt.format(glossary=self.glossary)},
            {"role": "user", "content": text},
        ]
         
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=300,
            )
            print(text, "\n",response.choices[0].message.content, "\n$$$$$$$$$$$$$$$$$$$")
            self.n_api_requests += 1
            self.token_usage_prompt += response.usage.prompt_tokens
            self.token_usage_generated += response.usage.completion_tokens
        
            return response.choices[0].message.content
        except:
            logger.error(f"FAILED TO GET RESPONSE. \nInput: {text} \nContent: {response}")
        return None
    
    async def translate_batch(self, texts: List[str]) -> List[str]:
        """Translate a batch of texts."""
        logger.info(f"Translating a batch of {len(texts)} texts")

        translated_texts = []

        for text in texts:
            messages = [
                {"role": "system", "content": self.prompt.format(glossary=self.glossary)},
                {"role": "user", "content": text},
            ]

            try:
                # Translate each message individually
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=300,
                )

                # Extract the translated message
                translated_text = response.choices[0].message.content
                translated_texts.append(translated_text)

                # Track token usage
                self.n_api_requests += 1
                self.token_usage_prompt += response.usage.prompt_tokens
                self.token_usage_generated += response.usage.completion_tokens

            except RateLimitError:
                logger.warning("Rate limit exceeded. Retrying after cooldown...")
                async with self.lock:
                    await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Error during translation: {e}")
                translated_texts.append("ERROR")

        return translated_texts

    async def translate_entry_batch(self, entries: List[polib.POEntry]):
        logger.info(f"Starting translation for a batch of {len(entries)} entries")
        texts = [entry.msgid for entry in entries]
        translated_texts = await self.translate_batch(texts)

        for entry, translated_text in zip(entries, translated_texts):
            entry.msgstr = translated_text
            logger.info(f"Translated entry: '{entry.msgid}' to '{entry.msgstr}'")

        return entries

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
    