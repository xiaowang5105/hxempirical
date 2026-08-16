from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------- registry ----------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.22  16aug2026", "*! hxregistry 3.1.23  16aug2026", "registry version")
r = once(
    r,
    " signtest test lincom regress ",
    " signtest test testparm testnl lincom nlcom contrast pwcompare predictnl lrtest hausman suest linktest estimates estat regress ",
    "postestimation statistics catalog",
)
r = once(
    r,
    '    local post_cmds "test lincom predict margins"\n',
    '    local post_cmds "test testparm testnl lincom nlcom contrast pwcompare predict predictnl margins lrtest hausman suest linktest estimates estat"\n',
    "post command catalog",
)
r = once(
    r,
    '    local post_methods "系数检验 预测边际"\n',
    '    local post_methods "假设检验 组合与比较 预测与边际 模型管理与诊断"\n',
    "post method groups",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "估计后分析", "postestimation") local view "test lincom predict margins"\n',
    '    else if inlist(`"`method\'"\', "估计后分析", "postestimation") local view "test testparm testnl lincom nlcom contrast pwcompare predict predictnl margins marginsplot lrtest hausman suest linktest estimates estat"\n',
    "Statistics postestimation route",
)
# Add new structured post-method routes while retaining the old aliases below.
compat_anchor = '    else if inlist(`"`method\'"\', "系数检验", "coefficient") local view "test lincom"\n'
new_routes = '''    else if inlist(`"`method'"', "假设检验", "post_tests") local view "test testparm testnl lrtest hausman"
    else if inlist(`"`method'"', "组合与比较", "post_comparisons") local view "lincom nlcom contrast pwcompare suest"
    else if inlist(`"`method'"', "预测与边际", "post_prediction") local view "predict predictnl margins marginsplot"
    else if inlist(`"`method'"', "模型管理与诊断", "post_manage") local view "estimates estat linktest"
'''
r = once(r, compat_anchor, new_routes + compat_anchor, "post compatibility routes")
r = once(
    r,
    '    else if inlist(`"`method\'"\', "系数检验", "coefficient") local view "test lincom"\n',
    '    else if inlist(`"`method\'"\', "系数检验", "coefficient") local view "test testparm testnl lincom nlcom contrast pwcompare"\n',
    "legacy coefficient post route",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "预测边际", "prediction") local view "predict margins"\n',
    '    else if inlist(`"`method\'"\', "预测边际", "prediction") local view "predict predictnl margins marginsplot"\n',
    "legacy prediction post route",
)
keyword_anchor = '        local key_margins "margins 边际效应 调节效应"\n'
keyword_add = '''        local key_testparm "testparm joint Wald parameter terms 联合检验 参数组 因子变量"
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
'''
r = once(r, keyword_anchor, keyword_anchor + keyword_add, "postestimation search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------- semantics ----------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.21  16aug2026", "*! hxsemantics 1.4.22  16aug2026", "semantics version")
# Extend the low-barrier expression pages for general Wald/combinations.
s = once(
    s,
    '    else if inlist("`cmd\'", "test", "lincom", "predict", "margins") {\n',
    '    else if inlist("`cmd\'", "test", "testparm", "testnl", "lincom", "nlcom", "predict", "margins") {\n',
    "post expression command group",
)
test_anchor = '''        if "`cmd'" == "test" {
            local template "expression_body"
            local title "test — 回归系数检验"
            local purpose1 "在回归后检验一个或多个系数是否等于指定值。"
            local purpose2 "可以检验单个系数，也可以联合检验多个系数。"
            local example1 "test x = 0"
            local explain1 "检验 x 的回归系数是否等于 0。"
            local example2 "test x c1 c2"
            local explain2 "联合检验 x、c1、c2 的系数是否都为 0。"
        }
'''
if s.count(test_anchor) != 1:
    raise SystemExit(f"test semantic anchor count={s.count(test_anchor)}")
test_extra = '''        else if "`cmd'" == "testparm" {
            local template "expression_body"
            local title "testparm — 联合检验一组模型项"
            local purpose1 "对一组系数、因子变量 levels 或交互项执行联合 Wald 检验。"
            local purpose2 "特别适合检验 i.group、交互项或一组滞后项是否整体显著。"
            local example1 "testparm i.group"
            local explain1 "联合检验 group 的所有非基准类别系数是否同时为 0。"
            local example2 "testparm c.x#i.group"
            local explain2 "联合检验 x 与 group 的全部交互项。"
        }
        else if "`cmd'" == "testnl" {
            local template "expression_body"
            local title "testnl — 非线性 Wald 假设检验"
            local purpose1 "检验由回归系数组成的非线性约束，并用 delta method 计算 Wald statistic。"
            local purpose2 "表达式直接引用 _b[var] 或 equation-specific coefficient names。"
            local example1 "testnl (_b[x])^2 = 1"
            local explain1 "检验 x 系数平方是否等于 1。"
            local example2 "testnl _b[x1]/_b[x2] = 1"
            local explain2 "检验两个系数之比是否等于 1。"
        }
'''
s = s.replace(test_anchor, test_anchor + test_extra, 1)
lincom_anchor = '''        else if "`cmd'" == "lincom" {
            local template "expression_body"
            local title "lincom — 计算回归系数的线性组合"
            local purpose1 "在回归后计算系数之和、差或其他线性组合，并给出标准误。"
            local purpose2 "表达式中使用回归变量名。"
            local example1 "lincom x + c1"
            local explain1 "计算 x 与 c1 两个系数之和。"
            local example2 "lincom x - c1"
            local explain2 "计算 x 与 c1 两个系数之差。"
        }
'''
if s.count(lincom_anchor) != 1:
    raise SystemExit(f"lincom semantic anchor count={s.count(lincom_anchor)}")
nlcom_block = '''        else if "`cmd'" == "nlcom" {
            local template "expression_body"
            local title "nlcom — 非线性系数组合"
            local purpose1 "计算系数的比率、乘积、转折点等非线性函数，并用 delta method 给出标准误和区间。"
            local purpose2 "表达式通常直接引用 _b[var]；多方程模型应使用 equation-specific coefficient names。"
            local example1 "nlcom (_b[x])^2"
            local explain1 "报告 x 系数平方及其 delta-method 标准误。"
            local example2 "nlcom -_b[x]/(2*_b[c.x#c.x])"
            local explain2 "计算二次项模型的 turning point。"
        }
'''
s = s.replace(lincom_anchor, lincom_anchor + nlcom_block, 1)
# Remaining postestimation commands use their native command bodies.
s = once(
    s,
    " bayes bayesmh bayespredict bayesreps bayesstats bayesgraph bayestest bayesvarstable bayesirf bayesfcast bmacoefsample bmagraph bmastats bmapredict power ",
    " bayes bayesmh bayespredict bayesreps bayesstats bayesgraph bayestest bayesvarstable bayesirf bayesfcast bmacoefsample bmagraph bmastats bmapredict contrast pwcompare predictnl lrtest hausman suest linktest estimates estat power ",
    "postestimation command-body catalog",
)
# Insert specialized native-body semantics before power.
post_marker = '''        else if "`cmd'" == "power" {
'''
if s.count(post_marker) != 1:
    raise SystemExit(f"postestimation insertion marker count={s.count(post_marker)}")
post_blocks = '''        else if "`cmd'" == "contrast" {
            local expr_label "contrast operator + factor variable/interaction + effects/nowald/mcompare() 等"
            local example1 "contrast ar.agegroup, nowald effects"
            local explain1 "对 agegroup 做 reverse-adjacent contrasts，直接比较每一档与前一档的 adjusted linear prediction。"
            local example2 "contrast p.agegroup"
            local explain2 "用 orthogonal polynomial contrasts 检查有序类别的 linear/quadratic/cubic 等趋势。"
        }
        else if "`cmd'" == "pwcompare" {
            local expr_label "factor variable + effects + mcompare() 多重比较校正"
            local example1 "pwcompare agegrp, effects mcompare(tukey)"
            local explain1 "对 agegrp 所有 level 做 pairwise comparisons，并用 Tukey HSD 调整推断。"
            local example2 "help pwcompare"
            local explain2 "Bonferroni、Sidak、Scheffe 等 mcompare() 选择应与预先设定的比较族对应。"
        }
        else if "`cmd'" == "predictnl" {
            local expr_label "新变量 = nonlinear prediction expression + se()/ci()"
            local example1 "predictnl xb2 = predict(xb)^2, se(se_xb2)"
            local explain1 "把 linear prediction 的平方作为非线性预测量，并用 delta method 生成标准误 se_xb2。"
            local example2 "help predictnl"
            local explain2 "expression 可组合 predict()、系数与数据变量；复杂表达式运行前核对当前模型支持的 predict statistic。"
        }
        else if "`cmd'" == "lrtest" {
            local expr_label "受限模型 estimates-name + 非受限模型 estimates-name"
            local example1 "lrtest restricted unrestricted"
            local explain1 "比较两个已保存且使用同一数据/likelihood 的 nested maximum-likelihood models。"
            local example2 "help lrtest"
            local explain2 "LR test 依赖模型嵌套与可比 likelihood；robust/pseudolikelihood 场景应改用适当 Wald 或 score-type 检验。"
        }
        else if "`cmd'" == "hausman" {
            local expr_label "consistent model estimates-name + efficient-under-H0 model estimates-name + sigmamore/sigmaless 等"
            local example1 "hausman fixed random"
            local explain1 "比较已保存的 fixed 与 random effects estimates，检验两组系数系统差异。"
            local example2 "help hausman"
            local explain2 "Hausman 检验需要两组可比估计结果；协方差矩阵差与模型设定应在解释前核对。"
        }
        else if "`cmd'" == "suest" {
            local expr_label "两个或多个 estimates-name + vce()/cluster() 等 stacked sandwich 设定"
            local example1 "suest model1 model2"
            local explain1 "把 model1、model2 的参数向量与 robust covariance 合并，随后可用 test/testnl 做跨模型系数检验。"
            local example2 "help suest"
            local explain2 "先 estimates store 各模型；部分估计器不支持 suest，需要查看对应 postestimation help。"
        }
        else if "`cmd'" == "linktest" {
            local expr_label "模型设定 link test options（通常直接运行）"
            local example1 "linktest"
            local explain1 "在兼容的单方程模型后回归结果对 _hat 与 _hatsq；_hatsq 显著提示函数形式可能遗漏。"
            local example2 "help linktest"
            local explain2 "linktest 是 specification diagnostic，不能替代对理论变量、残差和识别假设的检查。"
        }
        else if "`cmd'" == "estimates" {
            local expr_label "store/restore/table/stats/save/use/replay 等 estimates suite 子命令"
            local example1 "estimates store model1"
            local explain1 "把当前 estimation results 在内存中命名为 model1，供后续比较、预测或检验。"
            local example2 "estimates table model1 model2, b(%9.3f) se"
            local explain2 "把两个已保存模型的 coefficients 与 standard errors 并列表格。"
        }
        else if "`cmd'" == "estat" {
            local expr_label "当前估计器支持的 estat 子命令：ic/vif/gof/hettest/vce/..."
            local example1 "estat ic"
            local explain1 "在支持的 likelihood-based model 后显示 AIC/BIC 等 information criteria。"
            local example2 "estat vce"
            local explain2 "显示当前 coefficient variance–covariance matrix；具体可用 estat 子命令随估计器变化。"
        }
'''
s = s.replace(post_marker, post_blocks + post_marker, 1)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------- permanent static contracts ----------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'bayesian_core = {"bayes", "bayesmh", "bayespredict", "bayesreps", "bayesstats", "bayesgraph", "bayestest"}\n'
checks = '''postestimation_core = {
    "test", "testparm", "testnl", "lincom", "nlcom", "contrast", "pwcompare", "predict", "predictnl", "margins",
    "lrtest", "hausman", "suest", "linktest", "estimates", "estat",
}
missing_post = sorted(postestimation_core - stats_cmds)
if missing_post:
    fail("postestimation command coverage missing: " + ", ".join(missing_post))
post_declared = set(local_words(registry, "post_cmds"))
missing_post_category = sorted(postestimation_core - post_declared)
if missing_post_category:
    fail("post command category missing: " + ", ".join(missing_post_category))
if "假设检验 组合与比较 预测与边际 模型管理与诊断" not in registry:
    fail("task-oriented postestimation method groups missing")
for needle in (
    "testparm i.group",
    "testnl (_b[x])^2 = 1",
    "nlcom (_b[x])^2",
    "contrast ar.agegroup, nowald effects",
    "pwcompare agegrp, effects mcompare(tukey)",
    "predictnl xb2 = predict(xb)^2, se(se_xb2)",
    "lrtest restricted unrestricted",
    "hausman fixed random",
    "suest model1 model2",
    "linktest",
    "estimates store model1",
    "estat ic",
):
    if needle not in semantics:
        fail(f"postestimation semantic contract missing: {needle}")
if "marginsplot" not in graph_cmds:
    fail("marginsplot must remain in Graphics while being reachable from postestimation")

'''
v = once(v, anchor, checks + anchor, "postestimation static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_POSTESTIMATION_PATCH_OK")
