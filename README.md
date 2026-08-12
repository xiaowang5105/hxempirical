# HX Empirical Workbench (`hxempirical`)

## 当前版本与下载

**当前发布版本：1.2.0**  
**支持：Stata 17 及以上版本**  
**上次修改时间：2026-08-12 20:11（UTC+8）**

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

## 项目简介

**HX Empirical Workbench** 是一个面向 Stata 的可视化实证分析工作台。

它的目标不是重新实现 Stata 已经成熟的统计命令，而是把常见的经管实证任务组织成更容易使用的界面：选择任务、选择变量、设置参数、实时查看命令，然后仍由 Stata 执行真实命令。

适用场景主要包括经济学、金融学、管理学等领域的课程论文、硕士论文和常规实证研究。对于不熟悉 Stata 命令语法的用户，可以通过界面降低操作门槛；对于已经熟悉 Stata 的用户，也可以把工作台作为命令组织、检查和快速配置工具。

## 它能做什么

hxempirical 目前主要提供以下能力：

- **任务式工作区与命令搜索**：基准回归等高频研究任务可直接进入工作区；具体估计器只占一个小型切换控件。同时也可以直接搜索 Stata 命令名。
- **可视化参数设置**：通过界面选择因变量、解释变量、控制变量、固定效应、聚类标准误、权重、`if/in` 等参数。
- **实时命令预览**：工作台始终显示最终准备提交给 Stata 的完整命令，便于检查、复制和复现。
- **普通回归与面板模型**：支持 `regress`、`areg`、`xtreg`、`qreg`、`rreg`、`newey`、`prais` 等 Stata 官方命令。
- **高维固定效应与 PPML**：支持 `reghdfe`、`ppmlhdfe` 等成熟第三方命令。
- **工具变量模型**：支持 `ivregress`、`ivreghdfe` 等命令，并提供内生变量、工具变量等结构化输入。
- **统计与检验**：支持描述统计、相关分析、均值检验、频数列联、常见 postestimation 等功能。
- **数据处理**：支持变量生成与修改、缺失值检查、重复值检查、`keep/drop`、`merge`、`append`、`reshape`、`collapse`、`xtset`、`tsset` 等操作。
- **文件导入与转换**：支持 DTA、Excel、CSV 等常见数据文件，并提供 Excel / CSV / TXT / TSV 转换为 `.dta` 的工作流。
- **图形与结果展示**：支持常见分布图、关系图、回归结果图，以及 `coefplot`、`event_plot` 等第三方图形命令。
- **Stata 官方 DID**：把 `didregress`（重复截面）和 `xtdidregress`（面板 / 纵向数据）作为普通命令直接使用；不再单独展示 HX DID 专区。
- **OneClick Workflow**：直接调用作者发布的真实 `oneclick` / `oneclick_robustness` 命令，并负责参数组织、运行隔离和结果读取。
- **运行监控**：记录最终命令、开始与结束时间、耗时、返回码以及可获得的数据变化和估计结果。
- **最近工作恢复**：保存最近使用的模型设置，方便重新打开后继续编辑。
- **Stata History**：完整命令继续写入 Stata History，便于后续整理成正式 `.do` 文件。

## 核心结构

hxempirical 目前分为两类功能。

### 普通命令

普通命令优先调用 **Stata 官方命令** 或 **成熟第三方命令**。

常见例子包括：

| 任务 | 实际命令 |
|---|---|
| 普通线性回归 | `regress` |
| 固定效应 | `areg` / `reghdfe` / `xtreg` |
| PPML 高维固定效应 | `ppmlhdfe` |
| 工具变量 | `ivregress` / `ivreghdfe` |
| 双重差分 | `didregress` / `xtdidregress` |
| 描述统计 | `summarize` / `tabstat` |
| 缩尾 | `winsor2` |
| 数据合并 | `merge` / `append` |
| 数据结构转换 | `reshape` / `collapse` |
| 系数图 | `coefplot` |

普通功能同时支持**任务入口**和**命令入口**：高频研究任务直接进入稳定工作区，在页内用紧凑下拉框切换真实估计命令；已知具体命令时仍可通过搜索直接打开。常用参数放前面，低频参数放到“更多设置”中。

HX 在这一层主要负责命令查找、中文说明、参数界面、变量选择、代码生成、运行前检查、依赖检测、History 记录、运行监控和结果读取。最终的估计与数据处理仍由对应的真实 Stata / 第三方命令完成。

### HX Workflow / 专区

Workflow 用于组织“一个完整研究任务”，而不是单独包装某一个命令。

当前自定义专区主要保留：

- **OneClick 专区**：调用真实外部 `oneclick` / `oneclick_robustness`，并补充参数组织、结果读取和运行隔离。

DID 不再作为 HX 专区重复实现；标准 DID 优先进入普通命令层，直接调用 Stata 官方 `didregress` / `xtdidregress`。

后续机制分析、稳健性分析、异质性分析等完整研究任务也可以继续按 Workflow 方式扩展。

## 设计原则

hxempirical 的核心原则是：**降低 Stata 的使用门槛，但不隐藏真实代码。**

普通命令遵循以下规则：

1. 已有 Stata 官方命令时，直接调用官方命令。
2. 已有成熟第三方实现时，调用原作者发布的命令。
3. 不为了做界面而重复实现已有统计估计方法。
4. 一个普通命令对应一个页面。
5. 常用参数优先显示，低频参数放入“更多设置”。
6. 界面实时生成最终 Stata 命令。
7. 运行前检查主要在后台完成，只有发现异常时才提示。
8. HX 自定义逻辑主要用于 GUI、解析、检查、调度、结果读取和 Workflow。

因此，工作台生成的命令可以直接复制到 `.do` 文件中，作为正式研究代码继续使用。

## 快速开始

可以先使用 Stata 自带的 `auto` 数据测试：

```stata
sysuse auto, clear
hxempirical
```

例如进入 `regress` 页面并设置：

- Y：`price`
- X：`mpg`
- Controls：`weight`

工作台会生成：

```stata
regress price mpg weight
```

确认后直接运行即可。

## 第三方命令

安装 hxempirical 本身不会一次性安装全部社区命令。进入相关功能时，工作台会检查目标命令是否已经安装；对于已配置可靠安装来源的命令，可以按需安装。

当前登记的可选命令包括：

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

安装指定扩展命令，例如：

```stata
hxempirical install reghdfe
```

OneClick 专区执行的是作者发布的真实外部命令。候选控制变量仍应依据理论、文献与识别设计确定。

## 更新

重新运行安装命令即可覆盖更新：

```stata
net install hxempirical, from("https://xiaowang5105.github.io/hxempirical/") replace force
```

也可以运行：

```stata
hxempirical update
```

如果当前 Stata 会话已经加载过 hxempirical，并在更新时出现 Java/JAR 文件正在使用或 `r(602)`，请关闭 Stata，重新打开后先执行安装或更新命令，再启动工作台。

## 常用管理命令

查看版本和环境：

```stata
hxempirical about
```

打开经典 Stata 对话框界面：

```stata
hxempirical, classic
```

仅在当前 Stata 会话添加菜单入口：

```stata
hxempirical menu
```

以后每次启动 Stata 都显示菜单入口：

```stata
hxempirical menu persist
```

移除持久菜单：

```stata
hxempirical menu remove
```

菜单位置：**用户（User） > 我的实证工具箱**

## 卸载

如果曾启用持久菜单，先运行：

```stata
hxempirical menu remove
```

然后卸载：

```stata
ado uninstall hxempirical
```

更新或卸载后重新启动 Stata，可以释放已经加载的 Java 类。

## 兼容性

- Stata 17 或更高版本
- Windows / macOS 按跨平台方式设计
- Java 工作台基于 Stata 自带 Java / SFI 接口
- Java 工作台无法启动时，可以使用经典界面：

```stata
hxempirical, classic
```

## 当前开发方向

当前开发继续围绕以下方向推进：

1. 普通功能统一调用真实 Stata 官方命令或成熟第三方命令。
2. 继续清理与现成命令重复的历史 HX 实现。
3. 普通命令页统一采用“常用参数 → 更多设置 → 最终命令”的结构。
4. 多步骤特调功能统一收归 HX Workflow。
5. 完善命令解析、自动页面生成、运行监控、结果读取和 History。
6. 持续扩展经管实证研究常用命令与 Workflow。

---

## 修改记录

### 2026-08-12 20:11（UTC+8）

**修改时间**：2026-08-12 20:11（UTC+8）

**修改内容**：

- 按最终视觉稿重构 Java 工作台整体外壳：新增固定左侧导航栏，统一为“工作台 / 数据 / 回归 / 检验 / OneClick / 历史 / 设置”，当前模块使用浅蓝高亮，辅助入口与版本信息收在侧栏底部。
- 首页改成正式桌面研究软件式工作台：顶部“开始分析”负责搜索任务或命令，并保留基准回归、固定效应、双重差分、描述统计、OneClick 五个快速入口；中部展示常用任务、当前数据和最近任务；底部“更多功能”直接展示，不再存在展开 / 收起状态。
- 普通任务页统一为“页面标题 + breadcrumb + 紧凑操作区 + 白色圆角内容卡 + 底部真实 Stata 命令”的布局；右侧数据 / 结果 / 运行区改成独立圆角信息卡，主工作区与右侧信息区约按 68% / 32% 分配。
- 基准回归继续采用任务优先逻辑：默认 `xtreg`，页内小型估计方法选择器切换 `xtreg` / `reghdfe` / `areg` / `regress`；切换时保留 Y、核心 X、Controls、样本、权重与聚类等公共研究设定。
- 命令 / 方法选择页同步改为统一标题、固定导航与圆角目录卡，不再回到旧式多窗格导航；OneClick、数据检查等现有业务逻辑继续保留，视觉壳统一到新设计。
- 状态栏、按钮、间距、标题层级、卡片边框和页面背景统一；Java 11 / class major 55 编译、首页 / 方法目录 / 基准回归 / OneClick 四类离线 UI 渲染测试通过，并同步重建 `hxworkbench.jar`。

### 2026-08-12 19:41（UTC+8）

**修改时间**：2026-08-12 19:41（UTC+8）

**修改内容**：

- 在 1.1.0 最终自查中补齐基准回归任务工作区的“继续工作 / 最近工作恢复”：现在会保存并恢复当前估计器、Y、核心 X、Controls、分类/交互/滞后项、`xtreg` 模型、`absorb()`、VCE、Cluster、`if/in`、权重和高级 options，不会因为切换估计方法而丢失任务状态。
- 旧版普通 `regress` 快照继续恢复到真正的 `regress` 页面，不会因为“基准回归”默认改为 `xtreg` 而误跳到任务工作区；VIF、异方差等普通 OLS 诊断搜索也继续进入真实 `regress` 后估计页面。
- 修正上述兼容边界后重新执行 Java 11 编译、class major 55 检查、JAR 重建，以及首页、命令目录、基准回归工作区三类离线 UI 渲染测试，最终验证通过。

### 2026-08-12 19:14（UTC+8）

**修改时间**：2026-08-12 19:14（UTC+8）

**修改内容**：

- 首页取消“展开全部功能 / 收起全部功能”机制，不再为了折叠状态固定上半区高度；完整功能目录直接展示并自然滚动，消除折叠时的大面积空白和展开前后的跳动。
- “基准回归”升级为任务工作区：点击首页后直接进入，不再先浏览命令卡；默认估计器为 `xtreg`（FE），右上角用小型“估计方法”下拉框切换 `xtreg` / `reghdfe` / `areg` / `regress`。
- 切换基准回归估计器时保留 Y、核心 X、Controls、样本条件、聚类、权重和已构造项等公共设置，仅替换 `xtreg` 模型、`absorb()` 等估计器特有字段以及最终真实 Stata 命令。
- 命令选择页改为紧凑目录，不再为每个命令铺设“适合 / 示例 / 区别”大卡片；只保留命令名、中文名称、一句话用途和 `Stata 官方` / `第三方` / `HX Workflow` 来源标签。
- 修复“普通线性回归 / 固定效应线性回归 / 特殊线性回归 / 分位数回归 / 时间序列线性回归”的 method-code 映射，并在每次读取方法时清除旧命令选择，防止标题已经切换但列表仍残留上一页命令。
- Java 工作台、JAR、help、package manifest、README 和公开版本信息同步升级为 **1.1.0**。

### 2026-08-12 17:18（UTC+8）

**修改时间**：2026-08-12 17:18（UTC+8）

**修改内容**：

- 固定开始页“展开全部功能 / 收起全部功能”控制区的垂直位置；展开完整功能目录时，按钮不再因为上方任务区被压缩而上下跳动。
- 按“官方命令优先”原则取消公开的 HX DID 专区入口；标准 DID 改为回归模型中的普通命令方法。
- 新增 Stata 官方 `didregress` 与 `xtdidregress` 页面：重复截面使用 `didregress`，面板 / 纵向数据使用 `xtdidregress`；页面结构化填写结果变量、协变量、处理变量、`group()`、`time()`、权重和标准误，并生成真实官方 Stata 命令。
- 首页“双重差分”、完整功能目录和 DID 关键词搜索全部改为进入官方 DID 命令选择页；旧 `did_builder` / `did_trends` / `event_plot` 不再作为 DID 专区公开导航。
- DID 运行前增加核心变量角色和必填项检查；`xtdidregress` 页面明确提示先使用 `xtset` 声明面板结构。
- 修正通用命令生成中的权重位置，使 `[weight=var]` 位于 `if/in` 之后，更符合 Stata 官方 syntax 顺序。
- Java 工作台、Stata 命令目录、语义层、解析兜底、命令生成、help、package manifest 与 README 同步更新为 **1.0.3**，并重新构建 `hxworkbench.jar`。

### 2026-08-12 16:49（UTC+8）

**修改时间**：2026-08-12 16:49（UTC+8）

**修改内容**：

- 重新组织 README 首页结构，将**当前版本号、安装源和一行安装命令置顶**，用户打开仓库后可以直接看到当前版本和安装方式。
- 重写项目简介、“它能做什么”、核心结构、设计原则、快速开始、第三方命令、更新、管理、兼容性等说明，使 README 更接近正式软件项目首页，而不是开发日志页面。
- 版本记录和历史开发记录继续保留在 README 后部，不删除此前记录。
- 本次仅修改 README 文档，不改变 hxempirical 程序功能；当前发布版本仍为 **1.0.2**。

## 版本记录

### 1.2.0（当前版本）

**发布时间**：2026-08-12 20:11（UTC+8）

**修改内容**：

- 按确认的视觉稿完成工作台整体 UI 重构，建立固定左侧导航与统一的桌面研究软件视觉系统。
- 首页重新组织为开始分析、快速开始、常用任务、当前数据、最近任务和更多功能。
- 普通工作区、方法目录、右侧数据 / 结果区和底部真实 Stata 命令区统一成同一套卡片与层级规范。
- 基准回归继续使用任务工作区和紧凑估计器切换，不牺牲真实 Stata 命令与参数透明度。

### 1.1.0

**发布时间**：2026-08-12 19:41（UTC+8）

**修改内容**：

- 首页改为单一稳定状态，完整功能目录始终显示。
- 基准回归改为任务工作区，默认 `xtreg`，页内紧凑切换 `reghdfe` / `areg` / `regress` 并保留公共变量设置。
- 命令选择页压缩为目录式布局，并修复方法切换后的命令列表残留问题。
- 最近工作恢复同步适配任务工作区，并保持旧 `regress` 快照与 OLS 诊断入口兼容。

### 1.0.3

**发布时间**：2026-08-12 17:18（UTC+8）

**修改内容**：

- 稳定开始页展开 / 收起按钮位置。
- 标准 DID 改为优先使用 Stata 官方 `didregress` / `xtdidregress`，不再公开单独 HX DID 专区。
- DID 页面、搜索、命令目录、运行前检查和真实命令生成同步完成；权重语法顺序一并修正。

### 1.0.2

**发布时间**：2026-08-12 16:31（UTC+8）

**修改内容**：

- 修复工作台点击“查看帮助”后 Stata Viewer 可能被工作台窗口遮挡的问题。帮助命令成功打开后，继续调用 Stata 官方 `window manage forward viewer` 将 Viewer 窗口置于最前；不再需要手动最小化或切换工作台才能看到帮助页。
- 该修复只调整窗口前后顺序，不改变帮助内容、命令解析、回归执行或数据处理逻辑。
- 同步更新 Java 工作台、Stata 入口、package manifest、help 与 README 版本为 **1.0.2**，并重新构建 `hxworkbench.jar`。

### 1.0.1

**发布时间**：2026-08-12 16:07（UTC+8）

**修改内容**：

- 修复开始页“展开全部功能”前后因垂直滚动条出现/消失造成的页面宽度跳动；开始页与命令选择页不再显示突兀的垂直滚动条，鼠标滚轮仍可正常滚动，展开、收起时主内容也不再左右位移。
- 工作页面和命令选择页面统一使用两个固定导航键：`← 上一级` 与 `首页`；取消“返回 OneClick 专区”“返回某某方法”等随页面变化的长按钮文案，也不再把首页按钮单独放在顶栏右侧。
- 面包屑路径改为真正的层级导航：`首页 › 分类 › 方法 › 当前命令`；首页、分类和方法等上级节点可直接点击，当前节点保持不可点击。
- 导航层级和按钮职责统一：`上一级` 只回到父级，`首页` 始终直接回到开始页，避免同一页面出现两个含义相近但位置、文案不同的“返回”入口。
- 同步修正 Java 工作台内部版本常量与版本输出，使 `HxWorkbench`、Stata 入口、package manifest、help 和 README 全部统一为 **1.0.1**；重新构建 `hxworkbench.jar` 并执行离线界面 smoke test。

### 1.0.0

**发布时间**：2026-08-12 15:46（UTC+8）

**版本说明**：2026-08-12 13:37—15:08 期间完成的普通命令层重构、界面调整、命令生成修正、运行前检查、Java 工作台重建与最终自查，全部统一归入 **hxempirical 1.0.0**。这些记录是同一个大版本的开发过程，不再视为多个独立发布版本。

<details>
<summary><strong>展开查看 1.0.0 开发过程记录</strong></summary>

### 2026-08-12 15:08（UTC+8）

**修改时间**：2026-08-12 15:08（UTC+8）

**修改内容**：

- 完成当前普通命令目录的逐项收尾审查；普通命令继续只生成并执行真实 Stata 官方命令或成熟第三方命令，HX 自定义逻辑继续集中在界面、解析、检查、调度、结果读取与 Workflow。
- 数据处理页补齐 `duplicates` / `misstable` 的明确语义；修正 `collapse` 的多变量 `by()` 设置，并为 `reshape`、`xtset`、`tsset` 提供与真实语法一致的字段名称。
- 统计检验页补齐 `ttest` 的角色说明与运行前检查，避免单样本、分组和配对三种模式混淆。
- 线性与特殊估计命令进一步结构化：`qreg` 的 `quantile()`、`cnsreg` 的 `constraints()`、`vwls` 的 `sd()`、`eivreg` 的 `reliab()`、`newey` 的 `lag()` 均提供直接字段，不再要求用户把最关键参数全部手写在高级 options 中。
- 修正 `margins` 代码生成位置，使 `dydx()` / `at()` 等内容按 Stata option 语法进入逗号后；`coefplot` 与 `event_plot` 增加命令主体输入入口，保留原作者命令语法。
- 特殊图形页统一为“核心变量直接显示，if 与低频图形 options 收入更多设置”，并在切换图形时清理上一页隐藏状态，避免旧筛选条件或图形选项被无意带入；普通图形导航不再把 HX 的 `did_trends` 当作普通图形方法展示。
- 补齐 `tsset`、`rreg`、`cnsreg`、`vwls`、`eivreg`、`newey`、`prais` 等命令的面包屑归类和帮助映射；普通命令运行前增加必要字段与明显角色冲突检查，并补上 `keep/drop` 模式必填项及 `tabstat` 变量必填检查。
- 通用命令页切换时清理上一条命令残留的字段状态，并应用语义默认值；`areg` 固定效应选择限制为单变量，其他 HDFE 命令继续支持多选。
- Java 工作台与 `hxworkbench.jar` 同步重建；完整离线 UI preview 集合、Java 11 / class major 55、命令目录覆盖和关键代码生成规则均纳入最终 smoke test。

### 2026-08-12 14:28（UTC+8）

**修改时间**：2026-08-12 14:28（UTC+8）

**修改内容**：

- 继续清理 `reghdfe`、`ppmlhdfe`、`ivregress`、`ivreghdfe`、`xtreg` 这组常用估计命令的普通命令页，统一“核心模型参数 → 标准误 → 更多设置”的层级。
- IV 页面把内生变量与工具变量提升到主要参数区；`ivregress` 的估计方法紧随核心变量设置，`ivreghdfe` 的固定效应与 VCE 继续保留在主页面。
- 面板命令开始使用显式语义默认值：`xtreg`、`xtlogit`、`xtprobit` 默认选择随机效应（RE），同时仍可在页面切换其他可用模型。
- 未安装 `reghdfe`、`ppmlhdfe`、`ivreghdfe` 时，最低命令契约仍保留因变量、解释变量、`if/in`、权重、`absorb()`、VCE 和 Cluster 等原生命令入口。
- 权重类型按命令收窄：`reghdfe` 提供 `fweight/aweight/pweight`，`ppmlhdfe` 提供 `fweight/pweight`，`ivreghdfe` 保留四类权重；避免界面生成命令本身不接受的权重类型。
- 对这组重点估计命令增加运行前结构检查：IV 角色重复或缺失、Cluster 变量缺失、权重变量缺失时先提示，不提交明显不完整的命令。
- `hxsemantics` 更新到 1.3.2，`hxresolve` 更新到 3.1.2；Java 工作台与 `hxworkbench.jar` 同步重建并通过编译和离线界面 smoke test。

### 2026-08-12 14:20（UTC+8）

**修改时间**：2026-08-12 14:20（UTC+8）

**修改内容**：

- 开始把普通命令的通用 Java 页面统一调整为“常用参数在前、低频参数放入更多设置”。
- 通用普通命令页中的 `if`、`in` 不再直接铺在主页面，统一收入“更多设置”；主页面继续保留该命令自身的因变量、解释变量、模型类型、`absorb()`、工具变量、标准误和按需显示的 Cluster 等常用字段。
- 为通用普通命令页补上结构化权重设置：支持 `fweight`、`aweight`、`pweight`、`iweight` 和权重变量，并继续生成真实 Stata `[weight=var]` 语法。
- “更多设置”现在统一容纳 `if`、`in`、权重和其他低频 Stata options；普通命令最终仍由 `hxpreview` 生成并执行真实 Stata / 第三方命令。
- `src/main/java/com/hexie/stata/HxWorkbench.java` 与 `hxworkbench.jar` 已同步重建；Java 11 / class major 55 编译检查通过，通用普通命令页与 `regress` 页的离线界面渲染 smoke test 通过。
- 本轮没有改变 DID、OneClick 等 HX Workflow 的业务逻辑。

### 2026-08-12 13:51（UTC+8）

**修改时间**：2026-08-12 13:51（UTC+8）

**修改内容**：

- 继续清理 `reghdfe`、`ppmlhdfe`、`ivregress` / `ivreghdfe` 一组常用估计命令的普通命令页与代码生成规则。
- 对 `reghdfe`、`ppmlhdfe`、`ivreghdfe` 增加最低命令契约：即使第三方命令尚未安装、当前机器暂时读取不到本地 help，也保留 `absorb()`、Robust、Cluster 等常用原命令入口；`ivreghdfe` 额外保留工具变量角色。
- `ivreghdfe` 的 Cluster 代码生成改为原命令兼容性更好的 `cluster(var)` 形式；其他使用 `vce(cluster var)` 的命令继续按各自原生语法生成。
- `hxresolve` 更新到 3.1.1，`hxpreview` 更新到 1.2.1。
- 本轮仍遵循“普通命令页只负责真实 Stata / 第三方命令；多步骤特调放 HX Workflow”的边界。

### 2026-08-12 13:45（UTC+8）

**修改时间**：2026-08-12 13:45（UTC+8）

**修改内容**：

- 继续按“一个普通命令页只展示该命令自己的参数”清理面板模型页面。
- `xtreg`、`xtlogit`、`xtprobit` 页面不再显示不会直接进入这些命令的“面板变量 / 时间变量”字段；面板结构改为先单独使用 Stata 官方 `xtset` 命令声明。
- 保留 `xtreg` 等命令自己的因变量、解释变量、模型类型、标准误、聚类、`if/in` 和更多 options。
- `ppmlhdfe` 在语义层明确保留 `absorb()`、VCE 和 Cluster 常用入口，即使命令尚未安装、自动解析信息不完整，也能优先生成常用参数页面。
- `hxsemantics` 更新到 1.3.1。

### 2026-08-12 13:37（UTC+8）

**修改时间**：2026-08-12 13:37（UTC+8）

**修改内容**：

- README 新增“上次修改时间”和累计“修改记录”，以后每次修改都在上一版记录基础上继续追加。
- 正式恢复并纳入当前 `hxworkbench.jar` 对应的 Java 源码基线：`src/main/java/com/hexie/stata/HxWorkbench.java`。
- 普通命令页开始落实“常用参数在前、低频参数在后”的统一设计原则。
- `regress` 页面已调整为优先显示 Y、核心 X、Controls 和标准误；`if/in`、分类变量、交互项、滞后项、权重、`noconstant`、`beta`、置信水平及其他低频 options 收入“更多设置”。
- 普通分析继续以 Stata 官方命令或成熟第三方命令为执行主体；HX 主要承担界面、解析、检查、调度、结果读取和 Workflow。
- 清理了部分与现成 Stata/第三方命令重复的旧 HX 实现，并继续将 DID、OneClick 等多步骤特调功能归入 HX Workflow。

</details>
