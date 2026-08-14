*! hxinstall 1.0.0  14aug2026
*! Robust bootstrap installer for hxempirical
version 17.0
set more off

local pages "https://xiaowang5105.github.io/hxempirical"
local raw   "https://raw.githubusercontent.com/xiaowang5105/hxempirical/main"

if c(stata_version) < 17 {
    display as error "hxempirical 需要 Stata 17 或更高版本。"
    display as text  "当前版本：Stata `c(stata_version)'。"
    exit 9
}

/* Install into PERSONAL rather than PLUS.  PERSONAL is on Stata's ado-path
   and is normally owned by the current user, avoiding system/lab PLUS
   permission problems that can make net install fail with r(603). */
local target `"`c(sysdir_personal)'"'
if `"`target'"' == "" {
    display as error "Stata 没有返回 PERSONAL ado 目录。请先运行 sysdir 检查安装环境。"
    exit 603
}

capture mkdir `"`target'"'
local lastchar = substr(`"`target'"', strlen(`"`target'"'), 1)
if !inlist(`"`lastchar'"', "/", "\") local target `"`target'/"'

/* Verify target write access before downloading anything. */
local probe `"`target'__hxempirical_write_test.tmp"'
tempname probehandle
capture file open `probehandle' using `"`probe'"', write text replace
if _rc {
    display as error "无法写入 Stata PERSONAL 目录：`target'"
    display as text  "请运行 sysdir 查看目录设置，或联系这台电脑的管理员检查该目录权限。"
    exit 603
}
file write `probehandle' "hxempirical write test" _n
file close `probehandle'
capture erase `"`probe'"'

/* Fetch the package manifest.  GitHub Pages is primary; raw.githubusercontent
   is an automatic fallback if Pages is unavailable from the current network. */
tempfile pkg
capture quietly copy `"`pages'/hxempirical.pkg"' `"`pkg'"', replace
local manifest_source "GitHub Pages"
if _rc {
    capture quietly copy `"`raw'/hxempirical.pkg"' `"`pkg'"', replace
    local manifest_source "GitHub Raw"
}
if _rc {
    display as error "无法连接 hxempirical 的两个在线安装源。"
    display as text  "已尝试："
    display as text  "  1. `pages'"
    display as text  "  2. `raw'"
    display as text  "请检查网络、代理或学校/单位网络限制后重试。"
    exit 603
}

/* Read the current package file list so this installer stays in sync with
   future releases without hard-coding every production filename here. */
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
    display as error "安装清单为空，已停止安装，现有文件不会被修改。"
    exit 498
}

/* Transaction-like staging: download every production file to Stata's
   temporary directory first.  Existing installation is not touched unless
   the complete download succeeds. */
local stage `"`c(tmpdir)'hxempirical_stage"'
capture mkdir `"`stage'"'
local slast = substr(`"`stage'"', strlen(`"`stage'"'), 1)
if !inlist(`"`slast'"', "/", "\") local stage `"`stage'/"'

local download_failed 0
local fallback_count 0
display as text "正在下载 hxempirical `package_version'（`nfiles' 个文件）..."
foreach f of local files {
    capture quietly copy `"`pages'/`f'"' `"`stage'`f'"', replace
    if _rc {
        capture quietly copy `"`raw'/`f'"' `"`stage'`f'"', replace
        if !_rc local ++fallback_count
    }
    if _rc {
        display as error "下载失败：`f'"
        local download_failed 1
        continue, break
    }
}
if `download_failed' {
    display as error "下载未完成，因此没有覆盖现有 hxempirical 安装。"
    display as text  "请检查网络后重新运行同一条安装命令。"
    exit 603
}

/* Commit staged files to PERSONAL only after the full download succeeds. */
local install_failed 0
foreach f of local files {
    capture quietly copy `"`stage'`f'"' `"`target'`f'"', replace
    if _rc {
        display as error "写入失败：`target'`f'"
        local install_failed 1
        continue, break
    }
}
if `install_failed' {
    display as error "安装目录写入失败。请检查 PERSONAL 目录权限后重新运行安装器。"
    exit 603
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

/* Drop cached ado programs so an update can be used in the same session.
   The dataset is not changed. */
capture discard

noi display as result _newline "hxempirical 安装完成。"
if `"`package_version'"' != "" noi display as text "版本：" as result "`package_version'"
noi display as text "安装位置：" as result `"`target'"'
noi display as text "清单来源：" as result "`manifest_source'"
if `fallback_count' > 0 noi display as text "网络回退：" as result "有 `fallback_count' 个文件自动改用 GitHub Raw 下载。"
noi display as text _newline "现在运行：" as result "hxempirical"
