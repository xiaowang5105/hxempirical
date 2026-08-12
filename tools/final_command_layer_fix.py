from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'missing pattern for {label}: {path}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


java = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
readme = Path('README.md')

# Hidden advanced graph state must never leak from a previous graph page.
replace_once(
    java,
    '''         this.breadcrumbLabel.setText(commandPath(var1));
         this.formPanel.removeAll();
         int var2 = 0;
''',
    '''         this.breadcrumbLabel.setText(commandPath(var1));
         this.depvar.setSelectedItem(null);
         this.panel.setSelectedItem(null);
         this.time.setSelectedItem(null);
         this.variables.clearSelection();
         this.ifCondition.setText("");
         this.options.setText("");
         this.expression.setText("twoway".equals(var1) ? "(scatter y x) (lfit y x)" : "");
         this.formPanel.removeAll();
         int var2 = 0;
''',
    'special graph state reset',
)

# Complete the remaining ordinary data/stat command guardrails.
needle = '''         if ("winsor2".equals(command) && this.variables.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "请选择至少 1 个需要缩尾的变量。", "缩尾设置尚未完整", 1);
            return false;
         }
'''
insert = needle + '''         if (Arrays.asList("keep", "drop").contains(command)) {
            if ("处理变量".equals(selected(this.model)) && this.variables.getSelectedValuesList().isEmpty()) {
               JOptionPane.showMessageDialog(this, command + " 选择“处理变量”时，需要选择至少 1 个变量。", "样本/变量处理设置尚未完整", 1);
               return false;
            }
            if ("处理样本".equals(selected(this.model)) && this.ifCondition.getText().trim().isBlank()) {
               JOptionPane.showMessageDialog(this, command + " 选择“处理样本”时，需要填写 if 条件。", "样本/变量处理设置尚未完整", 1);
               return false;
            }
         }
'''
replace_once(java, needle, insert, 'keep/drop validation')

needle2 = '''         if ("ttest".equals(command)) {
            if (this.variables.getSelectedValuesList().size() != 1 || this.expression.getText().trim().isBlank()) {
               JOptionPane.showMessageDialog(this, "ttest 需要选择 1 个被检验变量，并按检验方式填写比较值、分组变量或第二变量。", "t 检验设置尚未完整", 1);
               return false;
            }
         }
'''
insert2 = '''         if ("tabstat".equals(command) && this.variables.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "tabstat 需要选择至少 1 个要汇总的变量。", "描述统计设置尚未完整", 1);
            return false;
         }
''' + needle2
replace_once(java, needle2, insert2, 'tabstat validation')

# Keep the in-progress 15:08 cumulative record accurate rather than creating a second
# log entry for the same final completion pass.
replace_once(
    readme,
    '- 特殊图形页统一为“核心变量直接显示，if 与低频图形 options 收入更多设置”；普通图形导航不再把 HX 的 `did_trends` 当作普通图形方法展示。',
    '- 特殊图形页统一为“核心变量直接显示，if 与低频图形 options 收入更多设置”，并在切换图形时清理上一页隐藏状态，避免旧筛选条件或图形选项被无意带入；普通图形导航不再把 HX 的 `did_trends` 当作普通图形方法展示。',
    'README graph-state note',
)
replace_once(
    readme,
    '- 补齐 `tsset`、`rreg`、`cnsreg`、`vwls`、`eivreg`、`newey`、`prais` 等命令的面包屑归类和帮助映射；普通命令运行前增加必要字段与明显角色冲突检查。',
    '- 补齐 `tsset`、`rreg`、`cnsreg`、`vwls`、`eivreg`、`newey`、`prais` 等命令的面包屑归类和帮助映射；普通命令运行前增加必要字段与明显角色冲突检查，并补上 `keep/drop` 模式必填项及 `tabstat` 变量必填检查。',
    'README final validation note',
)

print('HX_FINAL_COMMAND_LAYER_FIX_OK')
