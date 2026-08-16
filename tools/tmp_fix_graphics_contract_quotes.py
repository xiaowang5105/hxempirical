from pathlib import Path
import json

p = Path("tools/verify_static_contracts.py")
lines = p.read_text(encoding="utf-8").splitlines()
out = []
changed = 0
for line in lines:
    stripped = line.strip()
    if ("local preview" in line or "probe_cmd" in line) and stripped.startswith("'") and stripped.endswith("',"):
        inner = stripped[1:-2]
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + json.dumps(inner, ensure_ascii=False) + ","
        changed += 1
    out.append(line)
if changed != 8:
    raise SystemExit(f"expected 8 Graphics quote repairs, got {changed}")
p.write_text("\n".join(out) + "\n", encoding="utf-8")
print("HX_GRAPHICS_CONTRACT_QUOTES_OK")
