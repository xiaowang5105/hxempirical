*! hxinstall_zip 1.0.0  14aug2026
*! Single-archive bootstrap installer for hxempirical
version 17.0
set more off

if c(stata_version) < 17 {
    display as error "hxempirical 需要 Stata 17 或更高版本。"
    exit 9
}

/* Download one repository archive instead of dozens of individual files. */
local archive "https://codeload.github.com/xiaowang5105/hxempirical/zip/refs/heads/main"
local target `"`c(sysdir_personal)'"'
if `"`target'"' == "" {
    display as error "Stata 没有返回 PERSONAL ado 目录。"
    exit 603
}

local tlast = substr(`"`target'"', strlen(`"`target'"'), 1)
if !inlist(`"`tlast'"', "/", "\") local target `"`target'/"'

/* Verify the user-level install directory before touching the installation. */
capture mkdir `"`target'"'
local probe `"`target'__hxempirical_write_test.tmp"'
tempname ph
capture file open `ph' using `"`probe'"', write text replace
if _rc {
    display as error "无法写入 Stata PERSONAL 目录：`target'"
    display as text  "请运行 sysdir 检查 PERSONAL 目录。"
    exit 603
}
file write `ph' "ok" _n
file close `ph'
capture erase `"`probe'"'

/* Use fixed names under Stata's temporary directory so unzipfile can work
   with a normal .zip filename on Windows and macOS. */
local tmp `"`c(tmpdir)'"'
local plast = substr(`"`tmp'"', strlen(`"`tmp'"'), 1)
if !inlist(`"`plast'"', "/", "\") local tmp `"`tmp'/"'
local zipfile `"`tmp'hxempirical-main.zip"'
local stage   `"`tmp'hxempirical_zip_stage"'

capture erase `"`zipfile'"'
capture mkdir `"`stage'"'

display as text "正在下载 hxempirical 单文件安装包..."
capture quietly copy `"`archive'"' `"`zipfile'"', replace
if _rc {
    display as error "下载安装包失败。"
    display as text  "下载地址：`archive'"
    display as text  "请检查当前网络能否访问 codeload.github.com。"
    exit 603
}

local oldpwd `"`c(pwd)'"'
capture noisily cd `"`stage'"'
if _rc {
    display as error "无法进入临时解压目录：`stage'"
    exit 603
}

capture noisily unzipfile `"`zipfile'"', replace
local unzip_rc = _rc
capture noisily cd `"`oldpwd'"'
if `unzip_rc' {
    display as error "安装包解压失败，返回码 `unzip_rc'。"
    exit `unzip_rc'
}

local root `"`stage'/hxempirical-main"'
capture confirm file `"`root'/hxempirical.pkg"'
if _rc {
    display as error "安装包结构异常：未找到 hxempirical.pkg。"
    exit 498
}

/* Read the official package manifest and copy only production files. */
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
if `nfiles' == 0 {
    display as error "hxempirical.pkg 中没有安装文件。"
    exit 498
}

/* Verify the whole archive before changing the existing installation. */
foreach f of local files {
    capture confirm file `"`root'/`f'"'
    if _rc {
        display as error "安装包缺少文件：`f'"
        display as text  "现有安装没有被覆盖。"
        exit 498
    }
}

/* Commit the verified package to PERSONAL. */
foreach f of local files {
    capture quietly copy `"`root'/`f'"' `"`target'`f'"', replace
    if _rc {
        display as error "写入失败：`target'`f'"
        display as text  "请检查 PERSONAL 目录权限。"
        exit 603
    }
}

capture confirm file `"`target'hxempirical.ado"'
if _rc exit 601
capture confirm file `"`target'hxworkbench.jar"'
if _rc exit 601

capture discard
noi display as result _newline "hxempirical 安装完成。"
if `"`package_version'"' != "" noi display as text "版本：" as result "`package_version'"
noi display as text "安装文件：" as result "`nfiles' 个"
noi display as text "安装位置：" as result `"`target'"'
noi display as text "现在运行：" as result "hxempirical"
