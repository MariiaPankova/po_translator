import asyncio
from typing import Dict
from loguru import logger

import polib

from translator import Translator, get_client


async def translate_text_entry(text: str, api_key: str):
    with Translator(get_client(api_key)) as translator:
        translated_text = await translator.translate(text)
    return translated_text, {
        "read_tokens": translator.token_usage_prompt,
        "gen_tokens": translator.token_usage_generated,
    }


async def translate_pofile(filepath: str, output_path: str, api_key: str, batch_size: int = 5) -> dict[str, int]:
    source_pofile = polib.pofile(filepath)
    translated_pofile = polib.POFile()
    translated_pofile.metadata = source_pofile.metadata

    logger.info(f"Starting translation for PO file: {filepath}")

    with Translator(get_client(api_key)) as translator:
        for i in range(0, len(source_pofile), batch_size):
            batch_entries = source_pofile[i:i + batch_size]
            logger.info(f"Translating batch {i//batch_size + 1} with {len(batch_entries)} entries")
            translated_batch = await translator.translate_entry_batch(batch_entries)
            translated_pofile.extend(translated_batch)

    translated_pofile.save(output_path)
    logger.info(f"Translation completed and saved to {output_path}")

    return {
        "read_tokens": translator.token_usage_prompt,
        "gen_tokens": translator.token_usage_generated,
    }



async def estimate_pofile(filepath: str, api_key: str):
    source_pofile = polib.pofile(filepath)
    token_estimate = 0
    for entry in source_pofile:
        token_estimate += Translator(get_client(api_key)).estimate_usage(entry)
    return token_estimate


if __name__ == "__main__":
    # # print(asyncio.run(get_translation("If we want this pattern to continue (and we do!), then $5^0$ must be $1$.")))
    print(
        asyncio.run(
            translate_pofile(
                "/Users/mariiapankova/Documents/projects/po_translator/data/learn.math.calculus-home.articles-uk.po",
                "data/test_translate2.po",
                api_key="sk..."
            )
        )
    )
    # translator.estimate_usage()
