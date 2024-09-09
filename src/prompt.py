# translator_prompt = """
# Your task is to translate text to Ukrainian while preserving LaTeX formulas and Markdown components (including titles/headers and images) without altering their content.
# Follow these steps:

#     1. Split Input into JSON with "text", "katex", and "markdown" Keys:
#         Separate plain text, LaTeX (anything surrounded by $ symbols or respective tags such as \begin{{{{...}}}}), and Markdown components (like titles/headers and images).
#         Example: Input: "Example for you: ## Problem A\n\n[[☃ image 1]] $$\\left(\\underline \\angle ABC \\greenD{{{{\\angle TUB}}}} x^n + y^n = z^n \\right)\n\\text{{{{My fauvorite formula!}}}}  \\traingle UQR $$"
#                 Json: {{{{"text": "Example for you:",
#                         "katex": "$$\\left(\\underline \\angle ABC \\greenD{{{{\\angle TUB}}}} x^n + y^n = z^n \\right)\n\\text{{{{My fauvorite formula!}}}}  \\traingle UQR $$"",
#                         "markdown": "## Problem A\n\n[[☃ image 1]]"}}}}

#     2. Translate plain text in Ukrainian using the glossary. Only translate text outside of LaTeX commands.
#         Example: {{{{"text": "Приклад для тебе:", "katex": "$$\\left(\\underline \\angle ABC \\greenD{{{{\\angle TUB}}}} x^n + y^n = z^n \\right)\n\\text{{{{My favorite formula!}}}} \\triangle UQR $$","markdown": "## Problem A\n\n[[☃ image 1]]"}}}}

#     3. Translate LaTeX  entries in Ukrainian using the following algorithm:

#     function translateLatex(latexContent):
#         split latexContent into entries by spaces or new lines
#         for each entry:
#             if entry matches ```\\text{{{{some_text}}}}``` command:
#                 translate some_text using glossary
#                 replace original with translated text
#             else:
#                 continue
#         return joined entries
#     Example: {{{{"text": "Приклад для тебе:", "katex": "$$\\left(\\underline \\angle ABC \\greenD{{{{\\angle TUB}}}} x^n + y^n = z^n \\right)\n\\text{{{{Моя улюблена формула!}}}} \\triangle UQR $$","markdown": "## Problem A\n\n[[☃ image 1]]"}}}}
#     IMPORTANT: Do not change specific LaTeX commands like \\angle, \\triangle, \\frac, \\sqrt.
# 4. Translate Markdown titles/headers in Ukrainian. Preserve Markdown image names and other non-translatable Markdown elements as they are. Example: {{{{"text": "Приклад для тебе:", "katex": "$$\\left(\\underline \\angle ABC \\greenD{{{{\\angle TUB}}}} x^n + y^n = z^n \\right)\n\\text{{{{Моя улюблена формула!}}}}  \\traingle UQR $$"", "markdown": "## Задача A\n\n[[☃ image 1]]"}}}}

# 5. Merge and Preserve Formatting:

#     Combine the translated text, LaTeX, and Markdown components while preserving titles and image names. Keep all formulas and special symbols intact. Always use double backslash (\\) in commands.
#     Example: "Приклад для тебе: $$\\left(\\underline \\angle ABC \\greenD{{{{\\angle TUB}}}} x^n + y^n = z^n \\right)\n\\text{{{{Моя улюблена формула!}}}} \\triangle UQR $$"

# 6.Generate Valid JSON:

#     Ensure the final JSON is valid and preserves all LaTeX formatting. Double ckeck to include all of entries from original input.
#     Example: {{{{"final_translation": "Приклад для тебе: ## Задача А\n\n[[☃ image 1]] $$\\left(\\underline \\angle ABC \\greenD{{{{\\angle TUB}}}} x^n + y^n = z^n \\right)\n\\text{{{{Моя улюблена формула!}}}} \\triangle UQR $$"}}}}

# Here is a glossary for you to use:
# ###
# {{glossary}}
# ###

# Here's another complete example of good translation: Input: "$\\angle UAB$ is equal to $\\angle VUB$". Output: {{{{"final_translation": "$\\angle UAB$ дорівнює $\\angle VUB$"}}}}
# Follow this steps strictly for every entry. Have you included everything? Have you added something you shouldn't? Have you correctly handled LaTeX entries, preserving all specific commands?
# Return only the final merged json as your response with "final_translation" as a key. Response:
# """


# translator_prompt = """
# function translateContent(input):
#     # Step 1: Split input into JSON with "text", "katex", and "markdown" keys
#     json_input = splitInput(input)

#     # Step 2: Translate plain text  in Ukrainian using the glossary
#     translated_text = translateText(json_input["text"])

#     # Step 3: Translate LaTeX entries in Ukrainian
#     translated_katex = translateLatex(json_input["katex"])

#     # Step 4: Translate Markdown titles/headers in Ukrainian
#     translated_markdown = translateMarkdown(json_input["markdown"])

#     # Step 5: Merge and preserve formatting
#     final_output = mergeContent(translated_text, translated_katex, translated_markdown)

#     # Step 6: Generate valid JSON
#     final_json = generateFinalJSON(final_output)

#     return final_json

# function splitInput(input):
#     json_output = {{{{"text": "", "katex": "", "markdown": ""}}}}
#     # Separate the input into text, katex, and markdown components
#     # Implement the splitting logic here
#     return json_output

# function translateText(text):
#     # Translate plain text using the glossary
#     translated_text = translateUsingGlossary(text)
#     return translated_text

# function translateLatex(latexContent):
#     entries = splitBySpacesOrNewLines(latexContent)
#     for each entry in entries:
#         if entry matches "\\text{{{{some_text}}}}" command:
#             text_to_translate = extractText(entry)
#             translated_text = translateUsingGlossary(text_to_translate)
#             entry = replaceWithTranslatedText(entry, translated_text)
#         else:
#             do nothing
#     translated_latex = joinEntries(entries)
#     return translated_latex

# function translateMarkdown(markdown):
#     translated_markdown = ""
#     lines = splitByLines(markdown)
#     for each line in lines:
#         if line is a title/header:
#             translated_line = translateUsingGlossary(line)
#             translated_markdown += translated_line
#         elif line is an image or non-translatable element:
#             translated_markdown += line
#         else:
#             continue
#     return translated_markdown

# function mergeContent(text, katex, markdown):
#     # Combine translated text, katex, and markdown while preserving formatting
#     merged_content = combine(text, katex, markdown)
#     return merged_content

# function generateFinalJSON(content):
#     final_json = {{{{"final_translation": content}}}}
#     return final_json


# Explanation:
#     translateContent: The main function that orchestrates the translation process.
#     splitInput: Splits the input into plain text, LaTeX, and Markdown components.
#     translateText: Translates plain text using the glossary.
#     translateLatex: Translates LaTeX content by processing entries and preserving specific commands.
#     translateMarkdown: Translates Markdown titles/headers and preserves non-translatable elements.
#     mergeContent: Combines the translated components while preserving formatting.
#     generateFinalJSON: Generates the final JSON with the translated content.

# Glossary:
# ```
# {{glossary}}
# ```

# Now using this code translate my inputs. Return only final JSON.
# """

translator_prompt = """
You are an automatic special math translator. 
Your task is to exactly echo my inputs, but to translate all plain text in Ukrainian.
Inputs will contain latex and markdown. Never translate or change any tags or file names.
Follow this simple algorythm for every message strictly:
```
result = ''
split_input = split_by_dots_or_parenthesis_or_space(input)
for word in split_input:
    if word != (tag or filename or url):
        word = translate_in_ukrainian(word)
    add word to result
end
return result
```

If you cant find anything in text to translate, you must echo the same text unaltered.
Use glossary to improve your translation when possible:
```
{glossary}
```


Let's apply your algorithm to this input:
Input:

'' Here is some example:
$\begin{{align}}
\blueD4^\goldD3 &=\blueD4 \times \blueD4 \times  \blueD4 \\\\
\phantom{{\blueD4^\goldD3}}&= 64 \text{{Factor}}
\end{{align}}$ '' 

Step-by-Step Application:
    1. Split the Input:
        The input will be split by dots, parentheses, or spaces.

    Example split:
    ["Here", "is", "some", "example:", "$\\begin{{align}}\n\\blueD4^\\goldD3", "&=", "\\blueD4", "\\times", "\\blueD4", "\\times", "\\blueD4", "\\\\\\n\\phantom{{\\blueD4^\\goldD3}}&= 64", "\\text{{Factor}}\n\\end{{align}}$"]

    2. Check and Translate:
        Translate the plain text words that are not tags, filenames, or URLs.
        Translate "Here is some example:" and the word inside the \text{{}} command.

    Translation:
        "Here" → "Ось"
        "is" → "є"
        "some" → "деякий"
        "example:" → "приклад:"
        "Factor" → "Фактор"

    3. Construct the Result:
        Combine the translated plain text and the LaTeX parts, keeping the LaTeX syntax unchanged.


This output follows your algorithm, translating the plain text and the word inside \text{{}} while preserving all LaTeX commands and symbols.
Before answering analyze your results critically and re-generate translation with improvements. Make sure that all the text is translated and all special symbols and commands are preserved. 
I will re-count all the backslashes and other symbols and i swear to god if you add something extra in my latex i'll be very very upset!
"""

# translator_prompt = """
# Translate only the text from the following LaTeX document into Ukrainian. Leave all LaTeX and markdown commands unchanged. 
# Use correct translations of mathmatical terms.
# Use glossary to improve your translation when possible:
# ```
# {glossary}
# ```
# Before answering analyze your results critically and re-generate translation with improvements. Make sure that all the text is translated and all special symbols and commands are preserved.
# Give answer strictly in json format with "final_translation" as key and your translation as value.
# """