from pathlib import Path

p = Path("tools/tmp_patch_graph_result_routing.py")
s = p.read_text(encoding="utf-8")
old = '''route_start = java.find('} else if (Arrays.asList(\\n               "twoway", "scatter", "line", "connected"')
route_end = java.find(').contains(this.currentCommand)) {\\n            this.selectResultView("graph", true);', route_start)
if route_start < 0 or route_end < 0:
    fail("expanded Graphics result-routing block missing")
route_scope = java[route_start:route_end]
'''
new = '''route_start = java.find('"graph_bar", "graph_dot", "graph_pie", "graph_box", "twoway_contour", "graph_matrix"')
route_end = java.find('this.selectResultView("graph", true);', route_start)
if route_start < 0 or route_end < 0:
    fail("expanded Graphics result-routing block missing")
route_scope = java[route_start:route_end]
'''
if s.count(old) != 1:
    raise SystemExit(f"old graph route verifier block expected once, got {s.count(old)}")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8", newline="\n")
print("HX_GRAPH_RESULT_ROUTING_HELPER_PREPARED")
