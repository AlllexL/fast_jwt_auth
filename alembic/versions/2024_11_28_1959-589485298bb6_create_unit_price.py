"""Create unit price

Revision ID: 589485298bb6
Revises: 14f9991e503b
Create Date: 2024-11-28 19:59:32.397796

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "589485298bb6"
down_revision: Union[str, None] = "14f9991e503b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "order_product_association",
        sa.Column("unit_price", sa.Integer(), server_default="0", nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("order_product_association", "unit_price")
    # ### end Alembic commands ###