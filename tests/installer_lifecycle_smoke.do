version 17.0
clear all
set more off

/* Run from the repository root, or pass the repository root as argument 1. */
args repository
if `"`repository'"' == "" local repository `"`c(pwd)'"'
local repository : subinstr local repository "\" "/", all
local installer `"`repository'/hxinstall.do"'
capture quietly confirm file `"`installer'"'
if _rc {
    display as error "HX_INSTALLER_TEST_FAIL cannot find hxinstall.do"
    exit 601
}

local original_personal `"`c(sysdir_personal)'"'
local original_pwd `"`c(pwd)'"'
tempfile lifecycle_base
local test_personal `"`lifecycle_base'_personal"'
local test_profile `"`test_personal'/profile.do"'
local begin "* >>> HXEMPIRICAL MANAGED MENU >>>"

sysdir set PERSONAL `"`test_personal'/"'
cd `"`c(tmpdir)'"'

/* The same automatic command installs into a clean PERSONAL directory. */
capture noisily do `"`installer'"' auto `"`repository'"'
local install_rc = _rc
if `install_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL install r(`install_rc')"
    exit `install_rc'
}
capture quietly confirm file `"`test_personal'/hxempirical.ado"'
if _rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL missing hxempirical.ado"
    exit 601
}
capture quietly confirm file `"`test_personal'/hxworkbench.jar"'
if _rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL missing hxworkbench.jar"
    exit 601
}
capture quietly confirm file `"`test_personal'/hxinstaller.ado"'
if _rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL missing hxinstaller.ado"
    exit 601
}
capture quietly confirm file `"`test_profile'"'
if _rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL missing persistent profile"
    exit 601
}

discard
capture noisily hxempirical doctor
local doctor_rc = _rc
if `doctor_rc' | r(core_healthy) != 1 {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL doctor r(`doctor_rc')"
    exit 459
}

/* Repeating the automatic command must take the fast current-version path. */
capture noisily do `"`installer'"' auto `"`repository'"'
local update_rc = _rc
if `update_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL update r(`update_rc')"
    exit `update_rc'
}

/* The same command repairs an incomplete installation automatically. */
capture quietly erase `"`test_personal'/hxhistory.ado"'
capture noisily do `"`installer'"' auto `"`repository'"'
local repair_rc = _rc
capture quietly confirm file `"`test_personal'/hxhistory.ado"'
local repaired_file_rc = _rc
if `repair_rc' | `repaired_file_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL automatic repair r(`repair_rc')"
    exit 601
}

tempname profile_in
file open `profile_in' using `"`test_profile'"', read text
local begin_count 0
file read `profile_in' line
while r(eof) == 0 {
    if trim(`"`line'"') == `"`begin'"' local ++begin_count
    file read `profile_in' line
}
file close `profile_in'
if `begin_count' != 1 {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL duplicate profile blocks: `begin_count'"
    exit 459
}

/* Uninstall uses the local manifest and removes the managed menu block. */
capture noisily do `"`installer'"' uninstall `"`repository'"'
local uninstall_rc = _rc
if `uninstall_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL uninstall r(`uninstall_rc')"
    exit `uninstall_rc'
}
capture quietly confirm file `"`test_personal'/hxempirical.ado"'
if !_rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL hxempirical.ado remains"
    exit 602
}
capture quietly confirm file `"`test_personal'/hxworkbench.jar"'
if !_rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL hxworkbench.jar remains"
    exit 602
}
capture quietly confirm file `"`test_personal'/hxinstaller.ado"'
if !_rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL hxinstaller.ado remains"
    exit 602
}

tempname profile_after
file open `profile_after' using `"`test_profile'"', read text
local begin_count 0
file read `profile_after' line
while r(eof) == 0 {
    if trim(`"`line'"') == `"`begin'"' local ++begin_count
    file read `profile_after' line
}
file close `profile_after'
if `begin_count' != 0 {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL profile block remains"
    exit 459
}

sysdir set PERSONAL `"`original_personal'"'
cd `"`original_pwd'"'
capture quietly erase `"`test_profile'"'
capture quietly erase `"`test_personal'/profile.before_hxempirical.do"'
capture quietly rmdir `"`test_personal'"'

display as result "HX_INSTALLER_LIFECYCLE_OK"
