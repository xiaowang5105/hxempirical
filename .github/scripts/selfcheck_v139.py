from pathlib import Path


def replace_method(src, signature, replacement):
    start = src.index(signature)
    brace = src.index('{', start)
    depth = 0
    i = brace
    in_str = False
    esc = False
    quote = ''
    while i < len(src):
        ch = src[i]
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                in_str = False
        else:
            if ch in ('"', "'"):
                in_str = True
                quote = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return src[:start] + replacement + src[i+1:]
        i += 1
    raise RuntimeError('unbalanced method: ' + signature)

p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')
assert 'public static final String VERSION = "1.3.8";' in s
s = s.replace('public static final String VERSION = "1.3.8";', 'public static final String VERSION = "1.3.9";', 1)
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.3.8");', 'SFIToolkit.displayln("HxWorkbench 1.3.9");', 1)

native_method = '''      static String lastNativeOutput() {
         String path = characteristic("hxtoolbox_last_results_file");
         if (path == null || path.isBlank()) {
            return "";
         }

         try {
            Path resultPath = Paths.get(path);
            if (!Files.isRegularFile(resultPath)) {
               return "";
            }

            final int maxBytes = 2 * 1024 * 1024;
            long fileSize = Files.size(resultPath);
            byte[] bytes;
            try (InputStream in = Files.newInputStream(resultPath)) {
               bytes = in.readNBytes(maxBytes);
            }

            Charset charset = StandardCharsets.UTF_8;
            int offset = 0;
            if (bytes.length >= 3 && (bytes[0] & 255) == 0xEF && (bytes[1] & 255) == 0xBB && (bytes[2] & 255) == 0xBF) {
               offset = 3;
            } else if (bytes.length >= 2 && (bytes[0] & 255) == 0xFF && (bytes[1] & 255) == 0xFE) {
               charset = StandardCharsets.UTF_16LE;
               offset = 2;
            } else if (bytes.length >= 2 && (bytes[0] & 255) == 0xFE && (bytes[1] & 255) == 0xFF) {
               charset = StandardCharsets.UTF_16BE;
               offset = 2;
            }

            String text = new String(bytes, offset, Math.max(0, bytes.length - offset), charset).replace("\\u0000", "").stripTrailing();
            if (fileSize > bytes.length) {
               text += "\\n\\n[输出过长：工具箱仅显示前 2 MB；完整内容仍保留在 Stata Results。]";
            }
            return text;
         } catch (Throwable var2) {
            return "";
         }
      }'''
s = replace_method(s, '      static String lastNativeOutput()', native_method)

sync_method = '''      private void syncRightPaneTitle() {
         int index = this.dataTabs.getSelectedIndex();
         if (index == 1) {
            this.rightPaneTitle.setText("结果");
            this.refreshButton.setVisible(false);
            String command = this.lastExecutedCommand == null ? "" : this.lastExecutedCommand.trim();
            this.dataLabel.setText(command.isBlank() ? "运行命令后显示 Stata 原始输出与执行摘要" : "最近命令：" + shortenCommand(command));
         } else if (index == 2) {
            this.rightPaneTitle.setText("运行日志");
            this.refreshButton.setVisible(false);
            this.dataLabel.setText(this.runInProgress ? "命令执行中 · 查看实时计时与状态" : "执行状态、耗时、Return code 与 History");
         } else {
            this.rightPaneTitle.setText("当前数据");
            this.refreshButton.setVisible(true);
            long n = Data.getObsTotal();
            int k = Data.getVarCount();
            String dataHint = "xtreg".equals(this.currentCommand) ? " | 拖动表头变量可直接填入左侧变量框" : " | 表格只读，可横向和纵向滚动";
            this.dataLabel.setText(n != 0L && k != 0 ? n + " 行 × " + k + " 列" + dataHint : "尚未载入数据");
         }
      }'''
s = replace_method(s, '      private void syncRightPaneTitle()', sync_method)

refresh_marker = '''         this.refreshHomeContext();
      }

      private void compareSnapshots'''
assert refresh_marker in s
s = s.replace(refresh_marker, '''         this.syncRightPaneTitle();
         this.refreshHomeContext();
      }

      private void compareSnapshots''', 1)
p.write_text(s, encoding='utf-8')

p = Path('hxempirical.ado')
a = p.read_text(encoding='utf-8')
assert '1.3.8' in a
p.write_text(a.replace('1.3.8', '1.3.9'), encoding='utf-8')

p = Path('hxempirical.pkg')
a = p.read_text(encoding='utf-8')
assert 'd Version 1.3.8' in a
p.write_text(a.replace('d Version 1.3.8', 'd Version 1.3.9', 1), encoding='utf-8')

p = Path('hxempirical.sthlp')
a = p.read_text(encoding='utf-8')
p.write_text(a.replace('1.3.8', '1.3.9'), encoding='utf-8')

p = Path('README.md')
a = p.read_text(encoding='utf-8')
a = a.replace('**当前发布版本：1.3.8**', '**当前发布版本：1.3.9**', 1)
a = a.replace('**上次修改时间：2026-08-13 14:31（UTC+8）**', '**上次修改时间：2026-08-13 14:42（UTC+8）**', 1)
a = a.replace('5. 常用参数优先显示，低频参数放入“更多设置”。', '5. 常用参数优先显示，低频参数按顺序放在后面，不通过隐藏式“更多设置”改变页面结构。', 1)
p.write_text(a, encoding='utf-8')
print('PATCH_OK')
