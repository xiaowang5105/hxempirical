*! hxparser 1.0.0  09aug2026
*! Unified parser: ado syntax + help Syntax/Options/Examples + official dialog
program define hxparser, rclass
    version 16.0
    syntax , COMMAND(name) [SOURCE(string asis) HELPFILE(string asis) ///
        DLGFILE(string asis)]

    local cmd = lower("`command'")
    foreach item in source helpfile dlgfile {
        local `item' = trim(`"``item''"')
        if substr(`"``item''"', 1, 1) == char(34) & ///
            substr(`"``item''"', -1, 1) == char(34) {
            local `item' = substr(`"``item''"', 2, strlen(`"``item''"') - 2)
        }
    }
    local source_rc .
    local help_rc .
    local adosyntax ""
    local versionline ""
    if `"`source'"' != "" & `"`source'"' != "Stata 内置命令或可执行组件" {
        tempname fa
        capture file open `fa' using `"`source'"', read text
        local source_rc = _rc
        if !_rc {
            local n 0
            file read `fa' line
            while r(eof) == 0 & `n' < 1200 {
                local ++n
                mata: st_local("__hxline", subinstr(subinstr(subinstr(subinstr(st_local("line"), char(96), ""), char(39), ""), char(37), ""), char(36), ""))
                local clean = trim(`"`__hxline'"')
                if `"`versionline'"' == "" & strpos(lower(`"`clean'"'), "*! version") local versionline `"`clean'"'
                if `"`adosyntax'"' == "" & ///
                    (substr(lower(`"`clean'"'), 1, 7) == "syntax " | ///
                    strpos(lower(`"`clean'"'), " syntax ")) {
                    local adosyntax `"`clean'"'
                    while substr(trim(`"`adosyntax'"'), -3, 3) == "///" & r(eof) == 0 {
                        file read `fa' line
                        mata: st_local("__hxline", subinstr(subinstr(subinstr(subinstr(st_local("line"), char(96), ""), char(39), ""), char(37), ""), char(36), ""))
                        local adosyntax `"`adosyntax' `=trim(`"`__hxline'"')'"'
                    }
                }
                file read `fa' line
            }
            file close `fa'
        }
    }

    local helpsyntax ""
    local optiontext ""
    local examples ""
    local dialogtext ""
    if `"`helpfile'"' != "" {
        tempname fh
        capture file open `fh' using `"`helpfile'"', read text
        local help_rc = _rc
        if !_rc {
            local n 0
            local section ""
            local syntax_collect 0
            file read `fh' line
            while r(eof) == 0 & `n' < 5000 {
                local ++n
                mata: st_local("__hxline", subinstr(subinstr(subinstr(subinstr(st_local("line"), char(96), ""), char(39), ""), char(37), ""), char(36), ""))
                local low = lower(trim(`"`__hxline'"'))
                if strpos(`"`low'"', "{title:syntax}") local section "syntax"
                else if strpos(`"`low'"', "{title:options}") local section "options"
                else if strpos(`"`low'"', "{title:example") local section "examples"
                else if strpos(`"`low'"', "{title:") local section ""

                if `"`section'"' == "syntax" {
                    if `syntax_collect' & strpos(`"`low'"', "{synopt") local syntax_collect 0
                    if `syntax_collect' & `"`low'"' != "" & strlen(`"`helpsyntax'"') < 2500 {
                        local helpsyntax `"`helpsyntax' `=trim(`"`__hxline'"')'"'
                    }
                    if !`syntax_collect' & `"`helpsyntax'"' == "" & ///
                        (strpos(`"`low'"', "{cmd:") | strpos(`"`low'"', "{cmdab:") | ///
                        strpos(`"`low'"', "{opt ") | strpos(`"`low'"', "{opt:")) {
                        local helpsyntax `"`=trim(`"`__hxline'"')'"'
                        local syntax_collect 1
                    }
                }
                if `"`section'"' == "options" & strlen(`"`optiontext'"') < 12000 {
                    local optiontext `"`optiontext' `__hxline'"'
                }
                if `"`section'"' == "examples" & strlen(`"`examples'"') < 12000 & ///
                    (strpos(`"`low'"', "{cmd:") | strpos(`"`low'"', "{stata ")) {
                    local examples `"`examples' `__hxline'"'
                }
                file read `fh' line
            }
            file close `fh'
        }
    }

    if `"`dlgfile'"' != "" {
        tempname fd
        capture file open `fd' using `"`dlgfile'"', read text
        if !_rc {
            local n 0
            file read `fd' line
            while r(eof) == 0 & `n' < 5000 & strlen(`"`dialogtext'"') < 16000 {
                local ++n
                mata: st_local("__hxline", subinstr(subinstr(subinstr(subinstr(st_local("line"), char(96), ""), char(39), ""), char(37), ""), char(36), ""))
                local low = lower(trim(`"`__hxline'"'))
                if regexm(`"`low'"', "varname|varlist|ifin|weight|option\(|vce|cluster|absorb|radio|combobox") {
                    local dialogtext `"`dialogtext' `__hxline'"'
                }
                file read `fd' line
            }
            file close `fd'
        }
    }

    local combined = lower(`"`adosyntax' `helpsyntax' `optiontext' `examples' `dialogtext'"')
    local syntaxonly = lower(`"`adosyntax' `helpsyntax'"')
    local has_depvar = regexm(`"`syntaxonly' `dialogtext'"', "depvar|dep\.var|dependent|varname[^\n]*dep")
    local has_varlist = regexm(`"`syntaxonly' `dialogtext'"', "indepvars|indepvar|varlist|exogvars|varnames")
    local has_if = regexm(`"`syntaxonly'"', "\[if\]|\{ifin\}|\[ifin\]|[ 	]if[ 	]*\]")
    local has_in = regexm(`"`syntaxonly'"', "\[in\]|\{ifin\}|\[ifin\]")
    local has_weight = regexm(`"`syntaxonly'"', "weight|fweight|aweight|pweight|iweight")
    local has_using = regexm(`"`syntaxonly'"', "(^|[^a-z])using([^a-z]|$)")
    local has_newvar = regexm(`"`syntaxonly'"', "newvar|newname")
    local has_expression = regexm(`"`syntaxonly'"', "=[ ]*(exp|expression)|=exp")
    local has_absorb = regexm(`"`combined'"', "absorb\(|absorb[:(]|absorb option")
    local has_vce = regexm(`"`combined'"', "vce\(|vce[:(]|robust|cluster")
    local has_cluster = regexm(`"`combined'"', "cluster\(|vce\(cluster|cluster clustvar")
    local has_iv = regexm(`"`syntaxonly'"', "varlist2[^=]*=|endog|instruments?|varlist_iv")
    local needs_panel = regexm(`"`combined'"', "xtset|panel variable|panelvar")

    local models ""
    if regexm(`"`syntaxonly'"', "\{opt[^}]*f:e[^}]*\}|,[ ]*fe([^a-z]|$)") local models "`models' fe"
    if regexm(`"`syntaxonly'"', "\{opt[^}]*r:e[^}]*\}|,[ ]*re([^a-z]|$)") local models "`models' re"
    if regexm(`"`syntaxonly'"', "\{opt[^}]*b:e[^}]*\}|,[ ]*be([^a-z]|$)") local models "`models' be"
    if regexm(`"`syntaxonly'"', "(^|[^a-z0-9])2sls([^a-z0-9]|$)") local models "`models' 2sls"
    if regexm(`"`syntaxonly'"', "(^|[^a-z])liml([^a-z]|$)") local models "`models' liml"
    if regexm(`"`syntaxonly'"', "(^|[^a-z])gmm([^a-z]|$)") local models "`models' gmm"
    if strpos(`"`syntaxonly'"', "estimator") {
        if regexm(`"`combined'"', "(^|[^a-z0-9])2sls([^a-z0-9]|$)") local models "`models' 2sls"
        if regexm(`"`combined'"', "(^|[^a-z])liml([^a-z]|$)") local models "`models' liml"
        if regexm(`"`combined'"', "(^|[^a-z])gmm([^a-z]|$)") local models "`models' gmm"
    }
    local models = trim(itrim("`models'"))
    local models : list uniq models
    local default_model : word 1 of `models'

    local model_before 0
    if `"`models'"' != "" & strpos(`"`syntaxonly'"', "estimator") & ///
        strpos(`"`syntaxonly'"', "depvar") & ///
        strpos(`"`syntaxonly'"', "estimator") < strpos(`"`syntaxonly'"', "depvar") {
        local model_before 1
    }

    local vces "default"
    if regexm(`"`combined'"', "robust") local vces "`vces' robust"
    if `has_cluster' local vces "`vces' cluster"

    local score = (`"`adosyntax'"' != "") + (`"`helpsyntax'"' != "") + ///
        (`"`optiontext'"' != "") + (`"`examples'"' != "") + (`"`dlgfile'"' != "")
    local quality "部分参数需要手动输入"
    if `score' >= 4 local quality "完整"
    else if `score' >= 2 local quality "基本完整"

    local schema `"`adosyntax'"'
    if `"`schema'"' == "" local schema `"`helpsyntax'"'
    if `"`schema'"' == "" local schema "未提取到结构化 Syntax；使用特殊语法与其他 options 输入框。"

    return local command `"`cmd'"'
    return local version `"`versionline'"'
    return local adosyntax `"`adosyntax'"'
    return local helpsyntax `"`helpsyntax'"'
    return local options `"`optiontext'"'
    return local examples `"`examples'"'
    return local dialog `"`dialogtext'"'
    return local schema `"`schema'"'
    return local quality `"`quality'"'
    return local models `"`models'"'
    return local default_model `"`default_model'"'
    return local vces `"`vces'"'
    return scalar score = `score'
    return scalar has_depvar = `has_depvar'
    return scalar has_varlist = `has_varlist'
    return scalar has_if = `has_if'
    return scalar has_in = `has_in'
    return scalar has_weight = `has_weight'
    return scalar has_using = `has_using'
    return scalar has_newvar = `has_newvar'
    return scalar has_expression = `has_expression'
    return scalar has_absorb = `has_absorb'
    return scalar has_vce = `has_vce'
    return scalar has_cluster = `has_cluster'
    return scalar has_iv = `has_iv'
    return scalar needs_panel = `needs_panel'
    return scalar model_before = `model_before'
    return scalar source_rc = `source_rc'
    return scalar help_rc = `help_rc'
    return local normsource `"`source'"'
    return local normhelp `"`helpfile'"'
end
