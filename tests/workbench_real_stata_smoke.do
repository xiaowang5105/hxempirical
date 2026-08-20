version 17.0
clear all
set more off

args repository
if `"`repository'"' == "" {
    display as error "repository path required"
    exit 198
}
adopath ++ `"`repository'"'
local hxjar `"`repository'/hxworkbench.jar"'

sysuse auto, clear
discard
javacall com.hexie.stata.HxWorkbench version, classpath(`"`hxjar'"')
assert _rc == 0
javacall com.hexie.stata.HxWorkbench selfTest, classpath(`"`hxjar'"')
assert _rc == 0
javacall com.hexie.stata.HxWorkbench workbenchSmokeTest, classpath(`"`hxjar'"')
assert _rc == 0
javacall com.hexie.stata.HxWorkbench launch, classpath(`"`hxjar'"')
assert _rc == 0
sleep 1200
javacall com.hexie.stata.HxWorkbench close, classpath(`"`hxjar'"')
assert _rc == 0

* OLS, postestimation, estimates, margins and a graph.
sysuse auto, clear
quietly regress price mpg weight
estimates store hx_ols
quietly margins, at(mpg=(20 30))
quietly regress price mpg weight
quietly estat hettest
quietly scatter price mpg, name(hx_smoke_graph, replace)
graph close hx_smoke_graph

* Instrumental variables.
quietly ivregress 2sls price weight (mpg = displacement)

* Panel model and optional reghdfe execution.
use `"`repository'/hx_nlswork.dta"', clear
quietly xtset idcode year
quietly xtreg ln_wage age tenure, fe
capture which reghdfe
if !_rc {
    quietly reghdfe ln_wage age tenure, absorb(idcode year)
    display as text "HX_REAL_STATA_REGHDFE_OK"
}
else display as text "HX_REAL_STATA_REGHDFE_PAGE_OK_EXTERNAL_NOT_INSTALLED"

* Difference-in-differences on disposable synthetic panel data.
clear
set obs 120
generate int id = ceil(_n/6)
bysort id: generate byte time = _n
generate byte treated = id <= 10 & time >= 4
generate double x = id/20 + time/10
generate double y = 2 + 0.8*treated + 0.4*x + sin(id + time)
quietly didregress (y x) (treated), group(id) time(time)

* Time-series model.
clear
set obs 120
generate int t = _n
tsset t
generate double x = cos(t/8)
generate double y = 0.5*x + sin(t/5) + t/100
quietly arima y x, arima(1,0,0)

* Survival model.
clear
set obs 100
generate double studytime = _n + 2
generate byte died = mod(_n, 3) == 0
generate double age = 25 + mod(_n, 45)
quietly stset studytime, failure(died)
quietly stcox age

* Merge.
tempfile hxmaster hxusing
clear
input byte id double x
1 10
2 20
3 30
end
save `hxmaster'
clear
input byte id double z
1 100
2 200
3 300
end
save `hxusing'
use `hxmaster', clear
quietly merge 1:1 id using `hxusing', nogen
assert _N == 3

* Reshape and collapse.
clear
input byte id double(y1 y2)
1 10 11
2 20 21
end
quietly reshape long y, i(id) j(year)
assert _N == 4
quietly collapse (mean) y, by(id)
assert _N == 2

display as result "HX_WORKBENCH_REAL_STATA_FULL_SMOKE_OK"
