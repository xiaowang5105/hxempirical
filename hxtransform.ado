*! hxtransform 1.0.0 - native Stata transformations behind hxselect
program define hxtransform, rclass
    version 16.0
    syntax , GENERATE(name) OPERATION(string) VAR1(name) ///
        [VAR2(name) BVALUE(string) CUTOFF(real 1) REPLACE]

    local operation = lower(trim(`"`operation'"'))
    confirm numeric variable `var1'
    if `"`var2'"' != "" confirm numeric variable `var2'

    local binary "add subtract multiply divide"
    local unary  "ln ln1p square sqrt abs zscore demean reciprocal lag lead difference growth winsor"
    if !strpos(" `binary' `unary' ", " `operation' ") {
        display as error "不支持的处理方法：`operation'"
        exit 198
    }

    if strpos(" `binary' ", " `operation' ") {
        if (`"`var2'"' == "" & `"`bvalue'"' == "") | ///
           (`"`var2'"' != "" & `"`bvalue'"' != "") {
            display as error "这个方法需要且只能选择一个 B：另一个变量或一个数字。"
            exit 198
        }
        if `"`bvalue'"' != "" {
            capture confirm number `bvalue'
            if _rc {
                display as error "B 的数字填写有误。"
                exit 198
            }
        }
    }

    if `"`generate'"' == `"`var1'"' | (`"`var2'"' != "" & `"`generate'"' == `"`var2'"') {
        display as error "新变量名不能与参与计算的原变量同名。"
        exit 198
    }
    capture confirm new variable `generate'
    if _rc & `"`replace'"' == "" {
        display as error "变量 `generate' 已存在；勾选覆盖后才能替换。"
        exit 110
    }
    if "`operation'" == "winsor" & (`cutoff' <= 0 | `cutoff' >= 50) {
        display as error "缩尾比例必须大于 0 且小于 50。"
        exit 198
    }

    if strpos(" lag lead difference growth ", " `operation' ") {
        capture quietly tsset
        if _rc | `"`r(timevar)'"' == "" {
            display as error "滞后、领先、差分和增长率需要先设置面板或时间变量（tsset/xtset）。"
            exit 459
        }
    }

    tempvar result
    local b = cond(`"`var2'"' != "", `"`var2'"', `"`bvalue'"')
    local rhs
    local qualifier

    if "`operation'" == "add"        local rhs "`var1' + `b'"
    if "`operation'" == "subtract"   local rhs "`var1' - `b'"
    if "`operation'" == "multiply"   local rhs "`var1' * `b'"
    if "`operation'" == "divide" {
        local rhs "`var1' / `b'"
        local qualifier "if `b' != 0"
    }
    if "`operation'" == "ln" {
        local rhs "ln(`var1')"
        local qualifier "if `var1' > 0"
    }
    if "`operation'" == "ln1p" {
        local rhs "ln(`var1' + 1)"
        local qualifier "if `var1' > -1"
    }
    if "`operation'" == "square"     local rhs "`var1'^2"
    if "`operation'" == "sqrt" {
        local rhs "sqrt(`var1')"
        local qualifier "if `var1' >= 0"
    }
    if "`operation'" == "abs"        local rhs "abs(`var1')"
    if "`operation'" == "zscore" {
        quietly summarize `var1'
        local mean : display %21.16g r(mean)
        local sd : display %21.16g r(sd)
        local rhs "(`var1' - `mean') / `sd'"
        local qualifier "if !missing(`var1')"
    }
    if "`operation'" == "demean" {
        quietly summarize `var1', meanonly
        local mean : display %21.16g r(mean)
        local rhs "`var1' - `mean'"
    }
    if "`operation'" == "reciprocal" {
        local rhs "1 / `var1'"
        local qualifier "if `var1' != 0"
    }
    if "`operation'" == "lag"        local rhs "L.`var1'"
    if "`operation'" == "lead"       local rhs "F.`var1'"
    if "`operation'" == "difference" local rhs "D.`var1'"
    if "`operation'" == "growth" {
        local rhs "100 * D.`var1' / L.`var1'"
        local qualifier "if L.`var1' != 0"
    }
    if "`operation'" == "winsor" {
        quietly centile `var1' if !missing(`var1'), centile(`cutoff' `=100-`cutoff'')
        local lo : display %21.16g r(c_1)
        local hi : display %21.16g r(c_2)
        local rhs "max(`lo', min(`var1', `hi'))"
        local qualifier "if !missing(`var1')"
    }

    local nativeverb "generate double"
    if `"`replace'"' != "" local nativeverb "replace"
    local nativecmd "`nativeverb' `generate' = `rhs' `qualifier'"
    local nativecmd = trim(`"`nativecmd'"')
    capture window push `nativecmd'
    quietly generate double `result' = `rhs' `qualifier'

    capture confirm variable `generate'
    if !_rc drop `generate'
    rename `result' `generate'
    label variable `generate' "由 hxselect 创建：`operation'(`var1')"

    quietly count if missing(`generate')
    local N_missing = r(N)
    return scalar N_missing = `N_missing'
    return local variable `generate'
    return local operation `operation'

    display as result "已生成新变量：`generate'"
    display as text "处理方法：`operation'；新变量缺失值：" as result `N_missing'

    quietly ds, has(type numeric)
    char _dta[hxselect_numeric_vars] `r(varlist)'

    capture hxhistory, add(`"`nativecmd'"')
end
