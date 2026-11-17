print("================================")
print("       OSINT AGGREGATOR")
print("       Учебный проект")
print("================================")

print("Python работает!")
print("Библиотека Requests установлена!")
import requests

print("Версия Requests:", requests.__version__)
print("\n--- Проверка API Agify ---")

url = "https://api.agify.io"
params = {
    "name": "michael"
}

response = requests.get(url, params=params)

print("Статус ответа:", response.status_code)

if response.status_code == 200:
    data = response.json()
    age_data = data
    print("Ответ API:", data)
else:
    print("Agify временно недоступен.")
    print("Ответ сервера:", response.text)

    age_data = {
        "name": "michael",
        "age": None
    }

print("\n--- Проверка API Genderize ---")

url = "https://api.genderize.io"
params = {
    "name": "michael"
}

response = requests.get(url, params=params)

print("Статус ответа:", response.status_code)

if response.status_code == 200:
    data = response.json()
    gender_data = data
    print("Ответ API:", data)
else:
    print("Genderize временно недоступен.")
    print("Ответ сервера:", response.text)

    gender_data = {
        "gender": None,
        "probability": None
    }

print("\n--- Общий результат ---")

print("Имя:", age_data["name"])
print("Оценка возраста:", age_data["age"])
print("Статистическая категория:", gender_data["gender"])
print("Вероятность:", gender_data["probability"])

print("\n--- Получение тестовых публикаций ---")

url = "https://jsonplaceholder.typicode.com/posts"

headers = {
    "User-Agent": "EducationalPythonProject/1.0",
    "Accept-Language": "ru-RU,ru;q=0.9"
}

params = {
    "userId": 23
}

response = requests.get(
    url,
    params=params,
    headers=headers
)

print("Статус ответа:", response.status_code)

posts = response.json()

print("Количество публикаций:", len(posts))
print("Полученные данные:", posts)

print("\n--- Формирование учебного отчёта ---")

report = {
    "name": age_data["name"],
    "estimated_age": age_data["age"],
    "gender_category": gender_data["gender"],
    "gender_probability": gender_data["probability"],
    "posts_count": len(posts)
}

print("Отчёт сформирован:")
print(report)

print("\n--- Отправка отчёта на тестовый сервер ---")

url = "https://httpbin.org/post"

response = requests.post(
    url,
    json=report,
    timeout=10
)

print("Статус ответа:", response.status_code)

result = response.json()

print("Сервер получил отчёт:")
print(result["json"])

print("\n--- Скачивание учебного изображения ---")

url = "https://picsum.photos/800/600"

response = requests.get(
    url,
    stream=True,
    timeout=15
)

print("Статус ответа:", response.status_code)

response.raise_for_status()

with open("evidence.jpg", "wb") as file:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            file.write(chunk)

print("Изображение сохранено: evidence.jpg")

print("\n--- Проверка обработки HTTPError ---")

try:
    response = requests.get(
        "https://httpbin.org/status/404",
        timeout=5
    )

    response.raise_for_status()

except requests.exceptions.HTTPError as error:
    print("Обработана HTTP-ошибка:", error)

    print("\n--- Проверка обработки Timeout ---")

try:
    response = requests.get(
        "https://httpbin.org/delay/6",
        timeout=3
    )

    print("Статус ответа:", response.status_code)

except requests.exceptions.Timeout:
    print("Сервер не ответил за 3 секунды.")
    print("Обработана ошибка Timeout.")