from pathlib import Path

root = Path(__file__).resolve().parents[1]
sem_path = root / "hxsemantics.ado"
java_path = root / "src/main/java/com/hexie/stata/HxWorkbench.java"
sem = sem_path.read_text(encoding="utf-8")
java = java_path.read_text(encoding="utf-8")

semantic_block = r'''
    /* Family-level copy for catalog commands that rely on the generic syntax parser.
       Keep the parsed Stata syntax/flags unchanged; only improve beginner-facing semantics. */
    if strpos(" table prtest sdtest oneway anova ranksum median signrank signtest ", " `cmd' ") {
        local title "`cmd' — 表格与假设检验"
        local purpose1 "用于描述分组结果或执行常见参数/非参数假设检验。"
        local purpose2 "先按页面填写检验对象和分组信息；方向、显著性和其他 Stata 选项放在最后检查。"
    }
    else if strpos(" iqreg bsqreg sureg mvreg ", " `cmd' ") {
        local title "`cmd' — 线性与多方程模型"
        local purpose1 "用于分位数估计、稳健分位数推断或多个线性方程的联合估计。"
        local purpose2 "先区分结果变量与解释变量；命令特有设定继续以 Stata 当前语法和 options 为准。"
    }
    else if strpos(" logistic hetprobit scobit cloglog ", " `cmd' ") {
        local title "`cmd' — 二元结果模型"
        local purpose1 "用于因变量只有两类结果时的概率模型估计。"
        local purpose2 "先选择二元因变量和解释变量；链接函数、异方差或显示方式等命令特有设置放在最后。"
    }
    else if strpos(" ologit oprobit ", " `cmd' ") {
        local title "`cmd' — 序数结果模型"
        local purpose1 "用于因变量具有明确等级顺序的离散选择模型。"
        local purpose2 "先选择序数因变量和解释变量；阈值与其他模型选项由 Stata 按当前命令处理。"
    }
    else if strpos(" mlogit mprobit asclogit asmprobit ", " `cmd' ") {
        local title "`cmd' — 多类别选择模型"
        local purpose1 "用于无序多类别结果或备选项层面的离散选择问题。"
        local purpose2 "先明确结果/选择变量和解释变量；基准类别、备选项结构等设置在运行前按 Stata 语法核对。"
    }
    else if strpos(" zip zinb tpoisson tnbreg ", " `cmd' ") {
        local title "`cmd' — 扩展计数结果模型"
        local purpose1 "用于零膨胀、截断或过度离散等特殊计数数据。"
        local purpose2 "先选择计数因变量和解释变量；inflate()、截断点等命令特有参数放在最后设置。"
    }
    else if strpos(" fracreg betareg glm ", " `cmd' ") {
        local title "`cmd' — 分数结果与广义线性模型"
        local purpose1 "用于比例/分数型因变量或需要自定义分布与链接函数的广义线性模型。"
        local purpose2 "先设置因变量和解释变量；family()、link() 等分布与链接设置按当前命令填写。"
    }
    else if strpos(" heckman heckprobit heckoprobit heckpoisson ", " `cmd' ") {
        local title "`cmd' — 样本选择模型"
        local purpose1 "用于处理样本进入观察过程可能非随机所产生的选择问题。"
        local purpose2 "结果方程与选择方程需要按命令语法分别确认；复杂方程选项保留在原生 Stata options 中。"
    }
    else if strpos(" arima arch ucm ", " `cmd' ") {
        local title "`cmd' — 单变量时间序列模型"
        local purpose1 "用于 ARIMA、ARCH/GARCH 或不可观测成分等时间序列建模。"
        local purpose2 "运行前应先确认时间变量和 tsset；滞后阶数、波动方程或状态成分按 Stata 语法设置。"
    }
    else if strpos(" dfuller pperron corrgram pergram ", " `cmd' ") {
        local title "`cmd' — 时间序列诊断与检验"
        local purpose1 "用于单位根、相关结构或周期特征等时间序列诊断。"
        local purpose2 "先确认时间序列已正确声明；滞后阶数、趋势项和检验选项在最后核对。"
    }
    else if strpos(" var svar vec varsoc vargranger varstable irf ", " `cmd' ") {
        local title "`cmd' — 多变量时间序列"
        local purpose1 "用于 VAR/SVAR/VEC、滞后阶数选择、Granger 检验、稳定性或脉冲响应分析。"
        local purpose2 "先确认系统变量与时间结构；识别限制、滞后阶数和结果对象等参数按当前命令设置。"
    }
    else if strpos(" spregress spivregress spxtregress ", " `cmd' ") {
        local title "`cmd' — 空间回归模型"
        local purpose1 "用于结果变量受到空间相关、空间滞后或空间内生性影响的模型。"
        local purpose2 "运行前应先准备 Stata 空间数据与权重矩阵；空间权重和模型类型按命令语法填写。"
    }
    else if strpos(" xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtabond xtdpdsys ", " `cmd' ") {
        local title "`cmd' — 面板数据模型"
        local purpose1 "用于面板数据下的计数、受限因变量、GEE、前沿或动态面板模型。"
        local purpose2 "页面会要求面板结构；模型、动态项和估计选项继续按 Stata 当前命令语法确认。"
        local panel_label "个体 / 面板变量"
        local time_label "时间变量（可按数据结构留空）"
    }
    else if strpos(" mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm ", " `cmd' ") {
        local title "`cmd' — 多层混合效应模型"
        local purpose1 "用于观测嵌套在个体、学校、地区等层级结构中的混合效应模型。"
        local purpose2 "固定部分与随机部分应按层级结构填写；随机效应方程和协方差结构按 Stata 原生语法核对。"
    }
    else if strpos(" stset sts stcox streg stcrreg ", " `cmd' ") {
        local title "`cmd' — 生存与事件史分析"
        local purpose1 "用于声明生存数据、绘制生存函数或估计 Cox、参数生存与竞争风险模型。"
        local purpose2 "先确认失败事件、分析时间和删失定义；生存数据声明与模型 options 需在运行前核对。"
    }
    else if strpos(" cc cs ir ", " `cmd' ") {
        local title "`cmd' — 流行病学效应量"
        local purpose1 "用于病例对照、队列或发病率资料的比值比、风险比和相关效应量计算。"
        local purpose2 "先确认病例/暴露或事件/时间变量角色；分层与置信区间选项按 Stata 命令设置。"
    }
    else if strpos(" eregress eprobit eoprobit epoisson eintreg ", " `cmd' ") {
        local title "`cmd' — 内生协变量模型"
        local purpose1 "用于结果方程中存在内生解释变量时的扩展回归模型。"
        local purpose2 "需要明确主结果方程与内生变量方程；复杂联立结构按 Stata 原生语法填写。"
    }
    else if strpos(" teffects etregress etpoisson ", " `cmd' ") {
        local title "`cmd' — 处理效应与因果推断"
        local purpose1 "用于潜在结果框架下的处理效应估计或内生处理模型。"
        local purpose2 "先明确结果变量、处理变量和协变量；处理模型、倾向得分或结果模型选项在最后核对。"
    }
    else if strpos(" sem gsem ", " `cmd' ") {
        local title "`cmd' — 结构方程模型"
        local purpose1 "用于同时估计多个路径、潜变量和测量/结构关系。"
        local purpose2 "模型方程通常需要直接按 Stata SEM/GSEM 语法表达；复杂路径和 family/link 设置保留原生写法。"
    }
    else if strpos(" fmm irt ", " `cmd' ") {
        local title "`cmd' — 潜在类别与测量模型"
        local purpose1 "用于有限混合、潜在类别或项目反应理论分析。"
        local purpose2 "类别数、题项模型和潜在结构高度依赖具体研究设计，运行前请按 Stata 当前语法确认。"
    }
    else if strpos(" factor pca canon cca manova discrim cluster ", " `cmd' ") {
        local title "`cmd' — 多元统计分析"
        local purpose1 "用于降维、典型相关、多元方差、判别或聚类等多变量分析。"
        local purpose2 "先选择参与分析的变量；提取方法、距离、类别或维度等命令特有参数放在最后。"
    }
    else if "`cmd'" == "svy" {
        local title "svy — 调查数据估计"
        local purpose1 "用于复杂抽样设计下的加权估计和设计型标准误。"
        local purpose2 "应先用 svyset 正确声明抽样设计；本页执行的估计命令需与该设计保持一致。"
    }
    else if strpos(" lasso elasticnet sqrtlasso dsregress poivregress xporegress xpoivregress ", " `cmd' ") {
        local title "`cmd' — Lasso 与高维变量选择"
        local purpose1 "用于高维协变量下的正则化、双重选择或部分线性/工具变量估计。"
        local purpose2 "结果变量、候选变量和惩罚/选择规则应结合具体方法设置；运行前核对模型目标与推断口径。"
    }
    else if "`cmd'" == "meta" {
        local title "meta — Meta 分析"
        local purpose1 "用于汇总多项研究的效应量并进行异质性、亚组或回归分析。"
        local purpose2 "应先正确声明效应量及其标准误；模型和图形设置按 Stata meta 工作流继续完成。"
    }
    else if "`cmd'" == "mi" {
        local title "mi — 多重插补"
        local purpose1 "用于多重插补数据的声明、插补、管理与估计。"
        local purpose2 "mi 是工作流型命令；应先明确当前处于 set、impute、estimate 或数据管理的哪一步。"
    }
    else if strpos(" npregress lowess lpoly ", " `cmd' ") {
        local title "`cmd' — 非参数与平滑分析"
        local purpose1 "用于非参数回归或局部平滑，减少对函数形式的强假设。"
        local purpose2 "带宽、核函数和局部多项式阶数会影响结果；建议结合右侧图形或结果诊断。"
    }
    else if strpos(" bitesti tabi ", " `cmd' ") {
        local title "`cmd' — 精确统计"
        local purpose1 "用于小样本或汇总计数资料的精确检验与列联表分析。"
        local purpose2 "直接填写计数或概率参数；检验方向和置信水平等选项在运行前核对。"
    }
    else if strpos(" bootstrap jackknife permute simulate statsby ", " `cmd' ") {
        local title "`cmd' — 重抽样与模拟"
        local purpose1 "用于 bootstrap、jackknife、置换检验、模拟或按组重复统计。"
        local purpose2 "需要明确被重复执行的统计量/命令以及重复次数；随机种子与保存选项建议在运行前显式设置。"
    }
    else if "`cmd'" == "power" {
        local title "power — 效能与样本量"
        local purpose1 "用于研究设计阶段计算统计效能、所需样本量或可检测效应。"
        local purpose2 "先明确检验类型、效应大小、显著性水平和目标 power，再核对设计参数。"
    }
    else if strpos(" bayes bayesmh bayespredict bayesstats bayesgraph ", " `cmd' ") {
        local title "`cmd' — 贝叶斯分析"
        local purpose1 "用于贝叶斯模型估计、MCMC、后验预测、诊断或结果图形。"
        local purpose2 "先验、采样设置和后验结果对象是核心；运行前应明确当前是估计、诊断还是后估计任务。"
    }
    else if "`cmd'" == "bma" {
        local title "bma — 贝叶斯模型平均"
        local purpose1 "用于在多个候选模型之间进行贝叶斯模型平均并反映模型不确定性。"
        local purpose2 "候选变量、先验和模型空间设定会直接影响结果，建议在运行前明确研究口径。"
    }
    else if "`cmd'" == "graph" {
        local title "graph — Stata 图形管理入口"
        local purpose1 "用于调用、管理或组合 Stata 图形命令。"
        local purpose2 "具体图形类型差异较大；建议从左侧图形分类选择更具体的命令页面。"
    }
    else if "`cmd'" == "twoway" {
        local title "twoway — 二维叠加图"
        local purpose1 "用于把散点、折线、拟合线、置信区间等多个二维图层叠加。"
        local purpose2 "图层主体保持 Stata 原生 twoway 语法，适合在实时命令中继续精修。"
    }
    else if strpos(" line connected qfit dotplot graph_box ", " `cmd' ") {
        local title "`cmd' — 基础统计图形"
        local purpose1 "用于展示变量随 X 的变化、拟合关系或分布/分组特征。"
        local purpose2 "先确定主要变量与坐标/分组角色；样本条件和图形 options 放在最后。"
    }
    else if strpos(" rvfplot rvpplot avplot avplots lvr2plot cprplot acprplot ", " `cmd' ") {
        local title "`cmd' — 回归诊断图"
        local purpose1 "用于回归后检查残差、影响点、部分关系或模型设定。"
        local purpose2 "需要先成功运行兼容的估计命令；诊断图的解释应结合残差结构和模型假设。"
    }
    else if strpos(" tsline xtline ", " `cmd' ") {
        local title "`cmd' — 时间/面板趋势图"
        local purpose1 "用于按时间展示单序列或面板变量的变化轨迹。"
        local purpose2 "运行前应正确声明时间或面板结构；分组、叠加和样式 options 放在最后。"
    }
    else if strpos(" roctab rocfit roccomp rocgold rocreg ", " `cmd' ") {
        local title "`cmd' — ROC 分析"
        local purpose1 "用于评估、比较或回归建模二元结局预测的 ROC 曲线与区分能力。"
        local purpose2 "先明确真实二元结局和预测评分/模型；比较、协变量调整和图形设置按命令语法填写。"
    }
'''

marker = '    if `"`models\'"\' != "" {\n'
if semantic_block.strip() not in sem:
    idx = sem.index(marker)
    sem = sem[:idx] + semantic_block + "\n" + sem[idx:]

family_title_lines = r'''         if (Arrays.asList("table", "prtest", "sdtest", "oneway", "anova", "ranksum", "median", "signrank", "signtest").contains(command)) return "检验设定";
         if (Arrays.asList("iqreg", "bsqreg", "sureg", "mvreg").contains(command)) return "方程与变量";
         if (Arrays.asList("logistic", "hetprobit", "scobit", "cloglog", "ologit", "oprobit", "mlogit", "mprobit", "asclogit", "asmprobit").contains(command)) return "结果与解释变量";
         if (Arrays.asList("zip", "zinb", "tpoisson", "tnbreg", "fracreg", "betareg", "glm", "heckman", "heckprobit", "heckoprobit", "heckpoisson").contains(command)) return "模型变量";
         if (Arrays.asList("arima", "arch", "ucm", "dfuller", "pperron", "corrgram", "pergram").contains(command)) return "时间序列设定";
         if (Arrays.asList("var", "svar", "vec", "varsoc", "vargranger", "varstable", "irf").contains(command)) return "系统与时间设定";
         if (Arrays.asList("spregress", "spivregress", "spxtregress").contains(command)) return "空间模型设定";
         if (Arrays.asList("xtpoisson", "xtnbreg", "xtgee", "xttobit", "xtcloglog", "xtintreg", "xtoprobit", "xtmlogit", "xtfrontier", "xtabond", "xtdpdsys").contains(command)) return "变量与面板";
         if (Arrays.asList("mixed", "melogit", "meprobit", "mepoisson", "menbreg", "meologit", "meoprobit", "mestreg", "metobit", "meglm").contains(command)) return "层级与变量";
         if (Arrays.asList("stset", "sts", "stcox", "streg", "stcrreg").contains(command)) return "生存数据设定";
         if (Arrays.asList("cc", "cs", "ir").contains(command)) return "效应量设定";
         if (Arrays.asList("eregress", "eprobit", "eoprobit", "epoisson", "eintreg", "teffects", "etregress", "etpoisson").contains(command)) return "因果模型设定";
         if (Arrays.asList("sem", "gsem", "fmm", "irt").contains(command)) return "模型结构";
         if (Arrays.asList("factor", "pca", "canon", "cca", "manova", "discrim", "cluster").contains(command)) return "多元分析设定";
         if ("svy".equals(command)) return "调查设计与估计";
         if (Arrays.asList("lasso", "elasticnet", "sqrtlasso", "dsregress", "poivregress", "xporegress", "xpoivregress").contains(command)) return "高维变量设定";
         if ("meta".equals(command)) return "Meta 分析设定";
         if ("mi".equals(command)) return "多重插补任务";
         if (Arrays.asList("npregress", "lowess", "lpoly").contains(command)) return "非参数设定";
         if (Arrays.asList("bitesti", "tabi").contains(command)) return "精确检验设定";
         if (Arrays.asList("bootstrap", "jackknife", "permute", "simulate", "statsby").contains(command)) return "重复任务设定";
         if ("power".equals(command)) return "效能与样本量";
         if (Arrays.asList("bayes", "bayesmh", "bayespredict", "bayesstats", "bayesgraph", "bma").contains(command)) return "贝叶斯设定";
         if (Arrays.asList("graph", "twoway", "line", "connected", "qfit", "dotplot", "graph_box").contains(command)) return "图形设定";
         if (Arrays.asList("rvfplot", "rvpplot", "avplot", "avplots", "lvr2plot", "cprplot", "acprplot").contains(command)) return "诊断图设定";
         if (Arrays.asList("tsline", "xtline").contains(command)) return "趋势图设定";
         if (Arrays.asList("roctab", "rocfit", "roccomp", "rocgold", "rocreg").contains(command)) return "ROC 设定";
'''

title_sig = '      private static String genericCoreTitle(String command) {\n'
if family_title_lines.strip() not in java:
    java = java.replace(title_sig, title_sig + family_title_lines, 1)

family_subtitle_lines = r'''         if (Arrays.asList("table", "prtest", "sdtest", "oneway", "anova", "ranksum", "median", "signrank", "signtest").contains(command)) return "先选择检验对象和分组信息；检验方向、显著性与低频 options 放在最后。";
         if (Arrays.asList("arima", "arch", "ucm", "dfuller", "pperron", "corrgram", "pergram", "var", "svar", "vec", "varsoc", "vargranger", "varstable", "irf").contains(command)) return "先确认时间结构与分析变量；滞后、趋势、识别限制等命令特有参数集中在后续设置。";
         if (Arrays.asList("xtpoisson", "xtnbreg", "xtgee", "xttobit", "xtcloglog", "xtintreg", "xtoprobit", "xtmlogit", "xtfrontier", "xtabond", "xtdpdsys").contains(command)) return "先选择结果变量、解释变量和面板结构，再设置当前模型支持的估计选项。";
         if (Arrays.asList("mixed", "melogit", "meprobit", "mepoisson", "menbreg", "meologit", "meoprobit", "mestreg", "metobit", "meglm").contains(command)) return "先确定结果变量、解释变量和层级结构；随机效应方程按 Stata 原生语法补充。";
         if (Arrays.asList("stset", "sts", "stcox", "streg", "stcrreg").contains(command)) return "先确认生存时间、失败事件和解释变量角色；删失与模型细节在最后核对。";
         if (Arrays.asList("sem", "gsem", "fmm", "irt").contains(command)) return "先明确模型方程或潜变量结构；复杂路径、类别和分布设定保留 Stata 原生表达。";
         if (Arrays.asList("lasso", "elasticnet", "sqrtlasso", "dsregress", "poivregress", "xporegress", "xpoivregress").contains(command)) return "先设置结果变量和候选解释变量，再核对惩罚、选择和推断规则。";
         if (Arrays.asList("bootstrap", "jackknife", "permute", "simulate", "statsby").contains(command)) return "先明确要重复执行的统计量或命令，再设置重复次数、随机种子和保存选项。";
         if (Arrays.asList("graph", "twoway", "line", "connected", "qfit", "dotplot", "graph_box", "rvfplot", "rvpplot", "avplot", "avplots", "lvr2plot", "cprplot", "acprplot", "tsline", "xtline", "roctab", "rocfit", "roccomp", "rocgold", "rocreg").contains(command)) return "先完成当前图形最关键的变量或结果对象；样本范围和 Stata 图形 options 放在最后。";
'''

subtitle_sig = '      private static String genericCoreSubtitle(String command) {\n'
if family_subtitle_lines.strip() not in java:
    java = java.replace(subtitle_sig, subtitle_sig + family_subtitle_lines, 1)

sem_path.write_text(sem, encoding="utf-8")
java_path.write_text(java, encoding="utf-8")
print("HX_UI_SEMANTIC_FAMILIES_PASS7_OK")
