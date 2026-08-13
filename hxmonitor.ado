*! hxmonitor 1.1.1  13aug2026
*! Live data monitor and before/after summaries for the empirical toolbox.
program define hxmonitor, rclass
    version 16.0
    #delimit ;
    syntax [, ACTION(string) COMMAND(string) MONITORVAR(string)
        DEPVAR(string) VARS(string asis) IFCOND(string asis)
        NEWVAR(string) EXPRESSION(string asis) USINGFILE(string asis)
        MODEL(string asis) PANEL(string) TIME(string)
        CONDVAR(string) CONDOP(string) CONDVALUE(string) CONDITION];
    #delimit cr

    local action = lower(trim(`"`action'"'))
    if "`action'" == "" local action "refresh"
    foreach item in command monitorvar depvar vars ifcond newvar expression ///
        usingfile model panel time condvar condop condvalue {
        local `item' = trim(`"``item''"')
        if substr(`"``item''"', 1, 1) == char(34) & ///
            substr(`"``item''"', -1, 1) == char(34) {
            local `item' = substr(`"``item''"', 2, strlen(`"``item''"') - 2)
        }
    }

    if "`action'" == "after" {
        local command `"$HXMON_command"'
        local monitorvar `"$HXMON_monitorvar"'
        local depvar `"$HXMON_depvar"'
        local vars `"$HXMON_vars"'
        local ifcond `"$HXMON_ifcond"'
        local newvar `"$HXMON_newvar"'
        local expression `"$HXMON_expression"'
        local usingfile `"$HXMON_usingfile"'
        local model `"$HXMON_model"'
        local panel `"$HXMON_panel"'
        local time `"$HXMON_time"'
    }
    else {
        if "`action'" != "refresh" {
            if "`command'" == "" local command : char _dta[hxtoolbox_monitor_command]
            if "`monitorvar'" == "" local monitorvar : char _dta[hxtoolbox_monitor_var]
            if "`depvar'" == "" local depvar : char _dta[hxtoolbox_monitor_depvar]
            if "`vars'" == "" local vars : char _dta[hxtoolbox_monitor_vars]
            if "`ifcond'" == "" local ifcond : char _dta[hxtoolbox_monitor_ifcond]
            if "`newvar'" == "" local newvar : char _dta[hxtoolbox_monitor_newvar]
            if "`expression'" == "" local expression : char _dta[hxtoolbox_monitor_expression]
            if "`usingfile'" == "" local usingfile : char _dta[hxtoolbox_monitor_using]
            if "`model'" == "" local model : char _dta[hxtoolbox_monitor_model]
            if "`panel'" == "" local panel : char _dta[hxtoolbox_monitor_panel]
            if "`time'" == "" local time : char _dta[hxtoolbox_monitor_time]
        }
        else {
            if "`command'" == "" local command : char _dta[hxtoolbox_resolve_name]
            if "`vars'" == "" local vars : char _dta[hxtoolbox_pick_vars]
            if "`monitorvar'" == "" local monitorvar : char _dta[hxtoolbox_monitor_var]
        }
    }
    local command = lower(trim(`"`command'"'))

    if "`condition'" != "" & `"`condvar'`condop'`condvalue'"' != "" {
        local ifcond `"`condvar' `condop' `condvalue'"'
    }

    if "`action'" == "snapshot" {
        global HXMON_command `"`command'"'
        global HXMON_monitorvar `"`monitorvar'"'
        global HXMON_depvar `"`depvar'"'
        global HXMON_vars `"`vars'"'
        global HXMON_ifcond `"`ifcond'"'
        global HXMON_newvar `"`newvar'"'
        global HXMON_expression `"`expression'"'
        global HXMON_usingfile `"`usingfile'"'
        global HXMON_model `"`model'"'
        global HXMON_panel `"`panel'"'
        global HXMON_time `"`time'"'
        global HXMON_before_N = _N
        global HXMON_before_K = c(k)
        capture unab hx_before_vars : _all
        global HXMON_before_vars `"`hx_before_vars'"'

        local target "`monitorvar'"
        if inlist("`command'", "replace", "generate") {
            if "`command'" == "replace" local target "`depvar'"
            else local target "`newvar'"
        }
        global HXMON_before_target "`target'"
        global HXMON_before_mean ""
        global HXMON_before_min ""
        global HXMON_before_max ""
        global HXMON_before_missing ""
        global HXMON_before_affected ""
        if "`command'" == "replace" & "`depvar'" != "" & `"`expression'"' != "" {
            tempvar hx_snapshot_use hx_snapshot_new
            quietly generate byte `hx_snapshot_use' = 1
            if `"`ifcond'"' != "" capture quietly replace `hx_snapshot_use' = 0 if !(`ifcond')
            capture confirm numeric variable `depvar'
            if !_rc {
                capture quietly generate double `hx_snapshot_new' = `expression' if `hx_snapshot_use'
            }
            else {
                capture quietly generate strL `hx_snapshot_new' = `expression' if `hx_snapshot_use'
            }
            if !_rc {
                quietly count if `hx_snapshot_use' & ///
                    ((missing(`depvar') != missing(`hx_snapshot_new')) | ///
                    (!missing(`depvar') & !missing(`hx_snapshot_new') & `depvar' != `hx_snapshot_new'))
                global HXMON_before_affected = r(N)
            }
        }
        capture confirm numeric variable `target'
        if !_rc {
            quietly summarize `target', meanonly
            global HXMON_before_mean = r(mean)
            global HXMON_before_min = r(min)
            global HXMON_before_max = r(max)
            quietly count if missing(`target')
            global HXMON_before_missing = r(N)
        }
        exit
    }

    local after_message "尚未执行操作；运行后这里显示前后变化。"
    if "`action'" == "after" {
        local dN = _N - real("$HXMON_before_N")
        local dK = c(k) - real("$HXMON_before_K")
        local signN = cond(`dN' > 0, "+", "")
        local signK = cond(`dK' > 0, "+", "")
        local after_message "执行后：观测数 `=real("$HXMON_before_N")' → `=_N'（`signN'`dN'），变量数 `=real("$HXMON_before_K")' → `=c(k)'（`signK'`dK'）。"
        capture unab hx_after_vars : _all
        local hx_before_vars `"$HXMON_before_vars"'
        local hx_added : list hx_after_vars - hx_before_vars
        local hx_removed : list hx_before_vars - hx_after_vars
        if "`hx_added'" != "" local after_message `"`after_message' 新增变量：`hx_added'。"'
        if "`hx_removed'" != "" local after_message `"`after_message' 删除变量：`hx_removed'。"'
        local target "$HXMON_before_target"
        if "`command'" == "generate" local target "`newvar'"
        capture confirm numeric variable `target'
        if !_rc {
            quietly summarize `target', meanonly
            local amean : display %10.4g r(mean)
            local amin : display %10.4g r(min)
            local amax : display %10.4g r(max)
            if "$HXMON_before_mean" != "" {
                local bmean : display %10.4g real("$HXMON_before_mean")
                local after_message `"`after_message' `target'：均值 `bmean' → `amean'，范围 [`amin', `amax']。"'
            }
            else {
                local after_message `"`after_message' 新变量 `target'：均值 `amean'，范围 [`amin', `amax']。"'
            }
        }
        if "$HXMON_before_affected" != "" {
            local affected_after "$HXMON_before_affected"
            local after_message `"`after_message' 实际修改观测：`affected_after'。"'
        }
        if "`command'" == "merge" {
            capture confirm variable _merge
            if !_rc {
                quietly count if _merge == 1
                local merge_master = r(N)
                quietly count if _merge == 2
                local merge_using = r(N)
                quietly count if _merge == 3
                local merge_matched = r(N)
                local after_message `"合并结果：匹配 `merge_matched'，仅主表 `merge_master'，仅副表 `merge_using'。 `after_message'"'
            }
        }
        if inlist("`command'", "regress", "areg", "reghdfe", "qreg", "xtreg", "xtlogit", "xtprobit") | ///
            inlist("`command'", "logit", "probit", "poisson", "nbreg", "ppmlhdfe", "ivregress", "ivreghdfe") {
            capture local eN = e(N)
            if !_rc local after_message `"模型结果：N=`eN'。"'
            capture local er2 = e(r2)
            if !_rc {
                local er2_text : display %8.4f `er2'
                local after_message `"`after_message' R²=`er2_text'。"'
            }
            capture local er2w = e(r2_w)
            if !_rc & "`command'" == "xtreg" {
                local er2w_text : display %8.4f `er2w'
                local after_message `"`after_message' 组内 R²=`er2w_text'。"'
            }
        }
    }

    if _N == 0 | c(k) == 0 {
        char _dta[hxtoolbox_monitor_data] "当前数据为空：0 行 × 0 列"
        char _dta[hxtoolbox_monitor_var] ""
        char _dta[hxtoolbox_monitor_stats1] "请先载入数据或使用左侧测试数据。"
        char _dta[hxtoolbox_monitor_stats2] ""
        char _dta[hxtoolbox_monitor_sample] "当前没有可分析的观测。"
        char _dta[hxtoolbox_monitor_operation] "操作摘要：请选择命令并载入数据。"
        char _dta[hxtoolbox_monitor_risk] "提醒：数据为空时无法预览变量和图形。"
        char _dta[hxtoolbox_monitor_rows] "没有数据"
        char _dta[hxtoolbox_monitor_change] `"`after_message'"'
        exit
    }

    local datasetN = _N
    local datasetK = c(k)

    if "`action'" == "after" {
        if "`command'" == "generate" {
            capture confirm variable `newvar'
            if !_rc local monitorvar "`newvar'"
        }
        else if "`command'" == "replace" {
            capture confirm variable `depvar'
            if !_rc local monitorvar "`depvar'"
        }
        else if "`command'" == "merge" {
            capture confirm variable _merge
            if !_rc local monitorvar "_merge"
        }
        else if "`command'" == "winsor2" {
            local winvar : word 1 of `vars'
            capture confirm variable `winvar'
            if !_rc local monitorvar "`winvar'"
        }
    }

    unab allvars : _all
    local validvars ""
    foreach v of local vars {
        capture confirm variable `v'
        if !_rc local validvars "`validvars' `v'"
    }
    local vars = trim(itrim("`validvars'"))

    capture confirm variable `monitorvar'
    if _rc local monitorvar ""
    if "`monitorvar'" == "" {
        capture confirm variable `depvar'
        if !_rc local monitorvar "`depvar'"
    }
    if "`monitorvar'" == "" {
        local monitorvar : word 1 of `vars'
    }
    if "`monitorvar'" == "" {
        local monitorvar : word 1 of `allvars'
    }

    char _dta[hxtoolbox_monitor_var] "`monitorvar'"
    local filename `"`c(filename)'"'
    if `"`filename'"' == "" local filename "内存数据"
    char _dta[hxtoolbox_monitor_data] `"当前数据：`filename'  |  `datasetN' 行 × `datasetK' 列"'

    tempvar touse
    quietly generate byte `touse' = 1
    local ifvalid 1
    if `"`ifcond'"' != "" {
        capture quietly replace `touse' = 0 if !(`ifcond')
        if _rc {
            local ifvalid 0
            quietly replace `touse' = 1
        }
    }
    local samplevars "`depvar' `vars'"
    if inlist("`command'", "generate", "replace", "keep", "drop", "merge", "append", "reshape") | ///
        inlist("`command'", "collapse", "xtset", "encode", "decode", "destring", "tostring", "winsor2") {
        local samplevars ""
    }
    local samplevars : list uniq samplevars
    local checkedvars ""
    foreach v of local samplevars {
        capture confirm variable `v'
        if !_rc local checkedvars "`checkedvars' `v'"
    }
    if "`checkedvars'" != "" quietly markout `touse' `checkedvars', strok
    quietly count if `touse'
    local sampleN = r(N)
    local excluded = _N - `sampleN'
    if `ifvalid' {
        char _dta[hxtoolbox_monitor_sample] `"预计有效样本：`sampleN'；排除：`excluded'（条件和所选变量缺失共同计算）。"'
    }
    else {
        char _dta[hxtoolbox_monitor_sample] "样本条件尚未完整，暂按全部观测预览。"
    }

    local vlabel : variable label `monitorvar'
    if `"`vlabel'"' == "" local vlabel "无变量标签"
    local vtype : type `monitorvar'
    quietly count if `touse' & missing(`monitorvar')
    local nmiss = r(N)
    quietly count if `touse' & !missing(`monitorvar')
    local nnonmiss = r(N)
    char _dta[hxtoolbox_monitor_stats1] `"变量：`monitorvar'  |  标签：`vlabel'  |  类型：`vtype'"'
    capture confirm numeric variable `monitorvar'
    if !_rc {
        quietly summarize `monitorvar' if `touse'
        if r(N) {
            local mean : display %10.4g r(mean)
            local sd : display %10.4g r(sd)
            local min : display %10.4g r(min)
            local max : display %10.4g r(max)
            char _dta[hxtoolbox_monitor_stats2] `"非缺失 `nnonmiss'，缺失 `nmiss'；均值 `mean'，SD `sd'，范围 [`min', `max']"'
        }
        else char _dta[hxtoolbox_monitor_stats2] `"非缺失 0，缺失 `nmiss'；当前样本无法计算数值统计。"'
    }
    else {
        char _dta[hxtoolbox_monitor_stats2] `"字符串变量；非缺失 `nnonmiss'，缺失 `nmiss'。可点击“统计”查看类别分布。"'
    }

    local showvars "`monitorvar' `depvar' `vars'"
    local showvars : list uniq showvars
    local limited ""
    local j 0
    foreach v of local showvars {
        capture confirm variable `v'
        if !_rc & `j' < 4 {
            local limited "`limited' `v'"
            local ++j
        }
    }
    if "`limited'" == "" {
        foreach v of local allvars {
            if `j' < 4 {
                local limited "`limited' `v'"
                local ++j
            }
        }
    }
    local limited = trim("`limited'")
    local header : subinstr local limited " " " | ", all
    local newline = char(13) + char(10)
    local rowtext `"`header'`newline'"'
    local shown 0
    forvalues i = 1/`=_N' {
        if `touse'[`i'] {
            local row ""
            foreach v of local limited {
                capture confirm numeric variable `v'
                if !_rc {
                    local cell : display %10.4g `v'[`i']
                }
                else {
                    local cell = `v'[`i']
                    local cell = substr(`"`cell'"', 1, 14)
                }
                local cell = trim(`"`cell'"')
                if "`row'" == "" local row `"`cell'"'
                else local row `"`row' | `cell'"'
            }
            local rowtext `"`rowtext'`row'`newline'"'
            local ++shown
            if `shown' >= 8 continue, break
        }
    }
    if `shown' == 0 local rowtext "没有符合当前条件的观测"
    char _dta[hxtoolbox_monitor_rows] `"`rowtext'"'

    local operation "操作摘要：请选择具体命令后，这里说明将影响的数据。"
    local risk "提醒：运行前检查命令预览和当前样本。"
    if "`command'" == "generate" {
        local operation `"操作摘要：将新增变量 `newvar'；预计计算 `sampleN' 个观测。"'
        local risk "提醒：新变量不会覆盖原变量；请检查公式中的零值、负值和缺失值。"
        if "`newvar'" != "" & `"`expression'"' != "" {
            tempvar hx_generate_preview
            capture quietly generate double `hx_generate_preview' = `expression' if `touse'
            if _rc capture quietly generate strL `hx_generate_preview' = `expression' if `touse'
            if !_rc {
                quietly count if `touse' & !missing(`hx_generate_preview')
                local generated = r(N)
                local operation `"操作摘要：将新增变量 `newvar'；当前条件下可计算 `generated' 个非缺失值。"'
                local rowtext `"观测 | `newvar'（执行前预览）`newline'"'
                local shown 0
                forvalues i = 1/`=_N' {
                    if `touse'[`i'] {
                        capture confirm numeric variable `hx_generate_preview'
                        if !_rc local newcell : display %10.4g `hx_generate_preview'[`i']
                        else {
                            local newcell = `hx_generate_preview'[`i']
                            local newcell = substr(`"`newcell'"', 1, 24)
                        }
                        local rowtext `"`rowtext'`i' | `newcell'`newline'"'
                        local ++shown
                        if `shown' >= 8 continue, break
                    }
                }
                char _dta[hxtoolbox_monitor_rows] `"`rowtext'"'
            }
        }
    }
    else if "`command'" == "replace" {
        local operation `"操作摘要：将修改原变量 `depvar'；预计影响 `sampleN' 个观测。"'
        local risk "提醒：会覆盖原值。建议先 generate 新变量或保存数据副本。"
        capture confirm variable `depvar'
        if !_rc & `"`expression'"' != "" {
            tempvar hx_replace_preview hx_changed
            capture confirm numeric variable `depvar'
            local dep_is_numeric = !_rc
            if `dep_is_numeric' capture quietly generate double `hx_replace_preview' = `expression' if `touse'
            else capture quietly generate strL `hx_replace_preview' = `expression' if `touse'
            if !_rc {
                quietly generate byte `hx_changed' = `touse' & ///
                    ((missing(`depvar') != missing(`hx_replace_preview')) | ///
                    (!missing(`depvar') & !missing(`hx_replace_preview') & `depvar' != `hx_replace_preview'))
                quietly count if `hx_changed'
                local affected = r(N)
                local unaffected = _N - `affected'
                local operation `"操作摘要：将修改 `depvar'；真正改变 `affected' 个观测，未改变 `unaffected' 个。"'
                local rowtext `"观测 | 原值 → 新值`newline'"'
                local shown 0
                forvalues i = 1/`=_N' {
                    if `hx_changed'[`i'] {
                        if `dep_is_numeric' {
                            local oldcell : display %10.4g `depvar'[`i']
                            local newcell : display %10.4g `hx_replace_preview'[`i']
                        }
                        else {
                            local oldcell = `depvar'[`i']
                            local oldcell = substr(`"`oldcell'"', 1, 14)
                            local newcell = `hx_replace_preview'[`i']
                            local newcell = substr(`"`newcell'"', 1, 14)
                        }
                        local rowtext `"`rowtext'`i' | `oldcell' → `newcell'`newline'"'
                        local ++shown
                        if `shown' >= 8 continue, break
                    }
                }
                if `affected' == 0 local rowtext "当前设置不会改变任何观测"
                char _dta[hxtoolbox_monitor_rows] `"`rowtext'"'
            }
            else local risk "检查结果：当前表达式尚未完成或与目标变量类型不兼容。"
        }
    }
    else if inlist("`command'", "keep", "drop") {
        if "`model'" == "处理变量" {
            local operation `"操作摘要：`command' 变量 `vars'；当前共有 `datasetK' 个变量。"'
        }
        else {
            local kept = cond("`command'" == "keep", `sampleN', _N - `sampleN')
            local operation `"操作摘要：`command' 样本；执行后预计保留 `kept' / `_N' 个观测。"'
        }
        local risk "提醒：keep/drop 会移除数据内容，建议先 preserve 或保存副本。"
    }
    else if "`command'" == "merge" {
        local operation `"操作摘要：按 `model' 使用键 `vars' 合并副表 `usingfile'。"'
        local risk "提醒：先检查主表和副表键的唯一性；执行后查看 _merge 分布。"
        if `"`usingfile'"' != "" & "`vars'" != "" & "`model'" != "" {
            capture quietly describe using `"`usingfile'"', short
            if !_rc {
                local usingN = r(N)
                local usingK = r(k)
                local master_unique "否"
                capture quietly isid `vars'
                if !_rc local master_unique "是"
                local using_unique "无法检查"
                preserve
                capture quietly use `"`usingfile'"', clear
                if !_rc {
                    capture quietly isid `vars'
                    if _rc local using_unique "否"
                    else local using_unique "是"
                }
                restore

                tempvar hx_merge_flag
                preserve
                capture quietly merge `model' `vars' using `"`usingfile'"', generate(`hx_merge_flag')
                local merge_rc = _rc
                if !`merge_rc' {
                    quietly count if `hx_merge_flag' == 1
                    local only_master = r(N)
                    quietly count if `hx_merge_flag' == 2
                    local only_using = r(N)
                    quietly count if `hx_merge_flag' == 3
                    local matched = r(N)
                }
                restore
                if !`merge_rc' {
                    local operation `"预计合并：主表 `datasetN' 行，副表 `usingN' 行；匹配 `matched'，仅主表 `only_master'，仅副表 `only_using'。"'
                    local risk `"键唯一性：主表 `master_unique'，副表 `using_unique'；执行后仍应检查 _merge。"'
                }
                else {
                    local operation `"操作摘要：主表 `datasetN' 行，副表 `usingN' 行 × `usingK' 列；模拟合并未通过。"'
                    local risk `"键唯一性：主表 `master_unique'，副表 `using_unique'。请检查合并类型、键和重名变量。"'
                }
            }
        }
    }
    else if "`command'" == "append" {
        local operation `"操作摘要：把 `usingfile' 追加到当前 `_N' 行数据下方。"'
        local risk "提醒：同名变量的类型、单位和编码必须一致。"
        if `"`usingfile'"' != "" {
            capture quietly describe using `"`usingfile'"', short
            if !_rc local operation `"`operation' 预计执行后 `=_N+r(N)' 行。"'
        }
    }
    else if "`command'" == "winsor2" {
        local operation `"操作摘要：对 `vars' 按 `expression' 分位点缩尾，方式：`model'。"'
        local risk "提醒：缩尾阈值具有主观性，应保留阈值并报告敏感性检验。"
        local winvar : word 1 of `vars'
        local cutlow : word 1 of `expression'
        local cuthigh : word 2 of `expression'
        if "`cutlow'" == "" local cutlow 1
        if "`cuthigh'" == "" local cuthigh 99
        capture confirm numeric variable `winvar'
        if !_rc {
            capture quietly centile `winvar', centile(`cutlow' `cuthigh')
            if !_rc {
                local low = r(c_1)
                local high = r(c_2)
                quietly count if !missing(`winvar') & (`winvar' < `low' | `winvar' > `high')
                local affected = r(N)
                local lowtext : display %10.4g `low'
                local hightext : display %10.4g `high'
                local operation `"缩尾预判：`winvar' 的阈值约为 [`lowtext', `hightext']；预计影响 `affected' 个观测。"'
            }
        }
    }
    else if "`command'" == "reshape" {
        local operation `"操作摘要：按 i=`panel'、j=`time' 执行 `model'；变量根为 `expression'。"'
        local risk "提醒：i 与 j 的组合、变量根命名必须符合宽长转换要求。"
    }
    else if "`command'" == "collapse" {
        local operation `"操作摘要：按 `panel' 分组，对 `vars' 计算 `model'；当前 `datasetN' 行将汇总成更少的行。"'
        local risk "提醒：collapse 会用汇总结果替换内存数据，建议先保存或 preserve。"
    }
    else if inlist("`command'", "encode", "decode", "destring", "tostring") {
        local operation `"操作摘要：转换变量 `depvar'；方式：`model'；新变量名：`newvar'。"'
        local risk "提醒：转换后检查缺失值、值标签和无法解析的字符串。"
    }
    else if "`command'" == "xtset" {
        local operation `"操作摘要：把 `panel' 设为个体、`time' 设为时间。"'
        local risk "提醒：个体—时间组合应唯一；xtset 不会自动填补缺失时期。"
        if "`panel'" != "" & "`time'" != "" {
            capture quietly isid `panel' `time'
            if _rc local risk "检查结果：个体—时间组合存在重复，当前设置无法作为标准面板键。"
            else local risk "检查结果：个体—时间组合唯一，可以执行 xtset。"
        }
    }
    else if inlist("`command'", "summarize", "tabstat", "pwcorr", "correlate", "ttest", "tabulate") {
        local operation `"操作摘要：将使用变量 `vars'；预计有效样本 `sampleN'。"'
        local risk "提醒：统计关系用于描述和检验，本身不提供因果识别。"
    }
    else if inlist("`command'", "regress", "areg", "reghdfe", "qreg", "xtreg", "xtlogit", "xtprobit") | ///
        inlist("`command'", "logit", "probit", "poisson", "nbreg", "ppmlhdfe", "ivregress", "ivreghdfe") {
        local operation `"操作摘要：因变量 `depvar'；解释变量 `vars'；预计回归样本 `sampleN' / `_N'。"'
        local risk "提醒：样本数已按条件和所选变量缺失计算；因果解释还需满足模型识别假设。"
    }
    char _dta[hxtoolbox_monitor_operation] `"`operation'"'
    char _dta[hxtoolbox_monitor_risk] `"`risk'"'
    char _dta[hxtoolbox_monitor_change] `"`after_message'"'

    char _dta[hxtoolbox_monitor_command] `"`command'"'
    char _dta[hxtoolbox_monitor_depvar] `"`depvar'"'
    char _dta[hxtoolbox_monitor_vars] `"`vars'"'
    char _dta[hxtoolbox_monitor_ifcond] `"`ifcond'"'
    char _dta[hxtoolbox_monitor_newvar] `"`newvar'"'
    char _dta[hxtoolbox_monitor_expression] `"`expression'"'
    char _dta[hxtoolbox_monitor_using] `"`usingfile'"'
    char _dta[hxtoolbox_monitor_model] `"`model'"'
    char _dta[hxtoolbox_monitor_panel] `"`panel'"'
    char _dta[hxtoolbox_monitor_time] `"`time'"'

    if inlist("`action'", "browse", "summary", "graph", "relation") {
        local native ""
        if "`action'" == "browse" {
            local native "browse `limited'"
        }
        else if "`action'" == "summary" {
            capture confirm numeric variable `monitorvar'
            if !_rc local native "summarize `monitorvar', detail"
            else local native "tabulate `monitorvar', missing"
        }
        else if "`action'" == "graph" {
            capture confirm numeric variable `monitorvar'
            if !_rc local native `"histogram `monitorvar', percent normal name(hxmonitor_distribution, replace) title("分布：`monitorvar'")"'
            else local native `"graph bar (count), over(`monitorvar') name(hxmonitor_distribution, replace) title("类别分布：`monitorvar'")"'
        }
        else {
            local x : word 1 of `vars'
            capture confirm numeric variable `depvar'
            local oky = !_rc
            capture confirm numeric variable `x'
            local okx = !_rc
            if !`oky' | !`okx' {
                display as error "关系图需要选择数值型因变量和至少一个数值型解释变量。"
                exit 198
            }
            local native `"twoway (scatter `depvar' `x') (lfit `depvar' `x'), name(hxmonitor_relation, replace) title("`depvar' 与 `x'")"'
        }
        capture window push `native'
        noisily `native'
        return local command `"`native'"'
    }

    return scalar N = `datasetN'
    return scalar K = `datasetK'
    return scalar sample_N = `sampleN'
    return local monitorvar "`monitorvar'"
    return local command "`command'"
end
