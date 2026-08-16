from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------------- registry ----------------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.5  16aug2026", "*! hxregistry 3.1.6  16aug2026", "registry version")
r = once(
    r,
    "ivregress ivreghdfe teffects etregress etpoisson didregress xtdidregress sem",
    "ivregress ivreghdfe teffects eteffects etregress etpoisson stteffects didregress xtdidregress mediate hdidregress xthdidregress sem",
    "causal catalog commands",
)
r = once(
    r,
    '''    if c(stata_version) < 17 {
        local stats_cmds : subinstr local stats_cmds " telasso" "", all
    }
    if c(stata_version) < 18 {
        local stats_cmds : subinstr local stats_cmds " bmaregress" "", all
    }
''',
    '''    if c(stata_version) < 17 {
        foreach cmd in didregress xtdidregress telasso {
            local stats_cmds : subinstr local stats_cmds " `cmd'" "", all
        }
    }
    if c(stata_version) < 18 {
        foreach cmd in mediate hdidregress xthdidregress bmaregress {
            local stats_cmds : subinstr local stats_cmds " `cmd'" "", all
        }
    }
''',
    "stats version gates",
)
r = once(
    r,
    '    local reg_cmds "regress areg reghdfe rreg cnsreg vwls eivreg qreg newey prais xtreg xtlogit xtprobit logit probit poisson nbreg ppmlhdfe ivregress ivreghdfe didregress xtdidregress"\n',
    '    local reg_cmds "regress areg reghdfe rreg cnsreg vwls eivreg qreg newey prais xtreg xtlogit xtprobit logit probit poisson nbreg ppmlhdfe ivregress ivreghdfe didregress xtdidregress"\n    if c(stata_version) < 17 {\n        local reg_cmds : subinstr local reg_cmds " didregress" "", all\n        local reg_cmds : subinstr local reg_cmds " xtdidregress" "", all\n    }\n',
    "legacy reg gate",
)
old_causal = '''    else if inlist(`"`method'"', "因果推断/处理效应", "causal_treatment") {
        local view "teffects etregress etpoisson didregress xtdidregress"
        if c(stata_version) >= 17 local view "`view' telasso"
    }
'''
new_causal = '''    else if inlist(`"`method'"', "因果推断/处理效应", "causal_treatment") {
        local view "teffects eteffects etregress etpoisson stteffects"
        if c(stata_version) >= 17 local view "`view' didregress xtdidregress telasso"
        if c(stata_version) >= 18 local view "`view' mediate hdidregress xthdidregress"
    }
'''
r = once(r, old_causal, new_causal, "causal method routing")
r = once(
    r,
    '    else if inlist(`"`method\'"\', "双重差分", "did") local view "didregress xtdidregress"\n',
    '    else if inlist(`"`method\'"\', "双重差分", "did") {\n        if c(stata_version) >= 17 local view "didregress xtdidregress"\n        else local view ""\n    }\n',
    "compatibility DID gate",
)
search_anchor = '        local key_xtdidregress "xtdidregress did panel longitudinal 双重差分 面板 平行趋势 因果推断 处理效应"\n'
search_add = '''        local key_hdIDregress "hdidregress heterogeneous did repeated cross section 异质 双重差分 队列 时间"
        local key_xthdidregress "xthdidregress heterogeneous did panel 异质 双重差分 面板 队列 时间"
        local key_eteffects "eteffects endogenous treatment effects 内生处理 处理效应 因果推断"
        local key_stteffects "stteffects survival treatment effects 生存 处理效应 因果推断"
        local key_mediate "mediate causal mediation 中介效应 直接效应 间接效应 因果中介"
'''
# use correctly cased macro key for lower-case command
search_add = search_add.replace("key_hdIDregress", "key_hdidregress")
r = once(r, search_anchor, search_anchor + search_add, "causal search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------------- semantics ----------------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.4  16aug2026", "*! hxsemantics 1.4.5  16aug2026", "semantics version")
s = once(
    s,
    " power teffects sts irf graph discrim cluster table ",
    " power teffects eteffects stteffects mediate hdidregress xthdidregress sts irf graph discrim cluster table ",
    "causal command-body catalog",
)
teffects_block = '''        else if "`cmd'" == "teffects" {
            local expr_label "估计器 + 结果方程 + 处理方程（如 psmatch (y) (treat x1 x2)）"
            local example1 "teffects psmatch (y) (treat x1 x2)"
            local explain1 "使用倾向得分匹配估计处理效应。"
            local example2 "teffects ipwra (y x1 x3) (treat x1 x2)"
            local explain2 "使用双重稳健 IPWRA。"
        }
'''
causal_more = teffects_block + '''        else if "`cmd'" == "eteffects" {
            local expr_label "(结果方程) + (内生处理方程)"
            local example1 "eteffects (wage tenure c.age##c.age) (college c.age##c.age i.pcollege)"
            local explain1 "用控制函数处理 college 的内生处理分配，并直接报告潜在结果框架下的处理效应。"
            local example2 "help eteffects"
            local explain2 "结果分布、处理模型和 ATE/ATET 目标按研究设计继续核对。"
        }
        else if "`cmd'" == "stteffects" {
            local expr_label "估计器 + 生存结果方程 / 处理方程 / 删失方程（按估计器填写）"
            local example1 "stteffects ra (age exercise diet education) (smoke)"
            local explain1 "在已经 stset 的数据上，用生存回归调整估计 smoke 对生存时间的处理效应。"
            local example2 "stteffects ipwra (age exercise diet education) (smoke age exercise education) (age exercise diet education)"
            local explain2 "IPWRA 同时建模生存结果、处理分配和删失机制。"
        }
        else if "`cmd'" == "mediate" {
            local expr_label "(结果模型) + (中介模型) + (处理变量[, 协变量])"
            local example1 "mediate (wellbeing, logit) (bonotonin, logit) (exercise)"
            local explain1 "把 exercise 的总效应分解为经 bonotonin 的间接效应和直接效应。"
            local example2 "help mediate"
            local explain2 "结果、中介和处理变量类型决定可用的模型组合。"
        }
        else if "`cmd'" == "hdidregress" {
            local expr_label "估计器 + (结果方程) + (处理方程) + group() + time()"
            local example1 "hdidregress aipw (bmi medu i.girl i.sports) (hhabit parksd), group(schools) time(year)"
            local explain1 "重复截面异质 DID：AIPW 允许 ATET 随处理 cohort 和时间变化。"
            local example2 "help hdidregress"
            local explain2 "可在 RA、IPW、AIPW、TWFE 中选择；group() 和 time() 属于核心识别结构。"
        }
        else if "`cmd'" == "xthdidregress" {
            local expr_label "估计器 + (结果方程) + (处理方程) + group()；面板与时间由上方 xtset 设定"
            local example1 "xthdidregress ra (registered best) (movie), group(breed)"
            local explain1 "面板异质 DID：页面运行前先按所选 panel/time 执行 xtset，再估计 cohort×time ATET。"
            local example2 "help xthdidregress"
            local explain2 "时间变量必须能够识别处理 cohort；估计器和协变量结构按研究设计核对。"
        }
'''
s = once(s, teffects_block, causal_more, "causal command-body semantics")
s = once(
    s,
    '    else if strpos(" teffects etregress etpoisson telasso ", " `cmd\' ") {\n',
    '    else if strpos(" teffects eteffects etregress etpoisson stteffects telasso mediate hdidregress xthdidregress ", " `cmd\' ") {\n',
    "causal family copy",
)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------------- Java low-barrier xthdidregress panel setup ----------------
jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")
j = once(
    j,
    '''            "xtintreg", "xtoprobit", "xtmlogit", "xtfrontier", "xtabond", "xtdpdsys"
         ).contains(command);
      }

      private static boolean isGenericPanelTimeRequired(String command) {
         return Arrays.asList("xtabond", "xtdpdsys").contains(command);
      }
''',
    '''            "xtintreg", "xtoprobit", "xtmlogit", "xtfrontier", "xtabond", "xtdpdsys", "xthdidregress"
         ).contains(command);
      }

      private static boolean isGenericPanelTimeRequired(String command) {
         return Arrays.asList("xtabond", "xtdpdsys", "xthdidregress").contains(command);
      }
''',
    "Java panel command/time lists",
)
j = once(
    j,
    'JOptionPane.showMessageDialog(this, "xtabond / xtdpdsys 需要时间变量来构造动态滞后结构。", "时间变量尚未选择", 1);',
    'JOptionPane.showMessageDialog(this, "当前命令需要时间变量；xtabond / xtdpdsys 用于动态滞后，xthdidregress 用于识别处理 cohort 和时间。", "时间变量尚未选择", 1);',
    "Java time validation copy",
)
jp.write_text(j, encoding="utf-8", newline="\n")


# ---------------- static contracts ----------------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''if "telasso" not in stats_cmds:
    fail("official telasso treatment-effects command missing from Statistics catalog")
'''
extra = '''causal_core = {"teffects", "eteffects", "etregress", "etpoisson", "stteffects"}
missing_causal = sorted(causal_core - stats_cmds)
if missing_causal:
    fail("official treatment-effects commands missing: " + ", ".join(missing_causal))
for stata18_cmd in ("mediate", "hdidregress", "xthdidregress"):
    if stata18_cmd not in stats_cmds:
        fail(f"Stata 18 causal command missing: {stata18_cmd}")
for needle in (
    'eteffects (wage tenure c.age##c.age) (college c.age##c.age i.pcollege)',
    'stteffects ra (age exercise diet education) (smoke)',
    'mediate (wellbeing, logit) (bonotonin, logit) (exercise)',
    'hdidregress aipw (bmi medu i.girl i.sports) (hhabit parksd), group(schools) time(year)',
    'xthdidregress ra (registered best) (movie), group(breed)',
):
    if needle not in semantics:
        fail(f"causal semantic contract missing: {needle}")
for needle in (
    '"xthdidregress"',
    'Arrays.asList("xtabond", "xtdpdsys", "xthdidregress")',
):
    if needle not in java:
        fail(f"xthdidregress low-barrier panel contract missing: {needle}")
'''
v = once(v, anchor, anchor + extra, "causal static completeness")
v = v.replace(
    '"legacy_did_hidden=1 event_plot_graph=1 official_did_stats=1 epoisson_removed=1 longtail_semantics=1 lasso_catalog=1 lca_example=1 docs_source_split=1"',
    '"legacy_did_hidden=1 event_plot_graph=1 official_did_stats=1 epoisson_removed=1 longtail_semantics=1 lasso_catalog=1 lca_example=1 causal_catalog=1 xthdid_panel=1 docs_source_split=1"',
)
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_CAUSAL_CATALOG_PATCH_OK")
