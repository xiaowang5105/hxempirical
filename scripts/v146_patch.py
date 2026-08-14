from pathlib import Path
import re

p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')

# Release version.
s = s.replace('public static final String VERSION = "1.4.5";', 'public static final String VERSION = "1.4.6";')
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.4.5");', 'SFIToolkit.displayln("HxWorkbench 1.4.6");')

field_old = '''      private JComboBox<String> xtregSeCombo;\n      private boolean xtregSyncingFromCommand;\n      private String activeSidebarKey = "home";'''
field_new = '''      private JComboBox<String> xtregSeCombo;\n      private boolean xtregSyncingFromCommand;\n      private String xtregClusterVar = "";\n      private String xtregExtraOptions = "";\n      private String xtregCustomXText = "";\n      private boolean xtregPreserveCustomX;\n      private String xtregCommandPrefix = "";\n      private String activeSidebarKey = "home";'''
assert field_old in s
s = s.replace(field_old, field_new, 1)

# Replace the UI -> command generator so manually-entered advanced syntax can survive later UI changes.
pat = re.compile(r'''         Runnable update = \(\) -> \{.*?         this\.xtregPreviewUpdater = update;''', re.S)
new_update = '''         Runnable update = () -> {
            String pv = Objects.toString(panelVar.getSelectedItem(), "").trim();
            String tv = Objects.toString(timeVar.getSelectedItem(), "").trim();
            String y = Objects.toString(dep.getSelectedItem(), "").trim();
            List<String> xs = indep.getSelectedValuesList();
            String model = fe.isSelected() ? "fe" : re.isSelected() ? "re" : be.isSelected() ? "be" : "pa";
            StringBuilder xt = new StringBuilder(this.xtregCommandPrefix == null ? "" : this.xtregCommandPrefix);
            xt.append("xtreg");
            if (!y.isBlank()) xt.append(" ").append(y);
            if (this.xtregPreserveCustomX && this.xtregCustomXText != null && !this.xtregCustomXText.isBlank()) {
               xt.append(" ").append(this.xtregCustomXText.trim());
            } else {
               for (String x : xs) xt.append(" ").append(x);
            }
            xt.append(", ").append(model);
            String sem = Objects.toString(se.getSelectedItem(), "");
            if ("稳健标准误".equals(sem)) xt.append(" vce(robust)");
            if ("按面板聚类".equals(sem) && !pv.isBlank()) {
               String cluster = this.xtregClusterVar == null || this.xtregClusterVar.isBlank() ? pv : this.xtregClusterVar.trim();
               xt.append(" vce(cluster ").append(cluster).append(")");
            }
            if (this.xtregExtraOptions != null && !this.xtregExtraOptions.isBlank()) xt.append(" ").append(this.xtregExtraOptions.trim());
            String setup = pv.isBlank() ? "xtset panelvar timevar" : "xtset " + pv + (tv.isBlank() ? "" : " " + tv);
            String shown = setup + "\\n" + xt;
            commandPreview.setText(shown);
            this.previewArea.setText(xt.toString());
            this.refreshInspectorRole();
         };
         this.xtregPreviewUpdater = update;'''
s, n = pat.subn(new_update, s, count=1)
assert n == 1, n

# X selection becomes authoritative only when the user actually changes it.
old_listener = '''         indep.addListSelectionListener(e -> { if (!this.rebuilding && !e.getValueIsAdjusting()) update.run(); });
         for (JRadioButton b : Arrays.asList(fe, re, be, pa)) b.addActionListener(e -> { if (!this.rebuilding) update.run(); });
         se.addActionListener(e -> { if (!this.rebuilding) update.run(); });'''
new_listener = '''         indep.addListSelectionListener(e -> { if (!this.rebuilding && !e.getValueIsAdjusting()) { this.xtregPreserveCustomX = false; this.xtregCustomXText = ""; update.run(); } });
         for (JRadioButton b : Arrays.asList(fe, re, be, pa)) b.addActionListener(e -> { if (!this.rebuilding) update.run(); });
         se.addActionListener(e -> { if (!this.rebuilding) { this.xtregClusterVar = ""; update.run(); } });'''
assert old_listener in s
s = s.replace(old_listener, new_listener, 1)

old_clear = '''         JButton clear = this.refButton("清空设置", false); clear.addActionListener(e -> { panelVar.setSelectedIndex(0); timeVar.setSelectedIndex(0); dep.setSelectedIndex(0); indep.clearSelection(); fe.setSelected(true); se.setSelectedIndex(0); update.run(); });'''
new_clear = '''         JButton clear = this.refButton("清空设置", false); clear.addActionListener(e -> { this.xtregClusterVar = ""; this.xtregExtraOptions = ""; this.xtregCustomXText = ""; this.xtregPreserveCustomX = false; this.xtregCommandPrefix = ""; panelVar.setSelectedIndex(0); timeVar.setSelectedIndex(0); dep.setSelectedIndex(0); indep.clearSelection(); fe.setSelected(true); se.setSelectedIndex(0); update.run(); });'''
assert old_clear in s
s = s.replace(old_clear, new_clear, 1)

# Run the command that is actually in the editable command box. Do not reject factor/TS X terms merely because JList cannot represent them literally.
run_pat = re.compile(r'''         JButton run = this\.refButton\("运行 xtreg", true\);\n         run\.addActionListener\(e -> \{.*?\n         \}\);\n         actions\.add\(prev\);''', re.S)
run_new = '''         JButton run = this.refButton("运行 xtreg", true);
         run.addActionListener(e -> {
            this.syncXtregControlsFromCommand();
            String pv = Objects.toString(panelVar.getSelectedItem(), "").trim();
            String y = Objects.toString(dep.getSelectedItem(), "").trim();
            String[] edited = this.extractXtregCommands(commandPreview.getText());
            String setup = edited[0];
            String cmd = edited[1];
            if (setup.isBlank() && !pv.isBlank()) {
               String tv = Objects.toString(timeVar.getSelectedItem(), "").trim();
               setup = "xtset " + pv + (tv.isBlank() ? "" : " " + tv);
            }
            if (pv.isBlank() || y.isBlank() || setup.isBlank() || cmd.isBlank() || setup.contains("panelvar")) {
               JOptionPane.showMessageDialog(this, "请至少完成面板 ID、因变量，并保留一条可执行的 xtreg 命令。", "设置尚未完成", JOptionPane.INFORMATION_MESSAGE);
               return;
            }
            int setupRc = HxWorkbench.StataBridge.execute(setup, false);
            if (setupRc != 0) {
               this.statusLabel.setText("xtset 失败，返回码：" + setupRc);
               return;
            }
            this.previewArea.setText(cmd);
            this.executeMonitoredCommand(
               cmd,
               "hxexecute, command(" + HxWorkbench.StataBridge.quote(cmd) + ")",
               false,
               result -> this.statusLabel.setText(
                  result.rc == 0 ? "xtreg 已运行；右侧‘结果’已同步 Stata Results。" : "xtreg 运行失败，返回码：" + result.rc
               )
            );
         });
         actions.add(prev);'''
s, n = run_pat.subn(run_new, s, count=1)
assert n == 1, n

# Replace the reverse parser with a parser that handles prefixes, continuation lines, factor/TS terms,
# clears omitted xtset time variables, preserves explicit cluster variables and unrepresented options.
sync_pat = re.compile(r'''      private void syncXtregControlsFromCommand\(\) \{.*?\n      \}\n\n      private void openCommandPage''', re.S)
sync_new = r'''      private static String collapseStataContinuation(String raw) {
         if (raw == null) return "";
         return raw.replaceAll("///\\s*\\R\\s*", " ");
      }

      private static String stripStataCommandPrefix(String line) {
         String value = line == null ? "" : line.trim();
         Pattern prefix = Pattern.compile("(?i)^(quietly|qui|capture|cap|noisily|noi)\\s*:?\\s+");
         while (!value.isBlank()) {
            Matcher matcher = prefix.matcher(value);
            if (!matcher.find()) break;
            value = value.substring(matcher.end()).trim();
         }
         return value;
      }

      private String[] extractXtregCommands(String raw) {
         String setup = "";
         String model = "";
         String normalized = collapseStataContinuation(raw);
         for (String line : normalized.split("\\R")) {
            String original = line.trim();
            if (original.isBlank()) continue;
            String core = stripStataCommandPrefix(original);
            String lower = core.toLowerCase(Locale.ROOT);
            if (lower.startsWith("xtset ")) setup = original;
            if (lower.startsWith("xtreg ")) model = original;
         }
         return new String[]{setup, model};
      }

      private static String xtregCore(String command) {
         return stripStataCommandPrefix(command);
      }

      private List<String> xtregBaseVariables(String term) {
         List<String> out = new ArrayList<>();
         if (term == null || term.isBlank()) return out;
         for (String piece : term.split("#+")) {
            String item = piece.trim();
            if (item.isBlank()) continue;
            int dot = item.lastIndexOf('.');
            if (dot >= 0 && dot + 1 < item.length()) item = item.substring(dot + 1);
            item = item.replaceAll("^[()]+|[(),]+$", "");
            if (item.matches("[A-Za-z_][A-Za-z0-9_]*")) out.add(item);
         }
         return out;
      }

      private boolean xtregListContains(String value) {
         if (value == null || this.xtregIndepList == null) return false;
         ListModel<String> model = this.xtregIndepList.getModel();
         for (int i = 0; i < model.getSize(); i++) if (value.equals(model.getElementAt(i))) return true;
         return false;
      }

      private void selectXtregBaseVariable(String value) {
         if (value == null || this.xtregIndepList == null) return;
         ListModel<String> model = this.xtregIndepList.getModel();
         for (int i = 0; i < model.getSize(); i++) {
            if (value.equals(model.getElementAt(i))) {
               this.xtregIndepList.addSelectionInterval(i, i);
               return;
            }
         }
      }

      private void syncXtregControlsFromCommand() {
         if (this.xtregSyncingFromCommand || this.xtregCommandPreview == null
            || this.xtregPanelVar == null || this.xtregTimeVar == null || this.xtregDepVar == null
            || this.xtregIndepList == null || this.xtregFeButton == null || this.xtregSeCombo == null) return;
         String raw = this.xtregCommandPreview.getText() == null ? "" : this.xtregCommandPreview.getText().trim();
         if (raw.isBlank()) return;

         String[] commands = this.extractXtregCommands(raw);
         String xtsetLine = commands[0];
         String xtregLine = commands[1];
         if (xtregLine.isBlank()) {
            this.statusLabel.setText("命令编辑：未找到可执行的 xtreg 命令；上方设置未改变。");
            return;
         }

         String xtregCore = xtregCore(xtregLine);
         boolean oldRebuilding = this.rebuilding;
         this.xtregSyncingFromCommand = true;
         this.rebuilding = true;
         int synced = 0;
         try {
            if (!xtsetLine.isBlank()) {
               String setupCore = stripStataCommandPrefix(xtsetLine);
               String[] parts = setupCore.replaceFirst("(?i)^xtset\\s+", "").trim().split("\\s+");
               this.xtregPanelVar.setSelectedIndex(0);
               this.xtregTimeVar.setSelectedIndex(0);
               if (parts.length >= 1 && this.setXtregComboValue(this.xtregPanelVar, parts[0])) synced++;
               if (parts.length >= 2 && this.setXtregComboValue(this.xtregTimeVar, parts[1])) synced++;
            }

            int keyword = Pattern.compile("(?i)\\bxtreg\\b").matcher(xtregLine).find() ? xtregLine.toLowerCase(Locale.ROOT).indexOf("xtreg") : -1;
            this.xtregCommandPrefix = keyword > 0 ? xtregLine.substring(0, keyword) : "";

            int comma = xtregCore.indexOf(',');
            String lhs = comma >= 0 ? xtregCore.substring(0, comma).trim() : xtregCore.trim();
            String opts = comma >= 0 ? xtregCore.substring(comma + 1).trim() : "";
            String varsText = lhs.replaceFirst("(?i)^xtreg\\s+", "").trim();
            String[] terms = varsText.isBlank() ? new String[0] : varsText.split("\\s+");
            if (terms.length >= 1 && this.setXtregComboValue(this.xtregDepVar, terms[0])) synced++;

            this.xtregIndepList.clearSelection();
            boolean customX = false;
            List<String> rawX = new ArrayList<>();
            for (int t = 1; t < terms.length; t++) {
               String term = terms[t];
               rawX.add(term);
               if (this.xtregListContains(term)) {
                  this.selectXtregBaseVariable(term);
                  synced++;
               } else {
                  customX = true;
                  for (String base : this.xtregBaseVariables(term)) {
                     if (this.xtregListContains(base)) {
                        this.selectXtregBaseVariable(base);
                        synced++;
                     }
                  }
               }
            }
            this.xtregCustomXText = String.join(" ", rawX);
            this.xtregPreserveCustomX = customX;

            String padded = " " + opts.toLowerCase(Locale.ROOT).replaceAll("\\s+", " ") + " ";
            if (Pattern.compile("(^|\\s)fe(\\s|$)").matcher(padded).find()) this.xtregFeButton.setSelected(true);
            else if (Pattern.compile("(^|\\s)re(\\s|$)").matcher(padded).find()) this.xtregReButton.setSelected(true);
            else if (Pattern.compile("(^|\\s)(be|between)(\\s|$)").matcher(padded).find()) this.xtregBeButton.setSelected(true);
            else if (Pattern.compile("(^|\\s)(pa|population-averaged)(\\s|$)").matcher(padded).find()) this.xtregPaButton.setSelected(true);
            synced++;

            Matcher clusterMatcher = Pattern.compile("(?i)vce\\s*\\(\\s*cluster\\s+([^\\s\\)]+)\\s*\\)").matcher(opts);
            if (clusterMatcher.find()) {
               this.xtregClusterVar = clusterMatcher.group(1).trim();
               this.xtregSeCombo.setSelectedItem("按面板聚类");
            } else if (Pattern.compile("(?i)vce\\s*\\(\\s*robust\\s*\\)").matcher(opts).find()) {
               this.xtregClusterVar = "";
               this.xtregSeCombo.setSelectedItem("稳健标准误");
            } else {
               this.xtregClusterVar = "";
               this.xtregSeCombo.setSelectedItem("默认标准误");
            }
            synced++;

            String extras = opts;
            extras = extras.replaceAll("(?i)(^|\\s)(fe|re|be|between|pa|population-averaged)(?=\\s|$)", " ");
            extras = extras.replaceAll("(?i)vce\\s*\\([^\\)]*\\)", " ");
            this.xtregExtraOptions = extras.replaceAll("\\s+", " ").trim();

            this.previewArea.setText(xtregLine);
            this.previewArea.setCaretPosition(0);
            this.refreshInspectorRole();
         } finally {
            this.rebuilding = oldRebuilding;
            this.xtregSyncingFromCommand = false;
         }
         this.statusLabel.setText("已从编辑后的命令同步上方设置（" + synced + " 项）；因子/交互/滞后项与未映射高级选项保持原命令语义。");
      }

      private void openCommandPage'''
s, n = sync_pat.subn(sync_new, s, count=1)
assert n == 1, n

p.write_text(s, encoding='utf-8')

# Text metadata.
for name in ['README.md', 'hxempirical.ado', 'hxempirical.pkg', 'hxempirical.sthlp']:
    q = Path(name)
    t = q.read_text(encoding='utf-8')
    t = t.replace('1.4.5', '1.4.6')
    q.write_text(t, encoding='utf-8')

print('V146_PATCH_OK')
