from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------- registry ----------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.16  16aug2026", "*! hxregistry 3.1.17  16aug2026", "registry version")
old_ts_catalog = "heckpoisson arima newey prais arch ucm dfuller pperron corrgram pergram var svar vec varsoc vargranger varstable irf spregress"
new_ts_catalog = "heckpoisson arima arfima arimasoc arfimasoc newey prais arch ucm mswitch threshold dfgls dfuller pperron corrgram cumsp pergram wntestb wntestq psdensity rolling forecast tsappend tsfill tsfilter tsreport tssmooth var svar vec varbasic varsoc vargranger varlmar varnorm varstable varwle vecrank veclmar vecnorm vecstable irf lpirf mgarch dfactor sspace xcorr spregress"
r = once(r, old_ts_catalog, new_ts_catalog, "time-series statistics catalog")

# Stata 18 additions in the time-series family.
r = once(
    r,
    "foreach cmd in mediate hdidregress xthdidregress bmaregress dtable gsbounds gsdesign ivfprobit ivqregress {",
    "foreach cmd in mediate hdidregress xthdidregress bmaregress dtable gsbounds gsdesign ivfprobit ivqregress arimasoc arfimasoc lpirf {",
    "Stata 18 time-series version gate",
)

r = once(
    r,
    '    else if inlist(`"`method\'"\', "时间序列", "time_series") local view "arima newey prais arch ucm dfuller pperron corrgram pergram"\n',
    '''    else if inlist(`"`method'"', "时间序列", "time_series") {
        local view "arima arfima"
        if c(stata_version) >= 18 local view "`view' arimasoc arfimasoc"
        local view "`view' newey prais arch ucm mswitch threshold dfgls dfuller pperron corrgram cumsp pergram wntestb wntestq"
        local view "`view' psdensity rolling forecast tsappend tsfill tsfilter tsreport tssmooth"
    }
''',
    "time-series method route",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "多元时间序列", "multivariate_ts") local view "var svar vec varsoc vargranger varstable irf"\n',
    '''    else if inlist(`"`method'"', "多元时间序列", "multivariate_ts") {
        local view "var svar vec varbasic varsoc vargranger varlmar varnorm varstable varwle vecrank veclmar vecnorm vecstable irf"
        if c(stata_version) >= 18 local view "`view' lpirf"
        local view "`view' mgarch dfactor sspace xcorr"
    }
''',
    "multivariate time-series method route",
)

keyword_anchor = '        local key_xtset "xtset panel data 面板 设置 个体 时间"\n'
keyword_add = '''        local key_arfima "arfima long memory fractional integration 长记忆 分数差分 时间序列"
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
'''
r = once(r, keyword_anchor, keyword_anchor + keyword_add, "time-series search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------- semantics ----------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.15  16aug2026", "*! hxsemantics 1.4.16  16aug2026", "semantics version")

old_body = " stset streg stintreg stintcox stcrreg arima arch ucm dfuller pperron corrgram pergram var svar vec varsoc vargranger varstable spregress "
new_body = " stset streg stintreg stintcox stcrreg arima arfima arimasoc arfimasoc arch ucm mswitch threshold dfgls dfuller pperron corrgram cumsp pergram wntestb wntestq psdensity rolling forecast tsappend tsfill tsfilter tsreport tssmooth var svar vec varbasic varsoc vargranger varlmar varnorm varstable varwle vecrank veclmar vecnorm vecstable irf lpirf mgarch dfactor sspace xcorr spregress "
s = once(s, old_body, new_body, "time-series command-body catalog")

marker = '''        else if "`cmd'" == "teffects" {
'''
if s.count(marker) != 1:
    raise SystemExit(f"time-series semantic insertion marker count={s.count(marker)}")
blocks = '''        else if "`cmd'" == "arfima" {
            local expr_label "时间序列 Y + AR/MA 阶数（分数差分参数 d 由模型估计）"
            local example1 "arfima y, ar(1) ma(1)"
            local explain1 "为长记忆过程拟合 ARFIMA，并同时允许短记忆 AR(1) 与 MA(1) 动态。"
            local example2 "help arfima"
            local explain2 "ARFIMA 适用于自相关缓慢衰减的长记忆序列；运行前先 tsset。"
        }
        else if inlist("`cmd'", "arimasoc", "arfimasoc") {
            local expr_label "时间序列 Y + maxar() + maxma() 候选最大阶数"
            local example1 "`cmd' ogap, maxar(4) maxma(3)"
            local explain1 "比较候选 ARMA/ARFIMA 规格并报告 AIC、BIC、HQIC；该入口仅在 Stata 18+ 展示。"
            local example2 "help `cmd'"
            local explain2 "信息准则用于辅助选择动态阶数，最终模型仍需结合残差诊断与经济机制。"
        }
        else if "`cmd'" == "mswitch" {
            local expr_label "dr/ar 模型类型 + Y + X + switch()/varswitch 等状态切换设定"
            local example1 "mswitch dr fedfunds"
            local explain1 "拟合两状态 Markov-switching dynamic regression，状态间允许参数随隐含 regime 转换。"
            local example2 "help mswitch"
            local explain2 "需要自回归状态过程时使用 ar；switch() 与 varswitch 用于指定哪些参数跨状态变化。"
        }
        else if "`cmd'" == "threshold" {
            local expr_label "Y + threshvar() + regionvars() + nthresholds()/optthresh()"
            local example1 "threshold pollution, threshvar(hour) regionvars(oldbus newbus car)"
            local explain1 "自动估计 hour 的门槛，使 oldbus/newbus/car 的系数在门槛两侧不同。"
            local example2 "help threshold"
            local explain2 "可指定或选择多个 threshold；AIC/BIC/HQIC 与研究机制共同决定状态数。"
        }
        else if "`cmd'" == "dfgls" {
            local expr_label "时间序列变量 + maxlag()/trend 等 DF-GLS 单位根设定"
            local example1 "dfgls y"
            local explain1 "对 y 执行 Elliott–Rothenberg–Stock DF-GLS 单位根检验。"
            local example2 "help dfgls"
            local explain2 "趋势项与最大滞后选择会影响检验；运行前先确认序列频率和 tsset。"
        }
        else if inlist("`cmd'", "wntestb", "wntestq") {
            local expr_label "要检验的时间序列 + lag 等检验设定"
            local example1 "`cmd' y"
            local explain1 "检验 y 是否可视为白噪声；wntestb 基于 Bartlett periodogram，wntestq 使用 portmanteau Q。"
            local example2 "help `cmd'"
            local explain2 "白噪声检验常用于模型前识别或残差诊断，滞后阶数应与数据频率匹配。"
        }
        else if "`cmd'" == "cumsp" {
            local expr_label "时间序列变量（累计谱分布图）"
            local example1 "cumsp y"
            local explain1 "绘制 y 的累计谱分布，用于观察频域能量是否集中在特定频率。"
            local example2 "help cumsp"
            local explain2 "适合与 periodogram 和白噪声检验配合进行频域诊断。"
        }
        else if "`cmd'" == "psdensity" {
            local expr_label "频率新变量 + 谱密度新变量（在 arima/arfima/ucm 后运行）"
            local example1 "psdensity omega density"
            local explain1 "根据上一项 ARIMA、ARFIMA 或 UCM 估计生成参数化谱密度。"
            local example2 "help psdensity"
            local explain2 "这是模型后频域分析入口，必须先存在兼容的时间序列估计结果。"
        }
        else if "`cmd'" == "rolling" {
            local expr_label "要保存的统计量 + window()/recursive + : 后估计命令"
            local example1 "rolling _b, window(20) saving(roll, replace): regress y x"
            local explain1 "用 20 期滚动窗口重复 regress y x，并保存各窗口系数。"
            local example2 "help rolling"
            local explain2 "rolling 会生成结果数据文件；window、step 和 recursive 应与研究的实时信息集一致。"
        }
        else if "`cmd'" == "forecast" {
            local expr_label "forecast 子命令与参数（create / estimates / identity / exogenous / solve 等）"
            local example1 "forecast create model"
            local explain1 "先创建 forecast model；随后逐步加入估计结果、恒等式和外生变量。"
            local example2 "forecast solve"
            local explain2 "完成模型定义后求解静态或动态预测；复杂多方程预测保留原生 suite 工作流。"
        }
        else if "`cmd'" == "tsappend" {
            local expr_label "add() / last() 等追加时间范围"
            local example1 "tsappend, add(12)"
            local explain1 "在时间序列末尾新增 12 期空观测，常用于生成未来期预测。"
            local example2 "help tsappend"
            local explain2 "该命令会增加内存中的观测数；运行前确认当前 tsset 频率与样本末期。"
        }
        else if "`cmd'" == "tsfill" {
            local expr_label "填补时间轴缺口；面板数据可按当前 tsset/xtset 结构补齐"
            local example1 "tsfill"
            local explain1 "为当前时间轴中的缺失期间添加空观测，使时间索引连续。"
            local example2 "help tsfill"
            local explain2 "新增观测中的业务变量通常仍为缺失值；补齐时间索引后还需决定如何处理这些缺失。"
        }
        else if "`cmd'" == "tsfilter" {
            local expr_label "滤波器 hp/bk/cf/bw + 新变量 = 原序列 + smooth()/maxperiod() 等参数"
            local example1 "tsfilter hp y_cycle = y, smooth(1600)"
            local explain1 "使用 Hodrick–Prescott filter 从季度序列 y 中提取周期成分 y_cycle。"
            local example2 "help tsfilter"
            local explain2 "HP、BK、CF、Butterworth 的边界与频率响应不同，应按数据频率和研究目标选型。"
        }
        else if "`cmd'" == "tsreport" {
            local expr_label "时间序列结构报告 options（通常可直接运行）"
            local example1 "tsreport"
            local explain1 "报告时间范围、缺口、重复/不连续时间等当前 time-series 数据结构信息。"
            local example2 "help tsreport"
            local explain2 "适合在 ARIMA、滤波、单位根等正式分析前检查时间轴质量。"
        }
        else if "`cmd'" == "tssmooth" {
            local expr_label "平滑方法 + 新变量 = 原序列 + window()/parms() 等参数"
            local example1 "tssmooth ma y_ma = y, window(2 1 2)"
            local explain1 "生成 y 的中心移动平均平滑序列 y_ma。"
            local example2 "help tssmooth"
            local explain2 "还可使用 exponential、dexponential、Holt–Winters seasonal/nonseasonal 等平滑方法。"
        }
        else if "`cmd'" == "varbasic" {
            local expr_label "内生变量列表 + lags()/step() 等快速 VAR/IRF 设置"
            local example1 "varbasic y1 y2"
            local explain1 "快速拟合基础 VAR，并生成常用 IRF/FEVD 结果，适合探索性分析。"
            local example2 "help varbasic"
            local explain2 "正式研究通常进一步使用 var + irf suite 明确滞后、识别和结果文件。"
        }
        else if strpos(" varlmar varnorm varwle veclmar vecnorm vecstable ", " `cmd' ") {
            local expr_label "上一项 VAR/VEC 模型的后估计检验参数（多数可直接运行）"
            local example1 "`cmd'"
            local explain1 "对上一项 VAR/VEC 结果执行对应的残差、自相关、正态性、稳定性或 lag-exclusion 诊断。"
            local example2 "help `cmd'"
            local explain2 "先确认当前 e() 结果来自兼容的 VAR/VEC 模型。"
        }
        else if "`cmd'" == "vecrank" {
            local expr_label "协整变量列表 + lags()/trend() 等 Johansen rank-test 设定"
            local example1 "vecrank y1 y2"
            local explain1 "使用 Johansen 方法估计 y1、y2 的 cointegrating rank，为后续 vec 规格提供依据。"
            local example2 "help vecrank"
            local explain2 "滞后阶数、确定性趋势与样本区间都会改变 rank test 的结论。"
        }
        else if "`cmd'" == "lpirf" {
            local expr_label "响应变量列表 + lags() + exog() 等 local-projection IRF 设定"
            local example1 "lpirf indpro inflation, lags(1/12) exog(L(0/12).money_shock)"
            local explain1 "直接用 local projections 估计工业产出和通胀对外生货币冲击的动态响应；Stata 18+。"
            local example2 "help lpirf"
            local explain2 "估计后继续用 irf create / graph / table 保存和比较 impulse responses。"
        }
        else if "`cmd'" == "mgarch" {
            local expr_label "ccc/dcc/vcc/dvech + 多元均值方程 + arch()/garch()/distribution()"
            local example1 "mgarch dcc (toyota honda =), arch(1) garch(1) distribution(t)"
            local explain1 "拟合两资产收益的 DCC-MGARCH，并允许条件相关随时间变化。"
            local example2 "help mgarch"
            local explain2 "CCC/DCC/VCC/dvech 对协方差动态施加不同结构，不能按普通多元回归解释。"
        }
        else if "`cmd'" == "dfactor" {
            local expr_label "观测方程 + 潜在动态因子方程"
            local example1 "dfactor (D.(ipman income hours unemp) =, noconstant) (f=, ar(1/2)), nolog"
            local explain1 "用一个 AR(2) 潜在因子解释四个宏观序列的一阶差分共同波动。"
            local example2 "help dfactor"
            local explain2 "观测方程与 factor 的 VAR/AR 动态都属于模型主体，应直接保留原生方程语法。"
        }
        else if "`cmd'" == "sspace" {
            local expr_label "状态方程 + 观测方程 + covariance/error-form 约束"
            local example1 "help sspace"
            local explain1 "state-space 语法需要同时定义不可观测 state 与观测方程；页面保留完整原生方程主体。"
            local example2 "predict statehat, states"
            local explain2 "估计完成后可预测不可观测状态，再用 tsline 检查动态路径。"
        }
        else if "`cmd'" == "xcorr" {
            local expr_label "两个时间序列 + lag() 等 cross-correlogram 设定"
            local example1 "xcorr y x"
            local explain1 "计算并绘制 y 与 x 在不同领先/滞后期的交叉相关。"
            local example2 "help xcorr"
            local explain2 "交叉相关主要用于动态先后关系探索，不能单独建立因果识别。"
        }
'''
s = s.replace(marker, blocks + marker, 1)

# Expand the existing family-level copy for titles/purpose.
s = once(
    s,
    '    else if strpos(" arima arch ucm ", " `cmd\' ") {\n',
    '    else if strpos(" arima arfima arimasoc arfimasoc arch ucm mswitch threshold dfgls dfuller pperron corrgram cumsp pergram wntestb wntestq psdensity rolling forecast tsappend tsfill tsfilter tsreport tssmooth ", " `cmd\' ") {\n',
    "univariate time-series family copy",
)
s = once(
    s,
    '        local purpose1 "用于 ARIMA、ARCH/GARCH 或不可观测成分等时间序列建模。"\n',
    '        local purpose1 "用于 ARIMA/ARFIMA、波动率、状态转换、门槛、单位根/白噪声、频域、滚动估计、滤波平滑与预测工作流。"\n',
    "univariate time-series purpose",
)
s = once(
    s,
    '    else if strpos(" var svar vec varsoc vargranger varstable irf ", " `cmd\' ") {\n',
    '    else if strpos(" var svar vec varbasic varsoc vargranger varlmar varnorm varstable varwle vecrank veclmar vecnorm vecstable irf lpirf mgarch dfactor sspace xcorr ", " `cmd\' ") {\n',
    "multivariate time-series family copy",
)
s = once(
    s,
    '        local purpose1 "用于 VAR/SVAR/VEC、滞后阶数选择、Granger 检验、稳定性或脉冲响应分析。"\n',
    '        local purpose1 "用于 VAR/SVAR/VEC、协整秩与系统诊断、local projections、MGARCH、动态因子、状态空间和脉冲响应分析。"\n',
    "multivariate time-series purpose",
)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------- permanent static contracts ----------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'panel_round2_core = {\n'
checks = '''time_series_core = {
    "arima", "arfima", "newey", "prais", "arch", "ucm", "mswitch", "threshold", "dfgls", "dfuller", "pperron",
    "corrgram", "cumsp", "pergram", "wntestb", "wntestq", "psdensity", "rolling", "forecast", "tsappend", "tsfill",
    "tsfilter", "tsreport", "tssmooth",
}
missing_ts = sorted(time_series_core - stats_cmds)
if missing_ts:
    fail("univariate time-series commands missing: " + ", ".join(missing_ts))
multivariate_ts_core = {
    "var", "svar", "vec", "varbasic", "varsoc", "vargranger", "varlmar", "varnorm", "varstable", "varwle",
    "vecrank", "veclmar", "vecnorm", "vecstable", "irf", "mgarch", "dfactor", "sspace", "xcorr",
}
missing_mvts = sorted(multivariate_ts_core - stats_cmds)
if missing_mvts:
    fail("multivariate time-series commands missing: " + ", ".join(missing_mvts))
for stata18_ts in ("arimasoc", "arfimasoc", "lpirf"):
    if stata18_ts not in stats_cmds:
        fail(f"Stata 18 time-series command missing: {stata18_ts}
")
if "arimasoc arfimasoc lpirf" not in registry:
    fail("Stata 18 time-series version gate missing arimasoc/arfimasoc/lpirf")
for needle in (
    'arfima y, ar(1) ma(1)',
    "arimasoc ogap, maxar(4) maxma(3)",
    "mswitch dr fedfunds",
    "threshold pollution, threshvar(hour) regionvars(oldbus newbus car)",
    "dfgls y",
    "wntestq y",
    "rolling _b, window(20) saving(roll, replace): regress y x",
    "forecast create model",
    "tsappend, add(12)",
    "tsfilter hp y_cycle = y, smooth(1600)",
    "tssmooth ma y_ma = y, window(2 1 2)",
    "vecrank y1 y2",
    "lpirf indpro inflation, lags(1/12) exog(L(0/12).money_shock)",
    "mgarch dcc (toyota honda =), arch(1) garch(1) distribution(t)",
    "dfactor (D.(ipman income hours unemp) =, noconstant) (f=, ar(1/2)), nolog",
    "xcorr y x",
):
    if needle not in semantics:
        fail(f"time-series semantic contract missing: {needle}")

'''
v = once(v, anchor, checks + anchor, "time-series static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_TIMESERIES_CATALOG_PATCH_OK")
