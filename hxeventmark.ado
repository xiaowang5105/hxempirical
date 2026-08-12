*! hxeventmark 1.0.0  11aug2026
*! Mark the currently active event-study estimation result for later pretrend testing.
program define hxeventmark, rclass
    version 17.0
    syntax , TREAT(name) EVENTCODE(name)

    capture confirm matrix e(b)
    if _rc {
        display as error "当前没有可标记的估计结果 e(b)。"
        exit 301
    }
    local cmdline `"`e(cmdline)'"'
    if `"`cmdline'"' == "" local cmdline `"`e(cmd)'"'
    local cols : colfullnames e(b)

    char _dta[hxtoolbox_event_estimation_cmdline] `"`cmdline'"'
    char _dta[hxtoolbox_event_estimation_colnames] `"`cols'"'
    char _dta[hxtoolbox_event_estimation_treat] "`treat'"
    char _dta[hxtoolbox_event_estimation_code] "`eventcode'"
    char _dta[hxtoolbox_pretrend_command] ""
    char _dta[hxtoolbox_pretrend_message] "事件研究结果已记录；政策前联合检验将读取当前真实 e(b) 与 e(sample)。"

    return local cmdline `"`cmdline'"'
    return local treat "`treat'"
    return local eventcode "`eventcode'"
end
