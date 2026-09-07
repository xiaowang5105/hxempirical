# HX Empirical Workbench (`hxempirical`)

## 当前版本

**当前发布版本：1.6.2**

**支持：Stata 17 及以上版本**  
**平台：Windows / macOS**

本页版本号对应当前分支的源码和发布包。在线安装获取 GitHub Pages 已部署的正式版本；开发分支的新功能随代码合并和部署一并上线。

## 1.6.2 更新要点

- **完整 CSV 检查**：流式解码避免中文字符边界误判；按逻辑记录检查整个文件，支持引号内换行，保护后部出现的前导零和长整数。列数或引号异常会停止导入。文件检查在后台执行，更改输入会取消旧检查。
- **模型选择与表格**：比较与共同样本导出前可多选模型；支持命名，导出所选模型的 TSV 系数表（含标准误、N、R²、命令与样本说明）。扩展 bootstrap、jackknife、svy、mi estimate 前缀和常见估计量识别；共同样本重估仍限普通线性模型。
- **合并预检**：经 hxexecute 运行的普通 merge 先在临时 frame 检查键类型、缺失和所需唯一性。预检失败保留原数据；成功后由 Stata 输出匹配报告。
- **项目 ZIP**：打包项目、模型和可识别的本地数据依赖，提供相对路径 replay.do、文件校验清单和创建项目时的 Stata 环境信息。解压后切换到解压目录运行；宏、未加引号路径、工作目录切换与第三方命令版本仍需核对。

完整测试范围见 [1.6.2 验证记录](docs/VALIDATION-1.6.2.md)。

大数据项目可设置自动恢复点频率（默认每步，也支持每 5／10 步或仅手动）。降低频率会增加异常退出时未保存的步骤数；手动保存始终立即保存完整数据。

## 1.6.1 更新要点

- **转换文件保护**：输出必须为 DTA，并拒绝与原文件相同的文件目标；先写入同目录临时 DTA，保存成功后再替换已确认的目标，失败保留旧文件。批量转换先检查同名目标，覆盖已有 DTA 前列出清单并确认。
- **载入确认与失败恢复**：转换后载入、打开数据表及查看变量共用确认入口，检查载入返回码；失败保留当前数据和估计结果。转换完成与载入完成分别显示。
- **转换步骤可重放**：项目导出包含临时 frame 中的实际导入、保存及清理步骤，载入单独记录；转换参数在开始执行前固定，失败转换保留为注释。重放会重新生成并覆盖成功转换的输出 DTA，执行前请核对路径和外部原文件。

本阶段完成范围和后续工作见[核心流程路线图](docs/ROADMAP.md)。

## 1.6.0 已有功能

- **保存研究项目**：保存当前数据、工作台运行步骤和模型设置，支持重新打开项目及导出 do-file。
- **比较模型与样本**：查看系数、标准误和实际估计样本，并导出共同样本重估脚本。
- **保留 Stata 执行状态**：监控与内部查询保留 `r()` 返回结果，变量表达式在正式运行时求值，监控保留随机数状态。
- **完整记录模型设置**：最近模型区分样本条件、固定效应、标准误类型和权重，保留完整命令。
- **修复窗口关闭等待问题**，补充项目行为测试和发布校验。
- **项目恢复与保存保护（9 月 6 日修订）**：恢复失败保留原数据和随机数状态；每个完成步骤写入恢复点，手动保存保留上一版本；拒绝缺失资源和链接目录，清理不再被项目或备份引用的旧数据快照。
- **面板、IV 与数据编辑修复**：面板页自动执行的 `xtset` 纳入项目步骤和导出脚本；IV 设置保留内生变量、工具变量及估计方式；公式栏和单元格编辑使用原始值，确认未修改的单元格保持原值。

详细变化见 [更新记录](CHANGELOG.md)，测试环境与结果见 [1.6.0 验证记录](docs/VALIDATION-1.6.0.md)。

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
- `doctor` 显示 `[核心组件：正常] 13/13`；
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
| 研究项目 | 数据与模型快照、步骤记录、设置恢复、do-file 导出 |
| 模型比较 | 系数与标准误比较、实际估计样本核对、共同样本重估脚本 |

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

## 研究项目与模型比较

工作台顶部的“研究项目”菜单支持保存数据快照和完整运行步骤、重新打开项目、恢复模型设置、导出 do-file、比较系数和实际估计样本，并导出共同样本重估脚本。项目文件使用 `.hxproj`，与旁边的 `hx-assets-*` 目录一起保留。

1. 载入数据，点击“研究项目 → 新建项目”，保存分析起点。
2. 在工作台运行分析；每个完成步骤自动写入 `.hxproj.recovery`。选择“保存项目和当前数据”可正式保存，并保留上一版本 `.hxproj.bak`。
3. 再次打开项目，确认载入保存的数据；通过“查看步骤 / 恢复模型设置”继续分析。
4. 需要复现时导出 do-file，核对路径及外部依赖后运行；需要比较模型时查看系数和实际样本。

打开项目会恢复上次保存的数据和随机数状态，历史命令由导出的脚本重跑。在 Stata 命令窗口中手动执行的步骤需自行补入脚本。移动项目后请重新导出脚本，以更新数据路径。

共同样本重估支持普通 `regress`、`areg`、`xtreg`、`reghdfe` 命令；含复杂前缀、宏或多行命令的模型需手动处理。第三方命令及外部数据文件需一并准备。

详细使用方法和适用范围见 [研究项目说明](docs/PROJECTS.md)，本版变化见 [CHANGELOG.md](CHANGELOG.md)。

项目快照目前支持单 frame；存在多个 frame 时会明确停止保存或恢复，请先分别另存数据。完整 frameset、宏和外部文件依赖仍需自行保留。移动项目时同时带上 `.hxproj`、`.recovery`、`.bak` 和 `hx-assets-*`。再次打开原项目可选择较新的恢复点；运行中的命令尚未形成恢复点。自动快照会增加大型数据每步运行后的保存时间。项目上限为 10,000 步、64 MB 日志；不支持原子替换的文件系统会拒绝保存并保留旧文件。

监控的行预览最多检查前 5,000 行并明确显示范围，样本统计仍使用全部数据。

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
- [研究项目说明](docs/PROJECTS.md)：项目保存、继续分析、脚本导出和模型比较。
- [更新记录](CHANGELOG.md)：各版本功能与修复。
- [1.6.0 验证记录](docs/VALIDATION-1.6.0.md)：测试范围、数值核对和发布产物校验。
- [AGENTS.md](AGENTS.md)：AI / 维护者强制规则。
- [历史 README 与旧版本开发记录](docs/README-history-20260820.md)：重构 README 前保留的完整历史说明。

## 兼容性

- Stata 17 或更高版本；
- Windows / macOS；
- Java 11 字节码；
- Stata 自带 Java / SFI；
- 不依赖 Windows COM 或平台专属原生插件。

1.6.2 的验证环境为 Windows / StataNow 19.5 MP。真实 Stata、Java 与发布检查的具体结果见[验证记录](docs/VALIDATION-1.6.2.md)，1.6.0 的测试记录[另行保留](docs/VALIDATION-1.6.0.md)。当前分支的远端检查及网页部署状态见 [GitHub Actions](https://github.com/xiaowang5105/hxempirical/actions)。Stata 17/18 与 macOS 尚未在本次环境中实测。
