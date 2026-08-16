from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------- registry ----------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.15  16aug2026", "*! hxregistry 3.1.16  16aug2026", "registry version")

old_panel_catalog = "xtreg xtlogit xtprobit xtologit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtivreg xtpcse xtregar xtrc xtstreg xtabond xtdpdsys mixed"
new_panel_catalog = "xtreg xtlogit xtprobit xtologit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtivreg xtpcse xtgls xtregar xtrc xtstreg xteregress xteprobit xteoprobit xteintreg xtheckman xthtaylor xtabond xtdpdsys xtdpd xtunitroot xtcointtest xtdescribe xtsum xttab xtdata mixed"
r = once(r, old_panel_catalog, new_panel_catalog, "panel round2 statistics catalog")

old_route = '''    else if inlist(`"`method'"', "纵向/面板数据", "panel_longitudinal") {
        local view "xtreg xtlogit xtprobit xtologit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit"
        if c(stata_version) >= 17 local view "`view' xtmlogit"
        local view "`view' xtfrontier xtivreg xtpcse xtregar xtrc xtstreg xtabond xtdpdsys"
    }
'''
new_route = '''    else if inlist(`"`method'"', "纵向/面板数据", "panel_longitudinal") {
        local view "xtreg xtlogit xtprobit xtologit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit"
        if c(stata_version) >= 17 local view "`view' xtmlogit"
        local view "`view' xtfrontier xtivreg xtpcse xtgls xtregar xtrc xtstreg"
        local view "`view' xteregress xteprobit xteoprobit xteintreg xtheckman xthtaylor"
        local view "`view' xtabond xtdpdsys xtdpd xtunitroot xtcointtest xtdescribe xtsum xttab xtdata"
    }
'''
r = once(r, old_route, new_route, "panel round2 method route")

keyword_anchor = '        local key_stintcox "stintcox interval censored Cox 区间删失 生存 Cox 比例风险"\n'
keyword_add = '''        local key_xteregress "xteregress extended random effects panel ERM 面板 扩展回归 内生协变量 选择 处理"
        local key_xteprobit "xteprobit extended random effects probit panel ERM 面板 扩展 Probit 内生协变量"
        local key_xteoprobit "xteoprobit extended ordered probit panel ERM 面板 扩展 有序 Probit"
        local key_xteintreg "xteintreg extended interval regression panel ERM 面板 扩展 区间回归"
        local key_xtheckman "xtheckman panel sample selection Heckman 面板 样本选择 随机效应"
        local key_xthtaylor "xthtaylor Hausman Taylor panel 面板 内生 个体效应 工具变量"
        local key_xtdpd "xtdpd dynamic panel GMM 动态面板 差分 系统 GMM 工具变量"
        local key_xtgls "xtgls panel generalized least squares FGLS 面板 广义最小二乘 异方差 自相关"
        local key_xtunitroot "xtunitroot panel unit root test 面板 单位根 平稳性"
        local key_xtcointtest "xtcointtest panel cointegration Kao Pedroni Westerlund 面板 协整检验"
        local key_xtdescribe "xtdescribe panel pattern 面板结构 描述 平衡 非平衡"
        local key_xtsum "xtsum panel summary within between 面板 描述统计 组内 组间"
        local key_xttab "xttab panel tabulation within between 面板 分类统计 组内 组间"
        local key_xtdata "xtdata panel transform within between 面板 数据变换 固定效应 随机效应"
'''
r = once(r, keyword_anchor, keyword_anchor + keyword_add, "panel round2 search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------- semantics ----------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.14  16aug2026", "*! hxsemantics 1.4.15  16aug2026", "semantics version")

old_body_panel = " spregress spivregress spxtregress xtivreg xtpcse xtregar xtrc xtstreg xtgee xttobit xtintreg xtfrontier xtabond xtdpdsys "
new_body_panel = " spregress spivregress spxtregress xtivreg xtpcse xtgls xtregar xtrc xtstreg xteregress xteprobit xteoprobit xteintreg xtheckman xthtaylor xtdpd xtunitroot xtcointtest xtdescribe xtsum xttab xtdata xtgee xttobit xtintreg xtfrontier xtabond xtdpdsys "
s = once(s, old_body_panel, new_body_panel, "panel round2 command-body catalog")

marker = '''        else if "`cmd'" == "xtivreg" {
'''
if s.count(marker) != 1:
    raise SystemExit(f"panel round2 semantic marker count={s.count(marker)}")
blocks = '''        else if "`cmd'" == "xteregress" {
            local expr_label "Y + X + endogenous()/select()/entreat() 扩展随机效应方程"
            local example1 "xteregress y x1, endogenous(x2 = x3 x4)"
            local explain1 "在线性随机效应面板结果方程中，把 x2 作为内生协变量并用 x3、x4 建模。"
            local example2 "help xteregress"
            local explain2 "还可联合 select() 与 entreat()；复杂多方程结构应直接保留 Stata ERM 原生语法。"
        }
        else if "`cmd'" == "xteprobit" {
            local expr_label "二元 Y + X + endogenous()/select()/entreat() 扩展随机效应 Probit"
            local example1 "xteprobit y x1, endogenous(x2 = x3 x4)"
            local explain1 "在随机效应 Probit 面板模型中显式建立 x2 的内生协变量方程。"
            local example2 "help xteprobit"
            local explain2 "内生协变量、样本选择和处理分配可在同一 ERM 框架联合建模。"
        }
        else if "`cmd'" == "xteoprobit" {
            local expr_label "有序 Y + X + endogenous()/select()/entreat() 扩展随机效应有序 Probit"
            local example1 "xteoprobit y x1, endogenous(x2 = x3 x4)"
            local explain1 "对面板有序结果建立随机效应 ordered-probit 主方程和内生协变量方程。"
            local example2 "help xteoprobit"
            local explain2 "结果类别必须有明确顺序；多方程结构继续使用 ERM 原生 options。"
        }
        else if "`cmd'" == "xteintreg" {
            local expr_label "结果下界 + 上界 + X + endogenous()/select()/entreat()"
            local example1 "xteintreg ylower yupper x1, endogenous(x2 = x3 x4)"
            local explain1 "区间结果由 ylower/yupper 表达，并在随机效应面板框架中处理 x2 的内生性。"
            local example2 "help xteintreg"
            local explain2 "左删失、右删失、精确值与区间值的编码应先核对上下界变量。"
        }
        else if "`cmd'" == "xtheckman" {
            local expr_label "结果方程 + select() 选择方程（随机效应面板 Heckman）"
            local example1 "xtheckman income c.age##c.age i.training#(c.exp##c.exp), select(working = age exp i.region i.training)"
            local explain1 "income 只在 working=1 时被观察；select() 显式建模进入结果样本的概率。"
            local example2 "help xtheckman"
            local explain2 "模型同时允许个体随机效应与结果/选择过程相关，选择方程属于核心识别结构。"
        }
        else if "`cmd'" == "xthtaylor" {
            local expr_label "Y + X + endog()（与个体效应相关的解释变量）"
            local example1 "xthtaylor y x1 x2 z1, endog(x2)"
            local explain1 "Hausman–Taylor 通过模型内部工具变量处理与个体效应相关的 x2，同时保留时间不变变量 z1。"
            local example2 "help xthtaylor"
            local explain2 "endog() 指变量与个体效应相关，识别依赖时间变/不变且外生/内生变量的划分。"
        }
        else if "`cmd'" == "xtdpd" {
            local expr_label "动态方程 + div()/dgmmiv()/lgmmiv() 等矩条件与工具变量集合"
            local example1 "xtdpd L(0/1).y x, div(x) dgmmiv(y)"
            local explain1 "直接声明动态回归项以及差分方程 GMM 工具变量；比 xtabond/xtdpdsys 提供更灵活的矩条件。"
            local example2 "help xtdpd"
            local explain2 "工具变量滞后区间和数量会直接影响识别与有限样本表现，运行前逐项核对。"
        }
        else if "`cmd'" == "xtgls" {
            local expr_label "Y + X + panels() + corr() 等 FGLS 协方差结构"
            local example1 "xtgls y x1 x2, panels(heteroskedastic) corr(ar1)"
            local explain1 "允许 panel-level heteroskedasticity，并用共同 AR(1) 描述面板内序列相关。"
            local example2 "help xtgls"
            local explain2 "FGLS 对 N/T 与协方差结构假设较敏感，panels() 和 corr() 应由数据结构决定。"
        }
        else if "`cmd'" == "xtunitroot" {
            local expr_label "检验方法 + 变量 + lags()/trend/demean 等单位根设定"
            local example1 "xtunitroot ips hprice"
            local explain1 "对 hprice 进行 Im–Pesaran–Shin 面板单位根检验；该命令需要已声明的 panel/time。"
            local example2 "help xtunitroot"
            local explain2 "LLC、HT、Breitung、IPS、Fisher、Hadri 等检验的 N/T 渐近条件并不相同。"
        }
        else if "`cmd'" == "xtcointtest" {
            local expr_label "Kao/Pedroni/Westerlund + 协整变量列表"
            local example1 "xtcointtest kao hprice aprice nprice"
            local explain1 "在已确认变量存在单位根后，使用 Kao 检验考察 panel 长期协整关系。"
            local example2 "help xtcointtest"
            local explain2 "Kao、Pedroni、Westerlund 对协整向量与面板异质性的假设不同，应与研究设定对应。"
        }
        else if "`cmd'" == "xtdescribe" {
            local expr_label "面板结构描述（通常直接运行；可补充 patterns 等 options）"
            local example1 "xtdescribe"
            local explain1 "查看 panel 数量、时间跨度、T_i 分布以及平衡/非平衡观测模式。"
            local example2 "help xtdescribe"
            local explain2 "适合在正式面板回归前检查面板覆盖、缺口与时间模式。"
        }
        else if "`cmd'" == "xtsum" {
            local expr_label "要汇总的变量列表"
            local example1 "xtsum hours"
            local explain1 "同时报告 hours 的 overall、between 和 within 变异，直接对应面板数据的三个层次。"
            local example2 "help xtsum"
            local explain2 "within 与 between 的标准差含义不同，不能按普通 summarize 的单一方差解释。"
        }
        else if "`cmd'" == "xttab" {
            local expr_label "一个分类变量"
            local example1 "xttab msp"
            local explain1 "把分类变量的总体频率、panel 间出现比例和 panel 内状态变化分开汇总。"
            local example2 "help xttab"
            local explain2 "适合检查二元/分类状态在面板内是否具有足够变化。"
        }
        else if "`cmd'" == "xtdata" {
            local expr_label "要转换的变量 + fe/re/be 等变换设定"
            local example1 "xtdata y x1 x2, fe clear"
            local explain1 "把当前变量转换为 fixed-effects within 形式；clear 会替换内存数据，运行前必须确认已保存原数据。"
            local example2 "help xtdata"
            local explain2 "这是数据变换工具，会影响后续分析数据；用于手工估计前应保留可恢复的原始数据。"
        }
'''
s = s.replace(marker, blocks + marker, 1)

# Separate utility/test copy from model copy so titles remain accurate.
family_marker = '''    else if strpos(" xtologit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtivreg xtpcse xtregar xtrc xtstreg xtabond xtdpdsys ", " `cmd' ") {
'''
if s.count(family_marker) != 1:
    raise SystemExit(f"panel family marker count={s.count(family_marker)}")
utility_family = '''    else if strpos(" xtunitroot xtcointtest xtdescribe xtsum xttab xtdata ", " `cmd' ") {
        local title "`cmd' — 面板数据工具与检验"
        local purpose1 "用于检查面板结构、分解 within/between 变异、变换 panel 数据，或执行单位根与协整检验。"
        local purpose2 "页面会先按 panel/time 执行 xtset；数据变换或时间序列检验还需核对命令自身的样本与渐近条件。"
        local panel_label "个体 / 面板变量"
        if inlist("`cmd'", "xtunitroot", "xtcointtest") local time_label "时间变量（检验必填）"
        else local time_label "时间变量（可按数据结构留空）"
    }
    else if strpos(" xtologit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtivreg xtpcse xtgls xtregar xtrc xtstreg xteregress xteprobit xteoprobit xteintreg xtheckman xthtaylor xtdpd xtabond xtdpdsys ", " `cmd' ") {
'''
s = s.replace(family_marker, utility_family, 1)
s = once(
    s,
    '        local purpose1 "用于面板数据下的有序/计数结果、IV、PCSE、序列相关、随机系数、生存、GEE、前沿或动态模型。"\n',
    '        local purpose1 "用于面板数据下的有序/计数结果、IV、FGLS/PCSE、序列相关、ERM、样本选择、Hausman–Taylor、生存、GEE、前沿或动态模型。"\n',
    "panel round2 family purpose",
)
s = once(
    s,
    '        if inlist("`cmd\'", "xtabond", "xtdpdsys") local time_label "时间变量（动态面板必填）"\n',
    '        if inlist("`cmd\'", "xtabond", "xtdpdsys", "xtdpd") local time_label "时间变量（动态面板必填）"\n',
    "panel round2 family time label",
)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------- Java panel declaration workflow ----------
jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")
old_panel_list = '''            "xtlogit", "xtprobit", "xtologit", "xtpoisson", "xtnbreg", "xtgee", "xttobit", "xtcloglog",
            "xtintreg", "xtoprobit", "xtmlogit", "xtfrontier", "xtivreg", "xtpcse", "xtregar", "xtrc", "xtstreg",
            "xtabond", "xtdpdsys", "xthdidregress"
'''
new_panel_list = '''            "xtlogit", "xtprobit", "xtologit", "xtpoisson", "xtnbreg", "xtgee", "xttobit", "xtcloglog",
            "xtintreg", "xtoprobit", "xtmlogit", "xtfrontier", "xtivreg", "xtpcse", "xtgls", "xtregar", "xtrc", "xtstreg",
            "xteregress", "xteprobit", "xteoprobit", "xteintreg", "xtheckman", "xthtaylor", "xtabond", "xtdpdsys", "xtdpd",
            "xtunitroot", "xtcointtest", "xtdescribe", "xtsum", "xttab", "xtdata", "xthdidregress"
'''
j = once(j, old_panel_list, new_panel_list, "Java panel round2 list")
j = once(
    j,
    'return Arrays.asList("xtabond", "xtdpdsys", "xthdidregress").contains(command);',
    'return Arrays.asList("xtabond", "xtdpdsys", "xtdpd", "xtunitroot", "xtcointtest", "xthdidregress").contains(command);',
    "Java panel time-required list",
)
j = once(
    j,
    '"当前动态面板模型需要时间变量，用于识别滞后期。请同时选择面板变量和时间变量。"',
    '"当前命令需要时间变量，用于动态滞后或面板时间序列检验。请同时选择面板变量和时间变量。"',
    "Java panel declaration warning",
)
j = once(
    j,
    '"运行时会先执行 xtset；当前动态面板模型必须同时指定面板变量和时间变量。"',
    '"运行时会先执行 xtset；当前命令必须同时指定面板变量和时间变量。"',
    "Java panel setup hint",
)
j = once(
    j,
    '"当前命令需要时间变量；xtabond / xtdpdsys 用于动态滞后，xthdidregress 用于识别处理 cohort 和时间。"',
    '"当前命令需要时间变量；动态面板、单位根/协整检验或异质 DID 都依赖明确的 panel-time 结构。"',
    "Java panel validation warning",
)
jp.write_text(j, encoding="utf-8", newline="\n")


# ---------- static contracts ----------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'panel_extension_core = {"xtologit", "xtivreg", "xtpcse", "xtregar", "xtrc", "xtstreg"}\n'
round2_checks = '''panel_round2_core = {
    "xteregress", "xteprobit", "xteoprobit", "xteintreg", "xtheckman", "xthtaylor",
    "xtdpd", "xtgls", "xtunitroot", "xtcointtest", "xtdescribe", "xtsum", "xttab", "xtdata",
}
missing_panel_round2 = sorted(panel_round2_core - stats_cmds)
if missing_panel_round2:
    fail("panel-data round-2 commands missing: " + ", ".join(missing_panel_round2))
for needle in (
    'xteregress y x1, endogenous(x2 = x3 x4)',
    'xteprobit y x1, endogenous(x2 = x3 x4)',
    'xteoprobit y x1, endogenous(x2 = x3 x4)',
    'xteintreg ylower yupper x1, endogenous(x2 = x3 x4)',
    'xtheckman income c.age##c.age i.training#(c.exp##c.exp), select(working = age exp i.region i.training)',
    'xthtaylor y x1 x2 z1, endog(x2)',
    'xtdpd L(0/1).y x, div(x) dgmmiv(y)',
    'xtgls y x1 x2, panels(heteroskedastic) corr(ar1)',
    'xtunitroot ips hprice',
    'xtcointtest kao hprice aprice nprice',
    'xtdescribe',
    'xtsum hours',
    'xttab msp',
    'xtdata y x1 x2, fe clear',
):
    if needle not in semantics:
        fail(f"panel round-2 semantic contract missing: {needle}")

'''
v = once(v, anchor, round2_checks + anchor, "panel round2 static contracts")
# Extend the Java routing assertion to the new panel tools and ensure time-critical commands stay protected.
time_anchor = '''for panel_cmd in panel_extension_core:
    if f'"{panel_cmd}"' not in panel_method_block:
        fail(f"Java panel auto-xtset routing missing: {panel_cmd}")
'''
time_new = '''for panel_cmd in panel_extension_core | panel_round2_core:
    if f'"{panel_cmd}"' not in panel_method_block:
        fail(f"Java panel auto-xtset routing missing: {panel_cmd}")
for time_required in ("xtdpd", "xtunitroot", "xtcointtest"):
    if f'"{time_required}"' not in java[java.find("private static boolean isGenericPanelTimeRequired"):java.find("private JPanel genericCardBody", java.find("private static boolean isGenericPanelTimeRequired"))]:
        fail(f"Java panel time-required routing missing: {time_required}")
'''
v = once(v, time_anchor, time_new, "panel round2 Java contracts")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_PANEL_ROUND2_PATCH_OK")
