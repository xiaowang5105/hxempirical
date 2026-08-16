from pathlib import Path

jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")

func_start = j.find("      private static String commandMethod(String var0)")
func_end = j.find("      private static String commandPath(String var0)", func_start)
if func_start < 0 or func_end < 0:
    raise SystemExit("commandMethod scope not found")
sc = j[func_start:func_end]

start_marker = '         } else if (Arrays.asList("summarize", "tabstat").contains(var0)) {'
end_marker = '         } else if ("did_builder".equals(var0)) {'
a = sc.find(start_marker)
b = sc.find(end_marker, a)
if a < 0 or b < 0:
    raise SystemExit(f"Statistics commandMethod replacement range not found: start={a} end={b}")

stats = '''         } else if (Arrays.asList("summarize", "ameans", "centile", "ci", "mean", "proportion", "ratio", "total", "tabstat", "tabulate", "table", "dtable", "ttest", "prtest", "sdtest", "oneway", "anova", "ranksum", "median", "signrank", "signtest").contains(var0)) {
            return "统计|汇总，表格和假设检验";
         } else if (Arrays.asList("regress", "areg", "reghdfe", "cnsreg", "rreg", "hetregress", "qreg", "iqreg", "bsqreg", "sqreg", "vwls", "eivreg", "intreg", "tobit", "truncreg", "churdle", "boxcox", "fp", "nl", "nlsur", "gmm", "sureg", "reg3", "mvreg", "frontier", "correlate", "pwcorr").contains(var0)) {
            return "统计|线性模型及相关";
         } else if (Arrays.asList("logit", "logistic", "binreg", "probit", "biprobit", "hetprobit", "scobit", "cloglog").contains(var0)) {
            return "统计|二元结果";
         } else if (Arrays.asList("ologit", "oprobit", "hetoprobit", "zioprobit", "ziologit").contains(var0)) {
            return "统计|序数结果";
         } else if (Arrays.asList("mlogit", "mprobit", "clogit", "slogit", "cmset", "cmsummarize", "cmchoiceset", "cmtab", "cmsample", "cmclogit", "cmmixlogit", "cmxtmixlogit", "cmmprobit", "cmroprobit", "cmrologit", "nlogit", "asclogit", "asmprobit").contains(var0)) {
            return "统计|分类结果";
         } else if (Arrays.asList("poisson", "nbreg", "gnbreg", "cpoisson", "ppmlhdfe", "zip", "zinb", "tpoisson", "tnbreg").contains(var0)) {
            return "统计|计数结果";
         } else if (Arrays.asList("fracreg", "betareg").contains(var0)) {
            return "统计|分数结果";
         } else if ("glm".equals(var0)) {
            return "统计|广义线性模型";
         } else if (Arrays.asList("heckman", "heckprobit", "heckoprobit", "heckpoisson").contains(var0)) {
            return "统计|选择模型";
         } else if (Arrays.asList("arima", "arfima", "arimasoc", "arfimasoc", "newey", "prais", "arch", "ucm", "mswitch", "threshold", "dfgls", "dfuller", "pperron", "corrgram", "cumsp", "pergram", "wntestb", "wntestq", "psdensity", "rolling", "forecast", "tsappend", "tsfill", "tsfilter", "tsreport", "tssmooth").contains(var0)) {
            return "统计|时间序列";
         } else if (Arrays.asList("var", "svar", "vec", "varbasic", "varsoc", "vargranger", "varlmar", "varnorm", "varstable", "varwle", "vecrank", "veclmar", "vecnorm", "vecstable", "irf", "lpirf", "mgarch", "dfactor", "sspace", "xcorr").contains(var0)) {
            return "统计|多元时间序列";
         } else if (Arrays.asList("spregress", "spivregress", "spxtregress").contains(var0)) {
            return "统计|空间自回归模型";
         } else if (Arrays.asList("xtreg", "xtlogit", "xtprobit", "xtologit", "xtpoisson", "xtnbreg", "xtgee", "xttobit", "xtcloglog", "xtintreg", "xtoprobit", "xtmlogit", "xtfrontier", "xtivreg", "xtpcse", "xtgls", "xtregar", "xtrc", "xtstreg", "xteregress", "xteprobit", "xteoprobit", "xteintreg", "xtheckman", "xthtaylor", "xtabond", "xtdpdsys", "xtdpd", "xtunitroot", "xtcointtest", "xtdescribe", "xtsum", "xttab", "xtdata").contains(var0)) {
            return "统计|纵向/面板数据";
         } else if (Arrays.asList("mixed", "mecloglog", "melogit", "meprobit", "mepoisson", "menbreg", "meologit", "meoprobit", "meintreg", "menl", "mestreg", "metobit", "meglm").contains(var0)) {
            return "统计|多层混合效应模型";
         } else if (Arrays.asList("ctset", "cttost", "ltable", "snapspan", "stset", "stdescribe", "stsum", "stci", "stcurve", "stbase", "stfill", "stgen", "stsplit", "stvary", "sttocc", "sttoct", "sts", "stcox", "streg", "stintreg", "stintcox", "stcrreg", "stir", "strate", "stptime", "stmh", "stmc").contains(var0)) {
            return "统计|生存分析";
         } else if (Arrays.asList("cc", "cs", "ir", "mcc", "dstdize", "pkexamine", "pksumm", "pkcross", "pkequiv", "pkcollapse", "pkshape").contains(var0)) {
            return "统计|流行病学及相关";
         } else if (Arrays.asList("eregress", "eprobit", "eoprobit", "eintreg").contains(var0)) {
            return "统计|内生协变量";
         } else if (Arrays.asList("teffects", "eteffects", "etregress", "etpoisson", "stteffects", "didregress", "xtdidregress", "mediate", "hdidregress", "xthdidregress", "telasso").contains(var0)) {
            return "统计|因果推断/处理效应";
         } else if (Arrays.asList("sem", "gsem").contains(var0)) {
            return "统计|结构方程模型(SEM)";
         } else if ("fmm".equals(var0)) {
            return "统计|有限混合模型(FMM)";
         } else if (Arrays.asList("irt", "irtgraph", "diflogistic", "difmh").contains(var0)) {
            return "统计|项目反应理论(IRT)";
         } else if (Arrays.asList("dsge", "dsgenl").contains(var0)) {
            return "统计|DSGE模型";
         } else if (Arrays.asList("alpha", "factor", "pca", "canon", "ca", "candisc", "hotelling", "manova", "mvreg", "mca", "mds", "mdslong", "mdsmat", "mvtest", "procrustes", "discrim", "cluster").contains(var0)) {
            return "统计|多元分析";
         } else if (Arrays.asList("svyset", "svydescribe", "svy").contains(var0)) {
            return "统计|调查数据分析";
         } else if (Arrays.asList("lasso", "elasticnet", "sqrtlasso", "poregress", "pologit", "popoisson", "dsregress", "dslogit", "dspoisson", "poivregress", "xporegress", "xpologit", "xpopoisson", "xpoivregress").contains(var0)) {
            return "统计|Lasso回归";
         } else if ("meta".equals(var0)) {
            return "统计|Meta分析";
         } else if ("mi".equals(var0)) {
            return "统计|多重插补";
         } else if (Arrays.asList("npregress", "nptrend").contains(var0)) {
            return "统计|非参数分析";
         } else if (Arrays.asList("exlogistic", "expoisson", "bitest", "bitesti", "ksmirnov", "symmetry", "tetrachoric", "tabi").contains(var0)) {
            return "统计|精确统计";
         } else if (Arrays.asList("bootstrap", "jackknife", "permute", "simulate", "statsby").contains(var0)) {
            return "统计|重抽样";
         } else if (Arrays.asList("power", "ciwidth", "gsbounds", "gsdesign").contains(var0)) {
            return "统计|效能，精度和样品含量";
         } else if (Arrays.asList("bayes", "bayesmh", "bayespredict", "bayesreps", "bayesstats", "bayesgraph", "bayestest", "bayesvarstable", "bayesirf", "bayesfcast").contains(var0)) {
            return "统计|贝叶斯分析";
         } else if (Arrays.asList("bmaregress", "bmacoefsample", "bmagraph", "bmastats", "bmapredict").contains(var0)) {
            return "统计|贝叶斯模型平均";
         } else if (Arrays.asList("ivregress", "ivprobit", "ivtobit", "ivpoisson", "ivfprobit", "ivqregress", "ivreghdfe").contains(var0)) {
            return "统计|工具变量与内生性";
         } else if (Arrays.asList("test", "testparm", "testnl", "lincom", "nlcom", "contrast", "pwcompare", "predict", "predictnl", "margins", "lrtest", "hausman", "suest", "linktest", "estimates", "estat").contains(var0)) {
            return "统计|估计后分析";
'''

sc = sc[:a] + stats + sc[b:]
j = j[:func_start] + sc + j[func_end:]
jp.write_text(j, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''for data_method_contract in (
    'Arrays.asList("use", "import", "export", "save").contains(var0)',
'''
pos = v.find(anchor)
if pos < 0:
    raise SystemExit("Data commandMethod contract anchor missing")
# Insert after the Data commandMethod contract block, before the next unrelated check.
end = v.find("\n\n", pos)
if end < 0:
    raise SystemExit("Data commandMethod contract block end missing")
checks = '''

statistics_command_method_contracts = {
    "summarize": "统计|汇总，表格和假设检验",
    "regress": "统计|线性模型及相关",
    "logit": "统计|二元结果",
    "ologit": "统计|序数结果",
    "mlogit": "统计|分类结果",
    "poisson": "统计|计数结果",
    "fracreg": "统计|分数结果",
    "glm": "统计|广义线性模型",
    "heckman": "统计|选择模型",
    "arima": "统计|时间序列",
    "var": "统计|多元时间序列",
    "spregress": "统计|空间自回归模型",
    "xtreg": "统计|纵向/面板数据",
    "mixed": "统计|多层混合效应模型",
    "stcox": "统计|生存分析",
    "cc": "统计|流行病学及相关",
    "eregress": "统计|内生协变量",
    "teffects": "统计|因果推断/处理效应",
    "sem": "统计|结构方程模型(SEM)",
    "irt": "统计|项目反应理论(IRT)",
    "dsge": "统计|DSGE模型",
    "pca": "统计|多元分析",
    "svy": "统计|调查数据分析",
    "lasso": "统计|Lasso回归",
    "meta": "统计|Meta分析",
    "mi": "统计|多重插补",
    "npregress": "统计|非参数分析",
    "exlogistic": "统计|精确统计",
    "bootstrap": "统计|重抽样",
    "power": "统计|效能，精度和样品含量",
    "bayes": "统计|贝叶斯分析",
    "bmaregress": "统计|贝叶斯模型平均",
    "ivregress": "统计|工具变量与内生性",
    "margins": "统计|估计后分析",
}
command_method_scope = java[java.find('private static String commandMethod(String var0)'):java.find('private static String commandPath(String var0)')]
for command, method_label in statistics_command_method_contracts.items():
    if command not in command_method_scope or f'return "{method_label}";' not in command_method_scope:
        fail(f"Statistics commandMethod canonical classification missing: {command} -> {method_label}")
if 'return "回归模型|工具变量";' in command_method_scope:
    fail("native IV commands still use the legacy regression commandPath classification")
if 'return "后估计|系数检验";' in command_method_scope or 'return "后估计|预测边际";' in command_method_scope:
    fail("native postestimation commands still use legacy post commandPath labels")
'''
v = v[:end] + checks + v[end:]
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_STATISTICS_COMMAND_METHOD_PATCH_OK")
