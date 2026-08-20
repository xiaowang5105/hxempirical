*! hxinstaller 1.5.14  20aug2026
*! Hidden transactional installer core for hxempirical
program define hxinstaller
    version 17.0
    set more off

    local personal `"`c(sysdir_personal)'"'
    local plus `"`c(sysdir_plus)'"'
    local personal : subinstr local personal "\" "/", all
    local plus : subinstr local plus "\" "/", all
    if `"`personal'"' != "" & substr(`"`personal'"', -1, 1) != "/" local personal `"`personal'/"'
    if `"`plus'"' != "" & substr(`"`plus'"', -1, 1) != "/" local plus `"`plus'/"'
    local lockroot ""
    if `"`personal'"' != "" {
        capture quietly mkdir `"`personal'"'
        local lockroot `"`personal'"'
    }
    else if `"`plus'"' != "" {
        capture quietly mkdir `"`plus'"'
        local lockroot `"`plus'"'
    }
    if `"`lockroot'"' == "" {
        noisily display as error "Stata 没有返回可用的 PERSONAL 或 PLUS ado 目录。"
        exit 603
    }

    /* File creation without replace is an atomic cross-process gate.  A lock
       left by an interrupted Stata session is never removed automatically. */
    local lockfile `"`lockroot'hxempirical.install.lock"'
    tempname lockhandle
    capture quietly file open `lockhandle' using `"`lockfile'"', write text
    local lock_rc = _rc
    if `lock_rc' {
        noisily display as error "另一个 hxempirical 安装、更新或卸载任务正在运行。"
        noisily display as text  "若所有 Stata 安装任务都已关闭，这是上次异常中断留下的锁："
        noisily display as result `"  erase "`lockfile'""'
        exit 602
    }
    capture file write `lockhandle' "hxempirical installer lock" _n
    local lock_write_rc = _rc
    capture file close `lockhandle'
    if `lock_write_rc' {
        capture quietly erase `"`lockfile'"'
        noisily display as error "无法建立 hxempirical 安装锁。"
        exit 603
    }

    /* The core temporarily shortens network timeouts.  Restore the caller's
       session settings even when an unexpected file error or user break exits
       the core before its local cleanup block. */
    local wrapper_timeout1 = c(timeout1)
    local wrapper_timeout2 = c(timeout2)
    capture noisily _hxinstaller_core `0'
    local core_rc = _rc
    capture quietly set timeout1 `wrapper_timeout1'
    capture quietly set timeout2 `wrapper_timeout2'
    capture quietly erase `"`lockfile'"'
    if `core_rc' exit `core_rc'
end

capture program drop _hxinstaller_core
program define _hxinstaller_core
version 17.0
set more off

args action source
local action = lower(trim(`"`action'"'))
if `"`action'"' == "" local action "auto"
if !inlist(`"`action'"', "auto", "install", "update", "repair", "uninstall") {
    noisily display as error "用法：hxinstaller [auto|install|update|repair|uninstall]"
    exit 198
}

local pages "https://xiaowang5105.github.io/hxempirical"
local raw   "https://raw.githubusercontent.com/xiaowang5105/hxempirical/main"
local source = trim(`"`source'"')
local remote_source = (`"`source'"' == "")
if substr(`"`source'"', 1, 1) == char(34) & substr(`"`source'"', -1, 1) == char(34) {
    local source = substr(`"`source'"', 2, strlen(`"`source'"') - 2)
}
if `"`source'"' != "" {
    /* Local release-source override used by the offline launcher and tests. */
    local pages `"`source'"'
    local raw   `"`source'"'
}

if c(stata_version) < 17 {
    noisily display as error "hxempirical 需要 Stata 17 或更高版本。"
    noisily display as text  "当前版本：Stata `c(stata_version)'。"
    exit 9
}

/* Use Stata's first-letter package layout.  Existing legacy PERSONAL-root
   installs remain updateable in place so an older file cannot shadow h/. */
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
    local select_probe `"`personal_h'__hxempirical_select.tmp"'
    tempname personal_probe
    capture quietly file open `personal_probe' using `"`select_probe'"', write text replace
    if !_rc {
        file write `personal_probe' "hxempirical target probe" _n
        file close `personal_probe'
        capture quietly erase `"`select_probe'"'
        local target `"`personal_h'"'
        local target_kind "PERSONAL/h"
    }
}
if `"`target'"' == "" & `"`plus'"' != "" {
    capture quietly mkdir `"`plus'"'
    local plus_h `"`plus'h/"'
    capture quietly mkdir `"`plus_h'"'
    local select_probe `"`plus_h'__hxempirical_select.tmp"'
    tempname plus_probe
    capture quietly file open `plus_probe' using `"`select_probe'"', write text replace
    if !_rc {
        file write `plus_probe' "hxempirical target probe" _n
        file close `plus_probe'
        capture quietly erase `"`select_probe'"'
        local target `"`plus_h'"'
        local target_kind "PLUS/h"
    }
}

/* Prefer an existing legacy-root installation only when no standard h/
   installation exists.  This keeps updates deterministic and avoids shadows. */
local standard_present 0
if `"`target'"' != "" {
    capture quietly confirm file `"`target'hxempirical.pkg"'
    if !_rc local standard_present 1
    capture quietly confirm file `"`target'hxempirical.ado"'
    if !_rc local standard_present 1
}
if !`standard_present' & `"`legacy_root'"' != "" {
    local legacy_present 0
    capture quietly confirm file `"`legacy_root'hxempirical.pkg"'
    if !_rc local legacy_present 1
    capture quietly confirm file `"`legacy_root'hxempirical.ado"'
    if !_rc local legacy_present 1
    if `legacy_present' {
        local target `"`legacy_root'"'
        local target_kind "PERSONAL（旧布局）"
    }
}
if `"`target'"' == "" {
    noisily display as error "hxempirical 找不到可写的持久 ado 目录。"
    exit 603
}

local probe `"`target'__hxempirical_write_test.tmp"'
tempname probehandle
capture quietly file open `probehandle' using `"`probe'"', write text replace
if _rc {
    noisily display as error "无法写入 Stata ado 目录：`target'"
    noisily display as text  "请运行 sysdir 查看目录设置，或联系管理员检查该目录权限。"
    exit 603
}
file write `probehandle' "hxempirical write test" _n
file close `probehandle'
capture quietly erase `"`probe'"'

/* The public one-line command is safe for both a clean installation and an
   existing installation.  An existing local manifest is the strongest signal;
   a leftover entry ado also counts as an update so rollback protection applies. */
if `"`action'"' == "auto" {
    capture quietly confirm file `"`target'hxempirical.pkg"'
    if !_rc local action "update"
    else {
        capture quietly confirm file `"`target'hxempirical.ado"'
        if !_rc local action "update"
        else local action "install"
    }
}

/* Uninstall works offline when the locally stored manifest is available. */
tempfile pkg bundle_index offline_index
local manifest_source ""
local release_base ""
local exploded_source 0
if `"`action'"' == "uninstall" {
    capture quietly confirm file `"`target'hxempirical.pkg"'
    if !_rc {
        capture quietly copy `"`target'hxempirical.pkg"' `"`pkg'"', replace
        if !_rc local manifest_source "本地安装清单"
    }
}

/* Bound each network wait.  Stata's default transfer timeout is 180 seconds,
   which makes a blocked GitHub request look like an application freeze. */
if `"`action'"' != "uninstall" noisily display as text "正在检查最新版本……"
local old_timeout1 = c(timeout1)
local old_timeout2 = c(timeout2)
if `remote_source' {
    quietly set timeout1 10
    quietly set timeout2 20
}

/* Select one complete release origin.  The manifest, index and every bundle
   segment are bound to this origin so one transaction never mixes Pages and
   Raw content from different deployments. */
if `"`manifest_source'"' == "" & !`remote_source' {
    capture quietly copy `"`source'/hxempirical.pkg"' `"`pkg'"', replace
    local candidate_pkg_rc = _rc
    if !`candidate_pkg_rc' {
        local release_base `"`source'"'
        capture quietly copy `"`source'/hxempirical-release.index"' `"`bundle_index'"', replace
        if _rc {
            capture quietly copy `"`source'/hxempirical-offline.index"' `"`offline_index'"', replace
            if !_rc {
                local exploded_source 1
                local manifest_source "本地解压包"
            }
        }
        else local manifest_source "本地分段发布包"
    }
}
if `"`manifest_source'"' == "" & `remote_source' {
    capture quietly copy `"`pages'/hxempirical.pkg"' `"`pkg'"', replace
    local candidate_pkg_rc = _rc
    capture quietly copy `"`pages'/hxempirical-release.index"' `"`bundle_index'"', replace
    local candidate_index_rc = _rc
    if !`candidate_pkg_rc' & !`candidate_index_rc' {
        local release_base `"`pages'"'
        local manifest_source "GitHub Pages"
    }
}
if `"`manifest_source'"' == "" & `remote_source' {
    capture quietly copy `"`raw'/hxempirical.pkg"' `"`pkg'"', replace
    local candidate_pkg_rc = _rc
    capture quietly copy `"`raw'/hxempirical-release.index"' `"`bundle_index'"', replace
    local candidate_index_rc = _rc
    if !`candidate_pkg_rc' & !`candidate_index_rc' {
        local release_base `"`raw'"'
        local manifest_source "GitHub Raw"
    }
}
if `remote_source' {
    quietly set timeout1 `old_timeout1'
    quietly set timeout2 `old_timeout2'
}
if `"`manifest_source'"' == "" {
    noisily display as error "无法从同一来源读取 hxempirical 安装清单和发布索引。"
    noisily display as text  "当前网络未能在限定时间内连接 GitHub。"
    noisily display as text  "请用浏览器打开安装说明：`pages'/INSTALL.md"
    exit 603
}

/* Read the release manifest. */
tempname manifest
file open `manifest' using `"`pkg'"', read text
local files ""
local files_key ""
local package_version ""
local manifest_format ""
local manifest_invalid 0
file read `manifest' line
while r(eof) == 0 {
    local line = trim(`"`line'"')
    gettoken tag rest : line
    if lower(`"`tag'"') == "v" {
        local vrest = trim(`"`rest'"')
        if `"`manifest_format'"' != "" | `"`vrest'"' != "3" local manifest_invalid 1
        else local manifest_format `"`vrest'"'
    }
    if lower(`"`tag'"') == "f" {
        gettoken fname unused : rest
        local fname = trim(`"`fname'"')
        local fname_key = lower(`"`fname'"')
        local unused = trim(`"`unused'"')
        if `"`fname'"' == "" | `"`unused'"' != "" | ///
            !regexm(`"`fname'"', "^hx[A-Za-z0-9_.-]+$") | ///
            strpos(`"`fname'"', "..") | strpos(`"`fname'"', "/") | ///
            strpos(`"`fname'"', "\") | strpos(`"`fname'"', ":") | ///
            substr(`"`fname'"', -1, 1) == "." | ///
            strpos(`" `files_key' "', `" `fname_key' "') {
            local manifest_invalid 1
        }
        else {
            local files `"`files' `fname'"'
            local files_key `"`files_key' `fname_key'"'
        }
    }
    if lower(`"`tag'"') == "d" {
        gettoken dkey drest : rest
        if lower(`"`dkey'"') == "version" local package_version = trim(`"`drest'"')
    }
    file read `manifest' line
}
file close `manifest'
local files = trim(itrim(`"`files'"'))
local files_key = trim(itrim(`"`files_key'"'))
local nfiles : word count `files'
if `nfiles' == 0 {
    noisily display as error "安装清单为空，操作已停止。"
    exit 498
}
if `manifest_invalid' | `"`manifest_format'"' != "3" | `"`package_version'"' == "" {
    noisily display as error "安装清单包含不安全、重复或无效的文件记录，操作已停止。"
    exit 498
}

/* A browser-downloaded exploded bundle carries a non-self-referential index
   that binds the package and every managed source file before staging. */
local exploded_pkg_bytes ""
local exploded_pkg_checksum ""
if `exploded_source' {
    local offline_valid 1
    local offline_format ""
    local offline_version ""
    local offline_package ""
    local offline_seen ""
    local offline_seen_key ""
    local offline_count 0
    tempname offline_in
    capture quietly file open `offline_in' using `"`offline_index'"', read text
    if _rc local offline_valid 0
    else {
        file read `offline_in' offline_line
        while r(eof) == 0 {
            local offline_line = trim(`"`offline_line'"')
            gettoken offline_tag offline_rest : offline_line
            if lower(`"`offline_tag'"') == "v" {
                local offline_value = trim(`"`offline_rest'"')
                if `"`offline_format'"' != "" | `"`offline_value'"' != "1" local offline_valid 0
                else local offline_format `"`offline_value'"'
            }
            else if lower(`"`offline_tag'"') == "d" {
                gettoken offline_key offline_value : offline_rest
                local offline_value = trim(`"`offline_value'"')
                if lower(`"`offline_key'"') == "version" local offline_version `"`offline_value'"'
                if lower(`"`offline_key'"') == "package" local offline_package `"`offline_value'"'
                if lower(`"`offline_key'"') == "pkg_bytes" local exploded_pkg_bytes `"`offline_value'"'
                if lower(`"`offline_key'"') == "pkg_checksum" local exploded_pkg_checksum `"`offline_value'"'
            }
            else if lower(`"`offline_tag'"') == "f" {
                gettoken offline_name offline_rest : offline_rest
                gettoken offline_bytes offline_checksum : offline_rest
                local offline_name = trim(`"`offline_name'"')
                local offline_name_key = lower(`"`offline_name'"')
                local offline_checksum = trim(`"`offline_checksum'"')
                if `"`offline_name'"' == "" | ///
                    !regexm(`"`offline_name'"', "^hx[A-Za-z0-9_.-]+$") | ///
                    strpos(`"`offline_name'"', "..") | strpos(`"`offline_name'"', "/") | ///
                    strpos(`"`offline_name'"', "\") | strpos(`"`offline_name'"', ":") | ///
                    substr(`"`offline_name'"', -1, 1) == "." | ///
                    !strpos(`" `files' "', `" `offline_name' "') | ///
                    strpos(`" `offline_seen_key' "', `" `offline_name_key' "') | ///
                    missing(real(`"`offline_bytes'"')) | missing(real(`"`offline_checksum'"')) {
                    local offline_valid 0
                }
                else {
                    local offline_seen `"`offline_seen' `offline_name'"'
                    local offline_seen_key `"`offline_seen_key' `offline_name_key'"'
                    local ++offline_count
                    capture quietly checksum `"`release_base'/`offline_name'"'
                    if _rc local offline_valid 0
                    else if r(filelen) != real(`"`offline_bytes'"') | r(checksum) != real(`"`offline_checksum'"') local offline_valid 0
                }
            }
            file read `offline_in' offline_line
        }
        file close `offline_in'
    }
    if `"`offline_format'"' != "1" | `"`offline_package'"' != "hxempirical.pkg" | `"`offline_version'"' != `"`package_version'"' | `offline_count' != `nfiles' | ///
        missing(real(`"`exploded_pkg_bytes'"')) | missing(real(`"`exploded_pkg_checksum'"')) {
        local offline_valid 0
    }
    foreach f of local files {
        if !strpos(`" `offline_seen' "', `" `f' "') local offline_valid 0
    }
    capture quietly checksum `"`pkg'"'
    if _rc local offline_valid 0
    else if r(filelen) != real(`"`exploded_pkg_bytes'"') | r(checksum) != real(`"`exploded_pkg_checksum'"') local offline_valid 0
    if !`offline_valid' {
        noisily display as error "离线包完整性验证失败；现有安装保持不变。"
        noisily display as text  "请重新下载并完整解压 hxempirical-release.zip。"
        exit 459
    }
}

if `"`action'"' == "uninstall" {
    /* The local manifest controls what will be erased.  Bind it to the
       checksum recorded by the last successful transaction first. */
    local uninstall_pkg_valid 0
    local uninstall_integrity `"`target'hxempirical.integrity"'
    capture quietly confirm file `"`uninstall_integrity'"'
    if !_rc {
        tempname uninstall_integrity_in
        capture quietly file open `uninstall_integrity_in' using `"`uninstall_integrity'"', read text
        if !_rc {
            local uninstall_pkg_bytes ""
            local uninstall_pkg_checksum ""
            local uninstall_integrity_format ""
            file read `uninstall_integrity_in' uninstall_integrity_line
            while r(eof) == 0 {
                local uninstall_integrity_line = trim(`"`uninstall_integrity_line'"')
                gettoken uninstall_integrity_tag uninstall_integrity_rest : uninstall_integrity_line
                if lower(`"`uninstall_integrity_tag'"') == "v" {
                    local uninstall_integrity_value = trim(`"`uninstall_integrity_rest'"')
                    if `"`uninstall_integrity_format'"' == "" local uninstall_integrity_format `"`uninstall_integrity_value'"'
                    else local uninstall_integrity_format "invalid"
                }
                else if lower(`"`uninstall_integrity_tag'"') == "d" {
                    gettoken uninstall_integrity_key uninstall_integrity_value : uninstall_integrity_rest
                    local uninstall_integrity_value = trim(`"`uninstall_integrity_value'"')
                    if lower(`"`uninstall_integrity_key'"') == "pkg_bytes" local uninstall_pkg_bytes `"`uninstall_integrity_value'"'
                    if lower(`"`uninstall_integrity_key'"') == "pkg_checksum" local uninstall_pkg_checksum `"`uninstall_integrity_value'"'
                }
                file read `uninstall_integrity_in' uninstall_integrity_line
            }
            file close `uninstall_integrity_in'
            if `"`uninstall_integrity_format'"' == "1" & !missing(real(`"`uninstall_pkg_bytes'"')) & !missing(real(`"`uninstall_pkg_checksum'"')) {
                capture quietly checksum `"`target'hxempirical.pkg"'
                if !_rc & r(filelen) == real(`"`uninstall_pkg_bytes'"') & r(checksum) == real(`"`uninstall_pkg_checksum'"') {
                    local uninstall_pkg_valid 1
                }
            }
        }
    }
    if !`uninstall_pkg_valid' {
        noisily display as error "本地安装清单未通过完整性验证；为保护其他文件，卸载未开始。"
        noisily display as text  "请先运行 hxempirical repair，成功后再卸载。"
        exit 459
    }

    /* Load the exact managed setup program before touching any file. */
    capture program drop hxsetup
    capture quietly run `"`target'hxsetup.ado"'
    local setup_loader_rc = _rc
    if `setup_loader_rc' {
        noisily display as error "无法载入已安装的 hxsetup.ado；卸载未开始。"
        exit `setup_loader_rc'
    }

    local removefiles `"`files'"'
    foreach extra in hxinstaller.ado hxempirical.pkg hxempirical.integrity {
        if !strpos(`" `removefiles' "', `" `extra' "') local removefiles `"`removefiles' `extra'"'
    }
    local removefiles = trim(itrim(`"`removefiles'"'))

    /* Back up the complete managed installation first.  Any failure leaves
       the live installation and its retry entry untouched. */
    tempfile uninstallbase
    /* A unique tempfile prefix avoids platform-specific mkdir behavior while
       keeping every backup in Stata's automatically managed temp directory. */
    local uninstall_backup `"`uninstallbase'_"'
    local uninstall_backup_failed 0
    foreach f of local removefiles {
        if `uninstall_backup_failed' continue, break
        capture quietly confirm file `"`target'`f'"'
        if !_rc {
            capture quietly copy `"`target'`f'"' `"`uninstall_backup'`f'"', replace
            local backup_rc = _rc
            if `backup_rc' {
                noisily display as error "无法备份待卸载文件：`target'`f'"
                noisily display as text "卸载未开始，现有安装保持不变。"
                local uninstall_backup_failed 1
            }
        }
    }
    if `uninstall_backup_failed' {
        foreach f of local removefiles {
            capture quietly erase `"`uninstall_backup'`f'"'
        }
        exit 603
    }

    /* Try the JAR first because Windows can lock it while the workbench is
       open.  Remaining files are removed only after that gate succeeds. */
    local erase_order ""
    if strpos(`" `removefiles' "', " hxworkbench.jar ") local erase_order "hxworkbench.jar"
    foreach f of local removefiles {
        if `"`f'"' != "hxworkbench.jar" local erase_order `"`erase_order' `f'"'
    }
    local erase_order = trim(itrim(`"`erase_order'"'))
    local erase_failed 0
    local failed_file ""
    foreach f of local erase_order {
        if `erase_failed' continue, break
        capture quietly confirm file `"`target'`f'"'
        if _rc continue
        local erase_rc 0
        if `"${HXEI_TEST_FAIL_FILE}"' == `"`f'"' local erase_rc 602
        else {
            capture quietly erase `"`target'`f'"'
            local erase_rc = _rc
            if `erase_rc' {
                capture quietly confirm file `"`target'`f'"'
                if _rc local erase_rc 0
            }
        }
        if `erase_rc' {
            local erase_failed 1
            local failed_file `"`f'"'
        }
    }

    if !`erase_failed' {
        capture noisily hxsetup, remove
        local profile_remove_rc = _rc
        if `profile_remove_rc' {
            local erase_failed 1
            local failed_file "profile.do 菜单配置"
        }
    }

    if `erase_failed' {
        /* Restore the retry entry and manifest first, then the full package. */
        local restore_failed 0
        local uninstall_restore_order "hxinstaller.ado hxempirical.pkg hxempirical.integrity"
        foreach f of local files {
            if !strpos(`" `uninstall_restore_order' "', `" `f' "') local uninstall_restore_order `"`uninstall_restore_order' `f'"'
        }
        foreach f of local uninstall_restore_order {
            capture quietly confirm file `"`uninstall_backup'`f'"'
            if !_rc {
                capture quietly checksum `"`uninstall_backup'`f'"'
                if _rc local restore_failed 1
                else {
                    local restore_bytes = r(filelen)
                    local restore_checksum = r(checksum)
                    capture quietly copy `"`uninstall_backup'`f'"' `"`target'`f'"', replace
                    if _rc local restore_failed 1
                    else {
                        capture quietly checksum `"`target'`f'"'
                        if _rc local restore_failed 1
                        else if r(filelen) != `restore_bytes' | r(checksum) != `restore_checksum' local restore_failed 1
                    }
                }
            }
        }
        if !`restore_failed' {
            foreach f of local removefiles {
                capture quietly erase `"`uninstall_backup'`f'"'
            }
        }
        noisily display as error _newline "卸载未完成：暂时无法移除 `failed_file'。"
        if `restore_failed' {
            noisily display as error "部分文件未能自动恢复；备份已保留，前缀为："
            noisily display as result `"  `uninstall_backup'"'
        }
        else noisily display as text "安装器已恢复全部受管文件，并保留 manifest 与重试入口。"
        noisily display as text "请关闭所有 Stata 窗口，重新打开后再次运行同一条卸载命令。"
        if `restore_failed' exit 603
        exit 602
    }

    /* Remove one legacy PLUS registration when it is unambiguous. Older
       machines may contain several registrations; leave those records to
       Stata's package manager and report the exact cleanup command. */
    capture quietly ado uninstall hxempirical, from(PLUS)
    capture quietly discard

    foreach f of local removefiles {
        capture quietly erase `"`uninstall_backup'`f'"'
    }

    capture quietly which hxempirical
    local legacy_found = !_rc
    noisily display as result _newline "hxempirical 的 PERSONAL 安装已卸载。"
    if `legacy_found' {
        noisily display as text "检测到 ado-path 中还有旧的 net install 记录。请运行："
        noisily display as result "  ado dir hxempirical"
        noisily display as text   "再按列表编号运行：ado uninstall [编号]"
    }
    noisily display as text "请重新启动 Stata，使已加载的 Java 类完全释放。"
    exit 0
}

/* Read the previous manifest so obsolete managed files can be removed only
   after a successful update. */
local oldfiles ""
local oldfiles_key ""
local installed_version ""
local old_manifest_format ""
local old_manifest_safe 1
capture quietly confirm file `"`target'hxempirical.pkg"'
if !_rc {
    tempname oldmanifest
    capture quietly file open `oldmanifest' using `"`target'hxempirical.pkg"', read text
    if !_rc {
        file read `oldmanifest' oldline
        while r(eof) == 0 {
            local oldline = trim(`"`oldline'"')
            gettoken oldtag oldrest : oldline
            if lower(`"`oldtag'"') == "v" {
                local old_vrest = trim(`"`oldrest'"')
                if `"`old_manifest_format'"' != "" | `"`old_vrest'"' != "3" local old_manifest_safe 0
                else local old_manifest_format `"`old_vrest'"'
            }
            if lower(`"`oldtag'"') == "f" {
                gettoken oldname oldunused : oldrest
                local oldname = trim(`"`oldname'"')
                local oldname_key = lower(`"`oldname'"')
                local oldunused = trim(`"`oldunused'"')
                if `"`oldname'"' == "" | `"`oldunused'"' != "" | ///
                    !regexm(`"`oldname'"', "^hx[A-Za-z0-9_.-]+$") | ///
                    strpos(`"`oldname'"', "..") | strpos(`"`oldname'"', "/") | ///
                    strpos(`"`oldname'"', "\") | strpos(`"`oldname'"', ":") | ///
                    substr(`"`oldname'"', -1, 1) == "." | ///
                    strpos(`" `oldfiles_key' "', `" `oldname_key' "') {
                    local old_manifest_safe 0
                }
                else {
                    local oldfiles `"`oldfiles' `oldname'"'
                    local oldfiles_key `"`oldfiles_key' `oldname_key'"'
                }
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
local oldfiles_key = trim(itrim(`"`oldfiles_key'"'))
if `"`old_manifest_format'"' != "3" local old_manifest_safe 0

/* A repeat install may use the fast path only after every managed file matches
   the locally stored Stata/POSIX checksum and byte length.  Older releases do
   not have this integrity file and therefore receive one verified repair. */
local install_complete 0
local local_pkg_bound 0
local integrity_file `"`target'hxempirical.integrity"'
capture quietly confirm file `"`integrity_file'"'
if !_rc {
    tempname integrity_in
    capture quietly file open `integrity_in' using `"`integrity_file'"', read text
    if !_rc {
        local integrity_ok 1
        local integrity_format ""
        local integrity_version ""
        local integrity_pkg_bytes ""
        local integrity_pkg_checksum ""
        local integrity_seen ""
        local integrity_count 0
        file read `integrity_in' integrity_line
        while r(eof) == 0 {
            local integrity_line = trim(`"`integrity_line'"')
            gettoken integrity_tag integrity_rest : integrity_line
            if lower(`"`integrity_tag'"') == "v" {
                local integrity_value = trim(`"`integrity_rest'"')
                if `"`integrity_format'"' != "" | `"`integrity_value'"' != "1" local integrity_ok 0
                else local integrity_format `"`integrity_value'"'
            }
            else if lower(`"`integrity_tag'"') == "d" {
                gettoken integrity_key integrity_value : integrity_rest
                local integrity_value = trim(`"`integrity_value'"')
                if lower(`"`integrity_key'"') == "version" local integrity_version `"`integrity_value'"'
                if lower(`"`integrity_key'"') == "pkg_bytes" local integrity_pkg_bytes `"`integrity_value'"'
                if lower(`"`integrity_key'"') == "pkg_checksum" local integrity_pkg_checksum `"`integrity_value'"'
            }
            else if lower(`"`integrity_tag'"') == "f" {
                gettoken integrity_name integrity_rest : integrity_rest
                local integrity_name_key = lower(`"`integrity_name'"')
                gettoken expected_bytes expected_checksum : integrity_rest
                local expected_checksum = trim(`"`expected_checksum'"')
                if `"`integrity_name'"' == "" | `"`expected_bytes'"' == "" | `"`expected_checksum'"' == "" {
                    local integrity_ok 0
                }
                else if substr(`"`integrity_name'"', -1, 1) == "." | ///
                    !strpos(`" `files' "', `" `integrity_name' "') | ///
                    strpos(`" `integrity_seen' "', `" `integrity_name_key' "') {
                    local integrity_ok 0
                }
                else {
                    local integrity_seen `"`integrity_seen' `integrity_name_key'"'
                    local ++integrity_count
                    capture quietly checksum `"`target'`integrity_name'"'
                    local checksum_rc = _rc
                    if `checksum_rc' local integrity_ok 0
                    else if r(filelen) != real(`"`expected_bytes'"') | r(checksum) != real(`"`expected_checksum'"') local integrity_ok 0
                }
            }
            file read `integrity_in' integrity_line
        }
        file close `integrity_in'
        if !missing(real(`"`integrity_pkg_bytes'"')) & !missing(real(`"`integrity_pkg_checksum'"')) {
            capture quietly checksum `"`target'hxempirical.pkg"'
            if !_rc & r(filelen) == real(`"`integrity_pkg_bytes'"') & r(checksum) == real(`"`integrity_pkg_checksum'"') {
                local local_pkg_bound 1
            }
        }
        if !`local_pkg_bound' local integrity_ok 0
        if `"`integrity_format'"' != "1" local integrity_ok 0
        if `"`integrity_version'"' != `"`package_version'"' local integrity_ok 0
        if `integrity_count' != `nfiles' local integrity_ok 0
        foreach f of local files {
            local f_key = lower(`"`f'"')
            if !strpos(`" `integrity_seen' "', `" `f_key' "') local integrity_ok 0
        }
        if `integrity_ok' local install_complete 1
    }
}
if !`local_pkg_bound' | !`old_manifest_safe' {
    /* A damaged legacy manifest is never allowed to define obsolete files. */
    local oldfiles ""
    local installed_version ""
}
if `"`installed_version'"' == "" {
    noisily display as text "当前状态：" as result "尚未安装"
}
else {
    noisily display as text "当前版本：" as result "`installed_version'"
}
noisily display as text "最新版本：" as result "`package_version'"
if `"`action'"' == "update" & !`install_complete' {
    noisily display as text "检测到安装文件不完整，将自动修复。"
    local action "repair"
}
if `"`action'"' == "repair" noisily display as text "正在执行修复安装……"
else if `"`action'"' == "update" noisily display as text "正在准备更新……"
else noisily display as text "正在准备安装……"

/* Use per-run staging and backup directories to avoid collisions between
   concurrent or interrupted installer runs. */
tempfile runbase
local stage `"`runbase'_stage"'
local backup `"`runbase'_backup"'
capture quietly mkdir `"`stage'"'
capture quietly mkdir `"`backup'"'
local slast = substr(`"`stage'"', strlen(`"`stage'"'), 1)
if !inlist(`"`slast'"', "/", "\") local stage `"`stage'/"'
local blast = substr(`"`backup'"', strlen(`"`backup'"'), 1)
if !inlist(`"`blast'"', "/", "\") local backup `"`backup'/"'

/* Download one release as small Base64 text segments.  This avoids the long,
   silent binary-JAR transfer that can be blocked by TLS inspection software. */
tempfile bundle_b64 bundle_zip
local download_failed 0
local index_source `"`manifest_source'"'
local failure_stage ""
local stage_aux "hxempirical.pkg hxinstall.do hxinstall_offline.do INSTALL.md hxempirical-offline.index __hx_release_part"

local parts ""
local expected_parts ""
local expected_bytes ""
local expected_checksum ""
local expected_archive ""
local expected_version ""
local expected_package ""
local expected_pkg_bytes ""
local expected_pkg_checksum ""
local index_format ""
if `exploded_source' {
    local expected_version `"`package_version'"'
    local expected_package "hxempirical.pkg"
    local expected_pkg_bytes `"`exploded_pkg_bytes'"'
    local expected_pkg_checksum `"`exploded_pkg_checksum'"'
}
if !`exploded_source' & !`download_failed' {
    tempname index_handle
    file open `index_handle' using `"`bundle_index'"', read text
    file read `index_handle' index_line
    while r(eof) == 0 {
        local index_line = trim(`"`index_line'"')
        gettoken index_tag index_rest : index_line
        if lower(`"`index_tag'"') == "v" {
            local index_value = trim(`"`index_rest'"')
            if `"`index_format'"' != "" | `"`index_value'"' != "1" local download_failed 1
            else local index_format `"`index_value'"'
        }
        else if lower(`"`index_tag'"') == "f" {
            gettoken part_name index_unused : index_rest
            local part_name = trim(`"`part_name'"')
            local index_unused = trim(`"`index_unused'"')
            if `"`part_name'"' != "" {
                if `"`index_unused'"' != "" | ///
                    !regexm(`"`part_name'"', "^release/hxempirical-release[.]b64[.][0-9][0-9][0-9]$") | ///
                    strpos(`" `parts' "', `" `part_name' "') local download_failed 1
                else local parts `"`parts' `part_name'"'
            }
            else local download_failed 1
        }
        if lower(`"`index_tag'"') == "d" {
            gettoken index_key index_value : index_rest
            local index_value = trim(`"`index_value'"')
            if lower(`"`index_key'"') == "archive" local expected_archive `"`index_value'"'
            if lower(`"`index_key'"') == "parts" local expected_parts `"`index_value'"'
            if lower(`"`index_key'"') == "bytes" local expected_bytes `"`index_value'"'
            if lower(`"`index_key'"') == "checksum" local expected_checksum `"`index_value'"'
            if lower(`"`index_key'"') == "version" local expected_version `"`index_value'"'
            if lower(`"`index_key'"') == "package" local expected_package `"`index_value'"'
            if lower(`"`index_key'"') == "pkg_bytes" local expected_pkg_bytes `"`index_value'"'
            if lower(`"`index_key'"') == "pkg_checksum" local expected_pkg_checksum `"`index_value'"'
        }
        file read `index_handle' index_line
    }
    file close `index_handle'
}
local parts = trim(itrim(`"`parts'"'))
local nparts : word count `parts'
if !`exploded_source' & (`"`index_format'"' != "1" | `nparts' == 0 | missing(real(`"`expected_parts'"')) | missing(real(`"`expected_bytes'"')) | missing(real(`"`expected_checksum'"'))) {
    local download_failed 1
    local failure_stage "解析发布包索引"
}
if !`exploded_source' & !`download_failed' & (`nparts' != real(`"`expected_parts'"') | real(`"`expected_parts'"') <= 0 | real(`"`expected_bytes'"') <= 0 | real(`"`expected_checksum'"') < 0 | missing(real(`"`expected_pkg_bytes'"')) | missing(real(`"`expected_pkg_checksum'"'))) {
    local download_failed 1
    local failure_stage "校验发布包索引字段"
}
if !`exploded_source' & !`download_failed' & (`"`expected_archive'"' != "hxempirical-release.zip" | `"`expected_package'"' != "hxempirical.pkg" | `"`expected_version'"' != `"`package_version'"' | real(`"`expected_pkg_bytes'"') <= 0 | real(`"`expected_pkg_checksum'"') < 0) {
    local download_failed 1
    local failure_stage "校验发布包与安装清单绑定"
}
if !`exploded_source' & !`download_failed' {
    capture quietly checksum `"`pkg'"'
    local pkg_checksum_rc = _rc
    if `pkg_checksum_rc' {
        local download_failed 1
        local failure_stage "计算安装清单 checksum，r(`pkg_checksum_rc')"
    }
    else if r(filelen) != real(`"`expected_pkg_bytes'"') | r(checksum) != real(`"`expected_pkg_checksum'"') {
        local download_failed 1
        local failure_stage "安装清单长度或 checksum 不匹配"
    }
}

/* A byte-perfect target is not enough: Stata must actually resolve the
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

/* Same-version fast return is allowed only after the same-source package and
   release index are mutually bound and the local per-file integrity scan has
   passed. */
if !`download_failed' & `"`action'"' == "update" & `"`installed_version'"' == `"`package_version'"' & `install_complete' {
    capture program drop hxsetup
    capture quietly run `"`target'hxsetup.ado"'
    local setup_loader_rc = _rc
    local menu_rc `setup_loader_rc'
    if !`setup_loader_rc' {
        capture noisily hxsetup, persist menusource(`"`target'hxmenu.ado"')
        local menu_rc = _rc
    }
    noisily display as result "已是最新版本，受管文件完整性检查通过。"
    noisily display as text "启动命令：" as result "hxempirical"
    if `menu_rc' noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"
    exit 0
}

tempname bundle_out
local bundle_open 0
if !`exploded_source' & !`download_failed' {
    file open `bundle_out' using `"`bundle_b64'"', write text replace
    local bundle_open 1
}
local part_number 0
if !`exploded_source' & `remote_source' {
    quietly set timeout1 10
    quietly set timeout2 20
}
foreach part of local parts {
    if `download_failed' continue, break
    local ++part_number
    noisily display as text "正在取得发布包：`part_number'/`nparts'（每段网络等待上限 20 秒）"
    local part_file `"`stage'__hx_release_part"'
    local got 0
    capture quietly copy `"`release_base'/`part'"' `"`part_file'"', replace
    if !_rc local got 1
    if !`got' {
        local download_failed 1
        local failure_stage "下载第 `part_number'/`nparts' 段"
        continue, break
    }

    tempname part_in
    file open `part_in' using `"`part_file'"', read text
    file read `part_in' part_line
    while r(eof) == 0 {
        file write `bundle_out' `"`part_line'"' _n
        file read `part_in' part_line
    }
    file close `part_in'
    capture quietly erase `"`part_file'"'
}
if `bundle_open' capture file close `bundle_out'

if !`exploded_source' & `remote_source' {
    quietly set timeout1 `old_timeout1'
    quietly set timeout2 `old_timeout2'
}

if !`exploded_source' & !`download_failed' {
    local bundle_b64_java : subinstr local bundle_b64 "\" "\\", all
    local bundle_zip_java : subinstr local bundle_zip "\" "\\", all
    capture java: java.nio.file.Files.write(java.nio.file.Paths.get("`bundle_zip_java'"), java.util.Base64.getMimeDecoder().decode(java.nio.file.Files.readString(java.nio.file.Paths.get("`bundle_b64_java'"))))
    local decode_rc = _rc
    if `decode_rc' {
        local download_failed 1
        local failure_stage "Base64 解码，r(`decode_rc')"
    }
}

/* Stata's official checksum command implements the POSIX 1003.2 CRC.  Bind
   the decoded archive to both the byte length and checksum advertised by the
   same-source release index before unzipfile sees it. */
if !`exploded_source' & !`download_failed' {
    capture quietly checksum `"`bundle_zip'"'
    local archive_checksum_rc = _rc
    if `archive_checksum_rc' {
        local download_failed 1
        local failure_stage "计算发布包 checksum，r(`archive_checksum_rc')"
    }
    else if r(filelen) != real(`"`expected_bytes'"') | r(checksum) != real(`"`expected_checksum'"') {
        local download_failed 1
        local failure_stage "发布包长度或 checksum 不匹配"
    }
}

if !`exploded_source' & !`download_failed' {
    local install_pwd `"`c(pwd)'"'
    capture quietly cd `"`stage'"'
    if _rc {
        local download_failed 1
        local failure_stage "进入临时目录"
    }
    if !`download_failed' {
        capture quietly unzipfile `"`bundle_zip'"', replace
        if _rc {
            local unzip_rc = _rc
            local download_failed 1
            local failure_stage "解压发布包，r(`unzip_rc')"
        }
    }
    capture quietly cd `"`install_pwd'"'
}

if `exploded_source' & !`download_failed' {
    foreach f of local files {
        capture quietly copy `"`release_base'/`f'"' `"`stage'`f'"', replace
        if _rc {
            local download_failed 1
            local failure_stage "读取离线文件 `f'"
            continue, break
        }
    }
}

if !`download_failed' {
    foreach f of local files {
        capture quietly confirm file `"`stage'`f'"'
        if _rc {
            noisily display as error "发布包校验失败：缺少 `f'"
            local download_failed 1
            local failure_stage "校验发布文件"
            continue, break
        }
    }
}

/* Build the local integrity record entirely from verified staged files before
   touching the live installation.  A write error therefore cannot bypass the
   transaction rollback after commit. */
tempfile new_integrity
if !`download_failed' {
    tempname integrity_out
    capture quietly file open `integrity_out' using `"`new_integrity'"', write text replace
    if _rc {
        local download_failed 1
        local failure_stage "创建本地完整性记录"
    }
    else {
        capture file write `integrity_out' "v 1" _n
        if _rc local download_failed 1
        if !`download_failed' {
            capture file write `integrity_out' "d version `package_version'" _n
            if _rc local download_failed 1
        }
        if !`download_failed' {
            capture file write `integrity_out' "d pkg_bytes `expected_pkg_bytes'" _n
            if _rc local download_failed 1
        }
        if !`download_failed' {
            capture file write `integrity_out' "d pkg_checksum `expected_pkg_checksum'" _n
            if _rc local download_failed 1
        }
        foreach f of local files {
            if `download_failed' continue, break
            capture quietly checksum `"`stage'`f'"'
            local checksum_rc = _rc
            if `checksum_rc' {
                local download_failed 1
                continue, break
            }
            if r(filelen) <= 0 {
                local download_failed 1
                continue, break
            }
            local file_bytes = trim(strofreal(r(filelen), "%21.0f"))
            local file_checksum = trim(strofreal(r(checksum), "%21.0f"))
            capture file write `integrity_out' "f `f' `file_bytes' `file_checksum'" _n
            if _rc local download_failed 1
        }
        capture file close `integrity_out'
        if _rc local download_failed 1
        if `download_failed' local failure_stage "写入本地完整性记录"
    }
}

if `download_failed' {
    foreach f of local files {
        capture quietly erase `"`stage'`f'"'
    }
    foreach f of local stage_aux {
        capture quietly erase `"`stage'`f'"'
    }
    capture quietly rmdir `"`stage'"'
    capture quietly rmdir `"`backup'"'
    noisily display as error "发布包未能完整取得，现有 hxempirical 安装保持不变。"
    if `"`failure_stage'"' != "" noisily display as text "失败阶段：`failure_stage'"
    noisily display as text  "当前网络对 Stata 的 GitHub 下载有限制。请使用浏览器离线安装："
    noisily display as result "  `pages'/hxempirical-release.zip"
    noisily display as text  "下载并解压后，在 Stata 中运行其中的 hxinstall_offline.do。"
    exit 603
}

/* Back up every file that this release may replace. */
local backup_failed 0
foreach f of local files {
    if `backup_failed' continue, break
    capture quietly confirm file `"`target'`f'"'
    if !_rc {
        capture quietly copy `"`target'`f'"' `"`backup'`f'"', replace
        if _rc {
            noisily display as error "无法备份现有文件：`target'`f'"
            local backup_failed 1
        }
    }
}
foreach f of local oldfiles {
    if `backup_failed' continue, break
    if !strpos(`" `files' "', `" `f' "') {
        capture quietly confirm file `"`target'`f'"'
        if !_rc {
            capture quietly copy `"`target'`f'"' `"`backup'`f'"', replace
            if _rc {
                noisily display as error "无法备份旧版本文件：`target'`f'"
                local backup_failed 1
            }
        }
    }
}
if !`backup_failed' capture quietly confirm file `"`target'hxempirical.pkg"'
if !`backup_failed' & !_rc {
    capture quietly copy `"`target'hxempirical.pkg"' `"`backup'hxempirical.pkg"', replace
    if _rc {
        noisily display as error "无法备份现有安装清单：`target'hxempirical.pkg"
        local backup_failed 1
    }
}
if !`backup_failed' capture quietly confirm file `"`target'hxempirical.integrity"'
if !`backup_failed' & !_rc {
    capture quietly copy `"`target'hxempirical.integrity"' `"`backup'hxempirical.integrity"', replace
    if _rc {
        noisily display as error "无法备份现有完整性清单：`target'hxempirical.integrity"
        local backup_failed 1
    }
}
if `backup_failed' {
    foreach f of local files {
        capture quietly erase `"`stage'`f'"'
        capture quietly erase `"`backup'`f'"'
    }
    foreach f of local stage_aux {
        capture quietly erase `"`stage'`f'"'
    }
    foreach f of local oldfiles {
        capture quietly erase `"`backup'`f'"'
    }
    capture quietly erase `"`backup'hxempirical.pkg"'
    capture quietly erase `"`backup'hxempirical.integrity"'
    capture quietly rmdir `"`stage'"'
    capture quietly rmdir `"`backup'"'
    noisily display as text "现有安装未修改。"
    exit 603
}

/* Commit the JAR first. A loaded/locked JAR therefore stops the update before
   any ado/help file is replaced. */
local commitfiles ""
if strpos(`" `files' "', " hxworkbench.jar ") local commitfiles "hxworkbench.jar"
foreach f of local files {
    if `"`f'"' != "hxworkbench.jar" local commitfiles `"`commitfiles' `f'"'
}
local commitfiles = trim(itrim(`"`commitfiles'"'))

local install_failed 0
foreach f of local commitfiles {
    capture quietly checksum `"`stage'`f'"'
    local staged_checksum_rc = _rc
    if `staged_checksum_rc' {
        local install_failed 1
        continue, break
    }
    local staged_bytes = r(filelen)
    local staged_checksum = r(checksum)
    capture quietly copy `"`stage'`f'"' `"`target'`f'"', replace
    if _rc {
        noisily display as error "写入失败：`target'`f'"
        local install_failed 1
        continue, break
    }
    capture quietly checksum `"`target'`f'"'
    local committed_checksum_rc = _rc
    if `committed_checksum_rc' {
        noisily display as error "写入后校验失败：`target'`f'"
        local install_failed 1
        continue, break
    }
    if r(filelen) != `staged_bytes' | r(checksum) != `staged_checksum' {
        noisily display as error "写入后校验失败：`target'`f'"
        local install_failed 1
        continue, break
    }
}
if !`install_failed' {
    capture quietly copy `"`pkg'"' `"`target'hxempirical.pkg"', replace
    if _rc {
        noisily display as error "写入安装清单失败：`target'hxempirical.pkg"
        local install_failed 1
    }
    else {
        capture quietly checksum `"`target'hxempirical.pkg"'
        local committed_pkg_checksum_rc = _rc
        if `committed_pkg_checksum_rc' {
            noisily display as error "写入后校验失败：`target'hxempirical.pkg"
            local install_failed 1
        }
        else if r(filelen) != real(`"`expected_pkg_bytes'"') | r(checksum) != real(`"`expected_pkg_checksum'"') {
            noisily display as error "写入后校验失败：`target'hxempirical.pkg"
            local install_failed 1
        }
    }
}
if !`install_failed' {
    quietly checksum `"`new_integrity'"'
    local new_integrity_bytes = r(filelen)
    local new_integrity_checksum = r(checksum)
    capture quietly copy `"`new_integrity'"' `"`target'hxempirical.integrity"', replace
    if _rc local install_failed 1
    else {
        capture quietly checksum `"`target'hxempirical.integrity"'
        if _rc local install_failed 1
        else if r(filelen) != `new_integrity_bytes' | r(checksum) != `new_integrity_checksum' local install_failed 1
    }
}

/* Obsolete managed files are part of the same transaction.  A locked or
   otherwise undeletable old file must not be hidden by the new manifest and
   integrity record, because a later fast update would never see it again. */
if !`install_failed' {
    foreach f of local oldfiles {
        if strpos(`" `files' "', `" `f' "') continue
        capture quietly confirm file `"`target'`f'"'
        if _rc continue
        local obsolete_erase_rc 0
        if `"${HXEI_TEST_FAIL_FILE}"' == `"`f'"' local obsolete_erase_rc 602
        else {
            capture quietly erase `"`target'`f'"'
            local obsolete_erase_rc = _rc
            capture quietly confirm file `"`target'`f'"'
            if !_rc local obsolete_erase_rc 602
            else if `obsolete_erase_rc' local obsolete_erase_rc 0
        }
        if `obsolete_erase_rc' {
            noisily display as error "无法移除旧版本文件：`target'`f'"
            local install_failed 1
            continue, break
        }
    }
}

/* Do not report success merely because files were written.  Verify the exact
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

/* Restore the complete previous installation when any commit step fails. */
if `install_failed' {
    local restore_failed 0
    local restore_targets `"`files'"'
    foreach f of local oldfiles {
        if !strpos(`" `restore_targets' "', `" `f' "') local restore_targets `"`restore_targets' `f'"'
    }
    foreach f in hxempirical.pkg hxempirical.integrity {
        if !strpos(`" `restore_targets' "', `" `f' "') local restore_targets `"`restore_targets' `f'"'
    }
    local restore_targets = trim(itrim(`"`restore_targets'"'))
    foreach f of local restore_targets {
        capture quietly confirm file `"`backup'`f'"'
        if !_rc {
            capture quietly checksum `"`backup'`f'"'
            if _rc local restore_failed 1
            else {
                local restore_bytes = r(filelen)
                local restore_checksum = r(checksum)
                capture quietly copy `"`backup'`f'"' `"`target'`f'"', replace
                if _rc local restore_failed 1
                else {
                    capture quietly checksum `"`target'`f'"'
                    if _rc local restore_failed 1
                    else if r(filelen) != `restore_bytes' | r(checksum) != `restore_checksum' local restore_failed 1
                }
            }
        }
        else {
            capture quietly erase `"`target'`f'"'
            capture quietly confirm file `"`target'`f'"'
            if !_rc local restore_failed 1
        }
    }

    foreach f of local files {
        capture quietly erase `"`stage'`f'"'
        if !`restore_failed' capture quietly erase `"`backup'`f'"'
    }
    foreach f of local stage_aux {
        capture quietly erase `"`stage'`f'"'
    }
    foreach f of local oldfiles {
        if !`restore_failed' capture quietly erase `"`backup'`f'"'
    }
    if !`restore_failed' {
        capture quietly erase `"`backup'hxempirical.pkg"'
        capture quietly erase `"`backup'hxempirical.integrity"'
    }
    capture quietly rmdir `"`stage'"'
    if !`restore_failed' capture quietly rmdir `"`backup'"'

    if `restore_failed' {
        noisily display as error "更新未完成，且部分文件未能自动恢复。"
        noisily display as text  "恢复备份已保留在："
        noisily display as result `"  `backup'"'
    }
    else noisily display as error "更新未完成，安装器已恢复原有文件。"
    noisily display as text  "若 hxworkbench.jar 正在使用，请关闭 Stata，重新打开后先运行更新命令。"
    exit 603
}

/* Remove per-run staging artifacts before loading any installed program. */
foreach f of local files {
    capture quietly erase `"`stage'`f'"'
    capture quietly erase `"`backup'`f'"'
}
foreach f of local stage_aux {
    capture quietly erase `"`stage'`f'"'
}
foreach f of local oldfiles {
    capture quietly erase `"`backup'`f'"'
}
capture quietly erase `"`backup'hxempirical.pkg"'
capture quietly erase `"`backup'hxempirical.integrity"'
capture quietly rmdir `"`stage'"'
capture quietly rmdir `"`backup'"'

capture quietly confirm file `"`target'hxempirical.ado"'
if _rc {
    noisily display as error "安装校验失败：未找到 hxempirical.ado。"
    exit 601
}
capture quietly confirm file `"`target'hxworkbench.jar"'
if _rc {
    noisily display as error "安装校验失败：未找到 hxworkbench.jar。"
    exit 601
}

capture quietly discard

/* A successful install/update also establishes the single persistent User-menu
   entry.  Package files remain usable if profile persistence is unavailable. */
capture program drop hxsetup
capture quietly run `"`target'hxsetup.ado"'
local setup_loader_rc = _rc
local menu_rc `setup_loader_rc'
if !`setup_loader_rc' {
    capture noisily hxsetup, persist menusource(`"`target'hxmenu.ado"')
    local menu_rc = _rc
}

local verb "安装"
if `"`action'"' == "update" local verb "更新"
if `"`action'"' == "repair" local verb "修复"
noisily display as result _newline "hxempirical `verb'完成。"
if `"`package_version'"' != "" noisily display as text "版本：" as result "`package_version'"
noisily display as text "安装位置：" as result `"`target'"'
noisily display as text "清单来源：" as result "`manifest_source'"
noisily display as text _newline "验证命令：" as result "which hxempirical"
noisily display as text "启动命令：" as result "hxempirical"
if `menu_rc' {
    noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"
}
else noisily display as text "顶部入口：" as result "用户(U) > 我的实证工具箱"
noisily display as text "如本次更新前已打开工作台，请重新启动 Stata。"
end

capture program drop _hxinstaller_effective
program define _hxinstaller_effective, rclass
    version 17.0
    syntax , TARGET(string) PACKAGEVERSION(string)

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
