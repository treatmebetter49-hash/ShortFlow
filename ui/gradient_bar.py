import tkinter as tk

from ui import theme

_GOLD_DARK = tuple(int(theme.GOLD_DARK[i:i + 2], 16) for i in (1, 3, 5))
_GOLD_HI = tuple(int(theme.GOLD_HI[i:i + 2], 16) for i in (1, 3, 5))
_BG = (18, 16, 12)


def _lerp(a, b, t):
    return int(a + (b - a) * t)


def _hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


class GradientProgressBar(tk.Canvas):
    def __init__(self, master, height=6, **kwargs):
        kwargs.setdefault("highlightthickness", 0)
        kwargs.setdefault("bd", 0)
        kwargs.setdefault("bg", "#0b0b0f")
        super().__init__(master, height=height, **kwargs)
        self._value = 0.0
        self.bind("<Configure>", self._redraw)

    def set(self, value: float):
        self._value = max(0.0, min(1.0, value))
        self._redraw()

    def _redraw(self, _event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1:
            return
        filled = int(w * self._value)
        # background
        self.create_rectangle(0, 0, w, h, fill=_hex(*_BG), outline="")
        if filled <= 0:
            return
        # gradient: draw thin vertical slices
        steps = max(filled, 1)
        for i in range(steps):
            t = i / max(steps - 1, 1)
            r = _lerp(_GOLD_DARK[0], _GOLD_HI[0], t)
            g = _lerp(_GOLD_DARK[1], _GOLD_HI[1], t)
            b = _lerp(_GOLD_DARK[2], _GOLD_HI[2], t)
            self.create_line(i, 0, i, h, fill=_hex(r, g, b))
