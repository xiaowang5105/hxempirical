# 1.6.0 本地验证记录

## 2026-09-06 面板、IV 与编辑回归修订

- 面板向导及通用页面自动执行的 `xtset` 纳入项目日志；从未声明面板的初始快照导出并重跑，`xtreg` 系数差异小于 1e-12。
- 通过真实工作台控件捕获、序列化并恢复 IV 内生变量、工具变量及 GMM 估计方式，恢复生成的命令在 Stata 中执行成功。Java 项目测试同时验证旧 33/34 字段记录兼容。
- 公式栏与编辑器使用原值。小数显示格式、值标签、日期、扩展缺失值和带首尾空格的字符串均通过未修改提交测试；高精度数值与带引号字符串的实际写入也通过。
- 修复嵌套命令重复处理普通引号的问题；运行期间预览刷新及面板准备步骤的拒绝路径通过测试。
- 同一最终生产 JAR 通过全部 12 项真实 Stata 测试，包括安装完整性、生命周期和路径遮挡。日志位于工作区 `hx-fix-validation/complete-workflow`。6 项仓库／发布检查和 `git diff --check` 通过。

新增集成测试使用真实 SFI 和工作台控件／回调，关闭测试界面的异步预览计时器，在 `javacall` 所在线程执行；尚未覆盖鼠标操作和完整界面并发行为。完整多 frame 封装、转换载入保护、模型支持范围等审查事项仍待处理。远端检查及网页上线状态见 [GitHub Actions](https://github.com/xiaowang5105/hxempirical/actions) 中对应提交的运行结果。

## 2026-09-06 项目恢复修订

本地修订增加：恢复失败回滚、完成步骤的自动恢复点、上一版本备份、资源完整性和容量限制、失败资源清理、旧快照引用保护、junction 检查及监控预览范围限制。完整 frameset 保存仍未实现，当前通过单 frame 检查明确阻止不完整快照。

- Java 11 生产编译和项目行为测试通过：主文件与恢复点独立、恢复点重新绑定原项目路径、备份可读、缺失 TSV 明确报错、超限保存保留旧文件、失败替换清理临时文件、保留引用中的快照并清理过期恢复快照。
- Windows junction 实测：资源目标尚不存在时即被拒绝，链接目标未创建文件。
- Stata 故障注入通过：无效 RNG state、切换 RNG 后读取不存在文件，均恢复原数据、估计矩阵、`e(sample)` 和随机数状态；多个 frame 保存失败后保留所有 frame。
- 监控稀疏条件测试通过：行预览标记前 5,000 行，样本统计仍计入后部观测。
- 仓库 6 项静态、发布与 JAR 来源检查通过；全部 11 项真实 Stata 测试通过（含安装完整性、生命周期、路径遮挡、项目往返与工作台测试）。全量 Stata 验证日志位于工作区 `hx-fix-validation/full`。

下面的远端提交、CI 链接及 ZIP 摘要记录此前版本；本次修订的当前校验值以 `hxempirical-release.index` 和 `HxWorkbench.jar-source` 为准。

验证环境：Windows、StataNow 19.5 MP、Stata 自带 SFI / JDK；构建产物为 Java 11 字节码。Stata 17/18 和 macOS 尚未在本次环境中实测。

## 已通过

- 6 项仓库、发布包、静态契约、安装器契约、Statistics 目录和 Java/JAR 来源一致性检查。
- Java 项目行为测试：完整模型设定去重、旧记录兼容、中文项目读写、相同 N 不同样本识别、脚本生成及资源路径校验。
- 11 项真实 Stata 测试：核心组件、执行状态、profile 安全、安装完整性、安装生命周期、安装输出、路径遮挡、离线安装、项目快照、项目往返重现、工作台主要功能。
- 工作台首页离屏渲染检查，确认“研究项目”入口可见。
- `git diff --check`。
- GitHub Actions 在 Ubuntu 上通过发布一致性、Java 11 编译及项目行为检查，见 [运行记录](https://github.com/xiaowang5105/hxempirical/actions/runs/34010918151)；该记录对应功能提交 `1760da0`。

路径遮挡测试在修复测试自身的硬编码版本、宏文本复制和 Windows 分隔符比较后单独重跑通过；其余 10 项使用同一最终生产 JAR 和发布包通过。

## 数值核对

- `summarize` 返回均值 10.5；经 `hxexecute`、界面内部查询和刷新后仍为 10.5。
- `generate centered = x - r(mean)` 的 20 条结果均正确，没有额外缺失值。
- 固定种子的 20 条随机数与直接执行逐项相同，运行后的 RNG 状态相同。
- 原生返回矩阵、宏和标量保留；内部查询后 `e(sample)` 和 `margins` 可用。
- 项目保存、读取、导出脚本重跑后，系数矩阵相对差异小于 1e-12。
- 两个模型的共同样本重估均使用同一组 70 条观测。

## 发布产物

- 版本：1.6.0。
- 管理文件：41；ZIP 文件：46；Base64 分段：17。
- ZIP SHA-256：`4e9c2ccfe012b27f14670d8683db2c12a55e4118e87cb0c2292e85f5ba33c171`。
- Java 来源清单同时绑定全部 5 个源文件和生产 JAR。

源码和发布产物已上传至 `codex/execution-project-workflow` 分支，见 [PR #38](https://github.com/xiaowang5105/hxempirical/pull/38)。真实 Stata 的 GitHub Actions 工作流已加入仓库；远端运行仍需维护者配置带授权 Stata 的 self-hosted runner 和 `STATA_EXE`。

本地原始测试日志位于 `.build/final-stata-logs-v2`；最终路径遮挡测试日志位于 `.build/shadowing-final-logs-v2`。这些目录不进入 Git 提交。
