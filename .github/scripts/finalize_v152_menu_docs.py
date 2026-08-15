from pathlib import Path

# Make PLUS/h a real core-install fallback without turning menu persistence into a failure.
p = Path('hxinstaller.ado')
s = p.read_text(encoding='utf-8')
old_menu = '''    local menu_rc 0
    if `"`target_kind'"' == "PERSONAL" {
        capture noisily hxsetup, persist
        local menu_rc = _rc
    }
    else capture quietly hxmenu
'''
new_menu = '''    local menu_rc 0
    if `"`target_kind'"' == "PERSONAL" {
        capture noisily hxsetup, persist
        local menu_rc = _rc
    }
    else {
        capture quietly hxsetup, persist
        local menu_rc = _rc
        if `menu_rc' capture quietly hxmenu
    }
'''
if s.count(old_menu) != 1:
    raise SystemExit(f'fast menu block count={s.count(old_menu)}')
s = s.replace(old_menu, new_menu, 1)
old_fast = '''    if `"`target_kind'"' == "PLUS" noisily display as text "当前安装位置：PLUS/h（PERSONAL 不可写）。"
    else if `menu_rc' noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"
'''
new_fast = '''    if `"`target_kind'"' == "PLUS" {
        noisily display as text "当前安装位置：" as result "PLUS/h"
        if `menu_rc' noisily display as text "菜单持久化不可用；重启 Stata 后直接运行：" as result "hxempirical"
        else noisily display as text "顶部入口：" as result "用户(U) > 我的实证工具箱"
    }
    else if `menu_rc' noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"
'''
if old_fast not in s:
    raise SystemExit('fast message block missing')
s = s.replace(old_fast, new_fast, 1)
old_menu2 = '''local menu_rc 0
if `"`target_kind'"' == "PERSONAL" {
    capture noisily hxsetup, persist
    local menu_rc = _rc
}
else capture quietly hxmenu
'''
new_menu2 = '''local menu_rc 0
if `"`target_kind'"' == "PERSONAL" {
    capture noisily hxsetup, persist
    local menu_rc = _rc
}
else {
    capture quietly hxsetup, persist
    local menu_rc = _rc
    if `menu_rc' capture quietly hxmenu
}
'''
if s.count(old_menu2) != 1:
    raise SystemExit(f'final menu block count={s.count(old_menu2)}')
s = s.replace(old_menu2, new_menu2, 1)
old_tail = '''if `"`target_kind'"' == "PLUS" {
    noisily display as text "安装目录回退：" as result "PERSONAL 不可写，已安装到 PLUS/h。"
    noisily display as text "本次会话可直接运行 hxempirical；持久菜单未写入 PERSONAL/profile.do。"
}
else if `menu_rc' {
'''
new_tail = '''if `"`target_kind'"' == "PLUS" {
    noisily display as text "安装位置：" as result "PLUS/h"
    if `menu_rc' noisily display as text "PERSONAL 菜单持久化不可用；重启 Stata 后直接运行：" as result "hxempirical"
    else noisily display as text "顶部入口：" as result "用户(U) > 我的实证工具箱"
}
else if `menu_rc' {
'''
if old_tail not in s:
    raise SystemExit('final message block missing')
s = s.replace(old_tail, new_tail, 1)
p.write_text(s, encoding='utf-8')

# README: describe fallback/menu behavior exactly.
p = Path('README.md')
s = p.read_text(encoding='utf-8')
s = s.replace('- 第一次运行：安装到当前用户的 `PERSONAL`；', '- 第一次运行：优先安装到当前用户的 `PERSONAL`；该目录不可写时自动尝试 `PLUS/h`；', 1)
s = s.replace('- 安装、更新和修复完成后都会建立唯一的 **用户（User） > 我的实证工具箱** 菜单入口。', '- 安装、更新和修复完成后都会尝试建立唯一的 **用户（User） > 我的实证工具箱** 菜单入口；若 `PERSONAL/profile.do` 不可写，核心安装仍然成功，重启后直接运行 `hxempirical`。', 1)
s = s.replace('每段网络等待上限为 20 秒，全部校验通过后才写入 `PERSONAL`。', '每段网络等待上限为 20 秒，全部校验通过后才写入最终选定的持久 ado 目录。', 1)
s = s.replace('4. 从 **用户（User） > 我的实证工具箱** 打开；遇到问题时运行下面三条命令并保存输出：', '4. 优先从 **用户（User） > 我的实证工具箱** 打开；如果安装器提示菜单未持久化，则在 Stata 中直接运行 `hxempirical`。遇到问题时运行下面三条命令并保存输出：', 1)
p.write_text(s, encoding='utf-8')

# INSTALL: update version example and distinguish core install from optional menu persistence.
p = Path('INSTALL.md')
s = p.read_text(encoding='utf-8')
s = s.replace('1. 取得短安装核心并检查 Stata 版本和 `PERSONAL` 写权限；', '1. 取得短安装核心，检查 Stata 版本，并选择可写的持久 ado 目录（优先 `PERSONAL`，必要时 `PLUS/h`）；', 1)
s = s.replace('8. 建立唯一的 **用户（User） > 我的实证工具箱** 菜单入口。', '8. 尝试建立唯一的 **用户（User） > 我的实证工具箱** 菜单入口；菜单持久化失败不会撤销已经成功的核心安装。', 1)
s = s.replace('当前版本：1.5.1\n最新版本：1.5.1', '当前版本：1.5.2\n最新版本：1.5.2', 1)
s = s.replace('使用 `PLUS/h` 回退时不会强行写入 `PERSONAL/profile.do`，因此菜单持久化会跳过，但 `hxempirical` 命令本身可正常使用。', '使用 `PLUS/h` 时，安装器会静默尝试菜单持久化；若 `PERSONAL/profile.do` 仍不可写，只跳过持久菜单，不影响 `hxempirical` 命令本身。', 1)
p.write_text(s, encoding='utf-8')

# Help text: remove two stale descriptions from the pre-compact UI.
p = Path('hxempirical.sthlp')
s = p.read_text(encoding='utf-8')
s = s.replace('opens one desktop-style workbench with a fixed left sidebar,', 'opens one desktop-style workbench with a collapsible left sidebar,', 1)
s = s.replace('it shows only the command name, Chinese title, one-line purpose, and source tag.\nDetailed examples and limitations are kept in the command page.', 'it shows command name, Chinese explanation, suitable scenario, example syntax, and an open action.\nA right-side command overview provides purpose, features, source, and help before entering the command page.', 1)
p.write_text(s, encoding='utf-8')

print('FINALIZE_V152_MENU_DOCS_OK')
