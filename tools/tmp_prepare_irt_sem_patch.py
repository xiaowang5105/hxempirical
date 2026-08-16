from pathlib import Path

p = Path("tools/tmp_patch_irt_sem_quality.py")
s = p.read_text(encoding="utf-8")
old = '        local purpose1 "用于估计题项难度、区分度和潜在能力 / 特质之间的关系。"\\n'
new = '        local purpose1 "用 Rasch、1PL/2PL/3PL、GRM 等模型分析潜在能力与题项反应之间的关系。"\\n'
if old not in s:
    raise SystemExit("IRT family purpose patch anchor missing")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8", newline="\n")
print("HX_IRT_PATCH_PREPARE_OK")
