package com.hexie.stata;

import java.awt.Component;
import java.awt.Container;
import java.awt.Window;
import java.awt.event.ActionListener;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Locale;
import javax.swing.AbstractButton;
import javax.swing.JCheckBox;
import javax.swing.JFileChooser;
import javax.swing.JOptionPane;
import javax.swing.JRadioButton;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;
import javax.swing.Timer;
import javax.swing.filechooser.FileNameExtensionFilter;

/**
 * Installs the direct Excel/CSV import affordance on the already-created
 * HxWorkbench window without duplicating the conversion engine.
 *
 * <p>The hook deliberately reuses WorkbenchFrame's existing single-file
 * conversion path. That path already performs file inspection, leading-zero
 * protection, collision handling, native Stata import/save commands, History
 * recording, and dataset refresh. This class only changes the user entrypoint:
 * choose an Excel/CSV file, derive the sibling .dta path, force "load after",
 * then hand off to the existing engine.</p>
 *
 * <p>This class has no compile-time dependency on Stata SFI. The current-data
 * warning checks SFI reflectively at runtime, so the class can be compiled in
 * hosted CI without fake SFI classes and can be added to the production JAR
 * without rebuilding HxWorkbench.class.</p>
 */
public final class HxDirectImportHook {
    private static final String HOOK_PROPERTY = "hx.directExcelCsvImport";
    private static final String OLD_EMPTY_LABEL = "Excel / CSV 转换为 DTA";
    private static final String OLD_HOME_LABEL = "导入 Excel/CSV";
    private static final String DIRECT_LABEL = "导入 Excel / CSV";
    private static final int MAX_INSTALL_ATTEMPTS = 24;

    private HxDirectImportHook() {
    }

    /** Entry point called by hxtoolbox.ado immediately after HxWorkbench.launch. */
    public static int install(String[] args) {
        SwingUtilities.invokeLater(() -> {
            patchOpenWorkbenchWindows();
            final int[] attempts = new int[]{0};
            Timer timer = new Timer(250, null);
            timer.addActionListener(event -> {
                attempts[0]++;
                int patched = patchOpenWorkbenchWindows();
                if (patched > 0 || attempts[0] >= MAX_INSTALL_ATTEMPTS) {
                    ((Timer) event.getSource()).stop();
                }
            });
            timer.setRepeats(true);
            timer.start();
        });
        return 0;
    }

    private static int patchOpenWorkbenchWindows() {
        int patched = 0;
        for (Window window : Window.getWindows()) {
            if (!window.isDisplayable()) {
                continue;
            }
            String className = window.getClass().getName();
            if (!className.contains("HxWorkbench$WorkbenchFrame")) {
                continue;
            }
            patched += patchTree(window, window);
        }
        return patched;
    }

    private static int patchTree(Component component, Window owner) {
        int patched = 0;
        if (component instanceof AbstractButton) {
            AbstractButton button = (AbstractButton) component;
            String text = button.getText();
            if (OLD_EMPTY_LABEL.equals(text) || OLD_HOME_LABEL.equals(text) || DIRECT_LABEL.equals(text)) {
                Object installed = button.getClientProperty(HOOK_PROPERTY);
                if (!Boolean.TRUE.equals(installed)) {
                    for (ActionListener listener : button.getActionListeners()) {
                        button.removeActionListener(listener);
                    }
                    button.setText(DIRECT_LABEL);
                    button.addActionListener(event -> chooseAndImport(owner));
                    button.putClientProperty(HOOK_PROPERTY, Boolean.TRUE);
                    patched++;
                }
            }
        }
        if (component instanceof Container) {
            for (Component child : ((Container) component).getComponents()) {
                patched += patchTree(child, owner);
            }
        }
        return patched;
    }

    private static void chooseAndImport(Window owner) {
        if (readBooleanField(owner, "runInProgress")) {
            JOptionPane.showMessageDialog(owner, "当前仍有命令在运行，请等待本次执行结束。", "正在运行", JOptionPane.INFORMATION_MESSAGE);
            return;
        }

        JFileChooser chooser = new JFileChooser();
        chooser.setDialogTitle("导入 Excel / CSV");
        chooser.setAcceptAllFileFilterUsed(false);
        chooser.setFileFilter(new FileNameExtensionFilter("Excel / CSV (*.xlsx, *.xls, *.csv)", "xlsx", "xls", "csv"));
        if (chooser.showOpenDialog(owner) != JFileChooser.APPROVE_OPTION) {
            return;
        }

        Path input = chooser.getSelectedFile().toPath().toAbsolutePath().normalize();
        if (!isSupportedInput(input)) {
            JOptionPane.showMessageDialog(owner, "请选择 .xlsx、.xls 或 .csv 文件。", "不支持的文件类型", JOptionPane.WARNING_MESSAGE);
            return;
        }

        if (currentDatasetPresent()) {
            int answer = JOptionPane.showConfirmDialog(
                owner,
                "导入完成后会把新数据载入当前 Stata，并替换内存中的现有数据。\n请确认当前数据已经保存。\n\n继续导入吗？",
                "确认导入 Excel / CSV",
                JOptionPane.OK_CANCEL_OPTION,
                JOptionPane.WARNING_MESSAGE
            );
            if (answer != JOptionPane.OK_OPTION) {
                return;
            }
        }

        Path output = defaultDtaOutput(input);
        try {
            setTextField(owner, "convertInputFile", input.toString());
            setTextField(owner, "convertOutputFile", output.toString());
            setSelected(owner, "convertSingleMode", true);
            setSelected(owner, "convertBatchMode", false);
            setSelected(owner, "convertLoadAfter", true);
            setSelected(owner, "convertProtectLeadingZeros", true);
            setSelected(owner, "convertDelimitedFirstRow", true);

            Method detect = owner.getClass().getDeclaredMethod("detectExternalFile", Path.class);
            detect.setAccessible(true);
            detect.invoke(owner, input);

            Method run = owner.getClass().getDeclaredMethod("runConvertDta");
            run.setAccessible(true);
            run.invoke(owner);
        } catch (ReflectiveOperationException error) {
            JOptionPane.showMessageDialog(
                owner,
                "直接导入入口无法连接到当前转换引擎：" + rootMessage(error) + "\n请从“数据处理 → 导入与转换”进入高级导入页面。",
                "导入入口不可用",
                JOptionPane.ERROR_MESSAGE
            );
        }
    }

    private static boolean isSupportedInput(Path path) {
        String name = path.getFileName().toString().toLowerCase(Locale.ROOT);
        return name.endsWith(".xlsx") || name.endsWith(".xls") || name.endsWith(".csv");
    }

    private static Path defaultDtaOutput(Path input) {
        String name = input.getFileName().toString();
        int dot = name.lastIndexOf('.');
        String stem = dot > 0 ? name.substring(0, dot) : name;
        Path parent = input.getParent();
        Path file = Paths.get(stem + ".dta");
        return parent == null ? file.toAbsolutePath().normalize() : parent.resolve(file).toAbsolutePath().normalize();
    }

    private static boolean currentDatasetPresent() {
        try {
            Class<?> data = Class.forName("com.stata.sfi.Data");
            Method obsMethod = data.getMethod("getObsTotal");
            Method varMethod = data.getMethod("getVarCount");
            long observations = ((Number) obsMethod.invoke(null)).longValue();
            int variables = ((Number) varMethod.invoke(null)).intValue();
            return observations > 0L || variables > 0;
        } catch (ReflectiveOperationException ignored) {
            return false;
        }
    }

    private static void setTextField(Window owner, String name, String value) throws ReflectiveOperationException {
        Field field = owner.getClass().getDeclaredField(name);
        field.setAccessible(true);
        ((JTextField) field.get(owner)).setText(value);
    }

    private static void setSelected(Window owner, String name, boolean value) throws ReflectiveOperationException {
        Field field = owner.getClass().getDeclaredField(name);
        field.setAccessible(true);
        Object control = field.get(owner);
        if (control instanceof JCheckBox) {
            ((JCheckBox) control).setSelected(value);
        } else if (control instanceof JRadioButton) {
            ((JRadioButton) control).setSelected(value);
        } else {
            throw new IllegalStateException("Unsupported selection control: " + name);
        }
    }

    private static boolean readBooleanField(Window owner, String name) {
        try {
            Field field = owner.getClass().getDeclaredField(name);
            field.setAccessible(true);
            return field.getBoolean(owner);
        } catch (ReflectiveOperationException ignored) {
            return false;
        }
    }

    private static String rootMessage(Throwable error) {
        Throwable cursor = error;
        while (cursor.getCause() != null) {
            cursor = cursor.getCause();
        }
        String message = cursor.getMessage();
        return message == null || message.isBlank() ? cursor.getClass().getSimpleName() : message;
    }

    public static void main(String[] args) {
        if (args.length == 1 && "--self-test".equals(args[0])) {
            if (!isSupportedInput(Paths.get("sample.xlsx"))
                || !isSupportedInput(Paths.get("sample.xls"))
                || !isSupportedInput(Paths.get("sample.csv"))
                || isSupportedInput(Paths.get("sample.dta"))
                || isSupportedInput(Paths.get("sample.tsv"))) {
                throw new IllegalStateException("supported-extension contract failed");
            }
            String output = defaultDtaOutput(Paths.get("folder", "企业数据.xlsx")).getFileName().toString();
            if (!"企业数据.dta".equals(output)) {
                throw new IllegalStateException("automatic DTA path contract failed: " + output);
            }
            System.out.println("HX_DIRECT_IMPORT_HOOK_OK extensions=xlsx,xls,csv output=.dta load_after=1");
            return;
        }
        System.out.println("Usage: HxDirectImportHook --self-test");
    }
}
