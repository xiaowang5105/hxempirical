from pathlib import Path

# Make uninstall wording location-neutral now that a managed install can live in PLUS/h.
p = Path('hxinstaller.ado')
s = p.read_text(encoding='utf-8')
s = s.replace('noisily display as result _newline "hxempirical 的 PERSONAL 安装已卸载。"', "noisily display as result _newline \"hxempirical 的受管安装已卸载（`target_kind'）。\"", 1)
p.write_text(s, encoding='utf-8')

# The product patch script creates a permanent workflow candidate, but GitHub Actions
# cannot push workflow-file changes with its repository token. Remove the candidate
# in the audit workspace; it will be added to the audited tree through the GitHub API
# after the product commit has been pushed successfully.
ci = Path('.github/workflows/ci.yml')
if ci.exists():
    ci.unlink()

print('POST_V152_OK')
