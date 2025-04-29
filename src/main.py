from fastapi import FastAPI

from src.dbTest import insertUser, init_models

app = FastAPI()


@app.on_event("startup")
async def on_startup():

    await init_models()

    print("Done")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, query_param: str = None):
    return {"item_id": item_id, "query_param": query_param}


@app.get("/Users/InsertUser")
async def insert_user():
    print("test")
    await insertUser()
    print("insert user")
    return True
