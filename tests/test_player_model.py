from src.models.player_model import Player
from src.models.table_model import Table
from src.models.user_model import User


def test_player_creation(db_session):
    new_user = User(userid=123, sname="abc")
    new_table = Table()
    new_player = Player()
    new_player.user = new_user
    new_player.table = new_table
    db_session.add(new_player)
    db_session.commit()
    player = db_session.query(Player).first()
    user = db_session.query(User).first()
    table = db_session.query(Table).first()
    assert player is not None
    assert player.user is user
    assert player.table is table
