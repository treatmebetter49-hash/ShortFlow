import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Callable

import customtkinter as ctk
import pandas as pd

from modules import machine, table


class MachineTab(ctk.CTkFrame):
    def __init__(self, master, get_config: Callable):
        super().__init__(master, fg_color="transparent")
        self._get_config = get_config
        self._df: pd.DataFrame | None = None
        self._topic: str = ""
        self._project_dir = None
        self._is_resume: bool = False
        self._build()

    def _build(self):
        # ── Source row ────────────────────────────────────────────────────────
        src = ctk.CTkFrame(self, fg_color="transparent")
        src.pack(fill="x", padx=20, pady=(20, 0))
        ctk.CTkButton(src, text="CSV laden", width=100, command=self._load_csv).pack(side="left")
        self._src_lbl = ctk.CTkLabel(src, text="Keine Tabelle geladen")
        self._src_lbl.pack(side="left", padx=(12, 0))

        # ── Output path ───────────────────────────────────────────────────────
        path_row = ctk.CTkFrame(self, fg_color="transparent")
        path_row.pack(fill="x", padx=20, pady=(10, 0))
        path_row.columnconfigure(1, weight=1)
        ctk.CTkLabel(path_row, text="Output:").grid(row=0, column=0, sticky="w")
        self._dir_var = tk.StringVar(value=self._get_config().get("output_dir", ""))
        ctk.CTkEntry(path_row, textvariable=self._dir_var).grid(row=0, column=1, sticky="ew", padx=(8, 8))
        ctk.CTkButton(path_row, text="Ändern", width=90, command=self._browse).grid(row=0, column=2)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(padx=20, pady=14)

        self._gen_btn = ctk.CTkButton(
            btn_row, text="MEDIEN-PAKET SCHNÜREN",
            height=44, font=ctk.CTkFont(size=15, weight="bold"),
            command=self._start,
        )
        self._gen_btn.pack(side="left", padx=(0, 10))

        self._resume_btn = ctk.CTkButton(
            btn_row, text="FORTSETZEN",
            height=44, font=ctk.CTkFont(size=15, weight="bold"),
            state="disabled",
            command=self._resume,
        )
        self._resume_btn.pack(side="left")

        # ── Log ───────────────────────────────────────────────────────────────
        self._log = ctk.CTkTextbox(self, state="disabled", font=ctk.CTkFont(family="Menlo", size=12))
        self._log.pack(fill="both", expand=True, padx=20, pady=(0, 8))
        for w in (self._log, self._log._textbox):
            w.bind("<MouseWheel>", lambda e: self._log._textbox.yview_scroll(int(-e.delta), "units"))

        # ── Progress bar ──────────────────────────────────────────────────────
        self._progress = ctk.CTkProgressBar(self)
        self._progress.set(0)
        self._progress.pack(fill="x", padx=20, pady=(0, 16))

    # ── Public: called by app when "Weiter zu Machine" is clicked ─────────────

    def load_from_brain(self, df: pd.DataFrame, topic: str = "", project_dir=None):
        self._df = df
        self._topic = topic
        self._project_dir = project_dir
        self._src_lbl.configure(text=f"Brain-Tabelle ({len(df)} Shorts)")
        dir_info = f"  →  {project_dir.name}" if project_dir else ""
        self._log_write(f"Tabelle aus Brain geladen: {len(df)} Shorts{dir_info}\n")

    # ── CSV load ──────────────────────────────────────────────────────────────

    def _load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("Alle", "*.*")])
        if not path:
            return
        try:
            self._df = table.load_csv(path)
            self._src_lbl.configure(text=f"Geladen: {Path(path).name} ({len(self._df)} Shorts)")
            self._log_write(f"CSV geladen: {Path(path).name}\n")
        except Exception as exc:
            messagebox.showerror("Fehler", str(exc))

    def _browse(self):
        path = filedialog.askdirectory(title="Output-Ordner wählen")
        if path:
            self._dir_var.set(path)

    # ── Generation ────────────────────────────────────────────────────────────

    def _start(self):
        if self._df is None:
            messagebox.showwarning("Fehler", "Keine Tabelle geladen.")
            return
        output_dir = self._dir_var.get().strip()
        if not output_dir:
            messagebox.showwarning("Fehler", "Bitte einen Output-Ordner angeben.")
            return
        cfg = self._get_config()
        if not cfg.get("fal_key"):
            messagebox.showwarning("Fehler", "FAL API Key fehlt. Bitte in den Einstellungen eintragen.")
            return

        is_resume = self._is_resume
        self._is_resume = False
        if not is_resume:
            machine.reset_mock()

        self._gen_btn.configure(state="disabled")
        self._resume_btn.configure(state="disabled")
        self._progress.set(0)
        self._log_write("\n--- Starte Generierung ---\n")

        total = len(self._df)
        counter = [0]

        def cb(msg: str):
            self.after(0, self._log_write, msg + "\n")
            if "✓ Fertig" in msg:
                counter[0] += 1
                self.after(0, self._progress.set, counter[0] / total if total else 1)

        threading.Thread(
            target=self._run,
            args=(self._df.copy(), output_dir, cfg["fal_key"], cb, self._topic, self._project_dir),
            daemon=True,
        ).start()

    def _resume(self):
        self._is_resume = True
        self._resume_btn.configure(state="disabled")
        self._log_write("\n--- Fortsetze Generierung ---\n")
        self._start()

    def _run(self, df: pd.DataFrame, output_dir: str, fal_key: str, cb: Callable, topic: str = "", project_dir=None):
        try:
            updated = machine.generate_images(df, output_dir, fal_key, cb, topic, project_dir=project_dir)
            self._df = updated
        except machine.BillingError as exc:
            self.after(0, self._on_billing_error, str(exc))
        except Exception as exc:
            self.after(0, messagebox.showerror, "Fehler", str(exc))
        finally:
            self.after(0, self._gen_btn.configure, {"state": "normal"})

    def _on_billing_error(self, msg: str):
        self._log_write(f"\n⛔ {msg}\n")
        self._resume_btn.configure(state="normal")
        messagebox.showerror("Guthaben leer", msg)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _log_write(self, text: str):
        self._log.configure(state="normal")
        self._log.insert("end", text)
        self._log.see("end")
        self._log.configure(state="disabled")
