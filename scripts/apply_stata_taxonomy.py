from pathlib import Path

p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')

s = s.replace('public static final String VERSION = "1.2.5";', 'public static final String VERSION = "1.2.6";')
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.2.5");', 'SFIToolkit.displayln("HxWorkbench 1.2.6");')
s = s.replace('new JLabel("版本：1.2.5")', 'new JLabel("版本：1.2.6")')

old_sidebar = '''         nav.add(this.sidebarButton("data", "▤", "数据", () -> this.browseCategoryOverview("data")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("reg", "↗", "回归", () -> this.browseMethod("reg", "线性模型")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("stats", "✓", "检验", () -> this.browseCategoryOverview("stats")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("oneclick", "◆", "OneClick", () -> this.browseMethodCategory("oneclick")));'''
new_sidebar = '''         nav.add(this.sidebarButton("data", "", "数据", () -> this.browseCategoryOverview("data")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("stats", "", "统计", () -> this.browseCategoryOverview("stats")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("graph", "", "图形", () -> this.browseCategoryOverview("graph")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("oneclick", "", "OneClick", () -> this.browseMethodCategory("oneclick")));'''
if old_sidebar not in s:
    raise SystemExit('sidebar anchor not found')
s = s.replace(old_sidebar, new_sidebar, 1)

s = s.replace('return "统计与检验";', 'return "统计";')
s = s.replace('new HxWorkbench.Category("统计与检验", "stats")', 'new HxWorkbench.Category("统计", "stats")')
s = s.replace('case "二元结果":\n               return "binary";', 'case "二元结果":\n               return "binary_outcomes";')

anchor = '''            case "描述统计":
               return "descriptive";'''
additions = '''            case "汇总，表格和假设检验":
               return "summary_tests";
            case "线性模型及相关":
               return "linear_related";
            case "序数结果":
               return "ordinal_outcomes";
            case "分类结果":
               return "categorical_outcomes";
            case "计数结果":
               return "count_outcomes";
            case "分数结果":
               return "fractional_outcomes";
            case "广义线性模型":
               return "glm_models";
            case "选择模型":
               return "selection_models";
            case "时间序列":
               return "time_series";
            case "多元时间序列":
               return "multivariate_ts";
            case "空间自回归模型":
               return "spatial_ar";
            case "纵向/面板数据":
               return "panel_longitudinal";
            case "多层混合效应模型":
               return "mixed_effects";
            case "生存分析":
               return "survival";
            case "流行病学及相关":
               return "epidemiology";
            case "内生协变量":
               return "endogenous_covariates";
            case "样本选择模型":
               return "sample_selection";
            case "因果推断/处理效应":
               return "causal_treatment";
            case "结构方程模型(SEM)":
               return "sem";
            case "潜在类别分析(LCA)":
               return "lca";
            case "有限混合模型(FMM)":
               return "fmm";
            case "项目反应理论(IRT)":
               return "irt";
            case "多元分析":
               return "multivariate";
            case "调查数据分析":
               return "survey";
            case "Lasso回归":
               return "lasso";
            case "Meta分析":
               return "meta";
            case "多重插补":
               return "mi";
            case "非参数分析":
               return "nonparametric";
            case "精确统计":
               return "exact_stats";
            case "重抽样":
               return "resampling";
            case "效能，精度和样品含量":
               return "power_precision";
            case "贝叶斯分析":
               return "bayes";
            case "贝叶斯模型平均":
               return "bma";
            case "二维图(散点图，折线图等)":
               return "twoway_graphs";
            case "条形图":
               return "bar_graph";
            case "点图":
               return "dot_graph";
            case "饼图":
               return "pie_graph";
            case "直方图":
               return "histogram_graph";
            case "箱线图":
               return "box_graph";
            case "等高线图":
               return "contour_graph";
            case "散点图矩阵":
               return "matrix_graph";
            case "分布图":
               return "distribution_graph";
            case "平滑和密度":
               return "smooth_density";
            case "回归诊断图":
               return "reg_diagnostic_graph";
            case "时间序列图":
               return "ts_graph";
            case "面板数据折线图":
               return "panel_line_graph";
            case "生存分析图":
               return "survival_graph";
            case "ROC分析":
               return "roc_graph";
            case "多元分析图":
               return "multivariate_graph";
            case "质量控制":
               return "quality_graph";
            case "更多统计图形":
               return "more_stat_graph";
            case "图形组合":
               return "graph_combine";
            case "管理图形":
               return "graph_manage";
            case "更改方案/大小":
               return "graph_scheme";
'''
if anchor not in s:
    raise SystemExit('methodCode anchor not found')
s = s.replace(anchor, additions + anchor, 1)

replacements = {
    'return "统计与检验|描述统计";': 'return "统计|汇总，表格和假设检验";',
    'return "统计与检验|相关分析";': 'return "统计|线性模型及相关";',
    'return "统计与检验|均值检验";': 'return "统计|汇总，表格和假设检验";',
    'return "统计与检验|频数列联";': 'return "统计|汇总，表格和假设检验";',
    'return "回归模型|线性模型";': 'return "统计|线性模型及相关";',
    'return "回归模型|双重差分";': 'return "统计|因果推断/处理效应";',
    'return "回归模型|面板模型";': 'return "统计|纵向/面板数据";',
    'return "回归模型|二元结果";': 'return "统计|二元结果";',
    'return "回归模型|计数模型";': 'return "统计|计数结果";',
    'return "图形|数据分布";': 'return "图形|分布图";',
    'return "图形|变量关系";': 'return "图形|二维图(散点图，折线图等)";',
    'return "图形|回归结果";': 'return "图形|更多统计图形";'
}
for a, b in replacements.items():
    s = s.replace(a, b)

p.write_text(s, encoding='utf-8')

for fn in ['hxempirical.ado', 'hxempirical.pkg', 'hxempirical.sthlp', 'hxtoolbox.sthlp', 'README.md']:
    q = Path(fn)
    if q.exists():
        t = q.read_text(encoding='utf-8').replace('1.2.5', '1.2.6')
        q.write_text(t, encoding='utf-8')

stub = Path('/tmp/sfi/com/stata/sfi')
stub.mkdir(parents=True, exist_ok=True)
Path('/tmp/classes').mkdir(parents=True, exist_ok=True)
files = {
'SFIToolkit.java': '''package com.stata.sfi; public class SFIToolkit { public static int executeCommand(String s, boolean b){return 0;} public static void errorln(String s){} public static void displayln(String s){} public static String stackTraceToString(Throwable t){return "";} }''',
'Characteristic.java': '''package com.stata.sfi; public class Characteristic { public static String getDtaChar(String s){return "";} }''',
'Macro.java': '''package com.stata.sfi; public class Macro { public static String getGlobal(String s){return "";} public static String getLocal(String s){return "";} public static void setGlobal(String s,String v){} public static void setLocal(String s,String v){} }''',
'Missing.java': '''package com.stata.sfi; public class Missing { public static boolean isMissing(double d){return Double.isNaN(d);} }''',
'Scalar.java': '''package com.stata.sfi; public class Scalar { public static double getValue(String s){return Double.NaN;} }''',
'Data.java': '''package com.stata.sfi; public class Data { public static long getObsTotal(){return 0L;} public static int getVarCount(){return 0;} public static String getVarName(int i){return "";} public static String getVarLabel(int i){return "";} public static String getVarFormat(int i){return "";} public static int getVarIndex(String s){return -1;} public static boolean isVarTypeString(int i){return false;} public static double getNum(int i,long j){return Double.NaN;} public static String getStr(int i,long j){return "";} public static String getFormattedValue(int i,long j){return "";} public static void storeNum(int i,long j,double d){} public static void storeStr(int i,long j,String s){} }''',
'Frame.java': '''package com.stata.sfi; public class Frame { public static Frame create(String s){return new Frame();} public static Frame connect(String s){return new Frame();} public void drop(){} public long getObsTotal(){return 0L;} public int getVarCount(){return 0;} public String getVarName(int i){return "";} public int getVarIndex(String s){return -1;} public boolean isVarTypeString(int i){return false;} public double getNum(int i,long j){return Double.NaN;} public String getStr(int i,long j){return "";} public String getFormattedValue(int i,long j){return "";} }'''
}
for name, text in files.items():
    (stub / name).write_text(text, encoding='utf-8')
