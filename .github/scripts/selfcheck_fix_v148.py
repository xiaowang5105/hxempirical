from pathlib import Path
import re


def once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 anchor, got {count}")
    return text.replace(old, new, 1)


# Registry fixes.
p = Path("hxregistry.ado")
s = p.read_text(encoding="utf-8")
s = once(s, "*! hxregistry 3.1.0  14aug2026", "*! hxregistry 3.1.1  14aug2026", "registry version")
s = once(
    s,
    'local graph_cmds "twoway scatter line connected lfit qfit histogram kdensity dotplot graph_box lowess lpoly rvfplot rvpplot avplot avplots lvr2plot cprplot acprplot tsline xtline roctab rocfit roccomp rocgold rocreg marginsplot coefplot event_plot"',
    'local graph_cmds "graph twoway scatter line connected lfit qfit histogram kdensity dotplot graph_box lowess lpoly rvfplot rvpplot avplot avplots lvr2plot cprplot acprplot tsline xtline roctab rocfit roccomp rocgold rocreg marginsplot coefplot event_plot"',
    "graph searchable command",
)
anchor = '        local key_histogram "histogram 直方图 分布 频数 密度"'
s = once(
    s,
    anchor,
    '        local key_graph "graph 饼图 散点图矩阵 质量控制 图形组合 管理图形 图形方案 图形大小"\n' + anchor,
    "graph search keywords",
)
p.write_text(s, encoding="utf-8")


# Java preview fixes.
p = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = p.read_text(encoding="utf-8")
j = j.replace('public static final String VERSION = "1.4.7";', 'public static final String VERSION = "1.4.8";', 1)
j = j.replace('SFIToolkit.displayln("HxWorkbench 1.4.7");', 'SFIToolkit.displayln("HxWorkbench 1.4.8");', 1)

old_graph_methods = '''         } else if ("graph".equals(var0)) {
            return Arrays.asList("数据分布", "变量关系", "分组趋势", "回归结果");
         } else if ("did".equals(var0)) {'''
new_graph_methods = '''         } else if ("graph".equals(var0)) {
            return Arrays.asList(
               "二维图(散点图，折线图等)", "条形图", "点图", "饼图", "直方图", "箱线图", "等高线图", "散点图矩阵", "分布图", "平滑和密度",
               "回归诊断图", "时间序列图", "面板数据折线图", "生存分析图", "ROC分析", "多元分析图", "质量控制", "更多统计图形", "图形组合", "管理图形", "更改方案/大小"
            );
         } else if ("did".equals(var0)) {'''
j = once(j, old_graph_methods, new_graph_methods, "graph preview methods")

routes = {
    "汇总，表格和假设检验": "summarize tabstat tabulate table ttest prtest sdtest oneway anova ranksum median signrank signtest",
    "线性模型及相关": "regress areg reghdfe cnsreg rreg qreg iqreg bsqreg vwls eivreg sureg mvreg correlate pwcorr",
    "二元结果": "logit logistic probit hetprobit scobit cloglog",
    "序数结果": "ologit oprobit",
    "分类结果": "mlogit mprobit asclogit asmprobit",
    "计数结果": "poisson nbreg ppmlhdfe zip zinb tpoisson tnbreg",
    "分数结果": "fracreg betareg",
    "广义线性模型": "glm",
    "选择模型": "heckman heckprobit heckoprobit heckpoisson",
    "时间序列": "arima newey prais arch ucm dfuller pperron corrgram pergram",
    "多元时间序列": "var svar vec varsoc vargranger varstable irf",
    "空间自回归模型": "spregress spivregress spxtregress",
    "纵向/面板数据": "xtreg xtlogit xtprobit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtabond xtdpdsys",
    "多层混合效应模型": "mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm",
    "生存分析": "stset sts stcox streg stcrreg",
    "流行病学及相关": "cc cs ir",
    "内生协变量": "eregress eprobit eoprobit epoisson eintreg",
    "样本选择模型": "heckman heckprobit heckoprobit heckpoisson",
    "因果推断/处理效应": "teffects etregress etpoisson didregress xtdidregress",
    "结构方程模型(SEM)": "sem gsem",
    "潜在类别分析(LCA)": "gsem",
    "有限混合模型(FMM)": "fmm",
    "项目反应理论(IRT)": "irt",
    "多元分析": "factor pca canon cca manova mvreg discrim cluster",
    "调查数据分析": "svy",
    "Lasso回归": "lasso elasticnet sqrtlasso dsregress poivregress xporegress xpoivregress",
    "Meta分析": "meta",
    "多重插补": "mi",
    "非参数分析": "ranksum median signrank signtest npregress kdensity lowess lpoly",
    "精确统计": "bitesti tabi",
    "重抽样": "bootstrap jackknife permute simulate statsby",
    "效能，精度和样品含量": "power",
    "贝叶斯分析": "bayes bayesmh bayespredict bayesstats bayesgraph",
    "贝叶斯模型平均": "bma",
    "工具变量与内生性": "ivregress ivreghdfe",
    "估计后分析": "test lincom predict margins",
    "二维图(散点图，折线图等)": "twoway scatter line connected lfit qfit lowess lpoly",
    "条形图": "twoway",
    "点图": "dotplot",
    "饼图": "graph",
    "直方图": "histogram",
    "箱线图": "graph_box",
    "等高线图": "twoway",
    "散点图矩阵": "graph",
    "分布图": "histogram kdensity",
    "平滑和密度": "kdensity lowess lpoly",
    "回归诊断图": "rvfplot rvpplot avplot avplots lvr2plot cprplot acprplot",
    "时间序列图": "tsline",
    "面板数据折线图": "xtline",
    "生存分析图": "sts",
    "ROC分析": "roctab rocfit roccomp rocgold rocreg",
    "多元分析图": "pca factor cluster",
    "质量控制": "graph",
    "更多统计图形": "marginsplot coefplot event_plot",
    "图形组合": "graph",
    "管理图形": "graph",
    "更改方案/大小": "graph",
}

pieces = []
for idx, (method, command_text) in enumerate(routes.items()):
    kw = "if" if idx == 0 else "else if"
    commands = command_text.split()
    if len(commands) == 1:
        ret = f'return Collections.singletonList("{commands[0]}");'
    else:
        args = ", ".join(f'"{cmd}"' for cmd in commands)
        ret = f"return Arrays.asList({args});"
    pieces.append(f'         {kw} ("{method}".equals(var0)) {{\n            {ret}\n         }} ')
block = "".join(pieces)

method_anchor = '''      private static List<String> previewCommandsForMethod(String var0) {
         if ("导入与转换".equals(var0)) {'''
method_replacement = '''      private static List<String> previewCommandsForMethod(String var0) {
''' + block + '''else if ("导入与转换".equals(var0)) {'''
j = once(j, method_anchor, method_replacement, "exhaustive preview command routes")
p.write_text(j, encoding="utf-8")


# Release metadata.
for name in ["hxempirical.ado", "hxempirical.sthlp"]:
    p = Path(name)
    p.write_text(p.read_text(encoding="utf-8").replace("1.4.7", "1.4.8"), encoding="utf-8")

p = Path("hxempirical.pkg")
p.write_text(p.read_text(encoding="utf-8").replace("d Version 1.4.7", "d Version 1.4.8"), encoding="utf-8")

p = Path("README.md")
x = p.read_text(encoding="utf-8")
x = x.replace("**当前发布版本：1.4.7**", "**当前发布版本：1.4.8**", 1)
x = re.sub(r"\*\*上次修改时间：[^\n]+\*\*", "**上次修改时间：2026-08-14 15:10（UTC+8）**", x, count=1)
marker = "## 修改记录\n"
note = """## 修改记录

### 2026-08-14 15:10（UTC+8）

- 深度自查搜索目录与点击目录的一致性：补齐 `graph` 搜索入口，解决饼图、散点图矩阵、质量控制、图形组合、图形管理等可点击但无法反向搜索的问题。
- 修复 Java 预览/自动化测试目录与正式 Stata 目录不一致：图形预览从旧的 4 个 HX 分类同步为当前 21 个 Stata 图形分类。
- `previewCommandsForMethod()` 对全部 36 个统计分类和 21 个图形分类建立与 `hxregistry` 一致的命令映射，后续 UI 渲染自查不再使用过时目录。
- 保留 `ppmlhdfe` 的正式路径：统计 → 计数结果 → ppmlhdfe，并将该路径纳入自动一致性审查。
"""
if marker not in x:
    raise SystemExit("README modification marker missing")
x = x.replace(marker, note, 1)
p.write_text(x, encoding="utf-8")
