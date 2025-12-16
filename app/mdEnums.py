from enum import IntEnum, Enum
from typing import Optional

class SettingLabel(Enum):
    FILE_NAME = "name"
    APP_VER_TYPE = "app_ver_type"
    APP_VER_NUM = "app_ver_num"
    BUILDER_PATH = "builder_path"
    CIF_PATH = "cif_path"
    TXT_PATH = "txt_path"


class CellDataLabel(IntEnum):
    STATE = 0
    FILE_NAME = 1
    SPACE_GROUP_IT_NUM = 2
    SPACE_GROUP_NAME = 3
    CELL_LENGTH = 4
    CELL_ANGLE = 5
    CELL_VOLUME = 6
    ATOM = 7

    def get_label_str(self)->str:
        match self.name:
            case 'STATE': return 'MakeCi_'
            case 'FILE_NAME': return 'fileName'
            case 'SPACE_GROUP_IT_NUM': return 'space_group_IT_number'
            case 'SPACE_GROUP_NAME': return 'space_group_name_H-M_alt'
            case 'CELL_LENGTH': return 'cell_length_'
            case 'CELL_ANGLE': return 'cell_angle_'
            case 'CELL_VOLUME': return 'cell_volume'
            case 'ATOM': return ''

    def get_label_re(self) -> str:
        match self.name:
            case 'STATE': return 'MakeCi_.*'
            case 'FILE_NAME': return 'fileName'
            case 'SPACE_GROUP_IT_NUM': return 'space_group_IT_number'
            case 'SPACE_GROUP_NAME': return 'space_group_name_H-M_alt'
            case 'CELL_LENGTH': return 'cell_length_'
            case 'CELL_ANGLE': return 'cell_angle_'
            case 'CELL_VOLUME': return 'cell_volume'
            case 'ATOM': return '[A-Z][a-z]?'

    def get_label_max_len(self)->int:
        match self.name:
            case 'ATOM': return 7
            case _: return 2

class TabIdx(IntEnum):
    FILE_PATH_SELECT = 0
    READ_DATA = 1
    BUILDER_LOG = 2
    BUILDER_RESULT = 3
    PLACE_HOLDER = 99

    def get_tab_name(self) -> str:
        match self.name:
            case 'FILE_PATH_SELECT': return "ファイル設定"
            case 'READ_DATA': return "読取結果"
            case 'BUILDER_LOG': return "Builderログ"
            case 'BUILDER_RESULT': return "Builder動作完了"
            case 'PLACE_HOLDER': return "**このタブは非表示タブです。**"


class BtmBtnIdx(IntEnum):
    NEXT_TAB = 0
    EXIT_APP = 1
    OTHER_FUNC1 = 2
    OTHER_FUNC2 = 3

    def get_btn_def_text(self) -> str:
        match self.name:
            case 'NEXT_TAB': return "Next"
            case 'EXIT_APP': return "AppExit"
            case 'OTHER_FUNC1': return "Func1"
            case 'OTHER_FUNC2': return "Func2"

class FilePickerIdx(IntEnum):
    BUILDER_PICK = 0
    CIF_PICK = 1
    OUTPUT_PICK = 2
    OUTPUT_SAVE = 3

    def get_fileType(self)->str:
        match self.name:
            case 'BUILDER_PICK':
                return "exe"
            case 'CIF_PICK':
                return "cif"
            case 'OUTPUT_PICK':
                return "txt"
            case 'OUTPUT_SAVE':
                return "txt"