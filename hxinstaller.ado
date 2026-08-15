*! hxinstaller 1.4.0  15aug2026
*! Hidden transactional installer core for hxempirical
program define hxinstaller
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

/* PERSONAL is normally user-writable and is searched before PLUS. */
local target `"`c(sysdir_personal)'"'
if `"`target'"' == "" {
    noisily display as error "Stata 没有返回 PERSONAL ado 目录。请先运行 sysdir 检查安装环境。"
    exit 603
}
capture quietly mkdir `"`target'"'
local lastchar = substr(`"`target'"', strlen(`"`target'"'), 1)
if !inlist(`"`lastchar'"', "/", "\") local target `"`target'/"'

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
tempfile pkg
local manifest_source ""
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

/* Pages is the primary source. Raw is one bounded fallback. */
if `"`manifest_source'"' == "" {
    capture quietly copy `"`pages'/hxempirical.pkg"' `"`pkg'"', replace
    if !_rc {
        if `remote_source' local manifest_source "GitHub Pages"
        else local manifest_source "本地离线包"
    }
}
if `"`manifest_source'"' == "" {
    capture quietly copy `"`raw'/hxempirical.pkg"' `"`pkg'"', replace
    if !_rc local manifest_source "GitHub Raw"
}
if `remote_source' {
    quietly set timeout1 `old_timeout1'
    quietly set timeout2 `old_timeout2'
}
if `"`manifest_source'"' == "" {
    noisily display as error "无法读取 hxempirical 安装清单。"
    noisily display as text  "当前网络未能在限定时间内连接 GitHub。"
    noisily display as text  "请用浏览器打开安装说明：`pages'/INSTALL.md"
    exit 603
}

/* Read the release manifest. */
tempname manifest
file open `manifest' using `"`pkg'"', read text
local files ""
local package_version ""
file read `manifest' line
while r(eof) == 0 {
    local line = trim(`"`line'"')
    gettoken tag rest : line
    if lower(`"`tag'"') == "f" {
        gettoken fname unused : rest
        if `"`fname'"' != "" local files `"`files' `fname'"'
    }
    if lower(`"`tag'"') == "d" {
        gettoken dkey drest : rest
        if lower(`"`dkey'"') == "version" local package_version = trim(`"`drest'"')
    }
    file read `manifest' line
}
file close `manifest'
local files = trim(itrim(`"`files'"'))
local nfiles : word count `files'
if `nfiles' == 0 {
    noisily display as error "安装清单为空，操作已停止。"
    exit 498
}

if `"`action'"' == "uninstall" {
    capture noisily hxsetup, remove

    local erase_failed 0
    foreach f of local files {
        capture quietly erase `"`target'`f'"'
        if _rc {
            capture quietly confirm file `"`target'`f'"'
            if !_rc {
                noisily display as error "暂时无法删除：`target'`f'"
                local erase_failed 1
            }
        }
    }
    capture quietly erase `"`target'hxinstaller.ado"'
    if _rc {
        capture quietly confirm file `"`target'hxinstaller.ado"'
        if !_rc {
            noisily display as error "暂时无法删除：`target'hxinstaller.ado"
            local erase_failed 1
        }
    }
    capture quietly erase `"`target'hxempirical.pkg"'
    /* Remove one legacy PLUS registration when it is unambiguous. Older
       machines may contain several registrations; leave those records to
       Stata's package manager and report the exact cleanup command. */
    capture quietly ado uninstall hxempirical, from(PLUS)
    capture quietly discard

    if `erase_failed' {
        noisily display as error _newline "部分文件正在被 Stata 使用。"
        noisily display as text "请关闭所有 Stata 窗口，重新打开后再运行同一条卸载命令。"
        exit 602
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

/* A normal repeat of the public command is a fast version check.  Missing
   managed files turn the same command into a repair automatically. */
local install_complete 1
foreach f of local files {
    capture quietly confirm file `"`target'`f'"'
    if _rc local install_complete 0
}
if `"`action'"' == "update" & `"`installed_version'"' == `"`package_version'"' & `install_complete' {
    capture noisily hxsetup, persist
    local menu_rc = _rc
    noisily display as text _newline "当前版本：" as result "`installed_version'"
    noisily display as text "最新版本：" as result "`package_version'"
    noisily display as result "已是最新版本，无需更新。"
    noisily display as text "启动命令：" as result "hxempirical"
    if `menu_rc' noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"
    exit 0
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
tempfile bundle_index bundle_b64 bundle_zip
local download_failed 0
local fallback_count 0
local index_source ""
local failure_stage ""

if `remote_source' {
    quietly set timeout1 10
    quietly set timeout2 20
}
capture quietly copy `"`pages'/hxempirical-release.index"' `"`bundle_index'"', replace
if !_rc local index_source "GitHub Pages"
if `"`index_source'"' == "" {
    capture quietly copy `"`raw'/hxempirical-release.index"' `"`bundle_index'"', replace
    if !_rc local index_source "GitHub Raw"
}
if `"`index_source'"' == "" {
    local download_failed 1
    local failure_stage "读取发布包索引"
}

local parts ""
if !`download_failed' {
    tempname index_handle
    file open `index_handle' using `"`bundle_index'"', read text
    file read `index_handle' index_line
    while r(eof) == 0 {
        local index_line = trim(`"`index_line'"')
        gettoken index_tag index_rest : index_line
        if lower(`"`index_tag'"') == "f" {
            gettoken part_name index_unused : index_rest
            if `"`part_name'"' != "" local parts `"`parts' `part_name'"'
        }
        file read `index_handle' index_line
    }
    file close `index_handle'
}
local parts = trim(itrim(`"`parts'"'))
local nparts : word count `parts'
if `nparts' == 0 {
    local download_failed 1
    local failure_stage "解析发布包索引"
}

tempname bundle_out
local bundle_open 0
if !`download_failed' {
    file open `bundle_out' using `"`bundle_b64'"', write text replace
    local bundle_open 1
}
local part_number 0
foreach part of local parts {
    if `download_failed' continue, break
    local ++part_number
    noisily display as text "正在取得发布包：`part_number'/`nparts'（每段网络等待上限 20 秒）"
    local part_file `"`stage'__hx_release_part"'
    local got 0
    capture quietly copy `"`pages'/`part'"' `"`part_file'"', replace
    if !_rc local got 1
    if !`got' {
        capture quietly copy `"`raw'/`part'"' `"`part_file'"', replace
        if !_rc {
            local got 1
            local ++fallback_count
        }
    }
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

if `remote_source' {
    quietly set timeout1 `old_timeout1'
    quietly set timeout2 `old_timeout2'
}

if !`download_failed' {
    local bundle_b64_java : subinstr local bundle_b64 "\" "\\", all
    local bundle_zip_java : subinstr local bundle_zip "\" "\\", all
    capture java: java.nio.file.Files.write(java.nio.file.Paths.get("`bundle_zip_java'"), java.util.Base64.getMimeDecoder().decode(java.nio.file.Files.readString(java.nio.file.Paths.get("`bundle_b64_java'"))))
    local decode_rc = _rc
    if `decode_rc' {
        local download_failed 1
        local failure_stage "Base64 解码，r(`decode_rc')"
    }
}

if !`download_failed' {
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

if `download_failed' {
    noisily display as error "发布包未能完整取得，现有 hxempirical 安装保持不变。"
    if `"`failure_stage'"' != "" noisily display as text "失败阶段：`failure_stage'"
    noisily display as text  "当前网络对 Stata 的 GitHub 下载有限制。请使用浏览器离线安装："
    noisily display as result "  `pages'/hxempirical-release.zip"
    noisily display as text  "下载并解压后，在 Stata 中运行其中的 hxinstall_offline.do。"
    exit 603
}

/* Back up every file that this release may replace. */
foreach f of local files {
    capture quietly confirm file `"`target'`f'"'
    if !_rc {
        capture quietly copy `"`target'`f'"' `"`backup'`f'"', replace
        if _rc {
            noisily display as error "无法备份现有文件：`target'`f'"
            exit 603
        }
    }
}
foreach f of local oldfiles {
    if !strpos(`" `files' "', `" `f' "') {
        capture quietly confirm file `"`target'`f'"'
        if !_rc capture quietly copy `"`target'`f'"' `"`backup'`f'"', replace
    }
}
capture quietly confirm file `"`target'hxempirical.pkg"'
if !_rc capture quietly copy `"`target'hxempirical.pkg"' `"`backup'hxempirical.pkg"', replace

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
    capture quietly copy `"`stage'`f'"' `"`target'`f'"', replace
    if _rc {
        noisily display as error "写入失败：`target'`f'"
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
}

/* Restore the complete previous installation when any commit step fails. */
if `install_failed' {
    foreach f of local files {
        capture quietly confirm file `"`backup'`f'"'
        if !_rc capture quietly copy `"`backup'`f'"' `"`target'`f'"', replace
        else capture quietly erase `"`target'`f'"'
    }
    foreach f of local oldfiles {
        capture quietly confirm file `"`backup'`f'"'
        if !_rc capture quietly copy `"`backup'`f'"' `"`target'`f'"', replace
    }
    capture quietly confirm file `"`backup'hxempirical.pkg"'
    if !_rc capture quietly copy `"`backup'hxempirical.pkg"' `"`target'hxempirical.pkg"', replace
    else capture quietly erase `"`target'hxempirical.pkg"'

    noisily display as error "更新未完成，安装器已恢复原有文件。"
    noisily display as text  "若 hxworkbench.jar 正在使用，请关闭 Stata，重新打开后先运行更新命令。"
    exit 603
}

/* Remove files that belonged to an older release but are absent now. */
foreach f of local oldfiles {
    if !strpos(`" `files' "', `" `f' "') capture quietly erase `"`target'`f'"'
}

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
capture noisily hxsetup, persist
local menu_rc = _rc

local verb "安装"
if `"`action'"' == "update" local verb "更新"
if `"`action'"' == "repair" local verb "修复"
noisily display as result _newline "hxempirical `verb'完成。"
if `"`package_version'"' != "" noisily display as text "版本：" as result "`package_version'"
noisily display as text "安装位置：" as result `"`target'"'
noisily display as text "清单来源：" as result "`manifest_source'"
if `fallback_count' > 0 noisily display as text "网络回退：" as result "有 `fallback_count' 个文件改用 GitHub Raw 下载。"
noisily display as text _newline "验证命令：" as result "which hxempirical"
noisily display as text "启动命令：" as result "hxempirical"
if `menu_rc' {
    noisily display as text "菜单持久化未完成；可稍后运行：" as result "hxempirical menu persist"
}
else noisily display as text "顶部入口：" as result "用户(U) > 我的实证工具箱"
noisily display as text "如本次更新前已打开工作台，请重新启动 Stata。"
end
