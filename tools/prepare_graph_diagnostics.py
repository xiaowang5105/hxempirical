from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
java_path = root / "src/main/java/com/hexie/stata/HxWorkbench.java"
static_path = root / "tools/verify_static_contracts.py"
java = java_path.read_text(encoding="utf-8")
static = static_path.read_text(encoding="utf-8")


def replace_exact(text, old, new, expected=1, label="anchor"):
    count = text.count(old)
    if count != expected:
        print(f"HX_GRAPH_DIAG_PATCH_FAIL {label}: expected {expected}, found {count}", file=sys.stderr)
        raise SystemExit(1)
    return text.replace(old, new)

# Route the remaining common 2D/smoothing/regression-diagnostic graphs through the structured Graphics workspace.
old_route = '"histogram", "kdensity", "scatter", "lfit", "graph_bar"'
new_route = '"histogram", "kdensity", "scatter", "line", "connected", "lfit", "qfit", "lowess", "lpoly", "rvfplot", "rvpplot", "avplot", "avplots", "lvr2plot", "cprplot", "acprplot", "graph_bar"'
java = replace_exact(java, old_route, new_route, expected=2, label="Java special route lists")

# Complete the Graphics method preview so the card matches the actual seven regression-diagnostic commands.
java = replace_exact(
    java,
    'case "回归诊断图": return "rvfplot · rvpplot · avplot · lvr2plot · cprplot";',
    'case "回归诊断图": return "rvfplot · rvpplot · avplot · avplots · lvr2plot · cprplot · acprplot";',
    label="diagnostic method preview",
)

# Add concise command guides for the newly structured pages.
guide_anchor = '         addGuide(var0, "twoway", "二维叠加图", "自由组合散点、线、置信区间等多个图层。", "需要制作结构较复杂的论文二维图形。", "twoway (scatter y x) (lfit y x)", "表达能力强，图层语法也更灵活。");\n'
guide_block = '''         addGuide(var0, "line", "折线图", "按一个横轴连接一个或多个 Y 系列。", "时间、排序指标或其他连续横轴上的趋势比较。", "line y1 y2 x", "Y 可多选；X 只指定一次，连接顺序由横轴取值决定。");
         addGuide(var0, "connected", "带点折线图", "同时显示观测点并按横轴连接。", "既要看到趋势线，也要保留每个观测点的位置。", "connected y x", "与 line 一样需要明确 Y 和 X；点与连接线样式放在图形 options 中。");
         addGuide(var0, "qfit", "二次拟合图", "绘制 Y 对 X 的 quadratic fit。", "散点关系存在明显弯曲、需要快速查看二次趋势。", "twoway qfit y x", "这是二次函数拟合的图形展示，正式函数形式仍应由研究设定决定。");
         addGuide(var0, "lowess", "LOWESS 平滑图", "用局部加权平滑展示 Y 与 X 的非参数趋势。", "探索非线性关系或检查线性设定是否过强。", "lowess y x", "平滑程度受 bandwidth 等设置影响。");
         addGuide(var0, "lpoly", "局部多项式平滑图", "用局部多项式回归展示 Y 与 X 的平滑关系。", "需要比简单局部均值更灵活的非参数趋势。", "lpoly y x", "degree、kernel、bandwidth 等保留为 Stata 原生 options。");
         addGuide(var0, "rvfplot", "残差 vs 拟合值", "基于当前兼容回归结果绘制 residual-versus-fitted plot。", "检查非线性、异方差和系统性残差模式。", "rvfplot, yline(0)", "典型用法在 regress 后；无需重新选择原始 Y/X。");
         addGuide(var0, "rvpplot", "残差 vs predictor", "把当前回归残差与指定 predictor 作图。", "检查残差是否随某个解释变量呈系统模式。", "rvpplot mpg", "页面只选择一个诊断变量；回归结果来自当前 estimation result。");
         addGuide(var0, "avplot", "Added-variable plot", "针对一个 predictor 绘制 added-variable / partial-regression plot。", "查看控制其他协变量后某个变量与结果的部分关系。", "avplot mpg", "典型用法在 regress 后；指定的是诊断变量，不是新的因变量。");
         addGuide(var0, "avplots", "全部 Added-variable plots", "为当前模型中的变量生成一组 added-variable plots。", "一次检查完整线性回归中的部分关系与潜在影响点。", "avplots", "直接复用当前兼容回归结果，不需要选择原始变量。");
         addGuide(var0, "lvr2plot", "Leverage vs residual-squared", "绘制 leverage 对 normalized residual squared。", "联合识别高杠杆和大残差观测。", "lvr2plot", "直接复用当前兼容回归结果。");
         addGuide(var0, "cprplot", "Component-plus-residual plot", "针对一个 predictor 绘制 component-plus-residual plot。", "检查该 predictor 的函数形式和部分残差模式。", "cprplot mpg", "典型用法在 regress 后；指定一个 predictor。");
         addGuide(var0, "acprplot", "Augmented component-plus-residual plot", "针对一个 predictor 绘制 augmented component-plus-residual plot。", "进一步检查 predictor 的函数形式与非线性。", "acprplot mpg", "典型用法在 regress 后；指定一个 predictor。");
'''
java = replace_exact(java, guide_anchor, guide_anchor + guide_block, label="command guide insertion")

# Add dedicated page semantics after the existing scatter/lfit block.
page_boundary = '            coreSubtitle = "先指定纵轴 Y 和唯一的横轴 X；右侧同步显示关系预览。";\n         } else if (Arrays.asList("graph_bar", "graph_dot").contains(var1)) {'
page_insert = '''            coreSubtitle = "先指定纵轴 Y 和唯一的横轴 X；右侧同步显示关系预览。";
         } else if (Arrays.asList("line", "connected").contains(var1)) {
            boolean connected = "connected".equals(var1);
            this.commandTitle.setText(connected ? "connected · 带点折线图" : "line · 折线图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> " + (connected ? "connected y x" : "line y1 y2 x") + "</html>");
            this.insightArea.setText("主要意图：沿一个明确的横轴 X 连接一个或多个 Y 系列。\\n\\nY 可以选择多个系列，X 只选择一次；connected 同时保留观测点，line 主要显示连接线。\\n\\n排序、connect()/sort、线型、marker、标题和尺寸继续使用 Stata 原生图形 options。");
            this.syntaxArea.setText("twoway " + var1 + " yvarlist xvar [if] [in] [, options]");
            coreTitle = "Y 系列与横轴 X";
            coreSubtitle = "选择至少一个纵轴 Y 系列，再指定唯一横轴 X；无需把 X 混进 Y 列表。";
         } else if ("qfit".equals(var1)) {
            this.commandTitle.setText("qfit · 二次拟合图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> twoway qfit mpg weight</html>");
            this.insightArea.setText("主要意图：用二次函数快速查看 Y 随 X 的弯曲趋势。\\n\\nY 与 X 分别选择，页面固定保持 qfit y x 的原生顺序。\\n\\n置信区间需要 qfitci；本页只生成 qfit，线型、范围和标题继续使用 Stata 原生 options。");
            this.syntaxArea.setText("twoway qfit yvar xvar [if] [in] [, options]");
            coreTitle = "Y / X 坐标";
            coreSubtitle = "分别指定纵轴 Y 和横轴 X；二次项由 qfit 自动拟合。";
         } else if (Arrays.asList("lowess", "lpoly").contains(var1)) {
            boolean localPoly = "lpoly".equals(var1);
            this.commandTitle.setText(localPoly ? "lpoly · 局部多项式平滑图" : "lowess · LOWESS 平滑图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> " + var1 + " y x</html>");
            this.insightArea.setText(localPoly
               ? "主要意图：用局部多项式回归平滑 Y 与 X 的关系。\\n\\n分别选择 Y 和 X；degree()、kernel()、bandwidth() 以及置信区间等继续使用 lpoly 原生 options。\\n\\n平滑结果用于探索函数形式，带宽和阶数会影响曲线形状。"
               : "主要意图：用局部加权回归平滑 Y 与 X 的关系。\\n\\n分别选择 Y 和 X；bandwidth()、mean、noweight、line options 等继续使用 lowess 原生 options。\\n\\n平滑结果用于探索非线性，带宽会影响曲线形状。");
            this.syntaxArea.setText(var1 + " yvar xvar [if] [in] [, options]");
            coreTitle = "Y / X 与平滑关系";
            coreSubtitle = "分别指定纵轴 Y 和横轴 X；平滑参数按需要在图形设置中调整。";
         } else if (Arrays.asList("rvfplot", "rvpplot", "avplot", "avplots", "lvr2plot", "cprplot", "acprplot").contains(var1)) {
            boolean needsPredictor = Arrays.asList("rvpplot", "avplot", "cprplot", "acprplot").contains(var1);
            String diagnosticName;
            if ("rvfplot".equals(var1)) diagnosticName = "残差 vs 拟合值";
            else if ("rvpplot".equals(var1)) diagnosticName = "残差 vs predictor";
            else if ("avplot".equals(var1)) diagnosticName = "Added-variable plot";
            else if ("avplots".equals(var1)) diagnosticName = "全部 Added-variable plots";
            else if ("lvr2plot".equals(var1)) diagnosticName = "Leverage vs residual-squared";
            else if ("cprplot".equals(var1)) diagnosticName = "Component-plus-residual plot";
            else diagnosticName = "Augmented component-plus-residual plot";
            this.commandTitle.setText(var1 + " · " + diagnosticName);
            String diagnosticExample = needsPredictor ? var1 + " mpg" : ("rvfplot".equals(var1) ? "rvfplot, yline(0)" : var1);
            this.exampleLabel.setText("<html><b>最简单例子：</b> " + diagnosticExample + "</html>");
            this.insightArea.setText(needsPredictor
               ? "这是回归后诊断图。先运行兼容的回归，再选择一个要检查的 predictor / 诊断变量。\\n\\n本页不会要求重新选择原回归的因变量；残差、拟合值和其他诊断量来自当前 estimation result。\\n\\n典型用法是在 regress 后；当前模型是否兼容由 Stata 在执行时判断。"
               : "这是回归后诊断图。页面直接沿用当前兼容的 estimation result，不需要重新选择原始数据中的 Y 或 X。\\n\\n诊断量由上一回归结果生成；本页只保留样本范围与图形 options。\\n\\n典型用法是在 regress 后；当前模型是否兼容由 Stata 在执行时判断。");
            this.syntaxArea.setText(needsPredictor ? var1 + " varname [if] [in] [, options]" : var1 + " [if] [in] [, options]");
            coreTitle = needsPredictor ? "诊断变量 / predictor" : "沿用上一回归结果";
            coreSubtitle = needsPredictor ? "只选择当前诊断图要求的 predictor；原回归 Y/X 不在这里重复选择。" : "无需选择原始变量；确认上一条兼容回归已成功运行。";
         } else if (Arrays.asList("graph_bar", "graph_dot").contains(var1)) {'''
java = replace_exact(java, page_boundary, page_insert, label="special graph page insertion")

# Give drag-and-drop targets command-specific meanings instead of generic graph roles.
drop_boundary = '''         } else if (Arrays.asList("rchart", "xchart", "shewhart").contains(var1)) {
            this.enableVariableDrop(this.variables, "样本内重复测量变量");
         } else {
            this.enableVariableDrop(this.depvar, "Y / 分布变量");
            this.enableVariableDrop(this.variables, "横轴 X");
            this.enableVariableDrop(this.panel, "分组 / 处理组变量");
            this.enableVariableDrop(this.time, "时间变量");
         }
'''
drop_new = '''         } else if (Arrays.asList("rchart", "xchart", "shewhart").contains(var1)) {
            this.enableVariableDrop(this.variables, "样本内重复测量变量");
         } else if (Arrays.asList("line", "connected").contains(var1)) {
            this.enableVariableDrop(this.variables, "纵轴 Y 系列");
            this.enableVariableDrop(this.panel, "横轴 X");
         } else if (Arrays.asList("qfit", "lowess", "lpoly").contains(var1)) {
            this.enableVariableDrop(this.depvar, "纵轴 Y");
            this.enableVariableDrop(this.panel, "横轴 X");
         } else if (Arrays.asList("rvpplot", "avplot", "cprplot", "acprplot").contains(var1)) {
            this.enableVariableDrop(this.depvar, "诊断变量 / predictor");
         } else {
            this.enableVariableDrop(this.depvar, "Y / 分布变量");
            this.enableVariableDrop(this.variables, "横轴 X");
            this.enableVariableDrop(this.panel, "分组 / 处理组变量");
            this.enableVariableDrop(this.time, "时间变量");
         }
'''
java = replace_exact(java, drop_boundary, drop_new, label="drag-drop roles")

# Add the visible fields for these dedicated pages.
field_boundary = '''            this.addGenericBodyField(coreBody, "Y / X", xy);
         } else if (Arrays.asList("graph_bar", "graph_dot").contains(var1)) {'''
field_insert = '''            this.addGenericBodyField(coreBody, "Y / X", xy);
         } else if (Arrays.asList("line", "connected").contains(var1)) {
            JPanel lineVars = new JPanel(new GridLayout(1, 2, 12, 0));
            lineVars.setOpaque(false);
            lineVars.add(this.fieldBlock("纵轴 Y 系列（至少 1 个，可多选）", this.listPane(this.variables)));
            lineVars.add(this.fieldBlock("横轴 X（选择一个）", this.panel));
            this.addGenericBodyField(coreBody, "Y 系列 / X", lineVars);
            JLabel lineSeriesHint = new JLabel("多个 Y 会共用同一个 X；工作台会阻止把横轴变量同时放入 Y 系列。");
            lineSeriesHint.setForeground(MUTED);
            lineSeriesHint.setFont(lineSeriesHint.getFont().deriveFont(9.8F));
            lineSeriesHint.setAlignmentX(0.0F);
            coreBody.add(lineSeriesHint);
         } else if (Arrays.asList("qfit", "lowess", "lpoly").contains(var1)) {
            JPanel smoothVars = new JPanel(new GridLayout(1, 2, 12, 0));
            smoothVars.setOpaque(false);
            smoothVars.add(this.fieldBlock("纵轴 Y", this.depvar));
            smoothVars.add(this.fieldBlock("横轴 X", this.panel));
            this.addGenericBodyField(coreBody, "Y / X", smoothVars);
         } else if (Arrays.asList("rvpplot", "avplot", "cprplot", "acprplot").contains(var1)) {
            this.addGenericBodyField(coreBody, "诊断变量 / predictor", this.depvar);
            JLabel diagnosticVarHint = new JLabel("这里只选择诊断针对的 predictor；原回归的因变量与其他协变量直接沿用当前 estimation result。");
            diagnosticVarHint.setForeground(MUTED);
            diagnosticVarHint.setFont(diagnosticVarHint.getFont().deriveFont(9.8F));
            diagnosticVarHint.setAlignmentX(0.0F);
            coreBody.add(diagnosticVarHint);
         } else if (Arrays.asList("rvfplot", "avplots", "lvr2plot").contains(var1)) {
            JLabel diagnosticPostHint = new JLabel("<html>直接使用最近一次兼容回归结果。页面不显示原始变量选择框；需要改变模型时先重新运行回归。</html>");
            diagnosticPostHint.setForeground(MUTED);
            diagnosticPostHint.setFont(diagnosticPostHint.getFont().deriveFont(10.0F));
            diagnosticPostHint.setAlignmentX(0.0F);
            coreBody.add(diagnosticPostHint);
         } else if (Arrays.asList("graph_bar", "graph_dot").contains(var1)) {'''
java = replace_exact(java, field_boundary, field_insert, label="special graph fields")

# These commands support explicit observation ranges; expose in alongside if.
java = replace_exact(
    java,
    'boolean includeIn = Arrays.asList("rchart", "xchart", "shewhart").contains(this.currentCommand);',
    'boolean includeIn = Arrays.asList("rchart", "xchart", "shewhart", "line", "connected", "qfit", "lowess", "lpoly", "rvfplot", "rvpplot", "avplot", "avplots", "lvr2plot", "cprplot", "acprplot").contains(this.currentCommand);',
    label="special graph in support",
)

# Build real Stata commands for the new structured pages.
preview_boundary = '''            if (!this.options.getText().trim().isBlank()) {
               var1 = var1 + ", " + this.options.getText().trim();
            }
         } else if (Arrays.asList("graph_bar", "graph_dot").contains(this.currentCommand)) {'''
preview_insert = '''            if (!this.options.getText().trim().isBlank()) {
               var1 = var1 + ", " + this.options.getText().trim();
            }
         } else if (Arrays.asList("line", "connected").contains(this.currentCommand)) {
            List<String> ySeries = this.variables.getSelectedValuesList();
            var1 = "twoway " + this.currentCommand + (ySeries.isEmpty() ? "" : " " + String.join(" ", ySeries)) + " " + selected(this.panel);
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            if (!this.inCondition.getText().trim().isBlank()) var1 += " in " + this.inCondition.getText().trim();
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if ("qfit".equals(this.currentCommand)) {
            var1 = "twoway qfit " + selected(this.depvar) + " " + selected(this.panel);
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            if (!this.inCondition.getText().trim().isBlank()) var1 += " in " + this.inCondition.getText().trim();
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if (Arrays.asList("lowess", "lpoly").contains(this.currentCommand)) {
            var1 = this.currentCommand + " " + selected(this.depvar) + " " + selected(this.panel);
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            if (!this.inCondition.getText().trim().isBlank()) var1 += " in " + this.inCondition.getText().trim();
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if (Arrays.asList("rvpplot", "avplot", "cprplot", "acprplot").contains(this.currentCommand)) {
            var1 = this.currentCommand + " " + selected(this.depvar);
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            if (!this.inCondition.getText().trim().isBlank()) var1 += " in " + this.inCondition.getText().trim();
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if (Arrays.asList("rvfplot", "avplots", "lvr2plot").contains(this.currentCommand)) {
            var1 = this.currentCommand;
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            if (!this.inCondition.getText().trim().isBlank()) var1 += " in " + this.inCondition.getText().trim();
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if (Arrays.asList("graph_bar", "graph_dot").contains(this.currentCommand)) {'''
java = replace_exact(java, preview_boundary, preview_insert, label="special graph preview builders")

# Give the inspector accurate roles for newly structured graph pages.
inspector_boundary = '''         if (Arrays.asList("scatter", "lfit").contains(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "纵轴 Y";
            if (this.variables.getSelectedValuesList().contains(variable)) return "横轴 X";
         }
         if (Arrays.asList("graph_bar", "graph_dot").contains(this.currentCommand)) {'''
inspector_insert = '''         if (Arrays.asList("scatter", "lfit").contains(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "纵轴 Y";
            if (this.variables.getSelectedValuesList().contains(variable)) return "横轴 X";
         }
         if (Arrays.asList("line", "connected").contains(this.currentCommand)) {
            if (this.variables.getSelectedValuesList().contains(variable)) return "纵轴 Y 系列";
            if (variable.equals(selected(this.panel))) return "横轴 X";
         }
         if (Arrays.asList("qfit", "lowess", "lpoly").contains(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "纵轴 Y";
            if (variable.equals(selected(this.panel))) return "横轴 X";
         }
         if (Arrays.asList("rvpplot", "avplot", "cprplot", "acprplot").contains(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "诊断变量 / predictor";
         }
         if (Arrays.asList("graph_bar", "graph_dot").contains(this.currentCommand)) {'''
java = replace_exact(java, inspector_boundary, inspector_insert, label="inspector roles")

# Validate only the roles these commands actually require.
validation_boundary = '''         if (Arrays.asList("scatter", "lfit").contains(command)) {
            if (selected(this.depvar).isBlank() || this.variables.getSelectedValuesList().size() != 1) {
               JOptionPane.showMessageDialog(this, "请选择纵轴 Y，并且只选择 1 个横轴 X。", "图形设置尚未完整", 1);
               return false;
            }
         }
         if ("twoway".equals(command) && this.expression.getText().trim().isBlank()) {'''
validation_insert = '''         if (Arrays.asList("scatter", "lfit").contains(command)) {
            if (selected(this.depvar).isBlank() || this.variables.getSelectedValuesList().size() != 1) {
               JOptionPane.showMessageDialog(this, "请选择纵轴 Y，并且只选择 1 个横轴 X。", "图形设置尚未完整", 1);
               return false;
            }
         }
         if (Arrays.asList("line", "connected").contains(command)) {
            String x = selected(this.panel);
            List<String> ys = this.variables.getSelectedValuesList();
            if (ys.isEmpty() || x.isBlank()) {
               JOptionPane.showMessageDialog(this, "line/connected 至少选择 1 个纵轴 Y 系列并指定横轴 X。", "图形设置尚未完整", 1);
               return false;
            }
            if (ys.contains(x)) {
               JOptionPane.showMessageDialog(this, "Y 系列不能同时作为横轴 X。", "图形变量角色重复", 2);
               return false;
            }
         }
         if (Arrays.asList("qfit", "lowess", "lpoly").contains(command)) {
            String y = selected(this.depvar), x = selected(this.panel);
            if (y.isBlank() || x.isBlank()) {
               JOptionPane.showMessageDialog(this, "qfit/lowess/lpoly 需要分别选择 Y 和 X。", "图形设置尚未完整", 1);
               return false;
            }
            if (y.equals(x)) {
               JOptionPane.showMessageDialog(this, "Y 和 X 必须使用不同变量。", "图形变量角色重复", 2);
               return false;
            }
         }
         if (Arrays.asList("rvpplot", "avplot", "cprplot", "acprplot").contains(command) && selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, command + " 需要选择 1 个诊断变量 / predictor。", "回归诊断图设置尚未完整", 1);
            return false;
         }
         if ("twoway".equals(command) && this.expression.getText().trim().isBlank()) {'''
java = replace_exact(java, validation_boundary, validation_insert, label="new graph validations")

# Static verifier: keep the special-route declaration in lockstep with Java.
static = replace_exact(static, old_route, new_route, expected=1, label="static special route")
static = replace_exact(
    static,
    'for graph_cmd in ("graph_matrix", "twoway_contour",',
    'for graph_cmd in ("line", "connected", "qfit", "lowess", "lpoly", "rvfplot", "rvpplot", "avplot", "avplots", "lvr2plot", "cprplot", "acprplot", "graph_matrix", "twoway_contour",',
    label="static structured graph loop",
)

# Lock in the new pages, builders, validations, roles, and explicit in support.
static_anchor = '''for needle in (
    'marginsplot · margins 结果图','''
static_block = '''for needle in (
    'line · 折线图',
    'connected · 带点折线图',
    'qfit · 二次拟合图',
    'lowess · LOWESS 平滑图',
    'lpoly · 局部多项式平滑图',
    'rvfplot · 残差 vs 拟合值',
    'rvpplot · 残差 vs predictor',
    'avplot · Added-variable plot',
    'avplots · 全部 Added-variable plots',
    'lvr2plot · Leverage vs residual-squared',
    'cprplot · Component-plus-residual plot',
    'acprplot · Augmented component-plus-residual plot',
    '纵轴 Y 系列（至少 1 个，可多选）',
    '诊断变量 / predictor',
    'var1 = "twoway qfit " + selected(this.depvar) + " " + selected(this.panel)',
    'Arrays.asList("rvfplot", "avplots", "lvr2plot").contains(this.currentCommand)',
    'line/connected 至少选择 1 个纵轴 Y 系列并指定横轴 X',
    'Y 系列不能同时作为横轴 X',
    'qfit/lowess/lpoly 需要分别选择 Y 和 X',
    '需要选择 1 个诊断变量 / predictor',
    '"rchart", "xchart", "shewhart", "line", "connected", "qfit", "lowess", "lpoly", "rvfplot", "rvpplot", "avplot", "avplots", "lvr2plot", "cprplot", "acprplot"',
):
    if needle not in java:
        fail(f"twoway/regression-diagnostic Graphics contract missing: {needle}")
for graph_cmd in ("line", "connected", "qfit", "lowess", "lpoly", "rvfplot", "rvpplot", "avplot", "avplots", "lvr2plot", "cprplot", "acprplot"):
    if graph_cmd not in roc_route_scope:
        fail(f"twoway/regression-diagnostic graph must route to graph result view: {graph_cmd}")

'''
static = replace_exact(static, static_anchor, static_block + static_anchor, label="static diagnostics contract block")

# Method-card previews must reflect the real command inventory.
static = replace_exact(
    static,
    'graph_method_preview_contracts = (\n    \'case "生存分析图": return "sts graph";\',',
    'graph_method_preview_contracts = (\n    \'case "二维图(散点图，折线图等)": return "twoway · scatter · line · connected · lfit · qfit";\',\n    \'case "平滑和密度": return "kdensity · lowess · lpoly";\',\n    \'case "回归诊断图": return "rvfplot · rvpplot · avplot · avplots · lvr2plot · cprplot · acprplot";\',\n    \'case "生存分析图": return "sts graph";\',',
    label="static method preview contracts",
)

java_path.write_text(java, encoding="utf-8")
static_path.write_text(static, encoding="utf-8")
print("HX_GRAPH_DIAGNOSTICS_PATCH_OK")
