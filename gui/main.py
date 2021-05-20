# -*- coding=utf-8 -*-

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from AoE2ScenarioParser.aoe2_scenario import AoE2DEScenario
from AoE2ScenarioParser.datasets.players import PlayerId

class MainWindow:
    def __init__(self):
        # 从文件中加载UI定义
        self.ui = uic.loadUi("gui_main.ui")
        # 主窗口对接的场景（初始为空对象，无任何属性/方法）
        self.scenario = AoE2DEScenario()
        # 单位tab的属性：{当前选择玩家、当前玩家的unit对象列表}
        self.unitTabAttrs = {"current_player": 1,
                             "current_px_units": []}
        self.signal_connect_slot()


    def connect_scenario(self, scenario: AoE2DEScenario):
        """与场景对象对接"""
        self.scenario = scenario


    def signal_connect_slot(self):
        """将信号与槽链接"""
        # <单位tab - 玩家下拉框> 变动 → 更新 <单位列表框>
        self.ui.combo_UnitTab_Px.currentIndexChanged.connect(self.ut_get_current_px_units)
        self.ui.combo_UnitTab_Px.currentIndexChanged.connect(self.ut_update_list_Units)
        self.ui.list_Units.clicked.connect(self.ut_load_unit_attrs)
        self.ui.list_Units.itemSelectionChanged.connect(self.ut_load_unit_attrs)


    def ut_get_current_px_units(self):
        """用于单位tab。获取 <玩家下拉框> 所对应的 <玩家编号> 及其 <单位列表对象(unit_manager.units)>"""
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


    def ut_update_list_Units(self):
        """用于单位tab。收集当前玩家的单位，编写文本项，并逐一加入单位列表框实现更新"""
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


    def ut_load_unit_attrs(self):
        """读取单位列表框里当前所选单位的属性，逐个加入到右侧的单位属性栏里。"""
        # 定位单位列表中所选项的index、当前玩家、当前玩家单位列表
        current_index = self.ui.list_Units.currentRow()
        current_player = self.unitTabAttrs["current_player"]
        current_px_units = self.unitTabAttrs["current_px_units"]
        # 定位index对应的Unit对象
        current_unit = current_px_units[current_index]
        # 更新各项属性框的数值
        self.ui.spin_UnitPoint_X.setValue(current_unit.x)
        self.ui.spin_UnitPoint_Y.setValue(current_unit.y)
        self.ui.spin_UnitPoint_Z.setValue(current_unit.z)
        self.ui.spin_UnitRotation.setValue(current_unit.rotation)
        # self.ui.combo_UnitPhase.setCurrentIndex(round(current_unit.rotation / 3.1415927 * 4))
        self.ui.edit_UnitFrame.setText(str(current_unit.initial_animation_frame))
        self.ui.edit_UnitStatus.setText(str(current_unit.status))
        self.ui.edit_UnitMapID.setText(str(current_unit.reference_id))
        self.ui.edit_UnitGarrisonInID.setText(str(current_unit.garrisoned_in_id))
        self.ui.combo_UnitOwner.setCurrentIndex(current_unit.player.value)


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
