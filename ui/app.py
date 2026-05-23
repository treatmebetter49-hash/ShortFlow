import customtkinter as ctk
import pandas as pd

from modules import config_manager
from ui.settings_tab import SettingsTab
from ui.brain_tab import BrainTab
from ui.machine_tab import MachineTab
from ui.onboarding_music import OnboardingMusic

_TAB_BRAIN = "🧠  Brain"
_TAB_MACHINE = "⚙️  Machine"
_TAB_SETTINGS = "🔧  Settings"


class App(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
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
        cfg = config_manager.load()
        if not cfg.get("first_run_music_setup_done", False):
            self.after(400, lambda: OnboardingMusic(self))

    def _build(self):
        self._tabs = ctk.CTkTabview(self)
        self._tabs.pack(fill="both", expand=True, padx=12, pady=12)

        for name in (_TAB_BRAIN, _TAB_MACHINE, _TAB_SETTINGS):
            self._tabs.add(name)

        self._settings = SettingsTab(self._tabs.tab(_TAB_SETTINGS))
        self._settings.pack(fill="both", expand=True)

        self._brain = BrainTab(
            self._tabs.tab(_TAB_BRAIN),
            get_config=self._settings.get_config,
            on_go_to_machine=self._go_to_machine,
        )
        self._brain.pack(fill="both", expand=True)

        self._machine = MachineTab(
            self._tabs.tab(_TAB_MACHINE),
            get_config=self._settings.get_config,
        )
        self._machine.pack(fill="both", expand=True)

        self._tabs.set(_TAB_BRAIN)

    def _go_to_machine(self, df: pd.DataFrame, topic: str = "", project_dir=None):
        self._machine.load_from_brain(df, topic, project_dir)
        self._tabs.set(_TAB_MACHINE)
