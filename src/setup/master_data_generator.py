from sqlalchemy.orm import Session
from models.power_model import Power


def generate_master_data(session: Session) -> None:
    master_data = [
        Power(symbol="a", name="Austria", adjective="Austrian"),
        Power(symbol="e", name="England", adjective="English"),
        Power(symbol="f", name="France", adjective="French"),
        Power(symbol="g", name="Germany", adjective="German"),
        Power(symbol="i", name="Italy", adjective="Italian"),
        Power(symbol="r", name="Russia", adjective="Russian"),
        Power(symbol="t", name="Turkey", adjective="Turkish"),
    ]
    session.add_all(master_data)
    session.commit()
