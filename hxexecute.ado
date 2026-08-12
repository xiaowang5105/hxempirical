*! hxexecute 1.5.0  11aug2026
*! Execute one native command with monitor snapshots while preserving History.
program define hxexecute, rclass
    version 16.0
    syntax , COMMAND(string asis)

    local native = trim(`"`command'"')
    if substr(`"`native'"', 1, 2) == char(96) + char(34) & ///
        substr(`"`native'"', -2, 2) == char(34) + char(39) {
        local native = substr(`"`native'"', 3, strlen(`"`native'"') - 4)
    }
    else if substr(`"`native'"', 1, 1) == char(34) & ///
        substr(`"`native'"', -1, 1) == char(34) {
        local native = substr(`"`native'"', 2, strlen(`"`native'"') - 2)
    }
    if `"`native'"' == "" {
        display as error "当前没有可执行的 Stata 命令。"
        exit 198
    }

    quietly hxmonitor, action(snapshot)
    local semantic_command : char _dta[hxtoolbox_monitor_command]
    local semantic_command = lower(trim(`"`semantic_command'"'))
    if "`semantic_command'" == "" {
        gettoken semantic_command unused : native
        local semantic_command = lower(trim("`semantic_command'"))
    }
    local changes_data = ///
        inlist("`semantic_command'", "generate", "replace", "keep", "drop", "merge", "append", "reshape") | ///
        inlist("`semantic_command'", "collapse", "winsor2", "xtset", "encode", "decode", "destring", "tostring") | ///
        inlist("`semantic_command'", "hxdidencode")
    char _dta[hxtoolbox_native_refresh] "0"
    char _dta[hxtoolbox_last_native_command] `"`native'"'
    char _dta[hxtoolbox_history_status] "准备写入"
    capture window push `native'
    local history_rc = _rc
    if `history_rc' {
        char _dta[hxtoolbox_history_status] "写入失败"
    }
    else {
        char _dta[hxtoolbox_history_status] "已写入"
    }
    capture noisily `native'
    local rc = _rc
    /* use/clear may replace dataset characteristics; restore audit fields. */
    char _dta[hxtoolbox_last_native_command] `"`native'"'
    if `history_rc' {
        char _dta[hxtoolbox_history_status] "写入失败"
    }
    else {
        char _dta[hxtoolbox_history_status] "已写入"
    }
    capture quietly hxrefresh
    capture quietly hxmonitor, action(after)
    if !`rc' & `changes_data' char _dta[hxtoolbox_native_refresh] "1"
    if `rc' {
        display as error "命令执行失败，返回码为 `rc'。数据观察区仍已刷新，可检查 History 中的最终命令。"
    }

    return scalar rc = `rc'
    return scalar history_rc = `history_rc'
    return local command `"`native'"'
    if `rc' exit `rc'
end
