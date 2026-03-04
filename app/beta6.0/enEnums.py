from enum import IntEnum, Enum

class TabIdx(IntEnum):
    CIF_SELECT = 0
    CIF_PREVIEW = 1
    APP_LOG = 2
    BUILDER_RESULT = 3
    MI_SELECT = 4
    GJF_PREVIEW = 5
    PLACE_HOLDER = 99

    def get_tab_name(self) -> str:
        match self.name:
            case 'CIF_SELECT': return "CIFファイル設定"
            case 'CIF_PREVIEW': return "CIFプレビュー"
            case 'APP_LOG': return "アプリ動作ログ"
            case 'BUILDER_RESULT': return "Builder動作完了"
            case 'MI_SELECT': return "MIファイル設定"
            case 'GJF_PREVIEW': return "GJF変換プレビュー"
            case 'PLACE_HOLDER': return "プレースホルダ"

class BtmBtnIdx(IntEnum):
    OTHER_FUNC2 = 3
    OTHER_FUNC1 = 2
    EXIT_APP = 1
    NEXT_TAB = 0

    def get_def_txt(self) -> str:
        match self.name:
            case 'EXIT_APP': return "ExitApp"
            case 'NEXT_TAB': return "Next"
            case 'OTHER_FUNC1': return "Func1"
            case 'OTHER_FUNC2': return "Func2"

class FilePickerIdx(Enum):
    PICK_BUILDER = "Builder.exe Path"
    PICK_CIF = "CIF File Path"
    PICK_TXT = "Text File Path"
    SAVE_TXT = "Text Output Path"
    PICK_MI = "MI File Path"
    PICK_GJF = "Based GJF File Path"
    SAVE_GJF = "GJF Output Path"

    def get_file_type(self) -> str:
        match self.name:
            case 'PICK_BUILDER': return "exe"
            case 'PICK_CIF': return "cif"
            case 'PICK_TXT': return "txt"
            case 'SAVE_TXT': return "txt"
            case 'PICK_MI': return "mi"
            case 'PICK_GJF': return "gjf"
            case 'SAVE_GJF': return "gjf"

class CellDataLbl(Enum):
    STATE = "state"
    DATA_NAME = "data_name"
    SPACE_G_IT_NUM = "_space_group_IT_number"
    SPACE_G_NAME = "_space_group_name_H-M_alt"
    CELL_LEN_A = "_cell_length_a"
    CELL_LEN_B = "_cell_length_b"
    CELL_LEN_C = "_cell_length_c"
    CELL_ANGLE_A = "_cell_angle_alpha"
    CELL_ANGLE_B = "_cell_angle_beta"
    CELL_ANGLE_C = "_cell_angle_gamma"
    CELL_VOLUME = "_cell_volume"
    ATOMS = "atoms"

class SettingLabel(Enum):
    APP_VER_TYPE = "app_ver_type"
    APP_VER_NUM = "app_ver_num"
    BUILDER_PATH = "builder_path"
    CIF_PATH = "cif_path"
    TXT_PATH = "txt_path"
    MI_PATH = "mi_path"
    GJF_BASE_PATH = "gjf_base_path"

class AppVerType(IntEnum):
    ALPHA = 0
    BETA = 3
    RELEASE = 10