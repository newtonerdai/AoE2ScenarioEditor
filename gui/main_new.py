# -*- coding=utf-8 -*-

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QStringListModel, QModelIndex, QItemSelection
from PyQt5 import uic
from AoE2ScenarioParser.aoe2_scenario import AoE2DEScenario
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.objects.data_objects.unit import Unit
from units_list_model import UnitsListModel
from typing import Union, List

class MainWindow:
    def __init__(self):
        # 从文件中加载UI定义
        self.ui = uic.loadUi("gui_main.ui")
        # 主窗口对接的场景（初始为空对象，无任何属性/方法）
        self.scenario = AoE2DEScenario()
        # 单位tab的属性：{当前选择玩家、当前玩家的unit对象列表、当前选中的单位对象}
        self.unitTabAttrs = {"current_player": 1,
                             "current_px_units": [],
                             "current_unit": None}

        self.unitTab_units: List[List[Unit]] = []   # TODO
        self.unitTab_px_units: List[Unit] = []  # TODO

        # 储存单位列表视图(QListView)里所有项的model（model的每个项 ↔ 一个Unit）
        self.unitslistmodel = UnitsListModel()
        self.ui.listView_Units.setModel(self.unitslistmodel)

        self.signal_connect_slot()

    def connect_scenario(self, scenario: AoE2DEScenario):
        """与场景对象对接"""
        self.scenario = scenario
        self.connect_units()

    def connect_units(self, player=1):
        """单位tab下的listView_Units ↔ aoesp的units列表"""
        self.unitTab_units = self.scenario.unit_manager.units
        self.unitTab_px_units = self.unitTab_units[player]
        self.unitslistmodel.reload_units(self.scenario.unit_manager.get_player_units(PlayerId(player)))

    # 初始化：信号 ↔<链接>↔ 槽
    def signal_connect_slot(self):
        """将信号与槽链接"""
        # <单位tab - 玩家下拉框> 选择任意项
        self.ui.combo_UnitTab_Px.activated[int].connect(self.ut_select_player)
        # <单位tab - 单位列表框> 点击框体 / 项选择改变
        self.ui.listView_Units.clicked.connect(self.ut_lw_on_reselect)
        self.ui.listView_Units.selectionModel().selectionChanged.connect(self.ut_lw_on_reselect)
        # <单位tab - 确认更改> 点击
        self.ui.button_UnitSaveChange.clicked.connect(self.ut_editattrs_on_click)
        # <单位tab - 放弃更改> 点击
        self.ui.button_UnitQuitChange.clicked.connect(self.ut_editattrs_on_click)


    # 【单位tab】
    # 自定义槽
    def ut_select_player(self):
        """<玩家下拉框> 选择一次 → ①获取当前玩家 + 更新current_px_units，②刷新列表框，③更新current_unit。"""
        self.ut_update_current_px_units()
        self.ut_update_listView_Units()
        self.ut_update_current_unit()
        pass

    def ut_lw_on_reselect(self):
        """listView_Units被单击/选择变更 → ①更新current_unit记录，②重载单位属性栏"""
        self.ut_update_current_unit()
        self.ut_load_unit_attrs()
        print("listView_Units被单击/选择变更，更新current_unit记录，重载单位属性栏")

    def ut_editattrs_on_click(self):
        """按钮<保存更改> 被单击 → 如果玩家未改变 则修改Unit (视图自动更新)；
                                    如果玩家改变，则修改Unit + 更新current_px_units + 给模型重载数据 + 更新current_unit"""
        current_unit: Union[Unit, None] = self.unitTabAttrs["current_unit"]
        if current_unit:
            player_pre = current_unit.player.value
            player_new = self.ui.combo_UnitOwner.currentIndex()
            if player_pre == player_new:
                self.ut_edit_unit_attrs()
                print("保存更改")
            elif player_pre != player_new:
                self.ut_edit_unit_attrs()
                self.ut_update_current_px_units()
                self.ut_update_listView_Units()
                self.ut_update_current_unit()
                print("保存更改。更新current_px_units，重载模型数据, 更新current_unit")
        else:
            print("未选择任何单位")

    def ut_new_unit(self):
        # <新增单位> 按钮点击时，执行：①修改单位属性，②刷新列表框
        pass

    # 由自定义槽调用的函数
    # ——辅助记录
    def ut_update_current_px_units(self):
        """更新单位tab的属性记录： <玩家下拉框> 所对应的 <玩家编号> 及其 <单位列表对象(unit_manager.units)>"""
        current_player = self.ui.combo_UnitTab_Px.currentIndex()  # 单位tab下的选择玩家（0=盖亚，1~8=P1~P8，9=全部玩家）
        current_px_units = []  # 属于当前玩家的单位对象列表：[{单位1}, {单位2} ...]
        if 0 <= current_player <= 8:
            playerid = PlayerId(current_player)  # 生成玩家编号对应的PlayerId对象（等效于PlayerId.GAIA~ONE~EIGHT）
            current_px_units = self.scenario.unit_manager.get_player_units(playerid)
        elif current_player == 9:
            current_px_units = self.scenario.unit_manager.get_all_units()
        # 保存 <玩家编号> 和 <单位列表对象>
        self.unitTabAttrs["current_player"] = current_player
        self.unitTabAttrs["current_px_units"] = current_px_units
        print("重新登记当前玩家所有单位")

    def ut_update_current_unit(self):
        """更新单位tab的属性记录： <单位列表框> 里的 <current_unit>。若未选中，则为None。"""
        # current_index = self.ui.listView_Units.currentIndex().row()
        current_selectindexes: List[QModelIndex] = self.ui.listView_Units.selectedIndexes()  # 无任何选中时为 []
        if len(current_selectindexes) > 0:
            current_selectindex = current_selectindexes[0].row()
            current_unit = self.unitslistmodel.getItem(current_selectindex)
            self.unitTabAttrs["current_unit"] = current_unit
            print("重新登记当前选中单位")
        else:
            self.unitTabAttrs["current_unit"] = None
            print("重新登记当前选中单位：无选中，故设为None")

    def ut_update_listView_Units(self):
        self.unitslistmodel.reload_units(self.unitTabAttrs["current_px_units"])
        print("重载listView里的单位")

    # ——页内操作
    def ut_load_unit_attrs(self):
        """读取 <单位列表框> 里 <current_unit> 的属性，逐个加入到右侧的单位属性栏里。"""
        # 定位index对应的Unit对象
        current_unit: Union[Unit, None] = self.unitTabAttrs["current_unit"]
        if type(current_unit) == Unit:
            # 更新各项属性栏的数值
            self.ui.spin_UnitPoint_X.setValue(current_unit.x)
            self.ui.spin_UnitPoint_Y.setValue(current_unit.y)
            self.ui.spin_UnitPoint_Z.setValue(current_unit.z)
            self.ui.spin_UnitRotation.setValue(current_unit.rotation)
            # self.ui.combo_UnitPhase.setCurrentIndex(round(current_unit.rotation / 3.1415927 * 4))   # TODO：初始相位的 float 与 n/4 形式的自动转换
            self.ui.edit_UnitFrame.setText(str(current_unit.initial_animation_frame))
            self.ui.edit_UnitStatus.setText(str(current_unit.status))
            self.ui.edit_UnitTypeID.setText(str(current_unit.unit_const))
            self.ui.edit_UnitMapID.setText(str(current_unit.reference_id))
            self.ui.edit_UnitGarrisonInID.setText(str(current_unit.garrisoned_in_id))
            self.ui.combo_UnitOwner.setCurrentIndex(current_unit.player.value)
            print("读取单位属性")
        else:
            print("未选择任何单位")

    def ut_edit_unit_attrs(self):
        """根据右侧 <单位属性栏> 的新属性，修改对应Unit对象的属性。"""
        # 定位index对应的Unit对象
        current_unit: Union[Unit, None] = self.unitTabAttrs["current_unit"]
        if type(current_unit) == Unit:
            current_unit.x = self.ui.spin_UnitPoint_X.value()
            current_unit.y = self.ui.spin_UnitPoint_Y.value()
            current_unit.z = self.ui.spin_UnitPoint_Z.value()
            current_unit.rotation = self.ui.spin_UnitRotation.value()
            # current_unit.rotation = eval(self.ui.combo_UnitPhase.currentText()) * 3.1415927   # TODO：初始相位的 float 与 n/4 形式的自动转换
            current_unit.initial_animation_frame = int(self.ui.edit_UnitFrame.text())
            current_unit.status = int(self.ui.edit_UnitStatus.text())
            current_unit.unit_const = int(self.ui.edit_UnitTypeID.text())
            current_unit.reference_id = int(self.ui.edit_UnitMapID.text())
            current_unit.garrisoned_in_id = int(self.ui.edit_UnitGarrisonInID.text())
            # current_unit._player = self.ui.combo_UnitOwner.currentIndex()   # 可以这么改。但为了避免aoesp作者暗改机制，用他给的方法更好
            new_player_id = PlayerId(self.ui.combo_UnitOwner.currentIndex())
            self.scenario.unit_manager.change_ownership(current_unit, new_player_id)
            print("编辑单位属性")
        else:
            print("未选择任何单位")
            QMessageBox.critical(self.ui, "错误", "未选择任何单位，请重试")

    def ut_add_new_unit(self):
        """给当前玩家创建新的Unit对象（选择所有玩家时，会提示给单位属性栏里的玩家添加）"""
        player = self.unitTabAttrs["current_player"]
        player_attr = self.ui.combo_UnitOwner.currentIndex()    # <单位属性栏> 里的玩家
        player_attrtext = self.ui.combo_UnitOwner.currentText()
        if 0 <= player <= 8:
            player_id = PlayerId(player)
        else:
            player_id = PlayerId(player_attr)
            QMessageBox.question(self.ui,
                                 "添加单位给...",
                                 f"当前列表为 {self.ui.combo_UnitTab_Px.currentText()}\n"
                                 f"是否将新单位添加到所有玩家？")
        x = self.ui.spin_UnitPoint_X.value()
        y = self.ui.spin_UnitPoint_Y.value()
        z = self.ui.spin_UnitPoint_Z.value()
        unit_const = int(self.ui.edit_UnitTypeID.text())
        self.scenario.unit_manager.add_unit(player_id, unit_const, x, y, z)
        print("添加单位")

# 读取场景
# read_file = r"C:/Users/acer/Games/Age of Empires 2 DE/76561199002600352/resources/_common/scenario/default0.aoe2scenario"
read_file = r"C:/Users/acer/Games/Age of Empires 2 DE/76561199002600352/resources/_common/scenario/C长坂坡之战-草图-赵云林中暗杀曹兵.aoe2scenario"
scenarioManager = AoE2DEScenario.from_file(read_file)
# 创建AOESE程序和主窗口
app = QApplication([])
mainWindow = MainWindow()
# 主窗口 & 场景 相对接
mainWindow.connect_scenario(scenarioManager)

# 场景信息载入信息tab
game_version = scenarioManager.game_version
scenario_version = scenarioManager.scenario_version
mainWindow.ui.edit_GameVersion.setText(game_version)
mainWindow.ui.edit_ScenarioVersion.setText(scenario_version)

# 显示AOESE程序和窗口
mainWindow.ui.show()
app.exec_()
