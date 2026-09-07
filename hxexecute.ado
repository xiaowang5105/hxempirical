*! hxexecute 1.6.2  07sep2026
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

    /* Monitoring must not consume results referenced by the next command. */
    tempname hx_input_results hx_native_results
    _return hold `hx_input_results'
    capture quietly hxmonitor, action(snapshot)
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
    char _dta[hxtoolbox_last_results_file] ""
    capture window push `native'
    local history_rc = _rc
    if `history_rc' {
        char _dta[hxtoolbox_history_status] "写入失败"
    }
    else {
        char _dta[hxtoolbox_history_status] "已写入"
    }
    /* Mirror the command's visible Stata Results into a text log that Java can read. */
    tempfile hx_results
    local hx_result_file `"`hx_results'.txt"'
    capture log close HXEMPIRICAL_RESULT
    capture log using `"`hx_result_file'"', text replace name(HXEMPIRICAL_RESULT)
    local hx_log_rc = _rc
    _return restore `hx_input_results'
    local rc = 0
    gettoken hx_first hx_rest : native
    if "`hx_first'" == "merge" {
        tempname hx_check_results
        _return hold `hx_check_results'
        capture noisily _hxexecute_mergecheck `hx_rest'
        local rc = _rc
        _return restore `hx_check_results'
    }
    if !`rc' {
        capture noisily `native'
        local rc = _rc
    }
    _return hold `hx_native_results'
    if !`hx_log_rc' capture log close HXEMPIRICAL_RESULT
    /* use/clear may replace dataset characteristics; restore audit fields. */
    char _dta[hxtoolbox_last_results_file] `"`hx_result_file'"'
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

    _return restore `hx_native_results'
    return add
    return scalar rc = `rc'
    return scalar history_rc = `history_rc'
    return local command `"`native'"'
    if `rc' exit `rc'
end

program define _hxexecute_mergecheck
    version 17.0
    gettoken relation 0 : 0
    syntax varlist using/ [, *]
    if !inlist("`relation'", "1:1", "1:m", "m:1") {
        display as error "工作台合并支持 1:1、1:m、m:1；请先明确键关系。"
        exit 198
    }
    tempname masterkeys usingkeys
    capture noisily {
        frame put `varlist', into(`masterkeys')
        frame create `usingkeys'
        frame `usingkeys': use `varlist' using `"`using'"', clear
        foreach key of local varlist {
            frame `masterkeys': local mt : type `key'
            frame `usingkeys': local ut : type `key'
            if (substr("`mt'",1,3)=="str") != (substr("`ut'",1,3)=="str") {
                display as error "合并键 `key' 的字符串/数值类型不一致。"
                error 106
            }
            frame `masterkeys': quietly count if missing(`key')
            if r(N) {
                display as error "主表合并键 `key' 有 " r(N) " 个缺失值。"
                error 459
            }
            frame `usingkeys': quietly count if missing(`key')
            if r(N) {
                display as error "副表合并键 `key' 有 " r(N) " 个缺失值。"
                error 459
            }
        }
        if inlist("`relation'", "1:1", "1:m") {
            frame `masterkeys': isid `varlist'
        }
        if inlist("`relation'", "1:1", "m:1") {
            frame `usingkeys': isid `varlist'
        }
        display as text "合并预检通过：键类型一致、无缺失，唯一性符合 `relation'。"
    }
    local rc = _rc
    capture frame drop `masterkeys'
    capture frame drop `usingkeys'
    if `rc' exit `rc'
end
