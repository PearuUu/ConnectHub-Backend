from fastapi import FastAPI

from src.dbTest import insertUser, init_models, insert_dummy_data, select_and_print_data, get_user_with_messages

app = FastAPI()


@app.on_event("startup")
async def on_startup():

    await init_models()
    await insert_dummy_data()
    await select_and_print_data()
    await get_user_with_messages(1)

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
