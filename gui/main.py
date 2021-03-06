# -*- coding=utf-8 -*-

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QStringListModel
from PyQt5 import uic
from AoE2ScenarioParser.aoe2_scenario import AoE2DEScenario
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.objects.data_objects.unit import Unit
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
        self.unitTab_itemstr: List[str] = ["unit_1", "unit_2", "unit_3"]    # TODO
        strlistmodel = QStringListModel()   # TODO
        strlistmodel.setStringList(self.unitTab_itemstr)    # TODO
        self.ui.listView_Units.setModel(strlistmodel)   # TODO
        self.ui.listView_Units.clicked.connect(self.ut_check_unit)  # TODO

        self.signal_connect_slot()

    def ut_check_unit(self, item_index):
        print(f"选择的项是 {self.unitTab_itemstr[item_index.row()]}")

    def connect_scenario(self, scenario: AoE2DEScenario):
        """与场景对象对接"""
        self.scenario = scenario
        self.connect_units()


    def connect_units(self, player=1):
        """单位tab下的listView_Units ↔ aoesp的units列表"""
        self.unitTab_units = self.scenario.unit_manager.units
        self.unitTab_px_units = self.unitTab_units[player]


    def signal_connect_slot(self):
        """将信号与槽链接"""
        # <单位tab - 玩家下拉框> 选择任意项 → 取消 <单位列表框> 的选择
        # <单位tab - 玩家下拉框> 选择任意项 → 更新 单位tab的属性记录（当前玩家、当前单位项列表）
        # <单位tab - 玩家下拉框> 选择任意项 → 更新 <单位列表框>
        # <单位tab - 玩家下拉框> 选择任意项 → 更新 单位tab的属性记录（当前选中单位）
        self.ui.combo_UnitTab_Px.activated[int].connect(self.ui.list_Units.clearSelection)
        self.ui.combo_UnitTab_Px.activated[int].connect(self.ut_update_current_px_units)
        self.ui.combo_UnitTab_Px.activated[int].connect(self.ut_update_list_Units)
        self.ui.combo_UnitTab_Px.activated[int].connect(self.ut_update_current_unit)
        # <单位tab - 单位列表框> 点击框体 / 项选择改变 → 更新 <单位属性栏>、单位tab的属性记录（当前选中单位）
        self.ui.list_Units.itemClicked.connect(self.ut_update_current_unit)
        self.ui.list_Units.itemClicked.connect(self.ut_load_unit_attrs)
        self.ui.list_Units.itemSelectionChanged.connect(self.ut_update_current_unit)
        self.ui.list_Units.itemSelectionChanged.connect(self.ut_load_unit_attrs)
        # <单位tab - 确认更改> 点击 → 依据 <单位属性栏> 修改 <当前选中单位对象>
        # <单位tab - 确认更改> 点击 → （修改完毕后）更新一次 <单位列表框>
        # <单位tab - 放弃更改> 点击 → 更新 <单位属性栏>
        self.ui.button_UnitSaveChange.clicked.connect(self.ut_edit_unit_attrs)
        self.ui.button_UnitSaveChange.clicked.connect(self.ut_update_list_Units)
        self.ui.button_UnitQuitChange.clicked.connect(self.ut_load_unit_attrs)


    # 【单位tab】
    def ut_select_player(self):
        # <玩家下拉框> 选择一次时，执行：①获取当前玩家，②更新当前px_units，③刷新列表框，④取消选择。
        pass

    def ut_click_or_reselect_item(self):
        # <单位项> 被点击 / 选择变更时，执行：①获取当前单位，②载入单位属性
        pass

    def ut_new_unit(self):
        # <新增单位> 按钮点击时，执行：①修改单位属性，②刷新列表框
        # 如果玩家有变动，则
        pass

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
        print("ut_update_current_px_units")

    def ut_update_current_unit(self):
        """更新单位tab的属性记录： <单位列表框> 里的 <current_unit>。若未选中，则为None。"""
        # 定位单位列表中当前选中项的index
        current_index = self.ui.list_Units.currentRow()
        if current_index >= 0:
            # 定位index对应的Unit对象
            current_px_units = self.unitTabAttrs["current_px_units"]
            self.unitTabAttrs["current_unit"] = current_px_units[current_index]
        else:
            self.unitTabAttrs["current_unit"] = None
        print("ut_update_current_unit")

    def ut_update_list_Units(self):
        """收集当前玩家的单位，编写文本项，并逐一加入单位列表框实现更新"""
        # 编写单位项，逐个加入列表中
        unit_items = []
        current_px_units: list = self.unitTabAttrs["current_px_units"]  # 属于当前玩家的单位对象列表：[{单位1}, {单位2} ...]
        for unit in current_px_units:
            map_id = unit.reference_id  # 地图ID
            type_name_en = unit.name  # 种类名称(英文)
            type_id = unit.unit_const  # 种类ID
            unit_items.append(f"{map_id}: {type_name_en} {{{type_id}}}")
        # 加入到 <单位列表框> 中
        self.ui.list_Units.clear()
        self.ui.list_Units.addItems(unit_items)
        print("ut_update_list_Units")

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
            self.ui.edit_UnitMapID.setText(str(current_unit.reference_id))
            self.ui.edit_UnitGarrisonInID.setText(str(current_unit.garrisoned_in_id))
            self.ui.combo_UnitOwner.setCurrentIndex(current_unit.player.value)
        else:
            print("未选择任何单位")
        print("ut_load_unit_attrs")

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
            current_unit.reference_id = int(self.ui.edit_UnitMapID.text())
            current_unit.garrisoned_in_id = int(self.ui.edit_UnitGarrisonInID.text())
            # current_unit._player = self.ui.combo_UnitOwner.currentIndex()   # 可以这么改。但为了避免aoesp作者暗改机制，用他给的方法更好
            new_player_id = PlayerId(self.ui.combo_UnitOwner.currentIndex())
            self.scenario.unit_manager.change_ownership(current_unit, new_player_id)
        else:
            # print("未选择任何单位")
            QMessageBox.critical(self.ui, "错误", "未选择任何单位，请重试")
        print("ut_edit_unit_attrs")

    def ut_add_new_unit(self):
        """给当前玩家创建新的Unit对象（选择所有玩家时，会给盖亚加），"""
        pass

# 读取场景
read_file = r"C:/Users/acer/Games/Age of Empires 2 DE/76561199002600352/resources/_common/scenario/default0.aoe2scenario"
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
