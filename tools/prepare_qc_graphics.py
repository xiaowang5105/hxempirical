from pathlib import Path

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


# 1. Dedicated QC controls.
replace_once(
    '      private final JCheckBox specialGraphRiskTable = new JCheckBox("显示风险人数表 risktable", false);',
    '''      private final JCheckBox specialGraphRiskTable = new JCheckBox("显示风险人数表 risktable", false);\n      private final JCheckBox specialGraphQcStabilized = new JCheckBox("样本量不等时稳定化 stabilized", false);\n      private final JTextField specialGraphQcStd = new JTextField();\n      private final JTextField specialGraphQcMean = new JTextField();\n      private final JTextField specialGraphQcLower = new JTextField();\n      private final JTextField specialGraphQcUpper = new JTextField();''',
    "QC control fields",
)

replace_once(
    '''            this.newvar,\n            this.expression,\n            this.model,''',
    '''            this.newvar,\n            this.expression,\n            this.specialGraphQcStd,\n            this.specialGraphQcMean,\n            this.specialGraphQcLower,\n            this.specialGraphQcUpper,\n            this.model,''',
    "QC text preview listeners",
)
replace_once(
    '         this.specialGraphRiskTable.addActionListener(var1x -> this.schedulePreview());',
    '         this.specialGraphRiskTable.addActionListener(var1x -> this.schedulePreview());\n         this.specialGraphQcStabilized.addActionListener(var1x -> this.schedulePreview());',
    "QC stabilized listener",
)

# 2. Route the five official QC commands to the structured graph workspace.
route_old = '"gladder", "qladder", "dotplot", "spikeplot", "sunflower", "serrbar", "graph_combine"'
route_new = '"gladder", "qladder", "dotplot", "spikeplot", "sunflower", "cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar", "graph_combine"'
route_count = text.count(route_old)
if route_count != 2:
    raise SystemExit(f"QC route anchors: expected 2, found {route_count}")
text = text.replace(route_old, route_new)

# cchart/pchart syntax does not take if/in; repeated-measurement QC charts do.
replace_once(
    '&& !Arrays.asList("screeplot", "scoreplot", "loadingplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay", "graph_combine", "graph").contains(var1);',
    '&& !Arrays.asList("screeplot", "scoreplot", "loadingplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay", "cchart", "pchart", "graph_combine", "graph").contains(var1);',
    "QC sample-condition eligibility",
)

# 3. Reset/style QC controls whenever a graph page opens.
replace_once(
    '''         this.specialGraphRiskTable.setForeground(TEXT);\n         this.configureSpecialGraphModel(var1);''',
    '''         this.specialGraphRiskTable.setForeground(TEXT);\n         this.specialGraphQcStabilized.setSelected(false);\n         this.specialGraphQcStabilized.setOpaque(false);\n         this.specialGraphQcStabilized.setForeground(TEXT);\n         this.specialGraphQcStd.setText("");\n         this.specialGraphQcMean.setText("");\n         this.specialGraphQcLower.setText("");\n         this.specialGraphQcUpper.setText("");\n         styleTextField(this.specialGraphQcStd);\n         styleTextField(this.specialGraphQcMean);\n         styleTextField(this.specialGraphQcLower);\n         styleTextField(this.specialGraphQcUpper);\n         this.configureSpecialGraphModel(var1);''',
    "QC reset/style",
)

# 4. Beginner-facing command semantics on the dedicated pages.
header_anchor = '''         } else if ("serrbar".equals(var1)) {\n            this.commandTitle.setText("serrbar · 均值与标准误条形图");'''
header_addition = r'''         } else if ("cchart".equals(var1)) {
            this.commandTitle.setText("cchart · 缺陷数控制图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> cchart defects day</html>");
            this.insightArea.setText("主要意图：按检查单位观察缺陷数是否落在过程控制限内。\n\n选择缺陷数变量和单位编号变量；单位编号用于横轴识别各检查单位。\n\n控制限样式、连接线、标记、标题等继续使用 Stata 原生图形 options。");
            this.syntaxArea.setText("cchart defect_var unit_var [, options]");
            coreTitle = "缺陷数与检查单位";
            coreSubtitle = "分别选择每个单位的缺陷数和单位编号；无需手写两个变量的顺序。";
         } else if ("pchart".equals(var1)) {
            this.commandTitle.setText("pchart · 不合格率控制图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> pchart rejects day ssize, stabilized</html>");
            this.insightArea.setText("主要意图：根据每个检查单位的不合格数和实际检查样本量绘制 fraction-defective 控制图。\n\n依次选择不合格数、单位编号和样本量变量；样本量不等时可显式开启 stabilized。\n\nStata 会根据不合格数 / 样本量计算比例；这里不要把已经算好的比例变量放进“不合格数”角色。");
            this.syntaxArea.setText("pchart reject_var unit_var ssize_var [, stabilized options]");
            coreTitle = "不合格数 / 单位 / 样本量";
            coreSubtitle = "三个角色分别选择；样本量不等时可开启 stabilized。";
         } else if ("rchart".equals(var1)) {
            this.commandTitle.setText("rchart · R 极差控制图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> rchart m1 m2 m3 m4, connect(l)</html>");
            this.insightArea.setText("主要意图：比较每个样本内多次测量的极差，检查过程离散程度是否稳定。\n\n一行代表一个样本，所选多个变量代表该样本内的重复测量；可选填写已知过程标准差 std()。\n\n样本筛选支持 if / in，连接方式、控制线和标题继续使用原生 options。");
            this.syntaxArea.setText("rchart varlist [if] [in] [, std(#) options]");
            coreTitle = "样本内重复测量";
            coreSubtitle = "选择同一批样本内的测量列；已知过程标准差时再填写 std()。";
         } else if ("xchart".equals(var1)) {
            this.commandTitle.setText("xchart · X-bar 均值控制图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> xchart m1 m2 m3 m4, mean(10) std(.5)</html>");
            this.insightArea.setText("主要意图：按样本观察重复测量的平均水平是否稳定。\n\n一行代表一个样本，多个变量代表样本内重复测量。std()、mean() 可留空让 Stata 从数据估计；如果直接指定控制限，lower() 与 upper() 必须成对填写。\n\n样本筛选支持 if / in。");
            this.syntaxArea.setText("xchart varlist [if] [in] [, std(#) mean(#) lower(#) upper(#) options]");
            coreTitle = "重复测量与控制限";
            coreSubtitle = "先选择测量列；过程参数未知时可全部留空，已知时再填写相应参数。";
         } else if ("shewhart".equals(var1)) {
            this.commandTitle.setText("shewhart · X-bar + R 联合控制图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> shewhart m1 m2 m3 m4, std(.5) mean(10)</html>");
            this.insightArea.setText("主要意图：在同一输出中纵向对齐 X-bar 均值控制图与 R 极差控制图。\n\n一行代表一个样本，多个变量代表样本内重复测量；std() 和 mean() 都可留空，由 Stata 从数据计算。\n\n样本筛选支持 if / in，组合图样式继续使用原生 options。");
            this.syntaxArea.setText("shewhart varlist [if] [in] [, std(#) mean(#) options]");
            coreTitle = "重复测量与过程参数";
            coreSubtitle = "选择样本内测量列；已知总体过程参数时再填写 std() / mean()。";
'''
insert_before(header_anchor, header_addition, "QC page headers")

# 5. True input roles instead of command-body typing.
core_anchor = '''         } else if ("serrbar".equals(var1)) {\n            JPanel seVars = new JPanel(new GridLayout(1, 3, 10, 0));'''
core_addition = r'''         } else if ("cchart".equals(var1)) {
            JPanel cVars = new JPanel(new GridLayout(1, 2, 12, 0));
            cVars.setOpaque(false);
            cVars.add(this.fieldBlock("缺陷数变量", this.depvar));
            cVars.add(this.fieldBlock("检查单位编号", this.panel));
            this.addGenericBodyField(coreBody, "两个变量角色", cVars);
            JLabel cHint = new JLabel("每行对应一个检查单位；缺陷数是 count，单位编号用于识别横轴上的单位。");
            cHint.setForeground(MUTED);
            cHint.setFont(cHint.getFont().deriveFont(9.8F));
            cHint.setAlignmentX(0.0F);
            coreBody.add(cHint);
         } else if ("pchart".equals(var1)) {
            JPanel pVars = new JPanel(new GridLayout(1, 3, 10, 0));
            pVars.setOpaque(false);
            pVars.add(this.fieldBlock("不合格数", this.depvar));
            pVars.add(this.fieldBlock("检查单位编号", this.panel));
            pVars.add(this.fieldBlock("检查样本量", this.time));
            this.addGenericBodyField(coreBody, "三个变量角色", pVars);
            this.addGenericBodyField(coreBody, "样本量不等", this.specialGraphQcStabilized);
            JLabel pHint = new JLabel("填写每个单位实际检查的数量；pchart 会自行计算 fraction defective，不需要预先生成比例。");
            pHint.setForeground(MUTED);
            pHint.setFont(pHint.getFont().deriveFont(9.8F));
            pHint.setAlignmentX(0.0F);
            coreBody.add(pHint);
         } else if ("rchart".equals(var1)) {
            this.addGenericBodyField(coreBody, "样本内重复测量变量（可多选）", this.listPane(this.variables));
            this.addGenericBodyField(coreBody, "已知过程标准差 std()（可选，只填数字）", this.specialGraphQcStd);
            JLabel rHint = new JLabel("数据结构：每一行是一批/一个样本；m1、m2、m3… 是该样本内的重复测量。");
            rHint.setForeground(MUTED);
            rHint.setFont(rHint.getFont().deriveFont(9.8F));
            rHint.setAlignmentX(0.0F);
            coreBody.add(rHint);
         } else if ("xchart".equals(var1)) {
            this.addGenericBodyField(coreBody, "样本内重复测量变量（可多选）", this.listPane(this.variables));
            JPanel xKnown = new JPanel(new GridLayout(1, 2, 12, 0));
            xKnown.setOpaque(false);
            xKnown.add(this.fieldBlock("已知标准差 std()（可选）", this.specialGraphQcStd));
            xKnown.add(this.fieldBlock("已知总体均值 mean()（可选）", this.specialGraphQcMean));
            this.addGenericBodyField(coreBody, "已知过程参数", xKnown);
            JPanel xLimits = new JPanel(new GridLayout(1, 2, 12, 0));
            xLimits.setOpaque(false);
            xLimits.add(this.fieldBlock("下控制限 lower()（可选）", this.specialGraphQcLower));
            xLimits.add(this.fieldBlock("上控制限 upper()（可选）", this.specialGraphQcUpper));
            this.addGenericBodyField(coreBody, "直接指定 X-bar 控制限", xLimits);
            JLabel xHint = new JLabel("lower()/upper() 要么都留空、要么一起填写；留空时控制限由 mean/std（指定或估计）计算。");
            xHint.setForeground(MUTED);
            xHint.setFont(xHint.getFont().deriveFont(9.8F));
            xHint.setAlignmentX(0.0F);
            coreBody.add(xHint);
         } else if ("shewhart".equals(var1)) {
            this.addGenericBodyField(coreBody, "样本内重复测量变量（可多选）", this.listPane(this.variables));
            JPanel sKnown = new JPanel(new GridLayout(1, 2, 12, 0));
            sKnown.setOpaque(false);
            sKnown.add(this.fieldBlock("已知标准差 std()（可选）", this.specialGraphQcStd));
            sKnown.add(this.fieldBlock("已知总体均值 mean()（可选）", this.specialGraphQcMean));
            this.addGenericBodyField(coreBody, "已知过程参数", sKnown);
            JLabel sHint = new JLabel("两项都可留空；Stata 会从重复测量数据计算过程均值和离散程度。");
            sHint.setForeground(MUTED);
            sHint.setFont(sHint.getFont().deriveFont(9.8F));
            sHint.setAlignmentX(0.0F);
            coreBody.add(sHint);
'''
insert_before(core_anchor, core_addition, "QC core inputs")

# 6. Do not show misleading generic drag-role names on QC pages.
old_drop = '''         this.enableVariableDrop(this.depvar, "Y / 分布变量");\n         this.enableVariableDrop(this.variables, "横轴 X");\n         this.enableVariableDrop(this.panel, "分组 / 处理组变量");\n         this.enableVariableDrop(this.time, "时间变量");'''
new_drop = '''         if ("cchart".equals(var1)) {\n            this.enableVariableDrop(this.depvar, "缺陷数变量");\n            this.enableVariableDrop(this.panel, "检查单位编号");\n         } else if ("pchart".equals(var1)) {\n            this.enableVariableDrop(this.depvar, "不合格数变量");\n            this.enableVariableDrop(this.panel, "检查单位编号");\n            this.enableVariableDrop(this.time, "检查样本量");\n         } else if (Arrays.asList("rchart", "xchart", "shewhart").contains(var1)) {\n            this.enableVariableDrop(this.variables, "样本内重复测量变量");\n         } else {\n            this.enableVariableDrop(this.depvar, "Y / 分布变量");\n            this.enableVariableDrop(this.variables, "横轴 X");\n            this.enableVariableDrop(this.panel, "分组 / 处理组变量");\n            this.enableVariableDrop(this.time, "时间变量");\n         }'''
replace_once(old_drop, new_drop, "QC drag roles")

# 7. rchart/xchart/shewhart support both if and in according to official syntax.
replace_once(
    '''         block.setLayout(new BoxLayout(block, BoxLayout.Y_AXIS));\n\n         JPanel content = new JPanel();''',
    '''         block.setLayout(new BoxLayout(block, BoxLayout.Y_AXIS));\n         boolean includeIn = Arrays.asList("rchart", "xchart", "shewhart").contains(this.currentCommand);\n\n         JPanel content = new JPanel();''',
    "QC in eligibility",
)
replace_once(
    '''         if (includeIf) {\n            content.add(this.labeledInline("样本条件 if", this.ifCondition));\n            content.add(Box.createVerticalStrut(8));\n         }\n         content.add(this.labeledInline(optionLabel, this.options));''',
    '''         if (includeIf) {\n            content.add(this.labeledInline("样本条件 if", this.ifCondition));\n            content.add(Box.createVerticalStrut(8));\n         }\n         if (includeIn) {\n            content.add(this.labeledInline("观测范围 in（例如 1/20）", this.inCondition));\n            content.add(Box.createVerticalStrut(8));\n         }\n         content.add(this.labeledInline(optionLabel, this.options));''',
    "QC in field",
)

# 8. Build exact official command shapes.
preview_anchor = '''         } else if ("serrbar".equals(this.currentCommand)) {\n            var1 = "serrbar " + selected(this.depvar) + " " + selected(this.panel) + " " + selected(this.time);'''
preview_addition = r'''         } else if ("cchart".equals(this.currentCommand)) {
            var1 = "cchart " + selected(this.depvar) + " " + selected(this.panel);
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if ("pchart".equals(this.currentCommand)) {
            var1 = "pchart " + selected(this.depvar) + " " + selected(this.panel) + " " + selected(this.time);
            ArrayList<String> pOpts = new ArrayList<>();
            if (this.specialGraphQcStabilized.isSelected()) pOpts.add("stabilized");
            if (!this.options.getText().trim().isBlank()) pOpts.add(this.options.getText().trim());
            if (!pOpts.isEmpty()) var1 += ", " + String.join(" ", pOpts);
         } else if (Arrays.asList("rchart", "xchart", "shewhart").contains(this.currentCommand)) {
            List<String> qcVars = this.variables.getSelectedValuesList();
            var1 = this.currentCommand + (qcVars.isEmpty() ? "" : " " + String.join(" ", qcVars));
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            if (!this.inCondition.getText().trim().isBlank()) var1 += " in " + this.inCondition.getText().trim();
            ArrayList<String> qcOpts = new ArrayList<>();
            String qcStd = this.specialGraphQcStd.getText().trim();
            String qcMean = this.specialGraphQcMean.getText().trim();
            String qcLower = this.specialGraphQcLower.getText().trim();
            String qcUpper = this.specialGraphQcUpper.getText().trim();
            if (!qcStd.isBlank()) qcOpts.add("std(" + qcStd + ")");
            if (("xchart".equals(this.currentCommand) || "shewhart".equals(this.currentCommand)) && !qcMean.isBlank()) qcOpts.add("mean(" + qcMean + ")");
            if ("xchart".equals(this.currentCommand) && !qcLower.isBlank() && !qcUpper.isBlank()) {
               qcOpts.add("lower(" + qcLower + ")");
               qcOpts.add("upper(" + qcUpper + ")");
            }
            if (!this.options.getText().trim().isBlank()) qcOpts.add(this.options.getText().trim());
            if (!qcOpts.isEmpty()) var1 += ", " + String.join(" ", qcOpts);
'''
insert_before(preview_anchor, preview_addition, "QC command generation")

# 9. Inspector role hints.
role_anchor = '''         if ("serrbar".equals(this.currentCommand)) {\n            if (variable.equals(selected(this.depvar))) return "均值变量";'''
role_addition = r'''         if ("cchart".equals(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "缺陷数";
            if (variable.equals(selected(this.panel))) return "检查单位编号";
         }
         if ("pchart".equals(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "不合格数";
            if (variable.equals(selected(this.panel))) return "检查单位编号";
            if (variable.equals(selected(this.time))) return "检查样本量";
         }
         if (Arrays.asList("rchart", "xchart", "shewhart").contains(this.currentCommand)
            && this.variables.getSelectedValuesList().contains(variable)) return "样本内重复测量";
'''
insert_before(role_anchor, role_addition, "QC inspector roles")

# 10. Validation: role completeness, distinct variables, numeric process parameters, paired X limits.
validation_anchor = '''         if ("serrbar".equals(command)) {\n            String mean = selected(this.depvar), error = selected(this.panel), axis = selected(this.time);'''
validation_addition = r'''         if ("cchart".equals(command)) {
            String defects = selected(this.depvar), unit = selected(this.panel);
            if (defects.isBlank() || unit.isBlank()) {
               JOptionPane.showMessageDialog(this, "cchart 需要分别选择缺陷数变量和检查单位编号。", "质量控制图设置尚未完整", 1);
               return false;
            }
            if (defects.equals(unit)) {
               JOptionPane.showMessageDialog(this, "缺陷数和检查单位编号必须使用不同变量。", "质量控制图变量重复", 2);
               return false;
            }
         }
         if ("pchart".equals(command)) {
            String rejects = selected(this.depvar), unit = selected(this.panel), ssize = selected(this.time);
            if (rejects.isBlank() || unit.isBlank() || ssize.isBlank()) {
               JOptionPane.showMessageDialog(this, "pchart 需要不合格数、检查单位编号和检查样本量三个变量。", "质量控制图设置尚未完整", 1);
               return false;
            }
            if (new LinkedHashSet<>(Arrays.asList(rejects, unit, ssize)).size() < 3) {
               JOptionPane.showMessageDialog(this, "pchart 的三个变量角色必须使用不同变量。", "质量控制图变量重复", 2);
               return false;
            }
         }
         if (Arrays.asList("rchart", "xchart", "shewhart").contains(command)) {
            if (this.variables.getSelectedValuesList().isEmpty()) {
               JOptionPane.showMessageDialog(this, command + " 至少选择 1 个样本内测量变量；通常应选择同一批样本的多次测量列。", "质量控制图设置尚未完整", 1);
               return false;
            }
            String stdText = this.specialGraphQcStd.getText().trim();
            if (!stdText.isBlank()) {
               try {
                  double stdValue = Double.parseDouble(stdText);
                  if (!(stdValue > 0.0)) throw new NumberFormatException();
               } catch (NumberFormatException ex) {
                  JOptionPane.showMessageDialog(this, "std() 请填写正数，例如 0.5。", "过程标准差无效", 1);
                  return false;
               }
            }
            if (Arrays.asList("xchart", "shewhart").contains(command)) {
               String meanText = this.specialGraphQcMean.getText().trim();
               if (!meanText.isBlank()) {
                  try { Double.parseDouble(meanText); }
                  catch (NumberFormatException ex) {
                     JOptionPane.showMessageDialog(this, "mean() 请填写数值，例如 10。", "过程均值无效", 1);
                     return false;
                  }
               }
            }
         }
         if ("xchart".equals(command)) {
            String lowerText = this.specialGraphQcLower.getText().trim();
            String upperText = this.specialGraphQcUpper.getText().trim();
            if (lowerText.isBlank() != upperText.isBlank()) {
               JOptionPane.showMessageDialog(this, "xchart 的 lower() 与 upper() 必须同时填写或同时留空。", "控制限设置不完整", 1);
               return false;
            }
            if (!lowerText.isBlank()) {
               try {
                  double lowerValue = Double.parseDouble(lowerText);
                  double upperValue = Double.parseDouble(upperText);
                  if (!(lowerValue < upperValue)) {
                     JOptionPane.showMessageDialog(this, "下控制限 lower() 必须小于上控制限 upper()。", "控制限顺序无效", 1);
                     return false;
                  }
               } catch (NumberFormatException ex) {
                  JOptionPane.showMessageDialog(this, "lower() / upper() 请填写数值。", "控制限格式无效", 1);
                  return false;
               }
            }
         }
'''
insert_before(validation_anchor, validation_addition, "QC validation")

JAVA.write_text(text, encoding="utf-8")

# 11. Extend static contracts without weakening existing checks.
s = STATIC.read_text(encoding="utf-8")
old_special = '"gladder", "qladder", "dotplot", "spikeplot", "sunflower", "serrbar", "graph_combine"'
new_special = '"gladder", "qladder", "dotplot", "spikeplot", "sunflower", "cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar", "graph_combine"'
if s.count(old_special) != 1:
    raise SystemExit(f"static special route anchor count={s.count(old_special)}")
s = s.replace(old_special, new_special, 1)
old_loop = '"dotplot", "spikeplot", "sunflower", "serrbar", "graph_combine", "graph"):'
new_loop = '"dotplot", "spikeplot", "sunflower", "cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar", "graph_combine", "graph"):'
if s.count(old_loop) != 1:
    raise SystemExit(f"static QC route loop anchor count={s.count(old_loop)}")
s = s.replace(old_loop, new_loop, 1)
needle_anchor = '''if "hxempirical 不再自动安装第三方命令" not in entry:\n    fail("public hxempirical install compatibility path must not install packages")'''
qc_contract = '''for needle in (\n    'cchart · 缺陷数控制图',\n    'pchart · 不合格率控制图',\n    'rchart · R 极差控制图',\n    'xchart · X-bar 均值控制图',\n    'shewhart · X-bar + R 联合控制图',\n    'var1 = "cchart " + selected(this.depvar) + " " + selected(this.panel)',\n    'var1 = "pchart " + selected(this.depvar) + " " + selected(this.panel) + " " + selected(this.time)',\n    'pOpts.add("stabilized")',\n    'qcOpts.add("std(" + qcStd + ")")',\n    'qcOpts.add("lower(" + qcLower + ")")',\n    'xchart 的 lower() 与 upper() 必须同时填写或同时留空',\n    'return "样本内重复测量"',\n):\n    if needle not in java:\n        fail(f"quality-control Graphics page contract missing: {needle}")\n\n'''
if s.count(needle_anchor) != 1:
    raise SystemExit(f"static QC contract insertion anchor count={s.count(needle_anchor)}")
s = s.replace(needle_anchor, qc_contract + needle_anchor, 1)
STATIC.write_text(s, encoding="utf-8")

# Fail closed if any core source contract is absent after patching.
final_text = JAVA.read_text(encoding="utf-8")
required = [
    '"cchart".equals(var1)',
    '"pchart".equals(var1)',
    'Arrays.asList("rchart", "xchart", "shewhart").contains(var1)',
    'this.specialGraphQcStabilized.isSelected()',
    'qcOpts.add("std(" + qcStd + ")")',
    'qcOpts.add("lower(" + qcLower + ")")',
    'content.add(this.labeledInline("观测范围 in（例如 1/20）", this.inCondition))',
    'xchart 的 lower() 与 upper() 必须同时填写或同时留空',
]
missing = [needle for needle in required if needle not in final_text]
if missing:
    raise SystemExit("QC Graphics source contract missing: " + repr(missing))
print("HX_QC_GRAPHICS_PATCH_OK")
