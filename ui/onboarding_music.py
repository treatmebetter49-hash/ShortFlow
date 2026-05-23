import tkinter as tk
import customtkinter as ctk

from modules import config_manager


class OnboardingMusic(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("ShortFlow – Einrichtung")
        self.resizable(False, False)
        w, h = 520, 360
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
        self.grab_set()
        self.lift()
        self.focus_force()

        self._cfg = config_manager.load()
        self._track_vars: list[tk.StringVar] = []

        self._frame = ctk.CTkFrame(self, fg_color="transparent")
        self._frame.pack(fill="both", expand=True, padx=32, pady=28)

        self._screen_a = self._build_screen_a()
        self._screen_b = self._build_screen_b()
        self._screen_c = self._build_screen_c()

        self._show(self._screen_a)

    # ── Screen helpers ────────────────────────────────────────────────────────

    def _show(self, target):
        for s in (self._screen_a, self._screen_b, self._screen_c):
            s.pack_forget()
        target.pack(fill="both", expand=True)

    # ── Screen A – Frage ──────────────────────────────────────────────────────

    def _build_screen_a(self) -> ctk.CTkFrame:
        f = ctk.CTkFrame(self._frame, fg_color="transparent")

        ctk.CTkLabel(
            f,
            text="Noch eine Frage, dann geht's los.",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        ).pack(anchor="w", pady=(0, 14))

        ctk.CTkLabel(
            f,
            text=(
                "Nutzt du feste Musiktitel für deine Shorts?\n\n"
                "ShortFlow kann automatisch den passenden Track\n"
                "pro Short vorschlagen – basierend auf der Energie\n"
                "des Inhalts."
            ),
            font=ctk.CTkFont(size=13),
            justify="left",
            anchor="w",
        ).pack(anchor="w", pady=(0, 28))

        btn_frame = ctk.CTkFrame(f, fg_color="transparent")
        btn_frame.pack(anchor="w")

        ctk.CTkButton(
            btn_frame,
            text="Ja, einrichten",
            width=148,
            command=lambda: self._show(self._screen_c),
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Nein, später",
            width=120,
            fg_color="transparent",
            border_width=1,
            command=self._skip,
        ).grid(row=0, column=1, padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Was bedeutet das?",
            width=160,
            fg_color="transparent",
            border_width=1,
            command=lambda: self._show(self._screen_b),
        ).grid(row=0, column=2)

        return f

    # ── Screen B – Erklärung ─────────────────────────────────────────────────

    def _build_screen_b(self) -> ctk.CTkFrame:
        f = ctk.CTkFrame(self._frame, fg_color="transparent")

        ctk.CTkLabel(
            f,
            text="Was ist Musik-Mapping?",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        ).pack(anchor="w", pady=(0, 14))

        ctk.CTkLabel(
            f,
            text=(
                "Viele Creator nutzen für bestimmte Short-Arten\n"
                "immer ähnliche Musik.\n\n"
                "Beispiel:\n"
                "  • Aggressive Shorts  →  Phonk-Track\n"
                "  • Spannende Shorts   →  Action-Musik\n"
                "  • Wissens-Shorts     →  Ruhige Musik\n\n"
                "ShortFlow erkennt die Energie jedes Shorts automatisch\n"
                "und schlägt dir den passenden Track vor.\n\n"
                "Das ist komplett optional und jederzeit änderbar."
            ),
            font=ctk.CTkFont(size=13),
            justify="left",
            anchor="w",
        ).pack(anchor="w", pady=(0, 28))

        ctk.CTkButton(
            f,
            text="Verstanden",
            width=140,
            command=lambda: self._show(self._screen_a),
        ).pack(anchor="w")

        return f

    # ── Screen C – Einrichten ────────────────────────────────────────────────

    def _build_screen_c(self) -> ctk.CTkFrame:
        f = ctk.CTkFrame(self._frame, fg_color="transparent")

        ctk.CTkLabel(
            f,
            text="Deine Musik-Zuordnung",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        ).pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(
            f,
            text="Trage deinen Track-Namen pro Energie-Typ ein (kann leer bleiben).",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
        ).pack(anchor="w", pady=(0, 18))

        grid = ctk.CTkFrame(f, fg_color="transparent")
        grid.pack(anchor="w", fill="x")
        grid.columnconfigure(1, weight=1)

        tracks = self._cfg.get("music_tracks", config_manager.DEFAULTS["music_tracks"])
        self._track_vars = []

        for i, entry in enumerate(tracks):
            ctk.CTkLabel(
                grid,
                text=entry["label"],
                font=ctk.CTkFont(size=13),
                anchor="w",
                width=200,
            ).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 14))

            var = tk.StringVar(value=entry.get("track", ""))
            self._track_vars.append(var)
            ctk.CTkEntry(grid, textvariable=var, width=240).grid(
                row=i, column=1, sticky="ew", pady=5
            )

        ctk.CTkButton(
            f,
            text="Speichern & loslegen",
            width=200,
            command=self._save_and_close,
        ).pack(anchor="w", pady=(22, 0))

        return f

    # ── Actions ───────────────────────────────────────────────────────────────

    def _skip(self):
        cfg = config_manager.load()
        cfg["first_run_music_setup_done"] = True
        cfg["music_mapping_enabled"] = False
        config_manager.save(cfg)
        self.destroy()

    def _save_and_close(self):
        cfg = config_manager.load()
        tracks = cfg.get("music_tracks", config_manager.DEFAULTS["music_tracks"])
        for i, var in enumerate(self._track_vars):
            if i < len(tracks):
                tracks[i]["track"] = var.get().strip()
        cfg["music_tracks"] = tracks
        cfg["first_run_music_setup_done"] = True
        cfg["music_mapping_enabled"] = True
        config_manager.save(cfg)
        self.destroy()
