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