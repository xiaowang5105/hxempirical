from pathlib import Path

p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')

# Version bump.
s = s.replace('public static final String VERSION = "1.2.6";', 'public static final String VERSION = "1.2.7";')
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.2.6");', 'SFIToolkit.displayln("HxWorkbench 1.2.7");')
s = s.replace('new JLabel("版本：1.2.6")', 'new JLabel("版本：1.2.7")')

# Preview mode should reflect the complete Stata Statistics taxonomy.
old_preview = '''         } else if ("stats".equals(var0)) {
            return Arrays.asList("描述统计", "相关分析", "均值检验", "频数列联");'''
new_preview = '''         } else if ("stats".equals(var0)) {
            return Arrays.asList(
               "汇总，表格和假设检验", "线性模型及相关", "二元结果", "序数结果", "分类结果", "计数结果", "分数结果", "广义线性模型", "选择模型",
               "时间序列", "多元时间序列", "空间自回归模型", "纵向/面板数据", "多层混合效应模型", "生存分析", "流行病学及相关", "内生协变量", "样本选择模型",
               "因果推断/处理效应", "结构方程模型(SEM)", "潜在类别分析(LCA)", "有限混合模型(FMM)", "项目反应理论(IRT)", "多元分析", "调查数据分析",
               "Lasso回归", "Meta分析", "多重插补", "非参数分析", "精确统计", "重抽样", "效能，精度和样品含量", "贝叶斯分析", "贝叶斯模型平均"
            );'''
if old_preview not in s:
    raise SystemExit('stats preview anchor not found')
s = s.replace(old_preview, new_preview, 1)

# Add the grouped statistics renderer before browseCategoryOverview.
anchor = '''      private void browseCategoryOverview(String var1) {'''
if anchor not in s:
    raise SystemExit('browseCategoryOverview anchor not found')
helpers = r'''      private static String statsMethodPreview(String method) {
         switch (method) {
            case "汇总，表格和假设检验": return "summarize · tabstat · tabulate · ttest";
            case "线性模型及相关": return "regress · areg · qreg · correlate";
            case "二元结果": return "logit · logistic · probit · cloglog";
            case "序数结果": return "ologit · oprobit";
            case "分类结果": return "mlogit · mprobit · asclogit";
            case "计数结果": return "poisson · nbreg · zinb";
            case "分数结果": return "fracreg · betareg";
            case "广义线性模型": return "glm";
            case "选择模型": return "heckman · heckprobit · heckpoisson";
            case "时间序列": return "arima · newey · prais · dfuller";
            case "多元时间序列": return "var · svar · vec · irf";
            case "空间自回归模型": return "spregress · spivregress · spxtregress";
            case "纵向/面板数据": return "xtreg · xtlogit · xtprobit · xtpoisson";
            case "多层混合效应模型": return "mixed · melogit · meprobit · mepoisson";
            case "生存分析": return "stset · sts · stcox · streg";
            case "流行病学及相关": return "cc · cs · ir";
            case "内生协变量": return "eregress · eprobit · eoprobit · epoisson";
            case "样本选择模型": return "heckman · heckprobit · heckoprobit";
            case "因果推断/处理效应": return "teffects · didregress · xtdidregress";
            case "结构方程模型(SEM)": return "sem · gsem";
            case "潜在类别分析(LCA)": return "gsem";
            case "有限混合模型(FMM)": return "fmm";
            case "项目反应理论(IRT)": return "irt";
            case "多元分析": return "factor · pca · manova · cluster";
            case "调查数据分析": return "svy";
            case "Lasso回归": return "lasso · elasticnet · sqrtlasso";
            case "Meta分析": return "meta";
            case "多重插补": return "mi";
            case "非参数分析": return "npregress · kdensity · lowess · lpoly";
            case "精确统计": return "bitesti · tabi";
            case "重抽样": return "bootstrap · jackknife · permute · simulate";
            case "效能，精度和样品含量": return "power";
            case "贝叶斯分析": return "bayes · bayesmh · bayespredict";
            case "贝叶斯模型平均": return "bma";
            default: return "查看该分类下的 Stata 命令";
         }
      }

      private JButton statsMethodRow(String number, String method, Color accent) {
         String commands = statsMethodPreview(method);
         JButton row = new JButton(
            "<html><table width='930' cellpadding='0' cellspacing='0'><tr>"
               + "<td width='58'><span style='color:#7b8aa3'>" + html(number) + "</span></td>"
               + "<td width='315'><b>" + html(method) + "</b></td>"
               + "<td><span style='font-family:monospace;color:#65758f'>" + html(commands) + "</span></td>"
               + "<td width='22'><span style='color:#607089'>›</span></td>"
               + "</tr></table></html>"
         );
         row.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 251, 255), new Color(241, 246, 253), TEXT, SURFACE));
         row.setBorder(BorderFactory.createCompoundBorder(BorderFactory.createMatteBorder(1, 0, 0, 0, new Color(232, 237, 244)), new EmptyBorder(2, 10, 2, 10)));
         row.setHorizontalAlignment(SwingConstants.LEFT);
         row.setFocusPainted(false);
         row.setContentAreaFilled(false);
         row.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         row.setMaximumSize(new Dimension(Integer.MAX_VALUE, 34));
         row.setPreferredSize(new Dimension(960, 34));
         row.addActionListener(e -> this.browseMethod("stats", method));
         return row;
      }

      private JComponent statsGroupBand(String title, String subtitle, Color accent, String[] methods, List<String> available, int groupNo) {
         JPanel group = new JPanel(new BorderLayout());
         group.setBackground(SURFACE);
         group.setBorder(new EmptyBorder(0, 0, 0, 0));
         group.setAlignmentX(0.0F);

         JPanel head = new JPanel(new BorderLayout(12, 0));
         head.setBackground(new Color(249, 251, 254));
         head.setBorder(new EmptyBorder(10, 14, 9, 14));
         JLabel dot = new JLabel("●");
         dot.setForeground(accent);
         dot.setFont(dot.getFont().deriveFont(Font.BOLD, 15.0F));
         head.add(dot, BorderLayout.WEST);
         JPanel text = new JPanel();
         text.setOpaque(false);
         text.setLayout(new BoxLayout(text, BoxLayout.X_AXIS));
         JLabel name = new JLabel(title);
         name.setForeground(TEXT);
         name.setFont(name.getFont().deriveFont(Font.BOLD, 15.0F));
         JLabel desc = new JLabel("   " + subtitle);
         desc.setForeground(MUTED);
         desc.setFont(desc.getFont().deriveFont(10.5F));
         text.add(name);
         text.add(desc);
         head.add(text, BorderLayout.CENTER);
         group.add(head, BorderLayout.NORTH);

         JPanel rows = new JPanel();
         rows.setBackground(SURFACE);
         rows.setLayout(new BoxLayout(rows, BoxLayout.Y_AXIS));
         int itemNo = 1;
         for (String method : methods) {
            if (available.isEmpty() || available.contains(method)) {
               rows.add(this.statsMethodRow(groupNo + "." + itemNo, method, accent));
               itemNo++;
            }
         }
         group.add(rows, BorderLayout.CENTER);
         group.setMaximumSize(new Dimension(Integer.MAX_VALUE, 46 + Math.max(1, itemNo - 1) * 34));
         return group;
      }

      private void renderStatsGroupedOverview(List<String> available) {
         this.setChooserBreadcrumb("首页  >  统计");
         this.chooserTitle.setText("统计");
         this.chooserHint.setText("按 Stata 原分类浏览；大类只负责视觉分组，小项保持 Stata 的原始顺序与名称。");
         this.chooserContent.removeAll();

         JPanel searchLine = new JPanel(new BorderLayout(10, 0));
         searchLine.setOpaque(false);
         searchLine.setBorder(new EmptyBorder(0, 0, 8, 0));
         JTextField find = new JTextField();
         styleTextField(find);
         find.setToolTipText("搜索统计方法或命令");
         find.setPreferredSize(new Dimension(620, 36));
         JButton go = this.refButton("搜索", false);
         ActionListener doSearch = e -> {
            String q = find.getText().trim();
            if (!q.isBlank()) {
               this.searchField.setText(q);
               this.smartHomeSearch();
            }
         };
         find.addActionListener(doSearch);
         go.addActionListener(doSearch);
         searchLine.add(find, BorderLayout.CENTER);
         searchLine.add(go, BorderLayout.EAST);
         searchLine.setMaximumSize(new Dimension(Integer.MAX_VALUE, 48));
         searchLine.setAlignmentX(0.0F);
         this.chooserContent.add(searchLine);

         Object[][] groups = new Object[][]{
            {"描述与比较", "汇总、表格和假设检验", new Color(54, 114, 236), new String[]{"汇总，表格和假设检验"}},
            {"回归与模型", "常见结果变量、广义模型与选择模型", new Color(35, 169, 105), new String[]{"线性模型及相关", "二元结果", "序数结果", "分类结果", "计数结果", "分数结果", "广义线性模型", "选择模型"}},
            {"时间与面板数据", "时间序列、空间、纵向与多层数据", new Color(128, 92, 220), new String[]{"时间序列", "多元时间序列", "空间自回归模型", "纵向/面板数据", "多层混合效应模型"}},
            {"进阶与结构", "生存、流行病学、内生性与样本选择", new Color(235, 151, 39), new String[]{"生存分析", "流行病学及相关", "内生协变量", "样本选择模型"}},
            {"因果与结构模型", "处理效应、SEM、潜在类别与多元分析", new Color(222, 92, 112), new String[]{"因果推断/处理效应", "结构方程模型(SEM)", "潜在类别分析(LCA)", "有限混合模型(FMM)", "项目反应理论(IRT)", "多元分析", "调查数据分析"}},
            {"扩展方法", "正则化、插补、重抽样、效能与贝叶斯", new Color(57, 145, 183), new String[]{"Lasso回归", "Meta分析", "多重插补", "非参数分析", "精确统计", "重抽样", "效能，精度和样品含量", "贝叶斯分析", "贝叶斯模型平均"}}
         };

         int groupNo = 1;
         for (Object[] spec : groups) {
            JComponent band = this.statsGroupBand((String)spec[0], (String)spec[1], (Color)spec[2], (String[])spec[3], available, groupNo++);
            this.chooserContent.add(band);
            this.chooserContent.add(Box.createVerticalStrut(10));
         }
         this.chooserContent.add(Box.createVerticalGlue());
         this.chooserReady = true;
         this.chooserAtCategoryLevel = true;
         this.configureChooserBack();
         this.homeButton.setVisible(true);
         this.homeButton.setEnabled(true);
         this.inspectorToggle.setVisible(false);
         this.chooserContent.revalidate();
         this.chooserContent.repaint();
         this.stageLayout.show(this.stageCards, "chooser");
      }

'''
s = s.replace(anchor, helpers + anchor, 1)

# Route Statistics to the grouped renderer after the registry supplies the native method list.
old_route = '''         this.setChooserBreadcrumb("开始  >  " + this.activeCategoryName);
         this.chooserTitle.setText(this.activeCategoryName);'''
new_route = '''         if ("stats".equals(var1)) {
            this.renderStatsGroupedOverview(var2);
            return;
         }

         this.setChooserBreadcrumb("开始  >  " + this.activeCategoryName);
         this.chooserTitle.setText(this.activeCategoryName);'''
if old_route not in s:
    raise SystemExit('category render route anchor not found')
s = s.replace(old_route, new_route, 1)

# Replace the large recommendation rail with a compact tip-only rail.
container_anchor = '''      private JComponent buildChooserContainer() {'''
if container_anchor not in s:
    raise SystemExit('chooser container anchor not found')
tip_method = r'''      private JPanel buildChooserTipPanel() {
         JPanel right = this.refCard();
         right.setLayout(new BoxLayout(right, BoxLayout.Y_AXIS));
         right.setPreferredSize(new Dimension(190, 0));
         right.setMaximumSize(new Dimension(190, Integer.MAX_VALUE));
         JLabel title = new JLabel("☼  小贴士");
         title.setForeground(new Color(225, 133, 18));
         title.setFont(title.getFont().deriveFont(Font.BOLD, 12.5F));
         title.setAlignmentX(0.0F);
         right.add(title);
         right.add(Box.createVerticalStrut(12));
         JLabel text = new JLabel("<html><div style='width:145px;color:#718096'>命令太多时，先从常用命令开始，再逐步深入。</div></html>");
         text.setFont(text.getFont().deriveFont(10.0F));
         text.setAlignmentX(0.0F);
         right.add(text);
         right.add(Box.createVerticalGlue());
         return right;
      }

'''
s = s.replace(container_anchor, tip_method + container_anchor, 1)
s = s.replace('root.add(this.buildChooserRecommendationPanel(), BorderLayout.EAST);', 'root.add(this.buildChooserTipPanel(), BorderLayout.EAST);', 1)

p.write_text(s, encoding='utf-8')

# Keep package/help/readme version labels synchronized.
for fn in ['hxempirical.ado', 'hxempirical.pkg', 'hxempirical.sthlp', 'hxtoolbox.sthlp', 'README.md']:
    q = Path(fn)
    if q.exists():
        q.write_text(q.read_text(encoding='utf-8').replace('1.2.6', '1.2.7'), encoding='utf-8')
