from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.user.router import router as user_router
from src.hobby.router import router as hobby_router
from src.messages.router import router as messages_router
from src.match.router import router as match_router
from src.exceptions import sqlalchemy_exception_handler, generic_exception_handler
from sqlalchemy.exc import SQLAlchemyError

from src.dbTest import init_models, insert_dummy_data

app = FastAPI()

# Register the auth router
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(hobby_router)
app.include_router(messages_router)
app.include_router(match_router)

app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.on_event("startup")
async def on_startup():

    await init_models()
    await insert_dummy_data()
    print("Done")


@app.get("/")
def read_root():
    return {"Hello": "World"}

