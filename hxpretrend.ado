*! hxpretrend 1.0.0  11aug2026
*! Build a testparm command from the actual active event-study e(b) and e(sample).
program define hxpretrend, rclass
    version 17.0
    syntax , TREAT(name) EVENTCODE(name)

    char _dta[hxtoolbox_pretrend_command] ""
    char _dta[hxtoolbox_pretrend_message] ""

    capture confirm matrix e(b)
    if _rc {
        char _dta[hxtoolbox_pretrend_message] "当前没有估计结果。请先运行事件研究回归。"
        exit 301
    }

    local marked_treat : char _dta[hxtoolbox_event_estimation_treat]
    local marked_code  : char _dta[hxtoolbox_event_estimation_code]
    local marked_cmd   : char _dta[hxtoolbox_event_estimation_cmdline]
    local marked_cols  : char _dta[hxtoolbox_event_estimation_colnames]
    if `"`marked_treat'"' == "" | `"`marked_code'"' == "" | `"`marked_cmd'"' == "" {
        char _dta[hxtoolbox_pretrend_message] "没有找到由工作台记录的事件研究结果。请先运行事件研究回归。"
        exit 301
    }
    if "`treat'" != "`marked_treat'" | "`eventcode'" != "`marked_code'" {
        char _dta[hxtoolbox_pretrend_message] "当前 treat / event_code 与上一条事件研究回归不一致。请重新运行事件研究回归。"
        exit 459
    }

    local current_cmd `"`e(cmdline)'"'
    if `"`current_cmd'"' == "" local current_cmd `"`e(cmd)'"'
    local current_cols : colfullnames e(b)
    if `"`current_cmd'"' != `"`marked_cmd'"' | `"`current_cols'"' != `"`marked_cols'"' {
        char _dta[hxtoolbox_pretrend_message] "最后一条估计结果已经变化。为避免检验错模型，请重新运行事件研究回归后再做政策前联合检验。"
        exit 459
    }

    local source : char _dta[hxtoolbox_event_source]
    local shift_text : char _dta[hxtoolbox_event_shift]
    local base_text : char _dta[hxtoolbox_event_base_relative]
    if `"`source'"' == "" | `"`shift_text'"' == "" | `"`base_text'"' == "" {
        char _dta[hxtoolbox_pretrend_message] "event_code 缺少来源、平移量或基准期记录。请重新生成 event_code。"
        exit 459
    }
    capture confirm numeric variable `source'
    if _rc {
        char _dta[hxtoolbox_pretrend_message] "原始 event_time 变量已不存在或不是数值型。请重新生成 event_time 和 event_code。"
        exit 111
    }

    local shift = real("`shift_text'")
    local base = real("`base_text'")
    quietly levelsof `source' if e(sample) & `source' < 0 & `source' != `base', local(periods)
    if `"`periods'"' == "" {
        char _dta[hxtoolbox_pretrend_message] "上一条事件研究的真实 e(sample) 中没有可检验的政策前非基准期。"
        exit 459
    }

    tempname omit
    capture quietly _ms_omit_info e(b)
    if !_rc matrix `omit' = r(omit)
    else matrix `omit' = J(1, colsof(e(b)), 0)
    local colnames : colnames e(b)
    local terms ""
    foreach rel of local periods {
        local code = `rel' + `shift'
        local target1 "1.`treat'#`code'.`eventcode'"
        local target2 "`code'.`eventcode'#1.`treat'"
        local j = 0
        foreach cname of local colnames {
            local ++j
            if `"`cname'"' == `"`target1'"' | `"`cname'"' == `"`target2'"' {
                local hxomit = el(`omit', 1, `j')
                if `hxomit' == 0 {
                    local terms `"`terms' `cname'"'
                }
            }
        }
    }
    local terms = trim(`"`terms'"')
    if `"`terms'"' == "" {
        char _dta[hxtoolbox_pretrend_message] "政策前时期在真实 e(b) 中均不存在或已被 Stata 省略，无法生成联合检验。"
        exit 459
    }

    local command `"testparm `terms'"'
    char _dta[hxtoolbox_pretrend_command] `"`command'"'
    char _dta[hxtoolbox_pretrend_message] "已根据上一条事件研究的真实 e(b) 与 e(sample) 生成政策前联合检验。"
    return local command `"`command'"'
    return local terms `"`terms'"'
end
