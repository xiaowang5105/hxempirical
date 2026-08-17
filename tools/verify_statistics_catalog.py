#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (ROOT / "hxregistry.ado").read_text(encoding="utf-8")
SEMANTICS = (ROOT / "hxsemantics.ado").read_text(encoding="utf-8")
JAVA = (ROOT / "src/main/java/com/hexie/stata/HxWorkbench.java").read_text(encoding="utf-8")
STATIC = (ROOT / "tools/verify_static_contracts.py").read_text(encoding="utf-8")


def fail(message: str) -> None:
    raise SystemExit("HX_STATISTICS_CATALOG_FAIL: " + message)


# This is the exact Stata Statistics hierarchy audited after the GLM section.
# Commands intentionally shared by more than one Statistics method remain in each method.
EXPECTED: dict[str, set[str]] = {
    "选择模型": {"heckman", "heckprobit", "heckoprobit", "heckpoisson"},
    "时间序列": {
        "arima", "arfima", "arimasoc", "arfimasoc", "newey", "prais", "arch", "ucm", "mswitch", "threshold",
        "dfgls", "dfuller", "pperron", "corrgram", "cumsp", "pergram", "wntestb", "wntestq", "psdensity", "rolling",
        "forecast", "tsappend", "tsfill", "tsfilter", "tsreport", "tssmooth",
    },
    "多元时间序列": {
        "var", "varsoc", "vargranger", "varlmar", "varnorm", "varstable", "irf", "lpirf", "svar", "vec", "vecrank",
        "veclmar", "vecnorm", "vecstable", "varbasic", "varwle", "mgarch", "dfactor", "sspace", "xcorr",
    },
    "空间自回归模型": {"spregress", "spivregress", "spxtregress"},
    "纵向/面板数据": {
        "xtreg", "xtlogit", "xtprobit", "xtologit", "xtpoisson", "xtnbreg", "xtgee", "xttobit", "xtcloglog", "xtintreg",
        "xtoprobit", "xtmlogit", "xtfrontier", "xtivreg", "xtpcse", "xtgls", "xtregar", "xtrc", "xtstreg", "xteregress",
        "xteprobit", "xteoprobit", "xteintreg", "xtheckman", "xthtaylor", "xtabond", "xtdpdsys", "xtdpd", "xtunitroot",
        "xtcointtest", "xtdescribe", "xtsum", "xttab", "xtdata",
    },
    "多层混合效应模型": {
        "mixed", "mecloglog", "melogit", "meprobit", "mepoisson", "menbreg", "meologit", "meoprobit", "meintreg", "menl",
        "mestreg", "metobit", "meglm",
    },
    "生存分析": {
        "stset", "stcox", "streg", "stintreg", "stintcox", "stcrreg", "sts", "stcurve", "stdescribe", "stsum", "stci",
        "stbase", "stfill", "stgen", "stsplit", "stvary", "sttocc", "sttoct", "stir", "strate", "stptime", "stmh", "stmc",
        "ctset", "cttost", "ltable", "snapspan",
    },
    "流行病学及相关": {"cc", "cs", "ir", "mcc", "dstdize", "pkexamine", "pksumm", "pkcross", "pkequiv", "pkcollapse", "pkshape"},
    "内生协变量": {"eregress", "eprobit", "eoprobit", "eintreg"},
    "因果推断/处理效应": {
        "didregress", "xtdidregress", "hdidregress", "xthdidregress", "mediate", "teffects", "eteffects", "etregress",
        "etpoisson", "stteffects", "telasso",
    },
    "结构方程模型(SEM)": {"sem", "gsem"},
    "潜在类别分析(LCA)": {"gsem"},
    "有限混合模型(FMM)": {"fmm"},
    "项目反应理论(IRT)": {"irt", "irtgraph", "diflogistic", "difmh"},
    "DSGE模型": {"dsge", "dsgenl"},
    "多元分析": {
        "alpha", "factor", "pca", "canon", "ca", "candisc", "hotelling", "manova", "mvreg", "mca", "mds", "mdslong",
        "mdsmat", "mvtest", "procrustes", "discrim", "cluster",
    },
    "调查数据分析": {"svyset", "svydescribe", "svy"},
    "Lasso回归": {
        "lasso", "elasticnet", "sqrtlasso", "poregress", "pologit", "popoisson", "dsregress", "dslogit", "dspoisson",
        "poivregress", "xporegress", "xpologit", "xpopoisson", "xpoivregress",
    },
    "Meta分析": {"meta"},
    "多重插补": {"mi"},
    "非参数分析": {"ranksum", "median", "signrank", "signtest", "npregress", "nptrend", "kdensity", "lowess", "lpoly"},
    "精确统计": {"exlogistic", "expoisson", "bitest", "bitesti", "ksmirnov", "symmetry", "tetrachoric", "tabi"},
    "重抽样": {"bootstrap", "jackknife", "permute", "simulate", "statsby"},
    "效能，精度和样品含量": {"power", "ciwidth", "gsbounds", "gsdesign"},
    "贝叶斯分析": {
        "bayes", "bayesmh", "bayespredict", "bayesreps", "bayesstats", "bayesgraph", "bayestest", "bayesvarstable", "bayesirf", "bayesfcast",
    },
    "贝叶斯模型平均": {"bmaregress", "bmacoefsample", "bmagraph", "bmastats", "bmapredict"},
    "工具变量与内生性": {"ivregress", "ivprobit", "ivtobit", "ivpoisson", "ivreghdfe", "ivfprobit", "ivqregress"},
    "估计后分析": {
        "test", "testparm", "testnl", "lincom", "nlcom", "contrast", "pwcompare", "predict", "predictnl", "margins", "marginsplot",
        "lrtest", "hausman", "suest", "linktest", "estimates", "estat",
    },
}

EXPECTED_METHOD_ORDER = list(EXPECTED)


def method_block(method: str) -> str:
    marker = f'"{method}"'
    start = REGISTRY.find(marker, REGISTRY.find("/* Stata Statistics menu. */"))
    if start < 0:
        fail(f"Statistics method missing from registry: {method}")
    line_start = REGISTRY.rfind("\n", 0, start) + 1
    next_start = REGISTRY.find("\n    else if inlist", start + len(marker))
    graphics = REGISTRY.find("\n    /* Stata Graphics menu.", start + len(marker))
    candidates = [x for x in (next_start, graphics) if x >= 0]
    end = min(candidates) if candidates else len(REGISTRY)
    return REGISTRY[line_start:end]


def routed_commands(block: str) -> set[str]:
    commands: set[str] = set()
    for line in block.splitlines():
        if "local view" not in line:
            continue
        for quoted in re.findall(r'"([^"]*)"', line):
            for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", quoted):
                if token != "view":
                    commands.add(token.lower())
    return commands


# The visible method order after GLM must remain exact, so a newly added Statistics
# family cannot silently escape the page-quality audit.
stats_methods_match = re.search(r'local stats_methods "([^"]+)"', REGISTRY)
if not stats_methods_match:
    fail("stats_methods declaration missing")
all_methods = stats_methods_match.group(1).split()
try:
    glm_index = all_methods.index("广义线性模型")
except ValueError:
    fail("广义线性模型 missing from stats_methods")
remaining_methods = all_methods[glm_index + 1:]
if remaining_methods != EXPECTED_METHOD_ORDER:
    fail(f"post-GLM method order drift: {remaining_methods}")

# Exact union for every remaining Statistics method.
for method, expected in EXPECTED.items():
    actual = routed_commands(method_block(method))
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        fail(f"{method} routing drift; missing={missing}, extra={extra}")

# All routed commands must be executable catalog entries. marginsplot is intentionally
# shared from Graphics into postestimation.
def local_words(name: str) -> set[str]:
    m = re.search(rf'local {re.escape(name)} "([^"]*)"', REGISTRY)
    if not m:
        fail(f"registry local missing: {name}")
    return set(m.group(1).split())

stats_cmds = local_words("stats_cmds")
graph_cmds = local_words("graph_cmds")
routed_union = set().union(*EXPECTED.values())
missing_catalog = sorted(routed_union - stats_cmds - graph_cmds)
if missing_catalog:
    fail("routed commands absent from executable catalog: " + ", ".join(missing_catalog))

# Version boundaries for the supported Stata 16-18 catalog. These strings are
# deliberate release guards and must not disappear during UI refactors.
VERSION_GUARDS = (
    "didregress xtdidregress telasso ziologit xtmlogit stintcox bayesvarstable bayesirf bayesfcast",
    "mediate hdidregress xthdidregress bmaregress bmacoefsample bmagraph bmastats bmapredict dtable gsbounds gsdesign ivfprobit ivqregress arimasoc arfimasoc lpirf",
    'if c(stata_version) >= 17 local view "`view\' xtmlogit"',
    'if c(stata_version) >= 17 local view "`view\' stintcox"',
    'if c(stata_version) >= 18 local view "`view\' arimasoc arfimasoc"',
    'if c(stata_version) >= 18 local view "`view\' lpirf"',
    'if c(stata_version) >= 18 local view "`view\' ivfprobit ivqregress"',
)
for guard in VERSION_GUARDS:
    if guard not in REGISTRY:
        fail(f"version guard missing: {guard}")

# Every remaining command must have explicit evidence in the current UI/semantic
# implementation or in the deep static-contract suite. This prevents a registry-only
# command from being mistaken for a reviewed page.
for cmd in sorted(routed_union):
    needle = f'"{cmd}"'
    if needle not in JAVA and needle not in SEMANTICS and needle not in STATIC:
        fail(f"no Java/semantic/static-contract evidence for command: {cmd}")

# Method-level deep-contract anchors: one per remaining Statistics family. These are
# intentionally broader than exact command strings and prove that each family has a
# dedicated safety/semantic audit rather than only catalog membership.
METHOD_EVIDENCE: dict[str, tuple[str, ...]] = {
    "选择模型": ("selection", "heckman"),
    "时间序列": ("time-series", "arima"),
    "多元时间序列": ("multivariate time-series", "vecrank"),
    "空间自回归模型": ("spregress", "spivregress", "spxtregress"),
    "纵向/面板数据": ("panel-data", "xtunitroot"),
    "多层混合效应模型": ("mixed-effects", "mecloglog"),
    "生存分析": ("survival workflow", "stintcox"),
    "流行病学及相关": ("epidemiology", "pkexamine"),
    "内生协变量": ("extended-regression", "eregress"),
    "因果推断/处理效应": ("treatment-effect", "didregress"),
    "结构方程模型(SEM)": ("SEM/LCA/FMM", "sem"),
    "潜在类别分析(LCA)": ("SEM/LCA/FMM", "gsem"),
    "有限混合模型(FMM)": ("SEM/LCA/FMM", "fmm"),
    "项目反应理论(IRT)": ("IRT", "irtgraph"),
    "DSGE模型": ("DSGE", "dsgenl"),
    "多元分析": ("multivariate", "procrustes"),
    "调查数据分析": ("survey", "svyset"),
    "Lasso回归": ("Lasso", "sqrtlasso"),
    "Meta分析": ("meta",),
    "多重插补": ("multiple-imputation", "mi"),
    "非参数分析": ("nonparametric", "npregress"),
    "精确统计": ("exact", "exlogistic"),
    "重抽样": ("resampling", "bootstrap"),
    "效能，精度和样品含量": ("power", "ciwidth"),
    "贝叶斯分析": ("Bayesian", "bayesmh"),
    "贝叶斯模型平均": ("BMA", "bmaregress"),
    "工具变量与内生性": ("instrumental-variable", "ivprobit"),
    "估计后分析": ("postestimation", "testparm"),
}
static_lower = STATIC.lower()
for method, anchors in METHOD_EVIDENCE.items():
    for anchor in anchors:
        if anchor.lower() not in static_lower:
            fail(f"{method} deep static-contract anchor missing: {anchor}")

print(
    "HX_STATISTICS_CATALOG_OK",
    f"methods={len(EXPECTED)}",
    f"unique_commands={len(routed_union)}",
)
