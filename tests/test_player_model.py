from models.player_model import Player
from models.table_model import Table
from models.user_model import User


def test_player_creation(master_data):
    new_user = User(xid=123, sname="abc")
    new_table = Table(master_data)
    new_player = Player()
    new_player.user = new_user
    new_player.table = new_table
    master_data.add(new_player)
    master_data.commit()
    player = master_data.query(Player).first()
    user = master_data.query(User).first()
    table = master_data.query(Table).first()
    assert player is not None
    assert player.user is user
    assert player.table is table
