import os

from ButterAndCrust.lib.DB.Tables.SQLTable import SQLTable

DB_LOC = os.path.dirname(__file__) + "/mockdata/OrderHistory.db"

def test_init():
    table = SQLTable("TempTable", ["ID"], DB_LOC)

    assert table.name == "TempTable"
    assert table.columns == ["ID"]