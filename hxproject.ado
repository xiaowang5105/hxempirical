*! hxproject 1.0.2 07sep2026
*! Project snapshots, model artifacts, and transactional data loading/restoration.
program define hxproject
    version 17.0
    gettoken action 0 : 0
    syntax using/ [, RNG(string) RNGSTATE(string) SORTRNGSTATE(string) DIRECTORY(string)]
    if !inlist("`action'", "snapshot", "model", "restore", "load") exit 198
    tempname saved_r
    _return hold `saved_r'
    local restoreopts ""
    if "`action'" == "restore" {
        local restoreopts `", rng(`rng') rngstate(`rngstate')"'
        if "`sortrngstate'" != "" local restoreopts `"`restoreopts' sortrngstate(`sortrngstate')"'
        if `"`directory'"' != "" local restoreopts `"`restoreopts' directory("`directory'")"'
    }
    capture noisily _hxproject_`action' using `"`using'"' `restoreopts'
    local rc = _rc
    _return restore `saved_r'
    if `rc' exit `rc'
end

program define _hxproject_load
    version 17.0
    syntax using/
    preserve
    capture noisily use `"`using'"', clear
    local rc = _rc
    if `rc' {
        restore
        exit `rc'
    }
    restore, not
    ereturn clear
end

program define _hxproject_singleframe
    version 17.0
    quietly frames dir
    local frames `"`r(frames)'"'
    local count : word count `frames'
    if `count' != 1 {
        display as error "项目快照当前支持单 frame；请先另存所有 frame，再关闭额外 frame。"
        exit 459
    }
end

program define _hxproject_restore
    version 17.0
    syntax using/ , RNG(string) RNGSTATE(string) [SORTRNGSTATE(string) DIRECTORY(string)]
    _hxproject_singleframe
    local oldrng `"`c(rng)'"'
    local oldstate `"`c(rngstate)'"'
    local oldsort `"`c(sortrngstate)'"'
    local oldpwd `"`c(pwd)'"'
    preserve
    capture noisily {
        set rng `rng'
        set rngstate `rngstate'
        if "`sortrngstate'" != "" set sortrngstate `sortrngstate'
        use `"`using'"', clear
        if `"`directory'"' != "" quietly cd `"`directory'"'
    }
    local rc = _rc
    if `rc' {
        restore
        quietly set rng `oldrng'
        quietly set rngstate `oldstate'
        quietly set sortrngstate `oldsort'
        quietly cd `"`oldpwd'"'
        exit `rc'
    }
    restore, not
    ereturn clear
end

program define _hxproject_snapshot
    version 17.0
    syntax using/
    _hxproject_singleframe
    tempname snapshot
    frame copy `c(frame)' `snapshot'
    capture frame `snapshot': quietly save `"`using'"'
    local rc = _rc
    frame drop `snapshot'
    if `rc' exit `rc'
    char _dta[hxproject_rngstate] `"`c(rngstate)'"'
    char _dta[hxproject_sortrngstate] `"`c(sortrngstate)'"'
    char _dta[hxproject_rng] `"`c(rng_current)'"'
    char _dta[hxproject_pwd] `"`c(pwd)'"'
    char _dta[hxproject_environment] `"Stata `c(stata_version)' | `c(os)' | `c(machine_type)'"'
end

program define _hxproject_model
    version 17.0
    syntax using/
    confirm matrix e(b)
    confirm matrix e(V)
    quietly estimates save `"`using'.ster"'
    quietly datasignature
    char _dta[hxproject_signature] `"`r(datasignature)'"'
    char _dta[hxproject_vce] `"`e(vce)'"'
    tempname b v out sampleframe
    matrix `b' = e(b)
    matrix `v' = e(V)
    local terms : colfullnames `b'
    file open `out' using `"`using'.tsv"', write text
    file write `out' "term" _tab "coefficient" _tab "se" _n
    local j = 0
    foreach term of local terms {
        local ++j
        file write `out' "`term'" _tab %24.17g (el(`b',1,`j')) _tab %24.17g (sqrt(el(`v',`j',`j'))) _n
    }
    file close `out'
    tempvar sample
    quietly generate byte `sample' = e(sample)
    frame put `sample', into(`sampleframe')
    capture frame `sampleframe': quietly export delimited using `"`using'.sample"', novarnames
    local rc = _rc
    frame drop `sampleframe'
    if `rc' exit `rc'
end
