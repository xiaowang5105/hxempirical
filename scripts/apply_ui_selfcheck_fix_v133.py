from pathlib import Path

root = Path('.')
java = root / 'src/main/java/com/hexie/stata/HxWorkbench.java'
s = java.read_text(encoding='utf-8')


def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'missing marker: {label}')
    s = s.replace(old, new, 1)

# Version bump after a second UI audit found a real narrow-layout failure.
s = s.replace('public static final String VERSION = "1.3.2";', 'public static final String VERSION = "1.3.3";', 1)
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.3.2");', 'SFIToolkit.displayln("HxWorkbench 1.3.3");', 1)

# Keep model choices fully clickable even when the command pane is narrowed.
rep(
    '         JPanel models = new JPanel(new GridLayout(2, 2, 8, 6)); models.setOpaque(false);\n',
    '         JPanel models = new JPanel(new GridLayout(4, 1, 0, 4)); models.setOpaque(false);\n',
    'xtreg model choices responsive layout'
)

# Keep all action buttons inside the card at narrow split positions.
rep(
    '         JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 0)); actions.setOpaque(false);\n',
    '         JPanel actions = new JPanel(new GridLayout(1, 3, 8, 0)); actions.setOpaque(false);\n',
    'xtreg action button responsive layout'
)

java.write_text(s, encoding='utf-8')

ado = root / 'hxempirical.ado'
a = ado.read_text(encoding='utf-8')
a = a.replace('*! hxempirical 1.3.2  13aug2026', '*! hxempirical 1.3.3  13aug2026', 1)
a = a.replace('display as text "版本：" as result "1.3.2"', 'display as text "版本：" as result "1.3.3"', 1)
a = a.replace('return local version "1.3.2"', 'return local version "1.3.3"', 1)
ado.write_text(a, encoding='utf-8')

pkg = root / 'hxempirical.pkg'
p = pkg.read_text(encoding='utf-8')
p = p.replace('d Version 1.3.2', 'd Version 1.3.3', 1)
pkg.write_text(p, encoding='utf-8')

print('UI self-check fixes v1.3.3 applied')
