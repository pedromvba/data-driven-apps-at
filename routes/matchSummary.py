# imports
import json
from fastapi import APIRouter
from services.matches import *

# APIRouter instance
router = APIRouter()

@router.get('/match_summary')
def get_summary(match_id:int):
    return summarizer(match_id)

