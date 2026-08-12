from pathlib import Path

STAMP = "2026-08-12 20:11（UTC+8）"

# README: version, top timestamp, cumulative change record, version record.
p = Path("README.md")
s = p.read_text(encoding="utf-8")
s = s.replace("**当前发布版本：1.1.0**", "**当前发布版本：1.2.0**", 1)
s = s.replace("**上次修改时间：2026-08-12 19:41（UTC+8）**", f"**上次修改时间：{STAMP}**", 1)
record = f'''### {STAMP}\n\n**修改时间**：{STAMP}\n\n**修改内容**：\n\n- 按最终视觉稿重构 Java 工作台整体外壳：新增固定左侧导航栏，统一为“工作台 / 数据 / 回归 / 检验 / OneClick / 历史 / 设置”，当前模块使用浅蓝高亮，辅助入口与版本信息收在侧栏底部。\n- 首页改成正式桌面研究软件式工作台：顶部“开始分析”负责搜索任务或命令，并保留基准回归、固定效应、双重差分、描述统计、OneClick 五个快速入口；中部展示常用任务、当前数据和最近任务；底部“更多功能”直接展示，不再存在展开 / 收起状态。\n- 普通任务页统一为“页面标题 + breadcrumb + 紧凑操作区 + 白色圆角内容卡 + 底部真实 Stata 命令”的布局；右侧数据 / 结果 / 运行区改成独立圆角信息卡，主工作区与右侧信息区约按 68% / 32% 分配。\n- 基准回归继续采用任务优先逻辑：默认 `xtreg`，页内小型估计方法选择器切换 `xtreg` / `reghdfe` / `areg` / `regress`；切换时保留 Y、核心 X、Controls、样本、权重与聚类等公共研究设定。\n- 命令 / 方法选择页同步改为统一标题、固定导航与圆角目录卡，不再回到旧式多窗格导航；OneClick、数据检查等现有业务逻辑继续保留，视觉壳统一到新设计。\n- 状态栏、按钮、间距、标题层级、卡片边框和页面背景统一；Java 11 / class major 55 编译、首页 / 方法目录 / 基准回归 / OneClick 四类离线 UI 渲染测试通过，并同步重建 `hxworkbench.jar`。\n\n'''
marker = "## 修改记录\n\n"
if record not in s:
    if marker not in s:
        raise SystemExit("README missing modification history marker")
    s = s.replace(marker, marker + record, 1)
version_record = f'''### 1.2.0（当前版本）\n\n**发布时间**：{STAMP}\n\n**修改内容**：\n\n- 按确认的视觉稿完成工作台整体 UI 重构，建立固定左侧导航与统一的桌面研究软件视觉系统。\n- 首页重新组织为开始分析、快速开始、常用任务、当前数据、最近任务和更多功能。\n- 普通工作区、方法目录、右侧数据 / 结果区和底部真实 Stata 命令区统一成同一套卡片与层级规范。\n- 基准回归继续使用任务工作区和紧凑估计器切换，不牺牲真实 Stata 命令与参数透明度。\n\n'''
version_marker = "## 版本记录\n\n"
if version_record not in s:
    if version_marker not in s:
        raise SystemExit("README missing version history marker")
    s = s.replace(version_marker, version_marker + version_record, 1)
s = s.replace("### 1.1.0（当前版本）", "### 1.1.0", 1)
p.write_text(s, encoding="utf-8")

# Package manifest.
p = Path("hxempirical.pkg")
s = p.read_text(encoding="utf-8").replace("d Version 1.1.0", "d Version 1.2.0", 1)
p.write_text(s, encoding="utf-8")

# Public entry point.
p = Path("hxempirical.ado")
s = p.read_text(encoding="utf-8")
s = s.replace("*! hxempirical 1.1.0  12aug2026", "*! hxempirical 1.2.0  12aug2026", 1)
s = s.replace('display as text "版本：" as result "1.1.0"', 'display as text "版本：" as result "1.2.0"', 1)
s = s.replace('return local version "1.1.0"', 'return local version "1.2.0"', 1)
p.write_text(s, encoding="utf-8")

# Help version and updated UI description.
p = Path("hxempirical.sthlp")
s = p.read_text(encoding="utf-8")
s = s.replace("{* *! version 1.1.0  12aug2026}{...}", "{* *! version 1.2.0  12aug2026}{...}", 1)
needle = "{cmd:hxempirical} opens one workbench containing command navigation, command\nsettings, a live command preview, and a read-only view of the dataset currently\nin Stata memory. Commands run in Stata itself. The complete command is added to\nStata's History window before execution."
replacement = "{cmd:hxempirical} opens one desktop-style workbench with a fixed left sidebar,\ntask-oriented pages, live command preview, and a read-only view of the dataset\ncurrently in Stata memory. Commands run in Stata itself. The complete command is\nadded to Stata's History window before execution."
if needle in s:
    s = s.replace(needle, replacement, 1)
p.write_text(s, encoding="utf-8")

print("HX_UI_120_RELEASE_METADATA_OK")
