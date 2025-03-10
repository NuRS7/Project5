from fastapi import FastAPI
from .routes import books
from .models import Base
from app.database import engine
app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(books.router)

