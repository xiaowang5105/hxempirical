from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------- registry ----------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.14  16aug2026", "*! hxregistry 3.1.15  16aug2026", "registry version")

old_catalog = "spregress spivregress spxtregress xtreg xtlogit xtprobit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtabond xtdpdsys mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm stset sts stcox streg stcrreg"
new_catalog = "spregress spivregress spxtregress xtreg xtlogit xtprobit xtologit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtivreg xtpcse xtregar xtrc xtstreg xtabond xtdpdsys mixed mecloglog melogit meprobit mepoisson menbreg meologit meoprobit meintreg menl mestreg metobit meglm stset sts stcox streg stintreg stintcox stcrreg"
r = once(r, old_catalog, new_catalog, "panel mixed survival catalog")

r = once(
    r,
    "foreach cmd in didregress xtdidregress telasso ziologit {",
    "foreach cmd in didregress xtdidregress telasso ziologit xtmlogit stintcox {",
    "Stata 17 version gate",
)

old_panel_route = '    else if inlist(`"`method\'"\', "纵向/面板数据", "panel_longitudinal") local view "xtreg xtlogit xtprobit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtabond xtdpdsys"\n'
new_panel_route = '''    else if inlist(`"`method'"', "纵向/面板数据", "panel_longitudinal") {
        local view "xtreg xtlogit xtprobit xtologit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit"
        if c(stata_version) >= 17 local view "`view' xtmlogit"
        local view "`view' xtfrontier xtivreg xtpcse xtregar xtrc xtstreg xtabond xtdpdsys"
    }
'''
r = once(r, old_panel_route, new_panel_route, "panel method route")

r = once(
    r,
    '    else if inlist(`"`method\'"\', "多层混合效应模型", "mixed_effects") local view "mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm"\n',
    '    else if inlist(`"`method\'"\', "多层混合效应模型", "mixed_effects") local view "mixed mecloglog melogit meprobit mepoisson menbreg meologit meoprobit meintreg menl mestreg metobit meglm"\n',
    "mixed method route",
)

r = once(
    r,
    '    else if inlist(`"`method\'"\', "生存分析", "survival") local view "stset sts stcox streg stcrreg"\n',
    '''    else if inlist(`"`method'"', "生存分析", "survival") {
        local view "stset sts stcox streg stintreg"
        if c(stata_version) >= 17 local view "`view' stintcox"
        local view "`view' stcrreg"
    }
''',
    "survival method route",
)

keyword_anchor = '        local key_xtprobit "xtprobit panel binary 面板 二元 概率回归"\n'
keyword_add = '''        local key_xtologit "xtologit panel ordered logit 面板 有序 逻辑回归 随机效应"
        local key_xtivreg "xtivreg panel instrumental variables 面板 工具变量 内生性 固定效应 随机效应"
        local key_xtpcse "xtpcse panel corrected standard errors 面板校正标准误 截面相关 AR1"
        local key_xtregar "xtregar panel AR1 serial correlation 面板 自相关 固定效应 随机效应"
        local key_xtrc "xtrc random coefficients panel 随机系数 面板回归"
        local key_xtstreg "xtstreg panel survival random effects 生存分析 面板 随机效应"
        local key_mecloglog "mecloglog mixed effects complementary loglog 多层 混合效应 二元"
        local key_meintreg "meintreg multilevel interval regression 多层 区间回归 随机系数"
        local key_menl "menl mixed effects nonlinear regression 多层 非线性 混合效应"
        local key_stintreg "stintreg interval censored survival 区间删失 生存 参数模型"
        local key_stintcox "stintcox interval censored Cox 区间删失 生存 Cox 比例风险"
'''
r = once(r, keyword_anchor, keyword_anchor + keyword_add, "search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------- semantics ----------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.13  16aug2026", "*! hxsemantics 1.4.14  16aug2026", "semantics version")

# Add complex commands to the guided native-command template.
s = once(
    s,
    " ivprobit ivtobit ivpoisson ivfprobit ivqregress mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm lasso ",
    " ivprobit ivtobit ivpoisson ivfprobit ivqregress mixed mecloglog melogit meprobit mepoisson menbreg meologit meoprobit meintreg menl mestreg metobit meglm lasso ",
    "mixed command-body catalog",
)
s = once(
    s,
    " npregress stset streg stcrreg arima ",
    " npregress stset streg stintreg stintcox stcrreg arima ",
    "survival command-body catalog",
)
s = once(
    s,
    " spregress spivregress spxtregress xtgee xttobit xtintreg xtfrontier xtabond xtdpdsys ",
    " spregress spivregress spxtregress xtivreg xtpcse xtregar xtrc xtstreg xtgee xttobit xtintreg xtfrontier xtabond xtdpdsys ",
    "panel command-body catalog",
)

panel_marker = '''        else if "`cmd'" == "xtgee" {
'''
if s.count(panel_marker) != 1:
    raise SystemExit(f"panel semantic marker count={s.count(panel_marker)}")
panel_blocks = '''        else if "`cmd'" == "xtivreg" {
            local expr_label "Y + 外生 X + (内生变量 = 工具变量) + fe/re 等面板 IV 设定"
            local example1 "xtivreg y x1 (x2 = z1 z2), fe"
            local explain1 "在面板固定效应模型中，把 x2 视为内生变量并使用 z1、z2 作为排除工具变量。"
            local example2 "help xtivreg"
            local explain2 "FE、RE、BE 与 G2SLS/EC2SLS 等可用设定应按识别策略和当前 Stata help 核对。"
        }
        else if "`cmd'" == "xtpcse" {
            local expr_label "Y + X + correlation() + pairwise/hetonly 等 PCSE 设定"
            local example1 "xtpcse y x1 x2, correlation(ar1) pairwise"
            local explain1 "使用面板校正标准误，并允许面板内 AR(1) 相关；pairwise 控制协方差估计的样本使用。"
            local example2 "help xtpcse"
            local explain2 "PCSE 的适用性取决于 N、T、同期截面相关与序列相关结构，应按数据结构选择。"
        }
        else if "`cmd'" == "xtregar" {
            local expr_label "Y + X + fe/re + AR(1) 面板误差设定"
            local example1 "xtregar y x1 x2, fe"
            local explain1 "估计带 AR(1) 扰动结构的固定效应面板线性模型。"
            local example2 "xtregar y x1 x2, re"
            local explain2 "随机效应版本同时建模个体效应与面板内一阶自相关。"
        }
        else if "`cmd'" == "xtrc" {
            local expr_label "Y + X（随机系数面板回归）"
            local example1 "xtrc y x1 x2"
            local explain1 "允许回归系数在面板个体之间随机变化，适用于参数异质性本身属于研究对象的场景。"
            local example2 "help xtrc"
            local explain2 "运行前应确认每个 panel 内有足够时间维度用于识别个体层面的系数差异。"
        }
        else if "`cmd'" == "xtstreg" {
            local expr_label "生存协变量 + distribution()；运行前还需 stset，并由页面执行 xtset"
            local example1 "xtstreg age female, distribution(weibull)"
            local explain1 "在已 stset 的面板生存数据上估计 Weibull 随机效应生存模型；页面会按所选 panel/time 先执行 xtset。"
            local example2 "help xtstreg"
            local explain2 "xtstreg 同时属于 st 与 xt 工作流；失败事件、分析时间和 censoring 定义必须先由 stset 正确声明。"
        }
'''
s = s.replace(panel_marker, panel_blocks + panel_marker, 1)

old_mixed_members = " mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm "
new_mixed_members = " mixed mecloglog melogit meprobit mepoisson menbreg meologit meoprobit meintreg menl mestreg metobit meglm "
member_count = s.count(old_mixed_members)
if member_count != 2:
    raise SystemExit(f"mixed family membership: expected 2 matches, got {member_count}")
s = s.replace(old_mixed_members, new_mixed_members)

mixed_case = '''            if "`cmd'" == "mixed" {
                local example1 "mixed y x1 x2 || school: x2 || class:"
                local explain1 "固定效应写在前面，|| 后按层级写随机截距 / 随机斜率。"
            }
            else {
                local example1 "help `cmd'"
                local explain1 "多层模型的 || 随机效应结构属于核心模型主体，不能只用普通 Y/X 框代替。"
            }
'''
mixed_case_new = '''            if "`cmd'" == "mixed" {
                local example1 "mixed y x1 x2 || school: x2 || class:"
                local explain1 "固定效应写在前面，|| 后按层级写随机截距 / 随机斜率。"
            }
            else if "`cmd'" == "mecloglog" {
                local example1 "mecloglog y x1 x2 || school:"
                local explain1 "对二元结果使用 complementary log-log 链接，并在 school 层加入随机截距。"
            }
            else if "`cmd'" == "meintreg" {
                local example1 "meintreg ylower yupper x1 x2 x3 || id:"
                local explain1 "ylower/yupper 给出区间结果边界，并在 id 层加入随机截距；还可扩展随机系数。"
            }
            else if "`cmd'" == "menl" {
                local example1 "menl weight = ({b1}+{U[id]})/(1+exp(-(time-{b2})/{b3}))"
                local explain1 "直接写非线性均值函数，并把 U[id] 作为 id 层随机效应嵌入参数表达式。"
            }
            else {
                local example1 "help `cmd'"
                local explain1 "多层模型的 || 随机效应结构属于核心模型主体，不能只用普通 Y/X 框代替。"
            }
'''
s = once(s, mixed_case, mixed_case_new, "mixed specialized examples")

survival_marker = '''        else if "`cmd'" == "arima" {
'''
if s.count(survival_marker) != 1:
    raise SystemExit(f"survival insertion marker count={s.count(survival_marker)}")
survival_blocks = '''        else if "`cmd'" == "stintreg" {
            local expr_label "协变量 + interval(下界 上界) + distribution() 区间删失生存设定"
            local example1 "stintreg i.stage, interval(ltime rtime) distribution(weibull)"
            local explain1 "用 ltime/rtime 表示事件发生区间，并拟合 Weibull 参数生存模型。"
            local example2 "help stintreg"
            local explain2 "区间、左、右删失都由 interval() 边界表达；分布假设应结合研究对象与诊断确定。"
        }
        else if "`cmd'" == "stintcox" {
            local expr_label "协变量 + interval(下界 上界)；区间删失 Cox 比例风险模型"
            local example1 "stintcox age_mean i.male i.needle i.inject i.jail, interval(ltime rtime)"
            local explain1 "在事件仅能定位到时间区间时拟合半参数 Cox 比例风险模型；该入口仅在 Stata 17+ 展示。"
            local example2 "help stintcox"
            local explain2 "interval() 的左右端点定义属于数据结构核心，比例风险设定仍需结合研究设计检查。"
        }
'''
s = s.replace(survival_marker, survival_blocks + survival_marker, 1)

# Expand family-level copy so new commands get clear titles and panel labels.
s = once(
    s,
    '    else if strpos(" xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtabond xtdpdsys ", " `cmd\' ") {\n',
    '    else if strpos(" xtologit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtivreg xtpcse xtregar xtrc xtstreg xtabond xtdpdsys ", " `cmd\' ") {\n',
    "panel family copy",
)
s = once(
    s,
    '        local purpose1 "用于面板数据下的计数、受限因变量、GEE、前沿或动态面板模型。"\n',
    '        local purpose1 "用于面板数据下的有序/计数结果、IV、PCSE、序列相关、随机系数、生存、GEE、前沿或动态模型。"\n',
    "panel family purpose",
)
s = once(
    s,
    '    else if strpos(" stset sts stcox streg stcrreg ", " `cmd\' ") {\n',
    '    else if strpos(" stset sts stcox streg stintreg stintcox stcrreg ", " `cmd\' ") {\n',
    "survival family copy",
)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------- Java panel workflow ----------
jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")
old_java_panel = '''            "xtlogit", "xtprobit", "xtpoisson", "xtnbreg", "xtgee", "xttobit", "xtcloglog",
            "xtintreg", "xtoprobit", "xtmlogit", "xtfrontier", "xtabond", "xtdpdsys", "xthdidregress"
'''
new_java_panel = '''            "xtlogit", "xtprobit", "xtologit", "xtpoisson", "xtnbreg", "xtgee", "xttobit", "xtcloglog",
            "xtintreg", "xtoprobit", "xtmlogit", "xtfrontier", "xtivreg", "xtpcse", "xtregar", "xtrc", "xtstreg",
            "xtabond", "xtdpdsys", "xthdidregress"
'''
java_count = j.count(old_java_panel)
if java_count != 1:
    raise SystemExit(f"Java generic panel list: expected 1 match, got {java_count}")
j = j.replace(old_java_panel, new_java_panel, 1)
jp.write_text(j, encoding="utf-8", newline="\n")


# ---------- permanent static contracts ----------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'iv_core = {"ivregress", "ivprobit", "ivtobit", "ivpoisson"}\n'
checks = '''panel_extension_core = {"xtologit", "xtivreg", "xtpcse", "xtregar", "xtrc", "xtstreg"}
missing_panel_extensions = sorted(panel_extension_core - stats_cmds)
if missing_panel_extensions:
    fail("panel-data main commands missing: " + ", ".join(missing_panel_extensions))
mixed_extension_core = {"mecloglog", "meintreg", "menl"}
missing_mixed_extensions = sorted(mixed_extension_core - stats_cmds)
if missing_mixed_extensions:
    fail("mixed-effects main commands missing: " + ", ".join(missing_mixed_extensions))
for survival_cmd in ("stintreg", "stintcox"):
    if survival_cmd not in stats_cmds:
        fail(f"interval-censored survival command missing: {survival_cmd}")
if "foreach cmd in didregress xtdidregress telasso ziologit xtmlogit stintcox" not in registry:
    fail("Stata 17 version gate must include xtmlogit and stintcox")
for needle in (
    'xtivreg y x1 (x2 = z1 z2), fe',
    'xtpcse y x1 x2, correlation(ar1) pairwise',
    'xtregar y x1 x2, fe',
    'xtrc y x1 x2',
    'xtstreg age female, distribution(weibull)',
    'mecloglog y x1 x2 || school:',
    'meintreg ylower yupper x1 x2 x3 || id:',
    'menl weight = ({b1}+{U[id]})/(1+exp(-(time-{b2})/{b3}))',
    'stintreg i.stage, interval(ltime rtime) distribution(weibull)',
    'stintcox age_mean i.male i.needle i.inject i.jail, interval(ltime rtime)',
):
    if needle not in semantics:
        fail(f"panel/mixed/survival semantic contract missing: {needle}")
panel_method_start = java.find("private static boolean isGenericPanelEstimator")
panel_method_end = java.find("private static boolean isGenericPanelTimeRequired", panel_method_start)
if panel_method_start < 0 or panel_method_end < 0:
    fail("Java generic panel estimator method missing")
panel_method_block = java[panel_method_start:panel_method_end]
for panel_cmd in panel_extension_core:
    if f'"{panel_cmd}"' not in panel_method_block:
        fail(f"Java panel auto-xtset routing missing: {panel_cmd}")

'''
v = once(v, anchor, checks + anchor, "panel mixed survival static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_PANEL_MIXED_SURVIVAL_PATCH_OK")
