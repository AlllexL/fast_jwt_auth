from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_manager
from .dependencies import product_by_id
from . import crud
from .schemas import ProductCreate, Product, ProductUpdate, ProductUpdatePartial

router = APIRouter(tags=["Products"])


@router.get("/", response_model=list[Product])
async def get_product(
    session: AsyncSession = Depends(db_manager.scoped_session_dependency),
):
    return await crud.get_products(session=session)


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    session: AsyncSession = Depends(db_manager.scoped_session_dependency),
):
    return await crud.product_create(product_in, session)


# @router.get("/{product_id}/", response_model=Product)
# async def get_product_by_id(
#     product_id: int, session: AsyncSession = Depends(db_manager.session_dependency)
# ):
#     product = await crud.get_product_by_id(product_id=product_id, session=session)
#     if product is not None:
#         return product
#
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found!"
#     )


@router.get("/{product_id}/", response_model=Product)
async def get_product_by_id(product: Product = Depends(product_by_id)):

    return product


@router.put("/{product_id}/", response_model=Product)
async def update_product(
    product_update: ProductUpdate,
    product: Product = Depends(product_by_id),
    session: AsyncSession = Depends(db_manager.session_dependency),
):
    return await crud.product_update(
        product=product, product_update=product_update, session=session
    )


@router.patch("/{product_id}/")
async def update_partial_product(
    update_partial_product: ProductUpdatePartial,
    product: Product = Depends(product_by_id),
    session: AsyncSession = Depends(db_manager.session_dependency),
):
    return await crud.product_update(
        product=product,
        product_update=update_partial_product,
        session=session,
        partial=True,
    )


@router.delete("/{product_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product: Product = Depends(product_by_id),
    session: AsyncSession = Depends(db_manager.session_dependency),
) -> None:
    await crud.product_delete(product=product, session=session)
