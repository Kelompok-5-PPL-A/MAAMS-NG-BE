from enum import Enum

class ValidationType(Enum):
    NORMAL = 'normal'
    ROOT = 'root'
    FALSE = 'false'
    ROOT_TYPE = 'root_type'

class FilterType(Enum):
    SEMUA = 'semua'
    TOPIK = 'topik'
    JUDUL = 'judul'
    PENGGUNA = 'pengguna'

class HistoryType(Enum):
    LAST_WEEK = 'last_week'
    OLDER = 'older'