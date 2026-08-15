# hxempirical 安装、更新与排错

## 先选安装方式

| 当前环境 | 推荐方式 |
|---|---|
| Stata 可以稳定访问 GitHub Pages | 在线安装 |
| 校园网、单位代理、网络审查、杀毒软件拦截，或 Stata 曾长时间显示“正忙” | 浏览器离线安装 |
| 需要给朋友批量安装 | 下载一次离线包，再分别安装 |

两种方式最终安装的是同一份发布包，优先写入当前用户的 `PERSONAL` ado 目录；如果该目录不可写，会自动回退到 Stata 已搜索的 `PLUS/h`。首次安装、检查更新和自动修复使用同一条命令。

## 方法 A：在线安装

在 **Stata 17 或更高版本**的命令窗口运行：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"
```

公开的 `hxinstall.do` 是短启动器，真正的事务式安装逻辑由 `hxinstaller.ado` 执行。Results 只回显短启动段和用户需要的状态，不再逐行回显安装器核心源码。

安装器依次执行：

1. 取得短安装核心，检查 Stata 版本，并选择可写的持久 ado 目录（优先 `PERSONAL`，必要时 `PLUS/h`）；
2. 读取 `hxempirical.pkg`，比较当前版本与最新版本；
3. 版本相同且文件完整时直接结束；
4. 需要安装、更新或修复时才下载 Base64 文本分段；
5. 使用 Stata 17 自带 Java 还原完整发布包；
6. 校验清单中的全部文件；
7. 备份已有版本并统一写入；
8. 尝试建立唯一的 **用户（User） > 我的实证工具箱** 菜单入口；菜单持久化失败不会撤销已经成功的核心安装。

已经是最新版本时，Results 显示：

```text
当前版本：1.5.8
最新版本：1.5.8
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
- 在线/本地共用的事务式安装器；
- 离线启动文件和本说明。

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
```

`reghdfe`、`winsor2`、`ivreghdfe`、`ppmlhdfe`、`oneclick`、`oneclick_robustness`、`coefplot`、`event_plot` 是可选扩展。它们缺失时，核心工作台和 Stata 官方命令仍然可用。 `oneclick` 可由 hxempirical 从 SSC 按 `tuples → oneclick` 顺序安装；`oneclick_robustness` 当前没有配置经过验证的 SSC 自动安装源，需要按作者发布说明手动安装。

## 更新

先关闭“我的实证工具箱”窗口，再选择一种方式：

在线更新：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"
```

离线更新：下载最新 ZIP，解压后重新运行 `hxinstall_offline.do`。

安装器通过 `PERSONAL` 中的本地清单识别已有版本。版本相同且受管文件完整时立即结束；存在新版时先备份再统一替换；同版本缺少文件时自动修复。写入失败时会恢复原版本。遇到 `hxworkbench.jar` 正在使用或 `r(602)` 时，请关闭所有 Stata 窗口，重新打开 Stata 后先执行更新。

## 修复安装

普通安装命令已经能够自动发现缺失文件。需要无条件重新覆盖全部受管文件时运行：

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

卸载器会删除 `PERSONAL` 中由 hxempirical 清单管理的文件，并移除 HX 写入 `profile.do` 的菜单区块。完成后重新启动 Stata。

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
do "tests/offline_launcher_smoke.do"
do "tests/installer_output_smoke.do"
```

这些测试使用隔离的临时 `PERSONAL`，覆盖目录创建、核心/可选依赖诊断、菜单持久化、首次安装、同版本快速退出、自动修复、核心源码不回显、离线启动和卸载。

## 传统 Stata 包管理（高级）

GitHub Pages 仍支持：

```stata
net install hxempirical, from("https://xiaowang5105.github.io/hxempirical/") replace force
```

普通用户使用在线安装器或浏览器离线包。统一安装器负责更新、回滚、清理旧文件和菜单持久化。
