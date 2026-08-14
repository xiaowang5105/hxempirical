*! hxportable 1.0.0  14aug2026
*! Permission-independent portable launcher for hxempirical
version 17.0
set more off

if c(stata_version) < 17 {
    display as error "hxempirical 需要 Stata 17 或更高版本。"
    exit 9
}

/* Choose a private writable cache outside Stata's PLUS/PERSONAL folders.
   HOME/USERPROFILE is preferred; current working directory is the fallback. */
local home : environment HOME
if `"`home'"' == "" local home : environment USERPROFILE

local target ""
if `"`home'"' != "" {
    local root `"`home'/.hxempirical"'
    capture mkdir `"`root'"'
    local candidate `"`root'/ado"'
    capture mkdir `"`candidate'"'
    local probe `"`candidate'/__hx_write_test.tmp"'
    tempname ph1
    capture file open `ph1' using `"`probe'"', write text replace
    if !_rc {
        file write `ph1' "ok" _n
        file close `ph1'
        capture erase `"`probe'"'
        local target `"`candidate'"'
    }
}

if `"`target'"' == "" {
    local candidate `"`c(pwd)'/.hxempirical_ado"'
    capture mkdir `"`candidate'"'
    local probe `"`candidate'/__hx_write_test.tmp"'
    tempname ph2
    capture file open `ph2' using `"`probe'"', write text replace
    if !_rc {
        file write `ph2' "ok" _n
        file close `ph2'
        capture erase `"`probe'"'
        local target `"`candidate'"'
    }
}

if `"`target'"' == "" {
    display as error "没有找到可写的用户目录。"
    display as text "请切换到一个可写目录后重新运行本命令。"
    exit 603
}

/* Make the private cache visible to Stata in this session. */
capture adopath ++ `"`target'"'

/* One archive download; bypasses Stata package-manager target directories. */
local archive "https://codeload.github.com/xiaowang5105/hxempirical/zip/refs/heads/main"
local tmp `"`c(tmpdir)'"'
local plast = substr(`"`tmp'"', strlen(`"`tmp'"'), 1)
if !inlist(`"`plast'"', "/", "\") local tmp `"`tmp'/"'
local zipfile `"`tmp'hxempirical-portable.zip"'
local stage   `"`tmp'hxempirical_portable_stage"'

capture erase `"`zipfile'"'
capture mkdir `"`stage'"'

display as text "正在准备 hxempirical 便携版..."
capture quietly copy `"`archive'"' `"`zipfile'"', replace
if _rc {
    /* If a cached copy already exists, allow offline launch. */
    capture confirm file `"`target'/hxempirical.ado"'
    if !_rc {
        capture discard
        display as text "网络不可用，已使用本机缓存：`target'"
        hxempirical
        exit
    }
    display as error "无法下载 hxempirical，且本机没有可用缓存。"
    exit 603
}

local oldpwd `"`c(pwd)'"'
capture noisily cd `"`stage'"'
if _rc exit 603
capture noisily unzipfile `"`zipfile'"', replace
local unzip_rc = _rc
capture noisily cd `"`oldpwd'"'
if `unzip_rc' exit `unzip_rc'

local root `"`stage'/hxempirical-main"'
capture confirm file `"`root'/hxempirical.pkg"'
if _rc {
    display as error "下载包结构异常。"
    exit 498
}

/* Install only files listed by the package manifest. */
tempname mf
file open `mf' using `"`root'/hxempirical.pkg"', read text
local files ""
local package_version ""
file read `mf' line
while r(eof) == 0 {
    local line = trim(`"`line'"')
    gettoken tag rest : line
    if lower(`"`tag'"') == "f" {
        gettoken fname unused : rest
        if `"`fname'"' != "" local files `"`files' `fname'"'
    }
    if lower(`"`tag'"') == "d" {
        gettoken dkey drest : rest
        if lower(`"`dkey'"') == "version" local package_version = trim(`"`drest'"')
    }
    file read `mf' line
}
file close `mf'
local files = trim(itrim(`"`files'"'))
local nfiles : word count `files'
if `nfiles' == 0 exit 498

foreach f of local files {
    capture confirm file `"`root'/`f'"'
    if _rc {
        display as error "安装包缺少文件：`f'"
        exit 498
    }
}

foreach f of local files {
    capture quietly copy `"`root'/`f'"' `"`target'/`f'"', replace
    if _rc {
        display as error "写入缓存失败：`target'/`f'"
        exit 603
    }
}

capture confirm file `"`target'/hxempirical.ado"'
if _rc exit 601
capture confirm file `"`target'/hxworkbench.jar"'
if _rc exit 601

capture discard
capture adopath ++ `"`target'"'

noi display as result _newline "hxempirical 便携版已就绪。"
if `"`package_version'"' != "" noi display as text "版本：" as result "`package_version'"
noi display as text "缓存位置：" as result `"`target'"'
noi display as text "本方式不写入 Stata PLUS/PERSONAL。"
noi display as text "正在启动 hxempirical..." _newline
hxempirical
