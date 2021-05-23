# -*- coding=utf-8 -*-

from PyQt5.QtCore import QAbstractListModel, QVariant, QModelIndex, QSize, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QListView, QHBoxLayout, QVBoxLayout, QPushButton, QWidget
from AoE2ScenarioParser.objects.data_objects.unit import Unit
from AoE2ScenarioParser.datasets.players import PlayerId
from typing import Union, List

# 创建一个基于 PyQt5.QtCore.QAbstractListModel 类的数据模型。
class UnitsListModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self._data_list = []  # 数据list，保存所有数据

    # 重新装载 Unit 对象
    def reload_units(self, units: List[Unit]):
        self.clear()
        self.addItems(units)

    # 继承后有 data() 和 rowCount() 两个方法必须要实现。
    def data(self, index: QModelIndex, role: int = ...):
        """
        继承父类，必须有。设置不同类型调用返回数据
        :param index: 索引
        :param role: 要获取的数据类型
        :return:
        """
        # 设置列表显示使用的数据
        if index.isValid() or (0 <= index.row() < len(self._data_list)):
            if role == Qt.DisplayRole:
                unit = self._data_list[index.row()]
                unit_name = unit.name if unit.name else "<Unknown>"
                display_str = f"{unit.reference_id}: {unit_name} {{{unit.unit_const}}}" # "mapID: typeNmae {typeID}"
                return QVariant(display_str)
            # elif role == Qt.DecorationRole:
            #     return QVariant(self._data_list[index.row()].reference_id)
            # elif role == Qt.SizeHintRole:
            #     return QVariant(QSize(70,80))
            # elif role == Qt.TextAlignmentRole:
            #     return QVariant(int(Qt.AlignHCenter|Qt.AlignVCenter))
        else:
            return QVariant()

    def rowCount(self, parent = QModelIndex()) -> int:
        """
        继承父类，必须有。返回数据总行数
        :param parent:
        :return:
        """
        return len(self._data_list)

    # 增删改清
    def addItem(self, unit: Unit):
        """
        自定义。添加单个数据
        :param unit: AOESP的Unit对象
        :return:
        """
        if unit:
            self.beginInsertRows(QModelIndex(), len(self._data_list), len(self._data_list) + 1)
            self._data_list.append(unit)
            self.endInsertRows()

    def addItems(self, units: List[Unit]):
        """
        自定义。添加多个数据
        :param units: 应为装载有多个Unit对象的列表
        :return:
        """
        for unit in units:
            self.addItem(unit)

    def insertItem(self, index, unit: Unit):
        """
        自定义。在index处插入单个数据
        :param index: 索引
        :param unit: AOESP的Unit对象
        :return:
        """
        if index > -1 and index < len(self._data_list):
            if unit:
                self.beginInsertRows(QModelIndex(), index, index + 1)
                self._data_list.insert(index, unit)
                self.endInsertRows()

    def deleteItem(self, index):
        """
        自定义。删除数据
        :param index: 索引
        :return:
        """
        self.beginRemoveRows(QModelIndex(), index, index - 1)
        del self._data_list[index]
        self.endRemoveRows()

    def takeItem(self, index):
        """
        自定义。剔除单个数据（但不del）
        :param index: 索引
        :return:
        """
        if index > -1 and index < len(self._data_list):
            self.beginRemoveRows(QModelIndex(), index, index - 1)
            self._data_list.pop(index)
            self.endRemoveRows()

    def updateItem(self, index, new_item):
        """
        自定义。更新数据（但不发送.dataChanged()信号）
        :param index: 索引
        :param new_item: 新数据
        :return:
        """
        self._data_list[index] = new_item
        # self.dataChanged(index, index, [Qt.DisplayRole])

    def getItem(self, index):
        if index > -1 and index < len(self._data_list):
            return self._data_list[index]

    def clear(self):
        """
        清空数据
        :return:
        """
        self.beginResetModel()
        self._data_list.clear()
        self.endResetModel()


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.centralwidget = QWidget(self)
        self.layoutVerti = QVBoxLayout(self.centralwidget)
        self.layoutHoriz = QHBoxLayout(self.centralwidget)
        self.listView = QListView(self.centralwidget)
        self.buttonNew = QPushButton("新建单位", self.centralwidget)
        self.buttonTake = QPushButton("移出单位", self.centralwidget)

        self.layoutHoriz.addWidget(self.buttonNew)
        self.layoutHoriz.addWidget(self.buttonTake)
        self.layoutVerti.addWidget(self.listView)
        self.layoutVerti.addLayout(self.layoutHoriz)
        self.setCentralWidget(self.centralwidget)

        self.listView = self.listView

        # 连接信号 & 槽
        self.buttonNew.clicked.connect(self.add_unit)
        self.buttonTake.clicked.connect(self.del_unit)

        # 创建新数据
        unit_a = Unit(PlayerId(0), 0, 0, 0, 0, 0, 0, 0, 0, 0)
        units = []
        for x in range(5, 10):
            new_unit = Unit(PlayerId(0), x, 0, 0, x, x, 0, 0, 0, 0)
            units.append(new_unit)

        # 添加新数据到 model 里
        self.list_model = UnitsListModel()
        self.list_model.addItem(unit_a)
        self.list_model.addItems(units)

        # 绑定 model → listView
        self.listView.setModel(self.list_model)


    player_, x_, y_, z_, reference_id_, status_, rotation_, unit_const_, initial_animation_frame_, garrisoned_in_id_\
        = PlayerId(0), 5.0, 5.0, 5.0, 8, 2, 3.1415926 / 4, 2, 5, -1
    def create_new_unit(self):
        # self.player_ = PlayerId(0)
        self.x_ += 1.0
        self.y_ += 1.0
        self.z_ += 1.0
        self.reference_id_ += 1
        self.unit_const_ += 1
        # self.status_ = 2
        # self.rotation_ = 3.1415926 / 4
        self.initial_animation_frame_ += 1
        # self.garrisoned_in_id_ = -1
        new_unit = Unit(self.player_,
                        self.x_,
                        self.y_,
                        self.z_,
                        self.reference_id_,
                        self.unit_const_,
                        self.status_,
                        self.rotation_,
                        self.initial_animation_frame_,
                        self.garrisoned_in_id_)
        return new_unit

    def add_unit(self):
        self.list_model.addItem(self.create_new_unit())

    def del_unit(self):
        self.list_model.deleteItem(self.listView.selectedIndexes()[0].row())  # TODO: 获取当前选择的索引

if __name__ == '__main__':
    # 创建程序和窗口。
    app = QApplication([])
    mainWindow = MyMainWindow()

    # 窗口显示
    mainWindow.resize(500, 400)
    mainWindow.show()
    app.exec_()
