from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, got {count}")
    return text.replace(old, new, 1)


# --- hxregistry: remove the nonexistent epoisson catalog entry ---
registry_path = Path("hxregistry.ado")
registry = registry_path.read_text(encoding="utf-8")
registry = replace_once(
    registry,
    "*! hxregistry 3.1.3  15aug2026",
    "*! hxregistry 3.1.4  16aug2026",
    "registry version",
)
registry = registry.replace(" eprobit eoprobit epoisson eintreg ", " eprobit eoprobit eintreg ")
if " epoisson " in f" {registry} ":
    raise SystemExit("epoisson still remains in hxregistry.ado")
registry_path.write_text(registry, encoding="utf-8", newline="\n")


# --- hxsemantics: promote syntax-sensitive panel commands and improve complex-model examples ---
sem_path = Path("hxsemantics.ado")
sem = sem_path.read_text(encoding="utf-8")
sem = replace_once(
    sem,
    "*! hxsemantics 1.4.2  16aug2026",
    "*! hxsemantics 1.4.3  16aug2026",
    "semantics version",
)
sem = sem.replace(" eprobit eoprobit epoisson eintreg ", " eprobit eoprobit eintreg ")

sem = replace_once(
    sem,
    "spregress spivregress spxtregress dsregress",
    "spregress spivregress spxtregress xtgee xttobit xtintreg xtfrontier xtabond xtdpdsys dsregress",
    "panel command-body catalog",
)

old_sem_gsem = '''        if inlist("`cmd'", "sem", "gsem") {
            local expr_label "模型方程（不重复命令名；如 (y <- x1 x2)）"
            local example1 "sem (y <- x1 x2)"
            local explain1 "直接用路径 / 方程语法描述结构模型。"
            local example2 "gsem (y <- x1 x2, family(bernoulli) link(logit))"
            local explain2 "gsem 的 family/link 可与方程写在同一主体中。"
        }
'''
new_sem_gsem = '''        if "`cmd'" == "sem" {
            local expr_label "线性 SEM 路径 / 方程（不重复 sem；如 (y <- x1 x2)）"
            local example1 "sem (y <- x1 x2)"
            local explain1 "最小线性路径模型：用 x1、x2 解释连续结果 y。"
            local example2 "sem (L1 -> m1 m2) (L2 -> m3 m4) (L3 <- L1 L2)"
            local explain2 "测量模型和结构路径可以在同一条 sem 命令中组合。"
        }
        else if "`cmd'" == "gsem" {
            local expr_label "广义 SEM 方程 + family()/link()/随机效应/潜在类别设定"
            local example1 "gsem (y <- x1 x2, family(bernoulli) link(logit))"
            local explain1 "对二元结果 y 拟合 logit 链接的广义结构方程。"
            local example2 "help gsem"
            local explain2 "多层、潜在类别、选择模型等 gsem 结构差异很大，复杂模型继续按当前 help 核对。"
        }
'''
sem = replace_once(sem, old_sem_gsem, new_sem_gsem, "sem/gsem split")

old_selection = '''        else if strpos(" heckman heckprobit heckoprobit heckpoisson ", " `cmd' ") {
            local expr_label "结果方程 + 选择方程主体（含 select() 等命令特有结构）"
            local example1 "help `cmd'"
            local explain1 "样本选择模型至少包含结果方程和选择机制，完整主体可以明确两套变量角色。"
        }
'''
new_selection = '''        else if strpos(" heckman heckprobit heckoprobit heckpoisson ", " `cmd' ") {
            local expr_label "结果方程 + select() 选择方程（两套变量角色必须同时明确）"
            if "`cmd'" == "heckman" {
                local example1 "heckman wage educ age, select(married children educ age)"
                local explain1 "连续结果 wage 只在被选择样本中观察；select() 描述进入样本的机制。"
                local example2 "help heckman"
                local explain2 "需要显式选择指示变量、两步法或 VCE 设置时继续核对当前 help。"
            }
            else if "`cmd'" == "heckprobit" {
                local example1 "heckprobit y x1 x2, select(selected = z1 z2 x1)"
                local explain1 "主方程是二元 Probit；selected 及 z1、z2、x1 构成选择方程。"
                local example2 "help heckprobit"
                local explain2 "运行前确认选择指示的 0/1 编码和排除限制。"
            }
            else if "`cmd'" == "heckoprobit" {
                local example1 "heckoprobit satisfaction educ age, select(work=educ age i.married##c.children)"
                local explain1 "主结果是有序类别，work 方程描述结果被观察到的选择过程。"
                local example2 "help heckoprobit"
                local explain2 "阈值、选择方程和标准误设置都应按研究设计核对。"
            }
            else {
                local example1 "heckpoisson patents investment i.firmtype, select(applied = investment size i.firmtype)"
                local explain1 "主方程解释计数结果 patents，applied 方程处理非随机样本选择。"
                local example2 "help heckpoisson"
                local explain2 "选择机制与计数过程应分别有清楚的经济含义。"
            }
        }
'''
sem = replace_once(sem, old_selection, new_selection, "sample-selection examples")

old_endog = '''        else if strpos(" eregress eprobit eoprobit eintreg ", " `cmd' ") {
            local expr_label "主结果方程 + 内生协变量 / 处理方程主体"
            local example1 "help `cmd'"
            local explain1 "扩展回归模型可能同时包含多个内生方程，页面使用完整原生主体避免丢失方程结构。"
        }
'''
new_endog = '''        else if strpos(" eregress eprobit eoprobit eintreg ", " `cmd' ") {
            local expr_label "主结果方程 + endogenous()/select()/entreat() 等扩展方程"
            if "`cmd'" == "eregress" {
                local example1 "eregress y x1, endogenous(x2 = x3 x4)"
                local explain1 "在线性结果方程中把 x2 作为内生协变量，并用 x3、x4 建模。"
            }
            else if "`cmd'" == "eprobit" {
                local example1 "eprobit y x1, endogenous(x2 = x3 x4)"
                local explain1 "二元 Probit 结果方程，同时显式建立 x2 的内生协变量方程。"
            }
            else if "`cmd'" == "eoprobit" {
                local example1 "eoprobit y x1, endogenous(x2 = x3 x4)"
                local explain1 "有序 Probit 结果方程，同时显式建立 x2 的内生协变量方程。"
            }
            else {
                local example1 "eintreg ylower yupper x1, endogenous(x2 = x3 x4)"
                local explain1 "区间结果必须同时给出下界和上界，再加入内生协变量方程。"
            }
            local example2 "help `cmd'"
            local explain2 "ERM 还可组合 select() 与 entreat()；复杂联立结构运行前核对当前 Stata help。"
        }
'''
sem = replace_once(sem, old_endog, new_endog, "endogenous-covariate examples")

mixed_marker = '''        else if strpos(" mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm ", " `cmd' ") {
'''
if sem.count(mixed_marker) != 1:
    raise SystemExit(f"mixed marker count={sem.count(mixed_marker)}")
panel_blocks = '''        else if "`cmd'" == "xtgee" {
            local expr_label "Y + X + family() + link() + corr()（GEE 核心设定）"
            local example1 "xtgee union age not_smsa, family(binomial) link(probit) corr(exchangeable)"
            local explain1 "二元结果采用 Probit 链接，并用 exchangeable 工作相关结构处理面板内相关。"
            local example2 "xtgee y x1 x2, family(gaussian) link(identity) corr(independent)"
            local explain2 "连续结果可使用 Gaussian + identity；相关结构应由数据与研究设计决定。"
        }
        else if "`cmd'" == "xttobit" {
            local expr_label "Y + X + ll()/ul() 截尾界限"
            local example1 "xttobit y x1 x2, ll(0)"
            local explain1 "随机效应面板 Tobit，结果在 0 处左删失。"
            local example2 "help xttobit"
            local explain2 "右删失或双侧删失时继续设置 ul() / ll()。"
        }
        else if "`cmd'" == "xtintreg" {
            local expr_label "结果下界 + 结果上界 + X（例如 ylower yupper x1 x2）"
            local example1 "xtintreg ylower yupper x1 x2 x3"
            local explain1 "ylower、yupper 分别记录区间结果的下界和上界；这两个结果变量都属于核心语法。"
            local example2 "help xtintreg"
            local explain2 "左删失、右删失和精确观测通过上下界变量中的缺失/相等关系表达。"
        }
        else if "`cmd'" == "xtfrontier" {
            local expr_label "Y + X + ti/tvd + production/cost 等前沿设定"
            local example1 "xtfrontier y x1 x2, ti"
            local explain1 "估计时间不变 inefficiency 的面板随机前沿模型。"
            local example2 "xtfrontier y x1 x2, tvd"
            local explain2 "tvd 允许 inefficiency 随时间按共同衰减结构变化。"
        }
        else if "`cmd'" == "xtabond" {
            local expr_label "Y + X + lags()/maxldep()/pre()/endogenous()/twostep 等动态面板设定"
            local example1 "xtabond y x1 x2, lags(1)"
            local explain1 "Arellano–Bond 差分 GMM；lags(1) 指定因变量动态滞后阶数。"
            local example2 "help xtabond"
            local explain2 "工具变量集合、预定变量、两步估计和 AR 检验会显著影响结果，运行前逐项核对。"
        }
        else if "`cmd'" == "xtdpdsys" {
            local expr_label "Y + X + lags()/maxldep()/pre()/endogenous()/twostep 等系统 GMM 设定"
            local example1 "xtdpdsys y x1 x2, lags(1)"
            local explain1 "Arellano–Bover/Blundell–Bond 系统估计同时利用差分方程和水平方程矩条件。"
            local example2 "help xtdpdsys"
            local explain2 "系统 GMM 的工具变量数量与有效性需要在研究中单独诊断。"
        }
'''
sem = sem.replace(mixed_marker, panel_blocks + mixed_marker, 1)

family_marker = '''    /* Family-level copy for catalog commands that rely on the generic syntax parser.
'''
if sem.count(family_marker) != 1:
    raise SystemExit("family-level marker not found exactly once")
generic_panel_examples = '''    /* Panel estimators whose Y/X grammar remains safe still get command-specific examples. */
    if "`cmd'" == "xtpoisson" {
        local example1 "xtpoisson y x1 x2, fe"
        local explain1 "固定效应面板 Poisson；运行前页面会先按所选数据结构执行 xtset。"
        local example2 "xtpoisson y x1 x2, re"
        local explain2 "随机效应面板 Poisson。"
    }
    else if "`cmd'" == "xtnbreg" {
        local example1 "xtnbreg y x1 x2, re"
        local explain1 "随机效应面板负二项模型。"
        local example2 "xtnbreg y x1 x2, fe"
        local explain2 "固定效应参数化应结合研究目标和 Stata 定义解释。"
    }
    else if "`cmd'" == "xtcloglog" {
        local example1 "xtcloglog y x1 x2, re"
        local explain1 "随机效应面板 complementary log-log 模型。"
        local example2 "help xtcloglog"
        local explain2 "总体平均等模型选项按当前 Stata 版本核对。"
    }
    else if "`cmd'" == "xtoprobit" {
        local example1 "xtoprobit y x1 x2"
        local explain1 "有序结果的随机效应面板 Probit。"
        local example2 "help xtoprobit"
        local explain2 "先确认结果类别具有明确顺序。"
    }
    else if "`cmd'" == "xtmlogit" {
        local example1 "xtmlogit y x1 x2, re"
        local explain1 "无序多类别结果的随机效应面板 multinomial logit。"
        local example2 "help xtmlogit"
        local explain2 "基准类别、固定/随机效应可用性和面板内变异要求运行前核对。"
    }

'''
sem = sem.replace(family_marker, generic_panel_examples + family_marker, 1)

old_fmm_irt = '''    else if strpos(" fmm irt ", " `cmd' ") {
        local title "`cmd' — 潜在类别与测量模型"
        local purpose1 "用于有限混合、潜在类别或项目反应理论分析。"
        local purpose2 "类别数、题项模型和潜在结构高度依赖具体研究设计，运行前请按 Stata 当前语法确认。"
    }
'''
new_fmm_irt = '''    else if "`cmd'" == "fmm" {
        local title "fmm — 有限混合模型"
        local purpose1 "把总体表示为若干未观测组分，并允许不同组分拥有不同回归参数或分布。"
        local purpose2 "第一步先确定潜在组分数量和冒号后的基础估计命令；类别数应结合理论与模型比较判断。"
    }
    else if "`cmd'" == "irt" {
        local title "irt — 项目反应理论"
        local purpose1 "用 Rasch、1PL/2PL/3PL、GRM 等模型分析潜在能力与题项反应之间的关系。"
        local purpose2 "先确定题项类型与 IRT 模型，再选择全部题项变量；不同题型不能随意套用同一响应模型。"
    }
'''
sem = replace_once(sem, old_fmm_irt, new_fmm_irt, "fmm/irt family split")

if " epoisson " in f" {sem} ":
    raise SystemExit("epoisson still remains in hxsemantics.ado")
sem_path.write_text(sem, encoding="utf-8", newline="\n")


# --- static audit: make the catalog correction and new semantics non-regressible ---
verify_path = Path("tools/verify_static_contracts.py")
verify = verify_path.read_text(encoding="utf-8")
verify = replace_once(
    verify,
    'java = read("src/main/java/com/hexie/stata/HxWorkbench.java")\n',
    'java = read("src/main/java/com/hexie/stata/HxWorkbench.java")\nsemantics = read("hxsemantics.ado")\n',
    "static verifier semantics load",
)
anchor = '''for official in ("didregress", "xtdidregress"):
    if official not in stats_cmds:
        fail(f"official DID command missing from Statistics catalog: {official}")

'''
checks = '''# Catalog correctness: Stata ERM has eregress/eintreg/eprobit/eoprobit; epoisson is not a public command.
if "epoisson" in stats_cmds or "epoisson" in registry or "epoisson" in semantics:
    fail("nonexistent epoisson leaked into Statistics catalog or semantics")
for official in ("eregress", "eintreg", "eprobit", "eoprobit"):
    if official not in stats_cmds:
        fail(f"official extended-regression command missing: {official}")
for needle in (
    'xtgee union age not_smsa, family(binomial) link(probit) corr(exchangeable)',
    'xtintreg ylower yupper x1 x2 x3',
    'xtfrontier y x1 x2, tvd',
    'xtabond y x1 x2, lags(1)',
    'xtdpdsys y x1 x2, lags(1)',
    'heckpoisson patents investment i.firmtype, select(applied = investment size i.firmtype)',
    'eprobit y x1, endogenous(x2 = x3 x4)',
):
    if needle not in semantics:
        fail(f"long-tail command semantic contract missing: {needle}")

'''
verify = replace_once(verify, anchor, anchor + checks, "static catalog checks")
verify = verify.replace(
    '"legacy_did_hidden=1 event_plot_graph=1 official_did_stats=1 docs_source_split=1"',
    '"legacy_did_hidden=1 event_plot_graph=1 official_did_stats=1 epoisson_removed=1 longtail_semantics=1 docs_source_split=1"',
)
verify_path.write_text(verify, encoding="utf-8", newline="\n")

print("HX_LONGTAIL_ROUND2_PATCH_OK")
