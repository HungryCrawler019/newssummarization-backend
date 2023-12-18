from PyPDF2 import PdfReader
import openai
from openai import OpenAI
import time
import json

client = OpenAI(api_key="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")


def read_pdf(file) -> str:
    pdf_file_obj = open(file, 'rb')
    pdf_reader = PdfReader(pdf_file_obj)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page_obj = pdf_reader.pages[page_num]
        text += page_obj.extract_text()
    pdf_file_obj.close()
    return text


def summarize(text: str, type: 0, length_type: 0) -> str:
    try:
        if length_type == 0:
            length_prompt = ""
            max_tokens = 400
        else:
            length_prompt = "very long"
            max_tokens = 1200

        # News
        if type == 0:
            instruction = f"Generate a {length_prompt} summarization of this article into news article, add an attractive headline, and mention in your summary that the article was published in the New York Post, for example by saying \"…, the New York Post reported.\" "
        elif type == 1:
            instruction = f"Generate a {length_prompt} summarization of this article about the judgment. You must add a headline that reads \"..., the Court ruled\""
        elif type == 2:
            instruction = f"Generate a {length_prompt} summarization of this article into news article, about the study, and add a headline that reads \"..., study shows\""
            
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                # {"role": "user", "content": f"Generate a very long summarization of the text.\n ------ \n {text} \n ------"},
                {"role": "user", "content": f"{instruction}\n ------ \n {text} \n ------"},
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except openai.RateLimitError as e:
        # Handle rate limit error (we recommend using exponential backoff)
        print(f"OpenAI API request exceeded rate limit: {e}")
        return ""


def translate(text: str, language: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "user", "content": f"Translate the text into {language}.\n ------ \n {text} \n ------"},
            ],
        )
        return response.choices[0].message.content
    except openai.RateLimitError as e:
        # Handle rate limit error (we recommend using exponential backoff)
        print(f"OpenAI API request exceeded rate limit: {e}")
        return ""


def detect_languages(text: str) -> str:
    try:
        sample_output1 = {"languages": ["English", "Ukrainian"]}
        sample_output2 = {"languages": ["French", "Germany"]}
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "user", "content": f"""
This is summary of the judgement.
------
{text}
------
Which country is this judgment against? In which country did the event happen? Which country is the applicant from?
List official languages in those countries and return them as array of strings in JSON format.

This is sample outputs:

Output 1.
{json.dumps(sample_output1)}

Output 2.
{json.dumps(sample_output2)}
"""},
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        # Handle rate limit error (we recommend using exponential backoff)
        print(f"OpenAI error: {e}")
        return ""


start = time.time()
text = read_pdf('./data/CASE OF BELTSIOS v. GREECE.pdf')
summary = summarize(text=text, length_type=1, type=1)
print(summary)
# languages = detect_languages(text=summary)
# print(languages)
# print(translate(summary, "French"))
end = time.time()
print(f"elapsed time: {end - start}")
