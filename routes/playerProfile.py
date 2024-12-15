import json
from fastapi import APIRouter
from services.playerStats import *

# APIRouter instance
router = APIRouter()


@router.get('/player_profile')
def get_profile(match_id:int, player_name:str):
    player_df = player_events(match_id, player_name)
    return player_df.to_dict(orient='records')
