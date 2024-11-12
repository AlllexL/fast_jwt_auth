from itertools import product

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import db_manager

from api_v1.products.schemas import ProductCreate, ProductUpdate, ProductUpdatePartial
from core.models import Product


async def get_products(session: AsyncSession) -> list[Product]:
    stmt = select(Product).order_by(Product.id)
    result: Result = await session.execute(stmt)
    products = result.scalars().all()
    return list(products)


async def get_product_by_id(product_id: int, session: AsyncSession) -> Product | None:
    # stmt = select(Product).where(Product.id == product_id)
    # result: Result = await session.execute(stmt)
    # product = result.scalar_one()
    # return product
    return await session.get(Product, product_id)


async def product_create(product_in: ProductCreate, session: AsyncSession) -> Product:
    prod = Product(**product_in.model_dump())
    session.add(prod)
    await session.commit()
    await session.refresh(prod)
    return prod


async def product_update(
    product: Product,
    product_update: ProductUpdate | ProductUpdatePartial,
    session: AsyncSession,
    partial: bool = False,
) -> Product:
    for name, value in product_update.model_dump(exclude_unset=partial).items():
        setattr(product, name, value)
    await session.commit()
    return product


async def product_delete(product: Product, session: AsyncSession) -> None:
    await session.delete(product)
    await session.commit()
