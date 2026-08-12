from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"missing pattern: {label}")
    return text.replace(old, new, 1)


def replace_required(text: str, old: str, new: str, label: str, minimum: int = 1) -> str:
    count = text.count(old)
    if count < minimum:
        raise SystemExit(f"missing pattern: {label}; found {count}, need {minimum}")
    return text.replace(old, new)


# -----------------------------------------------------------------------------
# Java workbench
# -----------------------------------------------------------------------------
java_path = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
java = java_path.read_text(encoding="utf-8")
java = replace_once(java, 'public static final String VERSION = "1.0.2";', 'public static final String VERSION = "1.0.3";', "java version")
java = replace_once(java, 'SFIToolkit.displayln("HxWorkbench 1.0.2");', 'SFIToolkit.displayln("HxWorkbench 1.0.3");', "java version output")

# Hide the old custom DID category everywhere it was presented in category lists.
did_category_line = '         this.categoryModel.addElement(new HxWorkbench.Category("DID 专区", "did"));\n'
if java.count(did_category_line) < 3:
    raise SystemExit(f"expected at least 3 visible DID category entries, found {java.count(did_category_line)}")
java = java.replace(did_category_line, "")

# Preview-only hard-coded category indexes shift after removing DID.
java = replace_once(
    java,
    '      private void populateOneClickPreviewState() {\n         this.rebuilding = true;\n         this.categoryList.setSelectedIndex(7);',
    '      private void populateOneClickPreviewState() {\n         this.rebuilding = true;\n         this.categoryList.setSelectedIndex(6);',
    "oneclick preview category index",
)
java = replace_once(
    java,
    '      private void populateDidPreviewState() {\n         this.rebuilding = true;\n         this.categoryList.setSelectedIndex(6);',
    '      private void populateDidPreviewState() {\n         this.rebuilding = true;\n         this.categoryList.setSelectedIndex(3);',
    "dormant did preview category index",
)

# Native DID becomes a regression method in preview and real navigation.
java = replace_once(
    java,
    '         for (String var2 : Arrays.asList("线性模型", "面板模型", "二元结果", "计数模型", "工具变量")) {',
    '         for (String var2 : Arrays.asList("线性模型", "面板模型", "二元结果", "计数模型", "工具变量", "双重差分")) {',
    "preview regression methods",
)
java = replace_once(
    java,
    '            case "工具变量":\n               return "iv";',
    '            case "工具变量":\n               return "iv";\n            case "双重差分":\n               return "did";',
    "method code for native did",
)
java = replace_once(
    java,
    '         } else if ("工具变量".equals(var0)) {\n            return Arrays.asList("ivregress", "ivreghdfe");\n         } else if ("系数检验".equals(var0)) {',
    '         } else if ("工具变量".equals(var0)) {\n            return Arrays.asList("ivregress", "ivreghdfe");\n         } else if ("双重差分".equals(var0)) {\n            return Arrays.asList("didregress", "xtdidregress");\n         } else if ("系数检验".equals(var0)) {',
    "preview commands for native did",
)
java = replace_once(
    java,
    '         } else if ("reg".equals(var0)) {\n            return Arrays.asList("线性模型", "面板模型", "二元结果", "计数模型", "工具变量");',
    '         } else if ("reg".equals(var0)) {\n            return Arrays.asList("线性模型", "面板模型", "二元结果", "计数模型", "工具变量", "双重差分");',
    "preview reg category methods",
)
java = replace_once(
    java,
    '         } else if ("工具变量".equals(var0)) {\n            return "处理解释变量内生性";\n         } else if ("系数检验".equals(var0)) {',
    '         } else if ("工具变量".equals(var0)) {\n            return "处理解释变量内生性";\n         } else if ("双重差分".equals(var0)) {\n            return "使用 Stata 官方 didregress / xtdidregress 估计标准 DID";\n         } else if ("系数检验".equals(var0)) {',
    "native did method summary",
)
java = replace_once(
    java,
    '         } else if ("工具变量".equals(var0)) {\n            return "普通 IV 用 ivregress；同时需要吸收多组高维固定效应时用 ivreghdfe。";\n         } else if ("合并与追加".equals(var0)) {',
    '         } else if ("工具变量".equals(var0)) {\n            return "普通 IV 用 ivregress；同时需要吸收多组高维固定效应时用 ivreghdfe。";\n         } else if ("双重差分".equals(var0)) {\n            return "重复截面使用 Stata 官方 didregress；面板数据先 xtset，再使用 xtdidregress。";\n         } else if ("合并与追加".equals(var0)) {',
    "native did method recommendation",
)

# Keep the top task block at a fixed height so the expand/collapse control never jumps vertically.
java = replace_once(
    java,
    '         var9.setMaximumSize(new Dimension(Integer.MAX_VALUE, 390));',
    '         var9.setPreferredSize(new Dimension(800, 390));\n         var9.setMinimumSize(new Dimension(0, 390));\n         var9.setMaximumSize(new Dimension(Integer.MAX_VALUE, 390));',
    "fixed home task region height",
)

# Replace custom DID launcher with official Stata DID commands.
java = replace_once(
    java,
    '         var13.add(this.homeLauncherButton("DID / 事件研究", "分步构建与平行趋势", () -> this.browseMethodCategory("did"), true));',
    '         var13.add(this.homeLauncherButton("双重差分", "didregress / xtdidregress", () -> this.browseMethod("reg", "双重差分"), true));',
    "home native did launcher",
)
java = replace_once(
    java,
    '               {"工具变量", "内生变量与工具变量", "reg", "工具变量"}\n            },\n            false\n         );',
    '               {"工具变量", "内生变量与工具变量", "reg", "工具变量"},\n               {"双重差分", "didregress / xtdidregress", "reg", "双重差分"}\n            },\n            false\n         );',
    "expanded native did regression card",
)
java = replace_once(
    java,
    '            "专题与图形",\n            new String[][]{\n               {"DID", "双重差分与事件研究", "methodcategory", "did"},\n               {"OneClick", "控制变量组合与稳健性", "methodcategory", "oneclick"},\n               {"数据图形", "分布、散点与趋势", "graph", "数据分布"},\n               {"回归结果图", "系数图与边际效应", "graph", "回归结果"}\n            },\n            true',
    '            "Workflow 与图形",\n            new String[][]{\n               {"OneClick", "控制变量组合与稳健性", "methodcategory", "oneclick"},\n               {"数据图形", "分布、散点与趋势", "graph", "数据分布"},\n               {"回归结果图", "系数图与边际效应", "graph", "回归结果"}\n            },\n            true',
    "expanded workflow section",
)
java = replace_once(
    java,
    '               } else if (containsAny(var2, "平行趋势", "事件研究", "eventstudy", "did", "双重差分")) {\n                  this.browseMethodCategory("did");',
    '               } else if (containsAny(var2, "平行趋势", "事件研究", "eventstudy", "did", "双重差分")) {\n                  this.browseMethod("reg", "双重差分");',
    "smart search native did route",
)

# Add native DID command cards.
needle = '         addGuide(var0, "did_trends", "处理组与对照组趋势",'
pos = java.find(needle)
if pos < 0:
    raise SystemExit("missing guide insertion anchor")
new_guides = '''         addGuide(\n            var0,\n            "didregress",\n            "官方双重差分（重复截面）",\n            "使用 Stata 官方 didregress 估计 DID / DDD 的平均处理效应。",\n            "不同时间抽取不同个体的重复截面数据，处理在组层级发生。",\n            "didregress (y x1 x2) (treat), group(group) time(year)",\n            "Stata 17+ 官方命令；面板数据应改用 xtdidregress。"\n         );\n         addGuide(\n            var0,\n            "xtdidregress",\n            "官方面板双重差分",\n            "使用 Stata 官方 xtdidregress 在纵向 / 面板数据中估计 DID。",\n            "同一个体或企业被重复观察的面板数据；运行前先用 xtset 声明面板结构。",\n            "xtdidregress (y x1 x2) (treat), group(group) time(year)",\n            "Stata 17+ 官方命令；重复截面数据使用 didregress。"\n         );\n'''
java = java[:pos] + new_guides + java[pos:]

# Run monitor should recognize official DID estimators.
java = replace_once(
    java,
    '            "ivreghdfe",\n            "ppmlhdfe",',
    '            "ivreghdfe",\n            "didregress",\n            "xtdidregress",\n            "ppmlhdfe",',
    "estimation command registry",
)

# DID weights: official didregress/xtdidregress support f/a/p weights, not iweights.
java = replace_once(
    java,
    '         if ("ppmlhdfe".equals(this.currentCommand)) {\n            var2 = Arrays.asList("无", "fweight", "pweight");\n         } else if ("reghdfe".equals(this.currentCommand)) {',
    '         if (Arrays.asList("didregress", "xtdidregress").contains(this.currentCommand)) {\n            var2 = Arrays.asList("无", "fweight", "aweight", "pweight");\n         } else if ("ppmlhdfe".equals(this.currentCommand)) {\n            var2 = Arrays.asList("无", "fweight", "pweight");\n         } else if ("reghdfe".equals(this.currentCommand)) {',
    "native did weights",
)

# Focused validation for official DID fields.
java = replace_once(
    java,
    '            "xtreg", "xtlogit", "xtprobit", "logit", "probit", "poisson", "nbreg", "ppmlhdfe", "ivregress", "ivreghdfe"\n         );',
    '            "xtreg", "xtlogit", "xtprobit", "logit", "probit", "poisson", "nbreg", "ppmlhdfe", "ivregress", "ivreghdfe",\n            "didregress", "xtdidregress"\n         );',
    "focused estimator list",
)
java = replace_once(
    java,
    '         if ("areg".equals(this.currentCommand) && this.absorb.getSelectedValuesList().size() != 1) {',
    '''         if (Arrays.asList("didregress", "xtdidregress").contains(this.currentCommand)) {\n            String treatment = selected(this.panel);\n            String didTime = selected(this.time);\n            List<String> didGroups = this.absorb.getSelectedValuesList();\n            if (treatment.isBlank() || didTime.isBlank() || didGroups.isEmpty()) {\n               JOptionPane.showMessageDialog(this, "DID 需要选择处理变量、time() 时间变量和至少 1 个 group() 变量。", "DID 设置尚未完整", 1);\n               return false;\n            }\n            String outcome = selected(this.depvar);\n            if (treatment.equals(outcome) || didTime.equals(outcome) || didGroups.contains(outcome)) {\n               JOptionPane.showMessageDialog(this, "结果变量不能同时作为处理变量、时间变量或 group() 变量。", "DID 变量角色重复", 2);\n               return false;\n            }\n            if (didGroups.contains(treatment) || didGroups.contains(didTime) || treatment.equals(didTime)) {\n               JOptionPane.showMessageDialog(this, "处理变量、时间变量和 group() 变量需要使用不同的数据角色。", "DID 变量角色重复", 2);\n               return false;\n            }\n            LinkedHashSet<String> didControls = new LinkedHashSet<>(this.variables.getSelectedValuesList());\n            didControls.retainAll(Arrays.asList(outcome, treatment, didTime));\n            if (!didControls.isEmpty()) {\n               JOptionPane.showMessageDialog(this, "协变量 / 控制变量中重复选择了 DID 核心变量：" + String.join("、", didControls), "DID 变量角色重复", 2);\n               return false;\n            }\n         }\n\n         if ("areg".equals(this.currentCommand) && this.absorb.getSelectedValuesList().size() != 1) {''',
    "native did validation",
)

# commandMethod() path mapping.
java = replace_once(
    java,
    '         } else if (Arrays.asList("xtreg", "xtlogit", "xtprobit").contains(var0)) {',
    '         } else if (Arrays.asList("didregress", "xtdidregress").contains(var0)) {\n            return "回归模型|双重差分";\n         } else if (Arrays.asList("xtreg", "xtlogit", "xtprobit").contains(var0)) {',
    "native did breadcrumb path",
)

java_path.write_text(java, encoding="utf-8")


# -----------------------------------------------------------------------------
# Stata command registry
# -----------------------------------------------------------------------------
reg_path = Path("hxregistry.ado")
reg = reg_path.read_text(encoding="utf-8")
reg = replace_once(reg, '*! hxregistry 2.9.0  12aug2026', '*! hxregistry 2.9.1  12aug2026', "registry version")
reg = replace_once(
    reg,
    'local reg_cmds "regress areg reghdfe rreg cnsreg vwls eivreg qreg newey prais xtreg xtlogit xtprobit logit probit poisson nbreg ppmlhdfe ivregress ivreghdfe"',
    'local reg_cmds "regress areg reghdfe rreg cnsreg vwls eivreg qreg newey prais xtreg xtlogit xtprobit logit probit poisson nbreg ppmlhdfe ivregress ivreghdfe didregress xtdidregress"',
    "native did registry commands",
)
reg = replace_once(
    reg,
    'local workflow_cmds "hxconvert did_builder did_trends oneclick oneclick_robustness"',
    'local workflow_cmds "hxconvert oneclick oneclick_robustness"',
    "workflow catalog without custom did",
)
reg = replace_once(
    reg,
    'local all_cmds "`data_cmds\' `stats_cmds\' `reg_cmds\' `post_cmds\' `graph_cmds\' `did_cmds\' `oneclick_cmds\'"',
    'local all_cmds "`data_cmds\' `stats_cmds\' `reg_cmds\' `post_cmds\' `graph_cmds\' `oneclick_cmds\'"',
    "hide custom did commands from public catalog",
)
reg = replace_once(
    reg,
    'local reg_methods "线性模型 面板模型 二元结果 计数模型 工具变量"',
    'local reg_methods "线性模型 面板模型 二元结果 计数模型 工具变量 双重差分"',
    "native did regression method",
)
reg = replace_once(
    reg,
    '    local key_ivregress "ivregress iv 2sls gmm liml 工具变量 内生性"',
    '    local key_ivregress "ivregress iv 2sls gmm liml 工具变量 内生性"\n    local key_didregress "didregress did difference-in-differences ddd 双重差分 重复截面 平行趋势 因果推断"\n    local key_xtdidregress "xtdidregress did panel longitudinal 双重差分 面板 平行趋势 因果推断"',
    "native did search keys",
)
reg = replace_once(
    reg,
    '    else if inlist(`"`method\'"\', "工具变量", "iv") local view "ivregress ivreghdfe"',
    '    else if inlist(`"`method\'"\', "工具变量", "iv") local view "ivregress ivreghdfe"\n    else if inlist(`"`method\'"\', "双重差分", "did") local view "didregress xtdidregress"',
    "native did method view",
)
reg_path.write_text(reg, encoding="utf-8")


# -----------------------------------------------------------------------------
# Semantic roles
# -----------------------------------------------------------------------------
sem_path = Path("hxsemantics.ado")
sem = sem_path.read_text(encoding="utf-8")
sem = replace_once(sem, '*! hxsemantics 1.4.0  12aug2026', '*! hxsemantics 1.4.1  12aug2026', "semantics version")
sem = replace_once(
    sem,
    '        inlist("`cmd\'", "nbreg", "ppmlhdfe", "ivregress", "ivreghdfe") {',
    '        inlist("`cmd\'", "nbreg", "ppmlhdfe", "ivregress", "ivreghdfe", "didregress", "xtdidregress") {',
    "semantics estimator group",
)
sem = replace_once(
    sem,
    '        else if inlist("`cmd\'", "xtreg", "xtlogit", "xtprobit") {',
    '''        else if inlist("`cmd'", "didregress", "xtdidregress") {\n            local template "didregress"\n            local has_depvar 1\n            local has_varlist 1\n            local has_if 1\n            local has_in 1\n            local has_weight 1\n            local has_absorb 1\n            local has_vce 1\n            local has_cluster 1\n            local needs_panel 1\n            local models ""\n            local default_model ""\n            local vces "default robust cluster"\n            local dep_label "结果变量 Y"\n            local vars_label "协变量 / 控制变量（可多选）"\n            local panel_label "处理变量（通常为 0/1）"\n            local time_label "时间变量 time()"\n            local absorb_label "处理发生层级 group()（可多选）"\n            if "`cmd'" == "didregress" {\n                local title "didregress — Stata 官方双重差分（重复截面）"\n                local purpose1 "使用 Stata 官方 didregress 估计标准 DID / DDD 的 ATET。"\n                local purpose2 "适合重复截面数据；处理变量放在第二组括号，group() 指定处理发生层级，time() 指定时间。"\n                local example1 "didregress (y x1 x2) (treat), group(group) time(year)"\n                local explain1 "用官方 didregress 估计重复截面 DID，并加入 x1、x2 协变量。"\n                local example2 "estat trendplots"\n                local explain2 "估计后可继续使用 Stata 官方 DID 诊断工具。"\n            }\n            else {\n                local title "xtdidregress — Stata 官方面板双重差分"\n                local purpose1 "使用 Stata 官方 xtdidregress 在纵向 / 面板数据中估计标准 DID。"\n                local purpose2 "运行前先单独使用 xtset 声明面板结构；本页填写结果、协变量、处理变量、group() 和 time()。"\n                local example1 "xtdidregress (y x1 x2) (treat), group(group) time(year)"\n                local explain1 "在已 xtset 的面板数据上使用官方 xtdidregress。"\n                local example2 "estat ptrends"\n                local explain2 "估计后可继续使用 Stata 官方平行趋势检验。"\n            }\n        }\n        else if inlist("`cmd'", "xtreg", "xtlogit", "xtprobit") {''',
    "native did semantics",
)
sem_path.write_text(sem, encoding="utf-8")


# -----------------------------------------------------------------------------
# Resolver minimum contract
# -----------------------------------------------------------------------------
res_path = Path("hxresolve.ado")
res = res_path.read_text(encoding="utf-8")
res = replace_once(res, '*! hxresolve 3.1.2  12aug2026', '*! hxresolve 3.1.3  12aug2026', "resolver version")
res = replace_once(
    res,
    '    if "`cmd\'" == "ivreghdfe" {\n        local has_iv 1\n    }',
    '''    if "`cmd'" == "ivreghdfe" {\n        local has_iv 1\n    }\n    if inlist("`cmd'", "didregress", "xtdidregress") {\n        local has_depvar 1\n        local has_varlist 1\n        local has_if 1\n        local has_in 1\n        local has_weight 1\n        local has_absorb 1\n        local has_vce 1\n        local has_cluster 1\n        local needs_panel 1\n        local vces "default robust cluster"\n    }''',
    "native did minimum contract",
)
res_path.write_text(res, encoding="utf-8")


# -----------------------------------------------------------------------------
# Native command generation
# -----------------------------------------------------------------------------
prev_path = Path("hxpreview.ado")
prev = prev_path.read_text(encoding="utf-8")
prev = replace_once(prev, '*! hxpreview 1.3.0  12aug2026', '*! hxpreview 1.3.1  12aug2026', "preview version")
prev = replace_once(
    prev,
    '    local opt ""\n\n    if "`is_xtset\'" == "1" {',
    '''    local opt ""\n\n    if `"`template'"' == "didregress" {\n        local did_outcome `"`depvar'"'\n        if `"`vars'"' != "" local did_outcome `"`did_outcome' `vars'"'\n        local preview `"`command'"'\n        if `"`did_outcome'"' != "" local preview `"`preview' (`did_outcome')"'\n        if `"`panel'"' != "" local preview `"`preview' (`panel')"'\n        if `"`absorb'"' != "" local opt `"`opt' group(`absorb')"'\n        if `"`time'"' != "" local opt `"`opt' time(`time')"'\n        local has_depvar 0\n        local has_varlist 0\n        local has_absorb 0\n        local needs_panel 0\n    }\n\n    if "`is_xtset'" == "1" {''',
    "native did preview core",
)
# Put Stata weights after if/in, which is the syntax order used by official estimators including DID.
weight_block = '''    if "`has_weight'" == "1" & `"`weight'"' != "" & `"`weightvar'"' != "" {\n        local preview `"`preview' [`weight'=`weightvar']"'\n    }\n\n'''
if prev.count(weight_block) != 1:
    raise SystemExit(f"expected one generic weight block, found {prev.count(weight_block)}")
prev = prev.replace(weight_block, "", 1)
prev = replace_once(
    prev,
    '    if "`has_in\'" == "1" & `"`incond\'"\' != "" {\n        local preview `"`preview\' in `incond\'"\'\n    }\n\n    if `"`template\'"\' == "margins"',
    '    if "`has_in\'" == "1" & `"`incond\'"\' != "" {\n        local preview `"`preview\' in `incond\'"\'\n    }\n    if "`has_weight\'" == "1" & `"`weight\'"\' != "" & `"`weightvar\'"\' != "" {\n        local preview `"`preview\' [`weight\'=`weightvar\']"\'\n    }\n\n    if `"`template\'"\' == "margins"',
    "weight syntax order",
)
prev_path.write_text(prev, encoding="utf-8")


# -----------------------------------------------------------------------------
# Package version metadata
# -----------------------------------------------------------------------------
pkg_path = Path("hxempirical.pkg")
pkg = pkg_path.read_text(encoding="utf-8")
pkg = replace_once(pkg, 'd Version 1.0.2', 'd Version 1.0.3', "pkg version")
pkg_path.write_text(pkg, encoding="utf-8")

ado_path = Path("hxempirical.ado")
ado = ado_path.read_text(encoding="utf-8")
ado = replace_once(ado, '*! hxempirical 1.0.2  12aug2026', '*! hxempirical 1.0.3  12aug2026', "ado version")
ado = replace_required(ado, '"1.0.2"', '"1.0.3"', "ado visible versions", 2)
ado_path.write_text(ado, encoding="utf-8")

help_path = Path("hxempirical.sthlp")
help_text = help_path.read_text(encoding="utf-8")
help_text = replace_once(help_text, '{* *! version 1.0.2  12aug2026}{...}', '{* *! version 1.0.3  12aug2026}{...}', "help version")
help_text = replace_once(
    help_text,
    'variables.\n\n{pstd}\nThe built-in linear-regression catalog also exposes',
    'variables. The regression catalog also includes Stata 17+ official DID commands: {cmd:didregress} for repeated cross-sectional data and {cmd:xtdidregress} for panel/longitudinal data. The old custom DID section is no longer shown as a separate public workflow.\n\n{pstd}\nThe built-in linear-regression catalog also exposes',
    "help native did introduction",
)
old_did_help = '''{pstd}\n{bf:DID 专区 > DID分步构建} is designed for a common policy timing setup and keeps calendar time, treatment group,\n{cmd:post}, relative {cmd:event_time}, and the regression-safe {cmd:event_code}\nseparate. The page shows only the fields required by the current step. It can\ngenerate {cmd:post}, {cmd:did}, and {cmd:event_time}; run\n{cmd:hxdidencode event_time, generate(event_code) base(-1)} to convert negative\nrelative periods into a nonnegative factor-variable code while preserving the\nchosen base period; build {cmd:i.treat##i.post}; build an event-study interaction\n{cmd:i.treat##i.event_code}; and automatically build the pre-policy {cmd:testparm}\njoint test from the actual last event-study {cmd:e(b)} and {cmd:e(sample)}. The\nworkbench records the event-study result after a successful run and refuses to\ntest if another estimation result has replaced it. Before estimation, treat/post\nare checked as numeric 0/1 variables on the requested regression sample, including\n{cmd:if} restrictions and complete-case requirements, and the selected event-study\nbase period must exist in the data. This avoids feeding negative relative-time\nvalues directly to Stata factor-variable notation. Staggered-treatment DID should\nuse a method designed for varying treatment dates.\n\n'''
new_did_help = '''{pstd}\nDifference-in-differences is now exposed through Stata's official commands rather than a separate HX DID workflow. Use {cmd:didregress} for repeated cross-sectional data and {cmd:xtdidregress} for panel/longitudinal data. For panel data, declare the panel structure first with {cmd:xtset}. The workbench generates the native command, for example {cmd:didregress (y x1 x2) (treat), group(group) time(year)}. After estimation, Stata's official DID postestimation tools such as {cmd:estat trendplots}, {cmd:estat ptrends}, and {cmd:estat granger} remain available in Stata.\n\n'''
help_text = replace_once(help_text, old_did_help, new_did_help, "replace old DID help section")
help_text = replace_once(help_text, 'HX empirical workbench, package version 1.0.2.', 'HX empirical workbench, package version 1.0.3.', "help footer version")
help_path.write_text(help_text, encoding="utf-8")


# -----------------------------------------------------------------------------
# README: release notes and architecture
# -----------------------------------------------------------------------------
readme_path = Path("README.md")
readme = readme_path.read_text(encoding="utf-8")
readme = replace_once(readme, '**当前发布版本：1.0.2**', '**当前发布版本：1.0.3**', "readme current version")
readme = replace_once(readme, '**上次修改时间：2026-08-12 16:49（UTC+8）**', '**上次修改时间：2026-08-12 17:18（UTC+8）**', "readme modified time")
readme = replace_once(
    readme,
    '- **DID Workflow**：围绕 DID 变量准备、事件时间、事件研究、政策前联合检验和动态图等步骤组织完整流程。',
    '- **Stata 官方 DID**：把 `didregress`（重复截面）和 `xtdidregress`（面板 / 纵向数据）作为普通命令直接使用；不再单独展示 HX DID 专区。',
    "readme capability native did",
)
readme = replace_once(
    readme,
    '| 工具变量 | `ivregress` / `ivreghdfe` |\n| 描述统计 |',
    '| 工具变量 | `ivregress` / `ivreghdfe` |\n| 双重差分 | `didregress` / `xtdidregress` |\n| 描述统计 |',
    "readme command table did",
)
readme = replace_once(
    readme,
    '目前主要包括：\n\n- **DID 专区**：将 DID 构造、事件时间、事件研究、政策前联合检验、图形等步骤放在同一流程中。\n- **OneClick 专区**：调用真实外部 `oneclick` / `oneclick_robustness`，并补充参数组织、结果读取和运行隔离。',
    '当前自定义专区主要保留：\n\n- **OneClick 专区**：调用真实外部 `oneclick` / `oneclick_robustness`，并补充参数组织、结果读取和运行隔离。\n\nDID 不再作为 HX 专区重复实现；标准 DID 优先进入普通命令层，直接调用 Stata 官方 `didregress` / `xtdidregress`。',
    "readme workflow architecture",
)
new_change = '''### 2026-08-12 17:18（UTC+8）\n\n**修改时间**：2026-08-12 17:18（UTC+8）\n\n**修改内容**：\n\n- 固定开始页“展开全部功能 / 收起全部功能”控制区的垂直位置；展开完整功能目录时，按钮不再因为上方任务区被压缩而上下跳动。\n- 按“官方命令优先”原则取消公开的 HX DID 专区入口；标准 DID 改为回归模型中的普通命令方法。\n- 新增 Stata 官方 `didregress` 与 `xtdidregress` 页面：重复截面使用 `didregress`，面板 / 纵向数据使用 `xtdidregress`；页面结构化填写结果变量、协变量、处理变量、`group()`、`time()`、权重和标准误，并生成真实官方 Stata 命令。\n- 首页“双重差分”、完整功能目录和 DID 关键词搜索全部改为进入官方 DID 命令选择页；旧 `did_builder` / `did_trends` / `event_plot` 不再作为 DID 专区公开导航。\n- DID 运行前增加核心变量角色和必填项检查；`xtdidregress` 页面明确提示先使用 `xtset` 声明面板结构。\n- 修正通用命令生成中的权重位置，使 `[weight=var]` 位于 `if/in` 之后，更符合 Stata 官方 syntax 顺序。\n- Java 工作台、Stata 命令目录、语义层、解析兜底、命令生成、help、package manifest 与 README 同步更新为 **1.0.3**，并重新构建 `hxworkbench.jar`。\n\n'''
readme = replace_once(readme, '## 修改记录\n\n', '## 修改记录\n\n' + new_change, "readme modification record")
new_release = '''### 1.0.3（当前版本）\n\n**发布时间**：2026-08-12 17:18（UTC+8）\n\n**修改内容**：\n\n- 稳定开始页展开 / 收起按钮位置。\n- 标准 DID 改为优先使用 Stata 官方 `didregress` / `xtdidregress`，不再公开单独 HX DID 专区。\n- DID 页面、搜索、命令目录、运行前检查和真实命令生成同步完成；权重语法顺序一并修正。\n\n### 1.0.2'''
readme = replace_once(readme, '### 1.0.2（当前版本）', new_release, "readme release section")
readme_path.write_text(readme, encoding="utf-8")

print("HX_NATIVE_DID_103_PATCH_OK")
