# hxempirical

**HX Empirical Workbench** 是一个面向 Stata 的可视化实证分析工作台，目标是把常见的经管实证操作从“记命令、查语法、反复改代码”变成“选择任务、设置参数、检查命令、直接运行”。

它适合希望降低 Stata 上手门槛，同时又需要保留完整代码、保证结果可复现的学生和研究者，尤其适合经济学、金融学、管理学等领域的课程论文、硕士论文和常规实证研究。

当前发布版本：**0.9.7**  
支持：**Stata 17 及以上版本**

## 它能做什么

hxempirical 在 Stata 内提供一个单窗口工作台。你可以从研究任务或命令出发，选择变量和参数，界面会同步生成完整的 Stata 命令。真正运行分析时，命令仍由 Stata 自身执行，并写入 Stata History，方便检查、复现和继续修改。

目前主要包括：

- **任务式入口**：可以按“普通线性回归”“固定效应”“工具变量”“DID”“数据处理”等研究任务寻找功能，也可以直接搜索 Stata 命令。
- **可视化回归设置**：通过界面选择因变量、核心解释变量、控制变量、固定效应、聚类标准误、权重、`if/in`、交互项、滞后项等。
- **实时命令预览**：界面底部始终显示将要提交给 Stata 的完整命令，可直接检查和修改。
- **回归后检验**：普通 OLS 可继续进行 VIF、异方差检验、RESET、信息准则、残差、Cook's distance、leverage、系数检验等常见 postestimation 操作。
- **数据查看与检查**：右侧可以查看当前 Stata 内存中的数据状态，并提供缺失值分析等工具；查看过程不会修改原始数据。
- **文件转换**：支持 Excel、CSV、TXT、TSV 转换为 `.dta`，提供预览、编码识别、批量转换和结果记录。
- **DID 分步构建**：帮助生成 `post`、`did`、事件时间变量、事件研究交互项和政策前联合检验，适合常见政策冲击研究流程。
- **图形工具**：提供分布图、变量关系图、分组趋势图、回归后图形以及 DID / event-study 相关图形入口。
- **OneClick 专区**：调用真实的外部 `oneclick` 命令，并把界面设置转换为对应的 Stata 命令；hxempirical 不自行替代其算法。
- **社区命令支持**：可检测并按需使用 `reghdfe`、`ppmlhdfe`、`ivreghdfe`、`winsor2`、`coefplot`、`event_plot` 等扩展命令。
- **运行监控**：记录命令、开始和结束时间、耗时、返回码、数据变化以及可获得的估计结果。
- **最近工作恢复**：保存最近的模型设置，重新打开后可以继续编辑，不会自动替你运行。

## 设计思路

hxempirical 的核心原则是：**让不会背 Stata 语法的人也能开始做实证，同时让熟悉 Stata 的人始终看得到真正执行的代码。**

因此，界面负责帮助你选择和组织参数，Stata 负责真正的数据处理、估计和绘图。生成的命令会进入 History，后续可以直接复制到 `.do` 文件中形成正式、可复现的研究代码。

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

可以先用 Stata 自带数据测试：

```stata
sysuse auto, clear
hxempirical
```

进入工作台后，可以搜索 `regress` 或选择普通线性回归，在界面中设置：

- Y：`price`
- X：`mpg`
- 控制变量：`weight`

界面会生成类似：

```stata
regress price mpg weight
```

确认后直接运行即可。

## 常用命令

查看版本和环境：

```stata
hxempirical about
```

检查可选扩展命令：

```stata
hxempirical doctor
```

安装指定扩展命令，例如：

```stata
hxempirical install reghdfe
```

打开经典 Stata 对话框界面：

```stata
hxempirical, classic
```

## 添加到 Stata 菜单

仅在当前 Stata 会话添加：

```stata
hxempirical menu
```

如果希望以后每次启动 Stata 都显示菜单入口：

```stata
hxempirical menu persist
```

移除该持久菜单：

```stata
hxempirical menu remove
```

菜单位置为：

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

如果当前 Stata 会话已经运行过 hxempirical，并在更新时出现 Java/JAR 文件正在使用、`r(602)` 等提示，请关闭 Stata，重新打开后先执行安装或更新命令。

## 卸载

如果曾启用持久菜单，建议先运行：

```stata
hxempirical menu remove
```

然后卸载：

```stata
ado uninstall hxempirical
```

卸载或更新后建议重新启动 Stata，以释放已经加载的 Java 类。

## 关于外部扩展命令

安装 hxempirical 本身不会自动下载所有社区命令。只有当某项功能真正需要外部命令时，工作台才会进行检测，并在有可靠安装来源的情况下提示安装。

例如：

- `reghdfe`
- `winsor2`
- `ivreghdfe`
- `ppmlhdfe`
- `oneclick`
- `oneclick_robustness`
- `coefplot`
- `event_plot`

其中 OneClick 功能调用作者真实的外部命令。控制变量组合仍应基于理论、文献和识别设计进行选择，工具本身不会替代研究设计。

## 兼容性

- Stata 17 或更高版本
- Windows / macOS 均按跨平台方式设计
- Java 工作台基于 Stata 自带 Java / SFI 接口
- 如果 Java 工作台无法启动，可以使用：

```stata
hxempirical, classic
```

打开随包提供的经典 Stata 界面。

## 当前定位

hxempirical 目前主要服务于经管实证研究中的高频操作，重点是：

1. 降低 Stata 命令使用门槛；
2. 把常见实证流程组织到统一界面；
3. 始终保留真实、完整、可复现的 Stata 命令；
4. 尽量减少在菜单、帮助文档、代码和数据窗口之间来回切换；
5. 让初学者可以直接开始，同时不给熟悉 Stata 的用户制造“黑箱”。

项目仍在持续完善中，后续会继续扩展常用实证命令、数据处理、诊断、绘图和论文工作流支持。
