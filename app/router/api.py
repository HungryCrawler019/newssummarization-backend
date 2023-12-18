from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Depends
from sendgrid.helpers.mail import Mail, Email, To, Content
from app.util.sendgrid import sendgrid_client, from_mail
from app.util.openai import client, openai
from app.util.news import getLatestNews
from app.dependency.auth import get_current_user
from app.model.user import User
from datetime import datetime
from PyPDF2 import PdfReader
from app.model.summarize import SummaryHistory, save_summary_history, get_summary_data
import os
import shutil
import json
from typing import List, Annotated
from datetime import datetime

router = APIRouter()


@router.post("/get-content")
async def get_content(user: Annotated[User, Depends(get_current_user)], file: UploadFile = File(...)) -> str:
    print("get-content")
    directory = "./data/upload"
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(f"{directory}/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pdf_file_obj = open(f"./data/upload/{file.filename}", 'rb')

    pdf_reader = PdfReader(pdf_file_obj)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page_obj = pdf_reader.pages[page_num]
        text += page_obj.extract_text()
    pdf_file_obj.close()
    return text

@router.get("/get_summaries/", response_model=List[SummaryHistory])
async def get_summaries(user: Annotated[User, Depends(get_current_user)],):
    try:
        summaries = get_summary_data()
        return summaries
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})

@router.get("/get_news/")
async def get_news(user: Annotated[User, Depends(get_current_user)],):
    try:
        result = getLatestNews()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})

@router.post("/summarize/")
async def summarize(user: Annotated[User, Depends(get_current_user)], text: str = Form(...), type: int = Form(...), length_type: int = Form(...)) -> str:
    try:
        print(text)
        print(type)
        print(length_type)
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
                {"role": "user", "content": f"{instruction}\n ------ \n {text} \n ------"},
            ],
            max_tokens=max_tokens
        )
        content = response.choices[0].message.content
        summary_history = SummaryHistory(
            text=text,
            content=content,
            date=datetime.now()
        )
        save_summary_history(summary_history)
        return content
    except Exception as e:
        print(f"Summarization Error: {e}")
        return HTTPException(status_code=500, detail={"error": e})


@router.post("/detect-language")
async def get_content(user: Annotated[User, Depends(get_current_user)], text: str = Form(...)) -> List[str]:
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
        languages = json.loads(response.choices[0].message.content)
        return languages['languages']
    except Exception as e:
        # Handle rate limit error (we recommend using exponential backoff)
        print(f"Language Detection Error: {e}")
        return HTTPException(status_code=500, detail={"error": e})


@router.post("/translate")
async def get_content(user: Annotated[User, Depends(get_current_user)], text: str = Form(...), language: str = Form(...)) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "user", "content": f"Translate the text into {language}.\n ------ \n {text} \n ------"},
            ],
        )
        return response.choices[0].message.content
    except openai.RateLimitError as e:
        print(f"Translation Error: {e}")
        return HTTPException(status_code=500, detail={"error": e})


@router.post("/send-mail")
async def send_mail(user: Annotated[User, Depends(get_current_user)], text: str = Form(...), to_email: str = Form(...)) -> bool:
    try:
        print(from_mail)
        from_email_obj = Email(from_mail)  # Change to your verified sender
        to_email_obj = To(to_email)  # Change to your recipient
        subject = f"Summarization {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        content = Content("text/plain", text)
        mail = Mail(from_email_obj, to_email_obj, subject, content)

        # Get a JSON-ready representation of the Mail object
        mail_json = mail.get()

        # Send an HTTP POST request to /mail/send
        response = sendgrid_client.client.mail.send.post(
            request_body=mail_json)
        if response.status_code == 202:
            return True
        else:
            return False
    except Exception as e:
        print(f"Send mail Error: {e}")
        # return HTTPException(status_code=500, detail={"error": e})
        return False
