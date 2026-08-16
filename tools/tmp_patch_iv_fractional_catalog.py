from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------------- registry ----------------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.13  16aug2026", "*! hxregistry 3.1.14  16aug2026", "registry version")
r = once(
    r,
    "eregress eprobit eoprobit eintreg ivregress ivreghdfe teffects",
    "eregress eprobit eoprobit eintreg ivregress ivprobit ivtobit ivpoisson ivfprobit ivqregress ivreghdfe teffects",
    "IV command catalog",
)
r = once(
    r,
    '''    if c(stata_version) < 18 {
        foreach cmd in mediate hdidregress xthdidregress bmaregress dtable gsbounds gsdesign {
            local stats_cmds : subinstr local stats_cmds " `cmd'" "", all
        }
    }
''',
    '''    if c(stata_version) < 18 {
        foreach cmd in mediate hdidregress xthdidregress bmaregress dtable gsbounds gsdesign ivfprobit ivqregress {
            local stats_cmds : subinstr local stats_cmds " `cmd'" "", all
        }
    }
''',
    "Stata 18 IV gates",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "工具变量与内生性", "iv_extensions") local view "ivregress ivreghdfe"\n',
    '''    else if inlist(`"`method'"', "工具变量与内生性", "iv_extensions") {
        local view "ivregress ivprobit ivtobit ivpoisson ivreghdfe"
        if c(stata_version) >= 18 local view "`view' ivfprobit ivqregress"
    }
''',
    "IV method routing",
)
anchor = '        local key_ivregress "ivregress iv 2sls gmm liml 工具变量 内生性"\n'
add = '''        local key_ivprobit "ivprobit instrumental variables probit endogenous binary 工具变量 二元 内生 probit"
        local key_ivtobit "ivtobit instrumental variables tobit censored endogenous 工具变量 tobit 删失 内生"
        local key_ivpoisson "ivpoisson instrumental variables poisson count endogenous gmm 工具变量 泊松 计数 内生"
        local key_ivfprobit "ivfprobit fractional probit endogenous covariates 工具变量 分数结果 内生 probit"
        local key_ivqregress "ivqregress instrumental variables quantile regression IQR smooth 工具变量 分位数 内生"
'''
r = once(r, anchor, anchor + add, "IV search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------------- semantics ----------------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.12  16aug2026", "*! hxsemantics 1.4.13  16aug2026", "semantics version")
s = once(
    s,
    " eregress eprobit eoprobit eintreg mixed melogit",
    " eregress eprobit eoprobit eintreg ivprobit ivtobit ivpoisson ivfprobit ivqregress mixed melogit",
    "IV command-body catalog",
)

# Give beta regression a low-barrier Y/X page with a hard domain reminder.
bma_marker = '''    /* bmaregress is the executable estimation command in Stata's BMA suite. */
'''
beta_block = '''    if "`cmd'" == "betareg" {
        local template "generic"
        local title "betareg — Beta 回归"
        local purpose1 "用于严格落在 0 与 1 之间的连续比例 / 分数结果，直接建模条件均值并允许 precision 子模型。"
        local purpose2 "结果中出现 0 或 1 时应优先考虑 fracreg；betareg 的标准 Beta 分布要求 0<Y<1。"
        local has_depvar 1
        local has_varlist 1
        local dep_label "分数结果 Y（必须严格位于 0 与 1 之间）"
        local vars_label "解释变量"
        local example1 "betareg gini i.rural i.democracy i.colony, nolog"
        local explain1 "对严格位于 (0,1) 的 gini 进行 Beta 回归。"
        local example2 "help betareg"
        local explain2 "precision()、link() 等参数决定离散程度与均值链接，复杂设定运行前核对。"
    }

'''
if s.count(bma_marker) != 1:
    raise SystemExit("bmaregress insertion marker missing")
s = s.replace(bma_marker, beta_block + bma_marker, 1)

# Insert IV command-body semantics immediately before mixed-effects grammar.
mixed_marker = '''        else if strpos(" mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm ", " `cmd' ") {
'''
if s.count(mixed_marker) != 1:
    raise SystemExit(f"mixed command-body marker count={s.count(mixed_marker)}")
iv_blocks = '''        else if "`cmd'" == "ivprobit" {
            local expr_label "二元 Y + 外生 X + (内生连续变量 = 工具变量)"
            local example1 "ivprobit y x1 (x2 = z1 z2)"
            local explain1 "在 Probit 结果方程中把 x2 视为连续内生协变量，并用 z1、z2 作为排除工具变量。"
            local example2 "help ivprobit"
            local explain2 "ML 与 two-step 的后估计能力不同；工具变量相关性和外生性仍需单独诊断。"
        }
        else if "`cmd'" == "ivtobit" {
            local expr_label "删失 Y + 外生 X + (内生连续变量 = 工具变量) + ll()/ul()"
            local example1 "ivtobit y x1 (x2 = z1 z2), ll(0)"
            local explain1 "对在 0 处左删失的结果建模，同时用 z1、z2 处理 x2 的内生性。"
            local example2 "help ivtobit"
            local explain2 "删失界限必须对应真实观测机制；ML/two-step 与 VCE 选项运行前核对。"
        }
        else if "`cmd'" == "ivpoisson" {
            local expr_label "估计器 + 计数 Y + 外生 X + (内生变量 = 工具变量)"
            local example1 "ivpoisson gmm accidents x1 x2 (horsepower = x3 x4)"
            local explain1 "使用 GMM Poisson，以 x3、x4 作为 horsepower 的工具变量。"
            local example2 "help ivpoisson"
            local explain2 "gmm 与 cfunction 的识别假设和可用后估计不同，先明确估计器再填方程。"
        }
        else if "`cmd'" == "ivfprobit" {
            local expr_label "分数 Y + 外生 X + (内生连续变量 = 工具变量)"
            local example1 "ivfprobit prate c.ltotemp##c.ltotemp i.sole (mrate = c.age##c.age)"
            local explain1 "Stata 18 fractional probit IV：mrate 是内生协变量，plan age 及其平方作为工具变量。"
            local example2 "help ivfprobit"
            local explain2 "fracreg/ivfprobit 允许分数结果包含 0 和 1；该入口仅在 Stata 18+ 展示。"
        }
        else if "`cmd'" == "ivqregress" {
            local expr_label "IQR/smooth + Y + (内生变量 = 工具变量) + 外生 X + quantile()"
            local example1 "ivqregress iqr assets (i.p401k = i.e401k) income age familysize i.married i.ira i.pension i.ownhome educ"
            local explain1 "使用 inverse quantile regression 估计内生 401(k) 参与对条件中位数的影响。"
            local example2 "ivqregress smooth assets (i.p401k = i.e401k) income age familysize, quantile(10(10)90)"
            local explain2 "smooth estimator 可同时研究多个条件分位数；该入口仅在 Stata 18+ 展示。"
        }
'''
s = s.replace(mixed_marker, iv_blocks + mixed_marker, 1)

# Family-level copy for IV pages and a clearer beta/frac distinction.
family_marker = '''    if strpos(" gnbreg cpoisson ", " `cmd' ") {
'''
iv_family = '''    if strpos(" ivprobit ivtobit ivpoisson ivfprobit ivqregress ", " `cmd' ") {
        local title "`cmd' — 工具变量与内生性"
        local purpose1 "用于二元、删失、计数、分数或分位数结果中存在内生解释变量的 IV 模型。"
        local purpose2 "页面保留估计器、结果分布、删失界限和 (内生变量 = 工具变量) 的原生位置，避免普通 IV Y/X 模板拆错语法。"
    }
    else if strpos(" gnbreg cpoisson ", " `cmd' ") {
'''
s = once(s, family_marker, iv_family, "IV family copy")
# Refine the existing frac/beta/glm family wording without changing safe generic roles.
s = once(
    s,
    '''    else if strpos(" fracreg betareg glm ", " `cmd' ") {
        local title "`cmd' — 分数结果与广义线性模型"
        local purpose1 "用于比例/分数型因变量或需要自定义分布与链接函数的广义线性模型。"
        local purpose2 "先设置因变量和解释变量；family()、link() 等分布与链接设置按当前命令填写。"
    }
''',
    '''    else if strpos(" fracreg betareg glm ", " `cmd' ") {
        local title "`cmd' — 分数结果与广义线性模型"
        local purpose1 "用于比例/分数型结果或需要自定义分布与链接函数的广义线性模型。"
        local purpose2 "fracreg 可处理 0/1 端点；betareg 要求 0<Y<1；GLM 的 family()/link() 决定模型形式。"
    }
''',
    "fractional family wording",
)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------------- static contracts ----------------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''count_core = {"poisson", "nbreg", "gnbreg", "cpoisson", "zip", "zinb", "tpoisson", "tnbreg"}
'''
checks = '''iv_core = {"ivregress", "ivprobit", "ivtobit", "ivpoisson"}
missing_iv = sorted(iv_core - stats_cmds)
if missing_iv:
    fail("instrumental-variable commands missing: " + ", ".join(missing_iv))
for stata18_iv in ("ivfprobit", "ivqregress"):
    if stata18_iv not in stats_cmds:
        fail(f"Stata 18 IV command missing: {stata18_iv}")
if "ivfprobit ivqregress" not in registry or "gsdesign ivfprobit ivqregress" not in registry:
    fail("Stata 18 IV version gate or routing missing")
for needle in (
    'betareg gini i.rural i.democracy i.colony, nolog',
    '0<Y<1',
    'ivprobit y x1 (x2 = z1 z2)',
    'ivtobit y x1 (x2 = z1 z2), ll(0)',
    'ivpoisson gmm accidents x1 x2 (horsepower = x3 x4)',
    'ivfprobit prate c.ltotemp##c.ltotemp i.sole (mrate = c.age##c.age)',
    'ivqregress iqr assets (i.p401k = i.e401k)',
):
    if needle not in semantics:
        fail(f"IV/fractional semantic contract missing: {needle}")

'''
v = once(v, anchor, checks + anchor, "IV fractional static contracts")
v = v.replace(
    'count_catalog=1 hurdle_model=1 summary_catalog=1',
    'count_catalog=1 hurdle_model=1 iv_catalog=1 fractional_semantics=1 summary_catalog=1',
)
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_IV_FRACTIONAL_PATCH_OK")
