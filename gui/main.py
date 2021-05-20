# -*- coding=utf-8 -*-

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from AoE2ScenarioParser.aoe2_scenario import AoE2DEScenario


class MainWindow:
    def __init__(self):
        # 从文件中加载UI定义
        self.ui = uic.loadUi("gui_main.ui")
        # 与场景对象挂钩
        self.scenario = AoE2DEScenario()
        self.signal_connect_slot()

    def connect_scenario(self, scenario: AoE2DEScenario):
        """与场景对象链接"""
        self.scenario = scenario

    def signal_connect_slot(self):
        """将信号与槽链接"""
        # <单位tab - 玩家下拉框> 变动 → 更新 <单位列表>
        self.ui.combo_UnitTab_Px.currentIndexChanged.connect(self.update_units_list)

    def update_units_list(self):
        """依据玩家下拉框的index收集玩家x的所有单位，然后更新到单位列表里。"""
        def gather_px_unit_items(player_):
            """ 收集某个玩家的单位项（用于放入UI单位列表框中）
                :param player_: 玩家ID（0=盖亚，1~8=玩家1~8）
                :return: list 单位项列表。格式：["地图ID: 种类名称 {种类ID}", ...]
            """
            unit_items_ = []
            units_of_px = scenario_units[player_]  # 属于该玩家的单位列表：[{第一个单位}, {第二个单位} ...]
            for unit in units_of_px:
                map_id = unit.reference_id  # 地图ID
                type_name_en = unit.name  # 种类名称(英文)
                type_id = unit.unit_const  # 种类ID
                unit_items_.append(f"{map_id}: {type_name_en} {{{type_id}}}")
            return unit_items_

        scenario_units = self.scenario.unit_manager.units     # 场景全单位列表：[ [盖亚单位], [P1单位] ... [P8单位] ]
        current_player = self.ui.combo_UnitTab_Px.currentIndex()  # 单位tab下的选择玩家（0=盖亚，1~8=P1~P8，9=全部玩家）
        print(f"下拉菜单选择了{current_player}")

        # 依据 '下拉框index' 收集 '玩家x的所有单位'
        unit_items = []
        if 0 <= current_player <= 8:
            # 盖亚, 玩家1~8
            unit_items = gather_px_unit_items(current_player)
        elif current_player == 9:
            # 所有玩家
            for player in range(0, 8):
                unit_items.extend(gather_px_unit_items(player))
        else:
            print("错误：选择了未知的玩家项：" + current_player)

        # 单位项加入到AOESE单位列表中
        self.ui.list_Units.clear()
        self.ui.list_Units.addItems(unit_items)



# 读取场景
read_file = r"C:/Users/acer/Games/Age of Empires 2 DE/76561199002600352/resources/_common/scenario/default0.aoe2scenario"
scenarioManager = AoE2DEScenario.from_file(read_file)
# 创建AOESE程序和主窗口
app = QApplication([])
mainWindow = MainWindow()
# 主窗口 & 场景 相链接
mainWindow.connect_scenario(scenarioManager)

# 场景信息载入信息tab
game_version = scenarioManager.game_version
scenario_version = scenarioManager.scenario_version
mainWindow.ui.edit_GameVersion.setText(game_version)
mainWindow.ui.edit_ScenarioVersion.setText(scenario_version)


# 显示AOESE程序和窗口
mainWindow.ui.show()
app.exec_()
