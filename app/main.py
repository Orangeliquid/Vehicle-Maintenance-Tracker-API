import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routes import users, vehicles, maintenance, reminder
from app.models import Base
from app.database import engine


@asynccontextmanager
async def lifespan(app_name: FastAPI):
    print("Server has started.")
    yield
    print("Server has closed.")

app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(vehicles.router)
app.include_router(maintenance.router)
app.include_router(reminder.router)

Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
