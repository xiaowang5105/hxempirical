from pathlib import Path

p = Path("tools/tmp_patch_graph_fallback_parity.py")
s = p.read_text(encoding="utf-8")
old = "    ('return Collections.singletonList(\"twoway\");', 'return Collections.singletonList(\"graph_bar\");', 'bar fallback'),"
new = "    ('}          else if (\"条形图\".equals(var0)) {\\n            return Collections.singletonList(\"twoway\");', '}          else if (\"条形图\".equals(var0)) {\\n            return Collections.singletonList(\"graph_bar\");', 'bar fallback'),"
if s.count(old) != 1:
    raise SystemExit(f"bar helper tuple expected once, got {s.count(old)}")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8", newline="\n")
print("HX_GRAPH_FALLBACK_HELPER_PREPARED")
