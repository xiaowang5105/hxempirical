from pathlib import Path
p=Path('scripts/apply_ui_v140.py')
s=p.read_text(encoding='utf-8')
old='new HxWorkbench.WorkbenchFrame.SimpleDocumentListener(this::refreshInspectorVariables)'
new='new HxWorkbench.SimpleDocumentListener(this::refreshInspectorVariables)'
assert old in s
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('FIX_UI_V140_COMPILE_OK')
