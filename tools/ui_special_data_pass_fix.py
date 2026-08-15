from pathlib import Path

path = Path(__file__).resolve().parent / "ui_special_data_pass.py"
text = path.read_text(encoding="utf-8")
start = text.index("# Missing-value analysis: three clear tasks instead of six equal-weight rows.")
call_start = text.index("replace_once(", start)
next_call = text.index("\n\nreplace_once(", call_start)
replacement = '''replace_once(
    "右侧只读数据表",
    "右侧当前数据表",
    "missing analysis current-data wording",
)'''
text = text[:call_start] + replacement + text[next_call:]
path.write_text(text, encoding="utf-8")
print("HX_UI_SPECIAL_DATA_SCRIPT_FIXED")
