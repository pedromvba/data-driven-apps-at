from pydantic import BaseModel
 
class MatchSummaryModel(BaseModel):
    match_id: int
    player_name: str
    
class MatchSummaryResponseModel(BaseModel):
    profile: str