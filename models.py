from sqlalchemy import Integer, Column
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class AvailableKeys(Base):
    __tablename__ = 'available_keys'
    seq: Mapped[int] = Column(Integer, primary_key=True)
    order_key: Mapped[int] = Column(Integer, index=True, nullable=False)

    def __repr__(self):
        return f"sequence_number: {self.seq}"


class BookedKeys(Base):
    __tablename__ = 'booked_keys'
    seq: Mapped[int] = mapped_column(Integer, primary_key=True)
    # added index, as later we want to do ordering on the basis of this column
    order_key: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    def __repr__(self):
        return f"sequence_number: {self.seq}"


# bulk operations in orm does not support these events
# and postgres Computed columns expression does not support mutable
# functions(whose output with same input will change with time)
# like random() and datetime()
# so now are forced to pass order_key value manually while AvailableKeys object creation.

# @listens_for(AvailableKeys, "before_insert")
# def lowercase(mapper, connection, target):
#     target.order_key = 123