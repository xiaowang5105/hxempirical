from pathlib import Path

STAMP = "2026-08-12 21:20（UTC+8）"

# README
p = Path('README.md')
s = p.read_text(encoding='utf-8')
s = s.replace('**当前发布版本：1.2.0**', '**当前发布版本：1.2.1**', 1)
s = s.replace('**上次修改时间：2026-08-12 20:11（UTC+8）**', f'**上次修改时间：{STAMP}**', 1)
record = f'''### {STAMP}\n\n**修改时间**：{STAMP}\n\n**修改内容**：\n\n- 不再按“相近风格”重做，而是以用户提供的三张 **1672×941** 参考界面为直接坐标基准，逐页重做工作台首页、回归 > 线性模型目录和 OneClick 控制变量组合筛选页。\n- 首页按参考图固定左侧导航、顶部“开始分析”、五个快速入口、当前数据、2×3 常用任务、最近任务和底部九个“更多功能”卡片的相对位置、尺寸与留白。\n- 线性模型目录按参考图固定搜索 / 筛选区、“怎么选？”推荐条、2×2 常用命令卡、四列更多线性模型和右侧三步推荐路径；`regress` / `areg` / `reghdfe` / `qreg` 保持真实命令入口。\n- OneClick 页按参考图固定三栏结构，重做场景标签、三步说明、Y / 核心 X、候选控制变量选择器、固定变量选择器、显著性水平按钮、`reg / reghdfe / logit / probit` 方法按钮、说明区、真实命令区、空数据插图和右侧推荐流程。\n- 默认窗口按参考图设置为 1672×941；离线预览使用 1672×901 客户区，补足 Windows 标题栏后与参考截图尺寸一致。\n- Java 11 编译、class major 55、JAR 重建，以及首页 / 线性模型 / OneClick 三张同尺寸离线渲染均通过后才进入发布。\n\n'''
marker = '## 修改记录\n\n'
if record not in s:
    if marker not in s:
        raise SystemExit('README 修改记录 marker missing')
    s = s.replace(marker, marker + record, 1)
s = s.replace('### 1.2.0（当前版本）', '### 1.2.0', 1)
version_record = f'''### 1.2.1（当前版本）\n\n**发布时间**：{STAMP}\n\n**修改内容**：\n\n- 按三张 1672×941 参考界面逐页重做首页、线性模型目录和 OneClick 页面，不再采用“同风格近似”方式。\n- 固定主要页面坐标、栏宽、卡片比例、按钮位置、标题层级、边框与留白，并用同尺寸离线截图逐页校对。\n- OneClick 控件和底部命令继续连接真实外部 `oneclick`；线性模型卡继续进入真实 Stata / 第三方命令。\n- Java 11 / class major 55 / JAR 与三张关键页面离线渲染验证通过。\n\n'''
vm = '## 版本记录\n\n'
if version_record not in s:
    if vm not in s:
        raise SystemExit('README 版本记录 marker missing')
    s = s.replace(vm, vm + version_record, 1)
p.write_text(s, encoding='utf-8')

# Public entry point
p = Path('hxempirical.ado')
s = p.read_text(encoding='utf-8')
s = s.replace('*! hxempirical 1.2.0  12aug2026', '*! hxempirical 1.2.1  12aug2026', 1)
s = s.replace('display as text "版本：" as result "1.2.0"', 'display as text "版本：" as result "1.2.1"', 1)
s = s.replace('return local version "1.2.0"', 'return local version "1.2.1"', 1)
p.write_text(s, encoding='utf-8')

# Package manifest
p = Path('hxempirical.pkg')
s = p.read_text(encoding='utf-8')
s = s.replace('d Version 1.2.0', 'd Version 1.2.1', 1)
p.write_text(s, encoding='utf-8')

# Help
p = Path('hxempirical.sthlp')
s = p.read_text(encoding='utf-8')
s = s.replace('{* *! version 1.2.0  12aug2026}{...}', '{* *! version 1.2.1  12aug2026}{...}', 1)
needle = '''The start page keeps one stable layout. Search and six common research tasks stay\nat the top, current-data status and recent work appear on the right, and the full\nfunction catalog is shown directly below with natural scrolling. There is no\nexpand/collapse state and no reserved blank area.\n'''
replacement = '''The 1.2.1 interface follows the supplied 1672x941 reference layouts directly.\nThe start page uses a fixed left navigation rail, a Start Analysis card, five\nquick actions, current-data status, a 2-by-3 common-task area, recent work, and a\nsingle row of additional functions. The linear-model directory and OneClick\nworkspace use the same fixed card proportions and right-side guidance structure.\n'''
if needle in s:
    s = s.replace(needle, replacement, 1)
p.write_text(s, encoding='utf-8')

print('HX_PIXEL_MATCH_121_RELEASE_METADATA_OK')
