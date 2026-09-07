# 1.6.1 验证记录

日期：2026-09-07。环境：Windows / StataNow 19.5 MP；使用 Stata 自带 SFI 和 JDK 构建 Java 11 字节码。

## 整体验证

- 最终生产 JAR 和发布包通过全部 13 项真实 Stata 测试，日志：工作区 `hx-fix-validation/data-safety-full-final`。此前完整测试记录保留在 `hx-fix-validation/data-safety-full`。
- 最终安装说明和文件头同步后，重新打包并通过安装完整性、生命周期、路径遮挡三项测试，日志：`hx-fix-validation/data-safety-release-final`。
- Java 项目行为和文件保护测试、6 项仓库／发布检查及 `git diff --check` 通过。
- 最终 ZIP SHA-256：`a6e12d6881915448179e41c6f7470bb004c749c87c162fb0a833609d69ec7747`。
- 生产 JAR SHA-256：`c6e2d9cedb86d8d0ee5cf5797b48f089a74406e398f1d56f7648ea901ec7cdc6`，来源清单绑定全部 6 个 Java 模块。

## 数据安全回归

- 真实 Stata 载入损坏或不存在 DTA，保留原数据、文件名、估计矩阵、估计样本和随机数状态；成功载入清除旧估计状态，其他 frame 保留。
- 真实工作台替换确认框选择取消，保持当前数据；实际文件转换保持原分析数据及估计系数。
- 转换失败保护已有 DTA；中文和空格路径转换成功，保存带前导零的字符串列；转换及随后载入的项目脚本重放得到一致数据，失败步骤不阻断后续已记录步骤。
- 文件行为测试覆盖跨格式／大小写重复目标、未经确认覆盖、临时文件缺失、确认后目标变化、运行期间目标出现、错误扩展名、原文件及硬链接目标，以及成功发布。
- 既有 Java 项目测试通过。定向日志位于工作区 `hx-fix-validation/data-safety-targeted`（载入测试通过；首次工作台测试因测试自身宏空值读取失败）和 `hx-fix-validation/data-safety-workflow-final`（修正测试后工作台回归通过）。

## 验证边界

集成测试调用真实 SFI、工作台转换方法和取消确认框；未覆盖完整的鼠标用户旅程、所有 Excel 格式、完整 UI 并发及性能。CSV 预检仍为抽样，复杂类型和多行字段待完善。Stata 17/18、macOS 尚未实测。

工作台对已有目标使用同目录暂存和原子替换；不支持原子替换时保留原文件并报告失败。目标变化检查使用文件标识、大小和修改时间，不能提供跨进程文件锁保证。导出脚本使用原生 Stata 的 `save, replace`，执行前需检查输出路径；外部原文件和依赖仍需用户保留。

发布产物校验值见 `hxempirical-release.index` 与 `HxWorkbench.jar-source`；线上版本及部署状态见 [GitHub Actions](https://github.com/xiaowang5105/hxempirical/actions)。
