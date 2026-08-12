{smcl}
{* *! version 1.0.1  12aug2026}{...}
{vieweralsosee "hxtoolbox" "help hxtoolbox"}{...}
{title:Title}

{phang}
{bf:hxempirical} {hline 2} open and manage the HX empirical workbench

{title:Syntax}

{p 8 16 2}{cmd:hxempirical} [{cmd:, classic}]
{p 8 16 2}{cmd:hxempirical about}
{p 8 16 2}{cmd:hxempirical doctor}
{p 8 16 2}{cmd:hxempirical menu}
{p 8 16 2}{cmd:hxempirical menu persist}
{p 8 16 2}{cmd:hxempirical menu remove}
{p 8 16 2}{cmd:hxempirical install} {it:command}
{p 8 16 2}{cmd:hxempirical update}

{title:Description}

{pstd}
{cmd:hxempirical} opens one workbench containing command navigation, command
settings, a live command preview, and a read-only view of the dataset currently
in Stata memory. Commands run in Stata itself. The complete command is added to
Stata's History window before execution.

{pstd}
The start page is a launcher rather than a full function wall. A large task
search sits at the top, six common jobs stay visible, current-data status and up
to three recent commands appear on the right, and the full function catalog is
collapsed until the user explicitly expands it. Selecting a method opens a
compact command-choice page. Selecting a command then enters a focused workspace
and hides the broader navigation. Every command page shows its complete path and
simplest example above the settings. Advanced free-text options stay collapsed
until requested; cluster variables appear only when the Cluster standard-error
choice is active.

{pstd}
Each command-choice row explains the Chinese name, purpose, suitable data,
simplest example, and the main difference from related commands. Methods with
one to four commands use a compact single-column list. Breadcrumbs and the
left-side back action return to the previous method level; the global
{bf:回到开始} action remains available at the top right. Search covers Stata
names, Chinese purposes, suitable-data descriptions, examples, and workflows.

{pstd}
The right side has three stable tabs: {bf:数据}, {bf:结果}, and {bf:运行}.
The content inside {bf:结果} changes with the active task. Missing-value,
conversion, graph, DID, and OneClick pages therefore expose only their relevant
outputs instead of a permanent row of unrelated tabs.

{pstd}
The workbench uses one resolver/parser/schema/renderer pipeline for official and
community-contributed commands. Syntax, help, examples, ado source, and an
official dialog are used when available. Unresolved syntax remains available in
the advanced-options field.


{title:Ordinary linear regression workspace}

{pstd}
The start page is task-first and keeps only six common jobs visible. A large
search field accepts command names, analysis keywords, and short task phrases;
common multi-concept requests such as enterprise-and-year fixed effects or
control-variable robustness are routed to the relevant method. The page also
shows the current Stata dataset status. {bf:继续工作} stores the last three model
specifications locally and restores their parameters without automatically
running them. The complete catalog is available through {bf:展开全部功能}. Methods
that contain only one command open that command directly, avoiding an extra
chooser click. The full regression category remains available under
{bf:回归模型}; it separates ordinary OLS, fixed-effects linear regression, robust
and special linear regression, quantile regression, time-series linear
regression, panel models, binary outcomes, count models, and instrumental
variables.

{pstd}
{bf:回归模型 > 普通线性回归 > regress} uses a dedicated workspace rather than
a generic syntax form. It separates the dependent variable Y, the core
explanatory variable X, and control variables. Beginner-facing builders add
categorical terms, interactions, and lags without requiring users to type
{cmd:i.}, {cmd:c.}, {cmd:##}, or {cmd:L.}. The page also exposes
{cmd:if}/{cmd:in}, f/a/p/i weights, conventional/robust/clustered standard
errors, {cmd:noconstant}, standardized {cmd:beta}, and the confidence level
while keeping free-form Stata syntax in an advanced section. The
right inspector can be hidden so the settings workspace can use the full width.

{pstd}
After a successful {cmd:regress}, the {bf:结果} tab groups common official
postestimation actions by purpose: {cmd:estat vif}, {cmd:estat hettest},
{cmd:estat imtest, white}, {cmd:estat ovtest}, {cmd:estat ic}, fitted values,
residuals, standardized and studentized residuals, Cook's distance, leverage,
and coefficient tests. These buttons execute native Stata commands through a
guarded runner and write those native commands to History. When the fitted
{cmd:regress} used robust or clustered VCE, the workbench disables influence
statistics that Stata only provides with the default OLS VCE; fitted values and
ordinary residuals remain available. For a no-constant model, the VIF action
automatically uses {cmd:estat vif, uncentered}.

{pstd}
The built-in linear-regression catalog also exposes {cmd:areg}, {cmd:rreg},
{cmd:cnsreg}, {cmd:vwls}, {cmd:eivreg}, {cmd:qreg}, {cmd:newey}, and
{cmd:prais}; {cmd:reghdfe} remains an optional community command. The
{cmd:newey}/{cmd:prais} pages link directly to a beginner-facing {cmd:tsset}
page instead of showing misleading panel-only fields. Other Stata commands can
still be opened by typing their command name in search, where the resolver
builds a page from the installed command's syntax and help.

{title:Command dock and run monitor}

{pstd}
The command-settings page ends with a fixed command dock. It shows the complete
editable Stata command in a monospaced field, provides one primary run action,
and reports the current run state and elapsed time without scrolling away.

{pstd}
The right-side {bf:运行} tab records the command, start and end times,
elapsed time, Stata return code, History-write status, processor status, data
shape before and after the run, and available estimation results such as
{cmd:e(N)} and {cmd:e(r2)}. The detailed section contains a timestamped log and
run queue. Ordinary Stata estimation commands use an indeterminate progress
state because their internal percentage is unavailable. Batch file conversion
uses the actual number of completed files and displays a real percentage.

{title:Installation}

{pstd}
Install from a package server with

{phang2}{cmd:. net install hxempirical, from("release_location")}

{pstd}
Then open it with

{phang2}{cmd:. hxempirical}

{pstd}
Opening {cmd:hxempirical} never edits PERSONAL/profile.do. During the current
Stata session it can add exactly one visible entry:

{phang2}{bf:User > 我的实证工具箱}

{pstd}
Use {cmd:hxempirical menu} for a session-only menu entry. If the user explicitly
wants the entry at every Stata startup, run {cmd:hxempirical menu persist}.
That command adds one HX-managed block to profile.do while preserving all
unrelated lines. Remove only that managed block with
{cmd:hxempirical menu remove}. hxempirical never uses {cmd:window menu clear}.

{title:Missing-value analysis}

{pstd}
Open {bf:数据 > 数据检查 > 缺失值分析}. The page supports all or selected
variables, one-way grouping, joint grouping, separate summaries for multiple
group variables, missing-count/rate filters, record drill-down, and four graph
views. It reads the complete current dataset and does not modify it. The native
{cmd:misstable summarize} check is written to Stata History.

{title:Convert files to DTA}

{pstd}
Open {bf:数据 > 导入与转换 > 转换为 DTA}. Select an Excel, CSV, TXT, or
TSV file and the page adapts its settings to the detected format. A read-only
preview reports observations, variables, inferred types, empty columns, mixed
numeric/text columns, duplicate headers, and columns that may lose leading
zeroes. For CSV/TXT, UTF-8, GB18030, and Windows-1252 are supported; automatic
mode probes the file before import and writes the resolved encoding into the
actual {cmd:import delimited} command. Potential code columns such as 000001 are
kept as strings by default. For legacy {cmd:.xls}, hxempirical does not invent a
{cmd:Sheet1} name when the workbook sheet list cannot be inspected; leaving the
sheet field at {bf:(默认工作表)} lets Stata use its default sheet.

{pstd}
Single-file mode asks before replacing an existing DTA. Batch mode converts a
folder of selected file types, can skip existing outputs, and reports every
success, failure, and skipped file. Batch read settings are frozen when the run
starts, so changing the UI cannot silently change later files. A {bf:停止批量任务}
button stops before the next file and keeps all files already completed. Imports
and saves run in a temporary Stata frame, leaving the dataset already in memory
unchanged unless {bf:load after conversion} is selected. The source
Excel/CSV/TXT file is never modified. The actual {cmd:import} and {cmd:save}
commands are written to Stata History.

{title:Optional commands}

{pstd}
{cmd:reghdfe}, {cmd:winsor2}, {cmd:ivreghdfe}, {cmd:ppmlhdfe},
{cmd:oneclick}, {cmd:oneclick_robustness}, {cmd:coefplot}, and {cmd:event_plot} are optional.
The package checks for optional commands only when needed. Commands with a
verified SSC source (including {cmd:oneclick} and {cmd:event_plot}) can be
installed after user confirmation. {cmd:oneclick_robustness} is detected when
present but is not downloaded from an unverified source. Nothing is downloaded
merely by installing {cmd:hxempirical}.

{phang2}{cmd:. hxempirical doctor}
{phang2}{cmd:. hxempirical install reghdfe}

{title:Compatibility}

{pstd}
Minimum version: Stata 17. The Java workbench is compiled for Java 11 bytecode
and uses Stata's bundled Java/SFI interface. It contains no COM Automation,
native C plugin, drive-letter path, or platform-specific font. If Java cannot
start, {cmd:hxempirical, classic} opens the included Stata dialog.

{title:Update and uninstall}

{phang2}{cmd:. hxempirical update}
{phang2}{cmd:. hxempirical menu remove}
{phang2}{cmd:. ado uninstall hxempirical}

{pstd}
Run {cmd:hxempirical menu remove} before uninstalling if a persistent startup menu was enabled. Restart Stata after an update or uninstall so the loaded Java class is
released.

{title:Examples}

{phang2}{cmd:. sysuse auto, clear}
{phang2}{cmd:. hxempirical}
{phang2}{cmd:. hxempirical about}
{phang2}{cmd:. hxempirical doctor}

{title:Graphs and OneClick}

{pstd}
The {bf:图形} category provides distribution, relationship, grouped-trend,
postestimation, and DID/event-study graph building blocks. The right-side graph
preview updates with selected variables; the final graph is still produced by
Stata's native graph system and the complete command is retained in History.

{pstd}
{bf:DID 专区 > DID分步构建} is designed for a common policy timing setup and keeps calendar time, treatment group,
{cmd:post}, relative {cmd:event_time}, and the regression-safe {cmd:event_code}
separate. The page shows only the fields required by the current step. It can
generate {cmd:post}, {cmd:did}, and {cmd:event_time}; run
{cmd:hxdidencode event_time, generate(event_code) base(-1)} to convert negative
relative periods into a nonnegative factor-variable code while preserving the
chosen base period; build {cmd:i.treat##i.post}; build an event-study interaction
{cmd:i.treat##i.event_code}; and automatically build the pre-policy {cmd:testparm}
joint test from the actual last event-study {cmd:e(b)} and {cmd:e(sample)}. The
workbench records the event-study result after a successful run and refuses to
test if another estimation result has replaced it. Before estimation, treat/post
are checked as numeric 0/1 variables on the requested regression sample, including
{cmd:if} restrictions and complete-case requirements, and the selected event-study
base period must exist in the data. This avoids feeding negative relative-time
values directly to Stata factor-variable notation. Staggered-treatment DID should
use a method designed for varying treatment dates.

{pstd}
The {bf:OneClick 专区} calls the author's real external {cmd:oneclick} command;
hxempirical does not substitute its own control-combination algorithm. The GUI
translates Y, focal X, candidate controls, significance level, estimator, fixed
effects, and standard-error choices into the external command syntax. The exact
{cmd:oneclick ...} line displayed in the command dock is the line submitted to
Stata and written to History.

{pstd}
After the external command finishes, hxempirical reads the generated
{cmd:subset.dta} into a temporary uniquely named frame and displays it under Results. The
external command is run inside a unique temporary working directory, so a user
file named {cmd:subset.dta} in the active project directory is never renamed,
erased, or overwritten. The dataset already in Stata memory is not replaced. A selected result row can be sent to
the corresponding ordinary regression page for review without automatic
execution. {cmd:oneclick} can be installed from SSC on request.
{cmd:oneclick_robustness} is also treated as an external command; hxempirical
does not invent an unverified download source for it.

{pstd}
OneClick output is a model-sensitivity and robustness aid. Candidate controls
should be chosen from theory, prior literature, and the identification design.
It does not replace a prespecified main model or causal identification strategy.

{title:Author}

{pstd}
HX empirical workbench, package version 1.0.1.
