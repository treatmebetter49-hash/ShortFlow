import sys
import tkinter as tk
from pathlib import Path

import customtkinter as ctk
import pandas as pd

from modules import config_manager, scanner
from ui.settings_tab import SettingsTab
from ui.brain_tab import BrainTab
from ui.machine_tab import MachineTab
from ui.onboarding_music import OnboardingMusic
from ui import theme

_TAB_BRAIN = "🧠  Brain"
_TAB_MACHINE = "⚙️  Machine"
_TAB_SETTINGS = "🔧  Settings"


class App(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        # Gold-Akzent direkt überschreiben (Werte zentral in ui/theme.py)
        from customtkinter.windows.widgets.theme import ThemeManager
        ThemeManager.theme["CTkButton"]["fg_color"]       = [theme.GLASS["fg_color"], theme.GLASS["fg_color"]]
        ThemeManager.theme["CTkButton"]["hover_color"]    = [theme.GLASS["hover_color"], theme.GLASS["hover_color"]]
        ThemeManager.theme["CTkButton"]["border_color"]   = [theme.GOLD, theme.GOLD]
        ThemeManager.theme["CTkButton"]["border_width"]   = 1
        ThemeManager.theme["CTkButton"]["corner_radius"]  = 10
        ThemeManager.theme["CTkButton"]["text_color"]     = [theme.GOLD_HI, theme.GOLD_HI]
        for key in ("CTkCheckBox", "CTkRadioButton"):
            ThemeManager.theme[key]["fg_color"] = [theme.GOLD, theme.GOLD]
            ThemeManager.theme[key]["hover_color"] = [theme.GOLD_HOVER, theme.GOLD_HOVER]
        ThemeManager.theme["CTkSwitch"]["progress_color"] = [theme.GOLD, theme.GOLD]
        ThemeManager.theme["CTkOptionMenu"]["fg_color"]              = [theme.GLASS["fg_color"], theme.GLASS["fg_color"]]
        ThemeManager.theme["CTkOptionMenu"]["button_color"]          = [theme.GLASS["hover_color"], theme.GLASS["hover_color"]]
        ThemeManager.theme["CTkOptionMenu"]["button_hover_color"]    = [theme.GLASS["hover_color"], theme.GLASS["hover_color"]]
        ThemeManager.theme["CTkOptionMenu"]["text_color"]            = [theme.GOLD_HI, theme.GOLD_HI]
        ThemeManager.theme["CTkSegmentedButton"]["selected_color"]       = [theme.GLASS["hover_color"], theme.GLASS["hover_color"]]
        ThemeManager.theme["CTkSegmentedButton"]["selected_hover_color"] = [theme.GLASS["hover_color"], theme.GLASS["hover_color"]]
        super().__init__()
        self.withdraw()
        self.title("ShortFlow")
        self.minsize(900, 600)
        w, h = 1100, 720
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self._build()
        self.deiconify()
        self.scan_result = scanner.ScanResult()
        self.after(50, self._run_startup_scan)
        cfg = config_manager.load()
        if not cfg.get("first_run_music_setup_done", False):
            self.after(400, lambda: OnboardingMusic(self))

    def _build(self):
        # ── Gradient Header ───────────────────────────────────────────────────
        _BG = "#111118"
        self._header = ctk.CTkFrame(self, fg_color=_BG, corner_radius=0, height=52)
        self._header.pack(fill="x")
        self._header.pack_propagate(False)

        inner = ctk.CTkFrame(self._header, fg_color=_BG, corner_radius=0)
        inner.pack(side="left", padx=20, pady=10)

        _GOLD_DARK = tuple(int(theme.GOLD_DARK[i:i + 2], 16) for i in (1, 3, 5))
        _GOLD_HI = tuple(int(theme.GOLD_HI[i:i + 2], 16) for i in (1, 3, 5))
        text = "ShortFlow"
        for i, ch in enumerate(text):
            t = i / max(len(text) - 1, 1)
            r = int(_GOLD_DARK[0] + (_GOLD_HI[0] - _GOLD_DARK[0]) * t)
            g = int(_GOLD_DARK[1] + (_GOLD_HI[1] - _GOLD_DARK[1]) * t)
            b = int(_GOLD_DARK[2] + (_GOLD_HI[2] - _GOLD_DARK[2]) * t)
            col = f"#{r:02x}{g:02x}{b:02x}"
            lbl = ctk.CTkLabel(inner, text=ch,
                               font=ctk.CTkFont(family="Helvetica", size=26, weight="bold"),
                               text_color=col, fg_color=_BG)
            lbl.pack(side="left")

        ctk.CTkFrame(self._header, fg_color="#2a2a3a", corner_radius=0, height=1).pack(
            side="bottom", fill="x"
        )

        self._tabs = ctk.CTkTabview(self)
        self._tabs.pack(fill="both", expand=True, padx=12, pady=(4, 4))

        for name in (_TAB_BRAIN, _TAB_MACHINE, _TAB_SETTINGS):
            self._tabs.add(name)

        self._settings = SettingsTab(self._tabs.tab(_TAB_SETTINGS))
        self._settings.pack(fill="both", expand=True)

        self._brain = BrainTab(
            self._tabs.tab(_TAB_BRAIN),
            get_config=self._settings.get_config,
            on_go_to_machine=self._go_to_machine,
            get_scan_result=lambda: self.scan_result,
        )
        self._brain.pack(fill="both", expand=True)

        self._machine = MachineTab(
            self._tabs.tab(_TAB_MACHINE),
            get_config=self._settings.get_config,
        )
        self._machine.pack(fill="both", expand=True)

        self._tabs.set(_TAB_BRAIN)

        self._status_bar = ctk.CTkLabel(
            self,
            text="Ordner werden gescannt...",
            anchor="w",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
        )
        self._status_bar.pack(fill="x", padx=14, pady=(0, 6))

    def _run_startup_scan(self):
        try:
            cfg = config_manager.load()
            output_dir = cfg.get("output_dir", "").strip()
            if output_dir:
                self.scan_result = scanner.scan_shorts_base(Path(output_dir))
            self._status_bar.configure(text=self.scan_result.status_text)
        except Exception:
            self._status_bar.configure(text="Scan fehlgeschlagen")

    def _go_to_machine(self, df: pd.DataFrame, topic: str = "", project_dir=None):
        self._machine.load_from_brain(df, topic, project_dir)
        self._tabs.set(_TAB_MACHINE)
