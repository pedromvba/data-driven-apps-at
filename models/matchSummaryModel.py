from pydantic import BaseModel
 
class MatchSummaryModel(BaseModel):
    match_id: int
    
class MatchSummaryResponseModel(BaseModel):
    summary: str
