from pathlib import Path

path = Path('README.md')
text = path.read_text(encoding='utf-8')

old = '''# HX Empirical Workbench (`hxempirical`)

## 当前版本与下载

**当前发布版本：1.4.9**  
**支持：Stata 17 及以上版本**  
**上次修改时间：2026-08-14 15:54（UTC+8）**

**安装源：** https://xiaowang5105.github.io/hxempirical/

在 Stata 命令窗口直接运行：

```stata
net install hxempirical, from("https://xiaowang5105.github.io/hxempirical/") replace force
```

安装完成后启动：

```stata
hxempirical
```

---
'''

new = '''# HX Empirical Workbench (`hxempirical`)

## 当前版本与下载

**当前发布版本：1.4.9**  
**支持：Stata 17 及以上版本**  
**上次修改时间：2026-08-14 17:06（UTC+8）**

### 推荐：让 Codex 帮你安装

不同电脑上的 Stata 版本、`PLUS` / `PERSONAL` 目录权限、`adopath` 和网络环境可能不同。为了减少 `r(603)`、目录不可写、下载源访问异常等安装问题，**建议直接让 Codex 根据当前电脑的实际环境完成安装和检查**。

可以把下面这段话直接发给 Codex：

> 请帮我在这台电脑上安装 `hxempirical`。仓库地址是 `https://github.com/xiaowang5105/hxempirical`。请先检查 Stata 版本、`sysdir`、`adopath`、`PLUS` / `PERSONAL` 写权限和网络访问情况，再选择适合当前系统的安装方式。安装完成后，请验证 `which hxempirical`、`hxempirical about`，并确认 `hxworkbench.jar` 可以被当前 Stata 使用。不要修改与 `hxempirical` 无关的 Stata 配置。

Codex 可以根据 Windows / macOS、个人电脑 / 学校机房、目录权限和网络情况选择不同安装路径，比要求所有电脑机械执行同一条命令更稳妥。

### 手动安装

如果希望自己安装，可以先使用 Stata 标准安装方式：

```stata
net install hxempirical, from("https://xiaowang5105.github.io/hxempirical/") replace force
```

安装完成后启动：

```stata
hxempirical
```

如果出现 `r(603)`、无法写入目录或下载失败，建议不要反复尝试同一条命令，直接把报错截图和本仓库地址交给 Codex 排查。

---
'''

if old not in text:
    raise SystemExit('top install block not found; README changed unexpectedly')
text = text.replace(old, new, 1)

marker = '## 修改记录\n\n### 2026-08-14 15:54（UTC+8）'
entry = '''## 修改记录

### 2026-08-14 17:06（UTC+8）

- README 安装说明改为优先建议使用 Codex 协助安装：先根据当前电脑的 Stata 版本、`sysdir`、`adopath`、目录写权限和网络环境选择合适安装方式，再做安装后验证。
- 保留 `net install` 作为手动安装方式；遇到 `r(603)`、目录不可写或下载异常时，建议把报错和仓库地址直接交给 Codex 排查，避免要求所有电脑机械使用同一安装路径。

### 2026-08-14 15:54（UTC+8）'''
if marker not in text:
    raise SystemExit('changelog marker not found; README changed unexpectedly')
text = text.replace(marker, entry, 1)

path.write_text(text, encoding='utf-8')
