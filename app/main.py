from typing import Union

from fastapi import FastAPI
from app.queries import *

app = FastAPI()


@app.get("/upgrades/{item_name}")
def upgrade_data(item_name: str, base_value: int, primling_price: int):
    result = find_item_values(item_name, base_value, primling_price);
    return result


