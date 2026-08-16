from pathlib import Path
import re


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


def function_scope(text: str, signature: str, next_signature: str) -> tuple[int, int, str]:
    start = text.find(signature)
    if start < 0:
        raise SystemExit(f"scope start missing: {signature}")
    end = text.find(next_signature, start)
    if end < 0:
        raise SystemExit(f"scope end missing: {next_signature}")
    return start, end, text[start:end]


def replace_method_return(scope: str, method: str, expression: str) -> str:
    pat = re.compile(rf'((?:if|else if) \("{re.escape(method)}"\.equals\(var0\)\) \{{\s*\n\s*)return [^;]+;')
    scope2, n = pat.subn(rf'\1return {expression};', scope, count=1)
    if n != 1:
        raise SystemExit(f"fallback return patch failed for {method}: {n}")
    return scope2


def replace_preview_case(scope: str, method: str, preview: str) -> str:
    pat = re.compile(rf'case "{re.escape(method)}": return "[^"]*";')
    scope2, n = pat.subn(f'case "{method}": return "{preview}";', scope, count=1)
    if n != 1:
        raise SystemExit(f"stats preview patch failed for {method}: {n}")
    return scope2

jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")

# Keep the emergency Java fallback conservative: only commands supported by the Stata-16 baseline.
cmd_start, cmd_end, cmd_scope = function_scope(
    j,
    "      private static List<String> previewCommandsForMethod(String var0)",
    "      private static List<String> previewMethodsForCategory(String var0)",
)
returns = {
    "汇总，表格和假设检验": 'Arrays.asList("summarize", "ameans", "centile", "ci", "mean", "proportion", "ratio", "total", "tabstat", "tabulate", "table", "ttest", "prtest", "sdtest", "oneway", "anova", "ranksum", "median", "signrank", "signtest")',
    "线性模型及相关": 'Arrays.asList("regress", "areg", "reghdfe", "cnsreg", "rreg", "hetregress", "qreg", "iqreg", "bsqreg", "sqreg", "vwls", "eivreg", "intreg", "tobit", "truncreg", "churdle", "boxcox", "fp", "nl", "nlsur", "gmm", "sureg", "reg3", "mvreg", "frontier", "correlate", "pwcorr")',
    "二元结果": 'Arrays.asList("logit", "logistic", "binreg", "probit", "biprobit", "hetprobit", "scobit", "cloglog")',
    "序数结果": 'Arrays.asList("ologit", "oprobit", "hetoprobit", "zioprobit")',
    "分类结果": 'Arrays.asList("mlogit", "mprobit", "clogit", "slogit", "cmset", "cmsummarize", "cmchoiceset", "cmtab", "cmsample", "cmclogit", "cmmixlogit", "cmxtmixlogit", "cmmprobit", "cmroprobit", "cmrologit", "nlogit", "asclogit", "asmprobit")',
    "计数结果": 'Arrays.asList("poisson", "nbreg", "gnbreg", "cpoisson", "ppmlhdfe", "zip", "zinb", "tpoisson", "tnbreg")',
    "分数结果": 'Arrays.asList("fracreg", "betareg")',
    "广义线性模型": 'Collections.singletonList("glm")',
    "选择模型": 'Arrays.asList("heckman", "heckprobit", "heckoprobit", "heckpoisson")',
    "时间序列": 'Arrays.asList("arima", "arfima", "newey", "prais", "arch", "ucm", "mswitch", "threshold", "dfgls", "dfuller", "pperron", "corrgram", "cumsp", "pergram", "wntestb", "wntestq", "psdensity", "rolling", "forecast", "tsappend", "tsfill", "tsfilter", "tsreport", "tssmooth")',
    "多元时间序列": 'Arrays.asList("var", "varsoc", "vargranger", "varlmar", "varnorm", "varstable", "irf", "svar", "vec", "vecrank", "veclmar", "vecnorm", "vecstable", "varbasic", "varwle", "mgarch", "dfactor", "sspace", "xcorr")',
    "空间自回归模型": 'Arrays.asList("spregress", "spivregress", "spxtregress")',
    "纵向/面板数据": 'Arrays.asList("xtreg", "xtlogit", "xtprobit", "xtologit", "xtpoisson", "xtnbreg", "xtgee", "xttobit", "xtcloglog", "xtintreg", "xtoprobit", "xtfrontier", "xtivreg", "xtpcse", "xtgls", "xtregar", "xtrc", "xtstreg", "xteregress", "xteprobit", "xteoprobit", "xteintreg", "xtheckman", "xthtaylor", "xtabond", "xtdpdsys", "xtdpd", "xtunitroot", "xtcointtest", "xtdescribe", "xtsum", "xttab", "xtdata")',
    "多层混合效应模型": 'Arrays.asList("mixed", "mecloglog", "melogit", "meprobit", "mepoisson", "menbreg", "meologit", "meoprobit", "meintreg", "menl", "mestreg", "metobit", "meglm")',
    "生存分析": 'Arrays.asList("stset", "stcox", "streg", "stintreg", "stcrreg", "sts", "stcurve", "stdescribe", "stsum", "stci", "stbase", "stfill", "stgen", "stsplit", "stvary", "sttocc", "sttoct", "stir", "strate", "stptime", "stmh", "stmc", "ctset", "cttost", "ltable", "snapspan")',
    "流行病学及相关": 'Arrays.asList("cc", "cs", "ir", "mcc", "dstdize", "pkexamine", "pksumm", "pkcross", "pkequiv", "pkcollapse", "pkshape")',
    "内生协变量": 'Arrays.asList("eregress", "eprobit", "eoprobit", "eintreg")',
    "样本选择模型": 'Arrays.asList("heckman", "heckprobit", "heckoprobit", "heckpoisson")',
    "因果推断/处理效应": 'Arrays.asList("teffects", "eteffects", "etregress", "etpoisson", "stteffects")',
    "结构方程模型(SEM)": 'Arrays.asList("sem", "gsem")',
    "潜在类别分析(LCA)": 'Collections.singletonList("gsem")',
    "有限混合模型(FMM)": 'Collections.singletonList("fmm")',
    "项目反应理论(IRT)": 'Arrays.asList("irt", "irtgraph", "diflogistic", "difmh")',
    "多元分析": 'Arrays.asList("alpha", "factor", "pca", "canon", "ca", "candisc", "hotelling", "manova", "mvreg", "mca", "mds", "mdslong", "mdsmat", "mvtest", "procrustes", "discrim", "cluster")',
    "调查数据分析": 'Arrays.asList("svyset", "svydescribe", "svy")',
    "Lasso回归": 'Arrays.asList("lasso", "elasticnet", "sqrtlasso", "poregress", "pologit", "popoisson", "dsregress", "dslogit", "dspoisson", "poivregress", "xporegress", "xpologit", "xpopoisson", "xpoivregress")',
    "Meta分析": 'Collections.singletonList("meta")',
    "多重插补": 'Collections.singletonList("mi")',
    "非参数分析": 'Arrays.asList("ranksum", "median", "signrank", "signtest", "npregress", "nptrend", "kdensity", "lowess", "lpoly")',
    "精确统计": 'Arrays.asList("exlogistic", "expoisson", "bitest", "bitesti", "ksmirnov", "symmetry", "tetrachoric", "tabi")',
    "重抽样": 'Arrays.asList("bootstrap", "jackknife", "permute", "simulate", "statsby")',
    "效能，精度和样品含量": 'Arrays.asList("power", "ciwidth")',
    "贝叶斯分析": 'Arrays.asList("bayes", "bayesmh", "bayespredict", "bayesreps", "bayesstats", "bayesgraph", "bayestest")',
    "贝叶斯模型平均": 'Arrays.asList("bmaregress", "bmacoefsample", "bmagraph", "bmastats", "bmapredict")',
    "工具变量与内生性": 'Arrays.asList("ivregress", "ivprobit", "ivtobit", "ivpoisson", "ivreghdfe")',
    "估计后分析": 'Arrays.asList("test", "testparm", "testnl", "lincom", "nlcom", "contrast", "pwcompare", "predict", "predictnl", "margins", "marginsplot", "lrtest", "hausman", "suest", "linktest", "estimates", "estat")',
}
for method, expr in returns.items():
    cmd_scope = replace_method_return(cmd_scope, method, expr)
# Insert DSGE between IRT and multivariate when absent.
if '"DSGE模型".equals(var0)' not in cmd_scope:
    marker = '         }          else if ("多元分析".equals(var0)) {'
    if cmd_scope.count(marker) != 1:
        raise SystemExit(f"DSGE fallback insertion marker count={cmd_scope.count(marker)}")
    block = '         }          else if ("DSGE模型".equals(var0)) {\n            return Arrays.asList("dsge", "dsgenl");\n'
    cmd_scope = cmd_scope.replace(marker, block + marker, 1)
j = j[:cmd_start] + cmd_scope + j[cmd_end:]

# Emergency method list: hide methods that are unavailable on the Stata-16 baseline and remove duplicate sample-selection navigation.
methods_start, methods_end, methods_scope = function_scope(
    j,
    "      private static List<String> previewMethodsForCategory(String var0)",
    "      private static List<String> splitControls(String var0)",
)
methods_scope = methods_scope.replace('"生存分析", "流行病学及相关", "内生协变量", "样本选择模型",', '"生存分析", "流行病学及相关", "内生协变量",')
methods_scope = methods_scope.replace('"有限混合模型(FMM)", "项目反应理论(IRT)", "多元分析",', '"有限混合模型(FMM)", "项目反应理论(IRT)", "DSGE模型", "多元分析",')
methods_scope = methods_scope.replace(', "贝叶斯分析", "贝叶斯模型平均", "工具变量与内生性"', ', "贝叶斯分析", "工具变量与内生性"')
j = j[:methods_start] + methods_scope + j[methods_end:]

# Statistics grouped overview follows the same public method set; selection-model compatibility remains callable but hidden.
j = once(
    j,
    '{"进阶与结构", "生存、流行病学、内生性与样本选择", new Color(235, 151, 39), new String[]{"生存分析", "流行病学及相关", "内生协变量", "样本选择模型"}}',
    '{"进阶与结构", "生存、流行病学与内生协变量", new Color(235, 151, 39), new String[]{"生存分析", "流行病学及相关", "内生协变量"}}',
    "hide duplicate sample-selection group",
)
j = once(
    j,
    '{"因果与结构模型", "处理效应、SEM、潜在类别与多元分析", new Color(222, 92, 112), new String[]{"因果推断/处理效应", "结构方程模型(SEM)", "潜在类别分析(LCA)", "有限混合模型(FMM)", "项目反应理论(IRT)", "多元分析", "调查数据分析"}}',
    '{"因果与结构模型", "处理效应、SEM、潜变量、DSGE 与多元分析", new Color(222, 92, 112), new String[]{"因果推断/处理效应", "结构方程模型(SEM)", "潜在类别分析(LCA)", "有限混合模型(FMM)", "项目反应理论(IRT)", "DSGE模型", "多元分析", "调查数据分析"}}',
    "add DSGE to statistics group",
)

# Human-readable method previews: show current core commands, not stale aliases.
prev_start, prev_end, prev_scope = function_scope(
    j,
    "      private static String statsMethodPreview(String method)",
    "      private static String genericMethodPreview(String category, String method)",
)
preview_map = {
    "时间序列": "arima · arfima · newey · arch · dfuller",
    "多元时间序列": "var · varsoc · vargranger · irf · svar · vec",
    "纵向/面板数据": "xtreg · xtlogit · xtpoisson · xtgee · xtivreg",
    "多层混合效应模型": "mixed · melogit · mepoisson · mestreg",
    "生存分析": "stset · stcox · streg · stintreg · stcrreg",
    "流行病学及相关": "cc · cs · ir · mcc · dstdize",
    "内生协变量": "eregress · eprobit · eoprobit · eintreg",
    "因果推断/处理效应": "teffects · eteffects · etregress · stteffects",
    "项目反应理论(IRT)": "irt · irtgraph · diflogistic · difmh",
    "多元分析": "alpha · factor · pca · canon · ca · manova",
    "调查数据分析": "svyset · svydescribe · svy",
    "Lasso回归": "lasso · elasticnet · sqrtlasso · dsregress · poregress",
    "非参数分析": "npregress · nptrend · kdensity · lowess · lpoly",
    "精确统计": "exlogistic · expoisson · bitest · ksmirnov · tabi",
    "效能，精度和样品含量": "power · ciwidth",
    "贝叶斯分析": "bayes · bayesmh · bayespredict · bayesstats",
    "贝叶斯模型平均": "bmaregress · bmastats · bmagraph · bmapredict",
    "工具变量与内生性": "ivregress · ivprobit · ivtobit · ivpoisson · ivreghdfe",
    "估计后分析": "test · lincom · predict · margins · estat · estimates",
}
for method, preview in preview_map.items():
    prev_scope = replace_preview_case(prev_scope, method, preview)
if 'case "DSGE模型":' not in prev_scope:
    marker = '            case "多元分析": return '
    pos = prev_scope.find(marker)
    if pos < 0:
        raise SystemExit("DSGE stats preview insertion marker missing")
    prev_scope = prev_scope[:pos] + '            case "DSGE模型": return "dsge · dsgenl";\n' + prev_scope[pos:]
j = j[:prev_start] + prev_scope + j[prev_end:]

# Method-key mapping needs DSGE so normal Registry navigation can round-trip the method name.
key_pat = re.compile(r'(case "项目反应理论\(IRT\)":\s*\n\s*return "irt";)')
if 'case "DSGE模型"' not in j:
    j, n = key_pat.subn(r'\1\n            case "DSGE模型":\n               return "dsge";', j, count=1)
    if n != 1:
        raise SystemExit(f"DSGE method-key insertion failed: {n}")

# Remove invalid/stale Java command knowledge from generic title helpers.
j = j.replace('"eregress", "eprobit", "eoprobit", "epoisson", "eintreg", "teffects", "etregress", "etpoisson"', '"eregress", "eprobit", "eoprobit", "eintreg", "teffects", "eteffects", "etregress", "etpoisson", "stteffects"')
j = j.replace('"factor", "pca", "canon", "cca", "manova", "discrim", "cluster"', '"alpha", "factor", "pca", "canon", "ca", "candisc", "hotelling", "manova", "mvreg", "mca", "mds", "mdslong", "mdsmat", "mvtest", "procrustes", "discrim", "cluster"')
j = j.replace('if ("svy".equals(command)) return "调查设计与估计";', 'if (Arrays.asList("svyset", "svydescribe", "svy").contains(command)) return "调查设计与估计";')
j = j.replace('"sem", "gsem", "fmm", "irt"', '"sem", "gsem", "fmm", "irt", "irtgraph", "diflogistic", "difmh", "dsge", "dsgenl"')
j = j.replace('"lasso", "elasticnet", "sqrtlasso", "dsregress", "poivregress", "xporegress", "xpoivregress"', '"lasso", "elasticnet", "sqrtlasso", "poregress", "pologit", "popoisson", "dsregress", "dslogit", "dspoisson", "poivregress", "xporegress", "xpologit", "xpopoisson", "xpoivregress"')

jp.write_text(j, encoding="utf-8", newline="\n")

# Static contracts: Java fallback is an emergency compatibility layer, but it must never reintroduce nonexistent or retired command names.
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'if "event_plot" not in graph_cmds:\n    fail("event_plot must remain public through the Graph catalog")\n'
checks = '''java_invalid_tokens = ("epoisson", "cca")
for invalid in java_invalid_tokens:
    if re.search(rf"(?<![A-Za-z0-9_]){re.escape(invalid)}(?![A-Za-z0-9_])", java):
        fail(f"stale/nonexistent Java command token remains: {invalid}")
if 'Collections.singletonList("bma")' in java:
    fail("Java BMA fallback still points to retired bma alias")
for java_stats_contract in (
    'return Arrays.asList("irt", "irtgraph", "diflogistic", "difmh");',
    'return Arrays.asList("svyset", "svydescribe", "svy");',
    'return Arrays.asList("exlogistic", "expoisson", "bitest", "bitesti", "ksmirnov", "symmetry", "tetrachoric", "tabi");',
    'return Arrays.asList("power", "ciwidth");',
    'return Arrays.asList("bmaregress", "bmacoefsample", "bmagraph", "bmastats", "bmapredict");',
    'return Arrays.asList("dsge", "dsgenl");',
    'case "DSGE模型": return "dsge · dsgenl";',
):
    if java_stats_contract not in java:
        fail(f"Java Statistics parity contract missing: {java_stats_contract}")
if '"内生协变量", "样本选择模型"' in java:
    fail("duplicate sample-selection method remains in Java public Statistics navigation")
'''
v = once(v, anchor, anchor + checks, "Java statistics parity static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_STATISTICS_JAVA_PARITY_PATCH_OK")
