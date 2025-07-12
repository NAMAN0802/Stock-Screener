from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI()

class Financial(BaseModel):
    marketcap: int
class Stock(BaseModel):
    name: str
    industry: str
    financials : Financial


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/stocks/{stock}")
async def stock(stock:str, details: str | None = None,indust:str | None = None):
    return {"stock": stock, "q": details,"indust":indust}