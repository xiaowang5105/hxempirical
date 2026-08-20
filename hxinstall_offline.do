*! hxinstall_offline 1.1.0  20aug2026
*! Browser-download/offline launcher for hxempirical
version 17.0
set more off

args manifest
local manifest = trim(`"`manifest'"')

if `"`manifest'"' == "" {
    capture quietly confirm file "hxempirical.pkg"
    if !_rc local manifest `"`c(pwd)'/hxempirical.pkg"'
}

if `"`manifest'"' == "" {
    global HX_OFFLINE_MANIFEST ""
    capture window fopen HX_OFFLINE_MANIFEST ///
        "选择解压文件夹中的 hxempirical.pkg" ///
        "HX 安装清单|hxempirical.pkg|Stata package (*.pkg)|*.pkg|All files (*.*)|*.*" pkg
    if _rc | `"$HX_OFFLINE_MANIFEST"' == "" {
        macro drop HX_OFFLINE_MANIFEST
        display as text "已取消离线安装。"
        exit 0
    }
    local manifest `"$HX_OFFLINE_MANIFEST"'
    macro drop HX_OFFLINE_MANIFEST
}

local manifest : subinstr local manifest "\" "/", all
capture quietly confirm file `"`manifest'"'
if _rc {
    display as error "找不到安装清单：`manifest'"
    exit 601
}

local slash = strrpos(`"`manifest'"', "/")
if `slash' <= 1 {
    display as error "无法识别离线包所在文件夹。"
    exit 198
}
local source = substr(`"`manifest'"', 1, `slash' - 1)
local installer `"`source'/hxinstall.do"'
capture quietly confirm file `"`installer'"'
if _rc {
    display as error "离线包中缺少 hxinstall.do。请重新下载并完整解压。"
    exit 601
}

/* The browser ZIP includes a non-self-referential per-file integrity index.
   The installer validates the extracted managed files directly, without
   requiring the GitHub-only Base64 distribution index and chunks. */
foreach required in hxinstaller.ado hxempirical.pkg hxempirical-offline.index {
    capture quietly confirm file `"`source'/`required'"'
    if _rc {
        display as error "离线包不完整：缺少 `required'。"
        display as text "请重新下载最新 hxempirical-release.zip，并完整解压后再运行。"
        exit 601
    }
}

display as text "正在从本地离线包安装：`source'"
quietly do `"`installer'"' auto `"`source'"'
