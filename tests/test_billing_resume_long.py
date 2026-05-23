"""
Realistischer Mock-Test: Billing-Error nach Bild 17, dann Resume.

Aufbau:
  - 3 Shorts × 10 Bilder = 30 Bilder gesamt
  - Run 1: Bilder 1–17 OK, Bild 18 → BillingError → Stop
  - Run 2: Resume mit frischer Mock-Queue (alles OK)

Prüfungen:
  1. Run 1 wirft BillingError
  2. Nach Run 1: Short01=10, Short02=7, Short03=0 PNGs
  3. Run 2 wirft KEIN BillingError
  4. Nach Run 2: Short01=10, Short02=10, Short03=10 PNGs
  5. Run-2-Log: 17 SKIP, 13 GEN, 0 BILLING
"""

import sys
import os
import pathlib
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import modules.machine as machine


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _make_df() -> pd.DataFrame:
    rows = []
    for s in range(1, 4):
        prompts = " || ".join(f"Prompt S{s}-B{i:02d}" for i in range(1, 11))
        rows.append({
            "Short": f"Short{s:02d}",
            "Hook": f"Hook {s}",
            "Text": f"Text {s}",
            "Titel": f"Titel {s}",
            "Beschreibung": f"Beschreibung {s}",
            "Prompts": prompts,
            "Status": "Ausstehend",
        })
    return pd.DataFrame(rows)


def _setup_mock(outcomes: list[str]) -> None:
    machine._MOCK_OUTCOMES.clear()
    machine._MOCK_OUTCOMES.extend(outcomes)
    machine._mock_idx[0] = 0


def _count_pngs(folder: pathlib.Path) -> int:
    if not folder.exists():
        return 0
    return len(list(folder.glob("Bild*.png")))


def _collect_logs() -> tuple[list[str], callable]:
    logs: list[str] = []
    def cb(msg: str) -> None:
        logs.append(msg)
    return logs, cb


# ──────────────────────────────────────────────────────────────────────────────
# Test
# ──────────────────────────────────────────────────────────────────────────────

def test_billing_resume_long() -> None:
    original_mock_flag = machine.USE_MOCK_IMAGE_API
    try:
        machine.USE_MOCK_IMAGE_API = True

        with tempfile.TemporaryDirectory() as tmpdir:
            df = _make_df()

            # ── RUN 1: 17 OK, dann BillingError auf Bild 18 ──────────────────
            print("\n" + "=" * 60)
            print("RUN 1 — 17 OK, dann BillingError")
            print("=" * 60)

            _setup_mock(["ok"] * 17 + ["billing"])
            logs1, cb1 = _collect_logs()

            billing_raised = False
            try:
                machine.generate_images(df.copy(), tmpdir, fal_key="dummy", progress_cb=cb1, topic="ResumeTest")
            except machine.BillingError:
                billing_raised = True

            # Assertion 1
            assert billing_raised, "Run 1: BillingError hätte ausgelöst werden sollen"

            # Projekt-Ordner ermitteln
            project_dirs = [p for p in pathlib.Path(tmpdir).iterdir() if p.is_dir()]
            assert len(project_dirs) == 1, f"Erwartet 1 Projektordner, gefunden: {project_dirs}"
            project_dir = project_dirs[0]

            n01 = _count_pngs(project_dir / "Short01")
            n02 = _count_pngs(project_dir / "Short02")
            n03 = _count_pngs(project_dir / "Short03")

            print(f"\nNach Run 1: Short01={n01}, Short02={n02}, Short03={n03}")

            # Assertion 2
            assert n01 == 10, f"Short01 nach Run 1: erwartet 10, gefunden {n01}"
            assert n02 == 7,  f"Short02 nach Run 1: erwartet 7, gefunden {n02}"
            assert n03 == 0,  f"Short03 nach Run 1: erwartet 0, gefunden {n03}"
            print("✓ Dateistand nach Run 1 korrekt")

            # ── RUN 2: Resume, keine Billing-Fehler ──────────────────────────
            print("\n" + "=" * 60)
            print("RUN 2 — Resume (alle restlichen Bilder OK)")
            print("=" * 60)

            _setup_mock([])  # leere Liste → immer "ok"
            logs2, cb2 = _collect_logs()

            try:
                machine.generate_images(df.copy(), tmpdir, fal_key="dummy", progress_cb=cb2, topic="ResumeTest")
            except machine.BillingError as exc:
                raise AssertionError(f"Run 2: unerwarteter BillingError: {exc}") from exc

            n01_after = _count_pngs(project_dir / "Short01")
            n02_after = _count_pngs(project_dir / "Short02")
            n03_after = _count_pngs(project_dir / "Short03")

            print(f"\nNach Run 2: Short01={n01_after}, Short02={n02_after}, Short03={n03_after}")

            # Assertion 3 — alle Ordner voll
            assert n01_after == 10, f"Short01 nach Resume: erwartet 10, gefunden {n01_after}"
            assert n02_after == 10, f"Short02 nach Resume: erwartet 10, gefunden {n02_after}"
            assert n03_after == 10, f"Short03 nach Resume: erwartet 10, gefunden {n03_after}"
            print("✓ Dateistand nach Run 2 korrekt")

            # Assertion 4 — Log-Zeilen prüfen
            skip_lines    = [l for l in logs2 if "[SKIP]" in l]
            gen_lines     = [l for l in logs2 if "[GEN]"  in l]
            billing_lines = [l for l in logs2 if "[BILLING]" in l]

            print(f"\nLog-Analyse Run 2:")
            print(f"  SKIP:    {len(skip_lines):>2}  (erwartet 17)")
            print(f"  GEN:     {len(gen_lines):>2}  (erwartet 13)")
            print(f"  BILLING: {len(billing_lines):>2}  (erwartet  0)")

            assert len(skip_lines)    == 17, f"SKIP: erwartet 17, gefunden {len(skip_lines)}"
            assert len(gen_lines)     == 13, f"GEN: erwartet 13, gefunden {len(gen_lines)}"
            assert len(billing_lines) ==  0, f"BILLING: erwartet 0, gefunden {len(billing_lines)}: {billing_lines}"
            print("✓ Log-Zeilen korrekt")

            # Assertion 5 — Reihenfolge: Short02 zuerst Skips, dann GEN
            short02_log = [l for l in logs2 if "Bild" in l and any(
                f"[{'SKIP' if 'SKIP' in l else 'GEN'}]  Bild{i:02d}" in l
                for i in range(1, 11)
            )]
            # Bild01–07 müssen als SKIP vor Bild08–10 als GEN erscheinen
            short02_lines = [l for l in logs2 if
                "[SKIP]" in l and any(f"Bild{i:02d}" in l for i in range(1, 8))
                or "[GEN]" in l and any(f"Bild{i:02d}" in l for i in range(8, 11))
            ]
            skip_before_gen = all(
                logs2.index(s) < logs2.index(g)
                for s in logs2 if "[SKIP]" in s and "Bild07" in s
                for g in logs2 if "[GEN]"  in g and "Bild08" in g
            )
            assert skip_before_gen, "Short02: SKIP von Bild07 muss vor GEN von Bild08 liegen"
            print("✓ Reihenfolge SKIP→GEN in Short02 korrekt")

    finally:
        machine.USE_MOCK_IMAGE_API = original_mock_flag
        machine._MOCK_OUTCOMES.clear()
        machine._MOCK_OUTCOMES.extend(["ok", "ok"])
        machine._mock_idx[0] = 0

    print("\n" + "=" * 60)
    print("✅ Alle Assertions bestanden")
    print("=" * 60)


if __name__ == "__main__":
    test_billing_resume_long()
