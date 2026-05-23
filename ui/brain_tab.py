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

from modules import brain, table

_PREVIEW_COLS = ["Short", "Datum", "Tag", "Hook", "Text", "Titel", "Status"]
_COL_WIDTHS = {"Short": 80, "Datum": 70, "Tag": 50, "Hook": 160, "Text": 160, "Titel": 140, "YTBeschreibung": 160, "IGBeschreibung": 160, "Prompts": 200, "Status": 90}
_TRUNCATE = 60
_MONTHS_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni",
              "Juli", "August", "September", "Oktober", "November", "Dezember"]


class BrainTab(ctk.CTkFrame):
    def __init__(self, master, get_config: Callable, on_go_to_machine: Callable):
        super().__init__(master, fg_color="transparent")
        self._get_config = get_config
        self._on_go_to_machine = on_go_to_machine
        self._df: pd.DataFrame | None = None
        self._project_dir = None
        self._html_path: Path | None = None
        self._file_stem = "Short-Tabelle"
        self._animating = False
        self._progress_val = 0.0
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
        ctk.CTkEntry(top, textvariable=self._topic_var, width=300).pack(side="left", padx=(8, 20))

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

        self._gen_btn = ctk.CTkButton(top, text="TABELLE GENERIEREN", command=self._start_generate)
        self._gen_btn.pack(side="left")
        self._status_lbl = ctk.CTkLabel(top, text="Bereit")
        self._status_lbl.pack(side="left", padx=(16, 0))

        # ── Progress bar ──────────────────────────────────────────────────────
        self._progress_bar = ctk.CTkProgressBar(self)
        self._progress_bar.set(0)
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
        self._open_btn = ctk.CTkButton(bot, text="Tabelle öffnen", command=self._open_html, state="disabled")
        self._open_btn.pack(side="left", padx=(0, 20))
        ctk.CTkButton(
            bot, text="→  WEITER ZU MACHINE",
            font=ctk.CTkFont(weight="bold"),
            command=self._go_to_machine,
        ).pack(side="left")
        ctk.CTkButton(
            bot, text="Vorhandene Tabelle laden",
            command=self._load_project,
        ).pack(side="right")

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
        self._set_status("Tabelle wird erstellt... 0%", busy=True)
        threading.Thread(target=self._generate, args=(topic, count, cfg["openai_key"], start_date), daemon=True).start()

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

    def _generate(self, topic: str, count: int, key: str, start_date=None):
        try:
            df = brain.generate_table(topic, count, key, start_date=start_date)
            self.after(0, self._on_success, df)
        except Exception as exc:
            import traceback
            print("\n─── FEHLER IN _generate ───")
            print(traceback.format_exc())
            print("──────────────────────────\n")
            self.after(0, self._on_error, str(exc))

    def _on_success(self, df: pd.DataFrame):
        self._animating = False
        self._progress_bar.set(1.0)
        self._df = df
        self._render_table(df)
        self._gen_btn.configure(state="normal")

        topic = self._topic_var.get().strip()
        cfg = self._get_config()
        output_dir = cfg.get("output_dir", "").strip()
        if not output_dir:
            output_dir = filedialog.askdirectory(title="Output-Ordner wählen")
        if output_dir:
            import re
            self._project_dir = brain.make_project_dir(topic, output_dir)
            clean = re.sub(r"[^\w\s-]", "", topic)
            clean = re.sub(r"\s+", "-", clean)
            clean = re.sub(r"-{2,}", "-", clean)
            clean = clean[:40]
            self._file_stem = f"{clean}-Short-Tabelle" if clean else "Short-Tabelle"
            self._auto_save_html(df, topic)
            self._status_lbl.configure(text=f"{len(df)} Shorts ✓  →  {self._project_dir.name}")
        else:
            self._status_lbl.configure(text=f"{len(df)} Shorts geladen ✓")

    def _on_error(self, msg: str):
        self._animating = False
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
            html_path = self._project_dir / f"{self._file_stem}.html"
            table.save_html(df, html_path, topic=topic, music_config=self._music_config())
            table.save_prompts_json(df, self._project_dir / ".prompts.json")
            self._html_path = html_path
            self._open_btn.configure(state="normal")
        except Exception as exc:
            print(f"[HTML AUTO-SAVE FEHLER] {exc}")

    def _open_html(self):
        if self._html_path and self._html_path.exists():
            webbrowser.open(self._html_path.as_uri())

    def _tick_progress(self):
        if not self._animating:
            return
        self._progress_val += (0.9 - self._progress_val) * 0.08
        self._progress_bar.set(self._progress_val)
        pct = int(self._progress_val * 100)
        self._status_lbl.configure(text=f"Tabelle wird erstellt... {pct}%")
        self.after(500, self._tick_progress)

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

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_status(self, text: str, busy: bool):
        self._status_lbl.configure(text=text)
        self._gen_btn.configure(state="disabled" if busy else "normal")
        if busy:
            self._animating = True
            self._progress_val = 0.0
            self._progress_bar.set(0)
            self._tick_progress()

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
        topic = re.sub(r"-\d{2}-\d{2}-\d{2}$", "", folder_name).replace("-", " ").strip()

        df = self._reconstruct_status(df, project_dir)

        self._df = df
        self._project_dir = project_dir
        self._topic_var.set(topic)
        stem = re.sub(r"[^\w\s-]", "", topic)
        stem = re.sub(r"\s+", "-", stem)
        self._file_stem = f"{stem}-Short-Tabelle" if stem else "Short-Tabelle"

        self._render_table(df)
        fertig = int((df["Status"] == "Fertig").sum())
        self._progress_bar.set(fertig / len(df) if len(df) else 0)
        self._status_lbl.configure(
            text=f"{len(df)} Shorts geladen — {fertig} Fertig  →  {project_dir.name}"
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
