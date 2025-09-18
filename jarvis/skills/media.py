from __future__ import annotations

import time

import pyautogui as pag


class MediaSkill:
    def play_pause(self) -> str:
        pag.press("playpause")
        return "Toggled play/pause."

    def volume_up(self, steps: int = 2) -> str:
        for _ in range(max(1, steps)):
            pag.press("volumeup")
            time.sleep(0.05)
        return "Volume up."

    def volume_down(self, steps: int = 2) -> str:
        for _ in range(max(1, steps)):
            pag.press("volumedown")
            time.sleep(0.05)
        return "Volume down."

    def mute(self) -> str:
        pag.press("volumemute")
        return "Muted."

    def unmute(self) -> str:
        pag.press("volumeup")
        return "Unmuted."
