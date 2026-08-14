# hxempirical 安装

## 一行安装（推荐）

在 **Stata 17 或更高版本**的命令窗口运行：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"
```

安装完成后验证并启动：

```stata
which hxempirical
hxempirical about
hxempirical
```

安装器会把文件放进当前用户的 `PERSONAL` ado 目录，通常不需要管理员权限。它会先下载完整发布包，再统一写入正式目录；更新中途发生写入错误时，会恢复原有文件。

如果这是全新的 Stata 用户环境，安装器和 `hxempirical menu persist` 会先创建 `PERSONAL` 目录并验证写权限。这个处理同时适用于 Windows 和 macOS。

安装器还会：

- 检查 Stata 版本和 `PERSONAL` 写权限；
- 从 `hxempirical.pkg` 自动读取发布清单；
- 优先使用 GitHub Pages，并重试临时网络错误；
- 给每次安装建立独立的临时目录；
- 保存本地安装清单，供以后更新、清理旧文件和卸载使用；
- 先更新 `hxworkbench.jar`，发现文件正在使用时立即停止，避免只更新一半。

## 更新

在已安装 hxempirical 的 Stata 中运行：

```stata
hxempirical update
```

也可以直接运行安装器的更新模式：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do" update
```

如果已经打开 Java 工作台，请先关闭工作台。遇到 JAR 正在使用或 `r(602)` 时，关闭 Stata，重新打开后先执行更新命令。

## 卸载

```stata
hxempirical uninstall
```

或：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do" uninstall
```

卸载器会删除 `PERSONAL` 中由 hxempirical 清单管理的文件，并移除 HX 写入 `profile.do` 的菜单区块。完成后重新启动 Stata。

如果这台电脑以前多次使用 `net install` 安装过旧版本，Stata 的 `PLUS` 目录可能还保留旧的包登记。卸载器会提示使用：

```stata
ado dir hxempirical
ado uninstall [编号]
```

按列表中的编号逐项清理旧登记。

## 网络和权限问题

先确认浏览器能够打开：

```text
https://xiaowang5105.github.io/hxempirical/hxempirical.pkg
```

然后在 Stata 中检查：

```stata
sysdir
adopath
```

`hxempirical doctor` 会分别显示：

- **核心组件**：缺失时代表安装不完整；
- **可选扩展**：`reghdfe`、`winsor2`、`ivreghdfe`、`ppmlhdfe`、`oneclick`、`oneclick_robustness`、`coefplot`、`event_plot`。这些命令未安装不会影响工作台启动，只影响对应功能。

如果 Java 工作台在某台电脑上无法启动，可以运行：

```stata
hxempirical, classic
```

经典界面提供基础兼容操作，最新工作台功能以 Java 界面为准。

## macOS / 干净用户目录验证

从仓库根目录启动 Stata 后运行：

```stata
do "tests/cross_platform_core_smoke.do"
```

脚本会把 `PERSONAL` 临时指向测试目录，检查目录自动创建、菜单持久化幂等性、菜单移除和核心/可选依赖诊断，最后恢复原来的 `PERSONAL` 设置并清理测试文件。

GitHub Raw 在部分学校网络、代理环境和 Stata TLS 环境中可能无法稳定读取，因此安装说明统一使用 GitHub Pages 地址。

## 传统包管理方式（高级）

GitHub Pages 仍支持 Stata 标准包安装：

```stata
net install hxempirical, from("https://xiaowang5105.github.io/hxempirical/") replace force
```

请选择一种安装方式并持续使用。普通用户建议一直使用上面的一行安装器；这样更新和卸载都由同一份本地清单管理。
