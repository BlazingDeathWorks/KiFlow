import json
from json import JSONEncoder


class Preset:
    def __init__(self, url: str, orders: list) -> None:
        self.url = url
        self.orders = orders

    def create_json(self):
        return json.dumps(self, indent=4, cls=PresetEncoder)


class Ki:
    def __init__(self, item: str, toppings: list[str]):
        self.item = item
        self.toppings = toppings

    def __str__(self):
        return str(self.item) + "\n" + str(self.toppings)


class PresetEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
