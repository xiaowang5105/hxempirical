from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------------- registry ----------------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.10  16aug2026", "*! hxregistry 3.1.11  16aug2026", "registry version")
r = once(
    r,
    "regress areg reghdfe cnsreg rreg qreg iqreg bsqreg vwls eivreg sureg mvreg correlate pwcorr",
    "regress areg reghdfe cnsreg rreg hetregress qreg iqreg bsqreg sqreg vwls eivreg intreg tobit truncreg boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate pwcorr",
    "linear catalog",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "线性模型及相关", "linear_related") local view "regress areg reghdfe cnsreg rreg qreg iqreg bsqreg vwls eivreg sureg mvreg correlate pwcorr"\n',
    '    else if inlist(`"`method\'"\', "线性模型及相关", "linear_related") local view "regress areg reghdfe cnsreg rreg hetregress qreg iqreg bsqreg sqreg vwls eivreg intreg tobit truncreg boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate pwcorr"\n',
    "linear method view",
)
anchor = '        local key_regress "regress ols linear regression 线性回归 最小二乘 基准回归 普通回归 稳健标准误 聚类"\n'
add = '''        local key_hetregress "hetregress heteroskedastic linear regression 异方差 线性回归 方差方程 het"
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
'''
r = once(r, anchor, anchor + add, "linear search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------------- semantics ----------------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.9  16aug2026", "*! hxsemantics 1.4.10  16aug2026", "semantics version")
s = once(
    s,
    " cc cs ir mcc dstdize sureg mvreg canon",
    " cc cs ir mcc dstdize hetregress sqreg intreg tobit truncreg boxcox fp nl nlsur gmm sureg reg3 mvreg frontier canon",
    "linear command-body catalog",
)

marker = '''        else if strpos(" sureg mvreg canon manova ", " `cmd' ") {
'''
if s.count(marker) != 1:
    raise SystemExit(f"system-model marker count={s.count(marker)}")
linear_blocks = '''        else if "`cmd'" == "hetregress" {
            local expr_label "Y + X + het() 方差方程 + ML/twostep 等估计设定"
            local example1 "hetregress y x1 x2, het(z1 z2)"
            local explain1 "均值方程用 x1、x2，het() 中 z1、z2 建模残差方差。"
            local example2 "help hetregress"
            local explain2 "方差方程是否合理直接影响效率与推断；可按研究设计选择 ML 或 two-step GLS。"
        }
        else if "`cmd'" == "sqreg" {
            local expr_label "Y + X + quantiles() + reps() 等同时分位数设定"
            local example1 "sqreg y x1 x2, quantile(.25 .5 .75) reps(100)"
            local explain1 "同时估计第 25、50、75 百分位，并用 bootstrap 得到跨分位数协方差。"
            local example2 "help sqreg"
            local explain2 "适合需要正式比较不同分位点系数的场景。"
        }
        else if "`cmd'" == "intreg" {
            local expr_label "结果下界 + 结果上界 + X"
            local example1 "intreg ylower yupper x1 x2"
            local explain1 "ylower、yupper 表示区间结果的下界和上界；相等可表示精确观测，缺失可表示单侧删失。"
            local example2 "help intreg"
            local explain2 "区间、左删失、右删失和精确观测可在同一模型中组合。"
        }
        else if "`cmd'" == "tobit" {
            local expr_label "Y + X + ll()/ul() 删失界限"
            local example1 "tobit y x1 x2, ll(0)"
            local explain1 "对在 0 处左删失的连续结果估计 Tobit 模型。"
            local example2 "tobit y x1 x2, ll(0) ul(100)"
            local explain2 "同时指定左右删失界限。"
        }
        else if "`cmd'" == "truncreg" {
            local expr_label "Y + X + ll()/ul() 截断界限"
            local example1 "truncreg y x1 x2, ll(0)"
            local explain1 "样本只观察到 y>0 的个体时，用左截断回归修正抽样机制。"
            local example2 "help truncreg"
            local explain2 "截断意味着界限外观测整体未进入样本；界限必须对应真实抽样规则。"
        }
        else if "`cmd'" == "boxcox" {
            local expr_label "Y + X + model()/lrtest 等 Box–Cox 变换设定"
            local example1 "boxcox y x1 x2, model(lhsonly)"
            local explain1 "只对因变量侧估计 Box–Cox 变换参数。"
            local example2 "help boxcox"
            local explain2 "lhs、rhs 或两侧变换的模型形式不同，运行前明确变量必须为正等数据要求。"
        }
        else if "`cmd'" == "fp" {
            local expr_label "<连续变量> + FP options + 冒号后的估计命令"
            local example1 "fp <age>, scale: regress y x <age>"
            local explain1 "让 Stata 在候选 fractional powers 中为 age 选择函数形式，再估计线性回归。"
            local example2 "help fp"
            local explain2 "fp 是前缀工作流；尖括号标记参与 fractional-polynomial 搜索的连续变量。"
        }
        else if "`cmd'" == "nl" {
            local expr_label "非线性方程（参数写在 {} 中，可给初值）"
            local example1 "nl (y = {b0=1}*(1-exp(-{b1=.1}*x)))"
            local explain1 "直接在方程中定义非线性函数和参数初值，用 nonlinear least squares 估计。"
            local example2 "help nl"
            local explain2 "复杂函数也可封装成 function evaluator program。"
        }
        else if "`cmd'" == "nlsur" {
            local expr_label "多个非线性方程（每个方程一组括号，共享参数可复用同名 {}）"
            local example1 "nlsur (y1 = {a1}*x1 + {a2}*x2) (y2 = {b1}*x1 + {b2}*x2)"
            local explain1 "联合估计两个非线性方程，并允许方程误差相关。"
            local example2 "help nlsur"
            local explain2 "需求系统等复杂模型常需自定义 evaluator；参数约束应显式记录。"
        }
        else if "`cmd'" == "gmm" {
            local expr_label "矩条件 / 残差方程 + instruments() + weight/VCE 设定"
            local example1 "gmm (y - {b0} - {b1}*x), instruments(z x)"
            local explain1 "指定一个残差矩条件，并用 z、x 作为工具变量进行 GMM 估计。"
            local example2 "help gmm"
            local explain2 "非线性、多方程、动态或面板矩条件应直接保留原生表达式结构。"
        }
        else if "`cmd'" == "reg3" {
            local expr_label "多个线性方程括号 + 2sls/3sls/sure 等系统估计设定"
            local example1 "reg3 (y1 x1 x2) (y2 y1 z1), 3sls"
            local explain1 "把两条联立线性方程作为系统，用三阶段最小二乘联合估计。"
            local example2 "help reg3"
            local explain2 "内生变量、排除限制和跨方程识别条件应在运行前明确。"
        }
        else if "`cmd'" == "frontier" {
            local expr_label "Y + X + production/cost + distribution()/uhet()/vhet() 等前沿设定"
            local example1 "frontier y x1 x2"
            local explain1 "默认拟合生产随机前沿模型。"
            local example2 "frontier lncost lnout lnp_l lnp_k, cost"
            local explain2 "加 cost 后拟合成本前沿；效率方向与生产前沿不同。"
        }
'''
s = s.replace(marker, linear_blocks + marker, 1)

# Family-level copy for a coherent title.
family_marker = '''    if strpos(" ameans centile ci mean proportion ratio total dtable ", " `cmd' ") {
'''
linear_family = '''    if strpos(" hetregress sqreg intreg tobit truncreg boxcox fp nl nlsur gmm reg3 frontier ", " `cmd' ") {
        local title "`cmd' — 线性模型及相关"
        local purpose1 "用于异方差、删失/截断、非线性、方程系统、GMM、函数形式或随机前沿等线性模型扩展。"
        local purpose2 "这些命令的核心语法差异较大；页面直接保留真正的方程、边界、矩条件或前缀结构。"
    }
    else if strpos(" ameans centile ci mean proportion ratio total dtable ", " `cmd' ") {
'''
s = once(s, family_marker, linear_family, "linear family copy")
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------------- static contracts ----------------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''summary_core = {"summarize", "ameans", "centile", "ci", "mean", "proportion", "ratio", "total", "tabstat", "tabulate", "table", "dtable"}
'''
checks = '''linear_related_core = {
    "regress", "areg", "cnsreg", "rreg", "hetregress", "qreg", "iqreg", "bsqreg", "sqreg",
    "vwls", "eivreg", "intreg", "tobit", "truncreg", "boxcox", "fp", "nl", "nlsur", "gmm",
    "sureg", "reg3", "mvreg", "frontier", "correlate", "pwcorr",
}
missing_linear = sorted(linear_related_core - stats_cmds)
if missing_linear:
    fail("linear-related commands missing: " + ", ".join(missing_linear))
for needle in (
    'hetregress y x1 x2, het(z1 z2)',
    'sqreg y x1 x2, quantile(.25 .5 .75) reps(100)',
    'intreg ylower yupper x1 x2',
    'tobit y x1 x2, ll(0)',
    'truncreg y x1 x2, ll(0)',
    'fp <age>, scale: regress y x <age>',
    'nl (y = {b0=1}*(1-exp(-{b1=.1}*x)))',
    'nlsur (y1 = {a1}*x1 + {a2}*x2) (y2 = {b1}*x1 + {b2}*x2)',
    'gmm (y - {b0} - {b1}*x), instruments(z x)',
    'reg3 (y1 x1 x2) (y2 y1 z1), 3sls',
    'frontier lncost lnout lnp_l lnp_k, cost',
):
    if needle not in semantics:
        fail(f"linear-related semantic contract missing: {needle}")

'''
v = once(v, anchor, checks + anchor, "linear static contracts")
v = v.replace(
    'summary_catalog=1 power_precision=1',
    'linear_catalog=1 summary_catalog=1 power_precision=1',
)
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_LINEAR_CATALOG_PATCH_OK")
