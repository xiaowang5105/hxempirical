from pathlib import Path

p=Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s=p.read_text(encoding='utf-8')
s=s.replace('JLabel version = new JLabel("版本：1.2.4");','JLabel version = new JLabel("版本：1.2.5");')
s=s.replace("<span style='font-size:22px;color:#2f76ed'>▣ ◕</span><br><b>新手指引</b><br>","<b>新手指引</b><br>")
s=s.replace("String glyph = taskGlyph(var1);\n         JButton var5 = new JButton(\n            \"<html><div style='text-align:left'><span style='font-size:16px;color:\" + (var4 ? \"#2563d9\" : \"#2f855a\") + \"'>\" + html(glyph) + \"</span>&nbsp;&nbsp;<b>\" + html(var1) + \"</b><br><span style='font-size:9px;color:#637083'>\" + html(var2) + \"</span><span style='float:right;color:#7b8798'>&nbsp;&nbsp;›</span></div></html>\"\n         );", "JButton var5 = new JButton(\n            \"<html><div style='text-align:left'><b>\" + html(var1) + \"</b><br><span style='font-size:9px;color:#637083'>\" + html(var2) + \"</span></div></html>\"\n         );")
# Keep the Current Data inspector fixed and non-toggleable in the visible UI.
s=s.replace('styleSecondaryButton(this.inspectorToggle);\n         this.inspectorToggle.addActionListener(var1x -> this.toggleInspector());', 'this.inspectorToggle.setVisible(false);')
p.write_text(s,encoding='utf-8')
print('FINALIZE_125_OK')
