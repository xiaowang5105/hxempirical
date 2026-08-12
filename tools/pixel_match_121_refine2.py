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
                if depth==0:return start,i+1
        elif state=='string':
            if ch=='\\':i+=1
            elif ch=='"':state='code'
        elif state=='char':
            if ch=='\\':i+=1
            elif ch=="'":state='code'
        elif state=='line':
            if ch=='\n':state='code'
        elif state=='block':
            if ch=='*' and nx=='/':state='code';i+=1
        i+=1
    raise SystemExit('unclosed '+signature)

def replace_method(src, sig, repl):
    a,b=method_span(src,sig); return src[:a]+repl.rstrip()+src[b:]

# display proxies for OneClick multi-selects
anchor='      private final JTextField exactOneClickOtherOptions = new JTextField();\n'
if 'exactOneClickCandidatesDisplay' not in s:
    s=s.replace(anchor,anchor+'      private final JTextField exactOneClickCandidatesDisplay = new JTextField();\n      private final JTextField exactOneClickRequiredDisplay = new JTextField();\n',1)

# reusable chooser dialog and selected-text sync
helpers=r'''
      private void chooseExactOneClickValues(JList<String> source, JTextField display, String title) {
         DefaultListModel<String> model=new DefaultListModel<>();
         for(int i=0;i<source.getModel().getSize();i++) model.addElement(source.getModel().getElementAt(i));
         JList<String> list=new JList<>(model); list.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION); list.setVisibleRowCount(Math.min(10,Math.max(4,model.size()))); setListSelectedValues(list,source.getSelectedValuesList());
         int rc=JOptionPane.showConfirmDialog(this,softScroll(list),title,JOptionPane.OK_CANCEL_OPTION,JOptionPane.PLAIN_MESSAGE);
         if(rc==JOptionPane.OK_OPTION){ setListSelectedValues(source,list.getSelectedValuesList()); display.setText(String.join("  ",list.getSelectedValuesList())); this.updateOneClickPreview(); }
      }

      private JComponent exactEmptyDataIllustration() {
         return new JComponent(){
            @Override protected void paintComponent(Graphics g0){
               super.paintComponent(g0); Graphics2D g=(Graphics2D)g0.create(); g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
               int w=getWidth(),h=getHeight(); int cx=w/2;
               g.setColor(new Color(242,247,255)); g.fillOval(cx-86,h/2-45,172,92);
               g.setColor(new Color(219,234,255)); g.fillRoundRect(cx-56,h/2-2,112,45,11,11);
               g.setColor(new Color(86,149,245)); g.fillRoundRect(cx-45,h/2-20,90,62,10,10);
               g.setColor(new Color(119,174,248)); g.fillRoundRect(cx-57,h/2-29,53,23,7,7);
               g.setColor(Color.WHITE); g.fillRect(cx-19,h/2-40,35,35); g.setColor(new Color(182,205,241)); g.drawLine(cx-14,h/2-29,cx+10,h/2-29); g.drawLine(cx-14,h/2-22,cx+8,h/2-22); g.drawLine(cx-14,h/2-15,cx+4,h/2-15);
               g.setColor(new Color(67,132,239)); int[] xs={cx+58,cx+86,cx+68}; int[] ys={h/2-46,h/2-61,h/2-31}; g.fillPolygon(xs,ys,3);
               g.setStroke(new BasicStroke(1.4f,BasicStroke.CAP_ROUND,BasicStroke.JOIN_ROUND,1f,new float[]{5f,5f},0f)); g.drawArc(cx+20,h/2-40,55,38,190,170);
               g.dispose();
            }
         };
      }
'''
if 'chooseExactOneClickValues' not in s:
    marker='      private JComponent buildExactOneClickContainer() {'
    pos=s.find(marker)
    if pos<0:raise SystemExit('oneclick builder marker missing')
    s=s[:pos]+helpers+'\n'+s[pos:]

# replace exact OneClick container with closer controls/layout
one=r'''      private JComponent buildExactOneClickContainer() {
         JPanel root = new JPanel(null); root.setBackground(APP_BG); root.setPreferredSize(new Dimension(1467,840)); this.exactOneClickRoot = root;
         JLabel crumb = new JLabel("首页   /   OneClick 专区   /   控制变量组合筛选   /   oneclick"); crumb.setForeground(new Color(91,111,144)); crumb.setFont(crumb.getFont().deriveFont(10.5F)); crumb.setBounds(20,12,620,24); root.add(crumb);
         JLabel title = new JLabel("控制变量组合筛选 · 外部 OneClick"); title.setForeground(TEXT); title.setFont(title.getFont().deriveFont(Font.BOLD,22.0F)); title.setBounds(20,42,520,32); root.add(title);
         JLabel sub = new JLabel("本页用于调用外部 oneclick 命令。你只需选择 Y、核心 X、候选控制变量和模型方法，工具将自动为你组装命令。"); sub.setForeground(MUTED); sub.setFont(sub.getFont().deriveFont(10.0F)); sub.setBounds(20,75,720,24); root.add(sub);
         JButton back = this.refButton("←  返回上一级", false); back.setBounds(995,20,140,38); back.addActionListener(e -> this.browseMethodCategory("oneclick")); root.add(back);
         JButton home = this.refButton("⌂  首页", false); home.setBounds(1145,20,105,38); home.addActionListener(e -> this.showHomePage()); root.add(home);
         JButton help = this.refButton("?  查看帮助", false); help.setBounds(1260,20,120,38); help.addActionListener(e -> this.openHelp()); root.add(help);

         JPanel scenario = this.refCard(); scenario.setLayout(new FlowLayout(FlowLayout.LEFT,12,0)); scenario.setBounds(16,115,745,49); JLabel sc = new JLabel("?  适合什么场景？"); sc.setForeground(TEXT); sc.setFont(sc.getFont().deriveFont(Font.BOLD,13.0F)); scenario.add(sc); scenario.add(this.refButton("控制变量筛选", false)); scenario.add(this.refButton("稳健性比较", false)); scenario.add(this.refButton("外部命令调用", false)); root.add(scenario);

         JPanel quick = this.refCard(); quick.setLayout(null); quick.setBounds(16,174,745,130); JLabel qt = new JLabel("快速理解 OneClick"); qt.setForeground(TEXT); qt.setFont(qt.getFont().deriveFont(Font.BOLD,13.0F)); qt.setBounds(14,8,200,22); quick.add(qt);
         String[][] q = {{"01","选择核心变量：Y、核心 X","确定因变量与核心解释变量。"},{"02","添加候选控制变量","从当前数据中选择候选控制变量。"},{"03","选择模型方法并运行","工具组装命令并运行外部 oneclick。"}};
         for(int i=0;i<3;i++){ int x=14+i*238; JPanel step=new JPanel(new BorderLayout(8,0)); step.setBackground(SURFACE); step.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220,228,239),8),new EmptyBorder(10,10,10,10))); step.setBounds(x,38,220,70); JLabel n=new JLabel(q[i][0],SwingConstants.CENTER); n.setOpaque(true); n.setBackground(new Color(34,109,246)); n.setForeground(Color.WHITE); n.setFont(n.getFont().deriveFont(Font.BOLD,12.0F)); n.setPreferredSize(new Dimension(31,31)); JPanel txt=new JPanel(); txt.setOpaque(false); txt.setLayout(new BoxLayout(txt,BoxLayout.Y_AXIS)); JLabel a=new JLabel(q[i][1]); a.setForeground(TEXT); a.setFont(a.getFont().deriveFont(Font.BOLD,10.5F)); JLabel d=new JLabel("<html><span style='font-size:8px;color:#718096'>"+html(q[i][2])+"</span></html>"); txt.add(a); txt.add(Box.createVerticalStrut(4)); txt.add(d); step.add(n,BorderLayout.WEST); step.add(txt,BorderLayout.CENTER); quick.add(step); if(i<2){ JLabel ar=new JLabel("→",SwingConstants.CENTER); ar.setForeground(new Color(170,188,215)); ar.setFont(ar.getFont().deriveFont(Font.BOLD,20.0F)); ar.setBounds(x+218,55,20,25); quick.add(ar);} }
         JLabel history = new JLabel("ⓘ  运行后命令会写入 Stata History。"); history.setForeground(MUTED); history.setFont(history.getFont().deriveFont(9.0F)); history.setBounds(14,108,300,18); quick.add(history); root.add(quick);

         JPanel settings = this.refCard(); settings.setLayout(null); settings.setBounds(16,312,745,270); JLabel st = new JLabel("⚙  参数设置"); st.setForeground(TEXT); st.setFont(st.getFont().deriveFont(Font.BOLD,13.0F)); st.setBounds(14,8,150,22); settings.add(st);
         styleCombo(this.oneClickY); styleCombo(this.oneClickX); styleTextField(this.exactOneClickModelOptions); styleTextField(this.exactOneClickOtherOptions); styleTextField(this.exactOneClickCandidatesDisplay); styleTextField(this.exactOneClickRequiredDisplay); this.exactOneClickCandidatesDisplay.setEditable(false); this.exactOneClickRequiredDisplay.setEditable(false);
         JLabel ly=new JLabel("因变量  Y"); ly.setForeground(TEXT); ly.setBounds(14,42,100,22); settings.add(ly); this.oneClickY.setBounds(145,40,220,32); settings.add(this.oneClickY);
         JLabel lx=new JLabel("核心解释变量  X"); lx.setForeground(TEXT); lx.setBounds(385,42,120,22); settings.add(lx); this.oneClickX.setBounds(505,40,220,32); settings.add(this.oneClickX);
         JLabel lc=new JLabel("候选控制变量"); lc.setForeground(TEXT); lc.setBounds(14,82,110,22); settings.add(lc); this.exactOneClickCandidatesDisplay.setBounds(145,80,545,32); settings.add(this.exactOneClickCandidatesDisplay); JButton cp=this.refButton("⌄",false); cp.setBounds(694,80,31,32); cp.addActionListener(e->this.chooseExactOneClickValues(this.oneClickCandidates,this.exactOneClickCandidatesDisplay,"选择候选控制变量")); settings.add(cp);
         JLabel lr=new JLabel("固定变量 fix(x) required"); lr.setForeground(TEXT); lr.setBounds(14,121,130,22); settings.add(lr); this.exactOneClickRequiredDisplay.setBounds(145,119,545,32); settings.add(this.exactOneClickRequiredDisplay); JButton rp=this.refButton("⌄",false); rp.setBounds(694,119,31,32); rp.addActionListener(e->this.chooseExactOneClickValues(this.oneClickRequired,this.exactOneClickRequiredDisplay,"选择固定变量")); settings.add(rp);
         JLabel lp=new JLabel("显著性水平 p(#)"); lp.setForeground(TEXT); lp.setBounds(14,162,120,22); settings.add(lp); JPanel pButtons=new JPanel(new GridLayout(1,3,0,0)); pButtons.setOpaque(false); pButtons.setBounds(145,158,190,34); ButtonGroup pGroup=new ButtonGroup(); String[] pv={"0.01","0.05","0.10"}; for(int i=0;i<3;i++){ final int idx=i; JToggleButton b=new JToggleButton(pv[i]); styleSecondaryButton(b); b.setSelected(i==1); b.addActionListener(e->{this.oneClickP.setSelectedIndex(idx);this.updateOneClickPreview();}); pGroup.add(b); pButtons.add(b);} settings.add(pButtons);
         JLabel lm=new JLabel("模型方法 m(method)"); lm.setForeground(TEXT); lm.setBounds(385,162,130,22); settings.add(lm); JPanel mButtons=new JPanel(new GridLayout(1,4,5,0)); mButtons.setOpaque(false); mButtons.setBounds(505,158,220,34); ButtonGroup mGroup=new ButtonGroup(); String[] mv={"reg","reghdfe","logit","probit"}; String[] internal={"regress","reghdfe","logit","probit"}; for(int i=0;i<4;i++){ final int idx=i; JToggleButton b=new JToggleButton(mv[i]); if(i==0) stylePrimaryButton(b); else styleSecondaryButton(b); b.setSelected(i==0); b.addActionListener(e->{this.oneClickEstimator.setSelectedItem(internal[idx]);this.updateOneClickConditionalFields();this.updateOneClickPreview();}); mGroup.add(b); mButtons.add(b);} settings.add(mButtons);
         JLabel lo=new JLabel("可选模型附加项  [o]"); lo.setForeground(TEXT); lo.setBounds(14,202,130,22); settings.add(lo); this.exactOneClickModelOptions.setBounds(145,199,220,32); settings.add(this.exactOneClickModelOptions);
         JLabel lz=new JLabel("其他选项  [z]"); lz.setForeground(TEXT); lz.setBounds(385,202,110,22); settings.add(lz); this.exactOneClickOtherOptions.setBounds(505,199,220,32); settings.add(this.exactOneClickOtherOptions);
         JLabel info=new JLabel("ⓘ  候选控制变量应先由理论、文献和识别设计确定，组合检验用于稳健性比较。"); info.setOpaque(true); info.setBackground(new Color(240,246,255)); info.setForeground(new Color(73,101,151)); info.setFont(info.getFont().deriveFont(9.0F)); info.setBounds(14,237,711,24); settings.add(info); root.add(settings);

         JPanel explain = this.refCard(); explain.setLayout(new BorderLayout(12,0)); explain.setBounds(16,595,745,96); JLabel ex = new JLabel("<html><b>◉  方法说明</b><br><br>• 本工具通过外部 oneclick 命令完成控制变量组合筛选。<br>• 运行后，工具会自动读取生成的 subset.dta，用于在右侧查看数据与结果。</html>"); ex.setForeground(TEXT); explain.add(ex,BorderLayout.CENTER); JTextArea syntax=new JTextArea("oneclick y candidates, fix(x required) p(#) m(method)\n[o(model_options)] [z]"); syntax.setEditable(false); syntax.setBackground(CODE_BG); syntax.setForeground(TEXT); syntax.setFont(new Font("Monospaced",Font.PLAIN,10)); syntax.setBorder(new EmptyBorder(8,10,8,10)); syntax.setPreferredSize(new Dimension(350,68)); explain.add(syntax,BorderLayout.EAST); root.add(explain);

         JPanel command = this.refCard(); command.setLayout(null); command.setBounds(16,704,745,106); JLabel ctitle=new JLabel("即将执行的 Stata 命令"); ctitle.setForeground(TEXT); ctitle.setFont(ctitle.getFont().deriveFont(Font.BOLD,12.0F)); ctitle.setBounds(14,6,190,22); command.add(ctitle); this.exactOneClickCommand.setEditable(false); this.exactOneClickCommand.setLineWrap(true); this.exactOneClickCommand.setWrapStyleWord(true); this.exactOneClickCommand.setBackground(new Color(244,248,255)); this.exactOneClickCommand.setForeground(TEXT); this.exactOneClickCommand.setFont(new Font("Monospaced",Font.PLAIN,10)); this.exactOneClickCommand.setBorder(new EmptyBorder(9,10,9,10)); JScrollPane cs=softScroll(this.exactOneClickCommand); cs.setBounds(14,32,420,55); command.add(cs); JButton copy=this.refButton("▣  复制命令",false); copy.setBounds(450,39,110,38); copy.addActionListener(e->{ Toolkit.getDefaultToolkit().getSystemClipboard().setContents(new StringSelection(this.exactOneClickCommand.getText()),null); }); command.add(copy); JButton run=this.refButton("▶  运行外部 OneClick",true); run.setBounds(570,39,155,38); run.addActionListener(e->this.runOneClick()); command.add(run); root.add(command);

         JPanel data = this.refCard(); data.setLayout(null); data.setBounds(780,115,405,695); JLabel dt=new JLabel("▣  当前数据"); dt.setForeground(TEXT); dt.setFont(dt.getFont().deriveFont(Font.BOLD,13.0F)); dt.setBounds(16,10,160,25); data.add(dt); JButton refresh=this.refButton("↻ 刷新",false); refresh.setBounds(315,9,70,32); refresh.addActionListener(e->this.refreshDataset(false)); data.add(refresh); JLabel tabs=new JLabel("数据      |      结果      |      日志"); tabs.setForeground(new Color(54,108,220)); tabs.setBounds(20,52,260,24); data.add(tabs); JComponent ill=this.exactEmptyDataIllustration(); ill.setBounds(72,125,260,210); data.add(ill); this.exactOneClickDataStatus.setForeground(TEXT); this.exactOneClickDataStatus.setFont(this.exactOneClickDataStatus.getFont().deriveFont(Font.BOLD,14.0F)); this.exactOneClickDataStatus.setBounds(45,340,315,30); data.add(this.exactOneClickDataStatus); this.exactOneClickDataDetail.setForeground(MUTED); this.exactOneClickDataDetail.setFont(this.exactOneClickDataDetail.getFont().deriveFont(9.5F)); this.exactOneClickDataDetail.setBounds(30,372,345,25); data.add(this.exactOneClickDataDetail); JButton au=this.refButton("▣  载入 auto 示例数据",false); au.setBounds(62,415,280,40); au.addActionListener(e->this.runUtility("sysuse auto, clear",true)); data.add(au); JButton own=this.refButton("↥  载入自己的 DTA",false); own.setBounds(62,465,280,40); own.addActionListener(e->this.chooseAndLoadDta()); data.add(own); JButton cv=this.refButton("▤  Excel / CSV 转换为 DTA",false); cv.setBounds(62,515,280,40); cv.addActionListener(e->this.navigateTo("data","导入与转换","hxconvert")); data.add(cv); JLabel hint=new JLabel("☼  提示：左侧完成变量设置，右侧查看数据与结果。"); hint.setForeground(MUTED); hint.setBounds(45,618,320,30); data.add(hint); root.add(data);

         JPanel recommend=this.refCard(); recommend.setLayout(new BoxLayout(recommend,BoxLayout.Y_AXIS)); recommend.setBounds(1200,115,240,695); JLabel rt=new JLabel("▥  推荐流程"); rt.setForeground(TEXT); rt.setFont(rt.getFont().deriveFont(Font.BOLD,14.0F)); rt.setAlignmentX(0.0F); recommend.add(rt); recommend.add(Box.createVerticalStrut(22)); String[][] rs={{"1","先确定核心变量","明确因变量 Y 与核心解释变量 X。"},{"2","再放入候选控制变量","根据理论与数据特征，添加候选控制变量。"},{"3","最后选择模型并运行","选择模型方法与显著性水平，运行外部 OneClick。"}}; Color[] rc={new Color(34,109,246),new Color(31,169,105),new Color(116,83,224)}; for(int i=0;i<3;i++){ JPanel rr=new JPanel(new BorderLayout(10,0)); rr.setOpaque(false); JLabel n=new JLabel(rs[i][0],SwingConstants.CENTER); n.setOpaque(true); n.setBackground(rc[i]); n.setForeground(Color.WHITE); n.setPreferredSize(new Dimension(29,29)); JPanel tx=new JPanel(); tx.setOpaque(false); tx.setLayout(new BoxLayout(tx,BoxLayout.Y_AXIS)); JLabel a=new JLabel(rs[i][1]); a.setForeground(TEXT); a.setFont(a.getFont().deriveFont(Font.BOLD,11.0F)); JLabel d=new JLabel("<html><div style='width:155px;color:#718096'>"+html(rs[i][2])+"</div></html>"); tx.add(a); tx.add(Box.createVerticalStrut(6)); tx.add(d); rr.add(n,BorderLayout.WEST); rr.add(tx,BorderLayout.CENTER); rr.setMaximumSize(new Dimension(Integer.MAX_VALUE,120)); recommend.add(rr); recommend.add(Box.createVerticalStrut(14)); } recommend.add(Box.createVerticalGlue()); JPanel tip=new JPanel(new BorderLayout()); tip.setBackground(new Color(255,250,241)); tip.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(255,219,166),9),new EmptyBorder(13,13,13,13))); tip.add(new JLabel("<html><b><span style='color:#f59e0b'>☼ 小贴士</span></b><br><br><span style='color:#68758b'>OneClick 最适合比较不同控制变量组合的稳健性结果，而不是替代理论选择。</span></html>"),BorderLayout.CENTER); tip.setMaximumSize(new Dimension(Integer.MAX_VALUE,150)); recommend.add(tip); root.add(recommend);
         return root;
      }'''
s=replace_method(s,'      private JComponent buildExactOneClickContainer()',one)

# preview state should match supplied OneClick screening mock, not robustness variant
preview=r'''      private void populateOneClickPreviewState() {
         this.rebuilding = true;
         this.categoryList.setSelectedIndex(6);
         this.methodModel.clear();
         this.methodModel.addElement("控制变量组合筛选");
         this.methodModel.addElement("控制变量组合稳健性");
         this.methodList.setSelectedIndex(0);
         this.commandModel.clear();
         this.commandModel.addElement("oneclick");
         this.commandList.setSelectedIndex(0);
         replaceComboItems(this.oneClickY, Arrays.asList("y", "x", "Size", "Lev", "ROA", "Growth", "Cash"));
         this.oneClickY.setSelectedItem("y");
         replaceComboItems(this.oneClickX, Arrays.asList("y", "x", "Size", "Lev", "ROA", "Growth", "Cash"));
         this.oneClickX.setSelectedItem("x");
         replaceComboItems(this.oneClickCluster, Arrays.asList("firm", "year"));
         this.oneClickCluster.setSelectedItem("firm");
         List vars = Arrays.asList("Size", "Lev", "ROA", "Growth", "Cash", "Age");
         replaceListItems(this.oneClickRequired, vars);
         replaceListItems(this.oneClickCandidates, vars);
         this.oneClickCandidates.clearSelection();
         this.oneClickRequired.clearSelection();
         replaceListItems(this.oneClickAbsorb, Arrays.asList("firm", "year"));
         this.oneClickAbsorb.clearSelection();
         this.oneClickEstimator.setSelectedItem("regress");
         this.oneClickP.setSelectedIndex(1);
         this.oneClickVce.setSelectedItem("默认");
         this.exactOneClickCandidatesDisplay.setText("");
         this.exactOneClickRequiredDisplay.setText("");
         this.rebuilding = false;
         this.showOneClickPage("oneclick");
         this.updateOneClickPreview();
      }'''
s=replace_method(s,'      private void populateOneClickPreviewState()',preview)

# linear exact vertical alignment with supplied screenshot
repls={
'back.setBounds(955,25,145,40)':'back.setBounds(955,63,145,40)',
'home.setBounds(1115,25,100,40)':'home.setBounds(1115,63,100,40)',
'help.setBounds(1230,25,100,40)':'help.setBounds(1230,63,100,40)',
'search.setBounds(30,120,1115,58)':'search.setBounds(30,143,1115,58)',
'recommend.setBounds(1165,124,240,640)':'recommend.setBounds(1165,146,240,640)',
'choose.setBounds(30,190,1115,56)':'choose.setBounds(30,217,1115,56)',
'commonCard.setBounds(30,258,1115,300)':'commonCard.setBounds(30,282,1115,300)',
'more.setBounds(30,570,1115,218)':'more.setBounds(30,600,1115,218)'
}
for a,b in repls.items():s=s.replace(a,b)

p.write_text(s,encoding='utf-8')
print('HX_PIXEL_MATCH_121_REFINE2_OK')
