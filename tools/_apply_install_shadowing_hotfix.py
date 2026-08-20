from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = "1.5.12"
NEW = "1.5.13"


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def write(rel, text):
    (ROOT / rel).write_text(text, encoding="utf-8", newline="\n")


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"PATCH_FAIL {label}: expected 1 occurrence, found {count}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Version surfaces (release artifacts/JAR are intentionally rebuilt later on
# a real Stata SFI machine by the production build script).
# ---------------------------------------------------------------------------
pkg = read("hxempirical.pkg")
pkg = replace_once(pkg, "d Version 1.5.12", "d Version 1.5.13", "pkg version")
write("hxempirical.pkg", pkg)

entry = read("hxempirical.ado")
if entry.count("1.5.12") != 3:
    raise SystemExit(f"PATCH_FAIL hxempirical version occurrences={entry.count('1.5.12')}")
entry = entry.replace("1.5.12", "1.5.13")

start = '''    if `"`action'"' == "doctor" {'''
end = '''    if `"`action'"' == "install" {'''
si = entry.find(start)
ei = entry.find(end, si)
if si < 0 or ei < 0:
    raise SystemExit("PATCH_FAIL doctor block markers")

doctor = r'''    if `"`action'"' == "doctor" {
        local core "hxtoolbox hxmenu hxsetup hxregistry hxresolve hxexecute hxmonitor hxrefresh hxpick"
        local core_total 11
        local core_ok 0
        local core_missing ""
        foreach component of local core {
            capture quietly which `component'
            if _rc local core_missing `"`core_missing' `component'"'
            else local ++core_ok
        }
        capture quietly findfile hxworkbench.jar
        if _rc local core_missing `"`core_missing' hxworkbench.jar"'
        else local ++core_ok
        capture quietly findfile hxtoolbox_v2.dlg
        if _rc local core_missing `"`core_missing' hxtoolbox_v2.dlg"'
        else local ++core_ok

        display as text _newline ustrunescape("\u6838\u5fc3\u5de5\u4f5c\u53f0\u68c0\u67e5")
        if `core_ok' == `core_total' {
            display as result ustrunescape("[\u6838\u5fc3\u7ec4\u4ef6\uff1a\u6b63\u5e38] ") "`core_ok'/`core_total'"
        }
        else {
            display as error ustrunescape("[\u6838\u5fc3\u7ec4\u4ef6\uff1a\u4e0d\u5b8c\u6574] ") "`core_ok'/`core_total'"
            display as error ustrunescape("\u7f3a\u5c11\uff1a") trim(`"`core_missing'"')
        }

        /* A complete active installation can still be stale when another HX
           copy lives in a different user ado directory.  Inspect both standard
           first-letter locations and report what Stata actually resolves. */
        local personal `"`c(sysdir_personal)'"'
        local plus `"`c(sysdir_plus)'"'
        local personal : subinstr local personal "\" "/", all
        local plus : subinstr local plus "\" "/", all
        if `"`personal'"' != "" & substr(`"`personal'"', -1, 1) != "/" local personal `"`personal'/"'
        if `"`plus'"' != "" & substr(`"`plus'"', -1, 1) != "/" local plus `"`plus'/"'
        local personal_h ""
        local plus_h ""
        if `"`personal'"' != "" local personal_h `"`personal'h/"'
        if `"`plus'"' != "" local plus_h `"`plus'h/"'

        local personal_version ""
        if `"`personal_h'"' != "" {
            capture quietly confirm file `"`personal_h'hxempirical.ado"'
            if !_rc {
                tempname hxpersonal
                capture quietly file open `hxpersonal' using `"`personal_h'hxempirical.ado"', read text
                if !_rc {
                    file read `hxpersonal' hxline
                    file close `hxpersonal'
                    local hxline = trim(`"`hxline'"')
                    gettoken hxmark hxrest : hxline
                    gettoken hxname hxrest : hxrest
                    gettoken hxver hxrest : hxrest
                    if `"`hxmark'"' == "*!" & lower(`"`hxname'"') == "hxempirical" local personal_version `"`hxver'"'
                }
            }
        }

        local plus_version ""
        if `"`plus_h'"' != "" {
            capture quietly confirm file `"`plus_h'hxempirical.ado"'
            if !_rc {
                tempname hxplus
                capture quietly file open `hxplus' using `"`plus_h'hxempirical.ado"', read text
                if !_rc {
                    file read `hxplus' hxline
                    file close `hxplus'
                    local hxline = trim(`"`hxline'"')
                    gettoken hxmark hxrest : hxline
                    gettoken hxname hxrest : hxrest
                    gettoken hxver hxrest : hxrest
                    if `"`hxmark'"' == "*!" & lower(`"`hxname'"') == "hxempirical" local plus_version `"`hxver'"'
                }
            }
        }

        local active_path ""
        local active_version ""
        capture quietly findfile hxempirical.ado
        if !_rc {
            local active_path `"`r(fn)'"'
            tempname hxactive
            capture quietly file open `hxactive' using `"`active_path'"', read text
            if !_rc {
                file read `hxactive' hxline
                file close `hxactive'
                local hxline = trim(`"`hxline'"')
                gettoken hxmark hxrest : hxline
                gettoken hxname hxrest : hxrest
                gettoken hxver hxrest : hxrest
                if `"`hxmark'"' == "*!" & lower(`"`hxname'"') == "hxempirical" local active_version `"`hxver'"'
            }
        }

        local shadow_found 0
        if `"`personal_version'"' != "" & `"`plus_version'"' != "" & `"`personal_version'"' != `"`plus_version'"' local shadow_found 1

        display as text _newline "安装路径检查"
        if `shadow_found' {
            display as error "[警告] 检测到多版本安装，存在 ado-path 版本遮挡风险。"
            if `"`active_path'"' != "" display as text "当前生效：" as result `"`active_path' (`active_version')"'
            if `"`personal_version'"' != "" display as text "PERSONAL/h：" as result `"`personal_h'hxempirical.ado (`personal_version')"'
            if `"`plus_version'"' != "" display as text "PLUS/h：" as result `"`plus_h'hxempirical.ado (`plus_version')"'
            display as text "建议运行：" as result "hxempirical repair"
        }
        else {
            display as result "[安装路径：正常]"
            if `"`active_path'"' != "" display as text "当前生效：" as result `"`active_path' (`active_version')"'
        }

        hxdependency check
        local optional_missing = r(optional_missing)
        return scalar core_healthy = (`core_ok' == `core_total')
        return scalar core_installed = `core_ok'
        return scalar core_total = `core_total'
        return scalar optional_missing = `optional_missing'
        return scalar shadowing_detected = `shadow_found'
        return local active_hxempirical `"`active_path'"'
        return local active_version `"`active_version'"'
        return local personal_version `"`personal_version'"'
        return local plus_version `"`plus_version'"'
        exit
    }

'''
entry = entry[:si] + doctor + entry[ei:]
write("hxempirical.ado", entry)

launcher = read("hxinstall.do")
launcher = replace_once(launcher, "*! hxinstall 1.5.12", "*! hxinstall 1.5.13", "hxinstall version")
write("hxinstall.do", launcher)

installer = read("hxinstaller.ado")
installer = replace_once(installer, "*! hxinstaller 1.5.12", "*! hxinstaller 1.5.13", "hxinstaller version")
if "_hxinstaller_effective" in installer:
    raise SystemExit("PATCH_FAIL effective helper already present")

fast_marker = '''/* Same-version fast return is allowed only after the same-source package and
   release index are mutually bound and the local per-file integrity scan has
   passed. */'''
fast_insert = r'''/* A byte-perfect target is not enough: Stata must actually resolve the
   command from that target.  This catches PERSONAL/PLUS and current-directory
   shadowing before the same-version fast path can report a false success. */
if `"`action'"' == "update" & `"`installed_version'"' == `"`package_version'"' & `install_complete' {
    local effective_ok 0
    local effective_path ""
    local effective_version ""
    capture quietly _hxinstaller_effective, target(`"`target'"') packageversion(`"`package_version'"')
    if !_rc {
        local effective_ok = r(ok)
        local effective_path `"`r(path)'"'
        local effective_version `"`r(version)'"'
    }
    if !`effective_ok' {
        noisily display as text "检测到当前生效路径与受管安装位置不一致，将自动执行修复。"
        if `"`effective_path'"' != "" noisily display as text "当前生效：" as result `"`effective_path' (`effective_version')"'
        noisily display as text "目标位置：" as result `"`target'hxempirical.ado (`package_version')"'
        local install_complete 0
        local action "repair"
    }
}

'''
installer = replace_once(installer, fast_marker, fast_insert + fast_marker, "fast-path effective check")

rollback_marker = "/* Restore the complete previous installation when any commit step fails. */"
post_commit = r'''/* Do not report success merely because files were written.  Verify the exact
   hxempirical.ado that Stata resolves now; on mismatch, reuse the existing
   transaction rollback so a shadowed install is never called complete. */
if !`install_failed' {
    local effective_ok 0
    local effective_path ""
    local effective_version ""
    capture quietly _hxinstaller_effective, target(`"`target'"') packageversion(`"`package_version'"')
    if !_rc {
        local effective_ok = r(ok)
        local effective_path `"`r(path)'"'
        local effective_version `"`r(version)'"'
    }
    if !`effective_ok' {
        noisily display as error "安装后的有效路径校验失败：Stata 没有解析到刚写入的版本。"
        if `"`effective_path'"' != "" noisily display as text "当前生效：" as result `"`effective_path' (`effective_version')"'
        else noisily display as text "当前生效：" as result "未找到 hxempirical.ado"
        noisily display as text "目标位置：" as result `"`target'hxempirical.ado (`package_version')"'
        noisily display as text "可能存在更高优先级的旧副本或自定义 adopath；请先处理路径遮挡后重试。"
        local install_failed 1
    }
}

'''
installer = replace_once(installer, rollback_marker, post_commit + rollback_marker, "post-commit effective check")

helper = r'''

capture program drop _hxinstaller_effective
program define _hxinstaller_effective, rclass
    version 17.0
    syntax , TARGET(string asis) PACKAGEVERSION(string)

    local expected `"`target'hxempirical.ado"'
    local expected_norm : subinstr local expected "\" "/", all
    local effective_path ""
    capture quietly findfile hxempirical.ado
    if !_rc local effective_path `"`r(fn)'"'
    local effective_norm : subinstr local effective_path "\" "/", all

    if lower("`c(os)'") == "windows" {
        local expected_norm = lower(`"`expected_norm'"')
        local effective_norm = lower(`"`effective_norm'"')
    }

    local effective_version ""
    if `"`effective_path'"' != "" {
        tempname hxeffective
        capture quietly file open `hxeffective' using `"`effective_path'"', read text
        if !_rc {
            file read `hxeffective' hxline
            file close `hxeffective'
            local hxline = trim(`"`hxline'"')
            gettoken hxmark hxrest : hxline
            gettoken hxname hxrest : hxrest
            gettoken hxver hxrest : hxrest
            if `"`hxmark'"' == "*!" & lower(`"`hxname'"') == "hxempirical" local effective_version `"`hxver'"'
        }
    }

    local path_ok = (`"`effective_norm'"' != "" & `"`effective_norm'"' == `"`expected_norm'"')
    local version_ok = (`"`effective_version'"' == `"`packageversion'"')
    return scalar ok = (`path_ok' & `version_ok')
    return local path `"`effective_path'"'
    return local version `"`effective_version'"'
    return local expected `"`expected'"'
end
'''
installer = installer.rstrip() + helper + "\n"
write("hxinstaller.ado", installer)

help_text = read("hxempirical.sthlp")
help_text = replace_once(help_text, "{* *! version 1.5.12  20aug2026}{...}", "{* *! version 1.5.13  20aug2026}{...}", "help header")
help_text = replace_once(help_text, "HX empirical workbench, package version 1.5.12.", "HX empirical workbench, package version 1.5.13.", "help footer")
help_anchor = '''{phang2}{cmd:. do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"}\n\n{pstd}\nThen open it with'''
help_repl = '''{phang2}{cmd:. do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"}\n\n{pstd}\nUse the maintained installer for normal install/update/repair. {cmd:net install} is retained only as a compatibility entry because Stata may place it under {bf:PLUS/h} while an older {bf:PERSONAL/h} copy has higher adopath priority. {cmd:hxempirical doctor} reports differing PERSONAL/PLUS versions and {cmd:hxempirical repair} updates the managed effective location.\n\n{pstd}\nThen open it with'''
help_text = replace_once(help_text, help_anchor, help_repl, "help install warning")
help_text = replace_once(help_text, "reports the core workbench separately from these extensions.", "reports the core workbench separately from these extensions and also checks for conflicting PERSONAL/h and PLUS/h HX versions.", "help doctor path note")
write("hxempirical.sthlp", help_text)

java = read("src/main/java/com/hexie/stata/HxWorkbench.java")
java = replace_once(java, 'VERSION = "1.5.12"', 'VERSION = "1.5.13"', "Java VERSION")
write("src/main/java/com/hexie/stata/HxWorkbench.java", java)

readme = read("README.md")
readme = replace_once(readme, "**当前发布版本：1.5.12**", "**当前发布版本：1.5.13**", "README current version")
release_anchor = "**上次修改时间：2026-08-20 18:30（UTC+8）**\n\n"
release_notes = '''### 1.5.13 安装路径遮挡修复\n\n- `hxempirical doctor` 现在同时检查 `PERSONAL/h` 与 `PLUS/h` 的 HX 版本，并显示 Stata 当前实际解析到的 `hxempirical.ado`；版本不一致时明确提示 ado-path 遮挡风险。\n- 在线安装器在“已是最新版本”快速退出前以及事务提交后都会验证**当前实际生效路径 + 版本**，不再把“文件写入成功”误报为“当前运行版本已更新”。\n- 日常安装、更新和修复统一使用 `hxinstall.do` / `hxempirical update` / `hxempirical repair`。`net install` 仅保留兼容入口，因为它的目标目录由 Stata 包管理器决定，可能写入 `PLUS/h` 而被更高优先级的 `PERSONAL/h` 旧副本遮挡。\n- 新增隔离的双目录遮挡 smoke test 和静态防回归契约。\n\n'''
readme = replace_once(readme, release_anchor, release_anchor + release_notes, "README release notes")
old_layout = "- 修复 `net install` 与旧 `hxinstall.do` 使用不同目录导致的版本遮挡：从本版起，两种安装方式都以 Stata 标准首字母目录 `PERSONAL/h`（不可写时 `PLUS/h`）为正式安装位置。"
new_layout = "- 事务式 `hxinstall.do` 统一管理 `PERSONAL/h`（不可写时 `PLUS/h`）；Stata 自带 `net install` 的目标目录由包管理器决定，不能保证与当前生效 HX 位于同一目录，因此不再作为日常安装/更新入口。"
readme = replace_once(readme, old_layout, new_layout, "README historical layout correction")
remember = "**日常使用只需要记住这一条。**"
remember_new = "**日常使用只需要记住这一条。** 不建议使用 `net install` 进行日常安装或更新；如果历史上用过 `net install`，运行 `hxempirical doctor` 检查是否存在 `PERSONAL/h` 与 `PLUS/h` 双版本，再用 `hxempirical repair` 统一当前有效安装。"
readme = replace_once(readme, remember, remember_new, "README net install warning")
write("README.md", readme)

install_doc = read("INSTALL.md")
install_doc = replace_once(install_doc, "## 1.5.12 安装布局与安全说明", "## 1.5.13 安装路径与遮挡防护", "INSTALL section title")
old_para = "全新安装统一使用 `PERSONAL/h`（或 `PLUS/h`）。`hxworkbench.jar`、`.dlg` 和内置 `.dta` 均作为系统安装文件处理。检测到 Stata 当前仍从旧版 `PERSONAL` 根目录加载 HX 时，事务式安装器会在原位置完成安全更新，防止新旧目录互相遮挡；这类旧布局可在确认新版正常后再按维护说明迁移。\n\n如果一直使用传统 `net install` 且电脑上还存在旧根目录副本，先运行一次 `hxinstall.do` 将旧副本更新到同一版本。确认 `which hxempirical` 指向预期位置后，再迁移或清理旧布局。"
new_para = "全新安装统一使用 `PERSONAL/h`（或 `PLUS/h`）。`hxworkbench.jar`、`.dlg` 和内置 `.dta` 均作为系统安装文件处理。检测到 Stata 当前仍从旧版 `PERSONAL` 根目录加载 HX 时，事务式安装器会在原位置完成安全更新，防止新旧目录互相遮挡；这类旧布局可在确认新版正常后再按维护说明迁移。\n\n**不要使用 `net install` 进行日常安装或更新。** Stata 自带包管理器可能把新版本写入 `PLUS/h`，而已有的 `PERSONAL/h` 旧副本在 adopath 中优先级更高，结果会出现“installation complete，但 `hxempirical about` 仍是旧版”。遇到历史双版本时运行 `hxempirical doctor`，再执行 `hxempirical repair`；事务式安装器会验证 Stata 当前实际解析到的路径和版本。"
install_doc = replace_once(install_doc, old_para, new_para, "INSTALL shadow warning")
install_doc = install_doc.replace("当前版本：1.5.12\n最新版本：1.5.12", "当前版本：1.5.13\n最新版本：1.5.13", 1)
validation_anchor = "核心诊断应显示：\n\n```text\n[核心组件：正常] 11/11\n```"
validation_repl = "核心诊断应显示：\n\n```text\n[核心组件：正常] 11/11\n[安装路径：正常]\n```\n\n如果同时存在 `PERSONAL/h` 和 `PLUS/h` 且版本不同，doctor 会列出当前生效路径和两个版本，并提示运行 `hxempirical repair`。"
install_doc = replace_once(install_doc, validation_anchor, validation_repl, "INSTALL doctor expectation")
maintenance = 'do "tests/installer_lifecycle_smoke.do"\n'
install_doc = replace_once(install_doc, maintenance, maintenance + 'do "tests/installer_shadowing_smoke.do"\n', "INSTALL test list")
advanced_old = '''## 传统 Stata 包管理（高级）\n\nGitHub Pages 仍支持：\n\n```stata\nnet install hxempirical, from(\"https://xiaowang5105.github.io/hxempirical/\") replace force\n```\n\n普通用户使用在线安装器或浏览器离线包。统一安装器负责更新、回滚、清理旧文件和菜单持久化。'''
advanced_new = '''## `net install` 兼容入口（不推荐用于日常更新）\n\nGitHub Pages 仍保留 Stata 包管理兼容入口：\n\n```stata\nnet install hxempirical, from(\"https://xiaowang5105.github.io/hxempirical/\") replace force\n```\n\n但 `net install` 的目标目录由 Stata 包管理器决定，可能写入 `PLUS/h`，无法保证覆盖 adopath 中优先级更高的 `PERSONAL/h` 旧副本。因此普通用户不要用它做日常安装/更新。标准入口始终是 `hxinstall.do`；若曾使用 `net install`，先运行 `hxempirical doctor`，发现双版本时运行 `hxempirical repair`。'''
install_doc = replace_once(install_doc, advanced_old, advanced_new, "INSTALL net compatibility section")
write("INSTALL.md", install_doc)

# ---------------------------------------------------------------------------
# Dedicated path-shadowing smoke test.  It creates an isolated PERSONAL/h stale
# header plus a newer PLUS/h copy, verifies doctor diagnostics, then repairs the
# effective PERSONAL target from the local release.
# ---------------------------------------------------------------------------
shadow_test = r'''version 17.0
clear all
set more off

args repository
if `"`repository'"' == "" local repository `"`c(pwd)'"'
local repository : subinstr local repository "\" "/", all
local installer `"`repository'/hxinstall.do"'
capture quietly confirm file `"`installer'"'
if _rc {
    display as error "HX_INSTALLER_SHADOWING_FAIL cannot find hxinstall.do"
    exit 601
}

local original_personal `"`c(sysdir_personal)'"'
local original_plus `"`c(sysdir_plus)'"'
local original_pwd `"`c(pwd)'"'
tempfile shadow_base stale_copy
local test_personal `"`shadow_base'_personal"'
local test_plus `"`shadow_base'_plus"'
local personal_h `"`test_personal'/h"'
local plus_h `"`test_plus'/h"'

sysdir set PERSONAL `"`test_personal'/"'
sysdir set PLUS `"`test_plus'/"'
capture quietly mkdir `"`test_personal'"'
capture quietly mkdir `"`test_plus'"'
capture quietly mkdir `"`personal_h'"'
capture quietly mkdir `"`plus_h'"'

capture noisily do `"`installer'"' auto `"`repository'"'
local install_rc = _rc
if `install_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    sysdir set PLUS `"`original_plus'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_SHADOWING_FAIL initial install r(`install_rc')"
    exit `install_rc'
}

/* Keep a current lower-priority PLUS copy, then make only the PERSONAL header
   stale.  The executable body remains current so the new doctor can diagnose
   the fixture exactly as a historical multi-version installation. */
capture quietly copy `"`repository'/hxempirical.ado"' `"`plus_h'/hxempirical.ado"', replace
if _rc {
    sysdir set PERSONAL `"`original_personal'"'
    sysdir set PLUS `"`original_plus'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_SHADOWING_FAIL cannot create PLUS fixture"
    exit 603
}

tempname stale_in stale_out
file open `stale_in' using `"`personal_h'/hxempirical.ado"', read text
file open `stale_out' using `"`stale_copy'"', write text replace
local first 1
file read `stale_in' line
while r(eof) == 0 {
    if `first' {
        file write `stale_out' "*! hxempirical 1.5.12  20aug2026" _n
        local first 0
    }
    else file write `stale_out' `"`line'"' _n
    file read `stale_in' line
}
file close `stale_in'
file close `stale_out'
copy `"`stale_copy'"' `"`personal_h'/hxempirical.ado"', replace

discard
capture noisily hxempirical doctor
local doctor_rc = _rc
local shadowing = .
local personal_version ""
local plus_version ""
if !`doctor_rc' {
    local shadowing = r(shadowing_detected)
    local personal_version `"`r(personal_version)'"'
    local plus_version `"`r(plus_version)'"'
}
if `doctor_rc' | `shadowing' != 1 | `"`personal_version'"' != "1.5.12" | `"`plus_version'"' != "1.5.13" {
    sysdir set PERSONAL `"`original_personal'"'
    sysdir set PLUS `"`original_plus'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_SHADOWING_FAIL doctor did not detect divergent PERSONAL/PLUS versions"
    exit 459
}

capture noisily do `"`installer'"' repair `"`repository'"'
local repair_rc = _rc
if `repair_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    sysdir set PLUS `"`original_plus'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_SHADOWING_FAIL repair r(`repair_rc')"
    exit `repair_rc'
}

discard
capture quietly findfile hxempirical.ado
local active_rc = _rc
local active_path ""
if !`active_rc' local active_path `"`r(fn)'"'
local active_norm : subinstr local active_path "\" "/", all
local expected_norm `"`personal_h'/hxempirical.ado"'
if lower("`c(os)'") == "windows" {
    local active_norm = lower(`"`active_norm'"')
    local expected_norm = lower(`"`expected_norm'"')
}
if `active_rc' | `"`active_norm'"' != `"`expected_norm'"' {
    sysdir set PERSONAL `"`original_personal'"'
    sysdir set PLUS `"`original_plus'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_SHADOWING_FAIL repair did not make PERSONAL/h effective"
    exit 459
}

capture noisily hxempirical doctor
local clean_doctor_rc = _rc
local clean_shadow = .
if !`clean_doctor_rc' local clean_shadow = r(shadowing_detected)
if `clean_doctor_rc' | `clean_shadow' != 0 | `"`r(personal_version)'"' != "1.5.13" | `"`r(plus_version)'"' != "1.5.13" {
    sysdir set PERSONAL `"`original_personal'"'
    sysdir set PLUS `"`original_plus'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_SHADOWING_FAIL repair did not converge versions"
    exit 459
}

sysdir set PERSONAL `"`original_personal'"'
sysdir set PLUS `"`original_plus'"'
cd `"`original_pwd'"'
discard
display as result "HX_INSTALLER_SHADOWING_OK"
'''
write("tests/installer_shadowing_smoke.do", shadow_test)

verifier = read("tools/verify_installer_contracts.py")
verifier = replace_once(verifier, 'launcher = read("hxinstall.do")\npkg = read("hxempirical.pkg")', 'launcher = read("hxinstall.do")\ninstaller = read("hxinstaller.ado")\npkg = read("hxempirical.pkg")', "verifier installer read")
old_comment = "# net install and the transactional installer must share one standard h/ layout."
new_comment = "# The maintained transactional installer owns the normal h/ layout.  net install is compatibility-only because Stata may choose PLUS/h and leave a higher-priority PERSONAL/h copy active."
verifier = replace_once(verifier, old_comment, new_comment, "verifier layout comment")
anchor = 'if "capture quietly run" not in launcher or "bootstrap_installer" not in launcher:\n    fail("public hxinstall.do does not load the exact temporary installer quietly")\n'
extra = '''if "capture quietly run" not in launcher or "bootstrap_installer" not in launcher:\n    fail("public hxinstall.do does not load the exact temporary installer quietly")\n\n# Path-shadowing must be observable to users and must block false installer success.\nfor needle in (\n    "检测到多版本安装",\n    "shadowing_detected",\n    "personal_version",\n    "plus_version",\n):\n    if needle not in entry:\n        fail(f"doctor path-shadowing diagnostic missing: {needle}")\nfor needle in (\n    "_hxinstaller_effective",\n    "检测到当前生效路径与受管安装位置不一致",\n    "安装后的有效路径校验失败",\n):\n    if needle not in installer:\n        fail(f"installer effective-path gate missing: {needle}")\nif "不建议使用 `net install`" not in readme:\n    fail("README must not recommend net install for routine updates")\nif "`net install` 兼容入口（不推荐用于日常更新）" not in install_doc:\n    fail("INSTALL.md must label net install as compatibility-only")\nshadow_test = read("tests/installer_shadowing_smoke.do")\nif "HX_INSTALLER_SHADOWING_OK" not in shadow_test or "shadowing_detected" not in shadow_test:\n    fail("installer path-shadowing smoke test missing")\n'''
verifier = replace_once(verifier, anchor, extra, "verifier shadow contracts")
write("tools/verify_installer_contracts.py", verifier)

print("HX_INSTALL_SHADOWING_PATCH_OK version=1.5.13")
