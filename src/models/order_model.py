from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from models.base_model import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    phase_id = Column(Integer, ForeignKey("phases.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    unit_id = Column(Integer, ForeignKey("units.id"))
    dest = Column(String)
    target_order_id = Column(Integer, ForeignKey("orders.id"))
    assumed = Column(Boolean, default=False)

    __mapper_args__ = {
        "polymorphic_identity": "order",
        "polymorphic_on": type,
    }


class HoldOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "hold",
    }


class MoveOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "move",
    }


class SupportOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "support",
    }


class ConvoyOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "convoy",
    }


class RetreatOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "retreat",
    }


class DisbandOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "disband",
    }


class GainOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "gain",
    }


class LoseOrder(Order):
    __mapper_args__ = {
        "polymorphic_identity": "lose",
    }
