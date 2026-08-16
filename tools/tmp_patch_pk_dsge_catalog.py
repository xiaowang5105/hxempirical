from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------- registry ----------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.19  16aug2026", "*! hxregistry 3.1.20  16aug2026", "registry version")

# Add real PK commands to epidemiology-related tools and real DSGE estimators to Statistics.
r = once(
    r,
    " stmh stmc cc cs ir mcc dstdize eregress ",
    " stmh stmc cc cs ir mcc dstdize pkexamine pksumm pkcross pkequiv pkcollapse pkshape eregress ",
    "PK statistics catalog",
)
r = once(
    r,
    " sem gsem fmm irt irtgraph diflogistic difmh alpha factor ",
    " sem gsem fmm irt irtgraph diflogistic difmh dsge dsgenl alpha factor ",
    "DSGE statistics catalog",
)

r = once(
    r,
    "项目反应理论(IRT) 多元分析",
    "项目反应理论(IRT) DSGE模型 多元分析",
    "DSGE method list",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "流行病学及相关", "epidemiology") local view "cc cs ir mcc dstdize"\n',
    '    else if inlist(`"`method\'"\', "流行病学及相关", "epidemiology") local view "cc cs ir mcc dstdize pkexamine pksumm pkcross pkequiv pkcollapse pkshape"\n',
    "PK epidemiology route",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "项目反应理论(IRT)", "irt") local view "irt irtgraph diflogistic difmh"\n',
    '    else if inlist(`"`method\'"\', "项目反应理论(IRT)", "irt") local view "irt irtgraph diflogistic difmh"\n    else if inlist(`"`method\'"\', "DSGE模型", "dsge") local view "dsge dsgenl"\n',
    "DSGE method route",
)

keyword_anchor = '        local key_difmh "difmh IRT Mantel Haenszel DIF differential item functioning 差异项目功能"\n'
keyword_add = '''        local key_dsge "dsge dynamic stochastic general equilibrium DSGE 动态随机一般均衡 线性化 宏观模型"
        local key_dsgenl "dsgenl nonlinear DSGE dynamic stochastic general equilibrium 非线性 动态随机一般均衡"
        local key_pkexamine "pkexamine pharmacokinetic concentration time AUC half-life cmax 药代动力学 浓度 时间 半衰期"
        local key_pksumm "pksumm pharmacokinetic summary AUC distribution 药代动力学 汇总 正态性"
        local key_pkcross "pkcross pharmacokinetic crossover experiment 交叉试验 药代动力学"
        local key_pkequiv "pkequiv bioequivalence pharmacokinetic 生物等效 药代动力学 TOST"
        local key_pkcollapse "pkcollapse pharmacokinetic collapse measurements reshape 药代动力学 AUC 数据转换"
        local key_pkshape "pkshape pharmacokinetic Latin square crossover reshape 药代动力学 拉丁方 交叉设计 重塑"
'''
r = once(r, keyword_anchor, keyword_anchor + keyword_add, "PK DSGE search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------- semantics ----------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.18  16aug2026", "*! hxsemantics 1.4.19  16aug2026", "semantics version")

s = once(
    s,
    " sem gsem mi meta fmm irt irtgraph diflogistic difmh svyset ",
    " sem gsem mi meta fmm irt irtgraph diflogistic difmh dsge dsgenl svyset ",
    "DSGE command-body catalog",
)
s = once(
    s,
    " cc cs ir mcc dstdize hetregress ",
    " cc cs ir mcc dstdize pkexamine pksumm pkcross pkequiv pkcollapse pkshape hetregress ",
    "PK command-body catalog",
)

# Insert DSGE semantics immediately after gsem, preserving LCA under gsem.
gsem_block = '''        else if "`cmd'" == "gsem" {
            local expr_label "广义 SEM 方程 + family()/link()/随机效应/潜在类别设定"
            local example1 "gsem (y <- x1 x2, family(bernoulli) link(logit))"
            local explain1 "对二元结果 y 拟合 logit 链接的广义结构方程。"
            local example2 "gsem (alcohol truant weapon theft vandalism <-), logit lclass(C 3)"
            local explain2 "LCA 使用 gsem 的 lclass()；这里拟合 3 个潜在类别的二元题项模型。"
        }
'''
if s.count(gsem_block) != 1:
    raise SystemExit(f"gsem insertion block count={s.count(gsem_block)}")
dsge_blocks = '''        else if "`cmd'" == "dsge" {
            local expr_label "线性化 DSGE 方程系统：控制变量方程 + (F.state = ..., state) 状态方程"
            local example1 "dsge (p = {beta}*E(F.p) + {kappa}*y) (F.y = {rho}*y, state)"
            local explain1 "两方程线性化 DSGE：p 是前瞻控制变量，y 是带冲击的状态变量；花括号内参数由模型估计。"
            local example2 "help dsge"
            local explain2 "正式模型应先 tsset；可继续加入 observed/unobserved 控制变量、多个状态方程和参数约束。"
        }
        else if "`cmd'" == "dsgenl" {
            local expr_label "非线性 DSGE 方程系统 + observed()/unobserved()/endostate()/exostate()"
            local example1 "dsgenl (1 = {beta}*(x/F.x)*(r/(F.p*z))) (1/{phi} + (p-1) = {phi}*x + {beta}*(F.p-1)) ({beta}*r = p^(1/{beta})*u) (ln(F.u) = {rhou}*ln(u)) (ln(F.z) = {rhoz}*ln(z)), observed(r p) unobserved(x) exostate(z u)"
            local explain1 "官方 New Keynesian 示例：r、p 为 observed，x 为 unobserved control，z、u 为外生 state；F. 表示一期前瞻值。"
            local example2 "help dsgenl"
            local explain2 "需要内生 state 时继续使用 endostate()；稳态、识别与收敛诊断是非线性 DSGE 的模型核心。"
        }
'''
s = s.replace(gsem_block, gsem_block + dsge_blocks, 1)

# Insert PK semantics before generic epidemiology commands.
pk_marker = '''        else if "`cmd'" == "hetregress" {
'''
if s.count(pk_marker) != 1:
    raise SystemExit(f"PK semantic marker count={s.count(pk_marker)}")
pk_blocks = '''        else if "`cmd'" == "pkexamine" {
            local expr_label "时间变量 + 浓度变量 + if/in；可加 graph/trapezoid/fit()"
            local example1 "pkexamine time concentration, graph"
            local explain1 "从单个 subject 的 concentration–time 数据计算 AUC、Cmax、Tmax、elimination rate 和 half-life，并绘图。"
            local example2 "help pkexamine"
            local explain2 "对多 subject 数据通常先按 id 选择个体，或使用 pksumm 汇总全部 subjects 的 PK measures。"
        }
        else if "`cmd'" == "pksumm" {
            local expr_label "subject ID + 时间变量 + 浓度变量 + graph/stat() 等汇总设定"
            local example1 "pksumm id time conc"
            local explain1 "对每个 subject 计算常见 PK measures，再汇总其均值、中位数、方差、偏度、峰度和正态性检验。"
            local example2 "pksumm id time conc, graph stat(auc)"
            local explain2 "在汇总全部 PK measures 的同时绘制 AUC 分布；stat() 可换成 half、ke、cmax 等。"
        }
        else if "`cmd'" == "pkcross" {
            local expr_label "结果变量 + param() + id()/sequence()/treatment()/period() crossover 设计字段"
            local example1 "pkcross y, param(3) id(idvar) sequence(seq) treatment(treat) period(period)"
            local explain1 "分析 crossover experiment；显式给出 subject、sequence、treatment 与 period 角色。"
            local example2 "help pkcross"
            local explain2 "carryover、period 与 sequence 效应应结合 crossover 设计核对，不能按普通独立样本比较解释。"
        }
        else if "`cmd'" == "pkequiv" {
            local expr_label "PK measure + treatment + period + sequence + subject ID + equivalence limits"
            local example1 "pkequiv auc treat period sequence id, limit(0.1) notost noboot"
            local explain1 "对 AUC 进行 crossover bioequivalence 分析，并把等效界限设为 10%。"
            local example2 "help pkequiv"
            local explain2 "bioequivalence 的 limit、TOST/CI 和 bootstrap 设定应来自研究方案与监管口径。"
        }
        else if "`cmd'" == "pkcollapse" {
            local expr_label "时间变量 + 一个或多个浓度变量 + id() + stat()/keep()"
            local example1 "pkcollapse time conc1 conc2, id(id) stat(auc) keep(seq)"
            local explain1 "把原始 concentration–time 记录压缩为 subject-level PK measurement 数据，同时保留 seq。"
            local example2 "help pkcollapse"
            local explain2 "pkcollapse 会重构当前内存数据；运行前保存原始 concentration–time 明细。"
        }
        else if "`cmd'" == "pkshape" {
            local expr_label "subject ID + sequence + period measurements + order()"
            local example1 "pkshape id seq period1 period2, order(RT TR)"
            local explain1 "把 2×2 crossover/Latin-square 的宽表 period measurements 重塑为 outcome、treat、carry、period 等长表字段。"
            local example2 "help pkshape"
            local explain2 "pkshape 会直接重组内存数据；order() 必须与实际 treatment sequence 一致，运行前先保存原数据。"
        }
'''
s = s.replace(pk_marker, pk_blocks + pk_marker, 1)

# Family-level copy for clear task framing.
irt_family = '''    else if strpos(" irt irtgraph diflogistic difmh ", " `cmd' ") {
        local title "`cmd' — 项目反应理论"
'''
if s.count(irt_family) != 1:
    raise SystemExit(f"IRT family marker count={s.count(irt_family)}")
dsge_family = '''    else if strpos(" dsge dsgenl ", " `cmd' ") {
        local title "`cmd' — 动态随机一般均衡模型"
        local purpose1 "用于求解或估计线性化与非线性 DSGE 方程系统，并保留前瞻变量、状态变量和结构参数的原生模型表达。"
        local purpose2 "先 tsset 并明确 observed/unobserved controls 与 endogenous/exogenous states；稳定性、识别和稳态属于必要诊断。"
    }
'''
s = s.replace(irt_family, dsge_family + irt_family, 1)

old_epi_family = '    else if strpos(" cc cs ir mcc dstdize ", " `cmd\' ") {\n'
new_epi_family = '    else if strpos(" cc cs ir mcc dstdize pkexamine pksumm pkcross pkequiv pkcollapse pkshape ", " `cmd\' ") {\n'
s = once(s, old_epi_family, new_epi_family, "PK epidemiology family")
s = once(
    s,
    '        local purpose1 "用于病例对照、队列或发病率资料的比值比、风险比和相关效应量计算。"\n',
    '        local purpose1 "用于病例对照、队列、发病率资料，以及 pharmacokinetic concentration–time、crossover 和 bioequivalence 分析。"\n',
    "PK epidemiology purpose",
)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------- permanent static contracts ----------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'irt_core = {"irt", "irtgraph", "diflogistic", "difmh"}\n'
checks = '''dsge_core = {"dsge", "dsgenl"}
missing_dsge = sorted(dsge_core - stats_cmds)
if missing_dsge:
    fail("DSGE command coverage missing: " + ", ".join(missing_dsge))
if "DSGE模型" not in registry:
    fail("DSGE method missing from Statistics navigation")
pk_core = {"pkexamine", "pksumm", "pkcross", "pkequiv", "pkcollapse", "pkshape"}
missing_pk = sorted(pk_core - stats_cmds)
if missing_pk:
    fail("pharmacokinetic command coverage missing: " + ", ".join(missing_pk))
if "pk" in stats_cmds:
    fail("umbrella help entry pk must not be exposed as an executable Statistics command")
for needle in (
    "dsge (p = {beta}*E(F.p) + {kappa}*y) (F.y = {rho}*y, state)",
    "observed(r p) unobserved(x) exostate(z u)",
    "pkexamine time concentration, graph",
    "pksumm id time conc",
    "pkcross y, param(3) id(idvar) sequence(seq) treatment(treat) period(period)",
    "pkequiv auc treat period sequence id, limit(0.1) notost noboot",
    "pkcollapse time conc1 conc2, id(id) stat(auc) keep(seq)",
    "pkshape id seq period1 period2, order(RT TR)",
):
    if needle not in semantics:
        fail(f"PK/DSGE semantic contract missing: {needle}")

'''
v = once(v, anchor, checks + anchor, "PK DSGE static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_PK_DSGE_PATCH_OK")
