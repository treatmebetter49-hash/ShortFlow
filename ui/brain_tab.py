import calendar
import datetime
import re
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Callable

import customtkinter as ctk
import pandas as pd

from modules import brain, table, netlify_telegram, config_manager
from ui.gradient_bar import GradientProgressBar
from ui.theme import GLASS as _GLASS

def _unique_html_path(base: Path) -> Path:
    if not base.exists():
        return base
    stem, suffix, parent = base.stem, base.suffix, base.parent
    i = 2
    while True:
        candidate = parent / f"{stem}-{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


_PREVIEW_COLS = ["Short", "Datum", "Tag", "Hook", "Text", "Titel", "Status"]
_COL_WIDTHS = {"Short": 80, "Datum": 70, "Tag": 50, "Hook": 160, "Text": 160, "Titel": 140, "YTBeschreibung": 160, "IGBeschreibung": 160, "Prompts": 200, "Status": 90}
_TRUNCATE = 60
_MONTHS_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni",
              "Juli", "August", "September", "Oktober", "November", "Dezember"]


class BrainTab(ctk.CTkFrame):
    def __init__(self, master, get_config: Callable, on_go_to_machine: Callable, get_scan_result: Callable | None = None):
        super().__init__(master, fg_color="transparent")
        self._get_config = get_config
        self._on_go_to_machine = on_go_to_machine
        self._get_scan_result = get_scan_result
        self._df: pd.DataFrame | None = None
        self._project_dir = None
        self._html_path: Path | None = None
        self._file_stem = "Short-Tabelle"
        self._animating = False
        self._elapsed_secs = 0
        self._current_phase = 0
        self._build()

    def _build(self):
        # ── Mode toggle ───────────────────────────────────────────────────────
        mode_row = ctk.CTkFrame(self, fg_color="transparent")
        mode_row.pack(fill="x", padx=20, pady=(20, 4))
        self._mode_var = tk.StringVar(value="einzeln")
        ctk.CTkRadioButton(
            mode_row, text="Einzeln", variable=self._mode_var, value="einzeln",
            command=self._on_mode_change,
        ).pack(side="left", padx=(0, 16))
        ctk.CTkRadioButton(
            mode_row, text="Monat", variable=self._mode_var, value="monat",
            command=self._on_mode_change,
        ).pack(side="left")

        # ── Top bar ───────────────────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(0, 0))

        ctk.CTkLabel(top, text="Thema:").pack(side="left")
        self._topic_var = tk.StringVar()
        ctk.CTkEntry(top, textvariable=self._topic_var, width=150).pack(side="left", padx=(8, 20))

        # Container hält beide Modi — nimmt feste Position ein
        _cnt = ctk.CTkFrame(top, fg_color="transparent")
        _cnt.pack(side="left")

        # Einzeln-Bereich
        self._einzeln_frame = ctk.CTkFrame(_cnt, fg_color="transparent")
        self._einzeln_frame.pack(side="left")
        ctk.CTkLabel(self._einzeln_frame, text="Shorts:").pack(side="left")
        self._count_var = tk.StringVar(value="10")
        ctk.CTkOptionMenu(
            self._einzeln_frame, variable=self._count_var,
            values=[str(n) for n in range(1, 32)], width=75,
        ).pack(side="left", padx=(8, 20))

        # Monat-Bereich (initial versteckt)
        _now = datetime.datetime.now()
        self._monat_frame = ctk.CTkFrame(_cnt, fg_color="transparent")
        ctk.CTkLabel(self._monat_frame, text="Monat:").pack(side="left")
        self._month_var = tk.StringVar(value=_MONTHS_DE[_now.month - 1])
        ctk.CTkOptionMenu(
            self._monat_frame, variable=self._month_var, values=_MONTHS_DE,
            width=110, command=self._update_month_count,
        ).pack(side="left", padx=(8, 8))
        ctk.CTkLabel(self._monat_frame, text="Jahr:").pack(side="left")
        self._year_var = tk.StringVar(value=str(_now.year))
        _year_entry = ctk.CTkEntry(self._monat_frame, textvariable=self._year_var, width=60)
        _year_entry.pack(side="left", padx=(8, 8))
        _year_entry.bind("<KeyRelease>", self._update_month_count)
        _init_days = calendar.monthrange(_now.year, _now.month)[1]
        self._month_count_lbl = ctk.CTkLabel(self._monat_frame, text=f"→ {_init_days} Shorts")
        self._month_count_lbl.pack(side="left", padx=(4, 20))

        self._gen_btn = ctk.CTkButton(top, text="TABELLE GENERIEREN", command=self._start_generate,
                                      **_GLASS)
        self._gen_btn.pack(side="left")
        self._status_lbl = ctk.CTkLabel(top, text="Bereit")
        self._status_lbl.pack(side="left", padx=(16, 0))

        # ── Progress bar ──────────────────────────────────────────────────────
        self._progress_bar = GradientProgressBar(self, height=6)
        self._progress_bar.pack(fill="x", padx=20, pady=(8, 0))

        # ── Table preview ─────────────────────────────────────────────────────
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=12)

        self._canvas = tk.Canvas(preview_frame, bg="#1e1e1e", highlightthickness=0)
        h_scroll = ttk_scrollbar(preview_frame, orient="horizontal", command=self._canvas.xview)
        v_scroll = ttk_scrollbar(preview_frame, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        h_scroll.pack(side="bottom", fill="x")
        v_scroll.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._canvas.bind("<MouseWheel>", self._on_table_scroll)

        self._table_inner = ctk.CTkFrame(self._canvas, fg_color="transparent")
        self._canvas_window = self._canvas.create_window((0, 0), window=self._table_inner, anchor="nw")
        self._table_inner.bind("<Configure>", self._on_inner_configure)

        # ── Bottom buttons ────────────────────────────────────────────────────
        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.pack(fill="x", padx=20, pady=(0, 16))
        self._open_btn = ctk.CTkButton(bot, text="Tabelle öffnen", command=self._open_html,
                                       state="disabled", **_GLASS)
        self._open_btn.pack(side="left", padx=(0, 20))
        ctk.CTkButton(
            bot, text="→  WEITER ZU MACHINE",
            font=ctk.CTkFont(weight="bold"),
            command=self._go_to_machine,
            **_GLASS,
        ).pack(side="left")
        ctk.CTkButton(
            bot, text="iPhone IG Export",
            command=self._save_ig_html,
            **_GLASS,
        ).pack(side="left", padx=(16, 0))
        ctk.CTkButton(
            bot, text="Vorhandene Tabelle laden",
            command=self._load_project,
            **_GLASS,
        ).pack(side="right")
        self._hooks_btn = ctk.CTkButton(
            bot, text="Nur Hooks neu generieren",
            command=self._start_regenerate_hooks,
            state="disabled",
            **_GLASS,
        )
        self._hooks_btn.pack(side="right", padx=(0, 16))

    def _on_inner_configure(self, _event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_table_scroll(self, event):
        self._canvas.yview_scroll(int(-event.delta), "units")

    def _bind_scroll_recursive(self, widget):
        widget.bind("<MouseWheel>", self._on_table_scroll)
        for child in widget.winfo_children():
            self._bind_scroll_recursive(child)

    # ── Generation ────────────────────────────────────────────────────────────

    def _start_generate(self):
        topic = self._topic_var.get().strip()
        if not topic:
            messagebox.showwarning("Fehler", "Bitte ein Thema eingeben.")
            return
        count = self._get_count()
        cfg = self._get_config()
        start_date = self._get_start_date()
        provider = cfg.get("provider", "openai")
        api_key = cfg.get("gemini_key", "") if provider == "gemini" else cfg.get("openai_key", "")
        fallback_provider = "openai" if provider == "gemini" else "gemini"
        fallback_key = cfg.get("openai_key", "") if provider == "gemini" else cfg.get("gemini_key", "")
        start_num = 1
        existing_hooks: list[str] = []
        if self._get_scan_result:
            scan = self._get_scan_result()
            start_num = scan.next_short_num
            existing_hooks = scan.existing_hooks
        self._set_status("", busy=True)
        threading.Thread(
            target=self._generate,
            args=(topic, count, api_key, start_date, provider, fallback_key, fallback_provider, start_num, existing_hooks),
            daemon=True,
        ).start()

    def _on_mode_change(self):
        if self._mode_var.get() == "einzeln":
            self._monat_frame.pack_forget()
            self._einzeln_frame.pack(side="left")
        else:
            self._einzeln_frame.pack_forget()
            self._monat_frame.pack(side="left")
            self._update_month_count()

    def _update_month_count(self, *_):
        month = _MONTHS_DE.index(self._month_var.get()) + 1
        try:
            year = int(self._year_var.get())
        except ValueError:
            return
        days = calendar.monthrange(year, month)[1]
        self._month_count_lbl.configure(text=f"→ {days} Shorts")

    def _get_count(self) -> int:
        if self._mode_var.get() == "einzeln":
            return int(self._count_var.get())
        month = _MONTHS_DE.index(self._month_var.get()) + 1
        try:
            year = int(self._year_var.get())
        except ValueError:
            year = datetime.datetime.now().year
        return calendar.monthrange(year, month)[1]

    def _get_start_date(self):
        import datetime as _dt
        if self._mode_var.get() == "monat":
            month = _MONTHS_DE.index(self._month_var.get()) + 1
            try:
                year = int(self._year_var.get())
            except ValueError:
                year = _dt.datetime.now().year
            return _dt.date(year, month, 1)
        return _dt.date.today()

    def _generate(self, topic: str, count: int, key: str, start_date=None, provider: str = "openai", fallback_key: str = "", fallback_provider: str = "", start_num: int = 1, existing_hooks: list[str] | None = None):
        try:
            df = brain.generate_table(topic, count, key, start_date=start_date, provider=provider, fallback_key=fallback_key, fallback_provider=fallback_provider, start_num=start_num, existing_hooks=existing_hooks)
            self.after(0, self._on_success, df)
        except Exception as exc:
            import traceback
            print("\n─── FEHLER IN _generate ───")
            print(traceback.format_exc())
            print("──────────────────────────\n")
            self.after(0, self._on_error, str(exc))

    def _on_success(self, df: pd.DataFrame):
        self._animating = False
        self._current_phase = 0
        self._progress_bar.set(1.0)
        self._df = df
        self._render_table(df)
        self._gen_btn.configure(state="normal")
        self._hooks_btn.configure(state="normal")

        topic = self._topic_var.get().strip()
        cfg = self._get_config()
        output_dir = cfg.get("output_dir", "").strip()
        if not output_dir:
            output_dir = filedialog.askdirectory(title="Output-Ordner wählen")
        if output_dir:
            import re
            start_date = self._get_start_date()
            self._project_dir = brain.make_project_dir(topic, output_dir, month=start_date.month, year=start_date.year)
            clean = re.sub(r"[^\w\s-]", "", topic)
            clean = re.sub(r"\s+", "-", clean)
            clean = re.sub(r"-{2,}", "-", clean)
            clean = clean[:40]
            self._file_stem = f"{clean}-Short-Tabelle" if clean else "Short-Tabelle"
            self._auto_save_html(df, topic)
            self._status_lbl.configure(text=f"{len(df)} Shorts ✓  →  {topic}")
        else:
            self._status_lbl.configure(text=f"{len(df)} Shorts geladen ✓")

    def _on_error(self, msg: str):
        self._animating = False
        self._current_phase = 0
        self._progress_bar.set(0)
        self._gen_btn.configure(state="normal")
        self._status_lbl.configure(text="Fehler")
        messagebox.showerror("Fehler", msg)

    def _music_config(self) -> dict:
        cfg = self._get_config()
        return {
            "enabled": cfg.get("music_mapping_enabled", False),
            "tracks": cfg.get("music_tracks", []),
        }

    def _auto_save_html(self, df: pd.DataFrame, topic: str):
        try:
            base_path = self._project_dir / f"{self._file_stem}.html"
            html_path = base_path
            table.append_to_html(df, html_path, topic=topic, music_config=self._music_config())
            table.save_prompts_json(df, self._project_dir / ".prompts.json")
            errors = table.validate_html(html_path)
            if errors:
                print(f"[HTML VALIDATION FEHLER] {errors}")
            self._html_path = html_path
            self._open_btn.configure(state="normal")
        except Exception as exc:
            print(f"[HTML AUTO-SAVE FEHLER] {exc}")

    def _save_ig_html(self):
        if self._df is None:
            messagebox.showwarning("Fehler", "Keine Tabelle vorhanden.")
            return
        try:
            if self._project_dir:
                base_path = self._project_dir / f"{self._file_stem}-IG.html"
                ig_path = _unique_html_path(base_path)
            else:
                p = filedialog.asksaveasfilename(
                    defaultextension=".html",
                    filetypes=[("HTML", "*.html")],
                    initialfile=f"{self._file_stem}-IG",
                )
                if not p:
                    return
                ig_path = Path(p)
            table.save_ig_html(self._df, ig_path, topic=self._topic_var.get().strip())
            self._status_lbl.configure(text=f"IG Export: {ig_path.name}")
            webbrowser.open(ig_path.as_uri())

            # Netlify + Telegram (optional — nur wenn Tokens gesetzt)
            cfg = config_manager.load()
            netlify_token = cfg.get("netlify_token", "")
            tg_bot = cfg.get("telegram_bot_token", "")
            tg_chat = cfg.get("telegram_chat_id", "")
            if netlify_token and tg_bot and tg_chat:
                def _deploy():
                    try:
                        self._status_lbl.configure(text="Lade auf Netlify hoch...")
                        site_id = cfg.get("netlify_site_id", "")
                        live_url = netlify_telegram.upload_to_netlify(ig_path, netlify_token, site_id)
                        topic = self._topic_var.get().strip()
                        netlify_telegram.send_telegram(
                            tg_bot, tg_chat,
                            f"📱 <b>ShortFlow IG Export</b>\n{topic}\n\n{live_url}"
                        )
                        self._status_lbl.configure(text=f"✅ Telegram-Link gesendet")
                    except Exception as exc:
                        self._status_lbl.configure(text=f"Netlify/Telegram Fehler: {exc}")
                threading.Thread(target=_deploy, daemon=True).start()
        except Exception as exc:
            messagebox.showerror("IG Export fehlgeschlagen", str(exc))

    def _open_html(self):
        if self._html_path and self._html_path.exists():
            webbrowser.open(self._html_path.as_uri())

    def _advance_phase(self, phase: int):
        if not self._animating:
            return
        _PHASES = [
            (0.25, "1/4 Anfrage wird vorbereitet"),
            (0.50, "2/4 Inhalte werden generiert"),
            (0.75, "3/4 Antwort wird geprüft"),
            (0.95, "4/4 Tabelle wird gebaut · 0s"),
        ]
        self._current_phase = phase
        self._progress_bar.set(_PHASES[phase - 1][0])
        self._status_lbl.configure(text=_PHASES[phase - 1][1])
        if phase == 2:
            self.after(6000, lambda: self._advance_phase(3))
        elif phase == 3:
            self.after(5000, lambda: self._advance_phase(4))
        elif phase == 4:
            self._elapsed_secs = 0
            self._tick_phase4()

    def _tick_phase4(self):
        if not self._animating or self._current_phase != 4:
            return
        self._elapsed_secs += 1
        s = self._elapsed_secs
        time_str = f"{s // 60}m {s % 60:02d}s" if s >= 60 else f"{s}s"
        self._status_lbl.configure(text=f"4/4 Tabelle wird gebaut · {time_str}")
        self.after(1000, self._tick_phase4)

    # ── Table rendering ───────────────────────────────────────────────────────

    def _render_table(self, df: pd.DataFrame):
        for w in self._table_inner.winfo_children():
            w.destroy()

        cols = [c for c in _PREVIEW_COLS if c in df.columns]

        for ci, col in enumerate(cols):
            w = _COL_WIDTHS.get(col, 120)
            ctk.CTkLabel(
                self._table_inner, text=col, font=ctk.CTkFont(weight="bold"),
                width=w, anchor="w", fg_color=("gray75", "gray28"), corner_radius=4,
            ).grid(row=0, column=ci, padx=2, pady=2, sticky="w")

        for ri, (_, row) in enumerate(df.iterrows(), start=1):
            for ci, col in enumerate(cols):
                raw = str(row[col])
                text = raw[:_TRUNCATE] + ("…" if len(raw) > _TRUNCATE else "")
                w = _COL_WIDTHS.get(col, 120)
                ctk.CTkLabel(
                    self._table_inner, text=text, width=w, anchor="w", wraplength=w - 10,
                ).grid(row=ri, column=ci, padx=2, pady=1, sticky="w")

        self._bind_scroll_recursive(self._table_inner)

    # ── Export ────────────────────────────────────────────────────────────────

    def _save_xlsx(self):
        if self._df is None:
            messagebox.showwarning("Fehler", "Keine Tabelle vorhanden.")
            return
        kwargs = {"defaultextension": ".xlsx", "filetypes": [("Excel", "*.xlsx")], "initialfile": self._file_stem}
        if self._project_dir:
            kwargs["initialdir"] = str(self._project_dir)
        path = filedialog.asksaveasfilename(**kwargs)
        if path:
            try:
                table.save_xlsx(self._df, path)
                self._status_lbl.configure(text=f"Gespeichert: {path.split('/')[-1]}")
            except Exception as exc:
                messagebox.showerror("Speichern fehlgeschlagen", str(exc))

    def _save_csv(self):
        if self._df is None:
            messagebox.showwarning("Fehler", "Keine Tabelle vorhanden.")
            return
        kwargs = {"defaultextension": ".csv", "filetypes": [("CSV", "*.csv")], "initialfile": self._file_stem}
        if self._project_dir:
            kwargs["initialdir"] = str(self._project_dir)
        path = filedialog.asksaveasfilename(**kwargs)
        if path:
            try:
                table.save_csv(self._df, path)
                self._status_lbl.configure(text=f"Gespeichert: {path.split('/')[-1]}")
            except Exception as exc:
                messagebox.showerror("Speichern fehlgeschlagen", str(exc))

    def _save_html(self):
        if self._df is None:
            messagebox.showwarning("Fehler", "Keine Tabelle vorhanden.")
            return
        kwargs = {
            "defaultextension": ".html",
            "filetypes": [("HTML", "*.html")],
            "initialfile": self._file_stem,
        }
        if self._project_dir:
            kwargs["initialdir"] = str(self._project_dir)
        path = filedialog.asksaveasfilename(**kwargs)
        if path:
            try:
                table.save_html(self._df, path, topic=self._topic_var.get().strip(),
                                music_config=self._music_config())
                prompts_path = Path(path).parent / ".prompts.json"
                table.save_prompts_json(self._df, prompts_path)
                self._status_lbl.configure(text=f"Gespeichert: {Path(path).name}")
            except Exception as exc:
                messagebox.showerror("Speichern fehlgeschlagen", str(exc))

    def _go_to_machine(self):
        if self._df is None:
            messagebox.showwarning("Fehler", "Bitte zuerst eine Tabelle generieren.")
            return
        self._on_go_to_machine(self._df, self._topic_var.get().strip(), self._project_dir)

    # ── Nur Hooks neu generieren ────────────────────────────────────────────

    def _start_regenerate_hooks(self):
        if self._df is None:
            messagebox.showwarning("Fehler", "Bitte zuerst eine Tabelle laden oder generieren.")
            return
        topic = self._topic_var.get().strip()
        if not topic:
            messagebox.showwarning("Fehler", "Bitte ein Thema eingeben.")
            return
        if not messagebox.askyesno(
            "Nur Hooks neu generieren",
            f"{len(self._df)} Hooks werden neu generiert (echter API-Call). "
            "Text, Titel, Prompts und Bilder bleiben unverändert.\n\nFortfahren?",
        ):
            return
        cfg = self._get_config()
        provider = cfg.get("provider", "openai")
        api_key = cfg.get("gemini_key", "") if provider == "gemini" else cfg.get("openai_key", "")
        fallback_provider = "openai" if provider == "gemini" else "gemini"
        fallback_key = cfg.get("openai_key", "") if provider == "gemini" else cfg.get("gemini_key", "")
        self._hooks_btn.configure(state="disabled")
        self._status_lbl.configure(text="Hooks werden neu generiert...")
        threading.Thread(
            target=self._regenerate_hooks_thread,
            args=(self._df.copy(), topic, api_key, provider, fallback_key, fallback_provider),
            daemon=True,
        ).start()

    def _regenerate_hooks_thread(self, df: pd.DataFrame, topic: str, api_key: str, provider: str, fallback_key: str, fallback_provider: str):
        try:
            new_df = brain.regenerate_hooks_only(
                df, topic, api_key, provider=provider,
                fallback_key=fallback_key, fallback_provider=fallback_provider,
            )
            self.after(0, self._on_hooks_success, new_df)
        except Exception as exc:
            import traceback
            print("\n─── FEHLER IN _regenerate_hooks_thread ───")
            print(traceback.format_exc())
            print("──────────────────────────\n")
            self.after(0, self._on_hooks_error, str(exc))

    def _on_hooks_success(self, df: pd.DataFrame):
        self._df = df
        self._render_table(df)
        self._hooks_btn.configure(state="normal")
        self._status_lbl.configure(text=f"{len(df)} Hooks neu generiert ✓")
        if self._html_path:
            try:
                table.save_html(df, self._html_path, topic=self._topic_var.get().strip(),
                                music_config=self._music_config())
                errors = table.validate_html(self._html_path)
                if errors:
                    print(f"[HTML VALIDATION FEHLER] {errors}")
            except Exception as exc:
                print(f"[HOOK-ONLY HTML SAVE FEHLER] {exc}")
        elif self._project_dir:
            self._auto_save_html(df, self._topic_var.get().strip())

    def _on_hooks_error(self, msg: str):
        self._hooks_btn.configure(state="normal")
        self._status_lbl.configure(text="Fehler")
        messagebox.showerror("Fehler", msg)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_status(self, text: str, busy: bool):
        self._status_lbl.configure(text=text)
        self._gen_btn.configure(state="disabled" if busy else "normal")
        if busy:
            self._animating = True
            self._elapsed_secs = 0
            self._current_phase = 1
            self._progress_bar.set(0.25)
            self._status_lbl.configure(text="1/4 Anfrage wird vorbereitet")
            self.after(1500, lambda: self._advance_phase(2))

    # ── Load existing project ─────────────────────────────────────────────────

    def _load_project(self):
        path = filedialog.askopenfilename(
            title="Bestehende Tabelle laden",
            filetypes=[
                ("ShortFlow Tabelle", "*.xlsx *.html"),
                ("Excel", "*.xlsx"),
                ("HTML", "*.html"),
            ],
        )
        if not path:
            return
        path = Path(path)
        project_dir = path.parent
        try:
            if path.suffix == ".xlsx":
                df = table.load_xlsx(path)
            elif path.suffix == ".html":
                prompts_path = project_dir / ".prompts.json"
                if not prompts_path.exists():
                    prompts_path = project_dir / "prompts.json"  # Fallback: alte Projekte
                if not prompts_path.exists():
                    messagebox.showerror(
                        "Prompts fehlen",
                        f"Keine .prompts.json gefunden in:\n{project_dir}\n\n"
                        "Bitte die Tabelle in ShortFlow neu als .html exportieren —\n"
                        "dabei wird .prompts.json automatisch mitgespeichert.",
                    )
                    return
                df = table.load_html(path)
                prompts = table.load_prompts_json(prompts_path)
                for idx in df.index:
                    short_id = str(df.at[idx, "Short"])
                    df.at[idx, "Prompts"] = prompts.get(short_id, "")
                self._html_path = path
                self._open_btn.configure(state="normal")
            else:
                raise ValueError(f"Nicht unterstütztes Format: {path.suffix}")
        except Exception as exc:
            messagebox.showerror("Fehler beim Laden", str(exc))
            return
        folder_name = project_dir.name
        _is_month = re.match(r'^\d{4}-\d{2}$', folder_name) or re.match(r"^\d{2}\.[A-Za-zäöüÄÖÜß]+'?\d{2}$", folder_name)
        if _is_month:
            topic = project_dir.parent.name
        else:
            topic = re.sub(r"-\d{2}-\d{2}-\d{2}$", "", folder_name).replace("-", " ").strip()

        df = self._reconstruct_status(df, project_dir)

        self._df = df
        self._project_dir = project_dir
        self._topic_var.set(topic)
        self._hooks_btn.configure(state="normal")
        stem = re.sub(r"[^\w\s-]", "", topic)
        stem = re.sub(r"\s+", "-", stem)
        self._file_stem = f"{stem}-Short-Tabelle" if stem else "Short-Tabelle"

        self._render_table(df)
        fertig = int((df["Status"] == "Fertig").sum())
        self._progress_bar.set(fertig / len(df) if len(df) else 0)
        self._status_lbl.configure(
            text=f"{len(df)} Shorts geladen — {fertig} Fertig  →  {topic}"
        )

    def _reconstruct_status(self, df: pd.DataFrame, project_dir: Path) -> pd.DataFrame:
        df = df.copy()
        for idx in df.index:
            short_id = str(df.at[idx, "Short"])
            short_dir = project_dir / short_id
            if short_dir.exists():
                pngs = list(short_dir.glob("*.png"))
                if len(pngs) >= 10:
                    df.at[idx, "Status"] = "Fertig"
                    print(f"[LOAD] {short_id}: {len(pngs)} Bilder → Fertig")
                else:
                    df.at[idx, "Status"] = "Ausstehend"
                    print(f"[LOAD] {short_id}: {len(pngs)} Bilder → Ausstehend")
            else:
                print(f"[LOAD] {short_id}: kein Ordner → {df.at[idx, 'Status']}")
        return df

    def get_dataframe(self) -> pd.DataFrame | None:
        return self._df


def ttk_scrollbar(parent, orient: str, command):
    import tkinter.ttk as ttk
    sb = ttk.Scrollbar(parent, orient=orient, command=command)
    return sb
