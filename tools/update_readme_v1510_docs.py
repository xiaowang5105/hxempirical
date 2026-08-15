from pathlib import Path
import re

p = Path('README.md')
s = p.read_text(encoding='utf-8')

s = s.replace('**上次修改时间：2026-08-15 21:10（UTC+8）**', '**上次修改时间：2026-08-15 21:28（UTC+8）**')

marker = '### 1.5.10 安装布局统一\n\n'
insert = (
    '### 1.5.10 安装布局统一\n\n'
    '- **以后安装、更新、修复统一只记一条命令：** `do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"`。不需要区分首次安装和日常更新。\n'
)
if marker not in s:
    raise SystemExit('missing v1.5.10 marker')
s = s.replace(marker, insert, 1)

old_install_head = '''### 安装或更新

#### 方法 A：在线安装

网络能够稳定访问 GitHub Pages 时，在 **Stata 17 或更高版本**的命令窗口运行：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"
```

这一条命令同时负责安装、检查更新和修复缺失文件。公开的 `hxinstall.do` 只有一个很短的启动段，复杂安装逻辑在后台 `.ado` 中执行，Results 不再逐行显示几百行安装器核心源码：
'''
new_install_head = '''### 安装与日常更新

#### 推荐方式：固定使用这一条命令

以后无论是**第一次安装、日常更新，还是修复缺失文件**，都在 **Stata 17 或更高版本**的命令窗口运行同一条命令：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"
```

**日常使用只需要记住这一条。** 安装器会自动判断当前状态，不需要先运行 `net install`，也不需要手工判断版本。公开的 `hxinstall.do` 只有一个很短的启动段，复杂安装逻辑在后台 `.ado` 中执行：
'''
if old_install_head not in s:
    raise SystemExit('install section header changed unexpectedly')
s = s.replace(old_install_head, new_install_head, 1)

needle = '- 安装、更新和修复完成后都会尝试建立唯一的 **用户（User） > 我的实证工具箱** 菜单入口；若 `PERSONAL/profile.do` 不可写，核心安装仍然成功，重启后直接运行 `hxempirical`。\n'
if needle not in s:
    raise SystemExit('install bullets changed unexpectedly')
s = s.replace(needle, needle + '- 如果本次更新包含 Java 工作台/JAR 变化，安装完成后请**彻底退出 Stata 再重新打开**，避免当前会话继续使用旧 Java 类。\n', 1)

third_party_pattern = re.compile(r'## 第三方命令\n\n.*?\n## 更新\n', re.S)
third_party_new = '''## 第三方命令

hxempirical **不负责替用户安装第三方命令**。工作台只检测是否已安装，不再自动安装；你需要什么外部命令，就按该命令作者的官方说明自行安装，安装完成后重新进入工作台的“外部命令”页面即可自动发现和使用。

当前常见外部命令包括：

- `reghdfe`
- `winsor2`
- `ivreghdfe`
- `ppmlhdfe`
- `oneclick`
- `oneclick_robustness`
- `coefplot`
- `event_plot`

检查当前环境：

```stata
hxempirical doctor
```

OneClick 专区调用的是作者发布的真实外部命令。`oneclick` 通过 SSC 安装，且依赖 `tuples`；这条依赖关系用于检测和兼容性说明，实际安装由用户自行完成。`oneclick_robustness` 按作者扩展处理，当前未配置经过验证的 SSC 自动安装源，需要按作者发布说明手动安装；安装完成后 hxempirical 会自动识别。

候选控制变量仍应依据理论、文献与识别设计确定。

## 更新
'''
if not third_party_pattern.search(s):
    raise SystemExit('third-party section not found')
s = third_party_pattern.sub(third_party_new, s, count=1)

update_pattern = re.compile(r'## 更新\n\n.*?\n## 常用管理命令\n', re.S)
update_new = '''## 更新

以后更新固定使用：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"
```

安装器会自动读取最新版本并判断：

- 当前没有安装：执行首次安装；
- 有新版本：备份后更新；
- 已是最新版且文件完整：直接提示无需更新；
- 版本相同但文件缺失：自动修复；
- 检测到 1.5.9 及以前遗留在 `PERSONAL` 根目录的旧 HX 文件：迁移到标准 `PERSONAL/h` 后清理旧影子文件。

更新完成后可以运行：

```stata
hxempirical about
```

确认版本。如果更新涉及 Java 工作台/JAR，请彻底退出 Stata 后重新打开，再运行 `hxempirical`。

`hxempirical update` 仍可使用，它会转到同一安装器；日常不需要记两套更新命令。

## 常用管理命令
'''
if not update_pattern.search(s):
    raise SystemExit('update section not found')
s = update_pattern.sub(update_new, s, count=1)

s = s.replace(
    '卸载器会删除 `PERSONAL` 中由本地清单管理的文件，并移除 HX 写入 `profile.do` 的菜单区块。若电脑以前多次使用 `net install` 安装过旧版本，卸载器会提示通过 `ado dir hxempirical` 和 `ado uninstall [编号]` 清理旧的 `PLUS` 包登记。完成后重新启动 Stata。',
    '卸载器会删除标准安装目录 `PERSONAL/h`（或回退时的 `PLUS/h`）中由本地清单管理的文件，并清理旧版遗留在 `PERSONAL` 根目录的 HX 影子文件，同时移除 HX 写入 `profile.do` 的菜单区块。若电脑以前多次使用 `net install` 安装过旧版本，卸载器会提示通过 `ado dir hxempirical` 和 `ado uninstall [编号]` 清理旧包登记。完成后重新启动 Stata。'
)

s = s.replace(
    '请选择一种安装方式并持续使用。推荐的一行安装器同时管理更新和卸载，可避免 `PLUS` 权限问题及重复包登记。',
    '`net install` 仍作为 Stata 传统包管理入口保留，但**不建议把它作为日常更新入口**。日常安装、更新和修复统一使用上面的 `hxinstall.do` 一行命令，避免再出现多套安装流程并存。'
)

s = s.replace(
    '5. 完善命令解析、自动页面生成、运行监控、结果读取和 History。',
    '5. 完善命令解析、自动页面生成、运行监控、结果读取和外部命令管理。'
)

record_marker = '## 修改记录\n\n'
if record_marker not in s:
    raise SystemExit('change log marker missing')
s = s.replace(record_marker, record_marker + '> 说明：以下旧记录保留当时版本的历史行为；当前安装、更新和第三方命令策略以上方“安装与日常更新”“第三方命令”章节为准。\n\n', 1)

p.write_text(s, encoding='utf-8')
print('README_V1510_DOCS_OK')
