# HX Empirical Workbench (`hxempirical`)

## 当前版本与下载

**当前发布版本：1.5.4**<br>
**支持：Stata 17 及以上版本**<br>
**上次修改时间：2026-08-15 18:44（UTC+8）**

### 1.5.4 数据表运算与外部命令

- 左侧“历史”入口改为“已下载外部命令”，动态显示工具箱已登记且当前 Stata 实际能够找到的第三方/外部命令；最近任务仍保留在首页。
- “当前数据”加入类似 WPS/Excel 的公式栏：双击单元格可直接改值，以 `=` 开头可按 Stata 表达式计算；支持写入单元格、整列计算和新建计算列。
- 所有数据写入仍由 Stata `replace` / `generate` 执行，并写入 Stata History，避免 Java 表格形成第二份数据状态。
- 当前实现聚焦实证数据运算，不宣称完整复刻 Excel；排序、复杂多单元格粘贴和撤销栈可在后续版本继续扩展。

### 1.5.3 目录显示修复

- 修复“数据 / 统计 / 图形”等一级目录进入后内容为空的问题：分类页与命令页现在统一渲染到实际可见的目录容器。
- 分类导航以随 JAR 发布的本地目录为稳定基线，并合并 Stata 侧 `hxregistry` 的新增项；即使运行时 characteristic 暂时不可用，也不会把整个目录清空。
- 分类页隐藏仅适用于命令列表的“全部 / 常用 / 官方 / 外部扩展 / 进阶”筛选，进入具体方法后再显示。

### 安装或更新

#### 方法 A：在线安装

网络能够稳定访问 GitHub Pages 时，在 **Stata 17 或更高版本**的命令窗口运行：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"
```

这一条命令同时负责安装、检查更新和修复缺失文件。公开的 `hxinstall.do` 只有一个很短的启动段，复杂安装逻辑在后台 `.ado` 中执行，Results 不再逐行显示几百行安装器核心源码：

- 第一次运行：优先安装到当前用户的 `PERSONAL`；该目录不可写时自动尝试 `PLUS/h`；
- 已安装且版本相同、文件完整：立即提示“已是最新版本”，不下载完整发布包；
- 发现新版：备份现有版本后安全更新；
- 版本相同但文件缺失：自动执行修复安装；
- 安装、更新和修复完成后都会尝试建立唯一的 **用户（User） > 我的实证工具箱** 菜单入口；若 `PERSONAL/profile.do` 不可写，核心安装仍然成功，重启后直接运行 `hxempirical`。

需要强制覆盖全部文件时运行：

```stata
hxempirical repair
```

确实需要下载完整发布包时，安装器才会取得带进度的文本分段。每段网络等待上限为 20 秒，全部校验通过后才写入最终选定的持久 ado 目录。

Stata 在一次 HTTPS 传输期间可能短暂显示“正忙”。请观察 Results 中的 `正在取得发布包：#/N`，让当前分段返回。需要中断时使用 Stata 工具栏的红色 **Break/停止** 按钮；安装器会保留原有安装。

#### 方法 B：浏览器离线安装（校园网、代理和卡顿环境推荐）

1. 用浏览器下载 [hxempirical 完整离线包](https://xiaowang5105.github.io/hxempirical/hxempirical-release.zip)。
2. 完整解压 ZIP。
3. 在 Stata 选择 **文件（File） > 执行 do 文件（Do...）**，打开解压目录中的 `hxinstall_offline.do`。
4. 文件选择框出现后，选择同一目录中的 `hxempirical.pkg`。
5. 安装完成后重新启动 Stata。

也可以直接运行解压后的启动文件；它会让你选择 `hxempirical.pkg`：

```stata
do "D:/你的解压目录/hxinstall_offline.do"
```

离线安装全过程从解压目录读取文件，不再由 Stata 访问 GitHub。以后更新时下载新的 ZIP 并重复相同步骤即可。

完成后重启 Stata，验证并启动：

```stata
which hxempirical
hxempirical about
hxempirical doctor
hxempirical
```

正常诊断应显示：

```text
[核心组件：正常] 11/11
```

`reghdfe`、`winsor2`、`oneclick`、`coefplot` 等属于可选扩展。它们未安装时，Stata 官方命令、数据处理和核心工作台仍可使用；进入对应功能并点击运行时，程序再询问是否安装。

安装器先完整取得并校验发布包，再统一写入正式目录；任何写入步骤失败都会恢复原有文件。Windows 和 macOS 使用相同的在线入口和离线包。

安装位置优先使用 `PERSONAL`。如果 `PERSONAL` 因权限策略不可写，安装器会自动尝试 Stata 已搜索的 `PLUS/h`；核心安装不再因为 `PERSONAL/profile.do` 权限异常直接失败。回退到 `PLUS/h` 时不会强行改写 `profile.do`，启动工具箱可直接运行 `hxempirical`。

### 给朋友安装时只需要这四步

1. 关闭已经打开的“我的实证工具箱”窗口。
2. 网络稳定时粘贴在线安装命令；校园网、代理或曾经卡顿时使用浏览器离线包。
3. 安装完成后重启 Stata。
4. 优先从 **用户（User） > 我的实证工具箱** 打开；如果安装器提示菜单未持久化，则在 Stata 中直接运行 `hxempirical`。遇到问题时运行下面三条命令并保存输出：

```stata
hxempirical about
hxempirical doctor
sysdir
```

GitHub 的 JAR/ZIP 二进制传输在部分学校网络、代理、杀毒软件和 Stata TLS 环境中可能被延迟。在线安装器使用分段文本发布包并设置传输上限；浏览器离线包是此类环境下的稳定入口。请勿把 GitHub Raw 地址用于 `net install`。

详细的更新、卸载和故障排查见 [INSTALL.md](INSTALL.md)。

### 传统包管理方式（高级）

GitHub Pages 仍支持：

```stata
net install hxempirical, from("https://xiaowang5105.github.io/hxempirical/") replace force
```

但推荐使用上面的 `hxinstall.do` 安装器，因为它会进行发布包校验、失败回滚和目录回退。

## 主要功能

`hxempirical` 是一个运行在 Stata 内的 Java 单窗口实证工作台，目标是把常见实证任务从“记命令、查帮助、反复改代码”转换成“选择任务、设置参数、检查命令、运行 Stata”。

当前主要包括：

- 数据导入与转换、缺失检查、变量和样本处理、合并追加、面板/时间结构；
- 描述统计、假设检验、线性/非线性模型、面板模型、时间序列、生存分析、调查数据等 Stata 分类；
- `regress`、`xtreg`、`reghdfe`、`ivregress`、`ivreghdfe`、`ppmlhdfe` 等常用估计命令；
- DID、事件研究、平行趋势等工作流；
- OneClick 控制变量组合筛选；
- 图形、结果、日志、变量摘要和当前数据联动；
- 当前数据的公式栏、直接单元格编辑、整列计算和新建计算列；
- 已下载外部命令的动态检测与集中入口；
- 左侧代码/命令预览与 Stata History 联动，保证分析可复现。

## 设计原则

1. **Stata 是唯一数据源。** Java 界面中的数据修改最终都执行为可见的 Stata 命令，不维护第二份隐藏数据。
2. **先常用、后长尾。** 高频命令优先展示，长尾命令仍可以搜索和进入。
3. **单页设置、命令可复现。** 参数选择会生成完整 Stata 命令，运行后写入 History。
4. **第三方命令不重写算法。** 对 `reghdfe`、`ppmlhdfe`、`oneclick` 等调用原命令，只在界面层降低使用门槛。
5. **正式功能与测试逻辑分离。** 预览、自查脚本不进入正式发布包。
