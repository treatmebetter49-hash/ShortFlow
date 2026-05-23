"""
Einmaliger echter Runtime-Test.
1 Short, 5 Bilder, echter FAL-API-Modus.
Gibt alle Debug-Logs auf stdout aus.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import modules.machine as machine
import modules.config_manager as cfg

assert not machine.USE_MOCK_IMAGE_API, "USE_MOCK_IMAGE_API muss False sein für diesen Test"

config = cfg.load()
fal_key = config.get("fal_key", "").strip()
output_dir = config.get("output_dir", "").strip()

assert fal_key,    "FAL-Key fehlt in config.json"
assert output_dir, "output_dir fehlt in config.json"

PROMPTS = [
    "Cinematic vertical shot of a dense misty forest at dawn, soft golden light filtering through trees, 720x1280, photorealistic",
    "Vertical close-up of rain drops on a glass window, city bokeh background at night, moody atmosphere, photorealistic",
    "Wide vertical shot of a lone lighthouse on rocky cliffs, stormy ocean waves, dramatic clouds, photorealistic",
    "Vertical aerial view of an autumn forest road winding through orange and red foliage, golden hour, photorealistic",
    "Cinematic vertical shot of a campfire in a dark pine forest, sparks rising, warm glowing light, photorealistic",
]

df = pd.DataFrame([{
    "Short":       "Short01",
    "Hook":        "Test-Hook",
    "Text":        "Test-Text",
    "Titel":       "RuntimeTest",
    "Beschreibung": "Echter Runtime-Test",
    "Prompts":     " || ".join(PROMPTS),
    "Status":      "Ausstehend",
}])

print("=" * 60)
print("ECHTER RUNTIME-TEST — 1 Short, 5 Bilder")
print(f"Output: {output_dir}")
print("=" * 60)

logs = []
def cb(msg: str) -> None:
    logs.append(msg)
    print(msg)

machine.generate_images(df, output_dir, fal_key, cb, topic="RuntimeTest")

print("\n" + "=" * 60)
print("ZUSAMMENFASSUNG")
print("=" * 60)
client_ids = [l for l in logs if "[DBG] client_id=" in l]
skips      = [l for l in logs if "[SKIP]" in l]
gens       = [l for l in logs if "[GEN]"  in l]
oks        = [l for l in logs if "[OK]"   in l]
errs       = [l for l in logs if "[ERR]"  in l]
billings   = [l for l in logs if "[BILLING]" in l]

print(f"client_id-Zeilen : {len(client_ids)}")
print(f"SKIP             : {len(skips)}")
print(f"GEN              : {len(gens)}")
print(f"OK               : {len(oks)}")
print(f"ERR              : {len(errs)}")
print(f"BILLING          : {len(billings)}")
if client_ids:
    print(f"Erster client_id : {client_ids[0].strip()}")
