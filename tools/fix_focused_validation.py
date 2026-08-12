from pathlib import Path

path = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
text = path.read_text(encoding="utf-8")

old = '''         if (this.flag("has_iv")) {
            List<String> var1 = this.endog.getSelectedValuesList();'''
new = '''         if (this.flag("has_depvar") && selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择因变量。", "因变量缺失", 1);
            return false;
         }

         if (this.flag("has_iv")) {
            List<String> var1 = this.endog.getSelectedValuesList();'''
if text.count(old) != 1:
    raise SystemExit(f"depvar validation anchor expected once, found {text.count(old)}")
text = text.replace(old, new, 1)

old = '''         if (!"无".equals(selected(this.genericWeightType)) && selected(this.genericWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后，请指定权重变量。", "权重变量缺失", 1);
            return false;
         }'''
new = '''         if (this.flag("has_weight")
            && !"无".equals(selected(this.genericWeightType))
            && selected(this.genericWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后，请指定权重变量。", "权重变量缺失", 1);
            return false;
         }'''
if text.count(old) != 1:
    raise SystemExit(f"weight validation anchor expected once, found {text.count(old)}")
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("FOCUSED_VALIDATION_FIX_OK")
