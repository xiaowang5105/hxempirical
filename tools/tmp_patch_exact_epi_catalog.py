from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------------- registry ----------------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.8  16aug2026", "*! hxregistry 3.1.9  16aug2026", "registry version")
r = once(
    r,
    "stset sts stcox streg stcrreg cc cs ir eregress",
    "stset sts stcox streg stcrreg cc cs ir mcc dstdize eregress",
    "epidemiology catalog",
)
r = once(
    r,
    "meta mi npregress kdensity lowess lpoly bitesti tabi bootstrap",
    "meta mi npregress kdensity lowess lpoly exlogistic expoisson bitest bitesti ksmirnov symmetry tetrachoric tabi bootstrap",
    "exact catalog",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "流行病学及相关", "epidemiology") local view "cc cs ir"\n',
    '    else if inlist(`"`method\'"\', "流行病学及相关", "epidemiology") local view "cc cs ir mcc dstdize"\n',
    "epidemiology method",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "精确统计", "exact_stats") local view "bitesti tabi"\n',
    '    else if inlist(`"`method\'"\', "精确统计", "exact_stats") local view "exlogistic expoisson bitest bitesti ksmirnov symmetry tetrachoric tabi"\n',
    "exact method",
)
anchor = '        local key_svyset "svyset survey design 调查数据 抽样设计 权重 分层 psu strata pweight"\n'
add = '''        local key_mcc "mcc matched case control matched pairs epidemiology 配对 病例对照 McNemar"
        local key_dstdize "dstdize standardize rates direct indirect standardization 标准化 标化率 流行病学"
        local key_exlogistic "exlogistic exact logistic regression 精确 logistic 小样本 完全预测"
        local key_expoisson "expoisson exact poisson regression 精确 poisson 小样本 计数"
        local key_bitest "bitest exact binomial probability test 二项 精确检验"
        local key_bitesti "bitesti immediate exact binomial probability test 二项 即时 精确检验"
        local key_ksmirnov "ksmirnov kolmogorov smirnov exact distribution 非参数 分布 检验"
        local key_symmetry "symmetry marginal homogeneity exact matched table 对称 边际同质 精确"
        local key_tetrachoric "tetrachoric binary correlation exact 二元 相关 四分相关"
'''
r = once(r, anchor, add + anchor, "exact epidemiology search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------------- semantics ----------------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.7  16aug2026", "*! hxsemantics 1.4.8  16aug2026", "semantics version")
s = once(
    s,
    " table prtest sdtest oneway anova ranksum median signrank signtest bitesti tabi cc cs ir sureg ",
    " table prtest sdtest oneway anova ranksum median signrank signtest exlogistic expoisson bitest bitesti ksmirnov symmetry tetrachoric tabi cc cs ir mcc dstdize sureg ",
    "exact/epi command-body catalog",
)
old_epi = '''        else if strpos(" cc cs ir ", " `cmd' ") {
            local expr_label "流行病学命令主体（病例 / 暴露 / 时间 / 分层参数）"
            local example1 "help `cmd'"
            local explain1 "病例对照、队列和发病率命令的变量角色不同，按当前 help 填写完整主体。"
        }
'''
new_epi = '''        else if strpos(" cc cs ir ", " `cmd' ") {
            local expr_label "流行病学命令主体（病例 / 暴露 / 时间 / 分层参数）"
            local example1 "help `cmd'"
            local explain1 "病例对照、队列和发病率命令的变量角色不同，按当前 help 填写完整主体。"
        }
        else if "`cmd'" == "mcc" {
            local expr_label "病例暴露变量 + 配对对照暴露变量（1:1 matched pairs）"
            local example1 "mcc smoke1 smoke0"
            local explain1 "每行是一对 matched case-control；smoke1 为病例暴露，smoke0 为其配对对照暴露。"
            local example2 "help mcc"
            local explain2 "mcc 适用于 1:1 配对；1:M 匹配应转用条件 logistic 等方法。"
        }
        else if "`cmd'" == "dstdize" {
            local expr_label "事件变量 + 人口/权重变量 + 标准化分层变量 + by()/using()"
            local example1 "dstdize deaths pop age_group, by(state)"
            local explain1 "按 age_group 对各 state 的率做标准化；实际标准人口来源需结合研究设计核对。"
            local example2 "help dstdize"
            local explain2 "直接/间接标准化、外部标准人口和保存选项请按当前 Stata help 设置。"
        }
'''
s = once(s, old_epi, new_epi, "epidemiology semantics")
old_exact = '''        else if strpos(" table prtest sdtest oneway anova ranksum median signrank signtest bitesti tabi ", " `cmd' ") {
            local expr_label "检验 / 表格主体（变量、分组、比较值或计数参数）"
            local example1 "help `cmd'"
            local explain1 "这些命令的变量角色和参数顺序差异较大，页面保留官方原生命令主体，避免把分组变量或比较值误标成解释变量。"
        }
'''
new_exact = '''        else if strpos(" table prtest sdtest oneway anova ranksum median signrank signtest bitesti tabi ", " `cmd' ") {
            local expr_label "检验 / 表格主体（变量、分组、比较值或计数参数）"
            local example1 "help `cmd'"
            local explain1 "这些命令的变量角色和参数顺序差异较大，页面保留官方原生命令主体，避免把分组变量或比较值误标成解释变量。"
        }
        else if "`cmd'" == "exlogistic" {
            local expr_label "二元/二项结果变量 + 解释变量"
            local example1 "exlogistic response treatment gender hypertension"
            local explain1 "使用 exact logistic 对小样本二元结果做条件精确推断。"
            local example2 "help exlogistic"
            local explain2 "条件化变量、内存/时间限制与 Monte Carlo 设置属于精确估计的重要选项。"
        }
        else if "`cmd'" == "expoisson" {
            local expr_label "计数结果变量 + 解释变量 + exposure()/offset() 等设定"
            local example1 "expoisson y x1 x2"
            local explain1 "对计数结果执行 exact Poisson 回归。"
            local example2 "help expoisson"
            local explain2 "暴露量、条件化和计算控制选项运行前按当前 help 核对。"
        }
        else if "`cmd'" == "bitest" {
            local expr_label "二元变量 = 原假设概率（如 outcome = .5）"
            local example1 "bitest outcome = .5"
            local explain1 "检验二元 outcome 的成功概率是否等于 0.5，使用精确二项分布。"
            local example2 "help bitest"
            local explain2 "即时汇总数据可改用 bitesti。"
        }
        else if "`cmd'" == "ksmirnov" {
            local expr_label "变量 = 理论 CDF 表达式，或变量 + by() 两样本分组"
            local example1 "ksmirnov x, by(group)"
            local explain1 "比较 group 两组的经验分布是否相同。"
            local example2 "help ksmirnov"
            local explain2 "单样本检验需要提供理论累计分布函数表达式。"
        }
        else if "`cmd'" == "symmetry" {
            local expr_label "配对/方阵分类变量 + exact 等检验选项"
            local example1 "symmetry before after, exact"
            local explain1 "检验配对分类结果 before/after 的对称性，并请求精确检验。"
            local example2 "help symmetry"
            local explain2 "边际同质与 exact 选项按表结构继续核对。"
        }
        else if "`cmd'" == "tetrachoric" {
            local expr_label "两个或多个二元变量"
            local example1 "tetrachoric y x1 x2"
            local explain1 "估计二元变量背后潜在连续变量之间的 tetrachoric correlation。"
            local example2 "help tetrachoric"
            local explain2 "变量应具有二元编码；多变量时返回相关矩阵。"
        }
'''
s = once(s, old_exact, new_exact, "exact semantics")
# Family-level copy: include new exact/epi commands in meaningful titles.
s = once(
    s,
    '    else if strpos(" cc cs ir ", " `cmd\' ") {\n',
    '    else if strpos(" cc cs ir mcc dstdize ", " `cmd\' ") {\n',
    "epidemiology family",
)
s = once(
    s,
    '    else if strpos(" bitesti tabi ", " `cmd\' ") {\n',
    '    else if strpos(" exlogistic expoisson bitest bitesti ksmirnov symmetry tetrachoric tabi ", " `cmd\' ") {\n',
    "exact family",
)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------------- static contracts ----------------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''multivariate_core = {
    "alpha", "factor", "pca", "canon", "ca", "candisc", "hotelling", "manova", "mvreg",
    "mca", "mds", "mdslong", "mdsmat", "mvtest", "procrustes", "discrim", "cluster",
}
'''
extra = '''exact_core = {"exlogistic", "expoisson", "bitest", "bitesti", "ksmirnov", "symmetry", "tetrachoric", "tabi"}
missing_exact = sorted(exact_core - stats_cmds)
if missing_exact:
    fail("exact-statistics commands missing: " + ", ".join(missing_exact))
for epi_cmd in ("cc", "cs", "ir", "mcc", "dstdize"):
    if epi_cmd not in stats_cmds:
        fail(f"epidemiology workflow command missing: {epi_cmd}")
for needle in (
    'exlogistic response treatment gender hypertension',
    'bitest outcome = .5',
    'mcc smoke1 smoke0',
    'dstdize deaths pop age_group, by(state)',
):
    if needle not in semantics:
        fail(f"exact/epidemiology semantic contract missing: {needle}")

'''
v = once(v, anchor, extra + anchor, "exact/epi static contracts")
v = v.replace(
    'multivariate_catalog=1 docs_source_split=1',
    'multivariate_catalog=1 exact_epi_catalog=1 docs_source_split=1',
)
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_EXACT_EPI_CATALOG_PATCH_OK")
