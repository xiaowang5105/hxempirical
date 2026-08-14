*! hxinstall 1.1.0  14aug2026
*! Transactional bootstrap installer for hxempirical
version 17.0
set more off

args action
local action = lower(trim(`"`action'"'))
if `"`action'"' == "" local action "install"
if !inlist(`"`action'"', "install", "update", "uninstall") {
    display as error "用法：do hxinstall.do [install|update|uninstall]"
    exit 198
}

local pages "https://xiaowang5105.github.io/hxempirical"
local raw   "https://raw.githubusercontent.com/xiaowang5105/hxempirical/main"

if c(stata_version) < 17 {
    display as error "hxempirical 需要 Stata 17 或更高版本。"
    display as text  "当前版本：Stata `c(stata_version)'。"
    exit 9
}

/* PERSONAL is normally user-writable and is searched before PLUS. */
local target `"`c(sysdir_personal)'"'
if `"`target'"' == "" {
    display as error "Stata 没有返回 PERSONAL ado 目录。请先运行 sysdir 检查安装环境。"
    exit 603
}
capture mkdir `"`target'"'
local lastchar = substr(`"`target'"', strlen(`"`target'"'), 1)
if !inlist(`"`lastchar'"', "/", "\") local target `"`target'/"'

/* Fail early when PERSONAL is not writable. */
local probe `"`target'__hxempirical_write_test.tmp"'
tempname probehandle
capture file open `probehandle' using `"`probe'"', write text replace
if _rc {
    display as error "无法写入 Stata PERSONAL 目录：`target'"
    display as text  "请运行 sysdir 查看目录设置，或联系管理员检查该目录权限。"
    exit 603
}
file write `probehandle' "hxempirical write test" _n
file close `probehandle'
capture erase `"`probe'"'

/* Uninstall works offline when the locally stored manifest is available. */
tempfile pkg
local manifest_source ""
if `"`action'"' == "uninstall" {
    capture confirm file `"`target'hxempirical.pkg"'
    if !_rc {
        capture quietly copy `"`target'hxempirical.pkg"' `"`pkg'"', replace
        if !_rc local manifest_source "本地安装清单"
    }
}

/* Pages is the stable primary source. Retry transient failures before using
   Raw as a best-effort fallback for networks where it is reachable. */
if `"`manifest_source'"' == "" {
    forvalues attempt = 1/3 {
        capture quietly copy `"`pages'/hxempirical.pkg"' `"`pkg'"', replace
        if !_rc {
            local manifest_source "GitHub Pages"
            continue, break
        }
        if `attempt' < 3 sleep 300
    }
}
if `"`manifest_source'"' == "" {
    forvalues attempt = 1/2 {
        capture quietly copy `"`raw'/hxempirical.pkg"' `"`pkg'"', replace
        if !_rc {
            local manifest_source "GitHub Raw"
            continue, break
        }
        if `attempt' < 2 sleep 300
    }
}
if `"`manifest_source'"' == "" {
    display as error "无法读取 hxempirical 安装清单。"
    display as text  "请确认能访问 `pages'/hxempirical.pkg 后重试。"
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
    display as error "安装清单为空，操作已停止。"
    exit 498
}

if `"`action'"' == "uninstall" {
    capture noisily hxsetup, remove

    local erase_failed 0
    foreach f of local files {
        capture erase `"`target'`f'"'
        if _rc {
            capture confirm file `"`target'`f'"'
            if !_rc {
                display as error "暂时无法删除：`target'`f'"
                local erase_failed 1
            }
        }
    }
    capture erase `"`target'hxempirical.pkg"'
    /* Remove one legacy PLUS registration when it is unambiguous. Older
       machines may contain several registrations; leave those records to
       Stata's package manager and report the exact cleanup command. */
    capture quietly ado uninstall hxempirical, from(PLUS)
    capture discard

    if `erase_failed' {
        display as error _newline "部分文件正在被 Stata 使用。"
        display as text "请关闭所有 Stata 窗口，重新打开后再运行同一条卸载命令。"
        exit 602
    }
    capture quietly which hxempirical
    local legacy_found = !_rc
    display as result _newline "hxempirical 的 PERSONAL 安装已卸载。"
    if `legacy_found' {
        display as text "检测到 ado-path 中还有旧的 net install 记录。请运行："
        display as result "  ado dir hxempirical"
        display as text   "再按列表编号运行：ado uninstall [编号]"
    }
    display as text "请重新启动 Stata，使已加载的 Java 类完全释放。"
    exit 0
}

/* Read the previous manifest so obsolete managed files can be removed only
   after a successful update. */
local oldfiles ""
capture confirm file `"`target'hxempirical.pkg"'
if !_rc {
    tempname oldmanifest
    capture file open `oldmanifest' using `"`target'hxempirical.pkg"', read text
    if !_rc {
        file read `oldmanifest' oldline
        while r(eof) == 0 {
            local oldline = trim(`"`oldline'"')
            gettoken oldtag oldrest : oldline
            if lower(`"`oldtag'"') == "f" {
                gettoken oldname oldunused : oldrest
                if `"`oldname'"' != "" local oldfiles `"`oldfiles' `oldname'"'
            }
            file read `oldmanifest' oldline
        }
        file close `oldmanifest'
    }
}
local oldfiles = trim(itrim(`"`oldfiles'"'))

/* Use per-run staging and backup directories to avoid collisions between
   concurrent or interrupted installer runs. */
tempfile runbase
local stage `"`runbase'_stage"'
local backup `"`runbase'_backup"'
capture mkdir `"`stage'"'
capture mkdir `"`backup'"'
local slast = substr(`"`stage'"', strlen(`"`stage'"'), 1)
if !inlist(`"`slast'"', "/", "\") local stage `"`stage'/"'
local blast = substr(`"`backup'"', strlen(`"`backup'"'), 1)
if !inlist(`"`blast'"', "/", "\") local backup `"`backup'/"'

/* Download the complete release before changing the existing installation. */
local download_failed 0
local fallback_count 0
display as text "正在下载 hxempirical `package_version'（`nfiles' 个文件）..."
foreach f of local files {
    local got 0
    forvalues attempt = 1/3 {
        capture quietly copy `"`pages'/`f'"' `"`stage'`f'"', replace
        if !_rc {
            local got 1
            continue, break
        }
        if `attempt' < 3 sleep 250
    }
    if !`got' {
        forvalues attempt = 1/2 {
            capture quietly copy `"`raw'/`f'"' `"`stage'`f'"', replace
            if !_rc {
                local got 1
                local ++fallback_count
                continue, break
            }
            if `attempt' < 2 sleep 250
        }
    }
    if !`got' {
        display as error "下载失败：`f'"
        local download_failed 1
        continue, break
    }
}
if `download_failed' {
    display as error "下载未完成，现有 hxempirical 安装保持不变。"
    display as text  "请检查网络后重新运行同一条命令。"
    exit 603
}

/* Back up every file that this release may replace. */
foreach f of local files {
    capture confirm file `"`target'`f'"'
    if !_rc {
        capture quietly copy `"`target'`f'"' `"`backup'`f'"', replace
        if _rc {
            display as error "无法备份现有文件：`target'`f'"
            exit 603
        }
    }
}
foreach f of local oldfiles {
    if !strpos(`" `files' "', `" `f' "') {
        capture confirm file `"`target'`f'"'
        if !_rc capture quietly copy `"`target'`f'"' `"`backup'`f'"', replace
    }
}
capture confirm file `"`target'hxempirical.pkg"'
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
        display as error "写入失败：`target'`f'"
        local install_failed 1
        continue, break
    }
}
if !`install_failed' {
    capture quietly copy `"`pkg'"' `"`target'hxempirical.pkg"', replace
    if _rc {
        display as error "写入安装清单失败：`target'hxempirical.pkg"
        local install_failed 1
    }
}

/* Restore the complete previous installation when any commit step fails. */
if `install_failed' {
    foreach f of local files {
        capture confirm file `"`backup'`f'"'
        if !_rc capture quietly copy `"`backup'`f'"' `"`target'`f'"', replace
        else capture erase `"`target'`f'"'
    }
    foreach f of local oldfiles {
        capture confirm file `"`backup'`f'"'
        if !_rc capture quietly copy `"`backup'`f'"' `"`target'`f'"', replace
    }
    capture confirm file `"`backup'hxempirical.pkg"'
    if !_rc capture quietly copy `"`backup'hxempirical.pkg"' `"`target'hxempirical.pkg"', replace
    else capture erase `"`target'hxempirical.pkg"'

    display as error "更新未完成，安装器已恢复原有文件。"
    display as text  "若 hxworkbench.jar 正在使用，请关闭 Stata，重新打开后先运行更新命令。"
    exit 603
}

/* Remove files that belonged to an older release but are absent now. */
foreach f of local oldfiles {
    if !strpos(`" `files' "', `" `f' "') capture erase `"`target'`f'"'
}

capture confirm file `"`target'hxempirical.ado"'
if _rc {
    display as error "安装校验失败：未找到 hxempirical.ado。"
    exit 601
}
capture confirm file `"`target'hxworkbench.jar"'
if _rc {
    display as error "安装校验失败：未找到 hxworkbench.jar。"
    exit 601
}

capture discard

local verb "安装"
if `"`action'"' == "update" local verb "更新"
display as result _newline "hxempirical `verb'完成。"
if `"`package_version'"' != "" display as text "版本：" as result "`package_version'"
display as text "安装位置：" as result `"`target'"'
display as text "清单来源：" as result "`manifest_source'"
if `fallback_count' > 0 display as text "网络回退：" as result "有 `fallback_count' 个文件改用 GitHub Raw 下载。"
display as text _newline "验证命令：" as result "which hxempirical"
display as text "启动命令：" as result "hxempirical"
display as text "如本次更新前已打开工作台，请重新启动 Stata。"
