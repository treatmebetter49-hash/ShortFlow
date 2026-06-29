import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

from modules import config_manager


class SettingsTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._track_vars: list[tk.StringVar] = []
        self._musik_toggle_var = tk.BooleanVar(value=False)
        self._build()
        self._load()

    def _build(self):
        self.columnconfigure(1, weight=1)

        # Gemini disabled until provider-specific compatibility is implemented.
        # To re-enable: uncomment the SegmentedButton and Gemini key rows below.
        self._provider_var = tk.StringVar(value="openai")
        # ctk.CTkLabel(self, text="Textmodell:").grid(row=0, column=0, sticky="w", padx=20, pady=(40, 10))
        # ctk.CTkSegmentedButton(
        #     self,
        #     values=["openai", "gemini"],
        #     variable=self._provider_var,
        # ).grid(row=0, column=1, sticky="w", padx=(0, 20), pady=(40, 10))

        ctk.CTkLabel(self, text="OpenAI API-Key:").grid(row=1, column=0, sticky="w", padx=20, pady=(40, 10))
        self._openai_var = tk.StringVar()
        ctk.CTkEntry(self, textvariable=self._openai_var, show="•", width=460).grid(
            row=1, column=1, sticky="ew", padx=(0, 20), pady=(40, 10)
        )

        self._gemini_var = tk.StringVar()
        # ctk.CTkLabel(self, text="Gemini API-Key:").grid(row=2, column=0, sticky="w", padx=20, pady=10)
        # ctk.CTkEntry(self, textvariable=self._gemini_var, show="•", width=460).grid(
        #     row=2, column=1, sticky="ew", padx=(0, 20), pady=10
        # )

        ctk.CTkLabel(self, text="Bildgenerator API-Key:").grid(row=3, column=0, sticky="w", padx=20, pady=10)
        self._fal_var = tk.StringVar()
        ctk.CTkEntry(self, textvariable=self._fal_var, show="•", width=460).grid(
            row=3, column=1, sticky="ew", padx=(0, 20), pady=10
        )

        ctk.CTkLabel(self, text="Output-Ordner:").grid(row=4, column=0, sticky="w", padx=20, pady=10)
        dir_row = ctk.CTkFrame(self, fg_color="transparent")
        dir_row.grid(row=4, column=1, sticky="ew", padx=(0, 20), pady=10)
        dir_row.columnconfigure(0, weight=1)
        self._dir_var = tk.StringVar()
        ctk.CTkEntry(dir_row, textvariable=self._dir_var).grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(dir_row, text="Durchsuchen", width=120, command=self._browse).grid(
            row=0, column=1, padx=(8, 0)
        )

        ctk.CTkLabel(self, text="Netlify Token:").grid(row=5, column=0, sticky="w", padx=20, pady=10)
        self._netlify_var = tk.StringVar()
        ctk.CTkEntry(self, textvariable=self._netlify_var, show="•", width=460).grid(
            row=5, column=1, sticky="ew", padx=(0, 20), pady=10
        )

        ctk.CTkLabel(self, text="Telegram Bot-Token:").grid(row=6, column=0, sticky="w", padx=20, pady=10)
        self._tg_bot_var = tk.StringVar()
        ctk.CTkEntry(self, textvariable=self._tg_bot_var, show="•", width=460).grid(
            row=6, column=1, sticky="ew", padx=(0, 20), pady=10
        )

        ctk.CTkLabel(self, text="Telegram Chat-ID:").grid(row=7, column=0, sticky="w", padx=20, pady=10)
        self._tg_chat_var = tk.StringVar()
        ctk.CTkEntry(self, textvariable=self._tg_chat_var, width=460).grid(
            row=7, column=1, sticky="ew", padx=(0, 20), pady=10
        )

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=8, column=0, columnspan=2, sticky="w", padx=20, pady=(28, 0))
        ctk.CTkButton(btn_row, text="SPEICHERN", command=self._save).grid(row=0, column=0)
        self._status_lbl = ctk.CTkLabel(btn_row, text="")
        self._status_lbl.grid(row=0, column=1, padx=(14, 0))

        # ── Musik-Zuordnung ───────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="── Musik-Zuordnung",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).grid(row=9, column=0, columnspan=2, sticky="w", padx=20, pady=(36, 6))

        ctk.CTkSwitch(
            self,
            text="Musik-Mapping aktivieren",
            variable=self._musik_toggle_var,
        ).grid(row=10, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 14))

        musik_grid = ctk.CTkFrame(self, fg_color="transparent")
        musik_grid.grid(row=11, column=0, columnspan=2, sticky="w", padx=20)
        musik_grid.columnconfigure(1, weight=1)

        tracks = config_manager.DEFAULTS["music_tracks"]
        self._track_vars = []
        for i, entry in enumerate(tracks):
            ctk.CTkLabel(
                musik_grid,
                text=entry["label"],
                font=ctk.CTkFont(size=12),
                anchor="w",
                width=200,
            ).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 14))

            var = tk.StringVar()
            self._track_vars.append(var)
            ctk.CTkEntry(musik_grid, textvariable=var, width=300).grid(
                row=i, column=1, sticky="w", pady=5
            )

    def _load(self):
        cfg = config_manager.load()
        self._provider_var.set(cfg.get("provider", "openai"))
        self._openai_var.set(cfg["openai_key"])
        self._gemini_var.set(cfg.get("gemini_key", ""))
        self._fal_var.set(cfg["fal_key"])
        self._dir_var.set(cfg["output_dir"])
        self._netlify_var.set(cfg.get("netlify_token", ""))
        self._tg_bot_var.set(cfg.get("telegram_bot_token", ""))
        self._tg_chat_var.set(cfg.get("telegram_chat_id", ""))
        self._musik_toggle_var.set(cfg.get("music_mapping_enabled", False))
        tracks = cfg.get("music_tracks", config_manager.DEFAULTS["music_tracks"])
        for i, var in enumerate(self._track_vars):
            if i < len(tracks):
                var.set(tracks[i].get("track", ""))

    def _browse(self):
        path = filedialog.askdirectory(title="Output-Ordner wählen")
        if path:
            self._dir_var.set(path)

    def _save(self):
        cfg = config_manager.load()
        tracks = cfg.get("music_tracks", config_manager.DEFAULTS["music_tracks"])
        for i, var in enumerate(self._track_vars):
            if i < len(tracks):
                tracks[i]["track"] = var.get().strip()

        config_manager.save({
            **cfg,
            "provider": self._provider_var.get(),
            "openai_key": self._openai_var.get().strip(),
            "gemini_key": self._gemini_var.get().strip(),
            "fal_key": self._fal_var.get().strip(),
            "output_dir": self._dir_var.get().strip(),
            "netlify_token": self._netlify_var.get().strip(),
            "telegram_bot_token": self._tg_bot_var.get().strip(),
            "telegram_chat_id": self._tg_chat_var.get().strip(),
            "music_mapping_enabled": self._musik_toggle_var.get(),
            "music_tracks": tracks,
        })
        self._status_lbl.configure(text="Gespeichert ✓", text_color="#4CAF50")
        self.after(3000, lambda: self._status_lbl.configure(text=""))

    def get_config(self) -> dict:
        return config_manager.load()
