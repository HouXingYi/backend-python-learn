from sqlalchemy.orm import Session

from app.crud.base import BaseCrud
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductCrud(BaseCrud[Product]):
    def __init__(self, read_db: Session, write_db: Session):
        super().__init__(Product, read_db, write_db)

    @classmethod
    def conditions(cls, *, product_id: int | None = None) -> list:
        conditions = []
        if product_id is not None:
            conditions.append(Product.id == product_id)
        return conditions

    def list_products(self) -> list[Product]:
        return self.select_list([], order_by=[Product.id.desc()])

    def get_product(self, product_id: int) -> Product | None:
        return self.try_select_one(self.conditions(product_id=product_id))

    def create_product(self, product_in: ProductCreate) -> Product:
        product = Product(**product_in.model_dump())
        return self.insert(product)

    def update_product(
        self,
        product: Product,
        product_in: ProductUpdate,
    ) -> Product:
        for field, value in product_in.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        return self.update(product)

    def delete_product(self, product: Product) -> None:
        self.delete(product)


def list_products(db: Session) -> list[Product]:
    return ProductCrud(db, db).list_products()


def get_product(db: Session, product_id: int) -> Product | None:
    return ProductCrud(db, db).get_product(product_id)


def create_product(db: Session, product_in: ProductCreate) -> Product:
    return ProductCrud(db, db).create_product(product_in)


def update_product(
    db: Session,
    product: Product,
    product_in: ProductUpdate,
) -> Product:
    return ProductCrud(db, db).update_product(product, product_in)


def delete_product(db: Session, product: Product) -> None:
    ProductCrud(db, db).delete_product(product)
