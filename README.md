# hxempirical

**HX Empirical Workbench** 是一个面向 Stata 的可视化实证分析工作台。它把常见的经管实证操作组织成可点击、可选择、可预览代码的工作界面，同时保留完整的 Stata 命令，方便复现、检查和继续修改。

它主要面向经济学、金融学、管理学等领域的课程论文、硕士论文和常规实证研究，也适合希望降低 Stata 上手门槛、同时保留正式代码工作流的用户。

当前发布版本：**1.0.2**  
支持：**Stata 17 及以上版本**  
上次修改时间：**2026-08-12 16:31（UTC+8）**

## 版本记录

### 1.0.2（当前版本）

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

#### 1.0.0 开发过程记录

#### 2026-08-12 15:08（UTC+8）

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

#### 2026-08-12 14:28（UTC+8）

**修改时间**：2026-08-12 14:28（UTC+8）

**修改内容**：

- 继续清理 `reghdfe`、`ppmlhdfe`、`ivregress`、`ivreghdfe`、`xtreg` 这组常用估计命令的普通命令页，统一“核心模型参数 → 标准误 → 更多设置”的层级。
- IV 页面把内生变量与工具变量提升到主要参数区；`ivregress` 的估计方法紧随核心变量设置，`ivreghdfe` 的固定效应与 VCE 继续保留在主页面。
- 面板命令开始使用显式语义默认值：`xtreg`、`xtlogit`、`xtprobit` 默认选择随机效应（RE），同时仍可在页面切换其他可用模型。
- 未安装 `reghdfe`、`ppmlhdfe`、`ivreghdfe` 时，最低命令契约仍保留因变量、解释变量、`if/in`、权重、`absorb()`、VCE 和 Cluster 等原生命令入口。
- 权重类型按命令收窄：`reghdfe` 提供 `fweight/aweight/pweight`，`ppmlhdfe` 提供 `fweight/pweight`，`ivreghdfe` 保留四类权重；避免界面生成命令本身不接受的权重类型。
- 对这组重点估计命令增加运行前结构检查：IV 角色重复或缺失、Cluster 变量缺失、权重变量缺失时先提示，不提交明显不完整的命令。
- `hxsemantics` 更新到 1.3.2，`hxresolve` 更新到 3.1.2；Java 工作台与 `hxworkbench.jar` 同步重建并通过编译和离线界面 smoke test。

#### 2026-08-12 14:20（UTC+8）

**修改时间**：2026-08-12 14:20（UTC+8）

**修改内容**：

- 开始把普通命令的通用 Java 页面统一调整为“常用参数在前、低频参数放入更多设置”。
- 通用普通命令页中的 `if`、`in` 不再直接铺在主页面，统一收入“更多设置”；主页面继续保留该命令自身的因变量、解释变量、模型类型、`absorb()`、工具变量、标准误和按需显示的 Cluster 等常用字段。
- 为通用普通命令页补上结构化权重设置：支持 `fweight`、`aweight`、`pweight`、`iweight` 和权重变量，并继续生成真实 Stata `[weight=var]` 语法。
- “更多设置”现在统一容纳 `if`、`in`、权重和其他低频 Stata options；普通命令最终仍由 `hxpreview` 生成并执行真实 Stata / 第三方命令。
- `src/main/java/com/hexie/stata/HxWorkbench.java` 与 `hxworkbench.jar` 已同步重建；Java 11 / class major 55 编译检查通过，通用普通命令页与 `regress` 页的离线界面渲染 smoke test 通过。
- 本轮没有改变 DID、OneClick 等 HX Workflow 的业务逻辑。

#### 2026-08-12 13:51（UTC+8）

**修改时间**：2026-08-12 13:51（UTC+8）

**修改内容**：

- 继续清理 `reghdfe`、`ppmlhdfe`、`ivregress` / `ivreghdfe` 一组常用估计命令的普通命令页与代码生成规则。
- 对 `reghdfe`、`ppmlhdfe`、`ivreghdfe` 增加最低命令契约：即使第三方命令尚未安装、当前机器暂时读取不到本地 help，也保留 `absorb()`、Robust、Cluster 等常用原命令入口；`ivreghdfe` 额外保留工具变量角色。
- `ivreghdfe` 的 Cluster 代码生成改为原命令兼容性更好的 `cluster(var)` 形式；其他使用 `vce(cluster var)` 的命令继续按各自原生语法生成。
- `hxresolve` 更新到 3.1.1，`hxpreview` 更新到 1.2.1。
- 本轮仍遵循“普通命令页只负责真实 Stata / 第三方命令；多步骤特调放 HX Workflow”的边界。

#### 2026-08-12 13:45（UTC+8）

**修改时间**：2026-08-12 13:45（UTC+8）

**修改内容**：

- 继续按“一个普通命令页只展示该命令自己的参数”清理面板模型页面。
- `xtreg`、`xtlogit`、`xtprobit` 页面不再显示不会直接进入这些命令的“面板变量 / 时间变量”字段；面板结构改为先单独使用 Stata 官方 `xtset` 命令声明。
- 保留 `xtreg` 等命令自己的因变量、解释变量、模型类型、标准误、聚类、`if/in` 和更多 options。
- `ppmlhdfe` 在语义层明确保留 `absorb()`、VCE 和 Cluster 常用入口，即使命令尚未安装、自动解析信息不完整，也能优先生成常用参数页面。
- `hxsemantics` 更新到 1.3.1。

#### 2026-08-12 13:37（UTC+8）

**修改时间**：2026-08-12 13:37（UTC+8）

**修改内容**：

- README 新增“上次修改时间”和累计“修改记录”，以后每次修改都在上一版记录基础上继续追加。
- 正式恢复并纳入当前 `hxworkbench.jar` 对应的 Java 源码基线：`src/main/java/com/hexie/stata/HxWorkbench.java`。
- 普通命令页开始落实“常用参数在前、低频参数在后”的统一设计原则。
- `regress` 页面已调整为优先显示 Y、核心 X、Controls 和标准误；`if/in`、分类变量、交互项、滞后项、权重、`noconstant`、`beta`、置信水平及其他低频 options 收入“更多设置”。
- 普通分析继续以 Stata 官方命令或成熟第三方命令为执行主体；HX 主要承担界面、解析、检查、调度、结果读取和 Workflow。
- 清理了部分与现成 Stata/第三方命令重复的旧 HX 实现，并继续将 DID、OneClick 等多步骤特调功能归入 HX Workflow。

## 核心结构

hxempirical 目前按两类功能组织：

### 1. 普通命令

普通功能优先调用 **Stata 官方命令** 或 **成熟的第三方命令**。

例如：

- 普通线性回归：`regress`
- 面板模型：`xtreg`
- 高维固定效应：`reghdfe`
- PPML 高维固定效应：`ppmlhdfe`
- 工具变量：`ivregress`、`ivreghdfe`
- 缩尾：`winsor2`
- 系数图：`coefplot`
- 描述统计：`summarize`、`tabstat`
- 数据合并：`merge`、`append`
- 数据结构转换：`reshape`、`collapse`

HX 在这一层负责命令查找、中文说明、参数界面、变量选择、代码生成、运行前检查、History 记录、运行监控和结果展示。最终提交给 Stata 的仍是对应的真实命令。

每个普通命令页按使用频率组织参数：**常用参数直接显示，低频参数放到“更多设置”或高级选项中**。后台检查只在发现问题时提示，例如命令尚未安装、变量不存在、面板尚未 `xtset`、聚类变量无效等。

### 2. HX 专区 / Workflow

专区用于组织一个完整的实证任务。一个 Workflow 可以连续调用多个 Stata 官方命令、第三方命令和少量 HX 辅助逻辑，把多个步骤串成一套可执行流程。

目前包括：

- **DID 专区**：围绕 DID 变量准备、事件时间、事件研究、政策前联合检验和动态图等步骤组织流程。
- **OneClick 专区**：调用作者发布的真实外部 `oneclick` / `oneclick_robustness` 命令，并负责参数组织、运行隔离和结果读取。

后续的机制分析、稳健性分析、异质性分析等完整研究任务也可以继续按 Workflow 方式扩展。

## 它能做什么

hxempirical 在 Stata 内提供单窗口工作台。你可以从研究任务或命令出发，选择变量和参数，界面同步生成完整 Stata 命令。运行时由 Stata 执行该命令，并写入 Stata History。

目前主要包括：

- **任务式入口与命令搜索**：按普通线性回归、固定效应、工具变量、数据处理等任务寻找命令，也可以直接搜索 Stata 命令名。
- **可视化参数设置**：通过界面选择因变量、解释变量、控制变量、固定效应、聚类标准误、权重、`if/in` 等参数。
- **实时命令预览**：界面底部始终显示最终将提交给 Stata 的完整命令，并允许运行前检查和修改。
- **回归后检验**：支持常见 postestimation 命令，例如 VIF、异方差检验、RESET、信息准则、残差、Cook's distance、leverage 和系数检验。
- **数据查看与检查**：读取当前 Stata 内存中的数据状态，并提供变量、缺失值和数据结构相关入口。
- **文件转换 Workflow**：支持 Excel、CSV、TXT、TSV 转换为 `.dta`，包含预览、编码识别、批量转换和结果记录。
- **DID Workflow**：组织常见 DID / event-study 研究步骤。
- **图形命令**：提供分布图、变量关系图、回归结果图以及 DID / event-study 图形入口。
- **OneClick Workflow**：调用真实外部命令并读取其输出。
- **社区命令支持**：检测并按需使用 `reghdfe`、`ppmlhdfe`、`ivreghdfe`、`winsor2`、`coefplot`、`event_plot` 等扩展命令。
- **运行监控**：记录命令、开始和结束时间、耗时、返回码、数据变化以及可获得的估计结果。
- **最近工作恢复**：保存最近使用的模型设置，便于重新打开后继续编辑。

## 设计原则

hxempirical 的目标是让用户更容易使用 Stata，同时始终保留真实、完整、可复现的代码。

普通命令遵循以下原则：

1. **已有 Stata 官方命令时，直接调用官方命令。**
2. **已有成熟第三方实现时，调用原作者发布的命令。**
3. **常用参数放前面，低频参数放后面。**
4. **界面实时生成最终 Stata 命令。**
5. **运行前检查在后台完成，有异常时再提示用户。**
6. **统计估计和数据处理尽量交给实际 Stata 命令执行。**
7. **HX 自定义逻辑主要用于 GUI、解析、检查、调度、结果读取和 Workflow。**

因此，用户可以把工作台生成的命令直接复制进 `.do` 文件，形成正式的研究代码。

## 一行安装

在 Stata 命令窗口运行：

```stata
net install hxempirical, from("https://xiaowang5105.github.io/hxempirical/") replace force
```

安装完成后启动：

```stata
hxempirical
```

## 最简单的使用方式

可以先使用 Stata 自带数据测试：

```stata
sysuse auto, clear
hxempirical
```

进入工作台后搜索 `regress`，或者进入普通线性回归页面，设置：

- Y：`price`
- X：`mpg`
- 控制变量：`weight`

界面会生成：

```stata
regress price mpg weight
```

确认后直接运行。

## 第三方命令

安装 hxempirical 本身不会一次性下载全部社区命令。进入相关功能时，工作台会检查命令是否已经安装；对于已经配置可靠来源的命令，可以按需安装。

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

OneClick 专区执行作者发布的真实外部命令。候选控制变量仍应根据理论、文献和识别设计确定。

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

菜单位置：

**用户（User） > 我的实证工具箱**

## 更新或重新安装

可以重新运行安装命令：

```stata
net install hxempirical, from("https://xiaowang5105.github.io/hxempirical/") replace force
```

也可以运行：

```stata
hxempirical update
```

如果当前 Stata 会话已经加载过 hxempirical，并在更新时出现 Java/JAR 文件正在使用、`r(602)` 等提示，请关闭 Stata，重新打开后先执行安装或更新命令。

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
- Java 工作台无法启动时，可以使用：

```stata
hxempirical, classic
```

打开随包提供的经典 Stata 界面。

## 当前开发方向

当前重构重点是：

1. 普通功能统一回到真实 Stata 官方命令或第三方命令；
2. 清理历史版本中与现成命令重复的 HX 实现；
3. 普通命令页统一采用“常用参数 → 更多设置 → 最终命令”的结构；
4. 将多步骤特调功能统一收归 HX Workflow；
5. 保留命令解析、自动页面生成、运行监控和 History 等工作台基础能力；
6. 持续扩展经管实证研究常用命令与 Workflow。
