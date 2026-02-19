from enum import IntEnum, Enum

class TabIdx(IntEnum):
    CIF_SELECT = 0
    CIF_PREVIEW = 1
    APP_LOG = 2
    BUILDER_RESULT = 3
    MI_SELECT = 4
    MI_PREVIEW = 5
    PLACE_HOLDER = 99

    def get_tab_name(self) -> str:
        match self.name:
            case 'CIF_SELECT': return "CIFファイル設定"
            case 'CIF_PREVIEW': return "CIFプレビュー"
            case 'APP_LOG': return "アプリ動作ログ"
            case 'BUILDER_RESULT': return "Builder動作完了"
            case 'MI_SELECT': return "MIファイル設定"
            case 'MI_PREVIEW': return "GJF変換プレビュー"
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

