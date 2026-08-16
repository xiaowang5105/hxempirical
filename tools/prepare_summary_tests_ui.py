from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
java_path = root / "src/main/java/com/hexie/stata/HxWorkbench.java"
static_path = root / "tools/verify_static_contracts.py"
java = java_path.read_text(encoding="utf-8")
static = static_path.read_text(encoding="utf-8")


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        print(f"HX_SUMMARY_TEST_PATCH_FAIL {label}: expected 1, found {count}", file=sys.stderr)
        raise SystemExit(1)
    return text.replace(old, new)

# Central classification for the first Statistics method: only commands with stable, unambiguous roles are specialized.
anchor = '''      private static boolean isCoreModelCommand(String command) {
'''
insert = '''      private static boolean isStructuredSummaryTestCommand(String command) {
         return Arrays.asList("tabulate", "oneway", "ranksum", "median", "signrank", "signtest").contains(command);
      }

      private static boolean isCoreModelCommand(String command) {
'''
java = replace_once(java, anchor, insert, "summary-test classifier")

# Dedicated task form.  table/anova/dtable intentionally remain native-command-body pages.
anchor = '''      private void rebuildForm() {
'''
helper = '''      private void rebuildStructuredSummaryTestForm() {
         String command = this.currentCommand;
         this.enableVariableDrop(this.depvar, "检验 / 分类变量");
         this.enableVariableDrop(this.panel, "分组 / 第二分类变量");
         this.enableVariableDrop(this.expression, "比较对象 / 表达式");

         String title;
         String example;
         String insight;
         String syntax;
         String firstLabel;
         String secondLabel = "";
         String firstStep = "选择检验对象";
         String firstSubtitle;

         if ("tabulate".equals(command)) {
            title = "tabulate · 频数 / 列联表";
            example = "tabulate foreign";
            insight = "选择 1 个分类变量得到单向频数表；再选择第 2 个分类变量时生成双向列联表。卡方检验、行列百分比、缺失值显示等继续使用 tabulate 原生 options。";
            syntax = "tabulate var1 [var2] [if] [in] [, options]";
            firstLabel = "分类变量 1";
            secondLabel = "分类变量 2（可选）";
            firstStep = "选择分类变量";
            firstSubtitle = "第 1 个分类变量必选；第 2 个可选。只允许 1–2 个分类变量，避免把 tabulate 当普通 varlist 使用。";
         } else if ("oneway".equals(command)) {
            title = "oneway · 单因素方差分析";
            example = "oneway mpg rep78";
            insight = "结果变量放在前面，分组因子放在第二个位置。多因素、交互项、协变量或更复杂的 ANOVA 设计请使用 anova 的原生命令主体页。";
            syntax = "oneway response group [if] [in] [, options]";
            firstLabel = "结果变量";
            secondLabel = "分组因子";
            firstSubtitle = "明确区分连续结果与分组因子；这里只做单因素 ANOVA。";
         } else if ("ranksum".equals(command)) {
            title = "ranksum · Wilcoxon 秩和检验";
            example = "ranksum mpg, by(foreign)";
            insight = "用于比较独立组的分布位置；检验变量与分组变量是两个不同角色。分组通过官方 by() 选项写入命令。";
            syntax = "ranksum varname [if] [in], by(group) [options]";
            firstLabel = "检验变量";
            secondLabel = "分组变量 by()";
            firstSubtitle = "选择要比较的变量和独立分组变量；by() 由页面自动生成。";
         } else if ("median".equals(command)) {
            title = "median · 中位数相等检验";
            example = "median mpg, by(foreign)";
            insight = "检验不同组的中位数是否相等。页面把检验变量与 by() 分组变量分开，避免把分组字段误当普通分析变量。";
            syntax = "median varname [if] [in], by(group) [options]";
            firstLabel = "检验变量";
            secondLabel = "分组变量 by()";
            firstSubtitle = "选择要比较中位数的变量和分组变量；by() 由页面自动生成。";
         } else if ("signrank".equals(command)) {
            title = "signrank · Wilcoxon 配对符号秩检验";
            example = "signrank before = after";
            insight = "配对检验使用 varname = exp 结构。左侧选择第一个变量，右侧填写第二个变量或合法 Stata 表达式；页面不会把等号右侧误标成解释变量。";
            syntax = "signrank varname = exp [if] [in] [, options]";
            firstLabel = "配对变量 1";
            firstSubtitle = "左侧选择第一个配对变量；比较对象可直接填写第二个变量名或 Stata 表达式。";
         } else {
            title = "signtest · 配对符号检验";
            example = "signtest before = after";
            insight = "配对符号检验使用 varname = exp 结构。左侧选择第一个变量，右侧填写第二个变量或合法 Stata 表达式。";
            syntax = "signtest varname = exp [if] [in] [, options]";
            firstLabel = "配对变量 1";
            firstSubtitle = "左侧选择第一个配对变量；比较对象可直接填写第二个变量名或 Stata 表达式。";
         }

         this.commandTitle.setText(title);
         this.commandTitle.setToolTipText(title);
         this.exampleLabel.setText("<html><b>最简单例子：</b> " + html(example) + "</html>");
         this.insightArea.setText(insight);
         this.syntaxArea.setText(syntax);

         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.taskStepStripV153(firstStep, "样本与选项", "检查运行"), c);

         JPanel coreCard = this.xtregWizardCardV130(1, firstStep, firstSubtitle);
         JPanel coreBody = this.genericCardBody();
         this.addGenericBodyField(coreBody, firstLabel, this.depvar);
         if (!secondLabel.isBlank()) {
            this.addGenericBodyField(coreBody, secondLabel, this.panel);
         }
         if (Arrays.asList("signrank", "signtest").contains(command)) {
            this.addGenericBodyField(coreBody, "比较对象（第二变量或表达式）", this.expression);
         }
         coreCard.add(coreBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(coreCard, c);

         JPanel sampleCard = this.xtregWizardCardV130(2, "样本与选项", "if / in 与命令特有 options 集中在这里；默认不替你猜检验方向或报告选项。");
         JPanel sampleBody = this.genericCardBody();
         JPanel sampleRow = new JPanel(new GridLayout(1, 2, 10, 0));
         sampleRow.setOpaque(false);
         sampleRow.add(this.fieldBlock("样本条件 if（可选）", this.ifCondition));
         sampleRow.add(this.fieldBlock("观测范围 in（可选）", this.inCondition));
         this.addGenericBodyField(sampleBody, "样本范围", sampleRow);
         this.addGenericBodyField(sampleBody, "其他 Stata options（可选）", this.options);
         sampleCard.add(sampleBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(sampleCard, c);

         JPanel checkCard = this.xtregWizardCardV130(3, "检查运行", "下方命令预览始终使用真实 Stata 语法；运行前核对变量角色、样本条件和 options。");
         JPanel checkBody = this.genericCardBody();
         JLabel checkHint = new JLabel("<html>复杂多因素 ANOVA 使用 <b>anova</b>；新版多维报表使用 <b>table / dtable</b>。这些命令继续保留原生主体，不在本页强行简化。</html>");
         checkHint.setForeground(MUTED);
         checkHint.setFont(checkHint.getFont().deriveFont(9.8F));
         checkHint.setAlignmentX(0.0F);
         checkBody.add(checkHint);
         checkCard.add(checkBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(checkCard, c);

         GridBagConstraints filler = this.constraints(0, c.gridy + 1);
         filler.gridwidth = 2;
         filler.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), filler);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.rebuilding = false;
         this.statusLabel.setText(command + "：变量角色已按官方语法拆开；下方实时生成真实 Stata 命令。");
      }

      private void updateStructuredSummaryTestPreview() {
         String command = this.currentCommand;
         String first = selected(this.depvar);
         String second = selected(this.panel);
         String comparison = this.expression.getText().trim();
         StringBuilder preview = new StringBuilder(command);

         if (!first.isBlank()) preview.append(" ").append(first);
         if ("tabulate".equals(command) && !second.isBlank()) preview.append(" ").append(second);
         else if ("oneway".equals(command) && !second.isBlank()) preview.append(" ").append(second);
         else if (Arrays.asList("signrank", "signtest").contains(command) && !comparison.isBlank()) preview.append(" = ").append(comparison);

         if (!this.ifCondition.getText().trim().isBlank()) preview.append(" if ").append(this.ifCondition.getText().trim());
         if (!this.inCondition.getText().trim().isBlank()) preview.append(" in ").append(this.inCondition.getText().trim());

         ArrayList<String> opts = new ArrayList<>();
         if (Arrays.asList("ranksum", "median").contains(command) && !second.isBlank()) opts.add("by(" + second + ")");
         if (!this.options.getText().trim().isBlank()) opts.add(this.options.getText().trim());
         if (!opts.isEmpty()) preview.append(", ").append(String.join(" ", opts));

         this.rebuilding = true;
         this.previewArea.setText(preview.toString());
         this.previewArea.setCaretPosition(0);
         this.rebuilding = false;
         this.flashCommandPreview();
      }

      private void rebuildForm() {
'''
java = replace_once(java, anchor, helper, "structured summary-test helpers")

# Route those pages into the dedicated builder after generic controls have been reset/refreshed.
anchor = '''         if (this.flag("has_cluster") && !comboContains(this.vce, "cluster")) this.vce.addItem("cluster");

         boolean rawCommandBody = "command_body".equals(this.sem("template"));
'''
replacement = '''         if (this.flag("has_cluster") && !comboContains(this.vce, "cluster")) this.vce.addItem("cluster");

         if (isStructuredSummaryTestCommand(this.currentCommand)) {
            this.rebuildStructuredSummaryTestForm();
            return;
         }

         boolean rawCommandBody = "command_body".equals(this.sem("template"));
'''
java = replace_once(java, anchor, replacement, "rebuildForm route")

# Build the preview locally because several commands use positional group roles or required by().
anchor = '''            } else if ("did_builder".equals(this.currentCommand)) {
               this.updateDidBuilderPreview();
            } else if (Arrays.asList("histogram", "kdensity", "scatter", "line", "connected", "lfit", "qfit", "lowess", "lpoly",'''
replacement = '''            } else if ("did_builder".equals(this.currentCommand)) {
               this.updateDidBuilderPreview();
            } else if (isStructuredSummaryTestCommand(this.currentCommand)) {
               this.updateStructuredSummaryTestPreview();
            } else if (Arrays.asList("histogram", "kdensity", "scatter", "line", "connected", "lfit", "qfit", "lowess", "lpoly",'''
java = replace_once(java, anchor, replacement, "preview route")

# Inspector roles follow the same command-specific semantics shown in the form.
anchor = '''         if (Arrays.asList("histogram", "kdensity").contains(this.currentCommand)) {
'''
replacement = '''         if ("tabulate".equals(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "分类变量 1";
            if (variable.equals(selected(this.panel))) return "分类变量 2";
         }
         if ("oneway".equals(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "结果变量";
            if (variable.equals(selected(this.panel))) return "分组因子";
         }
         if (Arrays.asList("ranksum", "median").contains(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "检验变量";
            if (variable.equals(selected(this.panel))) return "分组变量";
         }
         if (Arrays.asList("signrank", "signtest").contains(this.currentCommand) && variable.equals(selected(this.depvar))) return "配对变量 1";
         if (Arrays.asList("histogram", "kdensity").contains(this.currentCommand)) {
'''
java = replace_once(java, anchor, replacement, "inspector roles")

# Command-specific validation.  Keep the complex table/anova reporting grammars untouched.
anchor = '''      private boolean validateOrdinaryCommandBeforeRun() {
         String command = this.currentCommand;
'''
replacement = '''      private boolean validateOrdinaryCommandBeforeRun() {
         String command = this.currentCommand;
         if ("tabulate".equals(command)) {
            String first = selected(this.depvar), second = selected(this.panel);
            if (first.isBlank()) {
               JOptionPane.showMessageDialog(this, "tabulate 至少需要选择第 1 个分类变量。", "列联表设置尚未完整", 1);
               return false;
            }
            if (!second.isBlank() && first.equals(second)) {
               JOptionPane.showMessageDialog(this, "两个分类变量不能是同一个变量。", "列联表变量重复", 2);
               return false;
            }
         }
         if (Arrays.asList("oneway", "ranksum", "median").contains(command)) {
            String first = selected(this.depvar), group = selected(this.panel);
            if (first.isBlank() || group.isBlank()) {
               JOptionPane.showMessageDialog(this, command + " 需要分别选择检验 / 结果变量和分组变量。", "检验设置尚未完整", 1);
               return false;
            }
            if (first.equals(group)) {
               JOptionPane.showMessageDialog(this, "检验 / 结果变量与分组变量必须不同。", "检验变量角色重复", 2);
               return false;
            }
         }
         if (Arrays.asList("signrank", "signtest").contains(command)) {
            String first = selected(this.depvar), comparison = this.expression.getText().trim();
            if (first.isBlank() || comparison.isBlank()) {
               JOptionPane.showMessageDialog(this, command + " 需要选择第一个配对变量，并填写等号右侧的第二变量或表达式。", "配对检验设置尚未完整", 1);
               return false;
            }
            if (first.equals(comparison)) {
               JOptionPane.showMessageDialog(this, "等号左右不能填写完全相同的变量。", "配对变量重复", 2);
               return false;
            }
         }
'''
java = replace_once(java, anchor, replacement, "summary-test validation")

# Static contracts: first Statistics method has an explicit safe-structure boundary.
static_anchor = '''if 'String nativeCommand = "graph_bar".equals(this.currentCommand) ? "graph bar" : "graph dot";' not in java:
'''
static_insert = '''for needle in (
    'private static boolean isStructuredSummaryTestCommand(String command)',
    '"tabulate", "oneway", "ranksum", "median", "signrank", "signtest"',
    'private void rebuildStructuredSummaryTestForm()',
    'private void updateStructuredSummaryTestPreview()',
    'tabulate · 频数 / 列联表',
    'oneway · 单因素方差分析',
    'ranksum · Wilcoxon 秩和检验',
    'median · 中位数相等检验',
    'signrank · Wilcoxon 配对符号秩检验',
    'signtest · 配对符号检验',
    'opts.add("by(" + second + ")")',
    'tabulate 至少需要选择第 1 个分类变量',
    '需要分别选择检验 / 结果变量和分组变量',
    '需要选择第一个配对变量，并填写等号右侧的第二变量或表达式',
):
    if needle not in java:
        fail(f"structured summary/test UI contract missing: {needle}")

for cmd in ("table", "anova", "dtable"):
    if f' {cmd} ' not in semantics:
        fail(f"complex Statistics command must remain represented in hxsemantics: {cmd}")
if ' table prtest sdtest oneway anova ranksum median signrank signtest bitesti tabi ' not in semantics:
    fail("native-body safety family for complex summary/test commands changed unexpectedly")

if 'String nativeCommand = "graph_bar".equals(this.currentCommand) ? "graph bar" : "graph dot";' not in java:
'''
static = replace_once(static, static_anchor, static_insert, "static summary-test contracts")

java_path.write_text(java, encoding="utf-8")
static_path.write_text(static, encoding="utf-8")
print("HX_SUMMARY_TEST_PATCH_OK")
