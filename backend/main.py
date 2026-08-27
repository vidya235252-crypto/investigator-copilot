from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import db
from routers import cases, review

app = FastAPI(title="InvestigatorCopilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()

app.include_router(cases.router)
app.include_router(review.router)

@app.get("/")
def root():
    return {"status": "ok", "service": "InvestigatorCopilot"}