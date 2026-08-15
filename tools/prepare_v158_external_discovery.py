from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]


def read(rel):
    return (root / rel).read_text(encoding="utf-8")


def write(rel, text):
    (root / rel).write_text(text, encoding="utf-8", newline="\n")


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 occurrence, found {count}")
    return text.replace(old, new, 1)


def replace_method(text, signature, replacement):
    start = text.find(signature)
    if start < 0:
        raise RuntimeError(f"method not found: {signature}")
    brace = text.find("{", start)
    if brace < 0:
        raise RuntimeError(f"opening brace not found: {signature}")
    depth = 0
    end = None
    for i in range(brace, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise RuntimeError(f"closing brace not found: {signature}")
    return text[:start] + replacement + text[end:]


java_rel = "src/main/java/com/hexie/stata/HxWorkbench.java"
java = read(java_rel)
java = replace_once(java, 'public static final String VERSION = "1.5.7";', 'public static final String VERSION = "1.5.8";', "java version")

browse_method = r'''      private void browseInstalledExternalCommands() {
         this.activeCategoryCode = "external";
         this.activeCategoryName = "已安装外部命令";
         this.activeMethodName = "已安装";
         this.rebuilding = true;
         this.commandModel.clear();
         List<String> installed = this.discoverInstalledExternalCommands();
         for (String command : installed) this.commandModel.addElement(command);
         this.rebuilding = false;
         this.renderCommandChooser("已安装外部命令", "", installed);
         this.chooserHint.setText(
            installed.isEmpty()
               ? "没有检测到用户目录中的外部 ado 命令。本页只扫描和统计，不负责安装；需要什么请自行安装后再刷新。"
               : "已检测到 " + installed.size() + " 个可用外部命令。扫描 PLUS / PERSONAL / OLDPLACE，并用 which 确认可调用；常用命令会提供增强说明。"
         );
         this.setSidebarActive("external");
         this.setBusy(false, installed.isEmpty() ? "没有检测到可用外部命令。" : "外部命令扫描完成：" + installed.size() + " 个可用。");
      }

      private List<String> discoverInstalledExternalCommands() {
         if (this.previewMode) {
            return new ArrayList<>(Arrays.asList("reghdfe", "winsor2", "ppmlhdfe", "oneclick", "coefplot"));
         }

         LinkedHashSet<String> installed = new LinkedHashSet<>();
         for (String command : EXTERNAL_COMMAND_CATALOG) {
            if (HxWorkbench.StataBridge.execute("quietly which " + command, false) == 0) installed.add(command);
         }

         LinkedHashSet<Path> roots = new LinkedHashSet<>();
         for (String cName : Arrays.asList("sysdir_plus", "sysdir_personal", "sysdir_oldplace")) {
            String raw = HxWorkbench.StataBridge.cString(cName).trim();
            if (raw.isBlank()) continue;
            try {
               Path path = Paths.get(raw).toAbsolutePath().normalize();
               if (Files.isDirectory(path)) roots.add(path);
            } catch (Throwable ignored) {
            }
         }

         TreeSet<String> discovered = new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
         for (Path adoRoot : roots) {
            try (Stream<Path> stream = Files.walk(adoRoot, 5)) {
               stream.filter(Files::isRegularFile).forEach(path -> {
                  String fileName = Objects.toString(path.getFileName(), "");
                  String lower = fileName.toLowerCase(Locale.ROOT);
                  if (!lower.endsWith(".ado") || fileName.length() <= 4) return;
                  String command = fileName.substring(0, fileName.length() - 4);
                  if (!command.matches("[A-Za-z][A-Za-z0-9_]*")) return;
                  if (command.toLowerCase(Locale.ROOT).startsWith("hx")) return;
                  discovered.add(command);
               });
            } catch (Throwable ignored) {
            }
         }

         for (String command : discovered) {
            if (installed.contains(command)) continue;
            if (HxWorkbench.StataBridge.execute("quietly which " + command, false) == 0) installed.add(command);
         }
         return new ArrayList<>(installed);
      }'''
java = replace_method(java, "      private void browseInstalledExternalCommands()", browse_method)

c_string_method = r'''      static String cString(String name) {
         if (name == null || !name.matches("[A-Za-z_][A-Za-z0-9_]*")) return "";
         String macroName = "HXEMPIRICAL__CSTRING";
         try {
            execute("global " + macroName + " \"\"", false);
            int rc = execute("global " + macroName + " = c(" + name + ")", false);
            if (rc != 0) return "";
            String value = Macro.getGlobal(macroName);
            return value == null ? "" : value;
         } catch (Throwable ignored) {
            return "";
         } finally {
            execute("capture macro drop " + macroName, false);
         }
      }

'''
marker = "      static String characteristic(String var0) {"
if marker not in java:
    raise RuntimeError("StataBridge characteristic marker not found")
java = java.replace(marker, c_string_method + marker, 1)
write(java_rel, java)

# Version surfaces.
ado_rel = "hxempirical.ado"
ado = read(ado_rel).replace("hxempirical 1.5.7", "hxempirical 1.5.8").replace('"1.5.7"', '"1.5.8"')
write(ado_rel, ado)

help_rel = "hxempirical.sthlp"
hlp = read(help_rel).replace("version 1.5.7", "version 1.5.8").replace("The 1.5.7 interface", "The 1.5.8 interface")
needle = "External commands are user-managed. The workbench only detects registered third-party commands\nthat Stata can currently find and lists them under {bf:外部命令}; it does not automatically install them.\nInstall any needed command using its author's instructions, then reopen {bf:外部命令} to detect it."
replacement = "External commands are user-managed. {bf:外部命令} scans Stata's user ado directories\n({bf:PLUS}, {bf:PERSONAL}, and {bf:OLDPLACE}), confirms discovered .ado names with {cmd:which}, and lists\nthe commands that are actually callable. The workbench does not automatically install them. Install any\nneeded command using its author's instructions, then reopen {bf:外部命令} to rescan it."
hlp = replace_once(hlp, needle, replacement, "help external discovery")
write(help_rel, hlp)

for rel in ["hxempirical.pkg", "hxinstall.do", "hxinstaller.ado", "INSTALL.md"]:
    write(rel, read(rel).replace("1.5.7", "1.5.8"))

readme_rel = "README.md"
readme = read(readme_rel)
readme = replace_once(readme, "**当前发布版本：1.5.7**", "**当前发布版本：1.5.8**", "README version")
anchor = "### 1.5.7 数据编辑与外部命令管理\n"
section = '''### 1.5.8 外部命令自动发现

- “外部命令”不再只检查预先登记的少量命令，而是扫描 Stata 的 `PLUS`、`PERSONAL`、`OLDPLACE` 用户 ado 目录，并用 `which` 再确认命令当前确实可调用。
- 因此以后用户自己安装新的第三方 `.ado` 命令后，重新进入“外部命令”即可发现；常用命令目录只用于补充中文说明，不再构成检测上限。
- hxempirical 仍然不替用户安装第三方命令：这里只负责扫描、统计、搜索和打开。

'''
readme = replace_once(readme, anchor, section + anchor, "README release anchor")
readme = readme.replace(
    '“外部命令”只负责检测和统计当前 Stata 已能找到的登记第三方命令，不再承担安装职责。',
    '“外部命令”负责扫描和统计 Stata 用户 ado 目录中当前实际可调用的第三方命令，不再承担安装职责。',
    1,
)
write(readme_rel, readme)

# Strengthen permanent static checks for broad discovery.
verify_rel = "tools/verify_static_contracts.py"
verify = read(verify_rel)
verify = verify.replace(
    'for needle in (\n    "已安装外部命令",\n    "本页只检测，不负责安装",',
    'for needle in (\n    "已安装外部命令",\n    "sysdir_plus",\n    "sysdir_personal",\n    "sysdir_oldplace",\n    "Files.walk",\n    "quietly which",\n    "本页只扫描和统计，不负责安装",',
    1,
)
verify = verify.replace(
    '"ui_external_manual_only=1 spreadsheet_editable=1 "',
    '"ui_external_manual_only=1 external_user_ado_scan=1 spreadsheet_editable=1 "',
    1,
)
write(verify_rel, verify)

print("HX_V158_PREP_OK")
