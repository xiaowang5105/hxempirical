*! hxoneclickrun 1.2.0  11aug2026
*! Execute the real external OneClick command in an isolated temporary directory.
program define hxoneclickrun, rclass
    version 17.0
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
    if `"`native'"' == "" exit 198

    gettoken external rest : native
    local external = lower(trim("`external'"))
    if !inlist("`external'", "oneclick", "oneclick_robustness") {
        display as error "hxoneclickrun 只接受 oneclick 或 oneclick_robustness。"
        exit 198
    }
    capture quietly which `external'
    if _rc {
        display as error "当前 Stata 尚未安装 `external'。"
        if "`external'" == "oneclick" display as text "可运行：ssc install oneclick, replace"
        exit 111
    }

    /*
       OneClick writes subset.dta to the current working directory. Run it in
       a unique temporary directory. The result frame also gets a Stata-generated
       unique name, so HX never drops or overwrites a user-owned frame by name.
    */
    local original_pwd `"`c(pwd)'"'
    tempfile hx_anchor
    local workdir `"`hx_anchor'_oneclick"'
    capture mkdir `"`workdir'"'
    local mkdir_rc = _rc
    if `mkdir_rc' {
        display as error "无法创建 OneClick 临时目录，返回码 `mkdir_rc'。"
        exit `mkdir_rc'
    }

    tempname hxframe
    local resultframe "`hxframe'"

    char _dta[hxtoolbox_last_native_command] `"`native'"'
    char _dta[hxtoolbox_history_status] "准备写入"
    char _dta[hxtoolbox_oneclick_frame] ""
    char _dta[hxtoolbox_oneclick_result] ""

    capture window push `native'
    local history_rc = _rc
    if `history_rc' char _dta[hxtoolbox_history_status] "写入失败"
    else char _dta[hxtoolbox_history_status] "已写入"

    capture cd `"`workdir'"'
    local cd_rc = _rc
    if `cd_rc' {
        capture rmdir `"`workdir'"'
        display as error "无法进入 OneClick 临时目录，返回码 `cd_rc'。"
        exit `cd_rc'
    }

    capture noisily `native'
    local rc = _rc

    local result_loaded 0
    local result_rc 0
    capture confirm file "subset.dta"
    if !_rc {
        capture frame create `resultframe'
        if !_rc {
            capture frame `resultframe': use "subset.dta", clear
            local result_rc = _rc
            if !`result_rc' {
                local result_loaded 1
                frame `resultframe': char _dta[hxempirical_owned_frame] "oneclick_result"
            }
            else capture frame drop `resultframe'
        }
        else local result_rc = _rc
    }

    capture erase "subset.dta"
    capture cd `"`original_pwd'"'
    local restore_pwd_rc = _rc
    capture rmdir `"`workdir'"'
    local cleanup_rc = _rc

    /* External commands may write output; restore HX audit fields afterwards. */
    char _dta[hxtoolbox_last_native_command] `"`native'"'
    if `history_rc' char _dta[hxtoolbox_history_status] "写入失败"
    else char _dta[hxtoolbox_history_status] "已写入"
    if `result_loaded' {
        char _dta[hxtoolbox_oneclick_frame] "`resultframe'"
        char _dta[hxtoolbox_oneclick_result] "已从隔离临时目录读取外部 subset.dta；用户当前数据、工作目录文件和已有 frame 均未改变"
    }
    else if `result_rc' char _dta[hxtoolbox_oneclick_result] "外部命令结束，但 subset.dta 读取失败"
    else char _dta[hxtoolbox_oneclick_result] "外部命令未生成 subset.dta"

    if `restore_pwd_rc' {
        display as error "警告：OneClick 已结束，但恢复原工作目录失败（返回码 `restore_pwd_rc'）。"
    }
    if `cleanup_rc' {
        display as text "提示：临时目录未完全删除；其中不会包含用户原始文件。"
    }

    return scalar rc = `rc'
    return scalar history_rc = `history_rc'
    return scalar result_loaded = `result_loaded'
    return scalar result_rc = `result_rc'
    return scalar restore_pwd_rc = `restore_pwd_rc'
    return scalar cleanup_rc = `cleanup_rc'
    return local command `"`native'"'
    return local frame "`resultframe'"
    return local original_pwd `"`original_pwd'"'

    if `rc' exit `rc'
end
