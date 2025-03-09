from pydantic import BaseModel
from typing import List


class FieldValuesDataClass(BaseModel):
    pengguna: List[str] = []  # untuk guest
    judul: List[str]
    topik: List[str]
