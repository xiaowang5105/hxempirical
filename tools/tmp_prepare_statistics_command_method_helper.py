from pathlib import Path

p = Path("tools/tmp_patch_statistics_command_method.py")
s = p.read_text(encoding="utf-8")
anchor = 'sc = sc[:a] + stats + sc[b:]\n'
insert = '''sc = sc[:a] + stats + sc[b:]
dead_post = ''' + "'''" + '''         } else if (Arrays.asList("test", "lincom").contains(var0)) {
            return "后估计|系数检验";
         } else if (Arrays.asList("predict", "margins").contains(var0)) {
            return "后估计|预测边际";
''' + "'''" + '''
if sc.count(dead_post) != 1:
    raise SystemExit(f"legacy postestimation commandMethod block expected once, got {sc.count(dead_post)}")
sc = sc.replace(dead_post, "", 1)
'''
if s.count(anchor) != 1:
    raise SystemExit(f"Statistics helper insertion anchor expected once, got {s.count(anchor)}")
s = s.replace(anchor, insert, 1)
p.write_text(s, encoding="utf-8", newline="\n")
print("HX_STATISTICS_COMMAND_METHOD_HELPER_PREPARED")
