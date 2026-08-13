from pathlib import Path
import re

src = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = src.read_text(encoding='utf-8')

# Remove dead labels from the deleted fake OneClick inspector.
s = re.sub(r'\n\s*private final JLabel exactOneClickDataStatus = new JLabel\([^\n]+\);', '', s, count=1)
s = re.sub(r'\n\s*private final JLabel exactOneClickDataDetail = new JLabel\([^\n]+\);', '', s, count=1)
s = re.sub(r'\n\s*this\.exactOneClickDataStatus\.setText\([^;]+;','',s,count=1)
s = re.sub(r'\n\s*this\.exactOneClickDataDetail\.setText\([^;]+;','',s,count=1)
if 'exactOneClickDataStatus' in s or 'exactOneClickDataDetail' in s:
    raise SystemExit('dead OneClick labels still referenced')

src.write_text(s, encoding='utf-8')

# Correct release dates and the last stale Run-tab wording.
p = Path('hxempirical.ado')
t = p.read_text(encoding='utf-8').replace('*! hxempirical 1.2.4  12aug2026','*! hxempirical 1.2.4  13aug2026',1)
p.write_text(t,encoding='utf-8')

p = Path('hxempirical.sthlp')
t = p.read_text(encoding='utf-8')
t = t.replace('{* *! version 1.2.4  12aug2026}{...}','{* *! version 1.2.4  13aug2026}{...}',1)
t = t.replace('The right-side {bf:运行} tab records the command, start and end times,','The right-side {bf:日志} tab records the command, start and end times,',1)
p.write_text(t,encoding='utf-8')

p = Path('hxempirical.pkg')
t = p.read_text(encoding='utf-8').replace('d Distribution-Date: 20260812','d Distribution-Date: 20260813',1)
p.write_text(t,encoding='utf-8')

# Append this self-check cleanup to README instead of silently changing files.
p = Path('README.md')
r = p.read_text(encoding='utf-8')
r = re.sub(r'\*\*上次修改时间：[^\n]+\*\*','**上次修改时间：2026-08-13 08:59（UTC+8）**',r,count=1)
entry='''### 2026-08-13 08:59（UTC+8）\n\n**修改时间**：2026-08-13 08:59（UTC+8）\n\n**修改内容**：\n\n- 对 1.2.4 修复版再做一轮收尾自查：删除已经失去界面用途的 OneClick 旧空状态标签与更新逻辑，避免继续维护两套右栏状态。\n- 修正 `hxempirical.sthlp` 中最后一处“运行”页签旧称，统一为“日志”；并把 1.2.4 的 ado/help/package 发布日期同步为 2026-08-13。\n- 重新执行 Java 11 / class major 55 编译和 OneClick 数据、OneClick 结果、日志、基准回归四页渲染验证。\n\n'''
r=r.replace('## 修改记录\n\n','## 修改记录\n\n'+entry,1)
p.write_text(r,encoding='utf-8')
print('HX_124_CLEANUP_OK')
