from pathlib import Path
p = Path('README.md')
s = p.read_text(encoding='utf-8')
s = s.replace('**上次修改时间：2026-08-12 19:14（UTC+8）**', '**上次修改时间：2026-08-12 19:41（UTC+8）**', 1)
marker = '## 修改记录\n\n'
entry = '''### 2026-08-12 19:41（UTC+8）\n\n**修改时间**：2026-08-12 19:41（UTC+8）\n\n**修改内容**：\n\n- 在 1.1.0 最终自查中补齐基准回归任务工作区的“继续工作 / 最近工作恢复”：现在会保存并恢复当前估计器、Y、核心 X、Controls、分类/交互/滞后项、`xtreg` 模型、`absorb()`、VCE、Cluster、`if/in`、权重和高级 options，不会因为切换估计方法而丢失任务状态。\n- 旧版普通 `regress` 快照继续恢复到真正的 `regress` 页面，不会因为“基准回归”默认改为 `xtreg` 而误跳到任务工作区；VIF、异方差等普通 OLS 诊断搜索也继续进入真实 `regress` 后估计页面。\n- 修正上述兼容边界后重新执行 Java 11 编译、class major 55 检查、JAR 重建，以及首页、命令目录、基准回归工作区三类离线 UI 渲染测试，最终验证通过。\n\n'''
if marker not in s: raise SystemExit('missing changelog marker')
s = s.replace(marker, marker + entry, 1)
s = s.replace('**发布时间**：2026-08-12 19:14（UTC+8）\n\n**修改内容**：\n\n- 首页改为单一稳定状态，完整功能目录始终显示。\n- 基准回归改为任务工作区，默认 `xtreg`，页内紧凑切换 `reghdfe` / `areg` / `regress` 并保留公共变量设置。\n- 命令选择页压缩为目录式布局，并修复方法切换后的命令列表残留问题。', '**发布时间**：2026-08-12 19:41（UTC+8）\n\n**修改内容**：\n\n- 首页改为单一稳定状态，完整功能目录始终显示。\n- 基准回归改为任务工作区，默认 `xtreg`，页内紧凑切换 `reghdfe` / `areg` / `regress` 并保留公共变量设置。\n- 命令选择页压缩为目录式布局，并修复方法切换后的命令列表残留问题。\n- 最近工作恢复同步适配任务工作区，并保持旧 `regress` 快照与 OLS 诊断入口兼容。', 1)
p.write_text(s, encoding='utf-8')
print('HX_README_110_FINAL_RECORD_OK')
