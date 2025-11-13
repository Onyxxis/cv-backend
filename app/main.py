from fastapi import FastAPI, HTTPException
from app.database import test_connection
import asyncio
from app.routes import user,template,cv,auth
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI(title="Kauza'cv Backend")
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",   
    # "https://ton-frontend-vercel.com",   
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=origins,   
    allow_credentials=True,
    allow_methods=["*"],     
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await test_connection()

app.include_router(user.router)
app.include_router(template.router)
app.include_router(cv.router)
app.include_router(auth.router)

