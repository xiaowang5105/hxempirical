from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/main/java/com/hexie/stata/HxWorkbench.java"
text = path.read_text(encoding="utf-8")

anchor = '''         String var2 = selected(this.didAction);\n         this.formPanel.removeAll();\n'''
start = text.index(anchor) + len(anchor)
end = text.index('''\n      private int addDidPanelStructure''', start)

new_block = r'''         this.enableVariableDrop(this.depvar, "结果变量");
         this.enableVariableDrop(this.variables, "控制变量");
         this.enableVariableDrop(this.didUnit, "个体变量");
         this.enableVariableDrop(this.didTime, "时间变量");
         this.enableVariableDrop(this.didTreat, "处理组变量");
         this.enableVariableDrop(this.didPost, "政策后变量");
         this.enableVariableDrop(this.didEvent, "相对政策时间");
         this.enableVariableDrop(this.didEventCode, "事件研究编码");
         this.enableVariableDrop(this.cluster, "聚类变量");

         boolean regressionStep = var2.startsWith("DID 交互回归") || var2.startsWith("事件研究回归");
         String taskTitle;
         String taskSubtitle;
         if (var2.startsWith("生成政策后")) {
            taskTitle = "生成 post";
            taskSubtitle = "用时间变量和政策发生年份生成政策后虚拟变量，并保留时间缺失值。";
         } else if (var2.startsWith("生成交互项")) {
            taskTitle = "生成 did";
            taskSubtitle = "用 treat × post 生成 DID 交互项；运行前会检查 treat/post 是否为 0/1。";
         } else if (var2.startsWith("生成相对")) {
            taskTitle = "生成 event_time";
            taskSubtitle = "以政策发生年份为 0，生成直观的政策前后相对时间。";
         } else if (var2.startsWith("生成事件研究编码")) {
            taskTitle = "生成 event_code";
            taskSubtitle = "选择 event_time 与真实存在的基准期，自动生成 Stata 因子变量可用的非负编码。";
         } else if (var2.startsWith("DID 交互回归")) {
            taskTitle = "DID 模型设定";
            taskSubtitle = "集中设置核心变量、面板结构、固定效应、控制变量和推断方式。";
         } else if (var2.startsWith("事件研究回归")) {
            taskTitle = "事件研究设定";
            taskSubtitle = "使用已生成的 event_code 设置动态效应回归，并保留基准期信息。";
         } else {
            taskTitle = "政策前联合检验";
            taskSubtitle = "根据 event_code 的生成记录自动识别政策前非基准期，并生成 testparm。";
         }

         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.taskStepStripV153("选择步骤", taskTitle, regressionStep ? "样本与运行" : "检查运行"), c);

         JPanel actionCard = this.xtregWizardCardV130(1, "选择步骤", "一次只完成一个 DID / Event Study 动作；切换后页面立即只保留该动作需要的字段。");
         JPanel actionBody = this.genericCardBody();
         this.addGenericBodyField(actionBody, "当前要做什么", this.didAction);
         actionCard.add(actionBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(actionCard, c);

         JPanel taskCard = this.xtregWizardCardV130(2, taskTitle, taskSubtitle);
         JPanel taskBody = this.genericCardBody();

         if (var2.startsWith("生成政策后")) {
            if (this.didNewVar.getText().isBlank()) this.didNewVar.setText("post");
            JPanel row = new JPanel(new GridLayout(1, 3, 9, 0));
            row.setOpaque(false);
            row.add(this.labeled("时间变量（如 year）", this.didTime));
            row.add(this.labeled("政策发生年份", this.didPolicyTime));
            row.add(this.labeled("新变量名", this.didNewVar));
            this.addGenericBodyField(taskBody, "生成规则", row);
         } else if (var2.startsWith("生成交互项")) {
            if (this.didNewVar.getText().isBlank()) this.didNewVar.setText("did");
            JPanel row = new JPanel(new GridLayout(1, 3, 9, 0));
            row.setOpaque(false);
            row.add(this.labeled("处理组 treat（0/1）", this.didTreat));
            row.add(this.labeled("政策后 post（0/1）", this.didPost));
            row.add(this.labeled("新变量名", this.didNewVar));
            this.addGenericBodyField(taskBody, "交互项规则", row);
         } else if (var2.startsWith("生成相对")) {
            if (this.didNewVar.getText().isBlank()) this.didNewVar.setText("event_time");
            JPanel row = new JPanel(new GridLayout(1, 3, 9, 0));
            row.setOpaque(false);
            row.add(this.labeled("时间变量（如 year）", this.didTime));
            row.add(this.labeled("政策发生年份", this.didPolicyTime));
            row.add(this.labeled("新变量名", this.didNewVar));
            this.addGenericBodyField(taskBody, "相对时间规则", row);
         } else if (var2.startsWith("生成事件研究编码")) {
            if (this.didNewVar.getText().isBlank() || Arrays.asList("post", "did", "event_time").contains(this.didNewVar.getText().trim())) {
               this.didNewVar.setText("event_code");
            }
            JPanel row = new JPanel(new GridLayout(1, 3, 9, 0));
            row.setOpaque(false);
            row.add(this.labeled("相对政策时间 event_time", this.didEvent));
            row.add(this.labeled("基准期（原始相对时间）", this.didBasePeriod));
            row.add(this.labeled("新编码变量名", this.didNewVar));
            this.addGenericBodyField(taskBody, "编码规则", row);
            JLabel hint = new JLabel("<html>工具先确认基准期确实存在，再自动平移编码；回归时继续使用原始基准期含义，无需手算编码值。</html>");
            hint.setForeground(MUTED);
            hint.setFont(hint.getFont().deriveFont(9.8F));
            hint.setAlignmentX(0.0F);
            taskBody.add(hint);
         } else if (regressionStep) {
            JPanel core = new JPanel(new GridLayout(1, 3, 9, 0));
            core.setOpaque(false);
            core.add(this.labeled("结果变量 Y", this.depvar));
            core.add(this.labeled("处理组 treat（0/1）", this.didTreat));
            if (var2.startsWith("事件研究回归")) {
               core.add(this.labeled("事件研究编码 event_code", this.didEventCode));
            } else {
               core.add(this.labeled("政策后 post（0/1）", this.didPost));
            }
            this.addGenericBodyField(taskBody, var2.startsWith("事件研究回归") ? "事件研究核心变量" : "DID 核心变量", core);

            JPanel panelAndFe = new JPanel();
            panelAndFe.setOpaque(false);
            panelAndFe.setLayout(new BoxLayout(panelAndFe, BoxLayout.Y_AXIS));
            JPanel panelGrid = new JPanel(new GridLayout(1, 2, 9, 0));
            panelGrid.setOpaque(false);
            panelGrid.add(this.labeled("个体变量（如 firm）", this.didUnit));
            panelGrid.add(this.labeled("时间变量（如 year）", this.didTime));
            panelGrid.setAlignmentX(0.0F);
            panelAndFe.add(panelGrid);
            panelAndFe.add(Box.createVerticalStrut(8));
            JPanel feRow = new JPanel(new FlowLayout(0, 14, 0));
            feRow.setOpaque(false);
            feRow.add(this.didUnitFE);
            feRow.add(this.didTimeFE);
            feRow.setAlignmentX(0.0F);
            panelAndFe.add(feRow);
            this.addGenericBodyField(taskBody, "面板结构与固定效应", panelAndFe);

            if (var2.startsWith("事件研究回归")) {
               JLabel baseHint = new JLabel("<html>event_code 请先由“生成事件研究编码”步骤创建；基准期信息已经随编码记录，回归时无需再次换算。</html>");
               baseHint.setForeground(MUTED);
               baseHint.setFont(baseHint.getFont().deriveFont(9.8F));
               baseHint.setAlignmentX(0.0F);
               taskBody.add(baseHint);
               taskBody.add(Box.createVerticalStrut(8));
            }

            this.addGenericBodyField(taskBody, "控制变量（可多选）", this.listPane(this.variables));
            boolean clustered = "cluster".equals(selected(this.vce));
            JPanel modelRow = new JPanel(new GridLayout(1, clustered ? 3 : 2, 9, 0));
            modelRow.setOpaque(false);
            modelRow.add(this.labeled("估计方法", this.didEstimator));
            modelRow.add(this.labeled("标准误", this.vce));
            if (clustered) modelRow.add(this.labeled("聚类变量", this.cluster));
            this.addGenericBodyField(taskBody, "估计与推断", modelRow);
         } else {
            JPanel row = new JPanel(new GridLayout(1, 2, 9, 0));
            row.setOpaque(false);
            row.add(this.labeled("处理组 treat（0/1）", this.didTreat));
            row.add(this.labeled("事件研究编码 event_code", this.didEventCode));
            this.addGenericBodyField(taskBody, "自动识别政策前交互项", row);
            JLabel hint = new JLabel("<html>工具根据 event_code 的生成记录、平移量和基准期自动生成 testparm；无需复制或手写系数名。</html>");
            hint.setForeground(MUTED);
            hint.setFont(hint.getFont().deriveFont(9.8F));
            hint.setAlignmentX(0.0F);
            taskBody.add(hint);
         }
         taskCard.add(taskBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(taskCard, c);

         JPanel runCard = this.xtregWizardCardV130(3, regressionStep ? "样本与运行" : "检查运行",
            regressionStep ? "最后补充样本条件和低频估计选项，并在下方核对真实 Stata 命令。" : "运行前在下方核对自动生成的真实 Stata 命令；完成后新变量会自动带入后续步骤。");
         JPanel runBody = this.genericCardBody();
         if (regressionStep) {
            this.addGenericBodyField(runBody, "样本条件 if（可选）", this.ifCondition);
            this.addGenericBodyField(runBody, "更多估计选项（可选）", this.options);
         } else {
            JLabel runHint = new JLabel("<html>当前步骤的命令会显示在下方命令区。点击“运行当前步骤”后，成功生成的 post、event_time 或 event_code 会自动填入后续对应位置。</html>");
            runHint.setForeground(MUTED);
            runHint.setFont(runHint.getFont().deriveFont(9.8F));
            runHint.setAlignmentX(0.0F);
            runBody.add(runHint);
         }
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
         this.updateDidBuilderPreview();
         this.statusLabel.setText("DID 当前按“选择步骤 → 当前任务 → 检查运行”组织；共同政策时点设定下，双向固定效应和按个体聚类继续作为常用默认项。");
      }
'''

text = text[:start] + new_block + text[end:]
path.write_text(text, encoding="utf-8")
print("HX_UI_DID_BUILDER_PASS_OK")
