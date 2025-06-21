# core/models.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RecordMarkdown:
    header: str
    main: str
    appendix: str

