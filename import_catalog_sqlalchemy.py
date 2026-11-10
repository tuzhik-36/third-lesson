import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    func,
    Integer,
    String,
    create_engine,
    event,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    products: Mapped[list["Product"]] = relationship(
        back_populates="category"
    )


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price_cents >= 0", name="check_nonnegative_price"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )

    category: Mapped[Category] = relationship(back_populates="products")


def price_to_cents(value):
    """Преобразует цену в целое число копеек без ошибок округления float."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Некорректная цена: {value!r}")

    if not amount.is_finite() or amount < 0:
        raise ValueError(f"Цена должна быть неотрицательным числом: {value!r}")

    rounded = amount.quantize(Decimal("0.01"))
    if rounded != amount:
        raise ValueError(
            f"Цена должна содержать не более 2 знаков после запятой: {value!r}"
        )

    return int(rounded * 100)


def validate_and_prepare(records):
    if not isinstance(records, list):
        raise ValueError("Ожидался JSON-массив товаров.")

    prepared = []
    categories = {}

    for index, item in enumerate(records, start=1):
        try:
            product_name = item["product_name"].strip()
            category_name = item["category"]["name"].strip()
            description = item["category"].get("description")
            price_cents = price_to_cents(item["price"])
        except (KeyError, TypeError, AttributeError) as error:
            raise ValueError(f"Некорректная запись товара №{index}: {error}")

        if not product_name:
            raise ValueError(f"В записи №{index} пустое название товара.")
        if not category_name:
            raise ValueError(f"В записи №{index} пустое название категории.")

        if category_name in categories and categories[category_name] != description:
            raise ValueError(
                f"Для категории {category_name!r} обнаружены разные описания."
            )

        categories[category_name] = description
        prepared.append(
            {
                "product_name": product_name,
                "price_cents": price_cents,
                "category_name": category_name,
            }
        )

    return categories, prepared


def create_database_engine(db_path):
    engine = create_engine(f"sqlite:///{Path(db_path)}")

    # SQLite по умолчанию не включает проверку внешних ключей.
    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def import_catalog(json_path, db_path):
    with Path(json_path).open("r", encoding="utf-8") as file:
        records = json.load(file)

    categories_data, products_data = validate_and_prepare(records)

    engine = create_database_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    # Контекст begin() автоматически фиксирует транзакцию при успехе
    # и откатывает её при возникновении ошибки.
    with Session.begin() as session:
        category_objects = {}

        for name, description in categories_data.items():
            category = session.scalar(
                select(Category).where(Category.name == name)
            )

            if category is None:
                category = Category(name=name, description=description)
                session.add(category)
            else:
                category.description = description

            category_objects[name] = category

        # Сохраняем категории, чтобы их id были доступны для товаров.
        session.flush()

        for item in products_data:
            category = category_objects[item["category_name"]]

            product = session.scalar(
                select(Product).where(
                    Product.product_name == item["product_name"]
                )
            )

            if product is None:
                product = Product(
                    product_name=item["product_name"],
                    price_cents=item["price_cents"],
                    category=category,
                )
                session.add(product)
            else:
                product.price_cents = item["price_cents"]
                product.category = category

    with Session() as session:
        category_count = session.scalar(select(func.count()).select_from(Category))
        product_count = session.scalar(select(func.count()).select_from(Product))

        # Проверяем, что каждый товар связан с существующей категорией.
        orphan_count = session.scalar(
            select(Product).outerjoin(Category).where(Category.id.is_(None))
        )

    engine.dispose()

    if orphan_count is not None:
        raise RuntimeError("Обнаружен товар без существующей категории.")

    print(
        f"Импорт завершён: категорий — {category_count}, "
        f"товаров — {product_count}."
    )
    print(f"База данных: {db_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Импорт JSON-каталога в SQLite с помощью SQLAlchemy."
    )
    parser.add_argument(
        "json_file",
        nargs="?",
        default="catalog.json",
        help="путь к исходному JSON (по умолчанию catalog.json)",
    )
    parser.add_argument(
        "--db",
        default="catalog.db",
        help="путь к SQLite-файлу (по умолчанию catalog.db)",
    )
    args = parser.parse_args()
    import_catalog(args.json_file, args.db)


if __name__ == "__main__":
    main()
