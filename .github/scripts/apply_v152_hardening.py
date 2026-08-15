from pathlib import Path


def replace_once(path, old, new):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'pattern not found in {path}: {old[:120]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Public launcher: bootstrap installer core in a tempfile, not the installed ado directory.
Path('hxinstall.do').write_text('''*! hxinstall 1.5.2  15aug2026
*! Short public launcher for hxempirical
version 17.0
set more off

args action source
if `"`action'"' == "" local action "auto"
local core_source "https://xiaowang5105.github.io/hxempirical"
if `"`source'"' != "" local core_source `"`source'"'

display as text _newline "hxempirical 安装管理"
display as text "正在启动安装器……"

tempfile hxinstaller_bootstrap
local old_timeout1 = c(timeout1)
local old_timeout2 = c(timeout2)
quietly set timeout1 10
quietly set timeout2 20
capture quietly copy `"`core_source'/hxinstaller.ado"' `"`hxinstaller_bootstrap'"', replace
local core_rc = _rc
quietly set timeout1 `old_timeout1'
quietly set timeout2 `old_timeout2'
if `core_rc' {
    display as error "无法取得安装器核心。请检查网络或使用浏览器离线包后重试。"
    exit 603
}

capture program drop hxinstaller
capture noisily do `"`hxinstaller_bootstrap'"'
local load_rc = _rc
if `load_rc' {
    display as error "安装器核心加载失败，Stata 返回码 r(`load_rc')。"
    exit `load_rc'
}

capture noisily hxinstaller `"`action'"' `"`source'"'
local install_rc = _rc
if `install_rc' display as error "hxempirical 操作未完成，Stata 返回码 r(`install_rc')。"
exit `install_rc'
''', encoding='utf-8')

# Installer hardening.
p = Path('hxinstaller.ado')
text = p.read_text(encoding='utf-8')
text = text.replace('*! hxinstaller 1.4.0  15aug2026', '*! hxinstaller 1.5.2  15aug2026', 1)
start = text.index('/* PERSONAL is normally user-writable and is searched before PLUS. */')
end_marker = '''capture quietly erase `"`probe'"'\n'''
end = text.index(end_marker, start) + len(end_marker)
new_target = '''/* Pick a persistent writable ado location. Prefer an existing HX install,
   then PERSONAL, then PLUS/h. */
local personal `"`c(sysdir_personal)'"'
local plus `"`c(sysdir_plus)'"'
local personal : subinstr local personal "\\" "/", all
local plus : subinstr local plus "\\" "/", all
if `"`personal'"' != "" & substr(`"`personal'"', -1, 1) != "/" local personal `"`personal'/"'
if `"`plus'"' != "" & substr(`"`plus'"', -1, 1) != "/" local plus `"`plus'/"'

local target ""
local target_kind ""

/* Reuse an existing managed location only when it lives under PERSONAL/PLUS
   and remains writable. Ignore source-tree copies found on adopath. */
capture quietly findfile hxempirical.ado
if !_rc {
    local existing `"`r(fn)'"'
    local existing : subinstr local existing "\\" "/", all
    local slash = strrpos(`"`existing'"', "/")
    if `slash' > 0 {
        local existing_dir = substr(`"`existing'"', 1, `slash')
        local allowed 0
        if `"`personal'"' != "" & strpos(lower(`"`existing_dir'"'), lower(`"`personal'"')) == 1 local allowed 1
        if `"`plus'"' != "" & strpos(lower(`"`existing_dir'"'), lower(`"`plus'"')) == 1 local allowed 1
        if `allowed' {
            local probe `"`existing_dir'__hxempirical_write_test.tmp"'
            tempname existing_probe
            capture quietly file open `existing_probe' using `"`probe'"', write text replace
            if !_rc {
                file write `existing_probe' "hxempirical write test" _n
                file close `existing_probe'
                capture quietly erase `"`probe'"'
                local target `"`existing_dir'"'
                if `"`personal'"' != "" & strpos(lower(`"`target'"'), lower(`"`personal'"')) == 1 local target_kind "PERSONAL"
                else local target_kind "PLUS"
            }
        }
    }
}

if `"`target'"' == "" & `"`personal'"' != "" {
    capture quietly mkdir `"`personal'"'
    local probe `"`personal'__hxempirical_write_test.tmp"'
    tempname personal_probe
    capture quietly file open `personal_probe' using `"`probe'"', write text replace
    if !_rc {
        file write `personal_probe' "hxempirical write test" _n
        file close `personal_probe'
        capture quietly erase `"`probe'"'
        local target `"`personal'"'
        local target_kind "PERSONAL"
    }
}

/* All managed files begin with h, so PLUS/h is a persistent standard ado path. */
if `"`target'"' == "" & `"`plus'"' != "" {
    capture quietly mkdir `"`plus'"'
    local plus_h `"`plus'h/"'
    capture quietly mkdir `"`plus_h'"'
    local probe `"`plus_h'__hxempirical_write_test.tmp"'
    tempname plus_probe
    capture quietly file open `plus_probe' using `"`probe'"', write text replace
    if !_rc {
        file write `plus_probe' "hxempirical write test" _n
        file close `plus_probe'
        capture quietly erase `"`probe'"'
        local target `"`plus_h'"'
        local target_kind "PLUS"
    }
}

if `"`target'"' == "" {
    noisily display as error "hxempirical 找不到可写的持久 ado 目录。"
    noisily display as text "已尝试 PERSONAL 和 PLUS/h。请运行 sysdir 检查目录权限。"
    exit 603
}
'''
text = text[:start] + new_target + text[end:]

# Parse bytes/hash from release index.
text = text.replace('''local parts ""\nif !`download_failed' {''', '''local parts ""\nlocal expected_bundle_bytes ""\nlocal expected_bundle_sha256 ""\nif !`download_failed' {''', 1)
old_loop = '''        gettoken index_tag index_rest : index_line
        if lower(`"`index_tag'"') == "f" {
            gettoken part_name index_unused : index_rest
            if `"`part_name'"' != "" local parts `"`parts' `part_name'"'
        }
        file read `index_handle' index_line
'''
new_loop = '''        gettoken index_tag index_rest : index_line
        if lower(`"`index_tag'"') == "f" {
            gettoken part_name index_unused : index_rest
            if `"`part_name'"' != "" local parts `"`parts' `part_name'"'
        }
        else if lower(`"`index_tag'"') == "d" {
            gettoken index_key index_value : index_rest
            if lower(`"`index_key'"') == "bytes" local expected_bundle_bytes = trim(`"`index_value'"')
            if lower(`"`index_key'"') == "sha256" local expected_bundle_sha256 = lower(trim(`"`index_value'"'))
        }
        file read `index_handle' index_line
'''
if old_loop not in text:
    raise SystemExit('release index loop not found')
text = text.replace(old_loop, new_loop, 1)

# Verify decoded archive before unzip.
unzip_marker = '''if !`download_failed' {
    local install_pwd `"`c(pwd)'"'
'''
verify = '''if !`download_failed' {
    tempfile bundle_verify
    local bundle_zip_java : subinstr local bundle_zip "\\" "\\\\", all
    local bundle_verify_java : subinstr local bundle_verify "\\" "\\\\", all
    capture java: java.nio.file.Files.writeString(java.nio.file.Paths.get("`bundle_verify_java'"), java.nio.file.Files.size(java.nio.file.Paths.get("`bundle_zip_java'")) + "\\n" + String.format("%064x", new java.math.BigInteger(1, java.security.MessageDigest.getInstance("SHA-256").digest(java.nio.file.Files.readAllBytes(java.nio.file.Paths.get("`bundle_zip_java'"))))))
    if _rc {
        local download_failed 1
        local failure_stage "发布包完整性校验"
    }
    else {
        tempname verify_in
        file open `verify_in' using `"`bundle_verify'"', read text
        file read `verify_in' actual_bundle_bytes
        file read `verify_in' actual_bundle_sha256
        file close `verify_in'
        local actual_bundle_bytes = trim(`"`actual_bundle_bytes'"')
        local actual_bundle_sha256 = lower(trim(`"`actual_bundle_sha256'"'))
        if `"`expected_bundle_bytes'"' == "" | `"`expected_bundle_sha256'"' == "" {
            local download_failed 1
            local failure_stage "发布索引缺少 bytes/sha256"
        }
        else if `"`actual_bundle_bytes'"' != `"`expected_bundle_bytes'"' {
            local download_failed 1
            local failure_stage "发布包大小校验失败"
        }
        else if `"`actual_bundle_sha256'"' != `"`expected_bundle_sha256'"' {
            local download_failed 1
            local failure_stage "发布包 SHA-256 校验失败"
        }
    }
}

if !`download_failed' {
    local install_pwd `"`c(pwd)'"'
'''
if unzip_marker not in text:
    raise SystemExit('unzip marker not found')
text = text.replace(unzip_marker, verify, 1)

# Do not make profile.do persistence a requirement when we had to install into PLUS/h.
old_menu = '''    capture noisily hxsetup, persist
    local menu_rc = _rc
'''
new_menu = '''    local menu_rc 0
    if `"`target_kind'"' == "PERSONAL" {
        capture noisily hxsetup, persist
        local menu_rc = _rc
    }
    else capture quietly hxmenu
'''
if text.count(old_menu) != 2:
    raise SystemExit(f'expected 2 menu blocks, got {text.count(old_menu)}')
text = text.replace(old_menu, new_menu, 2)
old_fast = '''    noisily display as text "启动命令：" as result "hxempirical"
    if `menu_rc' noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"
    exit 0
'''
new_fast = '''    noisily display as text "启动命令：" as result "hxempirical"
    if `"`target_kind'"' == "PLUS" noisily display as text "当前安装位置：PLUS/h（PERSONAL 不可写）。"
    else if `menu_rc' noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"
    exit 0
'''
if old_fast not in text:
    raise SystemExit('fast-exit menu block not found')
text = text.replace(old_fast, new_fast, 1)
old_tail = '''if `menu_rc' {
    noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"
}
else noisily display as text "顶部入口：" as result "用户(U) > 我的实证工具箱"
'''
new_tail = '''if `"`target_kind'"' == "PLUS" {
    noisily display as text "安装目录回退：" as result "PERSONAL 不可写，已安装到 PLUS/h。"
    noisily display as text "本次会话可直接运行 hxempirical；持久菜单未写入 PERSONAL/profile.do。"
}
else if `menu_rc' {
    noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"
}
else noisily display as text "顶部入口：" as result "用户(U) > 我的实证工具箱"
'''
if old_tail not in text:
    raise SystemExit('final menu block not found')
text = text.replace(old_tail, new_tail, 1)
p.write_text(text, encoding='utf-8')

# Version metadata + accurate classic fallback wording.
p = Path('hxempirical.ado')
text = p.read_text(encoding='utf-8')
text = text.replace('*! hxempirical 1.5.1  15aug2026', '*! hxempirical 1.5.2  15aug2026', 1)
text = text.replace('"1.5.1"', '"1.5.2"')
text = text.replace('\\u7ecf\\u5178 .dlg \\u81ea\\u52a8\\u540e\\u5907', '\\u7ecf\\u5178 .dlg \\u624b\\u52a8\\u540e\\u5907')
p.write_text(text, encoding='utf-8')
replace_once('hxempirical.pkg', 'd Version 1.5.1', 'd Version 1.5.2')

p = Path('hxempirical.sthlp')
text = p.read_text(encoding='utf-8').replace('1.5.1', '1.5.2')
if '{p 8 16 2}{cmd:hxempirical repair}' not in text:
    text = text.replace('{p 8 16 2}{cmd:hxempirical update}\n', '{p 8 16 2}{cmd:hxempirical update}\n{p 8 16 2}{cmd:hxempirical repair}\n', 1)
p.write_text(text, encoding='utf-8')

# Java: version + compact chooser cleanup.
p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
text = p.read_text(encoding='utf-8')
text = text.replace('public static final String VERSION = "1.5.1";', 'public static final String VERSION = "1.5.2";', 1)
old_advanced = '''         JButton advanced = this.refButton("高级筛选", false);
         advanced.addActionListener(e -> {
            this.chooserFilterMode = "进阶";
            this.chooserPage = 0;
            this.refreshChooserFilterStyles();
            this.renderChooserCatalog();
         });
         searchRow.add(this.chooserSearchField, BorderLayout.CENTER);
         searchRow.add(advanced, BorderLayout.EAST);
'''
if old_advanced not in text:
    raise SystemExit('duplicate advanced-filter block not found')
text = text.replace(old_advanced, '         searchRow.add(this.chooserSearchField, BorderLayout.CENTER);\n', 1)
text = text.replace('scroll.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);\n         int tableHeight = 31 + commands.size() * 38;', 'scroll.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);\n         int tableHeight = 31 + commands.size() * 38;', 1)
p.write_text(text, encoding='utf-8')

# Documentation.
p = Path('README.md')
text = p.read_text(encoding='utf-8')
text = text.replace('**当前发布版本：1.5.1**', '**当前发布版本：1.5.2**', 1)
text = text.replace('**上次修改时间：2026-08-15 01:00（UTC+8）**', '**上次修改时间：2026-08-15 17:10（UTC+8）**', 1)
anchor = '安装器先完整取得并校验发布包，再统一写入正式目录；任何写入步骤失败都会恢复原有文件。Windows 和 macOS 使用相同的在线入口和离线包。'
if anchor not in text:
    raise SystemExit('README install anchor missing')
text = text.replace(anchor, anchor + '\n\n安装位置优先使用 `PERSONAL`。如果 `PERSONAL` 因权限策略不可写，安装器会自动尝试 Stata 已搜索的 `PLUS/h`；核心安装不再因为 `PERSONAL/profile.do` 权限异常直接失败。回退到 `PLUS/h` 时不会强行改写 `profile.do`，启动工具箱可直接运行 `hxempirical`。', 1)
marker = '## 版本记录\n\n### 1.5.1（当前版本）'
entry = '''## 版本记录\n\n### 1.5.2（当前版本）\n\n**发布时间**：2026-08-15 17:10（UTC+8）\n\n**修改内容**：\n\n- 安装位置新增 `PERSONAL → PLUS/h` 自动回退；`PERSONAL` 因权限策略不可写时不再直接终止核心安装。\n- 公开 `hxinstall.do` 从临时文件加载安装核心，安装前不再提前覆盖已安装的 `hxinstaller.ado`。\n- 在线分段发布包在解压前核验 index 中的字节数和 SHA-256。\n- 命令目录移除与“进阶”重复的“高级筛选”按钮，窄窗口允许横向滚动命令表格。\n- `about` 将经典 `.dlg` 明确为手动兼容后备；新增发布一致性 CI。\n\n### 1.5.1'''
if marker not in text:
    raise SystemExit('README version marker missing')
text = text.replace(marker, entry, 1)
p.write_text(text, encoding='utf-8')

p = Path('INSTALL.md')
text = p.read_text(encoding='utf-8')
text = text.replace('都会写入当前用户的 `PERSONAL` ado 目录。', '优先写入当前用户的 `PERSONAL` ado 目录；如果该目录不可写，会自动回退到 Stata 已搜索的 `PLUS/h`。', 1)
old = 'Windows 和 macOS 使用同一发布包。安装器会创建缺失的 `PERSONAL` 目录，并在写文件前验证权限。'
new = 'Windows 和 macOS 使用同一发布包。安装器会创建缺失的 `PERSONAL` 目录并验证写权限；若 `PERSONAL` 不可写，会继续检查 `PLUS/h`。只有两个持久 ado 位置都不可写时才返回 `r(603)`。使用 `PLUS/h` 回退时不会强行写入 `PERSONAL/profile.do`，因此菜单持久化会跳过，但 `hxempirical` 命令本身可正常使用。'
if old not in text:
    raise SystemExit('INSTALL permission paragraph missing')
text = text.replace(old, new, 1)
p.write_text(text, encoding='utf-8')

# Permanent release verifier.
Path('tools/verify_release.py').write_text('''from pathlib import Path\nimport base64, hashlib, sys, zipfile\nroot = Path(__file__).resolve().parents[1]\ndef fail(msg):\n    print("HX_RELEASE_VERIFY_FAIL:", msg, file=sys.stderr); raise SystemExit(1)\npkg=(root/"hxempirical.pkg").read_text(encoding="utf-8").splitlines()\nmanaged=[x.split(None,1)[1].strip() for x in pkg if x.startswith("f ")]\nversions=[x.split(None,2)[2].strip() for x in pkg if x.startswith("d Version ")]\nif len(versions)!=1: fail("package version missing/duplicated")\nversion=versions[0]\nfor rel in managed:\n    if not (root/rel).is_file(): fail("managed file missing: "+rel)\nchecks={"README.md":f"当前发布版本：{version}","hxempirical.ado":f"\\\"{version}\\\"","hxempirical.sthlp":f"version {version}","src/main/java/com/hexie/stata/HxWorkbench.java":f"VERSION = \\\"{version}\\\""}\nfor rel,needle in checks.items():\n    if needle not in (root/rel).read_text(encoding="utf-8"): fail("version mismatch: "+rel)\nmeta={}; parts=[]\nfor line in (root/"hxempirical-release.index").read_text(encoding="utf-8").splitlines():\n    if line.startswith("d "):\n        _,k,v=line.split(None,2); meta[k]=v.strip()\n    elif line.startswith("f "): parts.append(line.split(None,1)[1].strip())\nif not {"archive","bytes","sha256","parts"} <= set(meta): fail("release index metadata incomplete")\nif int(meta["parts"])!=len(parts): fail("part count mismatch")\nraw=(root/meta["archive"]).read_bytes()\nif len(raw)!=int(meta["bytes"]): fail("zip byte count mismatch")\nif hashlib.sha256(raw).hexdigest()!=meta["sha256"].lower(): fail("zip sha256 mismatch")\nb64="".join("".join((root/p).read_text(encoding="utf-8").split()) for p in parts)\nif base64.b64decode(b64,validate=True)!=raw: fail("base64 parts mismatch")\nwith zipfile.ZipFile(root/meta["archive"]) as z: names=set(z.namelist())\nexpected=set(managed)|{"hxempirical.pkg","hxinstall.do","hxinstall_offline.do","INSTALL.md"}\nif names!=expected: fail(f"zip manifest mismatch missing={sorted(expected-names)} extra={sorted(names-expected)}")\nprint(f"HX_RELEASE_VERIFY_OK version={version} managed={len(managed)} zip_files={len(names)} parts={len(parts)} sha256={meta['sha256']}")\n''', encoding='utf-8')

Path('.github/workflows/ci.yml').write_text('''name: HX release consistency\n\non:\n  push:\n    branches: [main]\n  pull_request:\n    branches: [main]\n\npermissions:\n  contents: read\n\njobs:\n  release-consistency:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with:\n          python-version: "3.12"\n      - name: Verify managed release\n        run: python tools/verify_release.py\n      - name: Check JAR Java level\n        run: |\n          python - <<'PY'\n          import zipfile, struct\n          with zipfile.ZipFile('hxworkbench.jar') as z:\n              classes=[n for n in z.namelist() if n.endswith('.class')]\n              assert classes\n              majors=set()\n              for n in classes:\n                  magic,minor,major=struct.unpack('>IHH',z.read(n)[:8]); assert magic==0xCAFEBABE; majors.add(major)\n              assert max(majors)<=55, sorted(majors)\n              print('HX_JAR_LEVEL_OK',sorted(majors))\n          PY\n''', encoding='utf-8')

print('PATCH_V152_OK')
