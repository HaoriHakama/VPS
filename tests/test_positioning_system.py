from mylib.positioning_system import *


def test_data_list():
    data_list = DataList()

    assert data_list.x_data() is None
    assert data_list.y_data() is None
    assert data_list.z_data() is None

    data_list.add_data(PositionData([0.0, 1.0, 2.0], "20230501120000"))
    data_list.add_data(PositionData([3.0, 4.0, 5.0], "20230501120010"))
    data_list.add_data(PositionData([-1.0, -2.0, -3.0], "20230501120030"))

    assert data_list.x_data() == [0.0, 3.0, -1.0]
    assert data_list.y_data() == [1.0, 4.0, -2.0]
    assert data_list.z_data() == [2.0, 5.0, -3.0]
