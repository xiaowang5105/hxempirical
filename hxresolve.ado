*! hxresolve 3.1.1  12aug2026
*! Resolver -> Parser -> semantic interpretation -> Schema pipeline
program define hxresolve, rclass
    version 16.0
    syntax anything(name=rawcmd) [, REFRESH]

    gettoken cmd rest : rawcmd
    local cmd = lower(trim(`"`cmd'"'))
    if !regexm("`cmd'", "^[A-Za-z_][A-Za-z0-9_]*$") {
        display as error "请输入一个 Stata 命令名，例如 regress 或 winsor2。"
        exit 198
    }

    capture quietly which `cmd'
    local installed = cond(_rc, 0, 1)
    local source ""
    if `installed' {
        capture quietly findfile `cmd'.ado
        if !_rc local source `"`r(fn)'"'
        if `"`source'"' == "" local source "Stata 内置命令或可执行组件"
    }

    local helpfile ""
    capture quietly findfile `cmd'.sthlp
    if !_rc local helpfile `"`r(fn)'"'
    if `"`helpfile'"' == "" {
        capture quietly findfile `cmd'.hlp
        if !_rc local helpfile `"`r(fn)'"'
    }
    local dlgfile ""
    capture quietly findfile `cmd'.dlg
    if !_rc local dlgfile `"`r(fn)'"'

    quietly hxparser, command(`cmd') source("`source'") ///
        helpfile("`helpfile'") dlgfile("`dlgfile'")
    local parser_source_rc = r(source_rc)
    local parser_help_rc = r(help_rc)
    local parser_source `"`r(normsource)'"'
    local parser_help `"`r(normhelp)'"'
    local version `"`r(version)'"'
    local schema `"`r(schema)'"'
    local quality `"`r(quality)'"'
    local models `"`r(models)'"'
    local default_model `"`r(default_model)'"'
    local vces `"`r(vces)'"'
    local score = r(score)
    foreach flag in has_depvar has_varlist has_if has_in has_weight ///
        has_using has_newvar has_expression has_absorb has_vce ///
        has_cluster has_iv needs_panel model_before {
        local `flag' = r(`flag')
    }

    /* Every command enters the same semantic-interpretation layer. */
    quietly hxsemantics, command(`cmd') depvar(`has_depvar') ///
        varlist(`has_varlist') iflag(`has_if') inflag(`has_in') ///
        weight(`has_weight') using(`has_using') newvar(`has_newvar') ///
        expression(`has_expression') absorb(`has_absorb') ///
        vce(`has_vce') cluster(`has_cluster') iv(`has_iv') ///
        panel(`needs_panel') modelbefore(`model_before') ///
        models(`models') vces(`vces') quality(`quality')
    foreach flag in has_depvar has_varlist has_if has_in has_weight ///
        has_using has_newvar has_expression has_absorb has_vce ///
        has_cluster has_iv needs_panel model_before show_advanced ///
        show_merge_check is_xtset keepdrop_mode winsor_mode predict_mode {
        local `flag' = r(`flag')
    }
    local template `"`r(template)'"'
    local models `"`r(models)'"'
    local default_model `"`r(default_model)'"'
    local vces `"`r(vces)'"'

    /* Minimum native-command contracts for optional HDFE estimators.
       These keep common fields available even before the community command
       is installed and its local help/syntax can be parsed. */
    if inlist("`cmd'", "reghdfe", "ppmlhdfe", "ivreghdfe") {
        local has_absorb 1
        local has_vce 1
        local has_cluster 1
        if `"`vces'"' == "" | `"`vces'"' == "default" {
            local vces "default robust cluster"
        }
    }
    if "`cmd'" == "ivreghdfe" {
        local has_iv 1
    }

    quietly hxinsight, command(`cmd')

    local signature `"`source'|`version'|`helpfile'|`dlgfile'|`quality'|`score'|`template'|`models'|`vces'"'
    local cachedir `"`c(tmpdir)'hxempirical_cache"'
    capture mkdir `"`cachedir'"'
    local cache `"`cachedir'/`cmd'.schema"'
    local cachehit 0
    if "`refresh'" == "" {
        capture confirm file `"`cache'"'
        if !_rc {
            tempname fc
            capture file open `fc' using `"`cache'"', read text
            if !_rc {
                file read `fc' oldsig
                file close `fc'
                if `"`oldsig'"' == `"`signature'"' local cachehit 1
            }
        }
    }
    tempname fw
    capture file open `fw' using `"`cache'"', write replace text
    if !_rc {
        file write `fw' `"`signature'"' _n
        file write `fw' `"quality=`quality'"' _n
        file write `fw' `"schema quality=`quality'; score=`score'"' _n
        file close `fw'
    }

    local installed_text = cond(`installed', "已安装：是", "已安装：否")
    local source_text `"来源：`source'"'
    if !`installed' local source_text "来源：未在当前 adopath 中找到"
    local help_text = cond(`"`helpfile'"' == "", "Help：未找到独立 help 文件", "Help：已找到 Syntax / Options / Examples 资料")
    local dlg_text = cond(`"`dlgfile'"' == "", "官方 dialog：未找到", "官方 dialog：已找到，可作为 Schema 校验来源")
    local ui_quality `"`quality'"'
    if `"`template'"' != "generic" local ui_quality "完整（语义页）"
    local quality_text `"界面解析：`ui_quality'"'
    if `cachehit' local quality_text `"`quality_text'（缓存命中）"'

    char _dta[hxtoolbox_resolve_name] `"`cmd'"'
    char _dta[hxtoolbox_resolve_installed] `"`installed_text'"'
    char _dta[hxtoolbox_resolve_installed_flag] "`installed'"
    char _dta[hxtoolbox_resolve_source] `"`source_text'"'
    char _dta[hxtoolbox_resolve_help] `"`help_text'"'
    char _dta[hxtoolbox_resolve_dlg] `"`dlg_text'"'
    char _dta[hxtoolbox_resolve_quality] `"`quality_text'"'
    local schema_ui = subinstr(`"`schema'"', char(96), "", .)
    local schema_ui = subinstr(`"`schema_ui'"', char(39), "", .)
    local schema_ui = subinstr(`"`schema_ui'"', "%", "", .)
    local schema_ui = substr(`"`schema_ui'"', 1, 1000)
    char _dta[hxtoolbox_resolve_syntax] `"`schema_ui'"'
    char _dta[hxtoolbox_resolve_helpfile] `"`helpfile'"'
    char _dta[hxtoolbox_resolve_dlgfile] `"`dlgfile'"'
    char _dta[hxtoolbox_schema_models] `"`models'"'
    char _dta[hxtoolbox_schema_default_model] `"`default_model'"'
    char _dta[hxtoolbox_schema_vces] `"`vces'"'
    char _dta[hxtoolbox_schema_template] `"`template'"'
    foreach flag in has_depvar has_varlist has_if has_in has_weight ///
        has_using has_newvar has_expression has_absorb has_vce ///
        has_cluster has_iv needs_panel model_before {
        char _dta[hxtoolbox_schema_`flag'] "``flag''"
    }
    capture hxregistry, recent(`cmd')

    return scalar installed = `installed'
    return scalar cachehit = `cachehit'
    return scalar score = `score'
    return scalar parser_source_rc = `parser_source_rc'
    return scalar parser_help_rc = `parser_help_rc'
    return local command `"`cmd'"'
    return local source `"`source'"'
    return local helpfile `"`helpfile'"'
    return local dlgfile `"`dlgfile'"'
    return local quality `"`quality'"'
    return local schema `"`schema'"'
    return local template `"`template'"'
    return local parser_source `"`parser_source'"'
    return local parser_help `"`parser_help'"'
end
