from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "src/main/java/com/hexie/stata/HxWorkbench.java"
STATIC = ROOT / "tools/verify_static_contracts.py"
text = JAVA.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    text = text.replace(old, new, 1)


def insert_before(anchor: str, addition: str, label: str) -> None:
    replace_once(anchor, addition + anchor, label)


# Dedicated event_plot naming controls. They are result metadata, not data variables.
replace_once(
    '      private final JTextField specialGraphQcUpper = new JTextField();\n      private final JComboBox<String> regressX = variableCombo();',
    '      private final JTextField specialGraphQcUpper = new JTextField();\n      private final JTextField specialGraphEventStubLag = new JTextField();\n      private final JTextField specialGraphEventStubLead = new JTextField();\n      private final JComboBox<String> regressX = variableCombo();',
    "event_plot result fields",
)

replace_once(
    '''            this.specialGraphQcLower,\n            this.specialGraphQcUpper,\n            this.model,''',
    '''            this.specialGraphQcLower,\n            this.specialGraphQcUpper,\n            this.specialGraphEventStubLag,\n            this.specialGraphEventStubLead,\n            this.model,''',
    "event_plot preview listeners",
)

# Route all three result-based graph commands into the same dedicated graph workspace.
old_route = '"cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar", "graph_combine", "graph", "did_trends", "twoway"'
new_route = '"cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar", "marginsplot", "coefplot", "event_plot", "graph_combine", "graph", "did_trends", "twoway"'
count = text.count(old_route)
if count != 2:
    raise SystemExit(f"result graph route anchors: expected 2, found {count}")
text = text.replace(old_route, new_route)

# Result graphs do not accept an observation-level if qualifier here.
replace_once(
    '&& !Arrays.asList("screeplot", "scoreplot", "loadingplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay", "cchart", "pchart", "graph_combine", "graph").contains(var1);',
    '&& !Arrays.asList("screeplot", "scoreplot", "loadingplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay", "cchart", "pchart", "marginsplot", "coefplot", "event_plot", "graph_combine", "graph").contains(var1);',
    "result graph no-if contract",
)

# Reset and style result metadata fields when entering a graph page.
replace_once(
    '''         styleTextField(this.specialGraphQcLower);\n         styleTextField(this.specialGraphQcUpper);\n         this.configureSpecialGraphModel(var1);''',
    '''         styleTextField(this.specialGraphQcLower);\n         styleTextField(this.specialGraphQcUpper);\n         this.specialGraphEventStubLag.setText("");\n         this.specialGraphEventStubLead.setText("");\n         styleTextField(this.specialGraphEventStubLag);\n         styleTextField(this.specialGraphEventStubLead);\n         this.configureSpecialGraphModel(var1);''',
    "result graph reset/style",
)

# Add dedicated page copy before graph combine.
header_anchor = '''         } else if ("graph_combine".equals(var1)) {\n            this.commandTitle.setText("graph combine · 组合已生成图形");'''
header_addition = r'''         } else if ("marginsplot".equals(var1)) {
            this.commandTitle.setText("marginsplot · margins 结果图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> marginsplot</html>");
            this.insightArea.setText("主要意图：把上一条 margins 保存的预测、边际效应或对比结果直接绘图。\n\n横轴、分组和置信区间来自 margins 的结果；本页不重新要求选择原始数据里的 Y / X。\n\nrecast()/recastci()/plotopts()、参考线、标题以及 xsize()/ysize()/scale() 继续使用 Stata 原生图形 options。");
            this.syntaxArea.setText("marginsplot [, options]");
            coreTitle = "上一条 margins 结果";
            coreSubtitle = "直接复用当前 margins 结果；需要改变横轴或情景时，应先重新运行 margins。";
         } else if ("coefplot".equals(var1)) {
            this.commandTitle.setText("coefplot · 回归系数与置信区间图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> coefplot m1 m2, drop(_cons) xline(0)</html>");
            this.insightArea.setText("主要意图：从当前模型、已保存 estimates 或 Stata matrix 中提取系数并比较置信区间。\n\n结果对象可留空表示当前活动模型，也可填写 m1 m2、(m1) (m2) 或 matrix(...) 等作者原生规格；这里不把数据变量误当成系数来源。\n\nkeep()/drop()/rename()/recast()、参考线、标签、分组和尺寸继续使用 coefplot / twoway 原生 options。");
            this.syntaxArea.setText("coefplot subgraph [ || subgraph ... ] [, globalopts]");
            coreTitle = "估计结果 / 矩阵对象";
            coreSubtitle = "留空使用当前活动模型；多个保存模型或矩阵按 coefplot 原生 result specification 填写。";
         } else if ("event_plot".equals(var1)) {
            this.commandTitle.setText("event_plot · Event Study 动态系数图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> event_plot, default_look</html>");
            this.insightArea.setText("主要意图：把已经估计好的事件研究系数和置信区间画成动态效应图。\n\n结果对象可留空使用当前 estimation result，也可填写一个或多个 stored estimates，或 bmat#Vmat 矩阵对；最多组合 8 个结果。\n\ndid_imputation 的 tau#/pre# 命名可自动识别；其他估计器无法自动识别时，显式填写 stub_lag()/stub_lead()。图形样式继续使用作者原生 options。");
            this.syntaxArea.setText("event_plot [result_spec ...] [, stub_lag(string) stub_lead(string) options]");
            coreTitle = "事件研究结果对象";
            coreSubtitle = "先指定结果来源；系数前后期命名无法自动识别时，再填写 lag / lead stub。";
'''
insert_before(header_anchor, header_addition, "result graph page headers")

# True inputs for each result graph.
core_anchor = '''         } else if ("graph_combine".equals(var1)) {\n            this.addGenericBodyField(coreBody, "图形名 / .gph 文件（空格分隔）", this.expression);'''
core_addition = r'''         } else if ("marginsplot".equals(var1)) {
            JLabel marginsHint = new JLabel("<html>使用最近一次成功的 <b>margins</b> 结果。若需要新的 at()/dydx()/contrast 情景，请先回到 margins 页面重新计算。</html>");
            marginsHint.setForeground(MUTED);
            marginsHint.setFont(marginsHint.getFont().deriveFont(10.0F));
            marginsHint.setAlignmentX(0.0F);
            coreBody.add(marginsHint);
         } else if ("coefplot".equals(var1)) {
            this.addGenericBodyField(coreBody, "模型 / 矩阵规格（可留空）", this.expression);
            JLabel coefHint = new JLabel("<html>留空 = 当前模型；常见写法：<b>m1 m2</b>。需要分组、多个 subgraph 或 matrix() 时可直接使用 coefplot 作者原生规格。</html>");
            coefHint.setForeground(MUTED);
            coefHint.setFont(coefHint.getFont().deriveFont(9.8F));
            coefHint.setAlignmentX(0.0F);
            coreBody.add(coefHint);
         } else if ("event_plot".equals(var1)) {
            this.addGenericBodyField(coreBody, "结果对象（可留空）", this.expression);
            JPanel eventStubs = new JPanel(new GridLayout(1, 2, 12, 0));
            eventStubs.setOpaque(false);
            eventStubs.add(this.fieldBlock("政策后 stub_lag()（可选）", this.specialGraphEventStubLag));
            eventStubs.add(this.fieldBlock("政策前 stub_lead()（可选）", this.specialGraphEventStubLead));
            this.addGenericBodyField(coreBody, "系数命名规则", eventStubs);
            JLabel eventHint = new JLabel("<html>stub 中用 <b>#</b> 代表相对期数字，例如 tau# / pre#；多个结果可按顺序填写多个 stub。did_imputation 默认通常可留空。</html>");
            eventHint.setForeground(MUTED);
            eventHint.setFont(eventHint.getFont().deriveFont(9.8F));
            eventHint.setAlignmentX(0.0F);
            coreBody.add(eventHint);
'''
insert_before(core_anchor, core_addition, "result graph core inputs")

# Generate the real commands from result objects, never from dataset variables.
preview_anchor = '''         } else if ("graph_combine".equals(this.currentCommand)) {\n            var1 = "graph combine " + this.expression.getText().trim();'''
preview_addition = r'''         } else if ("marginsplot".equals(this.currentCommand)) {
            var1 = "marginsplot";
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if ("coefplot".equals(this.currentCommand)) {
            String resultSpec = this.expression.getText().trim();
            var1 = "coefplot" + (resultSpec.isBlank() ? "" : " " + resultSpec);
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if ("event_plot".equals(this.currentCommand)) {
            String resultSpec = this.expression.getText().trim();
            ArrayList<String> eventOpts = new ArrayList<>();
            String stubLag = this.specialGraphEventStubLag.getText().trim();
            String stubLead = this.specialGraphEventStubLead.getText().trim();
            if (!stubLag.isBlank()) eventOpts.add("stub_lag(" + stubLag + ")");
            if (!stubLead.isBlank()) eventOpts.add("stub_lead(" + stubLead + ")");
            if (!this.options.getText().trim().isBlank()) eventOpts.add(this.options.getText().trim());
            var1 = "event_plot" + (resultSpec.isBlank() ? "" : " " + resultSpec);
            if (!eventOpts.isEmpty()) var1 += ", " + String.join(" ", eventOpts);
'''
insert_before(preview_anchor, preview_addition, "result graph preview builders")

# Author requires # placeholder in explicit event_plot stubs.
validate_anchor = '''         if ("graph_combine".equals(command)) {\n            String[] graphNames = this.expression.getText().trim().split("\\\\s+");'''
validate_addition = r'''         if ("event_plot".equals(command)) {
            String lagStub = this.specialGraphEventStubLag.getText().trim();
            String leadStub = this.specialGraphEventStubLead.getText().trim();
            if (!lagStub.isBlank() && !lagStub.contains("#")) {
               JOptionPane.showMessageDialog(this, "event_plot 的 stub_lag() 需要用 # 标记相对期数字，例如 tau#。", "stub_lag() 格式错误", 1);
               return false;
            }
            if (!leadStub.isBlank() && !leadStub.contains("#")) {
               JOptionPane.showMessageDialog(this, "event_plot 的 stub_lead() 需要用 # 标记相对期数字，例如 pre#。", "stub_lead() 格式错误", 1);
               return false;
            }
         }
'''
insert_before(validate_anchor, validate_addition, "event_plot stub validation")

# External result-graph pages retain the existing manual-dependency policy.
replace_once(
    '         this.statusLabel.setText("图形页面按变量设定 → 检查运行组织；右侧图形预览会随变量选择更新。");',
    '         this.statusLabel.setText(Arrays.asList("marginsplot", "coefplot", "event_plot").contains(var1) ? "结果图页面按结果对象 → 图形设置组织；不会要求重新选择原始数据变量。" : "图形页面按变量设定 → 检查运行组织；右侧图形预览会随变量选择更新。");\n         if (!this.previewMode && Arrays.asList("coefplot", "event_plot").contains(var1)) this.offerOptionalDependency(var1);',
    "result graph status/dependency",
)

# Clarify the final Graphics catalog entry without inventing a global size command.
replace_once(
    '            case "更多统计图形": return "symplot · qnorm · qqplot · dotplot · sunflower · marginsplot · coefplot";',
    '            case "更多统计图形": return "symplot · qnorm · qqplot · dotplot · sunflower · marginsplot · coefplot · event_plot";',
    "more statistical graphs hint",
)
replace_once(
    '            case "更改方案/大小": return "set scheme";',
    '            case "更改方案/大小": return "set scheme · 单图 xsize()/ysize()/scale()";',
    "scheme/size hint",
)

JAVA.write_text(text, encoding="utf-8")

# Static contracts: these pages must stay structured and result-based.
s = STATIC.read_text(encoding="utf-8")
old_special = '"cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar", "graph_combine", "graph", "did_trends", "twoway"'
new_special = '"cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar", "marginsplot", "coefplot", "event_plot", "graph_combine", "graph", "did_trends", "twoway"'
if s.count(old_special) != 1:
    raise SystemExit(f"static special route anchor count={s.count(old_special)}")
s = s.replace(old_special, new_special, 1)
old_tuple = '"cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar", "graph_combine", "graph"):'
new_tuple = '"cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar", "marginsplot", "coefplot", "event_plot", "graph_combine", "graph"):'
if s.count(old_tuple) != 1:
    raise SystemExit(f"static required tuple anchor count={s.count(old_tuple)}")
s = s.replace(old_tuple, new_tuple, 1)
qc_end = '''    if needle not in java:\n        fail(f"quality-control Graphics page contract missing: {needle}")\n\n'''
if s.count(qc_end) != 1:
    raise SystemExit(f"result graph static insertion anchor count={s.count(qc_end)}")
result_contract = '''for needle in (\n    'marginsplot · margins 结果图',\n    'coefplot · 回归系数与置信区间图',\n    'event_plot · Event Study 动态系数图',\n    'var1 = "marginsplot";',\n    'var1 = "coefplot" + (resultSpec.isBlank() ? "" : " " + resultSpec);',\n    'var1 = "event_plot" + (resultSpec.isBlank() ? "" : " " + resultSpec);',\n    'eventOpts.add("stub_lag(" + stubLag + ")")',\n    'event_plot 的 stub_lag() 需要用 # 标记相对期数字',\n    '结果图页面按结果对象 → 图形设置组织',\n    'set scheme · 单图 xsize()/ysize()/scale()',\n):\n    if needle not in java:\n        fail(f"result-based Graphics page contract missing: {needle}")\nfor graph_cmd in ("marginsplot", "coefplot", "event_plot"):\n    if graph_cmd not in roc_route_scope:\n        fail(f"result-based graph must route to graph result view: {graph_cmd}")\n\n'''
s = s.replace(qc_end, qc_end + result_contract, 1)
STATIC.write_text(s, encoding="utf-8")
print("HX_RESULT_GRAPHICS_PATCH_OK")
