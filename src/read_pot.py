import asyncio

import polib

from translator import Translator, get_client



async def translate_text_entry(text: str, api_key:str):
    with Translator(get_client(api_key)) as translator:
        translated_text = await translator.translate(text)
    return translated_text, {
        "read_tokens": translator.token_usage_prompt,
        "gen_tokens": translator.token_usage_generated,
    }


async def translate_pofile(filepath: str, output_path: str, api_key: str) -> int:
    source_pofile = polib.pofile(filepath)

    translated_pofile = polib.POFile()
    translated_pofile.metadata = source_pofile.metadata

    with Translator(get_client(api_key)) as translator:
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
