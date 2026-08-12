
{smcl}
{* *! hxselect 2.1.0  08aug2026}{...}
{title:显著控制变量组合筛选器}

{p 4 4 2}
{cmd:hxselect} 穷举候选控制变量子集，仅保留目标系数在所有模型中同时达到
显著性与方向要求的组合。最多支持4个模型。

{title:打开窗口}
{p 4 4 2}
菜单路径：{bf:用户 > 我的实证工具箱 > 回归分析 > 高级：显著控制变量组合}。
命令行也可输入 {cmd:hxselect}。

{title:命令模板}
{p 4 4 2}
每个模型是一条可执行的 Stata 命令，其中必须包含 {cmd:{c -(}controls{c )-}}
占位符。程序会把每一组候选控制变量替换到该位置。

{title:示例}
{phang2}{cmd:. sysuse auto, clear}{p_end}
{phang2}{cmd:. hxselect, candidates(weight length turn displacement foreign) ///}{p_end}
{phang2}{cmd:    model1(regress price mpg {c -(}controls{c )-}, vce(robust)) target1(mpg) ///}{p_end}
{phang2}{cmd:    model2(regress price mpg {c -(}controls{c )-}) target2(mpg) ///}{p_end}
{phang2}{cmd:    pmax(.10) saving(common_models.dta) replace best}{p_end}

{title:结果}
{p 4 4 2}
结果数据包含控制变量组合、各模型的目标系数、p值、拟合度以及全部模型中最大的p值。
组合按最大p值和控制变量数量排序。

{title:数据处理页}
{p 4 4 2}
该页用中文步骤调用 Stata 自带的 {cmd:generate}、{cmd:egen}、时间序列运算符
和 {cmd:merge}。变量只能点选，新变量名由用户填写。支持加减乘除、自然对数、
加1取对数、平方、平方根、绝对值、标准化、去均值、倒数、滞后、领先、
一阶差分、增长率和双侧缩尾。

{p 4 4 2}
数据合并区分别选择主表和副表，填写关联变量，并用中文选择 1:1、m:1 或 1:m。
程序会在执行前检查关联变量能否唯一识别记录；失败时恢复进入合并前的内存数据。

{title:操作记录}
{p 4 4 2}
官方 dialog 提交的命令会直接进入 Stata 左侧 History。自定义数据处理和性能包装器
使用 {cmd:window push} 写入最终的 {cmd:generate}、{cmd:replace}、{cmd:use}、
{cmd:merge}、{cmd:save} 和 {cmd:set processors #}。显著组合运行排名第一的模型时，
最终回归命令也会进入 History。可复跑命令同时追加到个人目录的
{cmd:hxselect_history.do}。

{title:多线程开关}
{p 4 4 2}
从 {bf:用户 > 我的实证工具箱 > 性能设置} 点击开启多线程、关闭多线程（单核）或
查看当前线程状态。开启时使用 {cmd:c(processors_lic)} 所允许的全部处理器；关闭时
执行 {cmd:set processors 1}。设置只影响当前 Stata 会话。

{title:计算规模}
{p 4 4 2}
K个候选变量产生最多 2^K-1 个非空组合。程序限制候选变量不超过15个，
并用 {cmd:maxruns()} 防止意外运行过多回归。

{title:研究提示}
{p 4 4 2}
组合搜索属于探索性分析，会放大选择后的显著性。正式报告应披露候选池、
搜索规则和全部模型，并使用理论预设、样本外验证或多重检验校正确认结果。
