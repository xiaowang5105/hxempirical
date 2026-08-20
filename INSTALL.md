# hxempirical 安装、更新与排错

## 先选安装方式

| 当前环境 | 推荐方式 |
|---|---|
| Stata 可以稳定访问 GitHub Pages | 在线安装 |
| 校园网、单位代理、网络审查、杀毒软件拦截，或 Stata 曾长时间显示“正忙” | 浏览器离线安装 |
| 需要给朋友批量安装 | 下载一次离线包，再分别安装 |

两种方式最终安装的是同一份发布包，统一写入 Stata 标准首字母 ado 目录：优先 `PERSONAL/h`；如果该目录不可写，会自动回退到 `PLUS/h`。首次安装、检查更新和自动修复使用同一条命令。

## 1.5.13 安装路径与遮挡防护

全新安装统一使用 `PERSONAL/h`（或 `PLUS/h`）。`hxworkbench.jar`、`.dlg` 和内置 `.dta` 均作为系统安装文件处理。检测到 Stata 当前仍从旧版 `PERSONAL` 根目录加载 HX 时，事务式安装器会在原位置完成安全更新，防止新旧目录互相遮挡；这类旧布局可在确认新版正常后再按维护说明迁移。

**不要使用 `net install` 进行日常安装或更新。** Stata 自带包管理器可能把新版本写入 `PLUS/h`，而已有的 `PERSONAL/h` 旧副本在 adopath 中优先级更高，结果会出现“installation complete，但 `hxempirical about` 仍是旧版”。遇到历史双版本时运行 `hxempirical doctor`，再执行 `hxempirical repair`；事务式安装器会验证 Stata 当前实际解析到的路径和版本。

## 方法 A：在线安装

在 **Stata 17 或更高版本**的命令窗口运行：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"
```

公开的 `hxinstall.do` 是短启动器，真正的事务式安装逻辑由 `hxinstaller.ado` 执行。Results 只回显短启动段和用户需要的状态，不再逐行回显安装器核心源码。

安装器依次执行：

1. 取得短安装核心，检查 Stata 版本，并选择可写的持久 ado 目录（优先 `PERSONAL/h`，必要时 `PLUS/h`；已在使用的旧根目录安装会原位安全更新）；
2. 读取 `hxempirical.pkg`，比较当前版本与最新版本；
3. 版本相同且文件完整时直接结束；
4. 需要安装、更新或修复时才下载 Base64 文本分段；
5. 使用 Stata 17 自带 Java 还原完整发布包；
6. 校验清单中的全部文件；
7. 备份已有版本并统一写入；
8. 尝试建立唯一的 **用户（User） > 我的实证工具箱** 菜单入口；菜单持久化失败不会撤销已经成功的核心安装。

已经是最新版本时，Results 显示：

```text
当前版本：1.5.13
最新版本：1.5.13
已是最新版本，无需更新。
```

Results 窗口会持续显示：

```text
正在取得发布包：1/N（每段网络等待上限 20 秒）
正在取得发布包：2/N（每段网络等待上限 20 秒）
...
```

一次 HTTPS 传输期间，Stata 可能短暂显示“正忙”。当前分段最长等待 20 秒，随后会继续或给出明确错误。需要主动停止时，点击 Stata 工具栏的红色 **Break/停止** 按钮。安装器在取得并校验完整发布包之前不会改动已有安装。

## 方法 B：浏览器离线安装

此方法让浏览器负责下载，Stata 只读取本地文件。

1. 下载 [hxempirical-release.zip](https://xiaowang5105.github.io/hxempirical/hxempirical-release.zip)。
2. 右键 ZIP 并完整解压到普通文件夹。
3. 打开 Stata，选择 **文件（File） > 执行 do 文件（Do...）**。
4. 选择解压目录中的 `hxinstall_offline.do`。
5. 文件选择框出现后，选择同一目录中的 `hxempirical.pkg`。
6. 等待“hxempirical 安装完成”或“hxempirical 更新完成”，然后重启 Stata。

也可以在 Stata 中直接运行：

```stata
do "D:/你的解压目录/hxinstall_offline.do"
```

启动文件会弹出文件选择框。路径中可以有中文和空格。请选择解压目录里的 `hxempirical.pkg`。

离线安装包包含：

- 全部 `.ado`、`.sthlp`、`.dlg`、测试数据和 Java 工作台；
- `hxempirical.pkg` 完整清单；
- `hxempirical-offline.index` 逐文件长度与 checksum 索引；
- 在线/本地共用的事务式安装器；
- 离线启动文件和本说明。

离线启动器会先核对清单版本、文件名安全性，以及每个受管文件的长度和 checksum。任一文件损坏、缺失或大小写冲突都会在写入 `PERSONAL` 前停止。

原 ZIP 和解压目录不会被修改。更新完成后可以自行保留或删除下载文件。

## 安装完成后的验证

重新启动 Stata，然后运行：

```stata
which hxempirical
hxempirical about
hxempirical doctor
hxempirical
```

核心诊断应显示：

```text
[核心组件：正常] 11/11
[安装路径：正常]
```

如果同时存在 `PERSONAL/h` 和 `PLUS/h` 且版本不同，doctor 会列出当前生效路径和两个版本，并提示运行 `hxempirical repair`。

`reghdfe`、`winsor2`、`ivreghdfe`、`ppmlhdfe`、`oneclick`、`oneclick_robustness`、`coefplot`、`event_plot` 等属于外部扩展。它们缺失时，核心工作台和 Stata 官方命令仍然可用。hxempirical 只检测和展示，不负责安装；需要什么命令请按作者发布说明自行安装，安装完成后重新进入“外部命令”扫描。

## 更新

先关闭“我的实证工具箱”窗口，再选择一种方式：

在线更新：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"
```

离线更新：下载最新 ZIP，解压后重新运行 `hxinstall_offline.do`。

安装器通过 `PERSONAL` 中的本地清单和 `hxempirical.integrity` 识别已有版本。版本相同、完整性记录版本一致，并且每个受管文件的长度和 checksum 均吻合时才立即结束；文件缺失或内容变化会自动进入修复。存在新版时先备份再统一替换，写入失败时恢复原版本。遇到 `hxworkbench.jar` 正在使用或 `r(602)` 时，请关闭所有 Stata 窗口，重新打开 Stata 后先执行更新。

发布索引还记录 `hxempirical.pkg` 和发布 ZIP 的 SHA256，供构建流程与浏览器下载审计。Stata 端实际验证 pkg 与 ZIP 各自的字节数和 POSIX checksum，不会把未在 Stata 中计算的 SHA256 报告为验证成功。

## 修复安装

普通安装命令会自动发现缺失文件、长度变化和 checksum 不一致。需要无条件重新覆盖全部受管文件时运行：

```stata
hxempirical repair
```

也可以直接运行在线入口：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do" repair
```

## 卸载

已安装时运行：

```stata
hxempirical uninstall
```

也可以运行在线卸载器：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do" uninstall
```

卸载器先备份受管文件、安装清单、完整性记录和安装器，再优先删除容易被锁定的 `hxworkbench.jar`。任何删除或 `profile.do` 清理失败都会从备份恢复，并保留可重试入口；成功完成全部步骤后才报告卸载完成。完成后重新启动 Stata。

`hxempirical menu persist` 会先检查 `profile.do` 中 HX 标记是否成对且没有嵌套。发现孤立标记、缺失结束标记或备份失败时会停止，原 `profile.do` 保持不变。

如果电脑以前多次使用 `net install` 安装过旧版本，`PLUS` 目录可能还保留旧登记。按提示运行：

```stata
ado dir hxempirical
ado uninstall [编号]
```

## Stata 显示“正忙”时怎么处理

### 看到 `正在取得发布包：#/N`

安装器正在下载当前文本分段。每段最长等待 20 秒。让当前分段返回，或点击红色 **Break/停止**。完成中断后直接改用浏览器离线安装。

### 运行在线命令后很久没有任何安装器文字

Stata 正在下载最前面的 `hxinstall.do`，此时安装器代码尚未开始执行。点击红色 **Break/停止**，然后使用浏览器离线包。这通常代表当前网络对 Stata 的 GitHub HTTPS 请求有限制。

### Stata 无法恢复，只能从任务管理器关闭

重新打开 Stata后直接使用浏览器离线包。安装器在完整发布包校验前不会写入正式目录，因此未完成的在线下载不会形成半套新安装。随后运行：

```stata
which hxempirical
sysdir
```

如果 `which hxempirical` 显示已有版本，再用离线包执行一次更新即可。

## 网络诊断

浏览器分别打开：

- [安装入口](https://xiaowang5105.github.io/hxempirical/hxinstall.do)
- [发布清单](https://xiaowang5105.github.io/hxempirical/hxempirical.pkg)
- [完整离线包](https://xiaowang5105.github.io/hxempirical/hxempirical-release.zip)

浏览器能打开、Stata 持续超时时，直接使用离线安装。浏览器也无法打开时，请更换网络，或让朋友把 ZIP 文件传给你。

需要提交问题时，在 Stata 运行并保存输出：

```stata
about
sysdir
adopath
which hxempirical
```

已经成功装入核心命令时，再运行：

```stata
hxempirical about
hxempirical doctor
```

## macOS 与干净用户目录验证

Windows 和 macOS 使用同一发布包。安装器会创建缺失的 `PERSONAL` 目录并验证写权限；若 `PERSONAL` 不可写，会继续检查 `PLUS/h`。只有两个持久 ado 位置都不可写时才返回 `r(603)`。使用 `PLUS/h` 时，安装器会静默尝试菜单持久化；若 `PERSONAL/profile.do` 仍不可写，只跳过持久菜单，不影响 `hxempirical` 命令本身。

维护者从仓库根目录运行：

```stata
do "tests/cross_platform_core_smoke.do"
do "tests/installer_lifecycle_smoke.do"
do "tests/installer_shadowing_smoke.do"
do "tests/installer_integrity_smoke.do"
do "tests/offline_launcher_smoke.do"
do "tests/installer_output_smoke.do"
do "tests/hxsetup_profile_safety_smoke.do"
do "tests/workbench_real_stata_smoke.do" "仓库根目录"
```

Windows 维护者也可以运行 `tools/run_stata_tests.ps1`；它逐项启动 Stata、设置超时并保留失败日志。前六项安装测试使用隔离的临时 `PERSONAL`，覆盖目录创建、核心/可选依赖诊断、菜单持久化、首次安装、同版本完整性快速退出、损坏文件自动修复、发布索引拒绝、核心源码不回显、真实离线 ZIP 和事务卸载。最后一项使用真实 Stata Java 运行时验证最终 JAR 与主要命令页面。

## `net install` 兼容入口（不推荐用于日常更新）

GitHub Pages 仍保留 Stata 包管理兼容入口：

```stata
net install hxempirical, from("https://xiaowang5105.github.io/hxempirical/") replace force
```

但 `net install` 的目标目录由 Stata 包管理器决定，可能写入 `PLUS/h`，无法保证覆盖 adopath 中优先级更高的 `PERSONAL/h` 旧副本。因此普通用户不要用它做日常安装/更新。标准入口始终是 `hxinstall.do`；若曾使用 `net install`，先运行 `hxempirical doctor`，发现双版本时运行 `hxempirical repair`。
