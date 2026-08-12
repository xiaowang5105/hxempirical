from pathlib import Path
p=Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s=p.read_text(encoding='utf-8')
s=s.replace('g.intent', 'g.purpose')
anchor='      private final JTextArea exactOneClickCommand = new JTextArea();\n'
if 'exactOneClickModelOptions' not in s:
    s=s.replace(anchor, anchor+'      private final JTextField exactOneClickModelOptions = new JTextField();\n      private final JTextField exactOneClickOtherOptions = new JTextField();\n',1)
s=s.replace('this.oneClickModelOptions', 'this.exactOneClickModelOptions')
s=s.replace('styleTextField(this.exactOneClickModelOptions); styleTextField(this.options);', 'styleTextField(this.exactOneClickModelOptions); styleTextField(this.exactOneClickOtherOptions);')
s=s.replace('this.options.setBounds(520,220,205,32); settings.add(this.options);', 'this.exactOneClickOtherOptions.setBounds(520,220,205,32); settings.add(this.exactOneClickOtherOptions);')
# keep the reference-only extra option boxes reflected in the visible command box
needle='         this.exactOneClickCommand.setText(this.previewArea.getText());'
if needle in s and 'exactOneClickModelOptions.getText()' not in s:
    repl=needle+'\n         String hxO = this.exactOneClickModelOptions.getText().trim();\n         String hxZ = this.exactOneClickOtherOptions.getText().trim();\n         if (!hxO.isBlank()) this.exactOneClickCommand.append(" o(" + hxO + ")");\n         if (!hxZ.isBlank()) this.exactOneClickCommand.append(" " + hxZ);'
    s=s.replace(needle,repl,1)
p.write_text(s,encoding='utf-8')
print('HX_PIXEL_MATCH_121_FIX_OK')
