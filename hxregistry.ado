*! hxregistry 3.1.26  16aug2026
*! Stata-native catalog hierarchy plus HX workflow navigation, search, favorites, and recent-command state
program define hxregistry, rclass
    version 16.0
    syntax [, SEARCH(string asis) CATEGORY(string) FAVORITE(string) ///
        UNFAVORITE(string) RECENT(string) METHOD(string asis) RESET]

    /* Ordinary commands follow Stata's own Statistics/Graphics hierarchy.
       HX-only workflows stay separate. */
    local data_cmds "hxconvert generate replace keep drop merge append reshape collapse xtset tsset encode decode destring tostring winsor2 duplicates misstable"
    local stats_cmds "summarize ameans centile ci mean proportion ratio total tabstat tabulate table dtable ttest prtest sdtest oneway anova ranksum median signrank signtest test testparm testnl lincom nlcom contrast pwcompare predictnl lrtest hausman suest linktest estimates estat regress areg reghdfe cnsreg rreg hetregress qreg iqreg bsqreg sqreg vwls eivreg intreg tobit truncreg churdle boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate pwcorr logit logistic binreg probit biprobit hetprobit scobit cloglog ologit oprobit hetoprobit ziologit zioprobit mlogit mprobit clogit slogit cmset cmsummarize cmchoiceset cmtab cmsample cmclogit cmmixlogit cmxtmixlogit cmmprobit cmroprobit cmrologit nlogit asclogit asmprobit poisson nbreg gnbreg cpoisson zip zinb tpoisson tnbreg ppmlhdfe fracreg betareg glm heckman heckprobit heckoprobit heckpoisson arima arfima arimasoc arfimasoc newey prais arch ucm mswitch threshold dfgls dfuller pperron corrgram cumsp pergram wntestb wntestq psdensity rolling forecast tsappend tsfill tsfilter tsreport tssmooth var svar vec varbasic varsoc vargranger varlmar varnorm varstable varwle vecrank veclmar vecnorm vecstable irf lpirf mgarch dfactor sspace xcorr spregress spivregress spxtregress xtreg xtlogit xtprobit xtologit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtivreg xtpcse xtgls xtregar xtrc xtstreg xteregress xteprobit xteoprobit xteintreg xtheckman xthtaylor xtabond xtdpdsys xtdpd xtunitroot xtcointtest xtdescribe xtsum xttab xtdata mixed mecloglog melogit meprobit mepoisson menbreg meologit meoprobit meintreg menl mestreg metobit meglm ctset cttost ltable snapspan stset stdescribe stsum stci stcurve stbase stfill stgen stsplit stvary sttocc sttoct sts stcox streg stintreg stintcox stcrreg stir strate stptime stmh stmc cc cs ir mcc dstdize pkexamine pksumm pkcross pkequiv pkcollapse pkshape eregress eprobit eoprobit eintreg ivregress ivprobit ivtobit ivpoisson ivfprobit ivqregress ivreghdfe teffects eteffects etregress etpoisson stteffects didregress xtdidregress mediate hdidregress xthdidregress sem gsem fmm irt irtgraph diflogistic difmh dsge dsgenl alpha factor pca canon ca candisc hotelling manova mca mds mdslong mdsmat mvtest procrustes discrim cluster svyset svydescribe svy lasso elasticnet sqrtlasso poregress pologit popoisson dsregress dslogit dspoisson poivregress xporegress xpologit xpopoisson xpoivregress telasso meta mi npregress nptrend kdensity lowess lpoly exlogistic expoisson bitest bitesti ksmirnov symmetry tetrachoric tabi bootstrap jackknife permute simulate statsby power ciwidth gsbounds gsdesign bayes bayesmh bayespredict bayesreps bayesstats bayesgraph bayestest bayesvarstable bayesirf bayesfcast bmaregress bmacoefsample bmagraph bmastats bmapredict predict margins"
    if c(stata_version) < 17 {
        foreach cmd in didregress xtdidregress telasso ziologit xtmlogit stintcox bayesvarstable bayesirf bayesfcast {
            local stats_cmds : subinstr local stats_cmds " `cmd'" "", all
        }
    }
    if c(stata_version) < 18 {
        foreach cmd in mediate hdidregress xthdidregress bmaregress bmacoefsample bmagraph bmastats bmapredict dtable gsbounds gsdesign ivfprobit ivqregress arimasoc arfimasoc lpirf {
            local stats_cmds : subinstr local stats_cmds " `cmd'" "", all
        }
    }
    /* Legacy/HX shortcuts remain callable through compatibility paths, but old DID helpers are excluded from the public search catalog. */
    local reg_cmds "regress areg reghdfe rreg cnsreg vwls eivreg qreg newey prais xtreg xtlogit xtprobit logit probit poisson nbreg ppmlhdfe ivregress ivreghdfe didregress xtdidregress"
    if c(stata_version) < 17 {
        local reg_cmds : subinstr local reg_cmds " didregress" "", all
        local reg_cmds : subinstr local reg_cmds " xtdidregress" "", all
    }
    local post_cmds "test testparm testnl lincom nlcom contrast pwcompare predict predictnl margins lrtest hausman suest linktest estimates estat"
    local graph_cmds "graph twoway scatter line connected lfit qfit histogram kdensity graph_bar graph_dot graph_pie graph_box twoway_contour graph_matrix graph_combine lowess lpoly rvfplot rvpplot avplot avplots lvr2plot cprplot acprplot tsline xtline roctab rocfit roccomp rocgold rocreg cchart pchart rchart xchart shewhart serrbar symplot quantile qnorm pnorm qchi pchi qqplot gladder qladder dotplot spikeplot sunflower marginsplot coefplot event_plot"
    local did_cmds "did_builder did_trends event_plot"
    local oneclick_cmds "oneclick oneclick_robustness"
    local workflow_cmds "hxconvert oneclick oneclick_robustness"

    local all_cmds ""
    foreach cmd in `data_cmds' `stats_cmds' `graph_cmds' `oneclick_cmds' {
        if !strpos(" `all_cmds' ", " `cmd' ") local all_cmds "`all_cmds' `cmd'"
    }
    local all_cmds = trim(itrim("`all_cmds'"))

    local data_methods "导入与转换 数据检查 变量处理 样本处理 合并与追加 数据结构"

    /* Stata 18 Statistics menu order, followed by explicit HX navigation entries for searchable extensions. */
    local stats_methods "汇总，表格和假设检验 线性模型及相关 二元结果 序数结果 分类结果 计数结果 分数结果 广义线性模型 选择模型 时间序列 多元时间序列 空间自回归模型 纵向/面板数据 多层混合效应模型 生存分析 流行病学及相关 内生协变量 因果推断/处理效应 结构方程模型(SEM) 潜在类别分析(LCA) 有限混合模型(FMM) 项目反应理论(IRT) DSGE模型 多元分析 调查数据分析 Lasso回归 Meta分析 多重插补 非参数分析 精确统计 重抽样 效能，精度和样品含量 贝叶斯分析 贝叶斯模型平均 工具变量与内生性 估计后分析"
    if c(stata_version) < 18 {
        local stats_methods : subinstr local stats_methods " 贝叶斯模型平均" "", all
    }

    /* Kept as compatibility aliases for existing HX quick-entry buttons. */
    local reg_methods "线性模型 面板模型 二元结果 计数模型 工具变量 双重差分"
    local post_methods "假设检验 组合与比较 预测与边际 模型管理与诊断"

    /* Exact top-level order shown by Stata 18 Graphics menu. */
    local graph_methods "二维图(散点图，折线图等) 条形图 点图 饼图 直方图 箱线图 等高线图 散点图矩阵 分布图 平滑和密度 回归诊断图 时间序列图 面板数据折线图 生存分析图 ROC分析 多元分析图 质量控制 更多统计图形 图形组合 管理图形 更改方案/大小"

    local did_methods "DID分步构建 平行趋势与动态图"
    local oneclick_methods "控制变量组合筛选 控制变量组合稳健性"

    local defaults "regress xtreg reghdfe merge summarize margins"

    if "`reset'" != "" {
        global HXEMPIRICAL_FAVORITES ""
        global HXEMPIRICAL_RECENT ""
    }

    local favorites `"$HXEMPIRICAL_FAVORITES"'
    local favorites = trim(itrim(`"`favorites'"'))
    if `"`favorites'"' == "" local favorites "`defaults'"

    local favorite = lower(trim(`"`favorite'"'))
    local unfavorite = lower(trim(`"`unfavorite'"'))
    if `"`favorite'"' != "" {
        if !regexm("`favorite'", "^[A-Za-z_][A-Za-z0-9_]*$") {
            display as error "收藏的命令名无效。"
            exit 198
        }
        if !strpos(" `favorites' ", " `favorite' ") local favorites "`favorites' `favorite'"
    }
    if `"`unfavorite'"' != "" {
        local kept ""
        foreach cmd of local favorites {
            if "`cmd'" != "`unfavorite'" local kept "`kept' `cmd'"
        }
        local favorites = trim(itrim("`kept'"))
    }
    if `"`favorite'`unfavorite'"' != "" {
        global HXEMPIRICAL_FAVORITES `"`favorites'"'
    }

    local recentcmds `"$HXEMPIRICAL_RECENT"'
    local recentcmds = trim(itrim(`"`recentcmds'"'))
    local recent = lower(trim(`"`recent'"'))
    if `"`recent'"' != "" {
        gettoken recent_name unused : recent
        local updated "`recent_name'"
        local n 1
        foreach cmd of local recentcmds {
            if "`cmd'" != "`recent_name'" & `n' < 12 {
                local updated "`updated' `cmd'"
                local ++n
            }
        }
        local recentcmds = trim(itrim("`updated'"))
        global HXEMPIRICAL_RECENT `"`recentcmds'"'
    }

    local search = lower(trim(`"`search'"'))
    if substr(`"`search'"', 1, 1) == char(34) & substr(`"`search'"', -1, 1) == char(34) {
        local search = substr(`"`search'"', 2, strlen(`"`search'"') - 2)
    }
    local matches ""
    if `"`search'"' == "" local matches "`all_cmds'"
    else {
        local key_generate "generate gen 生成 创建 新变量 计算"
        local key_hxconvert "转换为dta 转换 dta excel csv txt 导入 文件"
        local key_replace "replace 修改 替换 更新变量"
        local key_keep "keep 保留 筛选 样本 变量"
        local key_drop "drop 删除 剔除 样本 缺失"
        local key_merge "merge 合并 主表 副表 匹配 关联"
        local key_append "append 追加 拼接 纵向合并"
        local key_reshape "reshape 宽表 长表 转换"
        local key_collapse "collapse 汇总 聚合 分组 均值"
        local key_xtset "xtset panel data 面板 设置 个体 时间"
        local key_arfima "arfima long memory fractional integration 长记忆 分数差分 时间序列"
        local key_arimasoc "arimasoc ARIMA ARMA lag order selection AIC BIC HQIC 阶数选择"
        local key_arfimasoc "arfimasoc ARFIMA lag order selection AIC BIC HQIC 阶数选择"
        local key_mswitch "mswitch Markov switching regime 状态转换 马尔可夫 转换 回归"
        local key_threshold "threshold regression 门槛 回归 阈值 时间序列"
        local key_dfgls "dfgls unit root DF GLS 单位根 检验 平稳性"
        local key_wntestb "wntestb white noise Bartlett 白噪声 周期图 检验"
        local key_wntestq "wntestq white noise portmanteau Q 白噪声 检验"
        local key_rolling "rolling recursive window 滚动窗口 递归估计"
        local key_forecast "forecast model forecasting dynamic static 预测 模型 情景"
        local key_tsfilter "tsfilter HP BK CF BW filter 滤波 周期 趋势"
        local key_tssmooth "tssmooth moving average exponential Holt Winters 平滑 预测"
        local key_lpirf "lpirf local projection impulse response 局部投影 脉冲响应"
        local key_mgarch "mgarch multivariate GARCH DCC CCC VCC 多元 波动率 相关"
        local key_dfactor "dfactor dynamic factor latent factor 动态因子 潜在因子"
        local key_sspace "sspace state space Kalman 状态空间 卡尔曼"
        local key_vecrank "vecrank Johansen cointegration rank 协整秩 检验"
        local key_irtgraph "irtgraph ICC TCC IIF TIF item characteristic information 项目反应 图形 信息函数 特征曲线"
        local key_diflogistic "diflogistic IRT differential item functioning logistic DIF 差异项目功能 逻辑回归"
        local key_difmh "difmh IRT Mantel Haenszel DIF differential item functioning 差异项目功能"
        local key_dsge "dsge dynamic stochastic general equilibrium DSGE 动态随机一般均衡 线性化 宏观模型"
        local key_dsgenl "dsgenl nonlinear DSGE dynamic stochastic general equilibrium 非线性 动态随机一般均衡"
        local key_pkexamine "pkexamine pharmacokinetic concentration time AUC half-life cmax 药代动力学 浓度 时间 半衰期"
        local key_pksumm "pksumm pharmacokinetic summary AUC distribution 药代动力学 汇总 正态性"
        local key_pkcross "pkcross pharmacokinetic crossover experiment 交叉试验 药代动力学"
        local key_pkequiv "pkequiv bioequivalence pharmacokinetic 生物等效 药代动力学 TOST"
        local key_pkcollapse "pkcollapse pharmacokinetic collapse measurements reshape 药代动力学 AUC 数据转换"
        local key_pkshape "pkshape pharmacokinetic Latin square crossover reshape 药代动力学 拉丁方 交叉设计 重塑"
        local key_nptrend "nptrend nonparametric trend Cochran Armitage Jonckheere Terpstra Cuzick 趋势检验 非参数 有序组 exact"
        local key_bayestest "bayestest Bayesian hypothesis model comparison interval Bayes factor 贝叶斯 假设检验 模型比较"
        local key_bayesreps "bayesreps Bayesian posterior predictive MCMC replicates 后验预测 复制样本 模型检查"
        local key_bayesvarstable "bayesvarstable Bayesian VAR stability eigenvalue 贝叶斯 VAR 稳定性 特征根"
        local key_bayesirf "bayesirf Bayesian IRF FEVD impulse response 贝叶斯 脉冲响应 方差分解"
        local key_bayesfcast "bayesfcast Bayesian dynamic forecast VAR 贝叶斯 动态预测"
        local key_bmacoefsample "bmacoefsample Bayesian model averaging posterior coefficient sample BMA 系数 后验抽样"
        local key_bmagraph "bmagraph BMA PMP PIP model size variable map coefficient density 模型概率 图"
        local key_bmastats "bmastats BMA posterior inclusion probability PIP model size jointness LPS 统计"
        local key_bmapredict "bmapredict BMA prediction posterior predictive mean credible interval 预测"
        local key_tsset "tsset time series 时间序列 时间变量 声明"
        local key_ctset "ctset count-time survival 生存 计数时间 声明"
        local key_cttost "cttost count-time to survival 转换 生存数据"
        local key_ltable "ltable life table actuarial 生存表 寿命表"
        local key_stdescribe "stdescribe survival describe 生存数据 描述 结构"
        local key_stsum "stsum survival summary Kaplan Meier 生存时间 汇总"
        local key_stci "stci survival confidence interval mean median 生存 置信区间"
        local key_stcurve "stcurve survival failure hazard cumulative hazard 生存曲线 风险"
        local key_stsplit "stsplit split time records 生存 时间段 拆分"
        local key_stgen "stgen survival history variable 生存 历史 生成变量"
        local key_stfill "stfill carry forward covariates 生存 协变量 前向填充"
        local key_stvary "stvary time-varying covariates 生存 时变变量"
        local key_sttocc "sttocc nested case control 生存 嵌套 病例对照"
        local key_sttoct "sttoct survival count-time 转换 生存 计数时间"
        local key_stir "stir incidence rate ratio 生存 发病率 比率"
        local key_strate "strate failure rates SMR 生存 率 标准化死亡比"
        local key_stptime "stptime person-time incidence rate 生存 人时 发病率"
        local key_stmh "stmh Mantel Haenszel rate ratio 生存 分层 率比"
        local key_stmc "stmc Mantel Cox rate ratio 生存 分层 率比"
        local key_encode "encode 字符串 数值 编码 标签"
        local key_decode "decode 数值 字符串 解码 标签"
        local key_destring "destring 字符串 转 数值"
        local key_tostring "tostring 数值 转 字符串"
        local key_winsor2 "winsor2 缩尾 极端值"
        local key_duplicates "duplicates 重复值 重复记录"
        local key_misstable "misstable 缺失值"
        local key_summarize "summarize sum 描述统计 汇总 均值 标准差"
        local key_ameans "ameans arithmetic geometric harmonic means 算术 几何 调和 平均数 描述统计"
        local key_centile "centile percentile quantile 百分位 分位数 置信区间"
        local key_ci "ci confidence interval means proportions variances 置信区间 均值 比例 方差"
        local key_mean "mean estimate means 均值 置信区间 分组"
        local key_proportion "proportion proportions 比例 构成比 置信区间"
        local key_ratio "ratio estimate ratios 比率 比值 分子 分母 置信区间"
        local key_total "total estimate totals 总量 总计 置信区间"
        local key_dtable "dtable table 1 descriptive statistics 描述统计 表1 分组检验"
        local key_tabstat "tabstat 分组统计 描述统计 汇总"
        local key_pwcorr "pwcorr 相关系数 显著性"
        local key_correlate "correlate corr 相关系数"
        local key_ttest "ttest 均值检验 t检验 假设检验"
        local key_tabulate "tabulate tab 频数 列联表 表格"
        local key_regress "regress ols linear regression 线性回归 最小二乘 基准回归 普通回归 稳健标准误 聚类"
        local key_hetregress "hetregress heteroskedastic linear regression 异方差 线性回归 方差方程 het"
        local key_sqreg "sqreg simultaneous quantile regression 同时 分位数回归 多分位"
        local key_intreg "intreg interval regression 区间回归 左删失 右删失 区间删失"
        local key_tobit "tobit censored regression 删失回归 左删失 右删失"
        local key_truncreg "truncreg truncated regression 截断回归 左截断 右截断"
        local key_boxcox "boxcox Box Cox transformation regression 变换 回归"
        local key_fp "fp fractional polynomial regression 分数多项式 非线性 函数形式"
        local key_nl "nl nonlinear least squares 非线性 最小二乘"
        local key_nlsur "nlsur nonlinear seemingly unrelated regression 非线性 似不相关 方程组"
        local key_gmm "gmm generalized method of moments 广义矩 估计 方程 工具变量"
        local key_reg3 "reg3 three stage least squares simultaneous equations 三阶段最小二乘 联立方程"
        local key_frontier "frontier stochastic frontier production cost efficiency 随机前沿 生产 成本 效率"
        local key_areg "areg absorb fixed effect 吸收固定效应 线性模型"
        local key_qreg "qreg quantile median 分位数回归 中位数"
        local key_rreg "rreg robust regression 稳健回归 异常值 outlier"
        local key_cnsreg "cnsreg constrained regression 约束回归 constraints 参数约束"
        local key_vwls "vwls variance weighted least squares 方差加权 最小二乘"
        local key_eivreg "eivreg errors in variables measurement error 测量误差 可靠度"
        local key_newey "newey newey west hac 标准误 自相关 时间序列"
        local key_prais "prais prais winsten cochrane orcutt ar1 自相关 时间序列"
        local key_xtreg "xtreg panel regression fixed effects random effects 面板回归 固定效应 随机效应 纵向"
        local key_xtlogit "xtlogit panel binary 面板 二元 逻辑回归"
        local key_xtprobit "xtprobit panel binary 面板 二元 概率回归"
        local key_xtologit "xtologit panel ordered logit 面板 有序 逻辑回归 随机效应"
        local key_xtivreg "xtivreg panel instrumental variables 面板 工具变量 内生性 固定效应 随机效应"
        local key_xtpcse "xtpcse panel corrected standard errors 面板校正标准误 截面相关 AR1"
        local key_xtregar "xtregar panel AR1 serial correlation 面板 自相关 固定效应 随机效应"
        local key_xtrc "xtrc random coefficients panel 随机系数 面板回归"
        local key_xtstreg "xtstreg panel survival random effects 生存分析 面板 随机效应"
        local key_mecloglog "mecloglog mixed effects complementary loglog 多层 混合效应 二元"
        local key_meintreg "meintreg multilevel interval regression 多层 区间回归 随机系数"
        local key_menl "menl mixed effects nonlinear regression 多层 非线性 混合效应"
        local key_stintreg "stintreg interval censored survival 区间删失 生存 参数模型"
        local key_stintcox "stintcox interval censored Cox 区间删失 生存 Cox 比例风险"
        local key_xteregress "xteregress extended random effects panel ERM 面板 扩展回归 内生协变量 选择 处理"
        local key_xteprobit "xteprobit extended random effects probit panel ERM 面板 扩展 Probit 内生协变量"
        local key_xteoprobit "xteoprobit extended ordered probit panel ERM 面板 扩展 有序 Probit"
        local key_xteintreg "xteintreg extended interval regression panel ERM 面板 扩展 区间回归"
        local key_xtheckman "xtheckman panel sample selection Heckman 面板 样本选择 随机效应"
        local key_xthtaylor "xthtaylor Hausman Taylor panel 面板 内生 个体效应 工具变量"
        local key_xtdpd "xtdpd dynamic panel GMM 动态面板 差分 系统 GMM 工具变量"
        local key_xtgls "xtgls panel generalized least squares FGLS 面板 广义最小二乘 异方差 自相关"
        local key_xtunitroot "xtunitroot panel unit root test 面板 单位根 平稳性"
        local key_xtcointtest "xtcointtest panel cointegration Kao Pedroni Westerlund 面板 协整检验"
        local key_xtdescribe "xtdescribe panel pattern 面板结构 描述 平衡 非平衡"
        local key_xtsum "xtsum panel summary within between 面板 描述统计 组内 组间"
        local key_xttab "xttab panel tabulation within between 面板 分类统计 组内 组间"
        local key_xtdata "xtdata panel transform within between 面板 数据变换 固定效应 随机效应"
        local key_reghdfe "reghdfe high dimensional fixed effects absorb 高维固定效应 吸收 固定效应 企业固定效应 年份固定效应"
        local key_logit "logit 二元 逻辑回归"
        local key_binreg "binreg binomial glm risk ratio risk difference odds ratio 二项 风险比 风险差"
        local key_biprobit "biprobit bivariate probit two binary equations 二元 双变量 probit 联立 方程"
        local key_hetoprobit "hetoprobit heteroskedastic ordered probit 序数 异方差 有序 probit"
        local key_ziologit "ziologit zero inflated ordered logit 零膨胀 序数 有序 logit inflate"
        local key_zioprobit "zioprobit zero inflated ordered probit 零膨胀 序数 有序 probit inflate"
        local key_clogit "clogit conditional logistic matched case control fixed effects 条件 logistic 配对 病例对照"
        local key_slogit "slogit stereotype logistic categorical ordinal stereotype 分类 立体型 logit"
        local key_cmset "cmset choice model data declare case alternative panel choice 选择模型 数据声明 备选项"
        local key_cmsummarize "cmsummarize choice data summarize 选择模型 描述 备选项"
        local key_cmchoiceset "cmchoiceset choice sets tabulate diagnose 选择集 检查"
        local key_cmtab "cmtab chosen alternatives tabulate 选择模型 选择结果 频数"
        local key_cmsample "cmsample choice sample exclusion 选择模型 样本 排除 诊断"
        local key_cmclogit "cmclogit conditional logit McFadden choice 选择模型 条件 logit 备选项"
        local key_cmmixlogit "cmmixlogit mixed logit random coefficients choice 混合 logit 随机系数 选择"
        local key_cmxtmixlogit "cmxtmixlogit panel mixed logit repeated choice 面板 混合 logit 重复选择"
        local key_cmmprobit "cmmprobit multinomial probit choice 多项 probit 选择模型"
        local key_cmroprobit "cmroprobit rank ordered probit choice 排序 probit 选择模型"
        local key_cmrologit "cmrologit rank ordered logit choice 排序 logit 选择模型"
        local key_nlogit "nlogit nested logit choice tree 巢式 logit 选择模型 树"
        local key_probit "probit 二元 概率回归"
        local key_poisson "poisson count 泊松 计数模型"
        local key_gnbreg "gnbreg generalized negative binomial heterogeneous dispersion 负二项 广义 异质 离散参数 lnalpha"
        local key_cpoisson "cpoisson censored poisson count 删失 泊松 计数 左删失 右删失 区间"
        local key_churdle "churdle Cragg hurdle double hurdle select limited outcome 障碍模型 两阶段 选择"
        local key_nbreg "nbreg negative binomial 负二项 计数模型"
        local key_ivregress "ivregress iv 2sls gmm liml 工具变量 内生性"
        local key_ivprobit "ivprobit instrumental variables probit endogenous binary 工具变量 二元 内生 probit"
        local key_ivtobit "ivtobit instrumental variables tobit censored endogenous 工具变量 tobit 删失 内生"
        local key_ivpoisson "ivpoisson instrumental variables poisson count endogenous gmm 工具变量 泊松 计数 内生"
        local key_ivfprobit "ivfprobit fractional probit endogenous covariates 工具变量 分数结果 内生 probit"
        local key_ivqregress "ivqregress instrumental variables quantile regression IQR smooth 工具变量 分位数 内生"
        local key_didregress "didregress did difference-in-differences ddd 双重差分 重复截面 平行趋势 因果推断 处理效应"
        local key_xtdidregress "xtdidregress did panel longitudinal 双重差分 面板 平行趋势 因果推断 处理效应"
        local key_hdidregress "hdidregress heterogeneous did repeated cross section 异质 双重差分 队列 时间"
        local key_xthdidregress "xthdidregress heterogeneous did panel 异质 双重差分 面板 队列 时间"
        local key_eteffects "eteffects endogenous treatment effects 内生处理 处理效应 因果推断"
        local key_stteffects "stteffects survival treatment effects 生存 处理效应 因果推断"
        local key_mediate "mediate causal mediation 中介效应 直接效应 间接效应 因果中介"
        local key_ivreghdfe "ivreghdfe high dimensional fixed effects instrument 高维固定效应 工具变量 内生性"
        local key_did_builder "did difference in differences event study treat post event_time 平行趋势 事件研究 双重差分 政策冲击 动态效应"
        local key_ppmlhdfe "ppmlhdfe poisson pseudo maximum likelihood fixed effects 泊松 伪极大似然 高维固定效应"
        local key_alpha "alpha cronbach reliability 量表 信度 克隆巴赫"
        local key_ca "ca correspondence analysis 对应分析 列联表"
        local key_candisc "candisc canonical discriminant analysis 典型 判别分析"
        local key_hotelling "hotelling t squared multivariate means 多元 均值 检验"
        local key_mca "mca multiple joint correspondence analysis 多重 联合 对应分析"
        local key_mds "mds multidimensional scaling 多维尺度 距离"
        local key_mdslong "mdslong multidimensional scaling long 多维尺度 长表 距离"
        local key_mdsmat "mdsmat multidimensional scaling matrix 多维尺度 矩阵 距离"
        local key_mvtest "mvtest multivariate test means covariance correlation normality 多元检验"
        local key_procrustes "procrustes transformation shape configuration 普鲁克拉斯 变换"
        local key_mcc "mcc matched case control matched pairs epidemiology 配对 病例对照 McNemar"
        local key_dstdize "dstdize standardize rates direct indirect standardization 标准化 标化率 流行病学"
        local key_exlogistic "exlogistic exact logistic regression 精确 logistic 小样本 完全预测"
        local key_expoisson "expoisson exact poisson regression 精确 poisson 小样本 计数"
        local key_bitest "bitest exact binomial probability test 二项 精确检验"
        local key_bitesti "bitesti immediate exact binomial probability test 二项 即时 精确检验"
        local key_ksmirnov "ksmirnov kolmogorov smirnov exact distribution 非参数 分布 检验"
        local key_symmetry "symmetry marginal homogeneity exact matched table 对称 边际同质 精确"
        local key_tetrachoric "tetrachoric binary correlation exact 二元 相关 四分相关"
        local key_svyset "svyset survey design 调查数据 抽样设计 权重 分层 psu strata pweight"
        local key_svydescribe "svydescribe survey describe 调查数据 设计结构 分层 psu"
        local key_svy "svy survey prefix 调查数据 加权估计 复杂抽样"
        local key_sqrtlasso "sqrtlasso square root lasso 平方根 lasso 高维 变量选择"
        local key_poregress "poregress partialing out lasso linear 高维 推断 部分化 线性回归"
        local key_pologit "pologit partialing out lasso logit 高维 推断 二元"
        local key_popoisson "popoisson partialing out lasso poisson 高维 推断 计数"
        local key_dslogit "dslogit double selection lasso logit 双重选择 高维 二元"
        local key_dspoisson "dspoisson double selection lasso poisson 双重选择 高维 计数"
        local key_xpologit "xpologit cross fit partialing out lasso logit 交叉拟合 高维 二元"
        local key_xpopoisson "xpopoisson cross fit partialing out lasso poisson 交叉拟合 高维 计数"
        local key_telasso "telasso treatment effects lasso 处理效应 高维 因果推断"
        local key_test "test 系数检验 联合检验 假设检验"
        local key_lincom "lincom 线性组合 系数"
        local key_power "power sample size effect size statistical power 样本量 效能 效应量"
        local key_ciwidth "ciwidth confidence interval width precision sample size 精度 置信区间宽度 样本量"
        local key_gsbounds "gsbounds group sequential stopping boundaries efficacy futility 序贯 停止界值 疗效 无效"
        local key_gsdesign "gsdesign group sequential sample size interim analysis 序贯设计 样本量 中期分析"
        local key_bmaregress "bmaregress bma bayesian model averaging 贝叶斯模型平均 模型不确定性 变量选择"
        local key_predict "predict 预测值 残差"
        local key_margins "margins 边际效应 调节效应"
        local key_graph_bar "graph bar bar chart 条形图 柱状图 over 分组 均值 频数"
        local key_graph_dot "graph dot dot chart 点图 over 分组 均值"
        local key_graph_pie "graph pie pie chart 饼图 over 分组 百分比"
        local key_graph_matrix "graph matrix scatterplot matrix 散点图矩阵 多变量"
        local key_twoway_contour "twoway contour contour plot 等高线 三变量 z y x"
        local key_graph_combine "graph combine combine graphs 图形组合 多图 拼图"
        local key_cchart "cchart quality control count chart 质量控制 c图 计数"
        local key_pchart "pchart quality control proportion chart 质量控制 p图 比例"
        local key_rchart "rchart quality control range chart 质量控制 R图 极差"
        local key_xchart "xchart quality control mean chart 质量控制 Xbar图 均值"
        local key_shewhart "shewhart quality control chart 质量控制 控制限"
        local key_serrbar "serrbar standard error bar chart 标准误 误差棒"
        local key_symplot "symplot symmetry plot distribution 对称图 分布诊断"
        local key_quantile "quantile quantile plot distribution 分位数图"
        local key_qnorm "qnorm quantile normal plot 正态 分位数图"
        local key_pnorm "pnorm normal probability plot 正态 概率图"
        local key_qchi "qchi quantile chi squared plot 卡方 分位数图"
        local key_pchi "pchi chi squared probability plot 卡方 概率图"
        local key_qqplot "qqplot quantile quantile two variables Q-Q 两变量 分位数"
        local key_gladder "gladder ladder of powers distribution transformation 变换 梯图"
        local key_qladder "qladder quantile normal ladder transformation 梯图 正态"
        local key_dotplot "dotplot distribution dot plot 分布 点图 堆叠"
        local key_spikeplot "spikeplot spike plot distribution 尖峰图 分布"
        local key_sunflower "sunflower density distribution bivariate scatter 密度 向日葵图"
        local key_testparm "testparm joint Wald parameter terms 联合检验 参数组 因子变量"
        local key_testnl "testnl nonlinear Wald hypothesis 非线性 假设检验 delta method"
        local key_nlcom "nlcom nonlinear combination coefficients delta method 非线性 系数组合"
        local key_contrast "contrast factor levels main interaction simple effects 对比 主效应 交互效应"
        local key_pwcompare "pwcompare pairwise comparison multiple comparisons Tukey Bonferroni 两两比较 多重比较"
        local key_predictnl "predictnl nonlinear prediction standard error delta method 非线性预测 标准误"
        local key_lrtest "lrtest likelihood ratio nested models 似然比 嵌套模型 检验"
        local key_hausman "hausman specification exogeneity IIA 固定效应 随机效应 模型比较"
        local key_suest "suest seemingly unrelated estimation combine estimates cross-model test 合并模型 跨模型检验"
        local key_linktest "linktest specification link test 模型设定 检验 _hat _hatsq"
        local key_estimates "estimates store restore table stats save replay 模型结果 保存 恢复 比较"
        local key_estat "estat postestimation statistics ic vif gof hettest vce 后估计 诊断"
        local key_graph "graph 饼图 散点图矩阵 质量控制 图形组合 管理图形 图形方案 图形大小"
        local key_histogram "histogram 直方图 分布 频数 密度"
        local key_kdensity "kdensity 核密度 平滑 分布"
        local key_scatter "scatter 散点图 二维图 变量关系"
        local key_lfit "lfit 线性拟合 拟合线 二维图"
        local key_graph_box "graph box 箱线图 分组分布 异常值"
        local key_twoway "twoway 二维图 叠加图 自定义图形"
        local key_marginsplot "marginsplot 边际效应图 调节效应图"
        local key_coefplot "coefplot 系数图 回归结果图"
        local key_did_trends "did trends 平行趋势 处理组 对照组 趋势图"
        local key_event_plot "event plot 事件研究 动态效应 平行趋势"
        local key_oneclick "oneclick 控制变量 组合 筛选 显著性"
        local key_oneclick_robustness "oneclick robustness 稳健性 specification curve 系数分布 控制变量组合 模型稳健性"
        foreach cmd of local all_cmds {
            local hay = lower(`"`cmd' `key_`cmd''"')
            if strpos(`"`hay'"', `"`search'"') local matches "`matches' `cmd'"
        }
        local matches = trim(itrim("`matches'"))
    }

    char _dta[hxtoolbox_commands] `"`all_cmds'"'
    char _dta[hxtoolbox_data_cmds] `"`data_cmds'"'
    char _dta[hxtoolbox_stats_cmds] `"`stats_cmds'"'
    char _dta[hxtoolbox_reg_cmds] `"`reg_cmds'"'
    char _dta[hxtoolbox_post_cmds] `"`post_cmds'"'
    char _dta[hxtoolbox_graph_cmds] `"`graph_cmds'"'
    char _dta[hxtoolbox_did_cmds] `"`did_cmds'"'
    char _dta[hxtoolbox_oneclick_cmds] `"`oneclick_cmds'"'
    char _dta[hxtoolbox_workflow_cmds] `"`workflow_cmds'"'
    char _dta[hxtoolbox_data_methods] `"`data_methods'"'
    char _dta[hxtoolbox_stats_methods] `"`stats_methods'"'
    char _dta[hxtoolbox_reg_methods] `"`reg_methods'"'
    char _dta[hxtoolbox_post_methods] `"`post_methods'"'
    char _dta[hxtoolbox_graph_methods] `"`graph_methods'"'
    char _dta[hxtoolbox_did_methods] `"`did_methods'"'
    char _dta[hxtoolbox_oneclick_methods] `"`oneclick_methods'"'
    char _dta[hxtoolbox_favorites] `"`favorites'"'
    char _dta[hxtoolbox_recent] `"`recentcmds'"'
    char _dta[hxtoolbox_search] `"`matches'"'

    local category = lower(trim(`"`category'"'))
    local view `"`matches'"'
    local method_view ""
    local browser_mode "commands"
    if `"`category'"' == "data" {
        local method_view `"`data_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "stats" {
        local method_view `"`stats_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "reg" {
        local method_view `"`reg_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "post" {
        local method_view `"`post_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "graph" {
        local method_view `"`graph_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "did" {
        local method_view `"`did_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "oneclick" {
        local method_view `"`oneclick_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "favorites" local view `"`favorites'"'
    if `"`category'"' == "recent" local view `"`recentcmds'"'

    local method = trim(`"`method'"')
    if substr(`"`method'"', 1, 1) == char(34) & substr(`"`method'"', -1, 1) == char(34) {
        local method = substr(`"`method'"', 2, strlen(`"`method'"') - 2)
    }
    local method_title `"`method'"'
    local method_desc "选择下面的具体 Stata 命令，再进入该命令自己的设置页面。"

    /* Data/HX compatibility paths. */
    if inlist(`"`method'"', "导入与转换", "import_convert") local view "hxconvert"
    else if inlist(`"`method'"', "数据检查", "data_check") local view "misstable duplicates"
    else if inlist(`"`method'"', "变量处理", "variable_processing") local view "generate replace encode decode destring tostring winsor2"
    else if inlist(`"`method'"', "样本处理", "sample_processing") local view "keep drop"
    else if inlist(`"`method'"', "合并与追加", "merge_append") local view "merge append"
    else if inlist(`"`method'"', "数据结构", "data_structure") local view "reshape collapse xtset tsset"

    /* Stata Statistics menu. */
    else if inlist(`"`method'"', "汇总，表格和假设检验", "summary_tests") {
        local view "summarize ameans centile ci mean proportion ratio total tabstat tabulate table"
        if c(stata_version) >= 18 local view "`view' dtable"
        local view "`view' ttest prtest sdtest oneway anova ranksum median signrank signtest"
    }
    else if inlist(`"`method'"', "线性模型及相关", "linear_related") local view "regress areg reghdfe cnsreg rreg hetregress qreg iqreg bsqreg sqreg vwls eivreg intreg tobit truncreg churdle boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate pwcorr"
    else if inlist(`"`method'"', "二元结果", "binary_outcomes") local view "logit logistic binreg probit biprobit hetprobit scobit cloglog"
    else if inlist(`"`method'"', "序数结果", "ordinal_outcomes") {
        local view "ologit oprobit hetoprobit zioprobit"
        if c(stata_version) >= 17 local view "`view' ziologit"
    }
    else if inlist(`"`method'"', "分类结果", "categorical_outcomes") local view "mlogit mprobit clogit slogit cmset cmsummarize cmchoiceset cmtab cmsample cmclogit cmmixlogit cmxtmixlogit cmmprobit cmroprobit cmrologit nlogit asclogit asmprobit"
    else if inlist(`"`method'"', "计数结果", "count_outcomes") local view "poisson nbreg gnbreg cpoisson ppmlhdfe zip zinb tpoisson tnbreg"
    else if inlist(`"`method'"', "分数结果", "fractional_outcomes") local view "fracreg betareg"
    else if inlist(`"`method'"', "广义线性模型", "glm_models") local view "glm"
    else if inlist(`"`method'"', "选择模型", "selection_models") local view "heckman heckprobit heckoprobit heckpoisson"
    else if inlist(`"`method'"', "时间序列", "time_series") {
        local view "arima arfima"
        if c(stata_version) >= 18 local view "`view' arimasoc arfimasoc"
        local view "`view' newey prais arch ucm mswitch threshold dfgls dfuller pperron corrgram cumsp pergram wntestb wntestq"
        local view "`view' psdensity rolling forecast tsappend tsfill tsfilter tsreport tssmooth"
    }
    else if inlist(`"`method'"', "多元时间序列", "multivariate_ts") {
        local view "var svar vec varbasic varsoc vargranger varlmar varnorm varstable varwle vecrank veclmar vecnorm vecstable irf"
        if c(stata_version) >= 18 local view "`view' lpirf"
        local view "`view' mgarch dfactor sspace xcorr"
    }
    else if inlist(`"`method'"', "空间自回归模型", "spatial_ar") local view "spregress spivregress spxtregress"
    else if inlist(`"`method'"', "纵向/面板数据", "panel_longitudinal") {
        local view "xtreg xtlogit xtprobit xtologit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit"
        if c(stata_version) >= 17 local view "`view' xtmlogit"
        local view "`view' xtfrontier xtivreg xtpcse xtgls xtregar xtrc xtstreg"
        local view "`view' xteregress xteprobit xteoprobit xteintreg xtheckman xthtaylor"
        local view "`view' xtabond xtdpdsys xtdpd xtunitroot xtcointtest xtdescribe xtsum xttab xtdata"
    }
    else if inlist(`"`method'"', "多层混合效应模型", "mixed_effects") local view "mixed mecloglog melogit meprobit mepoisson menbreg meologit meoprobit meintreg menl mestreg metobit meglm"
    else if inlist(`"`method'"', "生存分析", "survival") {
        /* Common estimation workflow first; data-management and legacy rate tools later. */
        local view "stset stcox streg stintreg"
        if c(stata_version) >= 17 local view "`view' stintcox"
        local view "`view' stcrreg sts stcurve stdescribe stsum stci"
        local view "`view' stbase stfill stgen stsplit stvary sttocc sttoct"
        local view "`view' stir strate stptime stmh stmc ctset cttost ltable snapspan"
    }
    else if inlist(`"`method'"', "流行病学及相关", "epidemiology") local view "cc cs ir mcc dstdize pkexamine pksumm pkcross pkequiv pkcollapse pkshape"
    else if inlist(`"`method'"', "内生协变量", "endogenous_covariates") local view "eregress eprobit eoprobit eintreg"
    else if inlist(`"`method'"', "样本选择模型", "sample_selection") local view "heckman heckprobit heckoprobit heckpoisson"
    else if inlist(`"`method'"', "因果推断/处理效应", "causal_treatment") {
        local view "teffects eteffects etregress etpoisson stteffects"
        if c(stata_version) >= 17 local view "`view' didregress xtdidregress telasso"
        if c(stata_version) >= 18 local view "`view' mediate hdidregress xthdidregress"
    }
    else if inlist(`"`method'"', "结构方程模型(SEM)", "sem") local view "sem gsem"
    else if inlist(`"`method'"', "潜在类别分析(LCA)", "lca") local view "gsem"
    else if inlist(`"`method'"', "有限混合模型(FMM)", "fmm") local view "fmm"
    else if inlist(`"`method'"', "项目反应理论(IRT)", "irt") local view "irt irtgraph diflogistic difmh"
    else if inlist(`"`method'"', "DSGE模型", "dsge") local view "dsge dsgenl"
    else if inlist(`"`method'"', "多元分析", "multivariate") local view "alpha factor pca canon ca candisc hotelling manova mvreg mca mds mdslong mdsmat mvtest procrustes discrim cluster"
    else if inlist(`"`method'"', "调查数据分析", "survey") local view "svyset svydescribe svy"
    else if inlist(`"`method'"', "Lasso回归", "lasso") local view "lasso elasticnet sqrtlasso poregress pologit popoisson dsregress dslogit dspoisson poivregress xporegress xpologit xpopoisson xpoivregress"
    else if inlist(`"`method'"', "Meta分析", "meta") local view "meta"
    else if inlist(`"`method'"', "多重插补", "mi") local view "mi"
    else if inlist(`"`method'"', "非参数分析", "nonparametric") local view "ranksum median signrank signtest npregress nptrend kdensity lowess lpoly"
    else if inlist(`"`method'"', "精确统计", "exact_stats") local view "exlogistic expoisson bitest bitesti ksmirnov symmetry tetrachoric tabi"
    else if inlist(`"`method'"', "重抽样", "resampling") local view "bootstrap jackknife permute simulate statsby"
    else if inlist(`"`method'"', "效能，精度和样品含量", "power_precision") {
        local view "power ciwidth"
        if c(stata_version) >= 18 local view "`view' gsbounds gsdesign"
    }
    else if inlist(`"`method'"', "贝叶斯分析", "bayes") {
        local view "bayes bayesmh bayespredict bayesreps bayesstats bayesgraph bayestest"
        if c(stata_version) >= 17 local view "`view' bayesvarstable bayesirf bayesfcast"
    }
    else if inlist(`"`method'"', "贝叶斯模型平均", "bma") {
        if c(stata_version) >= 18 local view "bmaregress bmacoefsample bmagraph bmastats bmapredict"
        else local view ""
    }
    else if inlist(`"`method'"', "工具变量与内生性", "iv_extensions") {
        local view "ivregress ivprobit ivtobit ivpoisson ivreghdfe"
        if c(stata_version) >= 18 local view "`view' ivfprobit ivqregress"
    }
    else if inlist(`"`method'"', "估计后分析", "postestimation") local view "test testparm testnl lincom nlcom contrast pwcompare predict predictnl margins marginsplot lrtest hausman suest linktest estimates estat"

    /* Stata Graphics menu. Multiword graph families use the native one-token
       entry point where the generic parser cannot safely represent a subcommand. */
    else if inlist(`"`method'"', "二维图(散点图，折线图等)", "twoway_graphs") local view "twoway scatter line connected lfit qfit lowess lpoly"
    else if inlist(`"`method'"', "条形图", "bar_graph") local view "graph_bar"
    else if inlist(`"`method'"', "点图", "dot_graph") local view "graph_dot"
    else if inlist(`"`method'"', "饼图", "pie_graph") local view "graph_pie"
    else if inlist(`"`method'"', "直方图", "histogram_graph") local view "histogram"
    else if inlist(`"`method'"', "箱线图", "box_graph") local view "graph_box"
    else if inlist(`"`method'"', "等高线图", "contour_graph") local view "twoway_contour"
    else if inlist(`"`method'"', "散点图矩阵", "matrix_graph") local view "graph_matrix"
    else if inlist(`"`method'"', "分布图", "distribution_graph") local view "histogram kdensity"
    else if inlist(`"`method'"', "平滑和密度", "smooth_density") local view "kdensity lowess lpoly"
    else if inlist(`"`method'"', "回归诊断图", "reg_diagnostic_graph") local view "rvfplot rvpplot avplot avplots lvr2plot cprplot acprplot"
    else if inlist(`"`method'"', "时间序列图", "ts_graph") local view "tsline"
    else if inlist(`"`method'"', "面板数据折线图", "panel_line_graph") local view "xtline"
    else if inlist(`"`method'"', "生存分析图", "survival_graph") local view "sts"
    else if inlist(`"`method'"', "ROC分析", "roc_graph") local view "roctab rocfit roccomp rocgold rocreg"
    else if inlist(`"`method'"', "多元分析图", "multivariate_graph") local view "pca factor cluster"
    else if inlist(`"`method'"', "质量控制", "quality_graph") local view "cchart pchart rchart xchart shewhart serrbar"
    else if inlist(`"`method'"', "更多统计图形", "more_stat_graph") local view "symplot quantile qnorm pnorm qchi pchi qqplot gladder qladder dotplot spikeplot sunflower marginsplot coefplot event_plot"
    else if inlist(`"`method'"', "图形组合", "graph_combine") local view "graph_combine"
    else if inlist(`"`method'"', "管理图形", "graph_manage") local view "graph"
    else if inlist(`"`method'"', "更改方案/大小", "graph_scheme") local view "graph"

    /* Compatibility aliases used by existing quick-entry cards. */
    else if inlist(`"`method'"', "描述统计", "descriptive") local view "summarize tabstat"
    else if inlist(`"`method'"', "相关分析", "correlation") local view "correlate pwcorr"
    else if inlist(`"`method'"', "均值检验", "mean_test") local view "ttest"
    else if inlist(`"`method'"', "频数列联", "frequency") local view "tabulate"
    else if inlist(`"`method'"', "普通线性回归", "linear_ols") local view "regress"
    else if inlist(`"`method'"', "固定效应线性回归", "linear_fe") local view "reghdfe areg"
    else if inlist(`"`method'"', "稳健与特殊线性回归", "linear_special") local view "rreg cnsreg vwls eivreg"
    else if inlist(`"`method'"', "分位数回归", "linear_quantile") local view "qreg"
    else if inlist(`"`method'"', "时间序列线性回归", "linear_ts") local view "newey prais"
    else if inlist(`"`method'"', "线性模型", "linear") local view "regress reghdfe areg qreg rreg cnsreg vwls eivreg newey prais"
    else if inlist(`"`method'"', "面板模型", "panel") local view "xtreg xtlogit xtprobit"
    else if inlist(`"`method'"', "计数模型", "count") local view "poisson nbreg ppmlhdfe"
    else if inlist(`"`method'"', "工具变量", "iv") local view "ivregress ivreghdfe"
    else if inlist(`"`method'"', "双重差分", "did") {
        if c(stata_version) >= 17 local view "didregress xtdidregress"
        else local view ""
    }
    else if inlist(`"`method'"', "DID分步构建", "did_build", "DID模型构建", "did_model") local view "did_builder"
    else if inlist(`"`method'"', "假设检验", "post_tests") local view "test testparm testnl lrtest hausman"
    else if inlist(`"`method'"', "组合与比较", "post_comparisons") local view "lincom nlcom contrast pwcompare suest"
    else if inlist(`"`method'"', "预测与边际", "post_prediction") local view "predict predictnl margins marginsplot"
    else if inlist(`"`method'"', "模型管理与诊断", "post_manage") local view "estimates estat linktest"
    else if inlist(`"`method'"', "系数检验", "coefficient") local view "test testparm testnl lincom nlcom contrast pwcompare"
    else if inlist(`"`method'"', "预测边际", "prediction") local view "predict predictnl margins marginsplot"
    else if inlist(`"`method'"', "数据分布", "graph_distribution") local view "histogram kdensity graph_box"
    else if inlist(`"`method'"', "变量关系", "graph_relation") local view "scatter lfit twoway"
    else if inlist(`"`method'"', "分组趋势", "graph_trend") local view "did_trends"
    else if inlist(`"`method'"', "回归结果", "graph_estimation") local view "coefplot marginsplot"
    else if inlist(`"`method'"', "平行趋势与动态图", "did_graph", "DID与事件研究", "graph_did") local view "did_trends event_plot"
    else if inlist(`"`method'"', "控制变量组合筛选", "oneclick_screen") local view "oneclick"
    else if inlist(`"`method'"', "控制变量组合稳健性", "oneclick_robustness") local view "oneclick_robustness"

    if `"`method'"' != "" local browser_mode "commands"

    char _dta[hxtoolbox_command_view] `"`view'"'
    char _dta[hxtoolbox_method_view] `"`method_view'"'
    char _dta[hxtoolbox_method_title] `"`method_title'"'
    char _dta[hxtoolbox_method_desc] `"`method_desc'"'
    char _dta[hxtoolbox_browser_mode] `"`browser_mode'"'

    return local commands `"`all_cmds'"'
    return local favorites `"`favorites'"'
    return local recent `"`recentcmds'"'
    return local matches `"`matches'"'
    return local methods `"`method_view'"'
    return local view `"`view'"'
end
