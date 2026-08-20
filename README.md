# HX Empirical Workbench (`hxempirical`)

## 当前版本

**当前发布版本：1.5.14**  
**支持：Stata 17 及以上版本**  
**平台：Windows / macOS**

## 唯一受支持的安装、更新与修复入口

在 Stata 17 或更高版本中运行：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"
```

首次安装、日常更新、同版本文件修复均使用以上命令。安装器会自动判断当前状态，并优先管理 `PERSONAL/h`；该位置不可写时才回退到 `PLUS/h`。

检测到多版本安装时运行：

```stata
hxempirical doctor
hxempirical repair
```

安装完成后彻底退出 Stata，重新打开并验证：

```stata
discard
which hxempirical
hxempirical about
hxempirical doctor
```

成功标准：

- `hxempirical about` 显示当前正式发布版本；
- `doctor` 显示 `[核心组件：正常] 11/11`；
- `doctor` 显示 `[安装路径：正常]`；
- `PERSONAL/h` 与 `PLUS/h` 不存在版本冲突；
- Stata 当前实际解析的文件与安装目标一致。

### 关于 net install

`net install` 仅作为兼容性测试接口保留，不属于日常安装、更新、修复、故障排查或发布验收流程。**不建议使用 `net install` 进行日常安装或更新。**

Stata 可能将传统包安装写入 `PLUS/h`，而更高优先级的 `PERSONAL/h` 旧副本仍会生效，进而形成“新版已经写入、旧版仍在运行”的路径遮挡。因此 README 不提供可复制执行的传统包安装命令。

## 项目简介

HX Empirical Workbench 是一个面向 Stata 的可视化实证分析工作台。它把 Stata 官方命令和成熟第三方命令组织成更容易使用的经管实证界面，同时始终显示最终 Stata 代码，便于检查、复制和复现。

核心原则是：**降低 Stata 的操作门槛，但不隐藏真实代码。**

工作台主要负责任务和命令搜索、变量选择与参数设置、实时 Stata 命令预览、运行前检查、外部命令检测、History 记录、运行监控、结果读取和多步骤 HX Workflow。最终估计和数据处理仍由真实 Stata 官方命令或用户已经安装的第三方命令执行。

## 主要功能

| 任务 | 实际命令 / 能力 |
|---|---|
| 普通线性回归 | `regress` |
| 固定效应 | `areg` / `reghdfe` / `xtreg` |
| PPML 高维固定效应 | `ppmlhdfe` |
| 工具变量 | `ivregress` / `ivreghdfe` |
| 双重差分 | `didregress` / `xtdidregress` |
| 描述统计 | `summarize` / `tabstat` |
| 数据合并 | `merge` / `append` |
| 数据结构转换 | `reshape` / `collapse` |
| 图形 | Stata 官方图形 + `coefplot` / `event_plot` |
| OneClick Workflow | 调用真实 `oneclick` / `oneclick_robustness` |
| 当前数据 | 轻量表格式查看与 Stata `replace` / `generate` 写入 |

完整 Statistics 目录覆盖 28 类、263 个唯一命令，并保留 Graphics、面板、时间序列、生存、IV、因果推断、SEM、Lasso、Meta、MI 等入口。

## 快速开始

安装完成并重新打开 Stata 后，可使用 Stata 自带数据测试：

```stata
sysuse auto, clear
hxempirical
```

例如在 `regress` 页面设置 Y=`price`、X=`mpg`、Controls=`weight`，工作台会生成并执行：

```stata
regress price mpg weight
```

## 第三方命令

hxempirical **不替用户安装第三方命令**。工作台只检测是否已安装，不再自动安装；需要某个第三方命令时，请按该命令作者的发布说明安装，安装完成后重新进入“外部命令”页面扫描即可。

常见外部命令包括 `reghdfe`、`winsor2`、`ivreghdfe`、`ppmlhdfe`、`oneclick`、`oneclick_robustness`、`coefplot` 和 `event_plot`。

`oneclick` 通过 SSC 安装，且依赖 `tuples`；这条依赖关系用于检测和兼容性说明，实际安装由用户自行完成。

`oneclick_robustness` 按作者扩展处理，当前未配置经过验证的 SSC 自动安装源，需要按作者发布说明手动安装；安装完成后 hxempirical 会自动识别。

## 安装器行为

事务式安装器遵循以下规则：

1. 优先使用可写的 `PERSONAL/h`；否则使用可写的 `PLUS/h`。
2. 完整发布包通过校验后才进入正式写入阶段。
3. 同版本但文件缺失或损坏时自动修复。
4. 有新版时先备份旧安装，再统一替换。
5. 写入完成后再次验证 Stata 当前实际解析到的 `hxempirical.ado` 路径和版本。
6. 当前有效路径或版本与目标不一致时，不报告成功。
7. 安装、更新、修复和卸载保持事务式；失败时恢复完整旧安装。
8. 不删除未经清单、版本、路径和所有权验证的用户文件。

`hxempirical doctor` 会同时检查 `PERSONAL/h`、`PLUS/h` 和当前实际生效的 `hxempirical.ado`，用于发现多版本路径遮挡。

## 离线安装

网络环境不稳定时，可从 GitHub Pages 下载完整 `hxempirical-release.zip`，完整解压后在 Stata 中执行解压目录里的 `hxinstall_offline.do`，并选择同一目录中的 `hxempirical.pkg`。离线包与在线安装器使用同一发布清单、逐文件完整性索引和事务式写入逻辑。

## 常用管理命令

查看版本：

```stata
hxempirical about
```

检查核心组件、路径和外部依赖：

```stata
hxempirical doctor
```

强制修复当前受管安装：

```stata
hxempirical repair
```

持久化菜单：

```stata
hxempirical menu persist
```

卸载：

```stata
hxempirical uninstall
```

经典兼容界面：

```stata
hxempirical, classic
```

## 发布与维护约束

仓库根目录的 [`AGENTS.md`](AGENTS.md) 定义 AI 和维护者必须遵守的安装与发布不变量。CI 会自动检查 README、安装器路径解析、发布版本和必要 smoke test 的接线，防止后续修改重新引入多入口或路径遮挡问题。

发布一致性由 `hxempirical.pkg`、源码公开版本、release ZIP、release index、Base64 分段、ZIP 重建校验、JAR / Java 来源绑定以及 installer / Statistics / static contract 检查共同约束。

## 文档

- [INSTALL.md](INSTALL.md)：详细安装、离线安装、更新、卸载和故障排查。
- [AGENTS.md](AGENTS.md)：AI / 维护者强制规则。
- [历史 README 与旧版本开发记录](docs/README-history-20260820.md)：重构 README 前保留的完整历史说明。

## 兼容性

- Stata 17 或更高版本；
- Windows / macOS；
- Java 11 字节码；
- Stata 自带 Java / SFI；
- 不依赖 Windows COM 或平台专属原生插件。
