# 1.6.0 本地验证记录

验证环境：Windows、StataNow 19.5 MP、Stata 自带 SFI / JDK；构建产物为 Java 11 字节码。Stata 17/18 和 macOS 尚未在本次环境中实测。

## 已通过

- 6 项仓库、发布包、静态契约、安装器契约、Statistics 目录和 Java/JAR 来源一致性检查。
- Java 项目行为测试：完整模型设定去重、旧记录兼容、中文项目读写、相同 N 不同样本识别、脚本生成及资源路径校验。
- 11 项真实 Stata 测试：核心组件、执行状态、profile 安全、安装完整性、安装生命周期、安装输出、路径遮挡、离线安装、项目快照、项目往返重现、工作台主要功能。
- 工作台首页离屏渲染检查，确认“研究项目”入口可见。
- `git diff --check`。

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

当前产物保存在本地，尚未上传 GitHub。真实 Stata 的 GitHub Actions 工作流已加入仓库；远端运行仍需维护者配置带授权 Stata 的 self-hosted runner 和 `STATA_EXE`。

本地原始测试日志位于 `.build/final-stata-logs-v2`；最终路径遮挡测试日志位于 `.build/shadowing-final-logs-v2`。这些目录不进入 Git 提交。
