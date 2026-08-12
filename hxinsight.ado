*! hxinsight 1.1.0  10aug2026
*! Beginner-facing intent, advantages, and limitations for toolbox commands.
program define hxinsight, rclass
    version 16.0
    syntax , COMMAND(name)

    local cmd = lower("`command'")
    local intent "执行 `cmd' 对应的数据处理或统计分析。"
    local advantages "使用 Stata 原生命令，过程可记录、可复查、可写入 do 文件复现。"
    local limitations "适用性取决于数据结构和模型假设；运行前请查看本命令 Help 与结果诊断。"

    if "`cmd'" == "generate" {
        local intent "根据现有变量或公式创建新变量，例如对数、比率、交互项。"
        local advantages "公式灵活，生成过程清楚，适合把论文中的变量构造完整记录下来。"
        local limitations "变量名不能重复；缺失值会随公式传播，取对数前还要检查零值和负值。"
    }
    else if "`cmd'" == "replace" {
        local intent "修改已有变量，可配合 if 只修改满足条件的样本。"
        local advantages "适合修正编码、处理异常值和按规则更新变量，条件控制直接。"
        local limitations "会覆盖原值；条件或公式写错会改变数据，操作前建议保留原变量或备份。"
    }
    else if inlist("`cmd'", "keep", "drop") {
        local intent "保留或删除指定变量与样本，整理出实际分析所需的数据。"
        local advantages "操作直接，能够快速缩小数据规模并统一论文样本范围。"
        local limitations "会从内存数据中移除内容；筛选条件应检查缺失值，操作前建议 preserve 或保存副本。"
    }
    else if "`cmd'" == "merge" {
        local intent "按企业、年份等关联键，把副表变量横向合并到当前主表。"
        local advantages "适合组合多个来源的数据，并用 _merge 清楚检查匹配结果。"
        local limitations "关联键必须符合 1:1、m:1 或 1:m 的唯一性；错误键会造成重复或错误匹配。"
    }
    else if "`cmd'" == "append" {
        local intent "把另一张表的观测追加到当前数据下方，常用于拼接年份或批次。"
        local advantages "适合快速形成多年或多地区的纵向总样本。"
        local limitations "同名变量的类型、单位和编码必须一致；不一致时可能出现缺失或含义混杂。"
    }
    else if "`cmd'" == "reshape" {
        local intent "在宽表和长表之间转换数据结构，使变量布局适合面板分析或展示。"
        local advantages "无需手工循环重排，能系统处理多个时期和多个变量前缀。"
        local limitations "i() 与 j() 的组合必须符合唯一性；错误前缀可能造成变量遗漏或转换失败。"
    }
    else if "`cmd'" == "collapse" {
        local intent "按企业、年份或地区聚合明细数据，生成均值、总和、中位数等组级统计。"
        local advantages "适合把交易级或个人级数据快速转换成论文分析层级。"
        local limitations "会用汇总数据替换当前数据；明细信息无法直接恢复，必须提前 preserve 或保存副本。"
    }
    else if "`cmd'" == "xtset" {
        local intent "声明面板个体与时间变量，为滞后项和面板模型建立数据结构。"
        local advantages "Stata 可以检查重复的个体—时间组合，并启用 xtreg、L.、F. 等功能。"
        local limitations "要求个体—时间键设置正确；xtset 只声明结构，不会自动解决缺期或因果识别问题。"
    }
    else if "`cmd'" == "winsor2" {
        local intent "把分布两端的极端值压到指定分位点，降低异常值对结果的影响。"
        local advantages "操作简单，常用于检验回归结果是否被少量极端观测主导。"
        local limitations "分位点选择带有主观性，也可能压掉真实的重要差异；应报告阈值并做敏感性检验。"
    }
    else if "`cmd'" == "duplicates" {
        local intent "识别或处理重复记录，检查企业—年份等键是否唯一。"
        local advantages "能够快速发现合并、面板设置和数据录入中的重复问题。"
        local limitations "相同记录有时具有真实含义；删除前必须确认重复的业务含义和识别键。"
    }
    else if "`cmd'" == "misstable" {
        local intent "汇总变量缺失情况，定位缺失较多的指标和样本。"
        local advantages "能在分析前快速完成缺失值概览和数据质量检查。"
        local limitations "只描述缺失情况；还需判断缺失机制以及删除、插补是否会带来选择偏差。"
    }
    else if inlist("`cmd'", "encode", "decode", "destring", "tostring") {
        local intent "在字符串与数值类型之间转换变量，使类别编码、合并键或计算格式符合后续分析要求。"
        local advantages "保留明确的转换命令，便于统一不同来源数据的变量类型。"
        local limitations "编码顺序、前导零、非数字字符和值标签可能改变变量含义，转换后必须核对。"
    }
    else if "`cmd'" == "summarize" {
        local intent "查看样本数、均值、标准差、最小值和最大值等基本统计量。"
        local advantages "速度快，适合分析前检查变量范围、量纲和明显异常。"
        local limitations "提供的是总体概览；均值会受极端值影响，也不能说明变量关系或因果效应。"
    }
    else if "`cmd'" == "tabstat" {
        local intent "自定义描述统计指标，并可按组比较均值、中位数等特征。"
        local advantages "指标和分组方式灵活，适合制作论文描述统计表。"
        local limitations "结果仍是描述性的；组间差异是否显著需要另做统计检验。"
    }
    else if inlist("`cmd'", "correlate", "pwcorr") {
        local intent "衡量变量之间的线性相关程度，初步检查方向和共线性风险。"
        local advantages "计算直观，pwcorr 还能显示显著性和成对有效样本。"
        local limitations "相关不代表因果；非线性关系可能被忽略，pwcorr 各系数使用的样本还可能不同。"
    }
    else if "`cmd'" == "ttest" {
        local intent "检验一个均值是否等于指定值，或两个组的均值是否存在差异。"
        local advantages "结论直观，适合平衡性、分组差异和简单假设检验。"
        local limitations "依赖独立性和方差等条件；没有控制其他因素，观察到的差异不等于因果效应。"
    }
    else if "`cmd'" == "tabulate" {
        local intent "统计类别变量频数，或查看两个类别变量的交叉分布。"
        local advantages "适合检查编码、样本构成和类别之间的原始关系。"
        local limitations "稀疏单元会使比例不稳定；列联关系没有控制混杂因素。"
    }
    else if "`cmd'" == "regress" {
        local intent "用普通最小二乘估计 y 与 x、控制变量之间的线性关系。"
        local advantages "系数容易解释，估计和诊断体系成熟，可使用稳健或聚类标准误。"
        local limitations "因果解释需要外生性；线性设定、遗漏变量、异常值和错误标准误都会影响结论。"
    }
    else if "`cmd'" == "areg" {
        local intent "在线性回归中吸收一个类别固定效应，例如企业固定效应。"
        local advantages "比手工加入大量虚拟变量简洁高效，适合单维固定效应。"
        local limitations "只能直接吸收一组固定效应；该组内不变化变量的系数无法估计。"
    }
    else if "`cmd'" == "reghdfe" {
        local intent "估计线性关系，同时吸收企业、年份等多个高维固定效应。"
        local advantages "适合大规模面板数据，能高效控制多维不随组内变化的遗漏因素。"
        local limitations "系数依赖组内变动；时间不变变量会被吸收，单例样本和固定效应设定也会改变样本。"
    }
    else if "`cmd'" == "qreg" {
        local intent "估计 x 对 y 的中位数或其他条件分位点的影响。"
        local advantages "可以揭示分布不同位置的异质性，对均值和极端结果的依赖较小。"
        local limitations "系数解释为条件分位数效应；标准误计算和固定效应处理比 OLS 更复杂。"
    }
    else if "`cmd'" == "xtreg" {
        local intent "分析重复观察的面板数据，并选择固定效应、随机效应或组间模型。"
        local advantages "FE 可控制个体长期不变的不可观测差异；RE 在其假设成立时利用更多变动、更有效率。"
        local limitations "FE 不能估计个体内不变化变量；RE 要求个体效应与解释变量不相关，并需正确 xtset。"
    }
    else if "`cmd'" == "xtlogit" {
        local intent "分析面板数据中的 0/1 结果，并控制个体层面的重复观察。"
        local advantages "适合企业或个人多期二元结果；FE 可处理部分时间不变个体异质性。"
        local limitations "FE 会丢掉结果始终为 0 或 1 的个体；系数是对数胜算，通常还需 margins 解释。"
    }
    else if "`cmd'" == "xtprobit" {
        local intent "使用 Probit 链接分析面板数据中的 0/1 结果。"
        local advantages "提供潜变量正态分布框架，可结合随机效应或总体平均模型。"
        local limitations "常用 RE 设定要求个体效应与解释变量关系正确；系数需通过 margins 转成概率变化。"
    }
    else if inlist("`cmd'", "logit", "probit") {
        local intent "估计二元结果发生的概率，适用于因变量只有 0 和 1 的情形。"
        local advantages "预测概率限定在 0—1；可用 margins 给出更直观的边际效应。"
        local limitations "系数不能直接当作概率变化；遗漏变量、内生性和链接函数设定会影响解释。"
    }
    else if "`cmd'" == "poisson" {
        local intent "解释非负计数结果，例如专利数、事件次数或交易笔数。"
        local advantages "保证预测值非负；配合稳健标准误时对条件均值的分布假设较宽松。"
        local limitations "应检查过度离散、零值结构和函数形式；系数通常按比例变化解释。"
    }
    else if "`cmd'" == "nbreg" {
        local intent "分析方差明显大于均值的计数型因变量。"
        local advantages "相较 Poisson 允许额外离散，常能更好拟合过度离散的计数数据。"
        local limitations "依赖负二项分布设定；大量结构性零值仍可能需要其他模型。"
    }
    else if "`cmd'" == "ppmlhdfe" {
        local intent "用 PPML 估计非负结果，同时吸收多个高维固定效应。"
        local advantages "保留零值，对异方差较稳健，特别适合贸易流量和乘法模型。"
        local limitations "可能出现分离或不收敛；系数按比例解释，固定效应和样本剔除情况必须检查。"
    }
    else if "`cmd'" == "ivregress" {
        local intent "用工具变量处理解释变量内生性，估计 2SLS、LIML 或 GMM 模型。"
        local advantages "当工具变量有效时，可缓解反向因果、测量误差和遗漏变量造成的内生性。"
        local limitations "工具变量必须相关且满足排除限制；弱工具变量会产生严重偏误，需报告第一阶段诊断。"
    }
    else if "`cmd'" == "ivreghdfe" {
        local intent "在工具变量估计中同时吸收企业、年份等高维固定效应。"
        local advantages "能够同时处理多维固定效应和解释变量内生性。"
        local limitations "仍依赖有效且足够强的工具变量；识别来自固定效应内变动，样本和诊断需仔细核对。"
    }
    else if "`cmd'" == "test" {
        local intent "在模型估计后检验单个或多个系数限制是否成立。"
        local advantages "能够进行联合显著性和系数相等检验，并使用当前模型的协方差矩阵。"
        local limitations "结论依赖上一项模型和标准误设定；大量重复检验还会增加偶然显著风险。"
    }
    else if "`cmd'" == "lincom" {
        local intent "计算回归系数的线性和、差或其他线性组合，并给出统计推断。"
        local advantages "自动利用系数协方差，适合交互项和组合效应的解释。"
        local limitations "只能直接处理线性组合；结果仍取决于上一项模型的正确设定。"
    }
    else if "`cmd'" == "predict" {
        local intent "根据上一项模型生成预测值、残差或其他诊断变量。"
        local advantages "便于模型诊断、绘图、异常观测检查和后续计算。"
        local limitations "样本内拟合不代表样本外预测能力，预测结果也不自动具有因果含义。"
    }
    else if "`cmd'" == "margins" {
        local intent "把回归结果转换为预测概率、边际效应或指定取值下的预测结果。"
        local advantages "特别适合解释 Logit、Probit 和交互项，比原始系数更直观。"
        local limitations "结果依赖模型设定、at() 取值和平均方式；复杂非线性模型需要明确说明计算口径。"
    }
    else if inlist("`cmd'", "histogram", "kdensity", "graph_box") {
        local intent "观察单个变量的分布形状、集中位置、尾部和潜在异常值。"
        local advantages "可以在回归前直观看到偏态、多峰、长尾和极端值，帮助判断是否需要变换或进一步检查。"
        local limitations "图形主要用于描述和诊断；分箱宽度、核带宽和分组方式会改变视觉结果，不能据此单独作因果判断。"
    }
    else if inlist("`cmd'", "scatter", "lfit", "twoway") {
        local intent "观察两个变量之间的原始关系，并按需要叠加线性拟合或其他图层。"
        local advantages "能快速识别方向、非线性、离群点和组间差异，也便于核对回归设定是否贴合数据。"
        local limitations "散点关系会受混杂因素、尺度和样本重叠影响；拟合线表示条件相关，不能自动解释为因果效应。"
    }
    else if inlist("`cmd'", "marginsplot", "coefplot", "event_plot", "did_trends") {
        local intent "把模型估计结果、边际效应或处理组与对照组的动态变化转成便于比较的图形。"
        local advantages "可以同时呈现点估计与不确定性，适合论文中的系数比较、异质性展示和平行趋势检查。"
        local limitations "图形质量取决于前一步模型与置信区间设定；事件研究图还要核对基准期、样本构成和预趋势检验。"
    }
    else if inlist("`cmd'", "oneclick", "oneclick_robustness") {
        local intent "系统遍历有理论依据的候选控制变量组合，观察核心系数对模型设定的敏感程度。"
        local advantages "可以完整保留各组合的系数、标准误、显著性和样本变化，帮助识别结论是否依赖某一组控制变量。"
        local limitations "组合数量会指数增长；候选变量必须由理论和研究设计确定，筛选结果只能作为敏感性与稳健性证据，不能替代识别策略。"
    }

    local recommended "已经载入 Stata、变量类型符合命令要求，并完成基本质量检查的数据。"
    if inlist("`cmd'", "generate", "replace", "keep", "drop") {
        local recommended "横截面、时间序列或面板数据都可；变量名称、类型、缺失值和筛选条件应当明确。"
    }
    else if "`cmd'" == "merge" {
        local recommended "拥有共同关联键的主表和副表，例如企业代码 firm 与年份 year，并能验证键的唯一性。"
    }
    else if "`cmd'" == "append" {
        local recommended "不同年份、地区或批次且字段结构相同或能够统一的多张数据表。"
    }
    else if "`cmd'" == "reshape" {
        local recommended "宽表中含有规则变量前缀，或长表中个体—维度组合唯一的数据。"
    }
    else if "`cmd'" == "collapse" {
        local recommended "明细层级观测较多、拥有清晰分组变量，并计划转换到企业或地区层级的数据。"
    }
    else if "`cmd'" == "xtset" {
        local recommended "长表形式的面板数据：同一个 firm 或个人在多个 year 被重复观察。"
    }
    else if "`cmd'" == "winsor2" {
        local recommended "包含连续型财务或经济指标、样本量较充足，并确实存在极端值影响的数据。"
    }
    else if "`cmd'" == "duplicates" {
        local recommended "需要检查企业—年份、个人—月份等识别键唯一性的任何微观或面板数据。"
    }
    else if "`cmd'" == "misstable" {
        local recommended "任何可能存在缺失值的数据，特别是合并后或正式回归前的数据。"
    }
    else if inlist("`cmd'", "encode", "decode", "destring", "tostring") {
        local recommended "变量类型与后续命令不一致的数据；转换前应检查值标签、非数字字符和前导零。"
    }
    else if inlist("`cmd'", "summarize", "tabstat") {
        local recommended "含有连续或数值型变量的横截面、时间序列或面板数据；tabstat 还适合带分组变量的数据。"
    }
    else if inlist("`cmd'", "correlate", "pwcorr") {
        local recommended "至少包含两个数值型变量，并关注近似线性关系的数据；需留意缺失值导致的样本变化。"
    }
    else if "`cmd'" == "ttest" {
        local recommended "连续型结果变量，以及一个比较值、两个独立组，或同一对象的成对观测数据。"
    }
    else if "`cmd'" == "tabulate" {
        local recommended "包含类别型、等级型或离散编码变量的数据，且各类别应有足够观测。"
    }
    else if "`cmd'" == "regress" {
        local recommended "因变量近似连续、解释关系可合理写成线性形式的横截面或合并数据。"
    }
    else if "`cmd'" == "areg" {
        local recommended "连续因变量并需要控制一组高类别固定效应的数据，例如企业或地区固定效应。"
    }
    else if "`cmd'" == "reghdfe" {
        local recommended "企业—年份等长表面板或重复观测数据，包含多组固定效应且核心变量具有组内变动。"
    }
    else if "`cmd'" == "qreg" {
        local recommended "连续型因变量，关注低位、中位或高位异质性，或分布偏斜、极端值较明显的数据。"
    }
    else if "`cmd'" == "xtreg" {
        local recommended "已正确 xtset 的长表面板数据，因变量近似连续，个体在多个时期重复出现。"
    }
    else if inlist("`cmd'", "xtlogit", "xtprobit") {
        local recommended "已正确 xtset 的长表面板数据，因变量为 0/1，个体具有多期观测和结果变动。"
    }
    else if inlist("`cmd'", "logit", "probit") {
        local recommended "因变量为 0/1 的横截面或适当处理相关性的合并数据，并且两类结果都有足够样本。"
    }
    else if "`cmd'" == "poisson" {
        local recommended "因变量是非负整数计数的数据，例如专利数、事件数或交易次数。"
    }
    else if "`cmd'" == "nbreg" {
        local recommended "非负整数计数数据，并且条件方差明显大于均值、存在过度离散。"
    }
    else if "`cmd'" == "ppmlhdfe" {
        local recommended "含大量零值的非负流量或规模数据，并需要控制企业、年份等多维固定效应。"
    }
    else if "`cmd'" == "ivregress" {
        local recommended "存在潜在内生解释变量 x，并拥有与 x 相关、满足排除限制的有效工具变量 z。"
    }
    else if "`cmd'" == "ivreghdfe" {
        local recommended "面板或重复观测数据，既有有效工具变量，又需要吸收企业、年份等多维固定效应。"
    }
    else if inlist("`cmd'", "test", "lincom", "predict", "margins") {
        local recommended "刚刚完成与该后估计命令兼容的回归，并保留上一项模型 e() 结果的数据与会话。"
    }
    else if inlist("`cmd'", "histogram", "kdensity", "graph_box") {
        local recommended "包含数值型连续或有序变量的数据；箱线图分组时还需要一个类别变量，并保证各组有足够观测。"
    }
    else if inlist("`cmd'", "scatter", "lfit", "twoway") {
        local recommended "至少包含两个数值型变量的数据；样本很多时可先检查重叠、异常值并考虑透明度或分组绘图。"
    }
    else if inlist("`cmd'", "marginsplot", "coefplot", "event_plot") {
        local recommended "已经完成相应回归、margins 或事件研究估计，并在当前会话保留可供绘图读取的估计结果。"
    }
    else if "`cmd'" == "did_trends" {
        local recommended "包含结果变量、时间变量和 0/1 处理组变量的重复截面或面板数据，处理前后时期应覆盖充分。"
    }
    else if inlist("`cmd'", "oneclick", "oneclick_robustness") {
        local recommended "已完成基础清洗的横截面或面板数据；核心解释变量明确，候选控制变量来自理论、文献和预先确定的研究设计。"
    }

    char _dta[hxtoolbox_insight_command] "`cmd'"
    char _dta[hxtoolbox_insight_intent] `"主要意图：`intent'"'
    char _dta[hxtoolbox_insight_data] `"推荐数据：`recommended'"'
    char _dta[hxtoolbox_insight_advantages] `"优点：`advantages'"'
    char _dta[hxtoolbox_insight_limitations] `"缺点与注意：`limitations'"'

    return local command "`cmd'"
    return local intent `"`intent'"'
    return local recommended `"`recommended'"'
    return local advantages `"`advantages'"'
    return local limitations `"`limitations'"'
end
