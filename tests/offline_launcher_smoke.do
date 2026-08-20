version 17.0
clear all
set more off

/* Run from the repository root, or pass the repository root as argument 1. */
args repository
if `"`repository'"' == "" local repository `"`c(pwd)'"'
local repository : subinstr local repository "\" "/", all
local archive `"`repository'/hxempirical-release.zip"'

foreach required in `"`archive'"' {
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
local install_target `"`test_personal'/h"'
local extracted `"`offline_base'_extracted"'
capture quietly mkdir `"`extracted'"'
capture quietly cd `"`extracted'"'
if _rc {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_OFFLINE_LAUNCHER_TEST_FAIL cannot create extraction directory"
    exit 603
}
capture quietly unzipfile `"`archive'"', replace
local unzip_rc = _rc
cd `"`original_pwd'"'
if `unzip_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    display as error "HX_OFFLINE_LAUNCHER_TEST_FAIL unzip r(`unzip_rc')"
    exit `unzip_rc'
}

local launcher `"`extracted'/hxinstall_offline.do"'
local manifest `"`extracted'/hxempirical.pkg"'
local installer `"`extracted'/hxinstall.do"'
foreach required in `"`launcher'"' `"`manifest'"' `"`installer'"' ///
    `"`extracted'/hxinstaller.ado"' `"`extracted'/hxempirical-offline.index"' {
    capture quietly confirm file `"`required'"'
    if _rc {
        sysdir set PERSONAL `"`original_personal'"'
        display as error "HX_OFFLINE_LAUNCHER_TEST_FAIL extracted package missing `required'"
        exit 601
    }
}
/* The real browser ZIP deliberately has no GitHub distribution index.  Its
   separate offline integrity index makes the extracted package self-contained. */
capture quietly confirm file `"`extracted'/hxempirical-release.index"'
if !_rc {
    sysdir set PERSONAL `"`original_personal'"'
    display as error "HX_OFFLINE_LAUNCHER_TEST_FAIL fixture is repository-shaped, not browser-ZIP-shaped"
    exit 459
}

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

capture quietly confirm file `"`install_target'/hxempirical.ado"'
local core_rc = _rc
capture quietly confirm file `"`install_target'/hxworkbench.jar"'
local jar_rc = _rc
capture quietly confirm file `"`install_target'/hxinstaller.ado"'
local installer_core_rc = _rc
if `core_rc' | `jar_rc' | `installer_core_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_OFFLINE_LAUNCHER_TEST_FAIL incomplete installation"
    exit 601
}

capture noisily do `"`installer'"' uninstall `"`extracted'"'
local uninstall_rc = _rc
sysdir set PERSONAL `"`original_personal'"'
cd `"`original_pwd'"'
if `uninstall_rc' {
    display as error "HX_OFFLINE_LAUNCHER_TEST_FAIL uninstall r(`uninstall_rc')"
    exit `uninstall_rc'
}

/* Corrupt one extracted managed file.  The offline index must reject the
   package before any managed file reaches a fresh PERSONAL directory. */
tempname damaged_source
file open `damaged_source' using `"`extracted'/hxhistory.ado"', write text append
file write `damaged_source' "* simulated damaged offline source" _n
file close `damaged_source'
sysdir set PERSONAL `"`test_personal'/"'
cd `"`c(tmpdir)'"'
capture noisily do `"`launcher'"' `"`manifest'"'
local damaged_rc = _rc
capture quietly confirm file `"`install_target'/hxempirical.ado"'
local damaged_partial_install = (_rc == 0)
sysdir set PERSONAL `"`original_personal'"'
cd `"`original_pwd'"'
if `damaged_rc' == 0 | `damaged_partial_install' {
    display as error "HX_OFFLINE_LAUNCHER_TEST_FAIL damaged offline package was accepted"
    exit 459
}
display as result "HX_OFFLINE_INTEGRITY_REJECTION_OK"

capture quietly erase `"`test_personal'/profile.do"'
capture quietly erase `"`test_personal'/profile.before_hxempirical.do"'
capture quietly rmdir `"`test_personal'"'

/* Remove the isolated extraction fixture after all assertions. */
local extracted_java : subinstr local extracted "\" "\\", all
capture java: java.nio.file.Files.walk(java.nio.file.Paths.get("`extracted_java'")).sorted(java.util.Comparator.reverseOrder()).forEach(p -> { try { java.nio.file.Files.deleteIfExists(p); } catch (java.io.IOException e) { throw new RuntimeException(e); } })
display as result "HX_OFFLINE_LAUNCHER_OK"
