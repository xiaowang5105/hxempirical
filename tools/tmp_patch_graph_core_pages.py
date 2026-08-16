from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


def exact_count_replace(text: str, old: str, new: str, count: int, label: str) -> str:
    n = text.count(old)
    if n != count:
        raise SystemExit(f"{label}: expected {count} matches, got {n}")
    return text.replace(old, new)


jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")

# Version marker for this visible UI batch.
j = once(j, 'public static final String VERSION = "1.5.11";', 'public static final String VERSION = "1.5.12";', "Java version")

# Shared UI control for the common survival-graph option.
field_anchor = '      private final JComboBox<String> genericWeightVar = variableCombo();\n'
j = once(
    j,
    field_anchor,
    field_anchor + '      private final JCheckBox specialGraphRiskTable = new JCheckBox("显示风险人数表 risktable", false);\n',
    "survival graph risk-table field",
)

# Route the newly structured graph pages through the dedicated graph builder and preview updater.
old_special = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "did_trends", "twoway")'
new_special = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "graph_matrix", "twoway_contour", "tsline", "xtline", "sts_graph", "roctab", "roccomp", "did_trends", "twoway")'
j = exact_count_replace(j, old_special, new_special, 2, "special graph route/update lists")

# Prevent partial preview churn while a specialized page is being rebuilt.
j = once(
    j,
    '         this.currentCommand = var1;\n         this.commandDock.setVisible(true);',
    '         this.currentCommand = var1;\n         this.rebuilding = true;\n         this.commandDock.setVisible(true);',
    "special graph rebuilding start",
)
j = once(
    j,
    '         this.options.setText("");\n         this.expression.setText("twoway".equals(var1) ? "(scatter y x) (lfit y x)" : "");\n',
    '         this.options.setText("");\n         this.specialGraphRiskTable.setSelected(false);\n         this.specialGraphRiskTable.setOpaque(false);\n         this.specialGraphRiskTable.setForeground(TEXT);\n         this.configureSpecialGraphModel(var1);\n         this.expression.setText("twoway".equals(var1) ? "(scatter y x) (lfit y x)" : "");\n',
    "special graph reset/configure",
)
j = once(
    j,
    '         this.formScroll.getVerticalScrollBar().setValue(0);\n         this.updateSpecialGraphPreview();\n',
    '         this.formScroll.getVerticalScrollBar().setValue(0);\n         this.rebuilding = false;\n         this.updateSpecialGraphPreview();\n',
    "special graph rebuilding end",
)

# Dedicated titles, task semantics, and examples.
title_anchor = '''         } else if ("graph_box".equals(var1)) {
            this.commandTitle.setText("graph box · 分布与异常值箱线图");
'''
title_blocks = '''         } else if ("graph_matrix".equals(var1)) {
            this.commandTitle.setText("graph matrix · 散点图矩阵");
            this.exampleLabel.setText("<html><b>最简单例子：</b> graph matrix mpg weight length</html>");
            this.insightArea.setText("主要意图：一次查看多个连续变量的两两关系、离群点和相关形态。\\n\\n至少选择 2 个变量；变量过多会让矩阵迅速变密，建议先放核心连续变量。\\n\\nhalf、diagonal()、marker 与标题等继续放在更多图形设置中。");
            this.syntaxArea.setText("graph matrix varlist [if] [, options]");
            coreTitle = "矩阵变量";
            coreSubtitle = "选择至少两个要两两比较的数值变量；先保留核心变量，避免矩阵过密。";
         } else if ("twoway_contour".equals(var1)) {
            this.commandTitle.setText("twoway contour · 等高线图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> twoway contour depth northing easting</html>");
            this.insightArea.setText("主要意图：用颜色或等高线展示 Z 随 Y、X 两个坐标共同变化的表面。\\n\\nStata 原生顺序固定为 Z → Y → X；三个角色必须使用不同变量。\\n\\n插值方法、ccuts()/levels()、颜色和标题等继续放在更多图形设置中。");
            this.syntaxArea.setText("twoway contour zvar yvar xvar [if] [, options]");
            coreTitle = "Z / Y / X 坐标";
            coreSubtitle = "按 Stata 原生顺序分别选择 Z 值、纵向坐标 Y 和横向坐标 X。";
         } else if (Arrays.asList("tsline", "xtline").contains(var1)) {
            boolean panelLine = "xtline".equals(var1);
            this.commandTitle.setText(panelLine ? "xtline · 面板数据折线图" : "tsline · 时间序列折线图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> " + (panelLine ? "xtline y, overlay" : "tsline y") + "</html>");
            this.insightArea.setText(panelLine
               ? "主要意图：按当前 xtset 的面板与时间结构绘制一个或多个变量的面板轨迹。\\n\\n本页不伪造额外时间参数；panel/time 结构沿用当前 Stata xtset。可选择默认分面显示或 overlay 叠加所有面板。\\n\\n正式绘图前如果尚未 xtset，请先到数据结构页面完成声明。"
               : "主要意图：按当前 tsset 的时间结构绘制一个或多个变量的时间路径。\\n\\n时间轴沿用当前 Stata tsset，本页只选择真正要画的序列。\\n\\n正式绘图前如果尚未 tsset，请先到数据结构页面完成声明。");
            this.syntaxArea.setText(panelLine ? "xtline varlist [if] [, overlay options]" : "tsline varlist [if] [, options]");
            coreTitle = panelLine ? "面板序列" : "时间序列";
            coreSubtitle = panelLine ? "选择至少一个变量；显示方式可在分面与 overlay 之间切换。" : "选择至少一个要沿当前时间轴绘制的变量。";
         } else if ("sts_graph".equals(var1)) {
            this.commandTitle.setText("sts graph · Kaplan–Meier 与生存函数图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> sts graph, by(group) risktable</html>");
            this.insightArea.setText("主要意图：在已经 stset 的数据上绘制 Kaplan–Meier 生存曲线、失败函数、累计风险或平滑风险函数。\\n\\n分析时间与失败事件沿用当前 stset；这里只选择可选分组、曲线类型和是否显示风险人数表。\\n\\n调整协变量、置信区间、tmin()/tmax() 和图形样式继续放在更多图形设置中。");
            this.syntaxArea.setText("sts graph [if] [, by(group) failure|cumhaz|hazard risktable options]");
            coreTitle = "生存曲线设置";
            coreSubtitle = "沿用当前 stset；选择可选分组、曲线类型，并按需显示风险人数表。";
         } else if (Arrays.asList("roctab", "roccomp").contains(var1)) {
            boolean compareRoc = "roccomp".equals(var1);
            this.commandTitle.setText(compareRoc ? "roccomp · 比较多条 ROC 曲线" : "roctab · 非参数 ROC 曲线");
            this.exampleLabel.setText("<html><b>最简单例子：</b> " + (compareRoc ? "roccomp status mod1 mod2, graph" : "roctab disease rating, graph") + "</html>");
            this.insightArea.setText(compareRoc
               ? "主要意图：在同一真实二元结局下比较两个或多个预测评分/分类器的 ROC 面积，并直接绘图。\\n\\n真实结局必填且应为二元变量；预测评分至少选择 2 个。独立样本 by()、summary 和图形样式继续放在更多设置中。"
               : "主要意图：用真实二元结局和一个连续/有序预测评分估计非参数 ROC 曲线与 AUC。\\n\\n真实结局必填，预测评分只选 1 个；本图形入口默认加入 graph。detail、binomial、Lorenz 和图形样式继续放在更多设置中。");
            this.syntaxArea.setText(compareRoc ? "roccomp refvar classvars [if] [, graph options]" : "roctab refvar classvar [if] [, graph options]");
            coreTitle = "真实结局与预测评分";
            coreSubtitle = compareRoc ? "选择一个真实二元结局，再选择至少两个要比较的评分。" : "选择一个真实二元结局和且仅一个预测评分。";
''' + title_anchor
j = once(j, title_anchor, title_blocks, "special graph title branches")

# Dedicated field layouts.
body_anchor = '''         } else if ("graph_box".equals(var1)) {
            JPanel boxVars = new JPanel(new GridLayout(1, 2, 12, 0));
'''
body_blocks = '''         } else if ("graph_matrix".equals(var1)) {
            this.addGenericBodyField(coreBody, "矩阵变量（至少 2 个，可多选）", this.listPane(this.variables));
            JLabel matrixHint = new JLabel("建议先选 2–6 个核心连续变量；变量太多时单元格会变小，解释也会变困难。");
            matrixHint.setForeground(MUTED);
            matrixHint.setFont(matrixHint.getFont().deriveFont(9.8F));
            matrixHint.setAlignmentX(0.0F);
            coreBody.add(matrixHint);
         } else if ("twoway_contour".equals(var1)) {
            JPanel contourVars = new JPanel(new GridLayout(1, 3, 10, 0));
            contourVars.setOpaque(false);
            contourVars.add(this.fieldBlock("Z 值 / 等高线变量", this.depvar));
            contourVars.add(this.fieldBlock("Y 坐标", this.panel));
            contourVars.add(this.fieldBlock("X 坐标", this.time));
            this.addGenericBodyField(coreBody, "三个变量角色", contourVars);
            JLabel contourHint = new JLabel("Stata 顺序是 contour z y x；这里分别固定三个角色，避免把 Y/X 顺序写反。");
            contourHint.setForeground(MUTED);
            contourHint.setFont(contourHint.getFont().deriveFont(9.8F));
            contourHint.setAlignmentX(0.0F);
            coreBody.add(contourHint);
         } else if (Arrays.asList("tsline", "xtline").contains(var1)) {
            this.addGenericBodyField(coreBody, "要绘制的变量（可多选）", this.listPane(this.variables));
            if ("xtline".equals(var1)) {
               this.addGenericBodyField(coreBody, "面板显示方式", this.model);
            }
            JLabel lineHint = new JLabel("<html>时间/面板结构沿用当前 <b>" + ("xtline".equals(var1) ? "xtset" : "tsset") + "</b>；本页不会偷偷改写数据声明。</html>");
            lineHint.setForeground(MUTED);
            lineHint.setFont(lineHint.getFont().deriveFont(9.8F));
            lineHint.setAlignmentX(0.0F);
            coreBody.add(lineHint);
         } else if ("sts_graph".equals(var1)) {
            JPanel survivalVars = new JPanel(new GridLayout(1, 2, 12, 0));
            survivalVars.setOpaque(false);
            survivalVars.add(this.fieldBlock("分组变量 by()（可选）", this.panel));
            survivalVars.add(this.fieldBlock("曲线类型", this.model));
            this.addGenericBodyField(coreBody, "曲线与分组", survivalVars);
            this.addGenericBodyField(coreBody, "常用显示", this.specialGraphRiskTable);
            JLabel survivalHint = new JLabel("当前分析时间和失败事件来自 stset；如果尚未 stset，请先完成生存数据声明。");
            survivalHint.setForeground(MUTED);
            survivalHint.setFont(survivalHint.getFont().deriveFont(9.8F));
            survivalHint.setAlignmentX(0.0F);
            coreBody.add(survivalHint);
         } else if (Arrays.asList("roctab", "roccomp").contains(var1)) {
            JPanel rocVars = new JPanel(new GridLayout(1, 2, 12, 0));
            rocVars.setOpaque(false);
            rocVars.add(this.fieldBlock("真实二元结局", this.depvar));
            rocVars.add(this.fieldBlock("预测评分 / 分类器", this.listPane(this.variables)));
            this.addGenericBodyField(coreBody, "ROC 变量", rocVars);
            JLabel rocHint = new JLabel("本图形入口会自动加入 graph；复杂 by()、summary、detail、权重或样式可在最终命令中继续补充。");
            rocHint.setForeground(MUTED);
            rocHint.setFont(rocHint.getFont().deriveFont(9.8F));
            rocHint.setAlignmentX(0.0F);
            coreBody.add(rocHint);
''' + body_anchor
j = once(j, body_anchor, body_blocks, "special graph field branches")

# Model choices used by xtline and sts graph only.
helper_anchor = '''      private JPanel buildSpecialGraphMoreSettings(boolean includeIf, String optionLabel) {
'''
helper = '''      private void configureSpecialGraphModel(String command) {
         this.model.removeAllItems();
         if ("xtline".equals(command)) {
            this.model.addItem("按面板分图（默认）");
            this.model.addItem("叠加所有面板（overlay）");
            this.model.setSelectedIndex(0);
         } else if ("sts_graph".equals(command)) {
            this.model.addItem("生存函数（默认）");
            this.model.addItem("失败函数（failure）");
            this.model.addItem("累计风险（cumhaz）");
            this.model.addItem("风险函数（hazard）");
            this.model.setSelectedIndex(0);
         } else {
            this.model.addItem("");
         }
      }

'''
j = once(j, helper_anchor, helper + helper_anchor, "special graph model helper")

# Build real native commands for the new structured pages.
preview_anchor = '''         } else if ("graph_box".equals(this.currentCommand)) {
            String var6 = selected(this.depvar);
'''
preview_blocks = '''         } else if ("graph_matrix".equals(this.currentCommand)) {
            List<String> matrixVars = this.variables.getSelectedValuesList();
            var1 = "graph matrix" + (matrixVars.isEmpty() ? "" : " " + String.join(" ", matrixVars));
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if ("twoway_contour".equals(this.currentCommand)) {
            var1 = "twoway contour " + selected(this.depvar) + " " + selected(this.panel) + " " + selected(this.time);
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if (Arrays.asList("tsline", "xtline").contains(this.currentCommand)) {
            List<String> lineVars = this.variables.getSelectedValuesList();
            var1 = this.currentCommand + (lineVars.isEmpty() ? "" : " " + String.join(" ", lineVars));
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            ArrayList<String> lineOpts = new ArrayList<>();
            if ("xtline".equals(this.currentCommand) && selected(this.model).startsWith("叠加")) lineOpts.add("overlay");
            if (!this.options.getText().trim().isBlank()) lineOpts.add(this.options.getText().trim());
            if (!lineOpts.isEmpty()) var1 += ", " + String.join(" ", lineOpts);
         } else if ("sts_graph".equals(this.currentCommand)) {
            var1 = "sts graph";
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            ArrayList<String> survivalOpts = new ArrayList<>();
            if (!selected(this.panel).isBlank()) survivalOpts.add("by(" + selected(this.panel) + ")");
            String curve = selected(this.model);
            if (curve.startsWith("失败")) survivalOpts.add("failure");
            else if (curve.startsWith("累计风险")) survivalOpts.add("cumhaz");
            else if (curve.startsWith("风险函数")) survivalOpts.add("hazard");
            if (this.specialGraphRiskTable.isSelected()) survivalOpts.add("risktable");
            if (!this.options.getText().trim().isBlank()) survivalOpts.add(this.options.getText().trim());
            if (!survivalOpts.isEmpty()) var1 += ", " + String.join(" ", survivalOpts);
         } else if (Arrays.asList("roctab", "roccomp").contains(this.currentCommand)) {
            List<String> scores = this.variables.getSelectedValuesList();
            var1 = this.currentCommand + " " + selected(this.depvar) + (scores.isEmpty() ? "" : " " + String.join(" ", scores));
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            ArrayList<String> rocOpts = new ArrayList<>();
            rocOpts.add("graph");
            if (!this.options.getText().trim().isBlank()) rocOpts.add(this.options.getText().trim());
            var1 += ", " + String.join(" ", rocOpts);
''' + preview_anchor
j = once(j, preview_anchor, preview_blocks, "special graph native preview branches")

# Keep variable-inspector role labels faithful to the current graph task.
role_anchor = '         if (variable.equals(selected(this.depvar))) return "因变量 Y";\n'
role_block = '''         if (Arrays.asList("histogram", "kdensity").contains(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "分布变量";
         }
         if (Arrays.asList("scatter", "lfit").contains(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "纵轴 Y";
            if (this.variables.getSelectedValuesList().contains(variable)) return "横轴 X";
         }
         if (Arrays.asList("graph_bar", "graph_dot").contains(this.currentCommand)) {
            if (this.variables.getSelectedValuesList().contains(variable)) return "数值变量";
            if (variable.equals(selected(this.panel))) return "分组 over()";
         }
         if ("graph_pie".equals(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "扇区数值";
            if (variable.equals(selected(this.panel))) return "分类 over()";
         }
         if ("graph_box".equals(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "箱线变量";
            if (variable.equals(selected(this.panel))) return "分组变量";
         }
         if ("graph_matrix".equals(this.currentCommand) && this.variables.getSelectedValuesList().contains(variable)) return "矩阵变量";
         if ("twoway_contour".equals(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "Z 值";
            if (variable.equals(selected(this.panel))) return "Y 坐标";
            if (variable.equals(selected(this.time))) return "X 坐标";
         }
         if (Arrays.asList("tsline", "xtline").contains(this.currentCommand) && this.variables.getSelectedValuesList().contains(variable)) return "绘图序列";
         if ("sts_graph".equals(this.currentCommand) && variable.equals(selected(this.panel))) return "生存曲线分组";
         if (Arrays.asList("roctab", "roccomp").contains(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "真实二元结局";
            if (this.variables.getSelectedValuesList().contains(variable)) return "预测评分 / 分类器";
         }
         if ("did_trends".equals(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "结果变量 Y";
            if (variable.equals(selected(this.panel))) return "处理组";
            if (variable.equals(selected(this.time))) return "时间变量";
         }
'''
j = once(j, role_anchor, role_block + role_anchor, "special graph inspector roles")

# Add a single listener for the new checkbox.
wire_anchor = '         this.missingChartType.addActionListener(var1x -> this.missingChart.setChartType(selected(this.missingChartType)));\n'
j = once(
    j,
    wire_anchor,
    wire_anchor + '         this.specialGraphRiskTable.addActionListener(var1x -> this.schedulePreview());\n',
    "risk-table preview listener",
)

# Validate only the genuine minimum requirements for these pages.
validation_anchor = '''         if (Arrays.asList("scatter", "lfit").contains(command)) {
'''
validation = '''         if ("graph_matrix".equals(command) && this.variables.getSelectedValuesList().size() < 2) {
            JOptionPane.showMessageDialog(this, "graph matrix 至少选择 2 个变量。", "图形设置尚未完整", 1);
            return false;
         }
         if ("twoway_contour".equals(command)) {
            String z = selected(this.depvar), y = selected(this.panel), x = selected(this.time);
            if (z.isBlank() || y.isBlank() || x.isBlank()) {
               JOptionPane.showMessageDialog(this, "等高线图需要分别选择 Z、Y、X 三个变量。", "图形设置尚未完整", 1);
               return false;
            }
            if (new LinkedHashSet<>(Arrays.asList(z, y, x)).size() < 3) {
               JOptionPane.showMessageDialog(this, "Z、Y、X 必须使用三个不同变量。", "图形变量角色重复", 2);
               return false;
            }
         }
         if (Arrays.asList("tsline", "xtline").contains(command) && this.variables.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "请选择至少 1 个要绘制的序列变量。", "图形设置尚未完整", 1);
            return false;
         }
         if ("roctab".equals(command)) {
            if (selected(this.depvar).isBlank() || this.variables.getSelectedValuesList().size() != 1) {
               JOptionPane.showMessageDialog(this, "roctab 需要 1 个真实二元结局和且仅 1 个预测评分。", "ROC 设置尚未完整", 1);
               return false;
            }
            if (this.variables.getSelectedValuesList().contains(selected(this.depvar))) {
               JOptionPane.showMessageDialog(this, "真实结局和预测评分不能是同一个变量。", "ROC 变量角色重复", 2);
               return false;
            }
         }
         if ("roccomp".equals(command)) {
            if (selected(this.depvar).isBlank() || this.variables.getSelectedValuesList().size() < 2) {
               JOptionPane.showMessageDialog(this, "roccomp 需要 1 个真实二元结局和至少 2 个预测评分。", "ROC 设置尚未完整", 1);
               return false;
            }
            if (this.variables.getSelectedValuesList().contains(selected(this.depvar))) {
               JOptionPane.showMessageDialog(this, "真实结局不能同时作为待比较的预测评分。", "ROC 变量角色重复", 2);
               return false;
            }
         }
'''
j = once(j, validation_anchor, validation + validation_anchor, "structured graph validation")

jp.write_text(j, encoding="utf-8", newline="\n")

# Static contracts for the new page architecture.
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
old_contract = '''for graph_cmd in ("graph_bar", "graph_dot", "graph_pie"):
    special_open = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "did_trends", "twoway").contains(var1)'
    if special_open not in java:
        fail("common graph commands are not routed to the special graph page")
'''
new_contract = '''special_open = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "graph_matrix", "twoway_contour", "tsline", "xtline", "sts_graph", "roctab", "roccomp", "did_trends", "twoway").contains(var1)'
if special_open not in java:
    fail("structured Graphics commands are not routed to the special graph page")
for graph_cmd in ("graph_matrix", "twoway_contour", "tsline", "xtline", "sts_graph", "roctab", "roccomp"):
    if graph_cmd not in special_open:
        fail(f"structured Graphics route contract missing: {graph_cmd}")
'''
v = once(v, old_contract, new_contract, "structured Graphics route contract")

contract_anchor = '''if '请选择饼图的分类变量 over()' not in java:
    fail("pie special graph validation missing")
'''
extra_contracts = '''for needle in (
    'graph matrix · 散点图矩阵',
    'twoway contour · 等高线图',
    'xtline · 面板数据折线图',
    'sts graph · Kaplan–Meier 与生存函数图',
    'roctab · 非参数 ROC 曲线',
    'roccomp · 比较多条 ROC 曲线',
    '显示风险人数表 risktable',
    'var1 = "graph matrix"',
    'var1 = "twoway contour "',
    'survivalOpts.add("risktable")',
    'rocOpts.add("graph")',
    'graph matrix 至少选择 2 个变量',
    '等高线图需要分别选择 Z、Y、X 三个变量',
    'roccomp 需要 1 个真实二元结局和至少 2 个预测评分',
):
    if needle not in java:
        fail(f"structured Graphics page contract missing: {needle}")
if 'public static final String VERSION = "1.5.12";' not in java:
    fail("HxWorkbench version marker was not advanced for the structured Graphics page batch")
'''
v = once(v, contract_anchor, contract_anchor + extra_contracts, "structured Graphics detailed contracts")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_GRAPH_CORE_PAGES_PATCH_OK")
