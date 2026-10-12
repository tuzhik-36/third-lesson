import json
from collections import defaultdict

with open("users.json", "r", encoding="utf-8") as file:
    users = json.load(file)

cities = defaultdict(list)

for user in users:
    city = user["address"]["city"]
    name = user["name"]

    cities[city].append(name)

with open("cities.json", "w", encoding="utf-8") as file:
    json.dump(
        dict(cities),
        file,
        ensure_ascii=False,
        indent=4
    )

print("Готово! Файл cities.json создан.")
