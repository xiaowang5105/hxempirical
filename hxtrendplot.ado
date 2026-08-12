*! hxtrendplot 1.0.0  10aug2026
*! Plot group means over time while preserving the current dataset.
program define hxtrendplot, rclass
    version 16.0
    syntax varname(numeric) [if] [in], GROUP(varname) TIME(varname) ///
        [POLICY(real) OPTIONS(string asis)]

    marksample touse
    preserve
    quietly keep if `touse'
    quietly collapse (mean) `varlist', by(`time' `group')
    local graphcmd `"twoway connected `varlist' `time', by(`group', note("")) sort"'
    if "`policy'" != "" local graphcmd `"`graphcmd' xline(`policy', lpattern(dash))"'
    if `"`options'"' != "" local graphcmd `"`graphcmd' `options'"'
    capture window push `graphcmd'
    capture noisily `graphcmd'
    local rc = _rc
    restore
    return local graph_command `"`graphcmd'"'
    if `rc' exit `rc'
end
