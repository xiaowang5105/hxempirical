from pathlib import Path
import re

ROOT = Path('.')


def replace_once(path, old, new):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'pattern not found in {path}: {old[:100]!r}')
    text = text.replace(old, new, 1)
    p.write_text(text, encoding='utf-8')


def replace_all(path, old, new):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'pattern not found in {path}: {old!r}')
    p.write_text(text.replace(old, new), encoding='utf-8')

# 1) Public launcher: keep the installer core out of PERSONAL until the transaction commits.
(Path('hxinstall.do')).write_text(r'''*! hxinstall 1.5.2  15aug2026
*! Short public launcher for hxempirical
version 17.0
set more off

args action source
if `"`action'"' == "" local action "auto"
local core_source "https://xiaowang5105.github.io/hxempirical"
if `"`source'"' != "" local core_source `"`source'"'

display as text _newline "hxempirical 安装管理"
display as text "正在启动安装器……"

/* Bootstrap into a temporary file.  The installed copy of hxinstaller.ado is
   replaced only inside the transactional commit performed by hxinstaller. */
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

# 2) Installer: version + writable target fallback.
p = Path('hxinstaller.ado')
text = p.read_text(encoding='utf-8')
text = text.replace('*! hxinstaller 1.4.0  15aug2026', '*! hxinstaller 1.5.2  15aug2026', 1)
old_target = r'''/* PERSONAL is normally user-writable and is searched before PLUS. */
local target `"`c(sysdir_personal)'"'
if `"`target'"' == "" {
    noisily display as error "Stata 没有返回 PERSONAL ado 目录。请先运行 sysdir 检查安装环境。"
    exit 603
}
capture quietly mkdir `"`target'"'
local lastchar = substr(`"`target'"', strlen(`"`target'"'), 1)
if !inlist(`"`lastchar'"', "/", "\\") local target `"`target'/"'

/* Fail early when PERSONAL is not writable. */
local probe `"`target'__hxempirical_write_test.tmp"'
tempname probehandle
capture quietly file open `probehandle' using `"`probe'"', write text replace
if _rc {
    noisily display as error "无法写入 Stata PERSONAL 目录：`target'"
    noisily display as text  "请运行 sysdir 查看目录设置，或联系管理员检查该目录权限。"
    exit 603
}
file write `probehandle' "hxempirical write test" _n
file close `probehandle'
capture quietly erase `"`probe'"'
'''
new_target = r'''/* Pick a persistent writable ado location.  Prefer an existing HX install,
   then PERSONAL, then PLUS/h.  This lets locked-down macOS/Windows accounts
   install even when their configured PERSONAL directory is not writable. */
local personal `"`c(sysdir_personal)'"'
local plus `"`c(sysdir_plus)'"'
local personal : subinstr local personal "\\" "/", all
local plus : subinstr local plus "\\" "/", all
if `"`personal'"' != "" & substr(`"`personal'"', -1, 1) != "/" local personal `"`personal'/"'
if `"`plus'"' != "" & substr(`"`plus'"', -1, 1) != "/" local plus `"`plus'/"'

local target ""
local target_kind ""

/* Reuse an existing managed location when it is inside PERSONAL or PLUS and
   remains writable.  Ignore a repository/current-directory copy on adopath. */
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

/* Normal per-user installation. */
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

/* Fallback to Stata's searched PLUS/h directory.  Every managed HX file starts
   with h, so this remains a standard persistent ado-path location. */
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
    noisily display as text "如果这是学校/单位受管电脑，请使用有写权限的用户账户或联系管理员。"
    exit 603
}
'''
if old_target not in text:
    raise SystemExit('installer target block not found')
text = text.replace(old_target, new_target, 1)

# Parse expected archive bytes/hash from release index.
old_index_init = '''local parts ""\nif !`download_failed' {'''
new_index_init = '''local parts ""\nlocal expected_bundle_bytes ""\nlocal expected_bundle_sha256 ""\nif !`download_failed' {'''
if old_index_init not in text:
    raise SystemExit('index init marker not found')
text = text.replace(old_index_init, new_index_init, 1)

old_index_loop = r'''        gettoken index_tag index_rest : index_line
        if lower(`"`index_tag'"') == "f" {
            gettoken part_name index_unused : index_rest
            if `"`part_name'"' != "" local parts `"`parts' `part_name'"'
        }
        file read `index_handle' index_line
'''
new_index_loop = r'''        gettoken index_tag index_rest : index_line
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
if old_index_loop not in text:
    raise SystemExit('index parse loop not found')
text = text.replace(old_index_loop, new_index_loop, 1)

# Verify decoded ZIP before unzip.
decode_marker = r'''if !`download_failed' {
    local install_pwd `"`c(pwd)'"'
'''
verify_block = r'''if !`download_failed' {
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
if decode_marker not in text:
    raise SystemExit('decode->unzip marker not found')
text = text.replace(decode_marker, verify_block, 1)

# Menu persistence: only require profile persistence for PERSONAL; PLUS fallback stays usable without it.
old_fast_menu = '''    capture noisily hxsetup, persist\n    local menu_rc = _rc\n'''
new_fast_menu = '''    local menu_rc 0\n    if `"`target_kind'"' == "PERSONAL" {\n        capture noisily hxsetup, persist\n        local menu_rc = _rc\n    }\n    else capture quietly hxmenu\n'''
if text.count(old_fast_menu) < 2:
    raise SystemExit('expected two menu persistence blocks')
text = text.replace(old_fast_menu, new_fast_menu, 2)

old_menu_tail = '''if `menu_rc' {\n    noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"\n}\nelse noisily display as text "顶部入口：" as result "用户(U) > 我的实证工具箱"\n'''
new_menu_tail = '''if `"`target_kind'"' == "PLUS" {\n    noisily display as text "安装目录回退：" as result "PERSONAL 不可写，已安装到 PLUS/h。"\n    noisily display as text "本次会话可直接运行 hxempirical；持久菜单未写入 PERSONAL/profile.do。"\n}\nelse if `menu_rc' {\n    noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"\n}\nelse noisily display as text "顶部入口：" as result "用户(U) > 我的实证工具箱"\n'''
if old_menu_tail not in text:
    raise SystemExit('menu tail not found')
text = text.replace(old_menu_tail, new_menu_tail, 1)

# Fast-exit message should also explain PLUS fallback.
old_fast_tail = '''    noisily display as text "启动命令：" as result "hxempirical"\n    if `menu_rc' noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"\n    exit 0\n'''
new_fast_tail = '''    noisily display as text "启动命令：" as result "hxempirical"\n    if `"`target_kind'"' == "PLUS" noisily display as text "当前安装位置：PLUS/h（PERSONAL 不可写）。"\n    else if `menu_rc' noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"\n    exit 0\n'''
if old_fast_tail not in text:
    raise SystemExit('fast tail not found')
text = text.replace(old_fast_tail, new_fast_tail, 1)
p.write_text(text, encoding='utf-8')

# 3) Public entry point and help/version metadata.
p = Path('hxempirical.ado')
text = p.read_text(encoding='utf-8')
text = text.replace('*! hxempirical 1.5.1  15aug2026', '*! hxempirical 1.5.2  15aug2026', 1)
text = text.replace('"1.5.1"', '"1.5.2"')
text = text.replace('Java \\u5355\\u7a97\\u53e3\\u5de5\\u4f5c\\u53f0\\uff1b\\u7ecf\\u5178 .dlg \\u81ea\\u52a8\\u540e\\u5907', 'Java \\u5355\\u7a97\\u53e3\\u5de5\\u4f5c\\u53f0\\uff1b\\u7ecf\\u5178 .dlg \\u624b\\u52a8\\u540e\\u5907')
p.write_text(text, encoding='utf-8')

replace_once('hxempirical.pkg', 'd Version 1.5.1', 'd Version 1.5.2')
replace_all('hxempirical.sthlp', '1.5.1', '1.5.2')
replace_once('hxempirical.sthlp', '{p 8 16 2}{cmd:hxempirical update}\n', '{p 8 16 2}{cmd:hxempirical update}\n{p 8 16 2}{cmd:hxempirical repair}\n')

# 4) Java: version, remove duplicate "高级筛选" alias, and allow narrow-window horizontal scrolling.
p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
text = p.read_text(encoding='utf-8')
text = text.replace('public static final String VERSION = "1.5.1";', 'public static final String VERSION = "1.5.2";', 1)
old_advanced = '''         JButton advanced = this.refButton("高级筛选", false);\n         advanced.addActionListener(e -> {\n            this.chooserFilterMode = "进阶";\n            this.chooserPage = 0;\n            this.refreshChooserFilterStyles();\n            this.renderChooserCatalog();\n         });\n         searchRow.add(this.chooserSearchField, BorderLayout.CENTER);\n         searchRow.add(advanced, BorderLayout.EAST);\n'''
new_advanced = '''         searchRow.add(this.chooserSearchField, BorderLayout.CENTER);\n'''
if old_advanced not in text:
    raise SystemExit('advanced filter alias block not found')
text = text.replace(old_advanced, new_advanced, 1)
text = text.replace('scroll.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);\n         int tableHeight = 31 + commands.size() * 38;', 'scroll.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);\n         int tableHeight = 31 + commands.size() * 38;', 1)
p.write_text(text, encoding='utf-8')

# 5) Documentation: current version + honest installation fallback.
p = Path('README.md')
text = p.read_text(encoding='utf-8')
text = text.replace('**当前发布版本：1.5.1**', '**当前发布版本：1.5.2**', 1)
text = text.replace('**上次修改时间：2026-08-15 01:00（UTC+8）**', '**上次修改时间：2026-08-15 17:10（UTC+8）**', 1)
needle = '安装器先完整取得并校验发布包，再统一写入正式目录；任何写入步骤失败都会恢复原有文件。Windows 和 macOS 使用相同的在线入口和离线包。'
replacement = needle + '\n\n安装位置优先使用当前用户的 `PERSONAL`。如果 `PERSONAL` 因权限策略不可写，安装器会自动尝试 Stata 已在 `adopath` 中搜索的 `PLUS/h`，因此不会仅因为 `PERSONAL/profile.do` 权限异常而阻断核心安装；此时不会强行修改 `profile.do`，启动工具箱可直接运行 `hxempirical`。'
if needle not in text:
    raise SystemExit('README installer paragraph not found')
text = text.replace(needle, replacement, 1)
marker = '## 版本记录\n\n### 1.5.1（当前版本）'
entry = '''## 版本记录\n\n### 1.5.2（当前版本）\n\n**发布时间**：2026-08-15 17:10（UTC+8）\n\n**修改内容**：\n\n- 安装位置新增 `PERSONAL → PLUS/h` 自动回退；`PERSONAL` 因权限策略不可写时不再直接终止核心安装。\n- 公开 `hxinstall.do` 改为从临时文件加载安装核心，安装前不再提前覆盖已安装的 `hxinstaller.ado`。\n- 在线分段发布包在解压前同时核验 index 中的字节数和 SHA-256，损坏或截断下载不会进入安装阶段。\n- 命令目录移除与“进阶”重复的“高级筛选”按钮，窄窗口允许横向滚动命令表格。\n- `about` 将经典 `.dlg` 明确为手动兼容后备；新增发布一致性 CI。\n\n### 1.5.1'''
if marker not in text:
    raise SystemExit('README version marker not found')
text = text.replace(marker, entry, 1)
p.write_text(text, encoding='utf-8')

p = Path('INSTALL.md')
text = p.read_text(encoding='utf-8')
text = text.replace('都会写入当前用户的 `PERSONAL` ado 目录。', '优先写入当前用户的 `PERSONAL` ado 目录；如果该目录不可写，会自动回退到 Stata 已搜索的 `PLUS/h`。', 1)
needle = 'Windows 和 macOS 使用同一发布包。安装器会创建缺失的 `PERSONAL` 目录，并在写文件前验证权限。'
replacement = 'Windows 和 macOS 使用同一发布包。安装器会创建缺失的 `PERSONAL` 目录并验证写权限；若 `PERSONAL` 不可写，会继续检查 `PLUS/h`。只有两个持久 ado 位置都不可写时才返回 `r(603)`。使用 `PLUS/h` 回退时不会强行写入 `PERSONAL/profile.do`，因此菜单持久化会跳过，但 `hxempirical` 命令本身可正常使用。'
if needle not in text:
    raise SystemExit('INSTALL mac paragraph not found')
text = text.replace(needle, replacement, 1)
p.write_text(text, encoding='utf-8')

# 6) Permanent release verifier + CI.
Path('tools/verify_release.py').write_text(r'''from pathlib import Path
import base64, hashlib, re, sys, zipfile

root = Path(__file__).resolve().parents[1]

def fail(msg):
    print(f'HX_RELEASE_VERIFY_FAIL: {msg}', file=sys.stderr)
    raise SystemExit(1)

pkg = (root / 'hxempirical.pkg').read_text(encoding='utf-8').splitlines()
managed = [line.split(None, 1)[1].strip() for line in pkg if line.startswith('f ')]
version_lines = [line.split(None, 2)[2].strip() for line in pkg if line.startswith('d Version ')]
if len(version_lines) != 1:
    fail('package version missing or duplicated')
version = version_lines[0]
for rel in managed:
    if not (root / rel).is_file():
        fail(f'managed file missing: {rel}')

checks = {
    'README.md': f'当前发布版本：{version}',
    'hxempirical.ado': f'版本：") as result "{version}"',
    'hxempirical.sthlp': f'version {version}',
    'src/main/java/com/hexie/stata/HxWorkbench.java': f'VERSION = "{version}"',
}
for rel, needle in checks.items():
    if needle not in (root / rel).read_text(encoding='utf-8'):
        fail(f'version mismatch in {rel}: expected {version}')

index_lines = (root / 'hxempirical-release.index').read_text(encoding='utf-8').splitlines()
meta = {}
parts = []
for line in index_lines:
    if line.startswith('d '):
        _, key, value = line.split(None, 2)
        meta[key] = value.strip()
    elif line.startswith('f '):
        parts.append(line.split(None, 1)[1].strip())
if not {'archive','bytes','sha256','parts'} <= meta.keys():
    fail('release index metadata incomplete')
if int(meta['parts']) != len(parts):
    fail('release index part count mismatch')
archive = root / meta['archive']
if not archive.is_file():
    fail('release zip missing')
raw = archive.read_bytes()
if len(raw) != int(meta['bytes']):
    fail('release zip byte count mismatch')
if hashlib.sha256(raw).hexdigest() != meta['sha256'].lower():
    fail('release zip sha256 mismatch')

b64 = ''.join(''.join((root / part).read_text(encoding='utf-8').split()) for part in parts)
try:
    rebuilt = base64.b64decode(b64, validate=True)
except Exception as exc:
    fail(f'base64 parts invalid: {exc}')
if rebuilt != raw:
    fail('base64 parts do not reproduce release zip')

with zipfile.ZipFile(archive) as zf:
    names = set(zf.namelist())
expected_bundle = set(managed) | {'hxempirical.pkg','hxinstall.do','hxinstall_offline.do','INSTALL.md'}
missing = expected_bundle - names
extra = names - expected_bundle
if missing:
    fail('zip missing: ' + ', '.join(sorted(missing)))
if extra:
    fail('zip has unmanaged files: ' + ', '.join(sorted(extra)))
print(f'HX_RELEASE_VERIFY_OK version={version} managed={len(managed)} zip_files={len(names)} parts={len(parts)} sha256={meta["sha256"]}')
''', encoding='utf-8')

Path('.github/workflows/ci.yml').write_text(r'''name: HX release consistency

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  release-consistency:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Verify managed release
        run: python tools/verify_release.py
      - name: Check whitespace
        run: git diff --check HEAD~1 HEAD || git diff --check
      - name: Check JAR Java level
        run: |
          python - <<'PY'
          import zipfile, struct
          with zipfile.ZipFile('hxworkbench.jar') as z:
              classes = [n for n in z.namelist() if n.endswith('.class')]
              assert classes, 'jar contains no class files'
              majors = set()
              for name in classes:
                  data = z.read(name)[:8]
                  magic, minor, major = struct.unpack('>IHH', data)
                  assert magic == 0xCAFEBABE
                  majors.add(major)
              assert max(majors) <= 55, f'Java class level too new: {sorted(majors)}'
              print('HX_JAR_LEVEL_OK', sorted(majors))
          PY
''', encoding='utf-8')

print('PATCH_V152_OK')
