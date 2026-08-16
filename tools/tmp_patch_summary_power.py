from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------------- registry ----------------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.9  16aug2026", "*! hxregistry 3.1.10  16aug2026", "registry version")
r = once(
    r,
    "summarize tabstat tabulate table ttest prtest sdtest",
    "summarize ameans centile ci mean proportion ratio total tabstat tabulate table dtable ttest prtest sdtest",
    "summary command catalog",
)
r = once(
    r,
    "bootstrap jackknife permute simulate statsby power bayes",
    "bootstrap jackknife permute simulate statsby power ciwidth gsbounds gsdesign bayes",
    "power command catalog",
)
r = once(
    r,
    '''    if c(stata_version) < 18 {
        foreach cmd in mediate hdidregress xthdidregress bmaregress {
            local stats_cmds : subinstr local stats_cmds " `cmd'" "", all
        }
    }
''',
    '''    if c(stata_version) < 18 {
        foreach cmd in mediate hdidregress xthdidregress bmaregress dtable gsbounds gsdesign {
            local stats_cmds : subinstr local stats_cmds " `cmd'" "", all
        }
    }
''',
    "Stata 18 gate",
)
old_summary = '    else if inlist(`"`method\'"\', "汇总，表格和假设检验", "summary_tests") local view "summarize tabstat tabulate table ttest prtest sdtest oneway anova ranksum median signrank signtest"\n'
new_summary = '''    else if inlist(`"`method'"', "汇总，表格和假设检验", "summary_tests") {
        local view "summarize ameans centile ci mean proportion ratio total tabstat tabulate table"
        if c(stata_version) >= 18 local view "`view' dtable"
        local view "`view' ttest prtest sdtest oneway anova ranksum median signrank signtest"
    }
'''
r = once(r, old_summary, new_summary, "summary method")
r = once(
    r,
    '    else if inlist(`"`method\'"\', "效能，精度和样品含量", "power_precision") local view "power"\n',
    '''    else if inlist(`"`method'"', "效能，精度和样品含量", "power_precision") {
        local view "power ciwidth"
        if c(stata_version) >= 18 local view "`view' gsbounds gsdesign"
    }
''',
    "power method",
)
anchor = '        local key_summarize "summarize sum 描述统计 汇总 均值 标准差"\n'
add = '''        local key_ameans "ameans arithmetic geometric harmonic means 算术 几何 调和 平均数 描述统计"
        local key_centile "centile percentile quantile 百分位 分位数 置信区间"
        local key_ci "ci confidence interval means proportions variances 置信区间 均值 比例 方差"
        local key_mean "mean estimate means 均值 置信区间 分组"
        local key_proportion "proportion proportions 比例 构成比 置信区间"
        local key_ratio "ratio estimate ratios 比率 比值 分子 分母 置信区间"
        local key_total "total estimate totals 总量 总计 置信区间"
        local key_dtable "dtable table 1 descriptive statistics 描述统计 表1 分组检验"
'''
r = once(r, anchor, anchor + add, "summary search keywords")
anchor2 = '        local key_bmaregress "bmaregress bma bayesian model averaging 贝叶斯模型平均 模型不确定性 变量选择"\n'
add2 = '''        local key_power "power sample size effect size statistical power 样本量 效能 效应量"
        local key_ciwidth "ciwidth confidence interval width precision sample size 精度 置信区间宽度 样本量"
        local key_gsbounds "gsbounds group sequential stopping boundaries efficacy futility 序贯 停止界值 疗效 无效"
        local key_gsdesign "gsdesign group sequential sample size interim analysis 序贯设计 样本量 中期分析"
'''
r = once(r, anchor2, add2 + anchor2, "power search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------------- semantics ----------------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.8  16aug2026", "*! hxsemantics 1.4.9  16aug2026", "semantics version")

summary_marker = '    else if inlist("`cmd\'", "summarize", "tabstat", "correlate", "pwcorr", "ttest", "tabulate") {\n'
summary_block = '''    else if inlist("`cmd'", "ameans", "centile", "mean", "proportion", "total") {
        local has_depvar 0
        local has_varlist 1
        local vars_label "要汇总 / 估计的变量"
        local show_advanced 1
        if "`cmd'" == "ameans" {
            local title "ameans — 算术、几何和调和平均数"
            local purpose1 "同时报告变量的算术平均数、几何平均数和调和平均数及其区间估计。"
            local purpose2 "适合正值变量；几何/调和平均数对零值和负值有定义限制。"
            local example1 "ameans y"
            local explain1 "报告 y 的三类平均数。"
            local example2 "ameans y x"
            local explain2 "一次汇总多个正值变量。"
        }
        else if "`cmd'" == "centile" {
            local title "centile — 百分位数及置信区间"
            local purpose1 "估计中位数或指定百分位点，并报告相应置信区间。"
            local purpose2 "常用 centile() 指定 25、50、75 等百分位。"
            local example1 "centile y, centile(25 50 75)"
            local explain1 "报告 y 的第 25、50、75 百分位。"
            local example2 "centile y"
            local explain2 "按 Stata 默认百分位设定估计 y。"
        }
        else if "`cmd'" == "mean" {
            local title "mean — 均值及设计型标准误"
            local purpose1 "估计一个或多个变量的总体均值、标准误和置信区间。"
            local purpose2 "可配合 over()、权重、稳健或聚类 VCE；调查设计数据可使用 svy: mean。"
            local example1 "mean y x"
            local explain1 "估计 y、x 的均值及置信区间。"
            local example2 "mean y, over(group)"
            local explain2 "按 group 分组估计 y 的均值。"
        }
        else if "`cmd'" == "proportion" {
            local title "proportion — 类别比例及置信区间"
            local purpose1 "估计类别变量各水平的总体比例并报告标准误和置信区间。"
            local purpose2 "与 tabulate 的频数展示不同，本页面向比例参数估计和推断。"
            local example1 "proportion group"
            local explain1 "估计 group 各类别的总体比例。"
            local example2 "proportion group, over(region)"
            local explain2 "按 region 分层报告 group 的比例。"
        }
        else {
            local title "total — 总量估计"
            local purpose1 "估计一个或多个变量的总体总量，并报告标准误和置信区间。"
            local purpose2 "可配合 over()、权重以及 survey 前缀。"
            local example1 "total sales"
            local explain1 "估计 sales 的总体总量。"
            local example2 "total sales, over(region)"
            local explain2 "按 region 分组估计 sales 总量。"
        }
    }
'''
if s.count(summary_marker) != 1:
    raise SystemExit(f"summary semantic marker count={s.count(summary_marker)}")
s = s.replace(summary_marker, summary_block + summary_marker, 1)

s = once(
    s,
    " power teffects eteffects stteffects mediate",
    " power ciwidth gsbounds gsdesign teffects eteffects stteffects mediate",
    "power command-body catalog",
)
s = once(
    s,
    " table prtest sdtest oneway anova ranksum median signrank signtest exlogistic",
    " table ci ratio dtable prtest sdtest oneway anova ranksum median signrank signtest exlogistic",
    "summary command-body catalog",
)

# Workflow-first Meta examples.
s = once(
    s,
    '''        else if "`cmd'" == "meta" {
            local expr_label "meta 子命令与完整参数（如 set / summarize / regress）"
            local example1 "meta summarize"
            local explain1 "对已经声明的 meta 数据进行汇总。"
            local example2 "meta regress x1 x2"
            local explain2 "执行 meta 回归；数据声明可使用 meta set / meta esize。"
        }
''',
    '''        else if "`cmd'" == "meta" {
            local expr_label "meta 子命令与完整参数（先 set/esize，再 summarize/regress/forest）"
            local example1 "meta set es se"
            local explain1 "第一步声明已计算好的效应量 es 和标准误 se。"
            local example2 "meta summarize"
            local explain2 "在已经声明的 meta 数据上汇总总体效应与异质性。"
        }
''',
    "meta workflow examples",
)

# Runnable resampling examples where a self-contained native command is possible.
old_resample = '''        else if strpos(" bootstrap jackknife permute simulate statsby ", " `cmd' ") {
            local expr_label "统计量 / 前缀参数 + 冒号后的命令（完整写出命令名后的部分）"
            if "`cmd'" == "bootstrap" {
                local example1 "bootstrap r(mean), reps(500): summarize y"
                local explain1 "对 summarize 返回的均值进行 bootstrap。"
            }
            else if "`cmd'" == "jackknife" {
                local example1 "jackknife r(mean): summarize y"
                local explain1 "对 summarize 返回的均值进行 jackknife。"
            }
            else {
                local example1 "help `cmd'"
                local explain1 "该命令包含前缀统计量、重复设置或冒号后的被执行命令，请按当前 help 填写完整主体。"
            }
        }
'''
new_resample = '''        else if strpos(" bootstrap jackknife permute simulate statsby ", " `cmd' ") {
            local expr_label "统计量 / 前缀参数 + 冒号后的命令（完整写出命令名后的部分）"
            if "`cmd'" == "bootstrap" {
                local example1 "bootstrap r(mean), reps(500): summarize y"
                local explain1 "对 summarize 返回的均值进行 bootstrap。"
            }
            else if "`cmd'" == "jackknife" {
                local example1 "jackknife r(mean): summarize y"
                local explain1 "对 summarize 返回的均值进行 jackknife。"
            }
            else if "`cmd'" == "permute" {
                local example1 "permute treatment _b[treatment], reps(500): regress y treatment x1 x2"
                local explain1 "随机置换 treatment，并用每次回归的 treatment 系数构造 permutation distribution。"
                local example2 "help permute"
                local explain2 "分层、聚类或复杂实验设计下必须让置换机制符合真实随机化结构。"
            }
            else if "`cmd'" == "statsby" {
                local example1 "statsby mean=r(mean) sd=r(sd), by(group): summarize y"
                local explain1 "对每个 group 重复 summarize y，并把均值、标准差收集成结果数据。"
                local example2 "help statsby"
                local explain2 "也可收集回归系数、检验统计量等 e()/r() 返回结果。"
            }
            else {
                local example1 "help simulate"
                local explain1 "simulate 需要一个能够在每次重复中生成随机数据并 return 标量的命令或 program；先定义该程序，再填写返回统计量与 reps()/seed()。"
            }
        }
'''
s = once(s, old_resample, new_resample, "resampling examples")

# Insert summary command-body semantics immediately before Bayes/power section.
power_block = '''        else if "`cmd'" == "power" {
            local expr_label "检验类型与设计参数（如 onemean 0 0.5, power(.8)）"
            local example1 "power onemean 0 0.5, power(.8)"
            local explain1 "一元均值检验的效能 / 样本量设计。"
            local example2 "power twomeans 0 0.5, power(.8)"
            local explain2 "两组均值比较的效能 / 样本量设计。"
        }
'''
summary_and_power = '''        else if "`cmd'" == "ci" {
            local expr_label "CI 类型 + 变量（means / proportions / variances）"
            local example1 "ci means y"
            local explain1 "计算 y 均值的置信区间。"
            local example2 "ci proportions binaryvar"
            local explain2 "计算二元变量成功比例的置信区间。"
        }
        else if "`cmd'" == "ratio" {
            local expr_label "分子/分母表达式（可一次填写多个 ratio）"
            local example1 "ratio sales/cost"
            local explain1 "估计总体均值之比 sales/cost，并报告标准误和置信区间。"
            local example2 "help ratio"
            local explain2 "多个 ratio、over()、权重和 VCE 设置可继续按当前 help 填写。"
        }
        else if "`cmd'" == "dtable" {
            local expr_label "连续变量 + i.分类变量 + by()/tests/export 等 Table 1 设置"
            local example1 "dtable price weight mpg i.rep78"
            local explain1 "连续变量报告均值/标准差，i.rep78 报告类别频数与比例。"
            local example2 "dtable age weight i.sex, by(group, tests)"
            local explain2 "按 group 生成 Table 1，并请求组间差异检验。"
        }
''' + power_block + '''        else if "`cmd'" == "ciwidth" {
            local expr_label "CI 设计类型 + width()/sd()/probwidth()/N() 等精度参数"
            local example1 "ciwidth twomeans, width(6) sd(5) probwidth(.96)"
            local explain1 "计算两独立样本均值差 CI 宽度不超过 6 所需的样本量。"
            local example2 "help ciwidth"
            local explain2 "可求样本量、CI 宽度或达到目标宽度的概率。"
        }
        else if "`cmd'" == "gsbounds" {
            local expr_label "efficacy()/futility() + nlooks() + power()/alpha() 等停止界值设定"
            local example1 "gsbounds, efficacy(obfleming) futility(obfleming) nlooks(5) power(.9) alpha(.05)"
            local explain1 "为 5 次分析计算 O'Brien–Fleming 疗效和无效停止界值。"
            local example2 "help gsbounds"
            local explain2 "边界类型、信息时间和单/双侧设计应在研究设计阶段明确。"
        }
        else if "`cmd'" == "gsdesign" {
            local expr_label "检验类型 + 原假设/备择参数 + SD/alpha/power/information/边界设定"
            local example1 "gsdesign twomeans 5.5 6.5, sd1(2) sd2(3) knownsds onesided alpha(.025) power(.9) nratio(2) information(50 65 80 90 100) efficacy(errobfleming) futility(errobfleming)"
            local explain1 "设计两样本均值 group-sequential trial，并计算每次 look 的停止界值与样本量。"
            local example2 "help gsdesign"
            local explain2 "可切换 one/two-sample means、proportions、log-rank 或 user-defined method。"
        }
'''
s = once(s, power_block, summary_and_power, "summary/power command-body semantics")

# Family-level copy for new commands.
family_marker = '    /* Family-level copy for catalog commands that rely on the generic syntax parser.\n'
family = '''    if strpos(" ameans centile ci mean proportion ratio total dtable ", " `cmd' ") {
        local title "`cmd' — 汇总统计与参数估计"
        local purpose1 "用于均值、百分位、置信区间、比例、比率、总量或 Table 1 等基础描述与推断任务。"
        local purpose2 "第一步只保留该命令真正需要的变量/表达式；分组、权重、VCE 和表格选项在运行前核对。"
    }
    else if strpos(" power ciwidth gsbounds gsdesign ", " `cmd' ") {
        local title "`cmd' — 效能、精度与样本量设计"
        local purpose1 "用于研究设计阶段计算 power、CI precision、停止界值或 group-sequential sample size。"
        local purpose2 "效应大小、alpha、power、CI width、looks 和边界方法都应来自预先设定的研究设计。"
    }

'''
if s.count(family_marker) != 1:
    raise SystemExit("family-level marker not found exactly once")
s = s.replace(family_marker, family_marker + family, 1)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------------- static contracts ----------------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''exact_core = {"exlogistic", "expoisson", "bitest", "bitesti", "ksmirnov", "symmetry", "tetrachoric", "tabi"}
'''
checks = '''summary_core = {"summarize", "ameans", "centile", "ci", "mean", "proportion", "ratio", "total", "tabstat", "tabulate", "table", "dtable"}
missing_summary = sorted(summary_core - stats_cmds)
if missing_summary:
    fail("summary/table commands missing: " + ", ".join(missing_summary))
power_core = {"power", "ciwidth", "gsbounds", "gsdesign"}
missing_power = sorted(power_core - stats_cmds)
if missing_power:
    fail("power/precision commands missing: " + ", ".join(missing_power))
for gated in ("dtable", "gsbounds", "gsdesign"):
    if f'foreach cmd in mediate hdidregress xthdidregress bmaregress dtable gsbounds gsdesign' not in registry:
        fail("Stata 18 summary/power version gate missing")
for needle in (
    'centile y, centile(25 50 75)',
    'ci means y',
    'ratio sales/cost',
    'dtable price weight mpg i.rep78',
    'ciwidth twomeans, width(6) sd(5) probwidth(.96)',
    'gsbounds, efficacy(obfleming) futility(obfleming) nlooks(5) power(.9) alpha(.05)',
    'gsdesign twomeans 5.5 6.5',
    'meta set es se',
    'permute treatment _b[treatment], reps(500): regress y treatment x1 x2',
    'statsby mean=r(mean) sd=r(sd), by(group): summarize y',
):
    if needle not in semantics:
        fail(f"summary/power/resampling semantic contract missing: {needle}")

'''
v = once(v, anchor, checks + anchor, "summary/power static contracts")
v = v.replace(
    'exact_epi_catalog=1 docs_source_split=1',
    'exact_epi_catalog=1 summary_catalog=1 power_precision=1 resampling_examples=1 meta_workflow=1 docs_source_split=1',
)
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_SUMMARY_POWER_PATCH_OK")
