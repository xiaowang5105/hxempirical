*! hxinstall 1.4.0  15aug2026
*! Short public launcher for hxempirical
version 17.0
set more off

args action source
if `"`action'"' == "" local action "auto"
local core_source "https://xiaowang5105.github.io/hxempirical"
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
capture quietly copy `"`core_source'/hxinstaller.ado"' `"`target'/hxinstaller.ado"', replace
local core_rc = _rc
quietly set timeout1 `old_timeout1'
quietly set timeout2 `old_timeout2'
if `core_rc' {
    display as error "无法取得安装器核心。请检查网络或离线包后重试。"
    exit 603
}

discard
capture noisily hxinstaller `"`action'"' `"`source'"'
local install_rc = _rc
if `install_rc' display as error "hxempirical 操作未完成，Stata 返回码 r(`install_rc')。"
exit `install_rc'
