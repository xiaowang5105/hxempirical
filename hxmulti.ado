*! hxmulti 1.0.0  08aug2026
*! 多模型共同显著控制变量组合筛选器
program define hxmulti, rclass
    version 16.0

    if `"`0'"' == "" {
        display as error "这是 hxselect 的内部计算引擎。请输入 hxselect 打开统一窗口。"
        exit
    }

    #delimit ;
    syntax , CANDIDATES(varlist numeric)
        MODEL1(string asis) TARGET1(string asis)
        [ MODEL2(string asis) TARGET2(string asis)
          MODEL3(string asis) TARGET3(string asis)
          MODEL4(string asis) TARGET4(string asis)
          SIGN1(string) SIGN2(string) SIGN3(string) SIGN4(string)
          PMAX(real 0.10)
          MINCONTROLS(integer 0)
          MAXCONTROLS(integer -1)
          MAXRUNS(integer 20000)
          INCLUDEEMPTY
          SAVING(string asis)
          REPLACE
          BEST ];
    #delimit cr

    if `pmax' <= 0 | `pmax' >= 1 {
        display as error "pmax() 必须在 0 与 1 之间"
        exit 198
    }
    // string asis 会保留用户输入的外层引号；文件名在使用前统一去除一层。
    local saving = strtrim(`"`saving'"')
    if substr(`"`saving'"', 1, 1) == char(34) & ///
        substr(`"`saving'"', -1, 1) == char(34) {
        local saving = substr(`"`saving'"', 2, strlen(`"`saving'"') - 2)
    }
    if strpos(`"`model1'"', "{controls}") == 0 {
        display as error "model1() 中必须包含占位符 {controls}"
        exit 198
    }
    if `"`model2'"' == "" & (`"`model3'"' != "" | `"`model4'"' != "") {
        display as error "请连续填写模型：使用 model3() 前先填写 model2()"
        exit 198
    }
    if `"`model3'"' == "" & `"`model4'"' != "" {
        display as error "请连续填写模型：使用 model4() 前先填写 model3()"
        exit 198
    }

    local nmodels = 1
    forvalues m = 2/4 {
        if `m' == 2 {
            local spec `"`model2'"'
            local target `"`target2'"'
        }
        else if `m' == 3 {
            local spec `"`model3'"'
            local target `"`target3'"'
        }
        else {
            local spec `"`model4'"'
            local target `"`target4'"'
        }
        if `"`spec'"' != "" {
            if `"`target'"' == "" {
                display as error "model`m'() 已填写，还需要 target`m'()"
                exit 198
            }
            if strpos(`"`spec'"', "{controls}") == 0 {
                display as error "model`m'() 中必须包含占位符 {controls}"
                exit 198
            }
            local nmodels = `m'
        }
    }

    forvalues m = 1/4 {
        if `m' == 1 local sign `"`sign1'"'
        else if `m' == 2 local sign `"`sign2'"'
        else if `m' == 3 local sign `"`sign3'"'
        else local sign `"`sign4'"'
        local sign = lower(strtrim(`"`sign'"'))
        if `"`sign'"' == "" local sign "any"
        if !inlist(`"`sign'"', "any", "positive", "negative") {
            display as error "sign`m'() 只接受 any、positive 或 negative"
            exit 198
        }
        local sign`m' `"`sign'"'
    }

    local ncandidates : word count `candidates'
    if `ncandidates' > 15 {
        display as error "候选变量最多15个；当前为 `ncandidates' 个。请先按理论缩小候选池。"
        exit 198
    }
    if `maxcontrols' == -1 local maxcontrols = `ncandidates'
    if `mincontrols' < 0 | `maxcontrols' < `mincontrols' | `maxcontrols' > `ncandidates' {
        display as error "请检查 mincontrols() 和 maxcontrols() 的范围"
        exit 198
    }
    if `maxruns' < 1 {
        display as error "maxruns() 必须大于0"
        exit 198
    }
    if `"`saving'"' == "" local saving "hxmulti_results.dta"
    if `"`replace'"' == "" {
        capture confirm new file `"`saving'"'
        if _rc {
            display as error `"结果文件已存在：`saving'。请更换文件名或勾选覆盖。"'
            exit 602
        }
    }

    local firstmask = cond(`"`includeempty'"' == "", 1, 0)
    local lastmask = 2^`ncandidates' - 1
    local eligible = 0
    forvalues mask = `firstmask'/`lastmask' {
        local k = 0
        forvalues j = 1/`ncandidates' {
            if mod(floor(`mask' / 2^(`j' - 1)), 2) == 1 local ++k
        }
        if inrange(`k', `mincontrols', `maxcontrols') local ++eligible
    }
    local planned = `eligible' * `nmodels'
    if `planned' > `maxruns' {
        display as error "计划最多运行 `planned' 次回归，超过 maxruns(`maxruns')。"
        display as error "请减少候选变量、收紧控制变量数量范围或提高 maxruns()。"
        exit 198
    }

    tempfile results
    tempname posth
    postfile `posth' str2045 subset int ncontrols ///
        double b1 p1 fit1 b2 p2 fit2 b3 p3 fit3 b4 p4 fit4 ///
        using `results', replace

    display as text _newline "多模型共同显著组合筛选"
    display as text "模型数量：" as result `nmodels'
    display as text "候选控制变量：" as result `"`candidates'"'
    display as text "候选组合数：" as result `eligible'
    display as text "最多执行回归：" as result `planned'
    display as text "共同显著阈值：p < " as result %5.3f `pmax'

    local tested = 0
    local passed = 0
    forvalues mask = `firstmask'/`lastmask' {
        local combo ""
        forvalues j = 1/`ncandidates' {
            if mod(floor(`mask' / 2^(`j' - 1)), 2) == 1 {
                local candidate : word `j' of `candidates'
                local combo `"`combo' `candidate'"'
            }
        }
        local combo = strtrim(`"`combo'"')
        local ncombo : word count `combo'
        if !inrange(`ncombo', `mincontrols', `maxcontrols') continue
        local ++tested

        local allpass = 1
        forvalues z = 1/4 {
            local b`z' = .
            local p`z' = .
            local fit`z' = .
        }

        forvalues m = 1/`nmodels' {
            if `m' == 1 {
                local spec `"`model1'"'
                local target `"`target1'"'
            }
            else if `m' == 2 {
                local spec `"`model2'"'
                local target `"`target2'"'
            }
            else if `m' == 3 {
                local spec `"`model3'"'
                local target `"`target3'"'
            }
            else {
                local spec `"`model4'"'
                local target `"`target4'"'
            }
            local cmd : subinstr local spec "{controls}" `"`combo'"', all
            capture quietly `cmd'
            if _rc {
                local allpass = 0
                continue, break
            }

            capture local b`m' = _b[`target']
            if _rc {
                local allpass = 0
                continue, break
            }
            capture local sem = _se[`target']
            if _rc | missing(`sem') | `sem' <= 0 {
                local allpass = 0
                continue, break
            }
            local stat = `b`m'' / `sem'
            capture local dfr = e(df_r)
            if _rc local dfr = .
            if missing(`dfr') local p`m' = 2 * (1 - normal(abs(`stat')))
            else local p`m' = 2 * ttail(`dfr', abs(`stat'))

            capture local fit`m' = e(r2_a)
            if _rc | missing(`fit`m'') {
                capture local fit`m' = e(r2)
                if _rc | missing(`fit`m'') {
                    capture local fit`m' = e(r2_p)
                    if _rc local fit`m' = .
                }
            }

            if `p`m'' >= `pmax' local allpass = 0
            if `"`sign`m''"' == "positive" & `b`m'' <= 0 local allpass = 0
            if `"`sign`m''"' == "negative" & `b`m'' >= 0 local allpass = 0
            if !`allpass' continue, break
        }

        if `allpass' {
            local ++passed
            post `posth' (`"`combo'"') (`ncombo') ///
                (`b1') (`p1') (`fit1') (`b2') (`p2') (`fit2') ///
                (`b3') (`p3') (`fit3') (`b4') (`p4') (`fit4')
        }
    }
    postclose `posth'

    preserve
    use `results', clear
    local plist ""
    local blist ""
    forvalues m = 1/`nmodels' {
        local plist `"`plist' p`m'"'
        local blist `"`blist' b`m'"'
    }
    if _N > 0 {
        egen worst_p = rowmax(`plist')
        sort worst_p ncontrols
    }
    else gen double worst_p = .
    char _dta[candidates] `"`candidates'"'
    char _dta[pmax] `"`pmax'"'
    forvalues m = 1/`nmodels' {
        if `m' == 1 {
            char _dta[model1] `"`model1'"'
            char _dta[target1] `"`target1'"'
        }
        else if `m' == 2 {
            char _dta[model2] `"`model2'"'
            char _dta[target2] `"`target2'"'
        }
        else if `m' == 3 {
            char _dta[model3] `"`model3'"'
            char _dta[target3] `"`target3'"'
        }
        else {
            char _dta[model4] `"`model4'"'
            char _dta[target4] `"`target4'"'
        }
    }
    if `"`replace'"' != "" save `"`saving'"', replace
    else save `"`saving'"'

    display as text _newline "同时满足全部模型的组合数：" as result _N
    if _N > 0 {
        display as text "结果按最差 p 值、控制变量数量排序："
        list subset ncontrols `plist' `blist' worst_p in 1/`=min(_N,20)', ///
            noobs abbreviate(22)
        local bestsubset = subset[1]
    }
    else local bestsubset ""
    restore

    display as text "结果文件：" as result `"`saving'"'
    if `"`best'"' != "" & `"`bestsubset'"' != "" {
        display as text _newline "排名第一的共同组合：" as result `"`bestsubset'"'
        forvalues m = 1/`nmodels' {
            if `m' == 1 local spec `"`model1'"'
            else if `m' == 2 local spec `"`model2'"'
            else if `m' == 3 local spec `"`model3'"'
            else local spec `"`model4'"'
            local cmd : subinstr local spec "{controls}" `"`bestsubset'"', all
            display as text "模型 `m'：" _newline as result `"`cmd'"'
            capture window push `cmd'
            `cmd'
        }
    }

    return scalar models = `nmodels'
    return scalar tested = `tested'
    return scalar passed = `passed'
    return local bestsubset `"`bestsubset'"'
    return local saving `"`saving'"'
end
