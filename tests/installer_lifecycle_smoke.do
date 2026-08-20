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
local install_target `"`test_personal'/h"'
local test_profile `"`test_personal'/profile.do"'
local test_cwd `"`lifecycle_base'_cwd"'
local begin "* >>> HXEMPIRICAL MANAGED MENU >>>"

sysdir set PERSONAL `"`test_personal'/"'
capture quietly mkdir `"`test_personal'"'
capture quietly mkdir `"`test_cwd'"'
cd `"`test_cwd'"'

/* Deliberately stale current-directory ado files must never shadow the exact
   bootstrap/setup files selected by the installer. */
tempname stale_installer stale_setup stale_menu
file open `stale_installer' using "hxinstaller.ado", write text replace
file write `stale_installer' "program define hxinstaller" _n
file write `stale_installer' "    exit 999" _n
file write `stale_installer' "end" _n
file close `stale_installer'
file open `stale_setup' using "hxsetup.ado", write text replace
file write `stale_setup' "program define hxsetup" _n
file write `stale_setup' "    exit 998" _n
file write `stale_setup' "end" _n
file close `stale_setup'
file open `stale_menu' using "hxmenu.ado", write text replace
file write `stale_menu' "program define hxmenu" _n
file write `stale_menu' "    global HXEI_SHADOW_MENU_CALLED 1" _n
file write `stale_menu' "end" _n
file close `stale_menu'

/* A pre-existing lock blocks a second transaction without changing PERSONAL. */
tempname stale_lock
file open `stale_lock' using `"`test_personal'/hxempirical.install.lock"', write text replace
file write `stale_lock' "simulated interrupted install" _n
file close `stale_lock'
capture noisily do `"`installer'"' auto `"`repository'"'
local lock_rc = _rc
capture quietly confirm file `"`install_target'/hxempirical.ado"'
local lock_created_install = (_rc == 0)
capture quietly erase `"`test_personal'/hxempirical.install.lock"'
if `lock_rc' == 0 | `lock_created_install' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL install lock was ignored"
    exit 459
}

/* The same automatic command installs into a clean PERSONAL directory. */
capture noisily do `"`installer'"' auto `"`repository'"'
local install_rc = _rc
if `install_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL install r(`install_rc')"
    exit `install_rc'
}
capture quietly confirm file `"`install_target'/hxempirical.ado"'
if _rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL missing hxempirical.ado"
    exit 601
}
capture quietly confirm file `"`install_target'/hxworkbench.jar"'
if _rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL missing hxworkbench.jar"
    exit 601
}
capture quietly confirm file `"`install_target'/hxinstaller.ado"'
if _rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL missing hxinstaller.ado"
    exit 601
}
if `"${HXEI_SHADOW_MENU_CALLED}"' != "" {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL current-directory hxmenu shadowed managed menu"
    exit 459
}
capture quietly confirm file `"`install_target'/hxempirical.integrity"'
if _rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL missing integrity manifest"
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
capture noisily do `"`test_profile'"'
local profile_run_rc = _rc
if `profile_run_rc' | `"${HXEI_SHADOW_MENU_CALLED}"' != "" {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL persisted profile used shadow hxmenu"
    exit 459
}
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

/* A zero-byte JAR under the current version must trigger repair, never the
   same-version fast path. */
tempname empty_jar
file open `empty_jar' using `"`install_target'/hxworkbench.jar"', write binary replace
file close `empty_jar'
quietly checksum `"`install_target'/hxworkbench.jar"'
if r(filelen) != 0 {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL could not create empty JAR fixture"
    exit 459
}
capture noisily do `"`installer'"' auto `"`repository'"'
local empty_repair_rc = _rc
capture quietly checksum `"`install_target'/hxworkbench.jar"'
local repaired_jar_rc = _rc
local repaired_jar_bytes 0
if !`repaired_jar_rc' local repaired_jar_bytes = r(filelen)
if `empty_repair_rc' | `repaired_jar_rc' | `repaired_jar_bytes' <= 0 {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL empty JAR was not repaired"
    exit 601
}
display as result "HX_INSTALLER_EMPTY_JAR_REPAIR_OK"

/* The same command repairs an incomplete installation automatically. */
capture quietly erase `"`install_target'/hxhistory.ado"'
capture noisily do `"`installer'"' auto `"`repository'"'
local repair_rc = _rc
capture quietly confirm file `"`install_target'/hxhistory.ado"'
local repaired_file_rc = _rc
if `repair_rc' | `repaired_file_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL automatic repair r(`repair_rc')"
    exit 601
}

/* A modified local package cannot define files for fast update or deletion. */
tempname sentinel_out package_append
file open `sentinel_out' using `"`install_target'/hx_user_keep.do"', write text replace
file write `sentinel_out' "* user-owned sentinel" _n
file close `sentinel_out'
file open `package_append' using `"`install_target'/hxempirical.pkg"', write text append
file write `package_append' "f hx_user_keep.do" _n
file close `package_append'
capture noisily do `"`installer'"' auto `"`repository'"'
local pkg_repair_rc = _rc
capture quietly confirm file `"`install_target'/hx_user_keep.do"'
local sentinel_rc = _rc
if `pkg_repair_rc' | `sentinel_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL damaged local pkg controlled user file"
    exit 459
}
display as result "HX_INSTALLER_LOCAL_PKG_BINDING_OK"

/* A deletion failure for an obsolete managed file must roll the entire update
   back, including the prior package and integrity records. */
tempname obsolete_out old_pkg_append old_pkg_in old_integrity_out
file open `obsolete_out' using `"`install_target'/hxobsolete.ado"', write text replace
file write `obsolete_out' "*! obsolete managed fixture" _n
file close `obsolete_out'
file open `old_pkg_append' using `"`install_target'/hxempirical.pkg"', write text append
file write `old_pkg_append' "f hxobsolete.ado" _n
file close `old_pkg_append'

local old_managed_files ""
local old_package_version ""
file open `old_pkg_in' using `"`install_target'/hxempirical.pkg"', read text
file read `old_pkg_in' old_pkg_line
while r(eof) == 0 {
    local old_pkg_line = trim(`"`old_pkg_line'"')
    gettoken old_pkg_tag old_pkg_rest : old_pkg_line
    if lower(`"`old_pkg_tag'"') == "f" {
        gettoken old_pkg_name old_pkg_unused : old_pkg_rest
        local old_managed_files `"`old_managed_files' `old_pkg_name'"'
    }
    if lower(`"`old_pkg_tag'"') == "d" {
        gettoken old_pkg_key old_pkg_value : old_pkg_rest
        if lower(`"`old_pkg_key'"') == "version" local old_package_version = trim(`"`old_pkg_value'"')
    }
    file read `old_pkg_in' old_pkg_line
}
file close `old_pkg_in'
quietly checksum `"`install_target'/hxempirical.pkg"'
local old_pkg_bytes = r(filelen)
local old_pkg_checksum = r(checksum)
file open `old_integrity_out' using `"`install_target'/hxempirical.integrity"', write text replace
file write `old_integrity_out' "v 1" _n
file write `old_integrity_out' "d version `old_package_version'" _n
file write `old_integrity_out' "d pkg_bytes `old_pkg_bytes'" _n
file write `old_integrity_out' "d pkg_checksum `old_pkg_checksum'" _n
foreach f of local old_managed_files {
    quietly checksum `"`install_target'/`f'"'
    local fixture_bytes = r(filelen)
    local fixture_checksum = r(checksum)
    file write `old_integrity_out' "f `f' `fixture_bytes' `fixture_checksum'" _n
}
file close `old_integrity_out'
quietly checksum `"`install_target'/hxempirical.integrity"'
local old_integrity_bytes = r(filelen)
local old_integrity_checksum = r(checksum)

global HXEI_TEST_FAIL_FILE "hxobsolete.ado"
capture noisily do `"`installer'"' repair `"`repository'"'
local obsolete_fail_rc = _rc
macro drop HXEI_TEST_FAIL_FILE
capture quietly confirm file `"`install_target'/hxobsolete.ado"'
local obsolete_restore_rc = _rc
quietly checksum `"`install_target'/hxempirical.pkg"'
local restored_pkg_ok = (r(filelen) == `old_pkg_bytes' & r(checksum) == `old_pkg_checksum')
quietly checksum `"`install_target'/hxempirical.integrity"'
local restored_integrity_ok = (r(filelen) == `old_integrity_bytes' & r(checksum) == `old_integrity_checksum')
if `obsolete_fail_rc' == 0 | `obsolete_restore_rc' | !`restored_pkg_ok' | !`restored_integrity_ok' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL obsolete-file rollback"
    exit 459
}
capture noisily do `"`installer'"' repair `"`repository'"'
local obsolete_retry_rc = _rc
capture quietly confirm file `"`install_target'/hxobsolete.ado"'
local obsolete_remains = (_rc == 0)
if `obsolete_retry_rc' | `obsolete_remains' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL obsolete file survived successful retry"
    exit 459
}
display as result "HX_INSTALLER_OBSOLETE_ROLLBACK_OK"

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

/* A simulated locked JAR must roll the uninstall transaction back completely,
   including the retry entry, manifest and profile menu block. */
global HXEI_TEST_FAIL_FILE "hxworkbench.jar"
capture noisily do `"`installer'"' uninstall `"`repository'"'
local locked_uninstall_rc = _rc
macro drop HXEI_TEST_FAIL_FILE
if `locked_uninstall_rc' == 0 {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL simulated locked JAR unexpectedly uninstalled"
    exit 459
}
foreach required in hxempirical.ado hxworkbench.jar hxinstaller.ado hxempirical.pkg hxempirical.integrity {
    capture quietly confirm file `"`install_target'/`required'"'
    if _rc {
        sysdir set PERSONAL `"`original_personal'"'
        cd `"`original_pwd'"'
        display as error "HX_INSTALLER_TEST_FAIL rollback lost `required'"
        exit 601
    }
}
tempname rollback_profile
file open `rollback_profile' using `"`test_profile'"', read text
local rollback_begin_count 0
file read `rollback_profile' line
while r(eof) == 0 {
    if trim(`"`line'"') == `"`begin'"' local ++rollback_begin_count
    file read `rollback_profile' line
}
file close `rollback_profile'
if `rollback_begin_count' != 1 {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL rollback changed profile"
    exit 459
}
display as result "HX_INSTALLER_UNINSTALL_ROLLBACK_OK"

/* A later deletion failure exercises restoration after the JAR and several
   earlier files have already been removed. */
global HXEI_TEST_FAIL_FILE "hxhistory.ado"
capture noisily do `"`installer'"' uninstall `"`repository'"'
local mid_uninstall_rc = _rc
macro drop HXEI_TEST_FAIL_FILE
if `mid_uninstall_rc' == 0 {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL simulated mid-uninstall failure was ignored"
    exit 459
}
foreach required in hxempirical.ado hxhistory.ado hxworkbench.jar hxinstaller.ado hxempirical.pkg hxempirical.integrity {
    capture quietly confirm file `"`install_target'/`required'"'
    if _rc {
        sysdir set PERSONAL `"`original_personal'"'
        cd `"`original_pwd'"'
        display as error "HX_INSTALLER_TEST_FAIL mid-uninstall rollback lost `required'"
        exit 601
    }
}
display as result "HX_INSTALLER_MID_UNINSTALL_ROLLBACK_OK"

/* Uninstall uses the local manifest and removes the managed menu block. */
capture noisily do `"`installer'"' uninstall `"`repository'"'
local uninstall_rc = _rc
if `uninstall_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL uninstall r(`uninstall_rc')"
    exit `uninstall_rc'
}
capture quietly confirm file `"`install_target'/hxempirical.ado"'
if !_rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL hxempirical.ado remains"
    exit 602
}
capture quietly confirm file `"`install_target'/hxworkbench.jar"'
if !_rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL hxworkbench.jar remains"
    exit 602
}
capture quietly confirm file `"`install_target'/hxinstaller.ado"'
if !_rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL hxinstaller.ado remains"
    exit 602
}
capture quietly confirm file `"`install_target'/hx_user_keep.do"'
if _rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_TEST_FAIL uninstall removed user sentinel"
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
capture quietly erase `"`install_target'/hx_user_keep.do"'
capture quietly erase `"`test_personal'/profile.before_hxempirical.do"'
capture quietly rmdir `"`test_personal'"'
capture quietly erase `"`test_cwd'/hxinstaller.ado"'
capture quietly erase `"`test_cwd'/hxsetup.ado"'
capture quietly erase `"`test_cwd'/hxmenu.ado"'
capture quietly rmdir `"`test_cwd'"'

display as result "HX_INSTALLER_CWD_SHADOW_OK"
display as result "HX_INSTALLER_LIFECYCLE_OK"
