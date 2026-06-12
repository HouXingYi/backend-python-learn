from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.products import ProductCrud
from app.db.session import get_read_db, get_write_db
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
def list_products(
    read_db: Session = Depends(get_read_db),
    write_db: Session = Depends(get_write_db),
) -> list[ProductRead]:
    crud = ProductCrud(read_db, write_db)
    return crud.list_products()


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    read_db: Session = Depends(get_read_db),
    write_db: Session = Depends(get_write_db),
) -> ProductRead:
    crud = ProductCrud(read_db, write_db)
    return crud.create_product(product_in)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    read_db: Session = Depends(get_read_db),
    write_db: Session = Depends(get_write_db),
) -> ProductRead:
    crud = ProductCrud(read_db, write_db)
    product = crud.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    read_db: Session = Depends(get_read_db),
    write_db: Session = Depends(get_write_db),
) -> ProductRead:
    crud = ProductCrud(read_db, write_db)
    product = crud.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.update_product(product, product_in)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    read_db: Session = Depends(get_read_db),
    write_db: Session = Depends(get_write_db),
) -> None:
    crud = ProductCrud(read_db, write_db)
    product = crud.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    crud.delete_product(product)
