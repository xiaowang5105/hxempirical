from pathlib import Path
p=Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s=p.read_text(encoding='utf-8')
old='''      private final JProgressBar monitorProgress = new JProgressBar();
      private final JToggleButton monitorDetailsToggle = new JToggleButton("详细运行信息  +");
      private final JPanel monitorDetails = new JPanel(new BorderLayout(0, 7));
'''
new='''      private final JProgressBar monitorProgress = new JProgressBar();
'''
if old not in s:
    raise SystemExit('monitor detail declarations not found')
s=s.replace(old,new,1)
s=s.replace('new JLabel("版本：1.2.1")','new JLabel("版本：1.2.2")',1)
if 'monitorDetailsToggle' in s or 'monitorDetails = new JPanel' in s:
    raise SystemExit('obsolete monitor detail fields remain')
if '版本：1.2.1' in s:
    raise SystemExit('old sidebar version remains')
p.write_text(s,encoding='utf-8')
print('HX_RIGHT_COLUMN_122_FINALIZE_OK')
