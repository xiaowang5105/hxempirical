{smcl}
{title:我的实证工具箱}

{pstd}
工具箱按照“分析大类 -> 方法类别 -> 具体命令 -> 命令设置页面”组织。
每个页面说明命令用途、输入栏含义和最简单的正确示例，并实时显示最终
Stata 命令。

{title:命令页面}

{pstd}
默认进入“开始”页。主导航依次选择“类别 -> 方法 -> 命令”，命令页顶部
显示当前位置，例如“回归模型 -> 线性模型 -> regress”。每个命令最简单
的正确例子直接显示在标题下方，不需要先打开方法说明。

{pstd}
主要参数使用中文任务语言，同时保留 {cmd:absorb()}、{cmd:vce()}、
{cmd:if}、{cmd:in} 等 Stata 原词。较少使用的参数收在“更多设置”中。
选择聚类标准误后才显示聚类变量；{cmd:replace} 勾选样本条件后才显示
条件变量、关系和数值。

{title:统一解释流程}

{pstd}
系统读取命令实现、ado syntax、help Syntax、Options、Examples 和官方
dialog，依次经过 Syntax Parser、参数语义解释、使用场景理解、Command
Schema 和 GUI Renderer。信息有限时，能够可靠解释的参数正常显示，
少数不确定内容进入高级自定义区域。

{title:运行与 History}

{pstd}
{bf:运行并观察}执行预览中的原生 Stata 命令。Results 显示 Stata
原生结果，History 记录最终完整命令，工具箱保持打开。{bf:复制命令}
把当前完整命令复制到剪贴板。

{pstd}
命令设置区底部固定显示“即将执行的 Stata 命令”，运行时同步显示状态和
真实耗时。右侧“运行监控”记录开始/结束时间、return code、History 写入
状态、处理器、数据前后观测数和变量数，以及可读取的回归 N、R-squared。
详细区包含时间线和运行队列。普通回归使用不确定进度动画；批量转换按
已完成文件数显示真实百分比。

{title:数据观察区}

{pstd}
右侧直接显示当前 Stata 内存数据的只读表格，可以纵向、横向滚动。
点击任一变量后，下方显示变量名、标签、类型、缺失情况、数值摘要和
抽样分布图。点击列名也会选中该变量。尚未载入数据时，空状态页可以
直接载入 auto、选择自己的 DTA，或进入 Excel/CSV 转换。表格只负责
观察；正式修改仍由 Stata 命令完成。

{pstd}
{cmd:generate}会在运行前预演新变量，{cmd:replace}会显示真正改变的
观测数及“原值 -> 新值”，{cmd:merge}会模拟检查主副表键和匹配数量。
运行后显示观测数、变量数和抽样单元格的前后变化。新增变量使用绿色，
发生变化的抽样值使用黄色；{cmd:keep}、{cmd:drop}、{cmd:merge} 和
{cmd:append} 同时报告样本数及变量数变化。

{title:转换为 DTA}

{pstd}
在“数据 -> 导入与转换 -> 转换为 DTA”中选择 Excel、CSV、TXT 或 TSV。
页面会按文件格式显示需要的读取设置，并在右侧先展示数据、变量类型和
潜在问题。股票代码等包含前导零的列默认按字符串保护。单文件转换会在
覆盖已有 DTA 前询问；批量转换可选择文件类型、输出文件夹和跳过已有
文件。原始文件始终保持不变，实际执行的 {cmd:import} 与 {cmd:save}
命令进入 Stata History。

{title:工作台模式}

{pstd}
默认界面是一个 Java 单窗口工作台：左侧命令导航，中间动态命令设置，
右侧同步数据表、变量摘要、分布图和变化对比。打开工具箱后无需再打开
Data Browser。Stata Results 继续显示原生命令结果，History 继续记录最终
完整命令。

{pstd}
通过工具箱成功执行
{cmd:generate}、{cmd:replace}、{cmd:keep}、{cmd:drop}、{cmd:merge}、
{cmd:append}、{cmd:winsor2}、{cmd:reshape} 或 {cmd:collapse} 等操作后，
右侧表格和变化对比会自动刷新。大型数据的样本数和变量数按完整数据
报告，逐值高亮使用有上限的快照，避免占用过多内存。

{pstd}
如果 Java 组件不可用，启动器自动打开原有 Stata 对话框。也可以运行
{cmd:hxtoolbox, classic} 手动打开经典界面。

{title:前置检查}

{pstd}
{cmd:merge} 可在运行前检查主表和副表的关联键唯一性。面板命令显示
当前 {cmd:xtset} 状态；尚未设置时，可选择个体变量和时间变量并直接
执行 {cmd:xtset firm year}。

{title:示例符号}

{pstd}
示例统一使用 y（因变量）、x（主要解释变量）、c1 c2（其他解释变量）、
firm（企业）、year（年份）和 z（工具变量）。
