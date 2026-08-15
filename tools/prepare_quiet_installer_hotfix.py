from pathlib import Path

root = Path(__file__).resolve().parents[1]

launcher_path = root / "hxinstall.do"
launcher = launcher_path.read_text(encoding="utf-8")
if launcher.count("capture noisily do") != 1:
    raise SystemExit("expected exactly one noisy bootstrap do invocation")
launcher = launcher.replace("capture noisily do", "capture quietly do", 1)
launcher_path.write_text(launcher, encoding="utf-8")

verify_path = root / "tools" / "verify_static_contracts.py"
verify = verify_path.read_text(encoding="utf-8")

needle = 'install_doc = read("INSTALL.md")\n'
if 'launcher = read("hxinstall.do")' not in verify:
    if needle not in verify:
        raise SystemExit("verify_static_contracts read block changed")
    verify = verify.replace(needle, needle + 'launcher = read("hxinstall.do")\n', 1)

anchor = 'if "hxempirical 不再自动安装第三方命令" not in entry:\n    fail("public hxempirical install compatibility path must not install packages")\n'
guard = '''\n# The public launcher must load the downloaded installer core silently.\n# Using `noisily do` echoes the entire ~580-line installer into Results.\nif "capture noisily do" in launcher:\n    fail("public hxinstall.do still echoes the installer core into Results")\nif "capture quietly do" not in launcher:\n    fail("public hxinstall.do does not load the installer core quietly")\n'''
if 'public hxinstall.do still echoes the installer core' not in verify:
    if anchor not in verify:
        raise SystemExit("verify_static_contracts external-policy anchor changed")
    verify = verify.replace(anchor, anchor + guard, 1)

if 'launcher_quiet=1' not in verify:
    print_anchor = 'docs_manual_only=1 spreadsheet_editable=1 '
    if print_anchor not in verify:
        raise SystemExit("verify_static_contracts summary anchor changed")
    verify = verify.replace(print_anchor, print_anchor + 'launcher_quiet=1 ', 1)

verify_path.write_text(verify, encoding="utf-8")
print("HX_QUIET_INSTALLER_PREP_OK")
