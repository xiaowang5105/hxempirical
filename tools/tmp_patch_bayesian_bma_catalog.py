from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------- registry ----------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.21  16aug2026", "*! hxregistry 3.1.22  16aug2026", "registry version")
r = once(
    r,
    " bayes bayesmh bayespredict bayesstats bayesgraph bmaregress predict margins",
    " bayes bayesmh bayespredict bayesreps bayesstats bayesgraph bayestest bayesvarstable bayesirf bayesfcast bmaregress bmacoefsample bmagraph bmastats bmapredict predict margins",
    "Bayesian and BMA statistics catalog",
)
r = once(
    r,
    "foreach cmd in didregress xtdidregress telasso ziologit xtmlogit stintcox {",
    "foreach cmd in didregress xtdidregress telasso ziologit xtmlogit stintcox bayesvarstable bayesirf bayesfcast {",
    "Stata 17 Bayesian gate",
)
r = once(
    r,
    "foreach cmd in mediate hdidregress xthdidregress bmaregress dtable gsbounds gsdesign ivfprobit ivqregress arimasoc arfimasoc lpirf {",
    "foreach cmd in mediate hdidregress xthdidregress bmaregress bmacoefsample bmagraph bmastats bmapredict dtable gsbounds gsdesign ivfprobit ivqregress arimasoc arfimasoc lpirf {",
    "Stata 18 BMA gate",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "贝叶斯分析", "bayes") local view "bayes bayesmh bayespredict bayesstats bayesgraph"\n',
    '''    else if inlist(`"`method'"', "贝叶斯分析", "bayes") {
        local view "bayes bayesmh bayespredict bayesreps bayesstats bayesgraph bayestest"
        if c(stata_version) >= 17 local view "`view' bayesvarstable bayesirf bayesfcast"
    }
''',
    "Bayesian method route",
)
r = once(
    r,
    '''    else if inlist(`"`method'"', "贝叶斯模型平均", "bma") {
        if c(stata_version) >= 18 local view "bmaregress"
        else local view ""
    }
''',
    '''    else if inlist(`"`method'"', "贝叶斯模型平均", "bma") {
        if c(stata_version) >= 18 local view "bmaregress bmacoefsample bmagraph bmastats bmapredict"
        else local view ""
    }
''',
    "BMA method route",
)
keyword_anchor = '        local key_nptrend "nptrend nonparametric trend Cochran Armitage Jonckheere Terpstra Cuzick 趋势检验 非参数 有序组 exact"\n'
keyword_add = '''        local key_bayestest "bayestest Bayesian hypothesis model comparison interval Bayes factor 贝叶斯 假设检验 模型比较"
        local key_bayesreps "bayesreps Bayesian posterior predictive MCMC replicates 后验预测 复制样本 模型检查"
        local key_bayesvarstable "bayesvarstable Bayesian VAR stability eigenvalue 贝叶斯 VAR 稳定性 特征根"
        local key_bayesirf "bayesirf Bayesian IRF FEVD impulse response 贝叶斯 脉冲响应 方差分解"
        local key_bayesfcast "bayesfcast Bayesian dynamic forecast VAR 贝叶斯 动态预测"
        local key_bmacoefsample "bmacoefsample Bayesian model averaging posterior coefficient sample BMA 系数 后验抽样"
        local key_bmagraph "bmagraph BMA PMP PIP model size variable map coefficient density 模型概率 图"
        local key_bmastats "bmastats BMA posterior inclusion probability PIP model size jointness LPS 统计"
        local key_bmapredict "bmapredict BMA prediction posterior predictive mean credible interval 预测"
'''
r = once(r, keyword_anchor, keyword_anchor + keyword_add, "Bayesian search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------- semantics ----------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.20  16aug2026", "*! hxsemantics 1.4.21  16aug2026", "semantics version")
s = once(
    s,
    " bayes bayesmh bayespredict bayesstats bayesgraph power ",
    " bayes bayesmh bayespredict bayesreps bayesstats bayesgraph bayestest bayesvarstable bayesirf bayesfcast bmacoefsample bmagraph bmastats bmapredict power ",
    "Bayesian command-body catalog",
)
old_post = '''        else if strpos(" bayespredict bayesstats bayesgraph ", " `cmd' ") {
            local expr_label "Bayesian 后估计子命令 / 结果对象与参数"
            local example1 "help `cmd'"
            local explain1 "先确认上一项 Bayesian 估计结果，再按当前后估计命令的子命令语法填写。"
        }
'''
new_post = '''        else if "`cmd'" == "bayespredict" {
            local expr_label "预测结果变量 / 模拟结果对象 + mean/median/saving() 等 posterior-predictive 设定"
            local example1 "bayespredict pmean, mean"
            local explain1 "在上一项 Bayesian 模型后，为每条观测计算 posterior predictive mean 并保存为 pmean。"
            local example2 "help bayespredict"
            local explain2 "完整 MCMC predictions 可保存到独立数据文件；需要可重复结果时显式设置随机数种子。"
        }
        else if "`cmd'" == "bayesreps" {
            local expr_label "新变量前缀 + nreps() + rseed()（MCMC replicated outcomes）"
            local example1 "bayesreps yrep*, nreps(10)"
            local explain1 "从 posterior predictive distribution 随机抽取 10 组 outcome replicates，写入当前数据的 yrep1–yrep10。"
            local example2 "help bayesreps"
            local explain2 "适合快速 posterior predictive model checks；Stata 16+。"
        }
        else if "`cmd'" == "bayesstats" {
            local expr_label "summary/ic/ess/grubin/ppvalues 等 Bayesian 后验统计子命令"
            local example1 "bayesstats summary"
            local explain1 "汇总当前 Bayesian MCMC 样本中的参数后验均值、中位数和 credible intervals。"
            local example2 "help bayesstats"
            local explain2 "模型比较、有效样本量、多链收敛和 posterior predictive p-values 继续按对应子命令设置。"
        }
        else if "`cmd'" == "bayesgraph" {
            local expr_label "diagnostics/trace/ac 等图形子命令 + 参数对象"
            local example1 "bayesgraph diagnostics {inflation:L1.ogap}"
            local explain1 "对指定 Bayesian 参数同时检查 trace、autocorrelation 等 MCMC 诊断图。"
            local example2 "help bayesgraph"
            local explain2 "运行前确认参数名来自当前 Bayesian estimation results。"
        }
        else if "`cmd'" == "bayestest" {
            local expr_label "interval/model 等 Bayesian hypothesis-test 子命令 + 参数或 stored estimates"
            local example1 "bayestest model lag1 lag2 lag3"
            local explain1 "比较已保存的 lag1、lag2、lag3 Bayesian 模型，报告 marginal likelihood 与 posterior model probabilities。"
            local example2 "help bayestest"
            local explain2 "interval 可做区间假设检验；model 比较前必须保存兼容的 Bayesian estimation results。"
        }
        else if "`cmd'" == "bayesvarstable" {
            local expr_label "上一项 bayes: var 的稳定性检验参数（通常可直接运行）"
            local example1 "bayesvarstable"
            local explain1 "检查 Bayesian VAR companion matrix 的 eigenvalue stability，并报告所有根位于单位圆内的 posterior probability。"
            local example2 "help bayesvarstable"
            local explain2 "该入口为 Stata 17+，前一项结果必须来自 bayes: var。"
        }
        else if "`cmd'" == "bayesirf" {
            local expr_label "create/graph/table/cgraph/ograph + IRF 结果集与 impulse/response 设定"
            local example1 "bayesirf create birf, set(birfex)"
            local explain1 "在 Bayesian VAR 或 Bayesian DSGE 后创建 birf，并保存到 birfex.irf。"
            local example2 "bayesirf graph irf, impulse(fedfunds)"
            local explain2 "绘制 fedfunds shock 的 posterior IRF credible bands；Stata 17+。"
        }
        else if "`cmd'" == "bayesfcast" {
            local expr_label "compute/graph + 新变量前缀 + step()/credible interval 等动态预测设定"
            local example1 "bayesfcast compute f_, step(10)"
            local explain1 "在 bayes: var 后生成未来 10 期 Bayesian dynamic forecasts，并以 f_ 为变量名前缀。"
            local example2 "bayesfcast graph f_inflation f_ogap f_fedfunds"
            local explain2 "绘制 posterior dynamic forecasts 及不确定性区间；Stata 17+。"
        }
        else if "`cmd'" == "bmacoefsample" {
            local expr_label "simulate/saving()/rseed() 等 BMA 系数 posterior-sample 设定"
            local example1 "bmacoefsample, rseed(18)"
            local explain1 "在 bmaregress 后模拟 regression coefficients 的 posterior sample，供 credible intervals 和后续 Bayesian summaries 使用。"
            local example2 "bmacoefsample, saving(bmacoef)"
            local explain2 "把 BMA 参数 posterior sample 保存为 bmacoef.dta；Stata 18+。"
        }
        else if "`cmd'" == "bmagraph" {
            local expr_label "pmp/msize/varmap/coefdensity 等 BMA 图形子命令"
            local example1 "bmagraph pmp"
            local explain1 "绘制 posterior model probabilities，查看模型空间中的主要高概率模型。"
            local example2 "bmagraph msize"
            local explain2 "绘制 posterior model-size distribution；Stata 18+。"
        }
        else if "`cmd'" == "bmastats" {
            local expr_label "models/msize/pip/jointness/lps 等 BMA 统计子命令"
            local example1 "bmastats pip"
            local explain1 "报告候选 predictors 的 posterior inclusion probabilities。"
            local example2 "bmastats models"
            local explain2 "汇总 posterior model probabilities 与变量包含情况；Stata 18+。"
        }
        else if "`cmd'" == "bmapredict" {
            local expr_label "新预测变量 + mean/cri 等 BMA posterior-predictive 设定"
            local example1 "bmapredict pmean, mean"
            local explain1 "计算包含 model uncertainty 的 BMA posterior predictive mean。"
            local example2 "bmapredict cri_l cri_u, cri rseed(18)"
            local explain2 "生成 posterior predictive credible interval 上下界；需要可用的 BMA posterior sample。"
        }
'''
s = once(s, old_post, new_post, "Bayesian specialized semantics")
s = once(
    s,
    '    else if strpos(" bayes bayesmh bayespredict bayesstats bayesgraph ", " `cmd\' ") {\n',
    '    else if strpos(" bayes bayesmh bayespredict bayesreps bayesstats bayesgraph bayestest bayesvarstable bayesirf bayesfcast ", " `cmd\' ") {\n',
    "Bayesian family copy",
)
s = once(
    s,
    '    else if "`cmd\'" == "bmaregress" {\n        local title "bmaregress — 贝叶斯模型平均线性回归"\n        local purpose1 "用于在线性回归候选模型之间进行贝叶斯模型平均并反映模型不确定性。"\n        local purpose2 "候选变量、always/group、模型先验和 g-prior 会影响结果，运行前应明确模型空间。"\n    }\n',
    '    else if strpos(" bmaregress bmacoefsample bmagraph bmastats bmapredict ", " `cmd\' ") {\n        local title "`cmd\' — 贝叶斯模型平均"\n        local purpose1 "用于 BMA 线性回归、posterior coefficient sampling、模型概率/变量包含诊断与 model-averaged prediction。"\n        local purpose2 "这些入口都属于 Stata 18+；先完成 bmaregress，再按当前后估计任务选择 sampling、graph、stats 或 predict。"\n    }\n',
    "BMA family copy",
)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------- permanent static contracts ----------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'dsge_core = {"dsge", "dsgenl"}\n'
checks = '''bayesian_core = {"bayes", "bayesmh", "bayespredict", "bayesreps", "bayesstats", "bayesgraph", "bayestest"}
missing_bayes = sorted(bayesian_core - stats_cmds)
if missing_bayes:
    fail("Bayesian core command coverage missing: " + ", ".join(missing_bayes))
bayes17 = {"bayesvarstable", "bayesirf", "bayesfcast"}
missing_bayes17 = sorted(bayes17 - stats_cmds)
if missing_bayes17:
    fail("Stata 17 Bayesian VAR postestimation missing: " + ", ".join(missing_bayes17))
if "stintcox bayesvarstable bayesirf bayesfcast" not in registry:
    fail("Stata 17 Bayesian VAR commands missing from version gate")
bma18 = {"bmaregress", "bmacoefsample", "bmagraph", "bmastats", "bmapredict"}
missing_bma = sorted(bma18 - stats_cmds)
if missing_bma:
    fail("Stata 18 BMA workflow missing: " + ", ".join(missing_bma))
if "bmaregress bmacoefsample bmagraph bmastats bmapredict" not in registry:
    fail("Stata 18 BMA commands missing from version gate or method route")
if "bayesselect" in stats_cmds:
    fail("post-Stata-18 bayesselect must not leak into the Stata 16-18 catalog")
for needle in (
    "bayespredict pmean, mean",
    "bayesreps yrep*, nreps(10)",
    "bayesstats summary",
    "bayesgraph diagnostics {inflation:L1.ogap}",
    "bayestest model lag1 lag2 lag3",
    "bayesvarstable",
    "bayesirf create birf, set(birfex)",
    "bayesirf graph irf, impulse(fedfunds)",
    "bayesfcast compute f_, step(10)",
    "bayesfcast graph f_inflation f_ogap f_fedfunds",
    "bmacoefsample, rseed(18)",
    "bmagraph pmp",
    "bmastats pip",
    "bmapredict pmean, mean",
):
    if needle not in semantics:
        fail(f"Bayesian/BMA semantic contract missing: {needle}")

'''
v = once(v, anchor, checks + anchor, "Bayesian BMA static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_BAYESIAN_BMA_PATCH_OK")
