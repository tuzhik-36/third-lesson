
import requests


def get_target_info(name):
    """Получение статистической информации об имени."""

    age_url = "https://api.agify.io"
    gender_url = "https://api.genderize.io"

    age_response = requests.get(age_url, params={"name": name}, timeout=10)
    gender_response = requests.get(gender_url, params={"name": name}, timeout=10)

    age_response.raise_for_status()
    gender_response.raise_for_status()

    age_data = age_response.json()
    gender_data = gender_response.json()

    age = age_data.get("age")
    gender = gender_data.get("gender")
    probability = gender_data.get("probability")

    if probability is not None:
        probability = round(probability * 100)
    else:
        probability = 0

    female_probability = (
        probability if gender == "female"
        else 100 - probability if gender == "male"
        else 0
    )

    print("\n========== ДОСЬЕ ==========")
    print(f"Имя: {name}")
    print(f"Вероятный возраст: {age}")
    print(f"Вероятность женского пола: {female_probability}%")
    print("===========================\n")


def get_posts(user_id):
    """Получение постов пользователя."""

    url = "https://jsonplaceholder.typicode.com/posts"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) СекретныйАгентБот/1.0",
        "Accept-Language": "ru-RU,ru;q=0.9"
    }

    params = {
        "userId": user_id
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    posts = response.json()

    print("====== ЦИФРОВАЯ АКТИВНОСТЬ ======")
    print(f"Количество полученных постов: {len(posts)}")

    if posts:
        print("\nЗаголовок первого поста:")
        print(posts[0]["title"])

    print("================================")


def main():
    name = input("Введите имя: ").strip()

    if not name:
        print("Ошибка: имя не может быть пустым.")
        return

    try:
        get_target_info(name)
        get_posts(23)

    except requests.exceptions.RequestException as error:
        print(f"Ошибка при выполнении запроса: {error}")

    except ValueError:
        print("Ошибка при обработке JSON.")


if __name__ == "__main__":
    main()
