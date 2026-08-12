*! hxregpost 1.1.0  11aug2026
*! Guarded postestimation runner for the ordinary regress workspace.
program define hxregpost, rclass
    version 16.0
    syntax [, COMMAND(string asis) STATUS]

    if lower("`e(cmd)'") != "regress" {
        display as error "当前活动估计结果不是 regress。请先重新运行普通线性回归，再使用这一诊断。"
        exit 301
    }

    local vce = lower(trim("`e(vce)'"))
    if "`vce'" == "" local vce "ols"
    tempname hxcons
    capture scalar `hxcons' = _b[_cons]
    local hascons = (_rc == 0)
    char _dta[hxtoolbox_regress_vce] "`vce'"
    char _dta[hxtoolbox_regress_hascons] "`hascons'"

    if "`status'" != "" {
        return local vce "`vce'"
        return scalar hascons = `hascons'
        exit
    }

    local native = trim(`"`command'"')
    if `"`native'"' == "" {
        display as error "没有提供要执行的 regress 后估计命令。"
        exit 198
    }

    local lower = lower(`"`native'"')
    local olsonly = regexm(`"`lower'"', "(^|[, ]+)(rstandard|rstudent|cooksd|hat|leverage)([ ,]|$)")
    if `olsonly' & "`vce'" != "ols" {
        display as error "当前 regress 使用 vce(`vce')。Stata 不提供 rstandard、rstudent、Cook's D 或 leverage 等 OLS 影响诊断。"
        display as text  "如需这些诊断，请另外运行一条使用默认 OLS VCE 的诊断回归；不要为了诊断而改写正式推断设定。"
        exit 198
    }

    hxexecute, command(`"`native'"')
    return scalar rc = r(rc)
    return local command `"`native'"'
end
