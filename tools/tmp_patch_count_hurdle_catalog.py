from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.12  16aug2026", "*! hxregistry 3.1.13  16aug2026", "registry version")
r = once(
    r,
    "truncreg boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate",
    "truncreg churdle boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate",
    "linear hurdle catalog",
)
r = once(
    r,
    "poisson nbreg zip zinb tpoisson tnbreg ppmlhdfe",
    "poisson nbreg gnbreg cpoisson zip zinb tpoisson tnbreg ppmlhdfe",
    "count catalog",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "线性模型及相关", "linear_related") local view "regress areg reghdfe cnsreg rreg hetregress qreg iqreg bsqreg sqreg vwls eivreg intreg tobit truncreg boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate pwcorr"\n',
    '    else if inlist(`"`method\'"\', "线性模型及相关", "linear_related") local view "regress areg reghdfe cnsreg rreg hetregress qreg iqreg bsqreg sqreg vwls eivreg intreg tobit truncreg churdle boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate pwcorr"\n',
    "linear hurdle method",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "计数结果", "count_outcomes") local view "poisson nbreg ppmlhdfe zip zinb tpoisson tnbreg"\n',
    '    else if inlist(`"`method\'"\', "计数结果", "count_outcomes") local view "poisson nbreg gnbreg cpoisson ppmlhdfe zip zinb tpoisson tnbreg"\n',
    "count method",
)
anchor = '        local key_poisson "poisson count 泊松 计数模型"\n'
add = '''        local key_gnbreg "gnbreg generalized negative binomial heterogeneous dispersion 负二项 广义 异质 离散参数 lnalpha"
        local key_cpoisson "cpoisson censored poisson count 删失 泊松 计数 左删失 右删失 区间"
        local key_churdle "churdle Cragg hurdle double hurdle select limited outcome 障碍模型 两阶段 选择"
'''
r = once(r, anchor, anchor + add, "count hurdle search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")

sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.11  16aug2026", "*! hxsemantics 1.4.12  16aug2026", "semantics version")
s = once(
    s,
    " truncreg boxcox fp nl nlsur gmm sureg reg3 mvreg frontier binreg",
    " truncreg churdle boxcox fp nl nlsur gmm sureg reg3 mvreg frontier gnbreg cpoisson binreg",
    "count hurdle command-body catalog",
)
marker = '''        else if "`cmd'" == "boxcox" {
'''
if s.count(marker) != 1:
    raise SystemExit(f"churdle insertion marker count={s.count(marker)}")
churdle = '''        else if "`cmd'" == "churdle" {
            local expr_label "结果模型类型 + Y + X + select() hurdle 方程 + ll()/ul() 界限"
            local example1 "churdle linear money dating teenager nkids, select(newborn hours distance weekends) ll(0)"
            local explain1 "正值部分用线性模型解释 money，select() 用 Probit 建模是否跨过 0 这一 hurdle。"
            local example2 "help churdle"
            local explain2 "可选择 linear、exponential 或 probit outcome model；hurdle 方程与结果方程可使用不同变量。"
        }
'''
s = s.replace(marker, churdle + marker, 1)
marker2 = '''        else if "`cmd'" == "binreg" {
'''
if s.count(marker2) != 1:
    raise SystemExit(f"count insertion marker count={s.count(marker2)}")
countblocks = '''        else if "`cmd'" == "gnbreg" {
            local expr_label "计数 Y + 均值方程 X + lnalpha() 离散参数方程"
            local example1 "gnbreg y x1 x2, lnalpha(z1 z2)"
            local explain1 "均值由 x1、x2 解释，同时允许负二项离散参数 alpha 随 z1、z2 系统变化。"
            local example2 "help gnbreg"
            local explain2 "当 dispersion 无需协变量解释时，普通 nbreg 更直接；lnalpha() 应有明确异质性依据。"
        }
        else if "`cmd'" == "cpoisson" {
            local expr_label "计数 Y + X + ll()/ul() 删失界限"
            local example1 "cpoisson accidents i.past i.parent i.ntickets, ul(3) irr"
            local explain1 "3 表示 3 次及以上时，用 ul(3) 处理右删失计数并报告 incidence-rate ratios。"
            local example2 "help cpoisson"
            local explain2 "删失保留观测但隐藏界限外真实计数；截断则是整个观测未进入样本。"
        }
'''
s = s.replace(marker2, countblocks + marker2, 1)
# Family copy additions.
s = once(
    s,
    '    if strpos(" hetregress sqreg intreg tobit truncreg boxcox fp nl nlsur gmm reg3 frontier ", " `cmd\' ") {\n',
    '    if strpos(" hetregress sqreg intreg tobit truncreg churdle boxcox fp nl nlsur gmm reg3 frontier ", " `cmd\' ") {\n',
    "linear family hurdle",
)
family_marker = '''    if strpos(" binreg biprobit ", " `cmd' ") {
'''
count_family = '''    if strpos(" gnbreg cpoisson ", " `cmd' ") {
        local title "`cmd' — 计数结果扩展模型"
        local purpose1 "用于离散程度本身存在协变量异质性，或计数结果发生左/右/区间删失的场景。"
        local purpose2 "lnalpha() 与 ll()/ul() 都属于数据生成过程的核心设定，页面直接保留原生语法。"
    }
    else if strpos(" binreg biprobit ", " `cmd' ") {
'''
s = once(s, family_marker, count_family, "count family copy")
sp.write_text(s, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''binary_core = {"logit", "logistic", "binreg", "probit", "biprobit", "hetprobit", "scobit", "cloglog"}
'''
checks = '''count_core = {"poisson", "nbreg", "gnbreg", "cpoisson", "zip", "zinb", "tpoisson", "tnbreg"}
missing_count = sorted(count_core - stats_cmds)
if missing_count:
    fail("count outcome commands missing: " + ", ".join(missing_count))
if "churdle" not in stats_cmds:
    fail("Cragg hurdle regression missing from Statistics catalog")
for needle in (
    'gnbreg y x1 x2, lnalpha(z1 z2)',
    'cpoisson accidents i.past i.parent i.ntickets, ul(3) irr',
    'churdle linear money dating teenager nkids, select(newborn hours distance weekends) ll(0)',
):
    if needle not in semantics:
        fail(f"count/hurdle semantic contract missing: {needle}")

'''
v = once(v, anchor, checks + anchor, "count hurdle static contracts")
v = v.replace(
    'discrete_choice_catalog=1 summary_catalog=1',
    'discrete_choice_catalog=1 count_catalog=1 hurdle_model=1 summary_catalog=1',
)
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_COUNT_HURDLE_PATCH_OK")
