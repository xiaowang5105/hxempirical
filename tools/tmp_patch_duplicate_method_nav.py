from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.24  16aug2026", "*! hxregistry 3.1.25  16aug2026", "registry version")
old_methods = 'local stats_methods "汇总，表格和假设检验 线性模型及相关 二元结果 序数结果 分类结果 计数结果 分数结果 广义线性模型 选择模型 时间序列 多元时间序列 空间自回归模型 纵向/面板数据 多层混合效应模型 生存分析 流行病学及相关 内生协变量 样本选择模型 因果推断/处理效应 结构方程模型(SEM) 潜在类别分析(LCA) 有限混合模型(FMM) 项目反应理论(IRT) DSGE模型 多元分析 调查数据分析 Lasso回归 Meta分析 多重插补 非参数分析 精确统计 重抽样 效能，精度和样品含量 贝叶斯分析 贝叶斯模型平均 工具变量与内生性 估计后分析"'
new_methods = 'local stats_methods "汇总，表格和假设检验 线性模型及相关 二元结果 序数结果 分类结果 计数结果 分数结果 广义线性模型 选择模型 时间序列 多元时间序列 空间自回归模型 纵向/面板数据 多层混合效应模型 生存分析 流行病学及相关 内生协变量 因果推断/处理效应 结构方程模型(SEM) 潜在类别分析(LCA) 有限混合模型(FMM) 项目反应理论(IRT) DSGE模型 多元分析 调查数据分析 Lasso回归 Meta分析 多重插补 非参数分析 精确统计 重抽样 效能，精度和样品含量 贝叶斯分析 贝叶斯模型平均 工具变量与内生性 估计后分析"'
r = once(r, old_methods, new_methods, "public statistics methods")
# Keep the old method route as a compatibility alias for saved UI state / older quick links.
if '"样本选择模型", "sample_selection") local view "heckman heckprobit heckoprobit heckpoisson"' not in r:
    raise SystemExit("sample-selection compatibility alias missing")
rp.write_text(r, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'stats_cmds = set(local_words(registry, "stats_cmds"))\n'
checks = '''stats_methods = local_words(registry, "stats_methods")
if "样本选择模型" in stats_methods:
    fail("duplicate sample-selection method leaked into public Statistics navigation")
if "选择模型" not in stats_methods:
    fail("public Selection models method missing")
if '"样本选择模型", "sample_selection") local view "heckman heckprobit heckoprobit heckpoisson"' not in registry:
    fail("legacy sample-selection navigation alias must remain resolvable")

'''
v = once(v, anchor, anchor + checks, "duplicate-method static contract anchor")
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_DUPLICATE_METHOD_NAV_PATCH_OK")
