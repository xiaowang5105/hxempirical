from pathlib import Path

p = Path("tools/tmp_patch_summary_power.py")
text = p.read_text(encoding="utf-8")

old_marker = "family_marker = '    /* Family-level copy for catalog commands that rely on the generic syntax parser.\\n'"
new_marker = "family_marker = '    /* Family-level copy for catalog commands that rely on the generic syntax parser.\\n       Keep the parsed Stata syntax/flags unchanged; only improve beginner-facing semantics. */\\n'"
if old_marker not in text:
    raise SystemExit("family insertion marker not found")
text = text.replace(old_marker, new_marker, 1)

old_block = '''r = once(
    r,
    "summarize tabstat tabulate table ttest prtest sdtest",
    "summarize ameans centile ci mean proportion ratio total tabstat tabulate table dtable ttest prtest sdtest",
    "summary command catalog",
)
'''
new_block = '''summary_old = "summarize tabstat tabulate table ttest prtest sdtest"
summary_new = "summarize ameans centile ci mean proportion ratio total tabstat tabulate table dtable ttest prtest sdtest"
if summary_old not in r:
    raise SystemExit("summary command catalog anchor missing")
r = r.replace(summary_old, summary_new, 1)
'''
if old_block not in text:
    raise SystemExit("summary command catalog patch block not found")
text = text.replace(old_block, new_block, 1)

p.write_text(text, encoding="utf-8", newline="\n")
print("HX_SUMMARY_POWER_PREPARE_OK")
