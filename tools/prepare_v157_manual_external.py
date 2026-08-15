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


def sub_once(text, pattern, replacement, label):
    rx = re.compile(pattern, re.S)
    text, count = rx.subn(lambda _: replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 match, found {count}")
    return text


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


# Java UI / behavior
java_rel = "src/main/java/com/hexie/stata/HxWorkbench.java"
java = read(java_rel)
java = replace_once(java, 'public static final String VERSION = "1.5.6";', 'public static final String VERSION = "1.5.7";', "java version")
java = sub_once(
    java,
    r'      private static final List<String> EXTERNAL_COMMAND_CATALOG = Arrays\.asList\(.*?\n      \);',
    '''      private static final List<String> EXTERNAL_COMMAND_CATALOG = Arrays.asList(
         "ftools", "reghdfe", "winsor2", "ranktest", "ivreg2", "ivreghdfe", "ppmlhdfe", "tuples", "oneclick", "oneclick_robustness", "coefplot", "event_plot"
      );''',
    "external command catalog",
)
java = replace_once(
    java,
    'this.statusLabel.setText(var1 + " 是可选扩展，当前尚未安装；可以先查看参数，点击运行时再决定是否安装。");',
    'this.statusLabel.setText(var1 + " 是外部命令，当前尚未安装；请按作者说明自行安装，安装后到“外部命令”重新检测。");',
    "optional dependency status",
)
java = replace_once(
    java,
    'this.baselineEstimatorSource.setText("第三方 · 需要安装");',
    'this.baselineEstimatorSource.setText("第三方 · 未安装");',
    "baseline source label",
)
manual_guard = '''      private boolean ensureOptionalDependencyBeforeRun(String command) {
         if (!OPTIONAL_DEPENDENCIES.contains(command) || this.optionalDependencyInstalled(command)) {
            return true;
         }
         this.statusLabel.setText("已取消运行：" + command + " 尚未安装。请自行安装后到‘外部命令’重新检测。");
         JOptionPane.showMessageDialog(
            this,
            command + " 尚未安装。\\n\\n工作台不会自动安装第三方命令。\\n请按该命令作者的说明自行安装，安装后回到‘外部命令’重新检测即可。",
            "缺少外部命令",
            JOptionPane.INFORMATION_MESSAGE
         );
         return false;
      }'''
java = replace_method(java, "      private boolean ensureOptionalDependencyBeforeRun(String command)", manual_guard)
java = sub_once(
    java,
    r'if \(!var1 && JOptionPane\.showConfirmDialog\(this, "当前没有安装 oneclick。现在从 SSC 安装吗？", "缺少 OneClick", 0\) == 0\) \{.*?JOptionPane\.showMessageDialog\(this, var2 \+ " 尚未安装。请先安装作者提供的外部命令后再运行。", "缺少外部命令", 1\);\s*\}',
    '''JOptionPane.showMessageDialog(
                     this,
                     var2 + " 尚未安装。\\n\\n工作台不会自动安装外部命令。请按作者说明自行安装，安装后到‘外部命令’重新检测再运行。",
                     "缺少外部命令",
                     JOptionPane.INFORMATION_MESSAGE
                  );''',
    "oneclick manual install",
)
java = java.replace('this.activeCategoryName = "已下载外部命令";', 'this.activeCategoryName = "已安装外部命令";')
java = java.replace('this.renderCommandChooser("已下载外部命令", "", installed);', 'this.renderCommandChooser("已安装外部命令", "", installed);')
java = replace_once(
    java,
    'installed.isEmpty()\n               ? "当前没有检测到工具箱已登记且 Stata 能找到的外部命令。"\n               : "仅显示工具箱已登记且当前 Stata 能找到的外部命令，共 " + installed.size() + " 个。"',
    'installed.isEmpty()\n               ? "当前没有检测到已安装的登记外部命令。本页只检测，不负责安装；需要什么请自行安装后再次进入本页。"\n               : "已检测到 " + installed.size() + " 个已安装外部命令（登记 " + EXTERNAL_COMMAND_CATALOG.size() + " 个）。本页只检测，不负责安装。"',
    "external chooser hint",
)
java = replace_once(
    java,
    'this.setBusy(false, installed.isEmpty() ? "没有检测到已安装的登记外部命令。" : "已读取当前可用的外部命令。");',
    'this.setBusy(false, installed.isEmpty() ? "没有检测到已安装的登记外部命令。" : "外部命令检测完成：" + installed.size() + " 个已安装。");',
    "external status",
)
write(java_rel, java)

# Public entry: the old install subcommand becomes an explicit manual-install notice.
ado_rel = "hxempirical.ado"
ado = read(ado_rel).replace("hxempirical 1.5.6", "hxempirical 1.5.7")
ado = ado.replace('"1.5.6"', '"1.5.7"')
ado = replace_once(
    ado,
    "        hxdependency install `rest'\n        exit",
    "        display as error ustrunescape(\"hxempirical 不再自动安装第三方命令。\")\n        display as text  ustrunescape(\"请按命令作者说明自行安装；安装后打开工作台 > 外部命令查看。\")\n        exit",
    "public install behavior",
)
ado = ado.replace(' | classic | install \\u547d\\u4ee4\\u540d | update', ' | classic | update')
write(ado_rel, ado)

# Help: editable data sheet and manual-only external commands.
help_rel = "hxempirical.sthlp"
hlp = read(help_rel)
hlp = hlp.replace("version 1.5.6", "version 1.5.7")
hlp = hlp.replace("The 1.5.6 interface", "The 1.5.7 interface")
hlp = hlp.replace('{p 8 16 2}{cmd:hxempirical install} {it:command}\n', '')
hlp = replace_once(
    hlp,
    "task-oriented pages, live command preview, and a read-only view of the dataset\ncurrently in Stata memory. Commands run in Stata itself. The complete command is\nadded to Stata's History window before execution.",
    "task-oriented pages, live command preview, and an editable spreadsheet-style view of the dataset\ncurrently in Stata memory. Double-clicked cell edits and the fx formula bar execute real Stata\n{cmd:replace}/{cmd:generate} operations. Commands run in Stata itself and are added to Stata History.",
    "help data description",
)
needle = "Unresolved syntax remains available in\nthe advanced-options field.\n"
insert = needle + "\n{pstd}\nExternal commands are user-managed. The workbench only detects registered third-party commands\nthat Stata can currently find and lists them under {bf:外部命令}; it does not automatically install them.\nInstall any needed command using its author's instructions, then reopen {bf:外部命令} to detect it.\n"
hlp = replace_once(hlp, needle, insert, "help external policy")
write(help_rel, hlp)

# Package/install version surfaces.
for rel in ["hxempirical.pkg", "hxinstall.do", "hxinstaller.ado", "INSTALL.md"]:
    write(rel, read(rel).replace("1.5.6", "1.5.7"))

# README current behavior and release note.
readme_rel = "README.md"
readme = read(readme_rel)
readme = replace_once(readme, "**当前发布版本：1.5.6**", "**当前发布版本：1.5.7**", "README version")
readme = replace_once(readme, "**上次修改时间：2026-08-15 19:21（UTC+8）**", "**上次修改时间：2026-08-15 20:22（UTC+8）**", "README timestamp")
anchor = "### 1.5.6 左侧导航重构\n"
section = '''### 1.5.7 数据编辑与外部命令管理

- “当前数据”明确作为轻量 WPS/Excel 式可编辑数据表：双击单元格可改值，`fx` 公式栏支持 `=Stata表达式`，可作用于单元格、整列或新建计算列；所有改动仍由真实 Stata `replace` / `generate` 执行。
- “外部命令”只负责检测和统计当前 Stata 已能找到的登记第三方命令，不再承担安装职责。
- `reghdfe`、`ppmlhdfe`、`winsor2`、`oneclick`、`coefplot` 等缺失时，工作台只提示“未安装”，不会再弹出自动安装流程。
- 用户需要什么外部命令，按作者说明自行安装；安装完成后重新进入“外部命令”即可检测和使用。

'''
readme = replace_once(readme, anchor, section + anchor, "README release anchor")
readme = replace_once(
    readme,
    '`reghdfe`、`winsor2`、`oneclick`、`coefplot` 等属于可选扩展。它们未安装时，Stata 官方命令、数据处理和核心工作台仍可使用；进入对应功能并点击运行时，程序再询问是否安装。',
    '`reghdfe`、`winsor2`、`oneclick`、`coefplot` 等属于外部扩展。它们未安装时，Stata 官方命令、数据处理和核心工作台仍可使用；工作台只检测是否已安装，不再自动安装。需要什么命令请按作者说明自行安装，随后在“外部命令”中重新检测。',
    "README external install policy",
)
write(readme_rel, readme)

print("HX_V157_PREP_OK")
