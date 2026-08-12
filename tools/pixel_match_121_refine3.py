from pathlib import Path
p=Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s=p.read_text(encoding='utf-8')
s=s.replace('ListSelectionModel.MULTIPLE_INTERVAL_SELECTION','2')
s=s.replace('if(i==0) stylePrimaryButton(b); else styleSecondaryButton(b); b.setSelected(i==0);', 'styleSecondaryButton(b); if(i==0) b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(new Color(34,109,246), new Color(28,94,222), new Color(24,82,198), Color.WHITE, new Color(34,109,246))); b.setSelected(i==0);')
p.write_text(s,encoding='utf-8')
print('HX_PIXEL_MATCH_121_REFINE3_OK')
