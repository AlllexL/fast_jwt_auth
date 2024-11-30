from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship


from .base import Base

# from .order_product_association import order_product_association_table

if TYPE_CHECKING:
    from . import Order
    from . import OrderProductAssociation


class Product(Base):

    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]

    # orders: Mapped[list["Order"]] = relationship(
    #     secondary="order_product_association", back_populates="products"
    # )

    orders_association: Mapped[list["OrderProductAssociation"]] = relationship(
        back_populates="product"
    )
