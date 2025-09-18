from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Intent:
    name: str
    text: str
    arg: Optional[str] = None


class NLU:
    """Very simple chat NLU: time/date/exit/list_voices/echo."""

    def parse(self, text: Optional[str]) -> Optional[Intent]:
        if not text:
            return None
        t = text.strip().lower()
        if not t:
            return None

        # exit
        if re.search(r"\b(exit|quit|stop|goodbye|bye)\b", t):
            return Intent("exit", text)

        # time questions
        if re.search(r"\b(time|what's the time|what time is it)\b", t):
            return Intent("time", text)

        # date/day questions
        if re.search(r"\b(date|what's the date|what day is it|day today)\b", t):
            return Intent("date", text)

        # list voices
        if re.search(r"\b(list|show|available) voices\b", t):
            return Intent("list_voices", text)

        # default: echo back
        return Intent("echo", text)
