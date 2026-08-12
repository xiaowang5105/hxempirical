from pathlib import Path

p=Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s=p.read_text(encoding='utf-8')


def method_span(src, signature):
    start=src.find(signature)
    if start<0: raise SystemExit('missing '+signature)
    brace=src.find('{',start); depth=0; i=brace; state='code'
    while i<len(src):
        ch=src[i]; nx=src[i+1] if i+1<len(src) else ''
        if state=='code':
            if ch=='"': state='string'
            elif ch=="'": state='char'
            elif ch=='/' and nx=='/': state='line'; i+=1
            elif ch=='/' and nx=='*': state='block'; i+=1
            elif ch=='{': depth+=1
            elif ch=='}':
                depth-=1
                if depth==0: return start,i+1
        elif state=='string':
            if ch=='\\': i+=1
            elif ch=='"': state='code'
        elif state=='char':
            if ch=='\\': i+=1
            elif ch=="'": state='code'
        elif state=='line':
            if ch=='\n': state='code'
        elif state=='block':
            if ch=='*' and nx=='/': state='code'; i+=1
        i+=1
    raise SystemExit('unclosed '+signature)


def replace_method(src,signature,repl):
    a,b=method_span(src,signature)
    return src[:a]+repl.rstrip()+src[b:]

# dedicated linear stage
anchor='         this.stageCards.add(this.buildChooserContainer(), "chooser");\n'
if '"linear_exact"' not in s:
    s=s.replace(anchor,anchor+'         this.stageCards.add(this.buildExactLinearContainer(), "linear_exact");\n',1)

helpers=r'''
      private JPanel exactLinearStep(String number, String title, String detail, Color color) {
         JPanel row=new JPanel(new BorderLayout(10,0)); row.setOpaque(false);
         JLabel n=new JLabel(number,SwingConstants.CENTER); n.setOpaque(true); n.setBackground(color); n.setForeground(Color.WHITE); n.setFont(n.getFont().deriveFont(Font.BOLD,12.0F)); n.setPreferredSize(new Dimension(30,30));
         JPanel text=new JPanel(); text.setOpaque(false); text.setLayout(new BoxLayout(text,BoxLayout.Y_AXIS));
         JLabel a=new JLabel(title); a.setForeground(TEXT); a.setFont(a.getFont().deriveFont(Font.BOLD,11.0F));
         JLabel d=new JLabel("<html><div style='width:145px;color:#718096'>"+html(detail)+"</div></html>"); d.setFont(d.getFont().deriveFont(9.5F));
         text.add(a); text.add(Box.createVerticalStrut(6)); text.add(d); row.add(n,BorderLayout.WEST); row.add(text,BorderLayout.CENTER); return row;
      }

      private JComponent exactLinearMainCard(String glyph, String command, String title, String desc, String example, Color accent) {
         JPanel card=new JPanel(null); card.setBackground(SURFACE); card.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220,228,239),9),new EmptyBorder(0,0,0,0)));
         JLabel icon=new JLabel(glyph,SwingConstants.CENTER); icon.setOpaque(true); icon.setBackground(new Color(Math.min(255,accent.getRed()+210),Math.min(255,accent.getGreen()+210),Math.min(255,accent.getBlue()+210))); icon.setForeground(accent); icon.setFont(icon.getFont().deriveFont(Font.BOLD,24.0F)); icon.setBounds(16,13,66,64); card.add(icon);
         JLabel cmd=new JLabel(command); cmd.setForeground(accent); cmd.setFont(new Font("Monospaced",Font.BOLD,12)); cmd.setBounds(98,12,220,20); card.add(cmd);
         JLabel name=new JLabel(title); name.setForeground(TEXT); name.setFont(name.getFont().deriveFont(Font.BOLD,13.0F)); name.setBounds(98,32,250,22); card.add(name);
         JLabel detail=new JLabel(desc); detail.setForeground(MUTED); detail.setFont(detail.getFont().deriveFont(9.5F)); detail.setBounds(98,55,300,20); card.add(detail);
         JLabel ex=new JLabel("示例：  "+example); ex.setOpaque(true); ex.setBackground(new Color(Math.min(255,accent.getRed()+225),Math.min(255,accent.getGreen()+225),Math.min(255,accent.getBlue()+225))); ex.setForeground(accent); ex.setFont(new Font("Monospaced",Font.PLAIN,9)); ex.setBounds(98,78,325,23); card.add(ex);
         JButton enter=this.refButton("进入设置",true); enter.setBounds(438,22,82,34); enter.addActionListener(e->this.openCommandPage(command)); card.add(enter);
         return card;
      }

      private JComponent exactLinearGroup(String glyph, String title, String[][] entries, Color accent) {
         JPanel card=new JPanel(null); card.setBackground(SURFACE); card.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(225,231,240),8),new EmptyBorder(0,0,0,0)));
         JLabel icon=new JLabel(glyph,SwingConstants.CENTER); icon.setForeground(accent); icon.setFont(icon.getFont().deriveFont(Font.BOLD,18.0F)); icon.setBounds(13,9,30,28); card.add(icon);
         JLabel h=new JLabel(title); h.setForeground(TEXT); h.setFont(h.getFont().deriveFont(Font.BOLD,11.0F)); h.setBounds(45,10,190,24); card.add(h);
         int y=43;
         for(String[] e:entries){ JButton b=new JButton("<html><b>"+html(e[0])+"</b>&nbsp;&nbsp;<span style='color:#6e7b91'>"+html(e[1])+"</span>&nbsp;›</html>"); b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE,new Color(249,251,254),new Color(242,246,251),TEXT,SURFACE)); b.setBorder(new EmptyBorder(2,5,2,5)); b.setHorizontalAlignment(SwingConstants.LEFT); b.setFocusPainted(false); b.setContentAreaFilled(false); b.setBounds(10,y,245,28); String cmd=e[0]; b.addActionListener(ev->this.openCommandPage(cmd)); card.add(b); y+=29; }
         return card;
      }

      private JComponent buildExactLinearContainer() {
         JPanel root=new JPanel(null); root.setBackground(APP_BG); root.setPreferredSize(new Dimension(1450,840));
         JLabel crumb=new JLabel("首页   /   回归   /   线性模型"); crumb.setForeground(new Color(84,107,144)); crumb.setFont(crumb.getFont().deriveFont(10.5F)); crumb.setBounds(30,17,430,24); root.add(crumb);
         JLabel title=new JLabel("线性模型"); title.setForeground(TEXT); title.setFont(title.getFont().deriveFont(Font.BOLD,27.0F)); title.setBounds(30,47,260,38); root.add(title);
         JLabel sub=new JLabel("先选分析目的，再进入具体命令。常用命令优先展示，其余命令按类别收纳。"); sub.setForeground(MUTED); sub.setFont(sub.getFont().deriveFont(11.0F)); sub.setBounds(30,85,650,25); root.add(sub);
         JButton back=this.refButton("←  返回上一级",false); back.setBounds(955,25,145,40); back.addActionListener(e->this.showHomePage()); root.add(back);
         JButton home=this.refButton("⌂  首页",false); home.setBounds(1115,25,100,40); home.addActionListener(e->this.showHomePage()); root.add(home);
         JButton help=this.refButton("?  帮助",false); help.setBounds(1230,25,100,40); help.addActionListener(e->this.openHelp()); root.add(help);

         JPanel search=this.refCard(); search.setLayout(null); search.setBounds(30,120,1115,58); JTextField find=new JTextField(); styleTextField(find); find.setToolTipText("搜索命令或分析目的，如 固定效应、分位数、工具变量"); find.setBounds(16,10,675,38); search.add(find); JButton all=this.refButton("全部",true); all.setBounds(715,10,78,38); search.add(all); JButton common=this.refButton("常用",false); common.setBounds(798,10,78,38); search.add(common); JButton advanced=this.refButton("进阶",false); advanced.setBounds(881,10,78,38); search.add(advanced); JButton filter=this.refButton("▽  筛选排序",false); filter.setBounds(980,10,115,38); search.add(filter); root.add(search);

         JPanel recommend=this.refCard(); recommend.setLayout(new BoxLayout(recommend,BoxLayout.Y_AXIS)); recommend.setBounds(1165,124,240,640); JLabel rt=new JLabel("▥  推荐路径"); rt.setForeground(TEXT); rt.setFont(rt.getFont().deriveFont(Font.BOLD,14.0F)); rt.setAlignmentX(0.0F); recommend.add(rt); recommend.add(Box.createVerticalStrut(24)); recommend.add(this.exactLinearStep("1","先用常用命令","从常用命令入手，快速完成基础分析。",new Color(34,109,246))); recommend.add(Box.createVerticalStrut(28)); recommend.add(this.exactLinearStep("2","看示例与说明","查看示例与说明，理解命令用法与适用场景。",new Color(31,169,105))); recommend.add(Box.createVerticalStrut(28)); recommend.add(this.exactLinearStep("3","再进入进阶命令","根据需求选择进阶命令，满足更复杂的分析。",new Color(116,83,224))); recommend.add(Box.createVerticalGlue()); JPanel tip=new JPanel(new BorderLayout()); tip.setBackground(new Color(255,250,241)); tip.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(255,219,166),9),new EmptyBorder(13,13,13,13))); tip.add(new JLabel("<html><b><span style='color:#f59e0b'>☼ 小贴士</span></b><br><br><span style='color:#68758b'>命令太多时，优先从常用命令开始，逐步深入更高阶方法！</span></html>"),BorderLayout.CENTER); tip.setMaximumSize(new Dimension(Integer.MAX_VALUE,140)); recommend.add(tip); root.add(recommend);

         JPanel choose=this.refCard(); choose.setLayout(null); choose.setBackground(new Color(246,250,255)); choose.setBounds(30,190,1115,56); JLabel how=new JLabel("●  怎么选？"); how.setForeground(TEXT); how.setFont(how.getFont().deriveFont(Font.BOLD,14.0F)); how.setBounds(16,9,120,36); choose.add(how); JButton c1=this.refButton("↗  普通 OLS  → regress",false); c1.setBounds(140,9,198,36); c1.addActionListener(e->this.openCommandPage("regress")); choose.add(c1); JButton c2=this.refButton("♟  单组固定效应  → areg",false); c2.setBounds(350,9,202,36); c2.addActionListener(e->this.openCommandPage("areg")); choose.add(c2); JButton c3=this.refButton("▱  多维固定效应  → reghdfe",false); c3.setBounds(565,9,220,36); c3.addActionListener(e->this.openCommandPage("reghdfe")); choose.add(c3); JButton c4=this.refButton("⌁  关注分布位置  → qreg",false); c4.setBounds(800,9,210,36); c4.addActionListener(e->this.openCommandPage("qreg")); choose.add(c4); root.add(choose);

         JPanel commonCard=this.refCard(); commonCard.setLayout(null); commonCard.setBounds(30,258,1115,300); JLabel ct=new JLabel("常用命令"); ct.setForeground(TEXT); ct.setFont(ct.getFont().deriveFont(Font.BOLD,14.0F)); ct.setBounds(16,8,120,25); commonCard.add(ct); JComponent m1=this.exactLinearMainCard("↗","regress","普通线性回归","用 OLS 估计连续因变量与解释变量的线性关系。","regress y x c1 c2, vce(robust)",new Color(54,114,236)); m1.setBounds(16,42,525,112); commonCard.add(m1); JComponent m2=this.exactLinearMainCard("♟","areg","单组固定效应","在回归中吸收一组大量类别固定效应。","areg y x c, absorb(firm)",new Color(29,164,101)); m2.setBounds(557,42,525,112); commonCard.add(m2); JComponent m3=this.exactLinearMainCard("▱","reghdfe","高维固定效应回归","高效吸收多组固定效应并支持聚类标准误。","reghdfe y x c, absorb(firm year) vce(cluster firm)",new Color(245,125,30)); m3.setBounds(16,165,525,112); commonCard.add(m3); JComponent m4=this.exactLinearMainCard("⌁","qreg","分位数回归","估计解释变量对条件分布不同分位点的影响。","qreg y x c, quantile(.5)",new Color(134,84,225)); m4.setBounds(557,165,525,112); commonCard.add(m4); root.add(commonCard);

         JPanel more=this.refCard(); more.setLayout(null); more.setBounds(30,570,1115,218); JLabel mt=new JLabel("更多线性模型"); mt.setForeground(TEXT); mt.setFont(mt.getFont().deriveFont(Font.BOLD,14.0F)); mt.setBounds(16,6,150,25); more.add(mt); JComponent g1=this.exactLinearGroup("◆","稳健与异常值处理",new String[][]{{"rreg","稳健回归（M-估计）"},{"cnsreg","截面回归（修正离群影响）"},{"newey","Newey-West 标准误"}},new Color(47,104,213)); g1.setBounds(16,36,260,160); more.add(g1); JComponent g2=this.exactLinearGroup("⚖","加权与广义最小二乘",new String[][]{{"regressw","加权最小二乘"},{"vwls","可变加权最小二乘"},{"gls","广义最小二乘"},{"prais","可行广义最小二乘"}},new Color(37,172,92)); g2.setBounds(287,36,260,160); more.add(g2); JComponent g3=this.exactLinearGroup("⚑","工具变量与内生性",new String[][]{{"ivregress","工具变量回归"},{"ivreg","2SLS 回归"},{"ivprobit","工具变量 Probit"},{"control","控制函数法"}},new Color(245,128,30)); g3.setBounds(558,36,260,160); more.add(g3); JComponent g4=this.exactLinearGroup("▦","其他线性扩展",new String[][]{{"sureg","联立方程回归"},{"seemingly","似不相关回归"},{"seemingly2","似不相关回归（扩展）"},{"ml","最大似然回归"}},new Color(132,85,220)); g4.setBounds(829,36,260,160); more.add(g4); JLabel expand=new JLabel("展开更多命令类别⌄",SwingConstants.CENTER); expand.setForeground(ACCENT); expand.setFont(expand.getFont().deriveFont(10.0F)); expand.setBounds(430,196,250,20); more.add(expand); root.add(more);
         return root;
      }

      private void showExactLinearPage() {
         this.activeCategoryCode="reg"; this.activeCategoryName="回归"; this.activeMethodName="线性模型"; this.chooserReady=false; this.setSidebarActive("reg"); this.inspectorToggle.setVisible(false); this.stageLayout.show(this.stageCards,"linear_exact"); this.statusLabel.setText("数据检查不停歇保障数据质量，仅用于质量评估与诊断。");
      }
'''
if 'private JComponent buildExactLinearContainer()' not in s:
    marker='      private JComponent buildChooserContainer() {'
    pos=s.find(marker)
    if pos<0: raise SystemExit('chooser marker missing')
    s=s[:pos]+helpers+'\n'+s[pos:]

# intercept only the exact linear directory; other methods keep generic chooser
sig='      private void browseMethod(String var1, String var2)'
a,b=method_span(s,sig)
body=s[a:b]
if 'showExactLinearPage' not in body:
    brace=body.find('{')+1
    body=body[:brace]+'\n         if ("reg".equals(var1) && "线性模型".equals(var2)) { this.showExactLinearPage(); return; }'+body[brace:]
    s=s[:a]+body+s[b:]

# home vertical alignment refinement
s=s.replace('hero.setBounds(25, 105, 975, 210)', 'hero.setBounds(25, 120, 988, 210)')
s=s.replace('data.setBounds(1015, 105, 425, 235)', 'data.setBounds(1030, 120, 410, 235)')
s=s.replace('common.setBounds(25, 335, 975, 300)', 'common.setBounds(25, 350, 988, 300)')
s=s.replace('recent.setBounds(1015, 355, 425, 280)', 'recent.setBounds(1030, 370, 410, 280)')
s=s.replace('more.setBounds(25, 655, 1415, 176)', 'more.setBounds(25, 670, 1415, 166)')
s=s.replace('moreGrid.setBounds(16,43,1383,108)', 'moreGrid.setBounds(16,43,1383,98)')

# oneclick block vertical alignment refinement
for old,new in [
('scenario.setBounds(16,108,745,52)','scenario.setBounds(16,115,745,49)'),
('quick.setBounds(16,170,745,130)','quick.setBounds(16,174,745,130)'),
('settings.setBounds(16,310,745,270)','settings.setBounds(16,312,745,270)'),
('explain.setBounds(16,590,745,96)','explain.setBounds(16,595,745,96)'),
('command.setBounds(16,696,745,106)','command.setBounds(16,704,745,106)'),
('data.setBounds(780,108,400,694)','data.setBounds(780,115,405,695)'),
('recommend.setBounds(1195,108,245,694)','recommend.setBounds(1200,115,240,695)')]:
    s=s.replace(old,new)

p.write_text(s,encoding='utf-8')
print('HX_PIXEL_MATCH_121_REFINE_OK')
