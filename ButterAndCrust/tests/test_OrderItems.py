
from ButterAndCrust.lib.items.OrderItems import Lineitems, _BaseItem, _BaseFriendlyItem

def test_BaseItem_init():
    """
    Tests the initialisation of the _BaseItem class
    """

    desc = "Test item"
    price = 1.0

    item = _BaseItem(desc, price=price)

    assert item.description == desc
    assert item.friendly_desc == desc
    assert item.price == price
    assert item.img == None

def test_BaseItem_compare():
    """
    Tests the __eq__ override of the _BaseItem class
    """

    item1 = _BaseItem("Item1")
    item2 = _BaseItem("Item1")
    item3 = _BaseItem("Item2")

    assert item1 == item2
    assert item1 != item3

def test_BaseFriendlyItem_init():
    """
    Tests the initialisation of the _BaseFriendlyItem class
    """

    desc = "Test item"
    friendly_desc = "friendly"
    price = 1.0

    item = _BaseFriendlyItem(desc, friendly_desc, price=price)

    assert item.description == desc
    assert item.friendly_desc == friendly_desc
    assert item.price == price
    assert item.img == None

def test_get():
    """
    Tests the Lineitems.get() method
    """
    expected = Lineitems.ExtraLoaf()
    actual = Lineitems.get("Extra Loaf")

    assert expected == actual

def test_unmatched_item():
    """
    Tests that if Lineitems.get() can't find an item it safely creates
    a _Baseitem type
    """

    desc = "Not a real item"

    expected = _BaseItem(desc)
    actual = Lineitems.get(desc)

    assert type(actual) is _BaseItem

    assert expected == actual

