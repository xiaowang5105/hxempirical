from pathlib import Path
import re

root = Path('.')
java = root / 'src/main/java/com/hexie/stata/HxWorkbench.java'
s = java.read_text(encoding='utf-8')

# Version
s = s.replace('public static final String VERSION = "1.2.7";', 'public static final String VERSION = "1.2.8";')

helper_marker = '      private void renderCommandChooser(String var1, String var2, List<String> var3) {'
helpers = r'''      private List<String> preferredCommandsForMethod(String method, List<String> commands) {
         ArrayList<String> picks = new ArrayList<>();
         List<String> wanted;
         if ("线性模型及相关".equals(method)) {
            wanted = Arrays.asList("regress", "areg", "qreg", "correlate");
         } else if ("汇总，表格和假设检验".equals(method)) {
            wanted = Arrays.asList("summarize", "tabstat", "tabulate", "ttest");
         } else if ("二元结果".equals(method)) {
            wanted = Arrays.asList("logit", "logistic", "probit", "cloglog");
         } else if ("序数结果".equals(method)) {
            wanted = Arrays.asList("ologit", "oprobit");
         } else if ("分类结果".equals(method)) {
            wanted = Arrays.asList("mlogit", "mprobit", "asclogit");
         } else if ("计数结果".equals(method)) {
            wanted = Arrays.asList("poisson", "nbreg", "zip", "zinb");
         } else if ("分数结果".equals(method)) {
            wanted = Arrays.asList("fracreg", "betareg");
         } else if ("时间序列".equals(method)) {
            wanted = Arrays.asList("arima", "newey", "prais", "dfuller");
         } else if ("纵向/面板数据".equals(method)) {
            wanted = Arrays.asList("xtreg", "xtlogit", "xtprobit", "xtpoisson");
         } else if ("生存分析".equals(method)) {
            wanted = Arrays.asList("stset", "sts", "stcox", "streg");
         } else if ("因果推断/处理效应".equals(method)) {
            wanted = Arrays.asList("teffects", "didregress", "xtdidregress");
         } else {
            wanted = Collections.emptyList();
         }

         for (String cmd : wanted) {
            if (commands.contains(cmd) && !picks.contains(cmd)) picks.add(cmd);
         }
         if (picks.isEmpty()) {
            for (String cmd : commands) {
               picks.add(cmd);
               if (picks.size() >= Math.min(4, commands.size())) break;
            }
         }
         return picks;
      }

      private JComponent chooserMethodLead(String detail) {
         JPanel lead = new JPanel(new BorderLayout(12, 0));
         lead.setBackground(new Color(248, 251, 255));
         lead.setBorder(new EmptyBorder(10, 14, 10, 14));
         lead.setAlignmentX(0.0F);
         JLabel dot = new JLabel("●");
         dot.setForeground(new Color(54, 114, 236));
         dot.setFont(dot.getFont().deriveFont(Font.BOLD, 14.0F));
         lead.add(dot, BorderLayout.WEST);
         JLabel text = new JLabel("<html><b>这一页怎么用</b>&nbsp;&nbsp;<span style='color:#637083'>" + html(detail) + "</span></html>");
         text.setForeground(TEXT);
         text.setFont(text.getFont().deriveFont(10.5F));
         lead.add(text, BorderLayout.CENTER);
         lead.setMaximumSize(new Dimension(Integer.MAX_VALUE, 54));
         return lead;
      }

      private JButton chooserListCommandRow(String command, boolean featured) {
         CommandGuide guide = commandGuide(command);
         String title = guide == null ? command : guide.title;
         String purpose = guide == null ? "进入命令设置页查看参数。" : guide.purpose;
         String example = guide == null ? command : guide.example;
         String source = commandSource(command);
         String body;
         if (featured) {
            body = "<html><table width='960' cellpadding='0' cellspacing='0'><tr>"
               + "<td width='155'><span style='font-family:monospace;font-size:17px;color:#2b63c5'><b>" + html(command) + "</b></span><br>"
               + "<span style='font-size:9px;color:#2b63c5'>" + html(source) + "</span></td>"
               + "<td><span style='font-size:15px'><b>" + html(title) + "</b></span><br>"
               + "<span style='font-size:10px;color:#5e6d82'>" + html(purpose) + "</span><br>"
               + "<span style='font-size:9px;color:#7c8899'>示例：" + html(example) + "</span></td>"
               + "<td width='82' align='right'><span style='font-size:10px;color:#53657d'>进入设置  ›</span></td>"
               + "</tr></table></html>";
         } else {
            body = "<html><table width='960' cellpadding='0' cellspacing='0'><tr>"
               + "<td width='145'><span style='font-family:monospace;font-size:13px;color:#2b63c5'><b>" + html(command) + "</b></span></td>"
               + "<td width='215'><span style='font-size:12px'><b>" + html(title) + "</b></span></td>"
               + "<td><span style='font-size:9px;color:#5e6d82'>" + html(purpose) + "</span></td>"
               + "<td width='84' align='right'><span style='font-size:9px;color:#7c8899'>" + html(source) + "  ›</span></td>"
               + "</tr></table></html>";
         }
         JButton row = new JButton(body);
         row.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 251, 255), new Color(241, 246, 253), TEXT, SURFACE));
         row.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createMatteBorder(1, 0, 0, 0, new Color(232, 237, 244)),
            new EmptyBorder(featured ? 7 : 4, 10, featured ? 7 : 4, 10)
         ));
         row.setHorizontalAlignment(SwingConstants.LEFT);
         row.setFocusPainted(false);
         row.setContentAreaFilled(false);
         row.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         row.setMaximumSize(new Dimension(Integer.MAX_VALUE, featured ? 72 : 38));
         row.setPreferredSize(new Dimension(980, featured ? 72 : 38));
         row.addActionListener(e -> this.openCommandPage(command));
         return row;
      }

      private JComponent chooserListSection(String title, String caption, List<String> commands, boolean featured) {
         JPanel section = this.refCard();
         section.setLayout(new BorderLayout(0, 8));
         section.setAlignmentX(0.0F);
         JPanel head = new JPanel();
         head.setOpaque(false);
         head.setLayout(new BoxLayout(head, BoxLayout.Y_AXIS));
         JLabel name = new JLabel(title);
         name.setForeground(TEXT);
         name.setFont(name.getFont().deriveFont(Font.BOLD, 14.0F));
         JLabel desc = new JLabel(caption);
         desc.setForeground(MUTED);
         desc.setFont(desc.getFont().deriveFont(9.5F));
         head.add(name);
         head.add(Box.createVerticalStrut(2));
         head.add(desc);
         section.add(head, BorderLayout.NORTH);
         JPanel rows = new JPanel();
         rows.setOpaque(false);
         rows.setLayout(new BoxLayout(rows, BoxLayout.Y_AXIS));
         boolean first = true;
         for (String cmd : commands) {
            JButton row = this.chooserListCommandRow(cmd, featured);
            if (first) {
               row.setBorder(new EmptyBorder(featured ? 7 : 4, 10, featured ? 7 : 4, 10));
               first = false;
            }
            rows.add(row);
         }
         section.add(rows, BorderLayout.CENTER);
         return section;
      }

'''

if 'private JComponent chooserListSection(String title, String caption' not in s:
    if helper_marker not in s:
        raise SystemExit('renderCommandChooser marker not found')
    s = s.replace(helper_marker, helpers + helper_marker, 1)

# Replace the two-column card wall used on normal method pages with list-first layout.
pattern = re.compile(
    r'''         \} else \{\n            JPanel common = this\.refCard\(\); common\.setLayout\(new BorderLayout\(0,10\)\); common\.setAlignmentX\(0\.0F\); JLabel ct = new JLabel\("可用命令"\);.*?            common\.add\(grid,BorderLayout\.CENTER\); this\.chooserContent\.add\(common\);\n         \}\n         this\.chooserContent\.add\(Box\.createVerticalGlue\(\)\);''',
    re.S,
)
replacement = r'''         } else {
            String methodName = var2.isBlank() ? var1 : var2;
            List<String> featured = this.preferredCommandsForMethod(methodName, var3);
            LinkedHashSet<String> restSet = new LinkedHashSet<>(var3);
            restSet.removeAll(featured);
            ArrayList<String> rest = new ArrayList<>(restSet);

            this.chooserContent.add(this.chooserMethodLead(
               "先从常用命令进入；需要完整目录时继续向下浏览。当前方法常见命令：" + statsMethodPreview(methodName)
            ));
            this.chooserContent.add(Box.createVerticalStrut(10));

            if (!featured.isEmpty()) {
               this.chooserContent.add(this.chooserListSection(
                  "常用命令", "优先展示更常用、更容易上手的命令。", featured, true
               ));
               this.chooserContent.add(Box.createVerticalStrut(10));
            }
            if (!rest.isEmpty()) {
               this.chooserContent.add(this.chooserListSection(
                  featured.isEmpty() ? "可用命令" : "全部命令",
                  featured.isEmpty() ? "当前方法下可直接使用的命令。" : "完整保留该方法下的其他 Stata 命令。",
                  rest, false
               ));
            }
         }
         this.chooserContent.add(Box.createVerticalGlue());'''

s2, n = pattern.subn(replacement, s, count=1)
if n != 1 and 'chooserMethodLead(' not in s:
    raise SystemExit(f'command-grid block replacement count={n}')
if n == 1:
    s = s2

# Normal method-page copy: concise and consistent with the grouped Statistics page.
s = s.replace(
    'this.chooserHint.setText(linear ? "先选分析目的，再进入具体命令。常用命令优先展示，其余命令按类别收纳。" : "选择一个命令进入设置；常用项优先，进阶项继续向下浏览。");',
    'this.chooserHint.setText(linear ? "先选分析目的，再进入具体命令。常用命令优先展示，其余命令按类别收纳。" : "先看常用命令，再继续浏览完整命令列表。");'
)

java.write_text(s, encoding='utf-8')

ado = root / 'hxempirical.ado'
a = ado.read_text(encoding='utf-8')
a = a.replace('*! hxempirical 1.2.7  13aug2026', '*! hxempirical 1.2.8  13aug2026')
a = a.replace('display as text "版本：" as result "1.2.4"', 'display as text "版本：" as result "1.2.8"')
a = a.replace('return local version "1.2.4"', 'return local version "1.2.8"')
ado.write_text(a, encoding='utf-8')

pkg = root / 'hxempirical.pkg'
p = pkg.read_text(encoding='utf-8').replace('d Version 1.2.7', 'd Version 1.2.8')
pkg.write_text(p, encoding='utf-8')

print('method list UI patch applied')
