from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/main/java/com/hexie/stata/HxWorkbench.java"
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    text = text.replace(old, new, 1)


# 1) Add dedicated preview entry points for the two remaining special pages.
replace_once(
'''            && !"--render-graph-preview".equals(var0[0])
            && !"--render-did-preview".equals(var0[0])
''',
'''            && !"--render-graph-preview".equals(var0[0])
            && !"--render-test-preview".equals(var0[0])
            && !"--render-performance-preview".equals(var0[0])
            && !"--render-did-preview".equals(var0[0])
''',
"preview allowlist",
)
replace_once(
'''               if (var11) {
                  var19x.populateGraphPreviewState();
               }

               if (var12) {
''',
'''               if (var11) {
                  var19x.populateGraphPreviewState();
               }

               if ("--render-test-preview".equals(var0[0])) {
                  var19x.showSpecialPage("test");
               }

               if ("--render-performance-preview".equals(var0[0])) {
                  var19x.showSpecialPage("performance");
               }

               if (var12) {
''',
"preview dispatch",
)

# 2) Add a compact two-step strip for immediate-action special pages.
marker = '''      private void showSpecialPage(String var1) {
'''
helper = r'''      private JComponent specialStepStripV153(String step1, String tip1, String step2, String tip2) {
         JPanel strip = cardPanel();
         strip.setBackground(SURFACE);
         strip.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 11),
            new EmptyBorder(9, 10, 9, 10)
         ));
         String[][] steps = new String[][]{
            {"1", step1, tip1},
            {"2", step2, tip2}
         };
         strip.setLayout(new GridLayout(1, 2, 8, 0));
         for (int i = 0; i < steps.length; i++) {
            JPanel p = new JPanel(new BorderLayout(6, 0));
            p.setOpaque(false);
            p.setMinimumSize(new Dimension(0, 0));
            p.add(this.xtregCircleBadge(steps[i][0], i == 0, 24), BorderLayout.WEST);
            JLabel label = new JLabel("<html><b>" + html(steps[i][1]) + "</b></html>");
            label.setForeground(TEXT);
            label.setFont(label.getFont().deriveFont(10.5F));
            label.setToolTipText(steps[i][2]);
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

# 3) Rebuild the test-data/performance content while retaining showSpecialPage's existing setup/cleanup shell.
method_start = text.index(marker)
body_start = text.index('         int var2 = 0;\n', method_start)
body_end = text.index('         GridBagConstraints var11 = this.constraints(0, var2);', body_start)
new_body = r'''         int var2 = 0;
         GridBagConstraints specialC = new GridBagConstraints();
         specialC.gridx = 0;
         specialC.gridy = 0;
         specialC.weightx = 1.0;
         specialC.fill = GridBagConstraints.HORIZONTAL;
         specialC.insets = new Insets(0, 0, 10, 0);

         if (var1.equals("test")) {
            this.setWorkspaceBreadcrumb("测试数据");
            this.commandTitle.setText("测试数据 · 选择一份练习数据开始");
            this.exampleLabel.setText("按用途选择数据；按钮点击后立即载入，并在右侧显示真实数据。");
            this.insightArea.setText(
               "测试数据用于熟悉工作台和 Stata 命令。横截面数据适合基础统计与回归；面板数据适合 xt 系列命令；merge / append 练习表用于数据合并。\n\n载入操作会替换当前内存数据，正式数据请先保存。"
            );
            this.formPanel.add(this.specialStepStripV153(
               "选择练习数据", "按当前要练习的任务选择横截面、面板或合并数据",
               "载入后检查", "右侧检查变量与观测，并在 Stata History 中确认执行命令"
            ), specialC);

            JPanel chooseCard = this.xtregWizardCardV130(1, "选择练习数据", "按研究任务分组；第一次使用建议从 auto 开始。");
            JPanel chooseBody = this.genericCardBody();

            JPanel crossSection = new JPanel(new GridLayout(1, 2, 8, 8));
            crossSection.setOpaque(false);
            String[][] crossData = new String[][]{
               {"汽车横截面 auto", "auto"},
               {"劳动数据 nlsw88", "nlsw88"}
            };
            for (String[] item : crossData) {
               JButton button = new JButton(item[0]);
               if ("auto".equals(item[1])) stylePrimaryButton(button); else styleSecondaryButton(button);
               button.addActionListener(event -> this.runUtility("hxtestdata " + item[1], true));
               crossSection.add(button);
            }
            this.addGenericBodyField(chooseBody, "横截面 / 常规练习", crossSection);

            JPanel panelData = new JPanel(new GridLayout(1, 3, 8, 8));
            panelData.setOpaque(false);
            for (String[] item : new String[][]{
               {"长面板 nlswork", "nlswork"},
               {"企业面板 grunfeld", "grunfeld"},
               {"工会面板 union", "union"}
            }) {
               JButton button = new JButton(item[0]);
               styleSecondaryButton(button);
               button.addActionListener(event -> this.runUtility("hxtestdata " + item[1], true));
               panelData.add(button);
            }
            this.addGenericBodyField(chooseBody, "面板数据", panelData);

            JPanel mergeData = new JPanel(new GridLayout(1, 2, 8, 8));
            mergeData.setOpaque(false);
            for (String[] item : new String[][]{
               {"创建 merge 练习表", "merge"},
               {"创建 append 练习表", "append"}
            }) {
               JButton button = new JButton(item[0]);
               styleSecondaryButton(button);
               button.addActionListener(event -> this.runUtility("hxtestdata " + item[1], true));
               mergeData.add(button);
            }
            this.addGenericBodyField(chooseBody, "数据合并练习", mergeData);

            JLabel overwriteHint = new JLabel("<html><b>数据安全：</b>载入练习数据会替换当前内存数据。正式数据请先保存；执行命令会写入 Stata History。</html>");
            overwriteHint.setForeground(new Color(143, 91, 24));
            overwriteHint.setFont(overwriteHint.getFont().deriveFont(9.8F));
            overwriteHint.setAlignmentX(0.0F);
            chooseBody.add(overwriteHint);
            chooseCard.add(chooseBody, BorderLayout.CENTER);
            specialC.gridy++;
            this.formPanel.add(chooseCard, specialC);

            JPanel checkCard = this.xtregWizardCardV130(2, "载入后的检查", "载入完成后只需要确认数据是否符合下一步任务。");
            JPanel checkBody = this.genericCardBody();
            JLabel checkText = new JLabel(
               "<html>① 右侧“当前数据”确认变量名、观测数和数据结构；&nbsp;&nbsp;② 面板数据建议继续到 xtset / xtreg；&nbsp;&nbsp;③ merge / append 练习表继续到对应数据处理页面。</html>"
            );
            checkText.setForeground(MUTED);
            checkText.setAlignmentX(0.0F);
            checkBody.add(checkText);
            checkCard.add(checkBody, BorderLayout.CENTER);
            specialC.gridy++;
            this.formPanel.add(checkCard, specialC);
            var2 = specialC.gridy + 1;
         } else {
            this.setWorkspaceBreadcrumb("性能设置");
            this.commandTitle.setText("性能设置 · Stata/MP 处理器");
            this.exampleLabel.setText("通常保持许可证允许的处理器上限；需要单线程复现时临时切换为 1 个处理器。");
            this.insightArea.setText(
               "这里控制 Stata/MP 当前使用的处理器数量。开启会使用许可证允许的上限；关闭会设置为 1 个处理器。\n\n处理器数量只影响能够并行利用 CPU 的计算；每次切换都会进入 Stata History，便于复现。"
            );
            this.formPanel.add(this.specialStepStripV153(
               "选择处理器策略", "在许可证上限和单线程之间切换",
               "确认当前状态", "查看 Stata 当前处理器设置并核对 History"
            ), specialC);

            JPanel strategyCard = this.xtregWizardCardV130(1, "处理器策略", "常规估计建议保持许可证上限；单线程主要用于复现或排查性能差异。");
            JPanel strategyBody = this.genericCardBody();
            JPanel strategyButtons = new JPanel(new GridLayout(1, 2, 8, 8));
            strategyButtons.setOpaque(false);
            JButton maxButton = new JButton("使用许可证处理器上限");
            JButton oneButton = new JButton("切换为 1 个处理器");
            stylePrimaryButton(maxButton);
            styleSecondaryButton(oneButton);
            maxButton.addActionListener(event -> this.runUtility("hxthreads on", false));
            oneButton.addActionListener(event -> this.runUtility("hxthreads off", false));
            strategyButtons.add(maxButton);
            strategyButtons.add(oneButton);
            this.addGenericBodyField(strategyBody, "当前要采用的策略", strategyButtons);
            JLabel perfHint = new JLabel("<html>提示：处理器更多并不保证每个命令都按相同比例提速；具体取决于 Stata 命令本身是否支持并行计算。</html>");
            perfHint.setForeground(MUTED);
            perfHint.setFont(perfHint.getFont().deriveFont(9.8F));
            perfHint.setAlignmentX(0.0F);
            strategyBody.add(perfHint);
            strategyCard.add(strategyBody, BorderLayout.CENTER);
            specialC.gridy++;
            this.formPanel.add(strategyCard, specialC);

            JPanel statusCard = this.xtregWizardCardV130(2, "确认当前状态", "切换后检查实际处理器设置；状态查询同样写入 Stata History。");
            JPanel statusBody = this.genericCardBody();
            JButton statusButton = new JButton("查看当前处理器状态");
            styleSecondaryButton(statusButton);
            statusButton.addActionListener(event -> this.runUtility("hxthreads status", false));
            this.addGenericBodyField(statusBody, "状态检查", statusButton);
            JLabel historyHint = new JLabel("<html>所有切换与状态查询都通过 HX 命令执行，可在 Stata History 中复查。</html>");
            historyHint.setForeground(MUTED);
            historyHint.setAlignmentX(0.0F);
            statusBody.add(historyHint);
            statusCard.add(statusBody, BorderLayout.CENTER);
            specialC.gridy++;
            this.formPanel.add(statusCard, specialC);
            var2 = specialC.gridy + 1;
         }

'''
text = text[:body_start] + new_body + text[body_end:]

path.write_text(text, encoding="utf-8")
print("HX_UI_SPECIAL_PASS4_OK")
