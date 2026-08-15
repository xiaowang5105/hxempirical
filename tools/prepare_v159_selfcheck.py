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


# Java: version bump and remove one Stata `which` call per discovered ado file.
java_rel = "src/main/java/com/hexie/stata/HxWorkbench.java"
java = read(java_rel)
java = replace_once(java, 'public static final String VERSION = "1.5.8";', 'public static final String VERSION = "1.5.9";', "java version")
old_loop = '''         for (String command : discovered) {
            if (installed.contains(command)) continue;
            if (HxWorkbench.StataBridge.execute("quietly which " + command, false) == 0) installed.add(command);
         }
         return new ArrayList<>(installed);'''
new_loop = '''         // A .ado file physically present under a user ado directory is already user-installed.
         // Do not cross the Java -> Stata bridge once per file; large PLUS trees can contain
         // hundreds of package helper programs and would otherwise make this navigation feel frozen.
         for (String command : discovered) {
            if (!installed.contains(command)) installed.add(command);
         }
         return new ArrayList<>(installed);'''
java = replace_once(java, old_loop, new_loop, "external discovery performance loop")
write(java_rel, java)

# Public Stata/version surfaces.
for rel in ["hxempirical.ado", "hxempirical.pkg", "hxinstall.do", "hxinstaller.ado"]:
    text = read(rel).replace("1.5.8", "1.5.9")
    write(rel, text)

# Help: remove stale auto-install promises and stale author version.
help_rel = "hxempirical.sthlp"
hlp = read(help_rel).replace("1.5.8", "1.5.9")
hlp = replace_once(
    hlp,
    '''External commands are user-managed. {bf:外部命令} scans Stata's user ado directories
({bf:PLUS}, {bf:PERSONAL}, and {bf:OLDPLACE}), confirms discovered .ado names with {cmd:which}, and lists
the commands that are actually callable. The workbench does not automatically install them. Install any
needed command using its author's instructions, then reopen {bf:外部命令} to rescan it.''',
    '''External commands are user-managed. {bf:外部命令} scans Stata's user ado directories
({bf:PLUS}, {bf:PERSONAL}, and {bf:OLDPLACE}) for installed .ado programs and lists them directly.
A small curated set of common external commands is also checked with {cmd:which} so commands installed
outside those standard user directories can still be recognized. The workbench never installs external
commands. Install what you need using the command author's instructions, then reopen {bf:外部命令} to rescan.''',
    "help external discovery paragraph",
)
old_optional = '''{pstd}
{cmd:reghdfe}, {cmd:winsor2}, {cmd:ivreghdfe}, {cmd:ppmlhdfe},
{cmd:oneclick}, {cmd:oneclick_robustness}, {cmd:coefplot}, and {cmd:event_plot} are optional.
The package checks for optional commands only when needed. Commands with a
verified SSC source (including {cmd:oneclick} and {cmd:event_plot}) can be
installed after user confirmation. {cmd:oneclick_robustness} is detected when
present but is not downloaded from an unverified source. Nothing is downloaded
merely by installing {cmd:hxempirical}.

{pstd}
Optional commands are not core-health failures. {cmd:hxempirical doctor}
reports the core workbench separately from these extensions. A command page can
be inspected without installing its extension; installation is offered only
when the user attempts to run that command.

{phang2}{cmd:. hxempirical doctor}
{phang2}{cmd:. hxempirical install reghdfe}'''
new_optional = '''{pstd}
{cmd:reghdfe}, {cmd:winsor2}, {cmd:ivreghdfe}, {cmd:ppmlhdfe},
{cmd:oneclick}, {cmd:oneclick_robustness}, {cmd:coefplot}, and {cmd:event_plot} are external extensions.
They are user-managed: hxempirical checks whether they are present but does not install them.
Install any command you need using its author's instructions, then reopen {bf:外部命令} to rescan.

{pstd}
Missing external commands are not core-health failures. {cmd:hxempirical doctor}
reports the core workbench separately from these extensions. A command page can
be inspected even when its extension is absent; attempting to run a missing external
command produces an install-it-yourself notice rather than an automatic installer.

{phang2}{cmd:. hxempirical doctor}'''
hlp = replace_once(hlp, old_optional, new_optional, "help optional commands section")
hlp = replace_once(
    hlp,
    '''external command is run inside a unique temporary working directory, so a user
file named {cmd:subset.dta} in the active project directory is never renamed,
erased, or overwritten. The dataset already in Stata memory is not replaced. A selected result row can be sent to
the corresponding ordinary regression page for review without automatic
execution. {cmd:oneclick} can be installed from SSC on request.
{cmd:oneclick_robustness} is also treated as an external command; hxempirical
does not invent an unverified download source for it.''',
    '''external command is run inside a unique temporary working directory, so a user
file named {cmd:subset.dta} in the active project directory is never renamed,
erased, or overwritten. The dataset already in Stata memory is not replaced. A selected result row can be sent to
the corresponding ordinary regression page for review without automatic
execution. If {cmd:oneclick} is absent, install it yourself using the author's published source before returning to the workbench.
{cmd:oneclick_robustness} is also treated as an external command; hxempirical
does not invent an unverified download source for it.''',
    "help oneclick manual install paragraph",
)
hlp = re.sub(r'HX empirical workbench, package version [0-9]+\.[0-9]+\.[0-9]+\.', 'HX empirical workbench, package version 1.5.9.', hlp, count=1)
write(help_rel, hlp)

# INSTALL guide: current package version and manual-only third-party policy.
install_rel = "INSTALL.md"
install = read(install_rel).replace("1.5.8", "1.5.9")
install = replace_once(
    install,
    '`reghdfe`、`winsor2`、`ivreghdfe`、`ppmlhdfe`、`oneclick`、`oneclick_robustness`、`coefplot`、`event_plot` 是可选扩展。它们缺失时，核心工作台和 Stata 官方命令仍然可用。 `oneclick` 可由 hxempirical 从 SSC 按 `tuples → oneclick` 顺序安装；`oneclick_robustness` 当前没有配置经过验证的 SSC 自动安装源，需要按作者发布说明手动安装。',
    '`reghdfe`、`winsor2`、`ivreghdfe`、`ppmlhdfe`、`oneclick`、`oneclick_robustness`、`coefplot`、`event_plot` 等属于外部扩展。它们缺失时，核心工作台和 Stata 官方命令仍然可用。hxempirical 只检测和展示，不负责安装；需要什么命令请按作者发布说明自行安装，安装完成后重新进入“外部命令”扫描。',
    "INSTALL external command policy",
)
write(install_rel, install)

# README: new release note; keep historical release notes as historical facts.
readme_rel = "README.md"
readme = read(readme_rel)
readme = replace_once(readme, "**当前发布版本：1.5.8**", "**当前发布版本：1.5.9**", "README current version")
readme = replace_once(readme, "**上次修改时间：2026-08-15 20:22（UTC+8）**", "**上次修改时间：2026-08-15 20:40（UTC+8）**", "README timestamp")
anchor = "### 1.5.8 外部命令自动发现\n"
section = '''### 1.5.9 自查修复：外部命令扫描与文档一致性

- 优化“外部命令”扫描：`PLUS` / `PERSONAL` / `OLDPLACE` 中实际存在的 `.ado` 文件直接计入，不再对每个文件逐条跨 Java→Stata 执行 `which`，避免安装包较多时进入页面明显卡顿。
- 常用外部命令仍保留一次 `which` 补充检测，因此放在标准用户 ado 目录之外、但 Stata 当前可找到的常见命令仍可识别。
- 修复 `help hxempirical` 和 `INSTALL.md` 中残留的旧“自动安装外部命令”说明；当前统一口径是：HX 只检测、统计、搜索和调用，第三方命令由用户自行安装。
- CI 新增文档与扫描性能防回归检查，防止以后再次出现“程序不安装，但帮助文件说会安装”或“每个 `.ado` 都单独 `which`”的问题。

'''
if anchor not in readme:
    raise RuntimeError("README v1.5.8 anchor not found")
readme = readme.replace(anchor, section + anchor, 1)
write(readme_rel, readme)

# Strengthen permanent static checks so both self-check findings cannot regress.
verify_rel = "tools/verify_static_contracts.py"
verify = read(verify_rel)
verify = replace_once(verify, 'readme = read("README.md")\njava = read("src/main/java/com/hexie/stata/HxWorkbench.java")', 'readme = read("README.md")\nhelp_text = read("hxempirical.sthlp")\ninstall_doc = read("INSTALL.md")\npkg = read("hxempirical.pkg")\njava = read("src/main/java/com/hexie/stata/HxWorkbench.java")', "static verifier inputs")
needle = '''if "hxempirical 不再自动安装第三方命令" not in entry:
    fail("public hxempirical install compatibility path must not install packages")
'''
insert = needle + '''
# User-ado discovery must not execute one Stata `which` call per scanned file.
discovery_start = java.find("private List<String> discoverInstalledExternalCommands")
discovery_end = java.find("return new ArrayList<>(installed);", discovery_start)
if discovery_start < 0 or discovery_end < 0:
    fail("external discovery method not found")
discovery_block = java[discovery_start:discovery_end]
if discovery_block.count("quietly which") != 1:
    fail("external discovery must use which only for the curated fast-path, not once per discovered ado file")
if "for (String command : discovered)" not in discovery_block:
    fail("external discovery loop missing")

# Current user-facing docs must not advertise the removed auto-install behavior.
for stale in (
    "can be installed after user confirmation",
    "installation is offered only",
    "hxempirical install reghdfe",
    "can be installed from SSC on request",
):
    if stale in help_text:
        fail(f"help still advertises removed auto-install behavior: {stale}")
if "hxempirical 只检测和展示，不负责安装" not in install_doc:
    fail("INSTALL.md must state that external commands are user-installed")
version_match = re.search(r"^d Version ([0-9]+\\.[0-9]+\\.[0-9]+)$", pkg, re.MULTILINE)
if not version_match:
    fail("package version not found")
current_version = version_match.group(1)
if f"package version {current_version}." not in help_text:
    fail("help author/footer version is stale")
'''
if needle not in verify:
    raise RuntimeError("static verifier insertion point missing")
verify = verify.replace(needle, insert, 1)
verify = replace_once(
    verify,
    '"ui_external_manual_only=1 external_user_ado_scan=1 spreadsheet_editable=1 "',
    '"ui_external_manual_only=1 external_user_ado_scan=1 external_scan_fastpath=1 docs_manual_only=1 spreadsheet_editable=1 "',
    "static verifier success marker",
)
write(verify_rel, verify)

print("HX_V159_SELF_CHECK_PREP_OK")
