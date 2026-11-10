import argparse
import json
import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL UNIQUE,
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);
"""


def price_to_cents(value):
    """Переводит цену в целое число копеек/центов без ошибок float."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Некорректная цена: {value!r}")

    if not amount.is_finite() or amount < 0:
        raise ValueError(f"Цена должна быть неотрицательным числом: {value!r}")

    rounded = amount.quantize(Decimal("0.01"))
    if rounded != amount:
        raise ValueError(f"Цена должна содержать не более 2 знаков после запятой: {value!r}")
    return int(rounded * 100)


def import_catalog(json_path, db_path):
    with Path(json_path).open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("Ожидался JSON-массив товаров.")

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA)

        # Сначала создаём уникальные категории.
        categories = {}
        for index, item in enumerate(records, start=1):
            try:
                category = item["category"]
                name = category["name"].strip()
                description = category.get("description")
            except (KeyError, TypeError, AttributeError):
                raise ValueError(f"В записи №{index} отсутствует корректная категория.")

            if not name:
                raise ValueError(f"В записи №{index} название категории пустое.")

            if name in categories and categories[name] != description:
                raise ValueError(
                    f"Для категории {name!r} обнаружены разные описания."
                )
            categories[name] = description

        for name, description in categories.items():
            connection.execute(
                """
                INSERT INTO categories (name, description)
                VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    description = excluded.description
                """,
                (name, description),
            )

        category_ids = {
            name: category_id
            for category_id, name in connection.execute(
                "SELECT id, name FROM categories"
            )
        }

        # Затем сохраняем товары, связывая каждый с категорией через FK.
        for index, item in enumerate(records, start=1):
            try:
                product_name = item["product_name"].strip()
                category_name = item["category"]["name"].strip()
                price_cents = price_to_cents(item["price"])
            except (KeyError, TypeError, AttributeError) as error:
                raise ValueError(f"Некорректная запись товара №{index}: {error}")

            if not product_name:
                raise ValueError(f"В записи №{index} пустое название товара.")

            connection.execute(
                """
                INSERT INTO products (product_name, price_cents, category_id)
                VALUES (?, ?, ?)
                ON CONFLICT(product_name) DO UPDATE SET
                    price_cents = excluded.price_cents,
                    category_id = excluded.category_id
                """,
                (product_name, price_cents, category_ids[category_name]),
            )

        # Проверяем целостность внешних ключей.
        violations = connection.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise RuntimeError(f"Обнаружены нарушения внешних ключей: {violations}")

        product_count = connection.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]
        category_count = connection.execute(
            "SELECT COUNT(*) FROM categories"
        ).fetchone()[0]

    print(f"Импорт завершён: категорий — {category_count}, товаров — {product_count}.")
    print(f"База данных: {db_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Импорт каталога JSON в нормализованную базу SQLite."
    )
    parser.add_argument("json_file", nargs="?", default="catalog.json",
                        help="путь к исходному JSON (по умолчанию catalog.json)")
    parser.add_argument("--db", default="catalog.db",
                        help="путь к SQLite-файлу (по умолчанию catalog.db)")
    args = parser.parse_args()
    import_catalog(args.json_file, args.db)


if __name__ == "__main__":
    main()
