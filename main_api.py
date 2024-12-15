from fastapi import FastAPI
from routes.matchSummary import router as matchSummaryRouter
from routes.playerProfile import router as playerProfileRouter

app = FastAPI()

app.include_router(matchSummaryRouter)
app.include_router(playerProfileRouter)


@app.get("/")
async def root():
    return {"message": "Application is running!"}