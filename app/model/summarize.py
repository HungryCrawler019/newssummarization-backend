# models.py
from pydantic import BaseModel
from datetime import datetime
from app.database import db

SummarizeDB = db.summarize

class SummaryHistory(BaseModel):
    text: str
    content: str
    date: datetime


def save_summary_history(summary_history: SummaryHistory):
    return SummarizeDB.insert_one(summary_history.dict())

def get_summary_data():
    return list(SummarizeDB.find({}, {'_id': 0}))