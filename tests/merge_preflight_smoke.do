version 17.0
clear all
set more off
args repository
adopath ++ `"`repository'"'
set obs 20
generate id = _n
generate y = id + sin(id)
generate x = id^2
tempfile other
preserve
keep id
generate z = id*2
save `other'
restore
regress y x
matrix original = e(b)
replace id = 1 in 2
capture noisily hxexecute, command(`"merge 1:1 id using "`other'""')
assert _rc != 0
assert _N == 20
assert id[2] == 1
assert mreldif(e(b),original) == 0
capture confirm variable z
assert _rc != 0
replace id = . in 2
capture noisily hxexecute, command(`"merge m:1 id using "`other'""')
assert _rc == 459
assert missing(id[2])
replace id = 2 in 2
hxexecute, command(`"merge 1:1 id using "`other'""')
assert _merge == 3
assert z == id*2
quietly frames dir
local count : word count `r(frames)'
assert `count' == 1
display as result "HX_MERGE_PREFLIGHT_SMOKE_OK"
