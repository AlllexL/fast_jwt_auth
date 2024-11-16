from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import UserRelationMixin

if TYPE_CHECKING:
    from .user import User


# class Profile(UserRelationMixin, Base):
class Profile(Base):
    # _user_id_unique = True
    # _user_back_populates = "profile"

    first_name: Mapped[str | None] = mapped_column(String(40))
    last_name: Mapped[str | None] = mapped_column(String(40))
    bio: Mapped[str | None] = None

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship(back_populates="profile")

    def __str__(self):
        return f"profile of {self.user}: {self.user_id=}, {self.first_name=}, {self.last_name=}"

    def __repr__(self):
        return str(self)
