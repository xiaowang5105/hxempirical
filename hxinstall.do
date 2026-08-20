*! hxinstall 1.5.12  20aug2026
*! Short public launcher for hxempirical
version 17.0
set more off

args action source
if `"`action'"' == "" local action "auto"
local pages_source "https://xiaowang5105.github.io/hxempirical"
local raw_source   "https://raw.githubusercontent.com/xiaowang5105/hxempirical/main"
local core_source `"`pages_source'"'
if `"`source'"' != "" local core_source `"`source'"'
local target `"`c(sysdir_personal)'"'
if `"`target'"' == "" {
    display as error "Stata 没有返回 PERSONAL ado 目录。请运行 sysdir 检查安装环境。"
    exit 603
}
capture quietly mkdir `"`target'"'

display as text _newline "hxempirical 安装管理"
display as text "正在启动安装器……"
local old_timeout1 = c(timeout1)
local old_timeout2 = c(timeout2)
quietly set timeout1 10
quietly set timeout2 20
tempfile bootstrap_installer
capture quietly copy `"`core_source'/hxinstaller.ado"' `"`bootstrap_installer'"', replace
local core_rc = _rc
if `core_rc' & `"`source'"' == "" {
    local core_source `"`raw_source'"'
    capture quietly copy `"`core_source'/hxinstaller.ado"' `"`bootstrap_installer'"', replace
    local core_rc = _rc
}
quietly set timeout1 `old_timeout1'
quietly set timeout2 `old_timeout2'
if `core_rc' {
    display as error "无法取得安装器核心。请检查网络或离线包后重试。"
    exit 603
}

/* Load the installer from the exact temporary file just downloaded.  This
   avoids current-directory shadowing and leaves an existing PERSONAL install
   unchanged until the installer's transaction commits. */
discard
capture program drop hxinstaller
capture quietly run `"`bootstrap_installer'"'
local loader_rc = _rc
if `loader_rc' {
    display as error "无法载入刚刚下载的安装器核心。"
    exit `loader_rc'
}
capture noisily hxinstaller `"`action'"' `"`source'"'
local install_rc = _rc
if `install_rc' display as error "hxempirical 操作未完成，Stata 返回码 r(`install_rc')。"
exit `install_rc'
