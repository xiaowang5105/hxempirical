from pathlib import Path
p=Path('.github/scripts/apply_v152_hardening.py')
s=p.read_text(encoding='utf-8')
old='''if text.count(old_menu) != 2:\n    raise SystemExit(f'expected 2 menu blocks, got {text.count(old_menu)}')\ntext = text.replace(old_menu, new_menu, 2)\n'''
new='''if text.count(old_menu) != 1:\n    raise SystemExit(f'expected 1 indented menu block, got {text.count(old_menu)}')\ntext = text.replace(old_menu, new_menu, 1)\nold_menu2 = ''' + '"""' + '''capture noisily hxsetup, persist\nlocal menu_rc = _rc\n''' + '"""' + '''\nnew_menu2 = ''' + '"""' + '''local menu_rc 0\nif `"`target_kind'"' == "PERSONAL" {\n    capture noisily hxsetup, persist\n    local menu_rc = _rc\n}\nelse capture quietly hxmenu\n''' + '"""' + '''\nif text.count(old_menu2) != 1:\n    raise SystemExit(f'expected 1 final menu block, got {text.count(old_menu2)}')\ntext = text.replace(old_menu2, new_menu2, 1)\n'''
if old not in s:
    raise SystemExit('menu replacement code not found')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('FIX_PATCH_SCRIPT_OK')
