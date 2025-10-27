from fastapi import FastAPI, HTTPException
from app.database import test_connection
import asyncio
from app.routes import user,template,cv,auth


app = FastAPI(title="Kauza'cv Backend")

@app.on_event("startup")
async def startup_event():
    await test_connection()

app.include_router(user.router)
app.include_router(template.router)
app.include_router(cv.router)
app.include_router(auth.router)

