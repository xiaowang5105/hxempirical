from pathlib import Path
import re

s = Path("hxregistry.ado").read_text(encoding="utf-8")


def local(name):
    m = re.search(r"^\s*local\s+" + re.escape(name) + r'\s+"([^"]*)"', s, re.M)
    if not m:
        raise SystemExit("missing local " + name)
    return m.group(1).split()


cats = {
    "data": ("data_cmds", "data_methods"),
    "stats": ("stats_cmds", "stats_methods"),
    "graph": ("graph_cmds", "graph_methods"),
    "oneclick": ("oneclick_cmds", "oneclick_methods"),
}
pat = re.compile(r'(?:^|\n)\s*(?:if|else if)\s+inlist\(`"`method\'"\',\s*"([^"]+)"[^\n]*?\)\s+local\s+view\s+"([^"]*)"')
routes = {m.group(1): m.group(2).split() for m in pat.finditer(s)}

searchable = set()
rows = []
for cat, (cmd_local, method_local) in cats.items():
    commands = local(cmd_local)
    methods = local(method_local)
    searchable.update(commands)
    if len(commands) != len(set(commands)):
        raise SystemExit(f"duplicate commands in {cat}")
    if len(methods) != len(set(methods)):
        raise SystemExit(f"duplicate methods in {cat}")
    routed = set()
    for method in methods:
        if method not in routes:
            raise SystemExit(f"NO_ROUTE {cat}/{method}")
        routed.update(routes[method])
        rows.append((cat, method, routes[method]))
    missing = [c for c in commands if c not in routed]
    if missing:
        raise SystemExit(f"SEARCH_WITHOUT_PATH {cat}: {missing}")

for cat, method, commands in rows:
    for command in commands:
        if command not in searchable:
            raise SystemExit(f"PATH_WITHOUT_SEARCH {cat}/{method}: {command}")

loop = re.search(r"foreach\s+cmd\s+in\s+([^\{]+)\{", s)
if not loop:
    raise SystemExit("all_cmds loop missing")
looptext = loop.group(1)
for token in ["`data_cmds'", "`stats_cmds'", "`graph_cmds'", "`oneclick_cmds'"]:
    if token not in looptext:
        raise SystemExit("all_cmds missing " + token)
for token in ["`reg_cmds'", "`post_cmds'", "`did_cmds'"]:
    if token in looptext:
        raise SystemExit("all_cmds includes hidden compatibility source " + token)

# Generate expected values for the Java reflection audit.
Path("/tmp/preview_expected.tsv").write_text(
    "\n".join(cat + "\t" + method + "\t" + " ".join(commands) for cat, method, commands in rows),
    encoding="utf-8",
)
Path("/tmp/method_expected.tsv").write_text(
    "\n".join(cat + "\t" + "|".join(local(method_local)) for cat, (_, method_local) in cats.items()),
    encoding="utf-8",
)

# Release version parity.
vals = {}
java = Path("src/main/java/com/hexie/stata/HxWorkbench.java").read_text(encoding="utf-8")
vals["java"] = re.search(r'VERSION\s*=\s*"([^"]+)"', java).group(1)
vals["ado"] = re.search(r"\*! hxempirical ([0-9.]+)", Path("hxempirical.ado").read_text(encoding="utf-8")).group(1)
vals["pkg"] = re.search(r"d Version ([0-9.]+)", Path("hxempirical.pkg").read_text(encoding="utf-8")).group(1)
vals["help"] = re.search(r"version ([0-9.]+)", Path("hxempirical.sthlp").read_text(encoding="utf-8")).group(1)
vals["readme"] = re.search(r"当前发布版本：([0-9.]+)", Path("README.md").read_text(encoding="utf-8")).group(1)
if len(set(vals.values())) != 1:
    raise SystemExit("VERSION_MISMATCH " + repr(vals))
if next(iter(vals.values())) != "1.4.8":
    raise SystemExit("unexpected release version " + repr(vals))

# Key routes explicitly required by the UI.
required = {
    "线性模型及相关": {"regress", "areg", "reghdfe", "qreg"},
    "计数结果": {"poisson", "nbreg", "ppmlhdfe"},
    "工具变量与内生性": {"ivregress", "ivreghdfe"},
    "估计后分析": {"test", "lincom", "predict", "margins"},
    "更多统计图形": {"marginsplot", "coefplot", "event_plot"},
}
for method, wanted in required.items():
    got = set(routes.get(method, []))
    missing = wanted - got
    if missing:
        raise SystemExit(f"KEY_ROUTE_MISSING {method}: {sorted(missing)}")

print("REGISTRY_BIJECTION_OK", len(searchable), "searchable commands", len(rows), "visible methods")
print("VERSION_METADATA_OK", vals)
