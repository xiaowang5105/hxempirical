from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------------- registry ----------------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.4  16aug2026", "*! hxregistry 3.1.5  16aug2026", "registry version")
r = once(
    r,
    "lasso elasticnet sqrtlasso dsregress poivregress xporegress xpoivregress meta",
    "lasso elasticnet sqrtlasso poregress pologit popoisson dsregress dslogit dspoisson poivregress xporegress xpologit xpopoisson xpoivregress telasso meta",
    "stats lasso catalog",
)
r = once(
    r,
    '    if c(stata_version) < 18 {\n        local stats_cmds : subinstr local stats_cmds " bmaregress" "", all\n    }\n',
    '    if c(stata_version) < 17 {\n        local stats_cmds : subinstr local stats_cmds " telasso" "", all\n    }\n    if c(stata_version) < 18 {\n        local stats_cmds : subinstr local stats_cmds " bmaregress" "", all\n    }\n',
    "stata version gates",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "因果推断/处理效应", "causal_treatment") local view "teffects etregress etpoisson didregress xtdidregress"\n',
    '    else if inlist(`"`method\'"\', "因果推断/处理效应", "causal_treatment") {\n        local view "teffects etregress etpoisson didregress xtdidregress"\n        if c(stata_version) >= 17 local view "`view\' telasso"\n    }\n',
    "causal method",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "Lasso回归", "lasso") local view "lasso elasticnet sqrtlasso dsregress poivregress xporegress xpoivregress"\n',
    '    else if inlist(`"`method\'"\', "Lasso回归", "lasso") local view "lasso elasticnet sqrtlasso poregress pologit popoisson dsregress dslogit dspoisson poivregress xporegress xpologit xpopoisson xpoivregress"\n',
    "lasso method",
)
search_anchor = '        local key_ppmlhdfe "ppmlhdfe poisson pseudo maximum likelihood fixed effects 泊松 伪极大似然 高维固定效应"\n'
search_add = '''        local key_sqrtlasso "sqrtlasso square root lasso 平方根 lasso 高维 变量选择"
        local key_poregress "poregress partialing out lasso linear 高维 推断 部分化 线性回归"
        local key_pologit "pologit partialing out lasso logit 高维 推断 二元"
        local key_popoisson "popoisson partialing out lasso poisson 高维 推断 计数"
        local key_dslogit "dslogit double selection lasso logit 双重选择 高维 二元"
        local key_dspoisson "dspoisson double selection lasso poisson 双重选择 高维 计数"
        local key_xpologit "xpologit cross fit partialing out lasso logit 交叉拟合 高维 二元"
        local key_xpopoisson "xpopoisson cross fit partialing out lasso poisson 交叉拟合 高维 计数"
        local key_telasso "telasso treatment effects lasso 处理效应 高维 因果推断"
'''
r = once(r, search_anchor, search_anchor + search_add, "lasso search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------------- semantics ----------------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.3  16aug2026", "*! hxsemantics 1.4.4  16aug2026", "semantics version")
s = once(
    s,
    " mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm lasso elasticnet npregress ",
    " mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm lasso elasticnet poregress pologit popoisson dslogit dspoisson xpologit xpopoisson telasso npregress ",
    "command-body additions",
)
s = once(
    s,
    '            local example2 "help gsem"\n            local explain2 "多层、潜在类别、选择模型等 gsem 结构差异很大，复杂模型继续按当前 help 核对。"\n',
    '            local example2 "gsem (alcohol truant weapon theft vandalism <-), logit lclass(C 3)"\n            local explain2 "LCA 使用 gsem 的 lclass()；这里拟合 3 个潜在类别的二元题项模型。"\n',
    "gsem LCA example",
)
lasso_block = '''        else if inlist("`cmd'", "lasso", "elasticnet") {
            local expr_label "模型类型 + 因变量 + 候选变量（如 linear y x1-x100）"
            local example1 "`cmd' linear y x1-x100"
            local explain1 "lasso / elasticnet 在因变量前需要明确 linear、logit、probit、poisson 或 cox 等模型类型。"
        }
'''
new_lasso_block = lasso_block + '''        else if strpos(" poregress pologit popoisson dslogit dspoisson xpologit xpopoisson ", " `cmd' ") {
            local expr_label "Y + 关注变量 + controls() 高维候选控制"
            local example1 "`cmd' y d1, controls(x1-x100)"
            if strpos(" poregress pologit popoisson ", " `cmd' ") {
                local explain1 "Partialing-out Lasso：d1 是关注变量，controls() 中的高维候选控制由 lasso 选择并部分化。"
            }
            else if strpos(" dslogit dspoisson ", " `cmd' ") {
                local explain1 "Double-selection Lasso：分别围绕结果与关注变量选择 controls()，再对 d1 做有效推断。"
            }
            else {
                local explain1 "Cross-fit partialing-out Lasso：用交叉拟合降低高维 nuisance 模型过拟合对 d1 推断的影响。"
            }
            local example2 "help `cmd'"
            local explain2 "模型分布、选择方法、聚类和交叉拟合设置按当前 Stata 版本继续核对。"
        }
        else if "`cmd'" == "telasso" {
            local expr_label "(结果变量 + 高维结果模型控制) + (处理变量 + 高维处理模型控制)"
            local example1 "telasso (y x1-x100) (treat w1-w100)"
            local explain1 "第一组括号是结果模型，第二组是处理分配模型；lasso 在两组高维候选控制中选择变量。"
            local example2 "telasso (y x1-x100) (treat w1-w100), atet"
            local explain2 "加 atet 后估计已接受处理者的平均处理效应。"
        }
'''
s = once(s, lasso_block, new_lasso_block, "lasso command-body semantics")

family_old = '''    else if strpos(" lasso elasticnet sqrtlasso dsregress poivregress xporegress xpoivregress ", " `cmd' ") {
        local title "`cmd' — Lasso 与高维变量选择"
        local purpose1 "用于高维协变量下的正则化、双重选择或部分线性/工具变量估计。"
        local purpose2 "结果变量、候选变量和惩罚/选择规则应结合具体方法设置；运行前核对模型目标与推断口径。"
    }
'''
family_new = '''    else if "`cmd'" == "sqrtlasso" {
        local title "sqrtlasso — Square-root Lasso"
        local purpose1 "对连续结果进行 Square-root Lasso 预测与变量选择；它只对应线性结果模型。"
        local purpose2 "直接选择结果变量和候选预测变量，无需像 lasso / elasticnet 那样在因变量前填写 linear。"
        local has_depvar 1
        local has_varlist 1
        local dep_label "连续结果变量 Y"
        local vars_label "候选预测变量"
        local example1 "sqrtlasso y x1-x1000"
        local explain1 "官方基础语法：对连续结果 y 在 x1 到 x1000 中进行 Square-root Lasso 选择。"
        local example2 "help sqrtlasso"
        local explain2 "惩罚参数选择、聚类等设置按当前 Stata 版本核对。"
    }
    else if strpos(" lasso elasticnet poregress pologit popoisson dsregress dslogit dspoisson poivregress xporegress xpologit xpopoisson xpoivregress ", " `cmd' ") {
        local title "`cmd' — Lasso 与高维变量选择"
        local purpose1 "用于高维协变量下的正则化、双重选择、部分化或交叉拟合推断。"
        local purpose2 "先区分关注变量和 controls() 高维候选控制；预测型 lasso / elasticnet 还需要在因变量前明确模型类型。"
    }
'''
s = once(s, family_old, family_new, "sqrtlasso/family semantics")
s = once(
    s,
    '    else if strpos(" teffects etregress etpoisson ", " `cmd\' ") {\n',
    '    else if strpos(" teffects etregress etpoisson telasso ", " `cmd\' ") {\n',
    "causal family title",
)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------------- static contracts ----------------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''for official in ("eregress", "eintreg", "eprobit", "eoprobit"):
    if official not in stats_cmds:
        fail(f"official extended-regression command missing: {official}")
'''
extra = '''
lasso_official = {
    "lasso", "elasticnet", "sqrtlasso",
    "poregress", "pologit", "popoisson", "poivregress",
    "dsregress", "dslogit", "dspoisson",
    "xporegress", "xpologit", "xpopoisson", "xpoivregress",
}
missing_lasso = sorted(lasso_official - stats_cmds)
if missing_lasso:
    fail("official Lasso commands missing from Statistics catalog: " + ", ".join(missing_lasso))
if "telasso" not in stats_cmds:
    fail("official telasso treatment-effects command missing from Statistics catalog")
for needle in (
    'sqrtlasso y x1-x1000',
    '`cmd\' y d1, controls(x1-x100)',
    'telasso (y x1-x100) (treat w1-w100)',
    'gsem (alcohol truant weapon theft vandalism <-), logit lclass(C 3)',
):
    if needle not in semantics:
        fail(f"Lasso/LCA semantic contract missing: {needle}")
'''
v = once(v, anchor, anchor + extra, "static Lasso completeness")
v = v.replace(
    '"legacy_did_hidden=1 event_plot_graph=1 official_did_stats=1 epoisson_removed=1 longtail_semantics=1 docs_source_split=1"',
    '"legacy_did_hidden=1 event_plot_graph=1 official_did_stats=1 epoisson_removed=1 longtail_semantics=1 lasso_catalog=1 lca_example=1 docs_source_split=1"',
)
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_LASSO_CATALOG_PATCH_OK")
