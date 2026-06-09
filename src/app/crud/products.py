from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def list_products(db: Session) -> list[Product]:
    statement = select(Product).order_by(Product.id.desc())
    return list(db.scalars(statement).all())


def get_product(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def create_product(db: Session, product_in: ProductCreate) -> Product:
    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(
    db: Session,
    product: Product,
    product_in: ProductUpdate,
) -> Product:
    for field, value in product_in.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()
