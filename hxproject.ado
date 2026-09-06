*! hxproject 1.0.0 05sep2026
*! Internal project snapshots and model artifacts; never changes active data/results.
program define hxproject
    version 17.0
    gettoken action 0 : 0
    syntax using/
    tempname saved_r
    _return hold `saved_r'
    capture noisily _hxproject_`action' using `"`using'"'
    local rc = _rc
    _return restore `saved_r'
    if `rc' exit `rc'
end

program define _hxproject_snapshot
    version 17.0
    syntax using/
    tempname snapshot
    frame copy `c(frame)' `snapshot'
    capture frame `snapshot': quietly save `"`using'"'
    local rc = _rc
    frame drop `snapshot'
    if `rc' exit `rc'
    char _dta[hxproject_rngstate] `"`c(rngstate)'"'
    char _dta[hxproject_sortrngstate] `"`c(sortrngstate)'"'
    char _dta[hxproject_rng] `"`c(rng)'"'
    char _dta[hxproject_pwd] `"`c(pwd)'"'
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
