from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/main/java/com/hexie/stata/HxWorkbench.java"
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    text = text.replace(old, new, 1)


# Reusable arbitrary step strip for special task pages.
marker = '''      private static boolean isCoreModelCommand(String command) {
'''
helper = '''      private JComponent taskStepStripV153(String... titles) {
         JPanel strip = cardPanel();
         strip.setBackground(SURFACE);
         strip.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 11),
            new EmptyBorder(9, 10, 9, 10)
         ));
         strip.setLayout(new GridLayout(1, titles.length, 8, 0));
         for (int i = 0; i < titles.length; i++) {
            JPanel p = new JPanel(new BorderLayout(6, 0));
            p.setOpaque(false);
            p.setMinimumSize(new Dimension(0, 0));
            p.add(this.xtregCircleBadge(Integer.toString(i + 1), i == 0, 24), BorderLayout.WEST);
            JLabel label = new JLabel("<html><b>" + html(titles[i]) + "</b></html>");
            label.setForeground(TEXT);
            label.setFont(label.getFont().deriveFont(10.5F));
            label.setMinimumSize(new Dimension(0, 0));
            p.add(label, BorderLayout.CENTER);
            strip.add(p);
         }
         strip.setPreferredSize(new Dimension(0, 52));
         strip.setMinimumSize(new Dimension(0, 52));
         strip.setMaximumSize(new Dimension(Integer.MAX_VALUE, 52));
         return strip;
      }

'''
if helper.strip() not in text:
    i = text.index(marker)
    text = text[:i] + helper + text[i:]


# Convert-to-DTA page: use the same task hierarchy as the redesigned command pages.
replace_once(
'''         JPanel var1 = new JPanel(new FlowLayout(0, 12, 0));
         var1.setOpaque(false);
         var1.add(this.convertSingleMode);
         var1.add(this.convertBatchMode);
         int var2 = 0;
         this.addField(var2++, "转换方式", var1);
         this.addField(var2++, "文件与读取设置", this.convertModeCards);
         GridBagConstraints var3 = this.constraints(0, var2);
         var3.gridwidth = 2;
         var3.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), var3);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.runButton.setText(this.convertSingleMode.isSelected() ? "转换为 DTA" : "开始批量转换");
         this.runButton.setEnabled(true);
         this.rebuilding = false;
         this.updateConversionPreview();
         this.statusLabel.setText("选择原始文件后会自动识别格式并在右侧显示只读预览。");
''',
'''         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.taskStepStripV153("转换方式", "文件与读取", "检查并转换"), c);

         JPanel modeCard = this.xtregWizardCardV130(1, "转换方式", "单个文件适合日常导入；批量转换适合同一目录中的多份原始表。");
         JPanel modeBody = this.genericCardBody();
         JPanel modeRow = new JPanel(new FlowLayout(0, 12, 0));
         modeRow.setOpaque(false);
         modeRow.add(this.convertSingleMode);
         modeRow.add(this.convertBatchMode);
         this.addGenericBodyField(modeBody, "选择处理方式", modeRow);
         modeCard.add(modeBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(modeCard, c);

         JPanel fileCard = this.xtregWizardCardV130(2, "文件与读取", "选择输入文件或文件夹，并设置读取规则与输出位置；右侧会同步显示预览和风险提示。");
         JPanel fileBody = this.genericCardBody();
         this.addGenericBodyField(fileBody, "当前模式设置", this.convertModeCards);
         fileCard.add(fileBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(fileCard, c);

         JPanel runCard = this.xtregWizardCardV130(3, "检查并转换", "运行前核对下方生成的真实 Stata 命令；原始文件保持只读，目标冲突会再次询问。");
         JPanel runBody = this.genericCardBody();
         JLabel safety = new JLabel("<html>单文件会在独立 frame 中读取并保存为 DTA；批量模式逐个处理文件。当前 Stata 数据不会因转换过程被替换。</html>");
         safety.setForeground(MUTED);
         safety.setFont(safety.getFont().deriveFont(9.8F));
         safety.setAlignmentX(0.0F);
         runBody.add(safety);
         runCard.add(runBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(runCard, c);

         GridBagConstraints filler = this.constraints(0, c.gridy + 1);
         filler.gridwidth = 2;
         filler.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), filler);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.runButton.setText(this.convertSingleMode.isSelected() ? "转换为 DTA" : "开始批量转换");
         this.runButton.setEnabled(true);
         this.rebuilding = false;
         this.updateConversionPreview();
         this.statusLabel.setText("按 3 步完成转换：选择方式 → 设置文件与读取规则 → 核对命令并运行。");
''',
"convert page task cards",
)

replace_once(
'''         var1.add(this.fieldBlock("1. 选择原始文件", this.pathChooser(this.convertInputFile, "浏览…", this::chooseConvertInput)));
''',
'''         var1.add(this.fieldBlock("原始文件", this.pathChooser(this.convertInputFile, "浏览…", this::chooseConvertInput)));
''',
"convert input label",
)
replace_once(
'''         var1.add(this.fieldBlock("2. 数据读取设置", this.convertFormatCards));
''',
'''         var1.add(this.fieldBlock("数据读取设置", this.convertFormatCards));
''',
"convert read label",
)
replace_once(
'''         var1.add(this.fieldBlock("3. 保存位置", this.pathChooser(this.convertOutputFile, "浏览…", this::chooseConvertOutput)));
''',
'''         var1.add(this.fieldBlock("DTA 保存位置", this.pathChooser(this.convertOutputFile, "浏览…", this::chooseConvertOutput)));
''',
"convert output label",
)


# Missing-value analysis: three clear tasks instead of six equal-weight rows.
replace_once(
'''\n\n优点\\n同时提供总体、分类汇总、联合明细、具体缺失记录和图形；结果直接联动右侧只读数据表。\\n\\n局限\\n''',
'''\n\n优点\\n同时提供总体、分类汇总、联合明细、具体缺失记录和图形；结果直接联动右侧当前数据表。\\n\\n局限\\n''',
"missing analysis current-data wording",
)

replace_once(
'''         int var2 = 0;
         JPanel var3 = new JPanel(new FlowLayout(0, 12, 0));
         var3.setOpaque(false);
         var3.add(this.missingAllVariables);
         var3.add(this.missingChooseVariables);
         JPanel var4 = new JPanel(new BorderLayout(0, 7));
         var4.setOpaque(false);
         var4.add(var3, "North");
         var4.add(this.listPane(this.missingVariables), "Center");
         this.addField(var2++, "检查变量", var4);
         this.addField(var2++, "如何查看缺失值", this.missingMode);
         this.addField(var2++, "分类变量（可多选）", this.listPane(this.missingGroups));
         JPanel var5 = new JPanel(new GridLayout(0, 1, 5, 5));
         var5.setOpaque(false);
         var5.add(this.missingSeparateSummary);
         var5.add(this.missingOnly);
         this.addField(var2++, "结果范围", var5);
         JPanel var6 = new JPanel(new GridLayout(1, 4, 7, 0));
         var6.setOpaque(false);
         var6.add(new JLabel("缺失变量数 ≥"));
         var6.add(this.missingMinCount);
         var6.add(new JLabel("缺失比例 ≥ (%)"));
         var6.add(this.missingMinRate);
         this.addField(var2++, "筛选阈值", var6);
         this.addField(var2++, "排序", this.missingSort);
         GridBagConstraints var7 = this.constraints(0, var2);
         var7.gridwidth = 2;
         var7.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), var7);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.runButton.setText("分析缺失值");
         this.runButton.setEnabled(Data.getVarCount() > 0);
         this.rebuilding = false;
         this.updateMissingPreview();
         this.statusLabel.setText("请选择检查变量和分类方式，然后开始分析。分析过程只读。");
''',
'''         JPanel scopeRow = new JPanel(new FlowLayout(0, 12, 0));
         scopeRow.setOpaque(false);
         scopeRow.add(this.missingAllVariables);
         scopeRow.add(this.missingChooseVariables);
         JPanel scopeChooser = new JPanel(new BorderLayout(0, 7));
         scopeChooser.setOpaque(false);
         scopeChooser.add(scopeRow, BorderLayout.NORTH);
         scopeChooser.add(this.listPane(this.missingVariables), BorderLayout.CENTER);

         JPanel resultRange = new JPanel(new GridLayout(0, 1, 5, 5));
         resultRange.setOpaque(false);
         resultRange.add(this.missingSeparateSummary);
         resultRange.add(this.missingOnly);

         JPanel thresholds = new JPanel(new GridLayout(1, 4, 7, 0));
         thresholds.setOpaque(false);
         thresholds.add(new JLabel("缺失变量数 ≥"));
         thresholds.add(this.missingMinCount);
         thresholds.add(new JLabel("缺失比例 ≥ (%)"));
         thresholds.add(this.missingMinRate);

         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.taskStepStripV153("检查范围", "分类方式", "筛选与排序"), c);

         JPanel scopeCard = this.xtregWizardCardV130(1, "检查范围", "默认检查当前数据全部变量；也可以只选择论文中需要核对的一组变量。");
         JPanel scopeBody = this.genericCardBody();
         this.addGenericBodyField(scopeBody, "检查变量", scopeChooser);
         scopeCard.add(scopeBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(scopeCard, c);

         JPanel groupCard = this.xtregWizardCardV130(2, "分类方式", "先决定总体查看还是按企业、年份等分类，再选择分类变量与结果范围。");
         JPanel groupBody = this.genericCardBody();
         this.addGenericBodyField(groupBody, "如何查看缺失值", this.missingMode);
         this.addGenericBodyField(groupBody, "分类变量（可多选）", this.listPane(this.missingGroups));
         this.addGenericBodyField(groupBody, "结果范围", resultRange);
         groupCard.add(groupBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(groupCard, c);

         JPanel filterCard = this.xtregWizardCardV130(3, "筛选与排序", "用阈值压缩结果量，再选择最适合排查问题的排序方式。");
         JPanel filterBody = this.genericCardBody();
         this.addGenericBodyField(filterBody, "筛选阈值", thresholds);
         this.addGenericBodyField(filterBody, "排序", this.missingSort);
         JLabel readOnlyHint = new JLabel("<html>分析过程只读：不会修改当前数据；运行后可从结果表定位具体缺失记录。</html>");
         readOnlyHint.setForeground(MUTED);
         readOnlyHint.setFont(readOnlyHint.getFont().deriveFont(9.8F));
         readOnlyHint.setAlignmentX(0.0F);
         filterBody.add(readOnlyHint);
         filterCard.add(filterBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(filterCard, c);

         GridBagConstraints filler = this.constraints(0, c.gridy + 1);
         filler.gridwidth = 2;
         filler.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), filler);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.runButton.setText("分析缺失值");
         this.runButton.setEnabled(Data.getVarCount() > 0);
         this.rebuilding = false;
         this.updateMissingPreview();
         this.statusLabel.setText("按 3 步完成缺失值检查：选择范围 → 分类方式 → 筛选与排序。分析过程只读。");
''',
"missing analysis task cards",
)

path.write_text(text, encoding="utf-8")
print("HX_UI_SPECIAL_DATA_PASS_OK")
