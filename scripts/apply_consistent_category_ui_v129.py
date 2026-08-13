from pathlib import Path
import re

root = Path('.')
java = root / 'src/main/java/com/hexie/stata/HxWorkbench.java'
s = java.read_text(encoding='utf-8')

s = s.replace('public static final String VERSION = "1.2.8";', 'public static final String VERSION = "1.2.9";')
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.2.7");', 'SFIToolkit.displayln("HxWorkbench 1.2.9");')
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.2.8");', 'SFIToolkit.displayln("HxWorkbench 1.2.9");')

old_sidebar = '''      private void syncSidebarFromContext() {
         String key = "home";
         if ("data".equals(this.activeCategoryCode)) key = "data";
         else if ("reg".equals(this.activeCategoryCode)) key = "reg";
         else if ("stats".equals(this.activeCategoryCode) || "post".equals(this.activeCategoryCode) || "graph".equals(this.activeCategoryCode)) key = "stats";
         else if ("oneclick".equals(this.activeCategoryCode)) key = "oneclick";'''
new_sidebar = '''      private void syncSidebarFromContext() {
         String key = "home";
         if ("data".equals(this.activeCategoryCode)) key = "data";
         else if ("stats".equals(this.activeCategoryCode) || "reg".equals(this.activeCategoryCode) || "post".equals(this.activeCategoryCode)) key = "stats";
         else if ("graph".equals(this.activeCategoryCode)) key = "graph";
         else if ("oneclick".equals(this.activeCategoryCode) || "did".equals(this.activeCategoryCode)) key = "oneclick";'''
if old_sidebar not in s:
    raise SystemExit('syncSidebarFromContext block not found')
s = s.replace(old_sidebar, new_sidebar, 1)

marker = '      private JButton statsMethodRow(String number, String method, Color accent) {'
if marker not in s:
    raise SystemExit('statsMethodRow marker not found')

helpers = r'''      private static String graphMethodPreview(String method) {
         switch (method) {
            case "二维图(散点图，折线图等)": return "twoway · scatter · line · connected";
            case "条形图": return "graph bar · graph hbar";
            case "点图": return "graph dot · dotplot";
            case "饼图": return "graph pie";
            case "直方图": return "histogram";
            case "箱线图": return "graph box · graph hbox";
            case "等高线图": return "twoway contour";
            case "散点图矩阵": return "graph matrix";
            case "分布图": return "histogram · kdensity";
            case "平滑和密度": return "kdensity · lowess · lpoly";
            case "回归诊断图": return "rvfplot · rvpplot · avplot";
            case "时间序列图": return "tsline";
            case "面板数据折线图": return "xtline";
            case "生存分析图": return "sts graph";
            case "ROC分析": return "roctab · rocfit · roccomp";
            case "多元分析图": return "pca · factor · cluster";
            case "质量控制": return "质量控制相关图形";
            case "更多统计图形": return "marginsplot · 更多统计图形";
            case "图形组合": return "graph combine";
            case "管理图形": return "graph display · graph save · graph export";
            case "更改方案/大小": return "set scheme · graph set";
            default: return "查看该分类下的 Stata 图形命令";
         }
      }

      private static String dataMethodPreview(String method) {
         switch (method) {
            case "导入与转换": return "Excel · CSV · TXT → DTA";
            case "数据检查": return "misstable · duplicates";
            case "变量处理": return "generate · replace · encode · winsor2";
            case "样本处理": return "keep · drop · if · in";
            case "合并与追加": return "merge · append";
            case "数据结构": return "reshape · collapse · xtset · tsset";
            default: return "查看该分类下的 Stata 命令";
         }
      }

      private static String genericMethodPreview(String category, String method) {
         if ("graph".equals(category)) return graphMethodPreview(method);
         if ("data".equals(category)) return dataMethodPreview(method);
         if ("stats".equals(category)) return statsMethodPreview(method);
         return methodSummary(method);
      }

      private JButton groupedMethodRow(String category, String number, String method, String preview, Color accent) {
         JButton row = new JButton(
            "<html><table width='930' cellpadding='0' cellspacing='0'><tr>"
               + "<td width='58'><span style='color:#7b8aa3'>" + html(number) + "</span></td>"
               + "<td width='315'><b>" + html(method) + "</b></td>"
               + "<td><span style='font-family:monospace;color:#65758f'>" + html(preview) + "</span></td>"
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
         row.addActionListener(e -> this.browseMethod(category, method));
         return row;
      }

      private JComponent groupedCategoryBand(String category, String title, String subtitle, Color accent, String[] methods, List<String> available, int groupNo) {
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
               rows.add(this.groupedMethodRow(category, groupNo + "." + itemNo, method, genericMethodPreview(category, method), accent));
               itemNo++;
            }
         }
         group.add(rows, BorderLayout.CENTER);
         group.setMaximumSize(new Dimension(Integer.MAX_VALUE, 46 + Math.max(1, itemNo - 1) * 34));
         return group;
      }

      private JComponent groupedOverviewSearch(String tooltip) {
         JPanel searchLine = new JPanel(new BorderLayout(10, 0));
         searchLine.setOpaque(false);
         searchLine.setBorder(new EmptyBorder(0, 0, 8, 0));
         JTextField find = new JTextField();
         styleTextField(find);
         find.setToolTipText(tooltip);
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
         return searchLine;
      }

      private void finishGroupedOverview() {
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
         this.syncSidebarFromContext();
      }

      private void renderGraphGroupedOverview(List<String> available) {
         this.setChooserBreadcrumb("首页  >  图形");
         this.chooserTitle.setText("图形");
         this.chooserHint.setText("按 Stata 原图形分类浏览；大类只负责视觉分组，小项保持 Stata 的原始顺序与名称。");
         this.chooserContent.removeAll();
         this.chooserContent.add(this.groupedOverviewSearch("搜索图形方法或命令"));

         Object[][] groups = new Object[][]{
            {"基础图形", "二维图、条形图、点图、饼图与常见分布图", new Color(54, 114, 236), new String[]{"二维图(散点图，折线图等)", "条形图", "点图", "饼图", "直方图", "箱线图", "等高线图", "散点图矩阵"}},
            {"分布与平滑", "分布展示、密度估计与平滑关系", new Color(35, 169, 105), new String[]{"分布图", "平滑和密度"}},
            {"模型与诊断", "回归、时间序列、面板、生存与 ROC 图形", new Color(128, 92, 220), new String[]{"回归诊断图", "时间序列图", "面板数据折线图", "生存分析图", "ROC分析"}},
            {"多元与统计图", "多元分析、质量控制及其他统计图形", new Color(235, 151, 39), new String[]{"多元分析图", "质量控制", "更多统计图形"}},
            {"组合与管理", "组合、保存、导出及图形方案设置", new Color(222, 92, 112), new String[]{"图形组合", "管理图形", "更改方案/大小"}}
         };

         int groupNo = 1;
         for (Object[] spec : groups) {
            this.chooserContent.add(this.groupedCategoryBand("graph", (String)spec[0], (String)spec[1], (Color)spec[2], (String[])spec[3], available, groupNo++));
            this.chooserContent.add(Box.createVerticalStrut(10));
         }
         this.finishGroupedOverview();
      }

      private void renderDataGroupedOverview(List<String> available) {
         this.setChooserBreadcrumb("首页  >  数据");
         this.chooserTitle.setText("数据");
         this.chooserHint.setText("按数据处理任务浏览；常用 Stata 命令直接显示在小项右侧。");
         this.chooserContent.removeAll();
         this.chooserContent.add(this.groupedOverviewSearch("搜索数据处理方法或命令"));

         Object[][] groups = new Object[][]{
            {"导入与检查", "先把数据读进来，再检查缺失与重复", new Color(54, 114, 236), new String[]{"导入与转换", "数据检查"}},
            {"变量与样本", "生成变量、清洗变量以及筛选样本", new Color(35, 169, 105), new String[]{"变量处理", "样本处理"}},
            {"合并与结构", "合并数据并设置宽长表、面板与时间结构", new Color(128, 92, 220), new String[]{"合并与追加", "数据结构"}}
         };

         int groupNo = 1;
         for (Object[] spec : groups) {
            this.chooserContent.add(this.groupedCategoryBand("data", (String)spec[0], (String)spec[1], (Color)spec[2], (String[])spec[3], available, groupNo++));
            this.chooserContent.add(Box.createVerticalStrut(10));
         }
         this.finishGroupedOverview();
      }

      private void renderCompactGroupedOverview(String category, String title, List<String> methods) {
         this.setChooserBreadcrumb("首页  >  " + title);
         this.chooserTitle.setText(title);
         this.chooserHint.setText("选择具体方法进入下一步；统一采用列表式导航。");
         this.chooserContent.removeAll();
         this.chooserContent.add(this.groupedOverviewSearch("搜索方法或命令"));
         JPanel section = new JPanel(new BorderLayout());
         section.setBackground(SURFACE);
         section.setAlignmentX(0.0F);
         JLabel head = new JLabel("可用方法");
         head.setForeground(TEXT);
         head.setFont(head.getFont().deriveFont(Font.BOLD, 14.0F));
         head.setBorder(new EmptyBorder(10, 14, 8, 14));
         section.add(head, BorderLayout.NORTH);
         JPanel rows = new JPanel();
         rows.setBackground(SURFACE);
         rows.setLayout(new BoxLayout(rows, BoxLayout.Y_AXIS));
         int i = 1;
         for (String method : methods) {
            rows.add(this.groupedMethodRow(category, Integer.toString(i++), method, genericMethodPreview(category, method), new Color(54, 114, 236)));
         }
         section.add(rows, BorderLayout.CENTER);
         this.chooserContent.add(section);
         this.finishGroupedOverview();
      }

'''

if 'private void renderGraphGroupedOverview(List<String> available)' not in s:
    s = s.replace(marker, helpers + marker, 1)

stats_branch = '''         if ("stats".equals(var1)) {
            this.renderStatsGroupedOverview(var2);
            return;
         }
'''
new_branches = stats_branch + '''
         if ("graph".equals(var1)) {
            this.renderGraphGroupedOverview(var2);
            return;
         }

         if ("data".equals(var1)) {
            this.renderDataGroupedOverview(var2);
            return;
         }
'''
if stats_branch not in s:
    raise SystemExit('stats browse branch not found')
s = s.replace(stats_branch, new_branches, 1)

pattern = re.compile(
    r'''         this\.setChooserBreadcrumb\("开始  >  " \+ this\.activeCategoryName\);\n         this\.chooserTitle\.setText\(this\.activeCategoryName\);\n         this\.chooserHint\.setText\("选择具体方法，再比较该方法下可用的 Stata 命令。"\);\n         this\.chooserContent\.removeAll\(\);\n         int var9 = var2\.size\(\) <= 4 \? 1 : 2;\n         JPanel var4 = new JPanel\(new GridLayout\(0, var9, 10, 10\)\);\n         var4\.setOpaque\(false\);\n         int var5 = Math\.max\(1, \(var2\.size\(\) \+ var9 - 1\) / var9\);\n         var4\.setPreferredSize\(new Dimension\(800, var5 \* 82\)\);\n         var4\.setMaximumSize\(new Dimension\(Integer\.MAX_VALUE, var5 \* 82\)\);\n\n         for \(String var7 : var2\) \{\n            JButton var8 = this\.homeTaskButton\(var7, methodSummary\(var7\), "did"\.equals\(var1\) \|\| "oneclick"\.equals\(var1\)\);\n            var8\.setPreferredSize\(new Dimension\(320, 72\)\);\n            var8\.addActionListener\(var3x -> this\.browseMethod\(var1, var7\)\);\n            var4\.add\(var8\);\n         \}\n\n         if \(var2\.size\(\) % var9 != 0\) \{\n            JPanel var10 = new JPanel\(\);\n            var10\.setOpaque\(false\);\n            var4\.add\(var10\);\n         \}\n\n         this\.chooserContent\.add\(var4\);\n         this\.chooserReady = true;\n         this\.chooserContent\.revalidate\(\);\n         this\.chooserContent\.repaint\(\);\n         this\.chooserAtCategoryLevel = true;\n         this\.configureChooserBack\(\);''',
    re.S,
)
replacement = '''         this.renderCompactGroupedOverview(var1, this.activeCategoryName, var2);'''
s2, n = pattern.subn(replacement, s, count=1)
if n != 1:
    raise SystemExit(f'generic card-wall replacement count={n}')
s = s2

java.write_text(s, encoding='utf-8')

ado = root / 'hxempirical.ado'
a = ado.read_text(encoding='utf-8')
a = a.replace('*! hxempirical 1.2.8  13aug2026', '*! hxempirical 1.2.9  13aug2026')
a = a.replace('display as text "版本：" as result "1.2.8"', 'display as text "版本：" as result "1.2.9"')
a = a.replace('return local version "1.2.8"', 'return local version "1.2.9"')
ado.write_text(a, encoding='utf-8')

pkg = root / 'hxempirical.pkg'
p = pkg.read_text(encoding='utf-8').replace('d Version 1.2.8', 'd Version 1.2.9')
pkg.write_text(p, encoding='utf-8')

print('consistent category UI v1.2.9 patch applied')
