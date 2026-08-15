from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
OLD = "1.5.9"
NEW = "1.5.10"


def read(path):
    return (root / path).read_text(encoding="utf-8")


def write(path, text):
    (root / path).write_text(text, encoding="utf-8", newline="\n")


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 occurrence, found {count}")
    return text.replace(old, new, 1)

# Version surfaces.
for path in ["hxempirical.ado", "hxempirical.sthlp", "hxinstall.do", "hxinstaller.ado", "src/main/java/com/hexie/stata/HxWorkbench.java"]:
    text = read(path)
    if OLD not in text:
        raise SystemExit(f"{path}: old version missing")
    write(path, text.replace(OLD, NEW))

pkg = read("hxempirical.pkg")
pkg = replace_once(pkg, "d Version 1.5.9", "d Version 1.5.10", "pkg version")
for name in ["hxtoolbox_v2.dlg", "hxworkbench.jar", "hx_nlswork.dta", "hx_grunfeld.dta", "hx_union.dta"]:
    pkg = replace_once(pkg, f"f {name}", f"F {name}", f"system file {name}")
write("hxempirical.pkg", pkg)

# Release verifier must treat F exactly like f as a managed install file.
ver = read("tools/verify_release.py")
ver = replace_once(
    ver,
    'managed = [x.split(None, 1)[1].strip() for x in pkg if x.startswith("f ")]',
    'managed = [x.split(None, 1)[1].strip() for x in pkg if len(x) > 2 and x[0].lower() == "f" and x[1].isspace()]',
    "verify_release managed parser",
)
write("tools/verify_release.py", ver)

# Make the PowerShell builder explicit about lowercase/uppercase f directives.
builder = read("tools/build_release_bundle.ps1")
builder = replace_once(builder, "if ($_ -match '^f\\s+(.+?)\\s*$')", "if ($_ -match '^[fF]\\s+(.+?)\\s*$')", "bundle manifest parser")
write("tools/build_release_bundle.ps1", builder)

installer = read("hxinstaller.ado")
old_target = r'''/* Pick a persistent writable ado location. Prefer an existing HX install,
   then PERSONAL, then PLUS/h. */
local personal `"`c(sysdir_personal)'"'
local plus `"`c(sysdir_plus)'"'
local personal : subinstr local personal "\" "/", all
local plus : subinstr local plus "\" "/", all
if `"`personal'"' != "" & substr(`"`personal'"', -1, 1) != "/" local personal `"`personal'/"'
if `"`plus'"' != "" & substr(`"`plus'"', -1, 1) != "/" local plus `"`plus'/"'

local target ""
local target_kind ""

/* Reuse an existing managed location only when it lives under PERSONAL/PLUS
   and remains writable. Ignore source-tree copies found on adopath. */
capture quietly findfile hxempirical.ado
if !_rc {
    local existing `"`r(fn)'"'
    local existing : subinstr local existing "\" "/", all
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
'''
new_target = r'''/* Use Stata's standard first-letter system directory for every installer.
   This matches net install and prevents PERSONAL root files from shadowing PERSONAL/h. */
local personal `"`c(sysdir_personal)'"'
local plus `"`c(sysdir_plus)'"'
local personal : subinstr local personal "\" "/", all
local plus : subinstr local plus "\" "/", all
if `"`personal'"' != "" & substr(`"`personal'"', -1, 1) != "/" local personal `"`personal'/"'
if `"`plus'"' != "" & substr(`"`plus'"', -1, 1) != "/" local plus `"`plus'/"'
local legacy_root `"`personal'"'

local target ""
local target_kind ""

if `"`personal'"' != "" {
    capture quietly mkdir `"`personal'"'
    local personal_h `"`personal'h/"'
    capture quietly mkdir `"`personal_h'"'
    local probe `"`personal_h'__hxempirical_write_test.tmp"'
    tempname personal_probe
    capture quietly file open `personal_probe' using `"`probe'"', write text replace
    if !_rc {
        file write `personal_probe' "hxempirical write test" _n
        file close `personal_probe'
        capture quietly erase `"`probe'"'
        local target `"`personal_h'"'
        local target_kind "PERSONAL"
    }
}

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
'''
installer = replace_once(installer, old_target, new_target, "installer target layout")

old_auto = r'''if `"`action'"' == "auto" {
    capture quietly confirm file `"`target'hxempirical.pkg"'
    if !_rc local action "update"
    else {
        capture quietly confirm file `"`target'hxempirical.ado"'
        if !_rc local action "update"
        else local action "install"
    }
}
'''
new_auto = r'''local legacy_present 0
if `"`legacy_root'"' != "" {
    capture quietly confirm file `"`legacy_root'hxempirical.ado"'
    if !_rc local legacy_present 1
    capture quietly confirm file `"`legacy_root'hxempirical.pkg"'
    if !_rc local legacy_present 1
}
if `"`action'"' == "auto" {
    capture quietly confirm file `"`target'hxempirical.pkg"'
    if !_rc local action "update"
    else {
        capture quietly confirm file `"`target'hxempirical.ado"'
        if !_rc local action "update"
        else if `legacy_present' local action "update"
        else local action "install"
    }
}
'''
installer = replace_once(installer, old_auto, new_auto, "installer auto legacy detection")

old_uninstall_manifest = r'''if `"`action'"' == "uninstall" {
    capture quietly confirm file `"`target'hxempirical.pkg"'
    if !_rc {
        capture quietly copy `"`target'hxempirical.pkg"' `"`pkg'"', replace
        if !_rc local manifest_source "本地安装清单"
    }
}
'''
new_uninstall_manifest = r'''if `"`action'"' == "uninstall" {
    capture quietly confirm file `"`target'hxempirical.pkg"'
    if !_rc {
        capture quietly copy `"`target'hxempirical.pkg"' `"`pkg'"', replace
        if !_rc local manifest_source "本地安装清单"
    }
    if `"`manifest_source'"' == "" & `"`legacy_root'"' != "" {
        capture quietly confirm file `"`legacy_root'hxempirical.pkg"'
        if !_rc {
            capture quietly copy `"`legacy_root'hxempirical.pkg"' `"`pkg'"', replace
            if !_rc local manifest_source "旧 PERSONAL 根目录清单"
        }
    }
}
'''
installer = replace_once(installer, old_uninstall_manifest, new_uninstall_manifest, "uninstall legacy manifest")

old_uninstall_pkg = r'''    capture quietly erase `"`target'hxempirical.pkg"'
    /* Remove one legacy PLUS registration when it is unambiguous. Older
'''
new_uninstall_pkg = r'''    capture quietly erase `"`target'hxempirical.pkg"'
    if `"`legacy_root'"' != "" & lower(`"`legacy_root'"') != lower(`"`target'"') {
        foreach f of local files {
            capture quietly erase `"`legacy_root'`f'"'
            if _rc {
                capture quietly confirm file `"`legacy_root'`f'"'
                if !_rc local erase_failed 1
            }
        }
        capture quietly erase `"`legacy_root'hxempirical.pkg"'
    }
    /* Remove one legacy PLUS registration when it is unambiguous. Older
'''
installer = replace_once(installer, old_uninstall_pkg, new_uninstall_pkg, "uninstall legacy cleanup")

old_prev = r'''/* Read the previous manifest so obsolete managed files can be removed only
   after a successful update. */
local oldfiles ""
local installed_version ""
capture quietly confirm file `"`target'hxempirical.pkg"'
if !_rc {
    tempname oldmanifest
    capture quietly file open `oldmanifest' using `"`target'hxempirical.pkg"', read text
    if !_rc {
        file read `oldmanifest' oldline
        while r(eof) == 0 {
            local oldline = trim(`"`oldline'"')
            gettoken oldtag oldrest : oldline
            if lower(`"`oldtag'"') == "f" {
                gettoken oldname oldunused : oldrest
                if `"`oldname'"' != "" local oldfiles `"`oldfiles' `oldname'"'
            }
            if lower(`"`oldtag'"') == "d" {
                gettoken oldkey oldvalue : oldrest
                if lower(`"`oldkey'"') == "version" local installed_version = trim(`"`oldvalue'"')
            }
            file read `oldmanifest' oldline
        }
        file close `oldmanifest'
    }
}
local oldfiles = trim(itrim(`"`oldfiles'"'))
'''
new_prev = r'''/* Read the previous manifest so obsolete managed files can be removed only
   after a successful update. Fall back to the pre-1.5.10 PERSONAL-root layout. */
local oldfiles ""
local installed_version ""
local oldmanifest_path ""
capture quietly confirm file `"`target'hxempirical.pkg"'
if !_rc local oldmanifest_path `"`target'hxempirical.pkg"'
if `"`oldmanifest_path'"' == "" & `"`legacy_root'"' != "" {
    capture quietly confirm file `"`legacy_root'hxempirical.pkg"'
    if !_rc local oldmanifest_path `"`legacy_root'hxempirical.pkg"'
}
if `"`oldmanifest_path'"' != "" {
    tempname oldmanifest
    capture quietly file open `oldmanifest' using `"`oldmanifest_path'"', read text
    if !_rc {
        file read `oldmanifest' oldline
        while r(eof) == 0 {
            local oldline = trim(`"`oldline'"')
            gettoken oldtag oldrest : oldline
            if lower(`"`oldtag'"') == "f" {
                gettoken oldname oldunused : oldrest
                if `"`oldname'"' != "" local oldfiles `"`oldfiles' `oldname'"'
            }
            if lower(`"`oldtag'"') == "d" {
                gettoken oldkey oldvalue : oldrest
                if lower(`"`oldkey'"') == "version" local installed_version = trim(`"`oldvalue'"')
            }
            file read `oldmanifest' oldline
        }
        file close `oldmanifest'
    }
}
local oldfiles = trim(itrim(`"`oldfiles'"'))
'''
installer = replace_once(installer, old_prev, new_prev, "previous manifest fallback")

marker = r'''/* Remove files that belonged to an older release but are absent now. */
foreach f of local oldfiles {
    if !strpos(`" `files' "', `" `f' "') capture quietly erase `"`target'`f'"'
}

capture quietly confirm file `"`target'hxempirical.ado"'
'''
replacement = r'''/* Remove files that belonged to an older release but are absent now. */
foreach f of local oldfiles {
    if !strpos(`" `files' "', `" `f' "') capture quietly erase `"`target'`f'"'
}

/* Pre-1.5.10 custom installs wrote managed files directly in PERSONAL.
   Remove those shadow copies only after the standard h/ installation commits. */
local legacy_cleanup_failed 0
if `"`target_kind'"' == "PERSONAL" & `"`legacy_root'"' != "" & lower(`"`legacy_root'"') != lower(`"`target'"') {
    foreach f of local files {
        capture quietly erase `"`legacy_root'`f'"'
        if _rc {
            capture quietly confirm file `"`legacy_root'`f'"'
            if !_rc local legacy_cleanup_failed 1
        }
    }
    foreach f of local oldfiles {
        capture quietly erase `"`legacy_root'`f'"'
        if _rc {
            capture quietly confirm file `"`legacy_root'`f'"'
            if !_rc local legacy_cleanup_failed 1
        }
    }
    capture quietly erase `"`legacy_root'hxempirical.pkg"'
}
if `legacy_cleanup_failed' {
    noisily display as error "新版已写入 PERSONAL/h，但旧 PERSONAL 根目录文件仍在遮挡。"
    noisily display as text "请关闭所有 Stata 窗口，重新打开后再次运行同一条更新命令完成迁移。"
    exit 602
}

capture quietly confirm file `"`target'hxempirical.ado"'
'''
installer = replace_once(installer, marker, replacement, "legacy cleanup after commit")
write("hxinstaller.ado", installer)

# README current release and explicit install-layout note.
readme = read("README.md")
readme = replace_once(readme, "**当前发布版本：1.5.9**", "**当前发布版本：1.5.10**", "README current version")
readme = replace_once(readme, "**上次修改时间：2026-08-15 20:40（UTC+8）**", "**上次修改时间：2026-08-15 21:10（UTC+8）**", "README timestamp")
anchor = "### 1.5.9 自查修复：外部命令扫描与文档一致性\n"
section = '''### 1.5.10 安装布局统一\n\n- 修复 `net install` 与旧 `hxinstall.do` 使用不同目录导致的版本遮挡：从本版起，两种安装方式都以 Stata 标准首字母目录 `PERSONAL/h`（不可写时 `PLUS/h`）为正式安装位置。\n- `hxempirical.pkg` 将 `hxworkbench.jar`、经典 `.dlg` 和内置测试 `.dta` 改为大写 `F` 系统安装文件，保证 `net install` 不会把这些必需文件当作普通 ancillary 文件。\n- `hxinstall.do` 会在新目录成功写入后清理 1.5.9 及以前遗留在 `PERSONAL` 根目录的 HX 受管文件，避免旧 `hxempirical.ado` / `hxworkbench.jar` 抢先被 Stata 找到。\n- 发布 CI 同时检查大小写 `f/F` 清单、标准 `h/` 布局和旧根目录迁移守卫。\n\n'''
if anchor not in readme:
    raise SystemExit("README history anchor missing")
readme = readme.replace(anchor, section + anchor, 1)
readme = readme.replace("- 第一次运行：优先安装到当前用户的 `PERSONAL`；该目录不可写时自动尝试 `PLUS/h`；", "- 第一次运行：优先安装到当前用户的 `PERSONAL/h`；该目录不可写时自动尝试 `PLUS/h`；", 1)
readme = readme.replace("安装位置优先使用 `PERSONAL`。如果 `PERSONAL` 因权限策略不可写，安装器会自动尝试 Stata 已搜索的 `PLUS/h`", "安装位置统一使用 Stata 标准首字母目录，优先 `PERSONAL/h`。如果 `PERSONAL/h` 因权限策略不可写，安装器会自动尝试 Stata 已搜索的 `PLUS/h`", 1)
write("README.md", readme)

install = read("INSTALL.md")
install = install.replace("当前版本：1.5.9", "当前版本：1.5.10", 1).replace("最新版本：1.5.9", "最新版本：1.5.10", 1)
install = install.replace("优先写入当前用户的 `PERSONAL` ado 目录；如果该目录不可写，会自动回退到 Stata 已搜索的 `PLUS/h`。", "统一写入 Stata 标准首字母 ado 目录：优先 `PERSONAL/h`；如果该目录不可写，会自动回退到 `PLUS/h`。", 1)
needle = "## 方法 A：在线安装\n"
note = '''## 1.5.10 安装布局说明\n\n从 1.5.10 起，`net install` 与 `hxinstall.do` 统一使用 `PERSONAL/h`（或 `PLUS/h`）。`hxworkbench.jar`、`.dlg` 和内置 `.dta` 均作为系统安装文件处理。旧版 `hxinstall.do` 曾把 HX 文件直接写进 `PERSONAL` 根目录；新版事务式安装器会在标准目录成功写入后清理这些旧影子文件。\n\n如果一直使用传统 `net install` 且电脑上还存在旧根目录副本，需要先用一次 `hxinstall.do` 完成自动迁移，或手动清理旧根目录 HX 文件；此后继续 `net install ..., replace force` 即可。\n\n'''
if needle not in install:
    raise SystemExit("INSTALL method anchor missing")
install = install.replace(needle, note + needle, 1)
write("INSTALL.md", install)

# Static checks for the packaging/layout contract.
static = read("tools/verify_static_contracts.py")
insert_before = "# Parse the registry structure rather than relying on the first foreach in the file.\n"
extra = '''# net install and the transactional installer must share one standard h/ layout.\nfor system_file in (\n    "hxtoolbox_v2.dlg",\n    "hxworkbench.jar",\n    "hx_nlswork.dta",\n    "hx_grunfeld.dta",\n    "hx_union.dta",\n):\n    if f"F {system_file}" not in pkg:\n        fail(f"required system file is not marked with uppercase F: {system_file}")\nif "local personal_h" not in read("hxinstaller.ado") or "local target `\\\"`personal_h'\\\"'" not in read("hxinstaller.ado"):\n    fail("transactional installer does not target PERSONAL/h")\nfor needle in (\n    "legacy_root",\n    "旧 PERSONAL 根目录文件仍在遮挡",\n    "Pre-1.5.10 custom installs wrote managed files directly in PERSONAL",\n):\n    if needle not in read("hxinstaller.ado"):\n        fail(f"legacy PERSONAL-root migration guard missing: {needle}")\nif "x[0].lower() == \\\"f\\\"" not in read("tools/verify_release.py"):\n    fail("release verifier does not include uppercase F package entries")\n\n'''
if insert_before not in static:
    raise SystemExit("static verifier anchor missing")
static = static.replace(insert_before, extra + insert_before, 1)
write("tools/verify_static_contracts.py", static)

print("HX_V1510_INSTALL_LAYOUT_PREP_OK")
