version 17.0
clear all
set more off

/* Run from the repository root, or pass the repository root as argument 1. */
args repository
if `"`repository'"' == "" local repository `"`c(pwd)'"'
local repository : subinstr local repository "\" "/", all
local launcher `"`repository'/hxinstall_offline.do"'
local manifest `"`repository'/hxempirical.pkg"'
local installer `"`repository'/hxinstall.do"'
local installer_core `"`repository'/hxinstaller.ado"'

foreach required in `"`launcher'"' `"`manifest'"' `"`installer'"' `"`installer_core'"' {
    capture quietly confirm file `"`required'"'
    if _rc {
        display as error "HX_OFFLINE_LAUNCHER_TEST_FAIL missing `required'"
        exit 601
    }
}

local original_personal `"`c(sysdir_personal)'"'
local original_pwd `"`c(pwd)'"'
tempfile offline_base
local test_personal `"`offline_base'_personal"'
sysdir set PERSONAL `"`test_personal'/"'
cd `"`c(tmpdir)'"'

capture noisily do `"`launcher'"' `"`manifest'"'
local install_rc = _rc
if `install_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_OFFLINE_LAUNCHER_TEST_FAIL install r(`install_rc')"
    exit `install_rc'
}

capture quietly confirm file `"`test_personal'/hxempirical.ado"'
local core_rc = _rc
capture quietly confirm file `"`test_personal'/hxworkbench.jar"'
local jar_rc = _rc
capture quietly confirm file `"`test_personal'/hxinstaller.ado"'
local installer_core_rc = _rc
if `core_rc' | `jar_rc' | `installer_core_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_OFFLINE_LAUNCHER_TEST_FAIL incomplete installation"
    exit 601
}

capture noisily do `"`installer'"' uninstall `"`repository'"'
local uninstall_rc = _rc
sysdir set PERSONAL `"`original_personal'"'
cd `"`original_pwd'"'
if `uninstall_rc' {
    display as error "HX_OFFLINE_LAUNCHER_TEST_FAIL uninstall r(`uninstall_rc')"
    exit `uninstall_rc'
}

capture quietly erase `"`test_personal'/profile.do"'
capture quietly erase `"`test_personal'/profile.before_hxempirical.do"'
capture quietly rmdir `"`test_personal'"'
display as result "HX_OFFLINE_LAUNCHER_OK"
