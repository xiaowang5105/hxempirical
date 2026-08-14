package com.hexie.stata;

import com.stata.sfi.Characteristic;
import com.stata.sfi.Data;
import com.stata.sfi.Frame;
import com.stata.sfi.Macro;
import com.stata.sfi.Missing;
import com.stata.sfi.SFIToolkit;
import com.stata.sfi.Scalar;
import java.awt.BasicStroke;
import java.awt.BorderLayout;
import java.awt.CardLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Container;
import java.awt.Cursor;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.GraphicsEnvironment;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Insets;
import java.awt.Rectangle;
import java.awt.RenderingHints;
import java.awt.Toolkit;
import java.awt.datatransfer.DataFlavor;
import java.awt.datatransfer.StringSelection;
import java.awt.datatransfer.Transferable;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.image.BufferedImage;
import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.math.BigInteger;
import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.Charset;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.Map.Entry;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import java.util.prefs.Preferences;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Stream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import javax.imageio.ImageIO;
import javax.swing.AbstractButton;
import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.ButtonGroup;
import javax.swing.ButtonModel;
import javax.swing.DefaultListCellRenderer;
import javax.swing.DefaultListModel;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JProgressBar;
import javax.swing.JRadioButton;
import javax.swing.JScrollPane;
import javax.swing.Scrollable;
import javax.swing.JSpinner;
import javax.swing.JSplitPane;
import javax.swing.JTabbedPane;
import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.JToggleButton;
import javax.swing.TransferHandler;
import javax.swing.ListModel;
import javax.swing.SpinnerNumberModel;
import javax.swing.SwingUtilities;
import javax.swing.SwingConstants;
import javax.swing.SwingWorker;
import javax.swing.Timer;
import javax.swing.UIManager;
import javax.swing.border.AbstractBorder;
import javax.swing.border.EmptyBorder;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import javax.swing.plaf.FontUIResource;
import javax.swing.plaf.basic.BasicButtonUI;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;

public final class HxWorkbench {
   public static final String VERSION = "1.4.8";
   private static HxWorkbench.WorkbenchFrame frame;

   private HxWorkbench() {
   }

   public static void main(String[] var0) throws Exception {
      if (var0.length == 2 && "--inspect-convert-file".equals(var0[0])) {
         HxWorkbench.ExternalFileProfile var20 = HxWorkbench.ExternalFileProfile.inspectRaw(Paths.get(var0[1]), "自动识别", true);
         System.out
            .println("HX_CONVERT_INSPECT_OK type=" + var20.type + " leading_zero_columns=" + var20.leadingZeroColumns + " warnings=" + var20.warnings.size());

         for (String var22 : var20.warnings) {
            System.out.println("HX_CONVERT_WARNING " + var22);
         }
      } else if (var0.length != 2
         || !"--render-preview".equals(var0[0])
            && !"--render-missing-preview".equals(var0[0])
            && !"--render-missing-results-preview".equals(var0[0])
            && !"--render-convert-preview".equals(var0[0])
            && !"--render-home-preview".equals(var0[0])
            && !"--render-method-preview".equals(var0[0])
            && !"--render-correlation-preview".equals(var0[0])
            && !"--render-workflow-preview".equals(var0[0])
            && !"--render-cluster-preview".equals(var0[0])
            && !"--render-monitor-preview".equals(var0[0])
            && !"--render-monitor-details-preview".equals(var0[0])
            && !"--render-graph-preview".equals(var0[0])
            && !"--render-did-preview".equals(var0[0])
            && !"--render-did-encode-preview".equals(var0[0])
            && !"--render-did-event-preview".equals(var0[0])
            && !"--render-did-pretrend-preview".equals(var0[0])
            && !"--render-oneclick-preview".equals(var0[0])
            && !"--render-oneclick-results-preview".equals(var0[0])
            && !"--render-regress-preview".equals(var0[0])) {
         System.out
            .println(
               "Usage: HxWorkbench --inspect-convert-file input.csv | --render-preview|--render-home-preview|--render-graph-preview|--render-did-preview|--render-oneclick-preview|--render-oneclick-results-preview output.png"
            );
      } else {
         boolean var1 = var0[0].startsWith("--render-missing");
         boolean var2 = "--render-missing-results-preview".equals(var0[0]);
         boolean var3 = "--render-convert-preview".equals(var0[0]);
         boolean var4 = "--render-home-preview".equals(var0[0]);
         boolean var5 = "--render-method-preview".equals(var0[0]);
         boolean var6 = "--render-correlation-preview".equals(var0[0]);
         boolean var7 = "--render-workflow-preview".equals(var0[0]);
         boolean var8 = "--render-cluster-preview".equals(var0[0]);
         boolean var9 = var0[0].startsWith("--render-monitor");
         boolean var10 = "--render-monitor-details-preview".equals(var0[0]);
         boolean var11 = "--render-graph-preview".equals(var0[0]);
         boolean var12 = "--render-did-preview".equals(var0[0]);
         boolean var13 = "--render-did-encode-preview".equals(var0[0]);
         boolean var14 = "--render-did-event-preview".equals(var0[0]);
         boolean var15 = "--render-did-pretrend-preview".equals(var0[0]);
         boolean var16 = "--render-oneclick-preview".equals(var0[0]);
         boolean var17 = "--render-oneclick-results-preview".equals(var0[0]);
         boolean var18 = "--render-regress-preview".equals(var0[0]);
         String var19 = var0[1];
         SwingUtilities.invokeAndWait(() -> {
            try {
               setNativeLookAndFeel();
               HxWorkbench.WorkbenchFrame var19x = new HxWorkbench.WorkbenchFrame(true);
               if (var1) {
                  var19x.populateMissingPreviewState();
               }

               if (var2) {
                  var19x.populateMissingResultsPreviewState();
               }

               if (var3) {
                  var19x.populateConvertPreviewState();
               }

               if (var4) {
                  var19x.populateHomePreviewState();
               }

               if (var5) {
                  var19x.browseMethod("reg", "线性模型");
               }

               if (var6) {
                  var19x.browseMethod("stats", "相关分析");
               }

               if (var7) {
                  var19x.browseMethodCategory("did");
               }

               if (var8) {
                  var19x.populateClusterPreviewState();
               }

               if (var9) {
                  var19x.populateMonitorPreviewState();
               }

               if (var10) {
                  var19x.populateMonitorDetailsPreviewState();
               }

               if (var11) {
                  var19x.populateGraphPreviewState();
               }

               if (var12) {
                  var19x.populateDidPreviewState();
               }

               if (var13) {
                  var19x.populateDidActionPreviewState("生成事件研究编码 event_code");
               }

               if (var14) {
                  var19x.populateDidActionPreviewState("事件研究回归");
               }

               if (var15) {
                  var19x.populateDidActionPreviewState("政策前联合显著性检验");
               }

               if (var16) {
                  var19x.populateOneClickPreviewState();
               }

               if (var17) {
                  var19x.populateOneClickResultsPreviewState();
               }

               if (var18) {
                  var19x.openBaselineRegressionWorkspace();
               }

               var19x.setSize(1672, 901);
               var19x.addNotify();
               Container var20x = var19x.getContentPane();
               var20x.setSize(1672, 901);
               var19x.validate();
               layoutTree(var20x);
               var19x.applyDividerRatios();
               layoutTree(var20x);
               BufferedImage var21 = new BufferedImage(var20x.getWidth(), var20x.getHeight(), 1);
               Graphics2D var22x = var21.createGraphics();
               var20x.printAll(var22x);
               var22x.dispose();
               ImageIO.write(var21, "png", new File(var19));
               var19x.dispose();
               System.out.println("HX_UI_PREVIEW_OK " + var19);
            } catch (Exception var23) {
               throw new RuntimeException(var23);
            }
         });
      }
   }

   private static void layoutTree(Container var0) {
      var0.doLayout();

      for (Component var4 : var0.getComponents()) {
         if (var4 instanceof Container) {
            layoutTree((Container)var4);
         }
      }
   }

   public static int launch(String[] var0) {
      SwingUtilities.invokeLater(() -> {
         try {
            setNativeLookAndFeel();
            if (frame == null || !frame.isDisplayable()) {
               frame = new HxWorkbench.WorkbenchFrame();
            }

            frame.setVisible(true);
            frame.setExtendedState(frame.getExtendedState() | 6);
            Timer var0x = new Timer(450, var0xx -> frame.applyDividerRatios());
            var0x.setRepeats(false);
            var0x.start();
            frame.setExtendedState(frame.getExtendedState() & -2);
            frame.toFront();
            frame.requestFocus();
            frame.refreshDataset(false);
         } catch (Throwable var1) {
            SFIToolkit.errorln("单窗口工作台启动失败：" + var1.getMessage());
            SFIToolkit.errorln(SFIToolkit.stackTraceToString(var1));
         }
      });
      return 0;
   }

   public static int selfTest(String[] var0) {
      try {
         long var1 = Data.getObsTotal();
         int var3 = Data.getVarCount();
         if (var3 <= 0 || Data.getVarName(1) != null && !Data.getVarName(1).isBlank()) {
            int var4 = SFIToolkit.executeCommand("quietly hxresolve regress", false);
            if (var4 != 0) {
               return var4;
            } else {
               String var5 = HxWorkbench.StataBridge.characteristic("hxtoolbox_sem_title");
               if (!var5.contains("regress")) {
                  SFIToolkit.errorln("HX_JAVA_SELFTEST_SCHEMA_MISSING");
                  return 459;
               } else {
                  SFIToolkit.displayln("HX_JAVA_SELFTEST_OK N=" + var1 + " K=" + var3 + " TITLE=" + var5);
                  return 0;
               }
            }
         } else {
            SFIToolkit.errorln("HX_JAVA_SELFTEST_BAD_FIRST_VARIABLE");
            return 459;
         }
      } catch (Throwable var6) {
         SFIToolkit.errorln("HX_JAVA_SELFTEST_EXCEPTION " + var6.getMessage());
         return 459;
      }
   }

   public static int version(String[] var0) {
      SFIToolkit.displayln("HxWorkbench 1.4.8");
      return 0;
   }

   public static int missingSelfTest(String[] var0) {
      try {
         if (Data.getVarIndex("price") > 0 && Data.getVarIndex("rep78") > 0) {
            HxWorkbench.MissingAnalysisResult var1 = HxWorkbench.MissingAnalysisResult.compute(
               Arrays.asList("price", "rep78"), Collections.singletonList("foreign"), 1, true, true, 1, 0.0, "缺失率从高到低"
            );
            if (var1.overallRows.size() == 2 && !var1.separateRows.isEmpty() && !var1.recordRows.isEmpty()) {
               SFIToolkit.displayln("HX_MISSING_SELFTEST_OK overall=" + var1.overallRows.size() + " records=" + var1.recordRows.size());
               return 0;
            } else {
               SFIToolkit.errorln("HX_MISSING_SELFTEST_BAD_RESULT");
               return 459;
            }
         } else {
            SFIToolkit.errorln("HX_MISSING_SELFTEST_REQUIRES_AUTO");
            return 459;
         }
      } catch (Throwable var2) {
         SFIToolkit.errorln("HX_MISSING_SELFTEST_EXCEPTION " + var2.getMessage());
         return 459;
      }
   }

   public static int conversionSelfTest(String[] var0) {
      String var1 = Macro.getGlobal("HX_CONVERT_TEST_INPUT");
      String var2 = Macro.getGlobal("HX_CONVERT_TEST_OUTPUT");
      if (var1 != null && !var1.isBlank() && var2 != null && !var2.isBlank()) {
         Path var3 = Paths.get(var1);
         Path var4 = Paths.get(var2);
         String var5 = "__hxconvtest";
         long var6 = Data.getObsTotal();
         Frame var8 = null;

         short var14;
         try {
            HxWorkbench.ExternalFileProfile var9 = HxWorkbench.ExternalFileProfile.inspectRaw(var3, "自动识别", true);

            try {
               Frame.connect(var5).drop();
            } catch (Throwable var29) {
            }

            var8 = Frame.create(var5);
            String var32 = var3.toString().toLowerCase(Locale.ROOT);
            String var11;
            if (!var32.endsWith(".xlsx") && !var32.endsWith(".xls")) {
               var11 = "frame " + var5 + ": import delimited using " + HxWorkbench.WorkbenchFrame.commandQuote(var3.toString()) + ", clear varnames(1)";
               if (!var9.leadingZeroColumns.isEmpty()) {
                  var11 = var11 + " stringcols(" + var9.leadingZeroColumns.get(0) + ")";
               }
            } else {
               var11 = "frame " + var5 + ": import excel using " + HxWorkbench.WorkbenchFrame.commandQuote(var3.toString()) + ", firstrow clear";
            }

            int var12 = SFIToolkit.executeCommand(var11, false);
            if (var12 != 0) {
               return var12;
            }

            var8 = Frame.connect(var5);
            int var13 = var8.getVarIndex("stkcd");
            if (var13 <= 0 || !var8.isVarTypeString(var13) || !"000001".equals(var8.getStr(var13, 1L))) {
               SFIToolkit.errorln("HX_CONVERT_SELFTEST_LEADING_ZERO_LOST");
               return 459;
            }

            var12 = SFIToolkit.executeCommand("frame " + var5 + ": save " + HxWorkbench.WorkbenchFrame.commandQuote(var4.toString()) + ", replace", false);
            if (var12 != 0 || !Files.isRegularFile(var4)) {
               return var12 == 0 ? 603 : var12;
            }

            if (Data.getObsTotal() == var6) {
               SFIToolkit.displayln(
                  "HX_CONVERT_SELFTEST_OK type="
                     + HxWorkbench.ExternalFileProfile.inspectRaw(var3, "自动识别", true).type
                     + " N="
                     + var8.getObsTotal()
                     + " K="
                     + var8.getVarCount()
               );
               return 0;
            }

            SFIToolkit.errorln("HX_CONVERT_SELFTEST_CURRENT_DATA_CHANGED");
            var14 = 459;
         } catch (Throwable var30) {
            SFIToolkit.errorln("HX_CONVERT_SELFTEST_EXCEPTION " + var30.getMessage());
            return 459;
         } finally {
            if (var8 != null) {
               try {
                  var8.drop();
               } catch (Throwable var28) {
               }
            }
         }

         return var14;
      } else {
         SFIToolkit.errorln("HX_CONVERT_SELFTEST_PATHS_MISSING");
         return 198;
      }
   }

   private static void setNativeLookAndFeel() {
      try {
         UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
      } catch (Exception var6) {
      }

      HashSet var0 = new HashSet<>(Arrays.asList(GraphicsEnvironment.getLocalGraphicsEnvironment().getAvailableFontFamilyNames()));
      String var1 = "SansSerif";

      for (String var3 : Arrays.asList("Microsoft YaHei UI", "PingFang SC", "Noto Sans CJK SC", "Source Han Sans SC", "Arial Unicode MS")) {
         if (var0.contains(var3)) {
            var1 = var3;
            break;
         }
      }

      Font var7 = new Font(var1, 0, 12);

      for (Object var4 : UIManager.getDefaults().keySet()) {
         Object var5 = UIManager.get(var4);
         if (var5 instanceof Font) {
            UIManager.put(var4, new FontUIResource(var7));
         }
      }

      UIManager.put("ToolTip.background", new Color(255, 255, 255));
      UIManager.put("ToolTip.foreground", new Color(29, 41, 57));
      UIManager.put("ToolTip.border", BorderFactory.createLineBorder(new Color(214, 220, 229)));
   }

   private static <T> T safe(HxWorkbench.UnsafeSupplier<T> var0, T var1) {
      try {
         Object var2 = var0.get();
         return (T)(var2 == null ? var1 : var2);
      } catch (Throwable var3) {
         return (T)var1;
      }
   }

   private static final class BatchConversionConfig {
      final boolean excelFirstRow;
      final boolean excelAllString;
      final boolean delimitedFirstRow;
      final String delimiter;
      final String encoding;
      final boolean protectLeadingZeros;
      final boolean skipExisting;

      private BatchConversionConfig(boolean var1, boolean var2, boolean var3, String var4, String var5, boolean var6, boolean var7) {
         this.excelFirstRow = var1;
         this.excelAllString = var2;
         this.delimitedFirstRow = var3;
         this.delimiter = var4;
         this.encoding = var5;
         this.protectLeadingZeros = var6;
         this.skipExisting = var7;
      }
   }

   private static final class BatchProgress {
      final int completed;
      final int total;
      final String fileName;
      final String status;
      final String detail;
      final int rc;

      private BatchProgress(int var1, int var2, String var3, String var4, String var5, int var6) {
         this.completed = var1;
         this.total = var2;
         this.fileName = var3;
         this.status = var4;
         this.detail = var5;
         this.rc = var6;
      }
   }

   private static final class BatchSummary {
      final int total;
      final List<Object[]> rows = new ArrayList<>();
      final List<String> failures = new ArrayList<>();
      int success;
      int failed;
      int skipped;
      int firstRc;
      boolean stopped;

      private BatchSummary(int var1) {
         this.total = var1;
      }

      static HxWorkbench.BatchSummary crashed(int var0, String var1) {
         HxWorkbench.BatchSummary var2 = new HxWorkbench.BatchSummary(var0);
         var2.failed = var0;
         var2.firstRc = 459;
         var2.failures.add("批量任务中断：" + var1);
         var2.rows.add(new Object[]{"批量任务", "-", "失败", var1});
         return var2;
      }
   }

   private static final class Category {
      private final String label;
      private final String code;

      private Category(String var1, String var2) {
         this.label = var1;
         this.code = var2;
      }

      @Override
      public String toString() {
         return this.label;
      }
   }

   private static final class ConversionOutcome {
      final boolean success;
      final Path input;
      final Path output;
      final int rc;
      final long n;
      final int k;
      final long bytes;
      final String message;

      private ConversionOutcome(boolean var1, Path var2, Path var3, int var4, long var5, int var7, long var8, String var10) {
         this.success = var1;
         this.input = var2;
         this.output = var3;
         this.rc = var4;
         this.n = var5;
         this.k = var7;
         this.bytes = var8;
         this.message = var10;
      }

      static HxWorkbench.ConversionOutcome success(Path var0, Path var1, long var2, int var4, long var5) {
         return new HxWorkbench.ConversionOutcome(true, var0, var1, 0, var2, var4, var5, "");
      }

      static HxWorkbench.ConversionOutcome failure(Path var0, Path var1, String var2) {
         return failure(var0, var1, 459, var2);
      }

      static HxWorkbench.ConversionOutcome failure(Path var0, Path var1, int var2, String var3) {
         return new HxWorkbench.ConversionOutcome(false, var0, var1, var2, 0L, 0, 0L, var3 == null ? "未知错误" : var3);
      }
   }

   private static final class DataTableModel extends AbstractTableModel {
      private int rows;
      private int cols;
      private List<String> names = Collections.emptyList();
      private Object[][] previewValues;
      private List<Long> visibleObservations;

      void reload() {
         this.previewValues = null;
         this.visibleObservations = null;
         long var1 = Data.getObsTotal();
         this.rows = (int)Math.min(2147483647L, Math.max(0L, var1));
         this.cols = Math.max(0, Data.getVarCount());
         ArrayList var3 = new ArrayList(this.cols);

         for (int var4 = 1; var4 <= this.cols; var4++) {
            int var5 = var4;
            var3.add(HxWorkbench.safe(() -> Data.getVarName(var5), "var" + var5));
         }

         this.names = var3;
         this.fireTableStructureChanged();
      }

      void showRows(List<Long> var1) {
         this.previewValues = null;
         this.visibleObservations = new ArrayList<>();
         long var2 = Data.getObsTotal();

         for (Long var5 : var1) {
            if (var5 != null && var5 >= 1L && var5 <= var2) {
               this.visibleObservations.add(var5);
            }
         }

         this.rows = this.visibleObservations.size();
         this.fireTableDataChanged();
      }

      void clearRowFilter() {
         this.visibleObservations = null;
      }

      void loadPreview() {
         this.names = Arrays.asList("make", "price", "mpg", "rep78", "headroom", "trunk", "weight");
         this.previewValues = new Object[][]{
            {"AMC Concord", "4,099", "22", "3", "2.5", "11", "2,930"},
            {"AMC Pacer", "4,749", "17", "3", "3.0", "11", "3,350"},
            {"AMC Spirit", "3,799", "22", ".", "3.0", "12", "2,640"},
            {"Buick Century", "4,816", "20", "3", "4.5", "16", "3,250"},
            {"Buick Electra", "7,827", "15", "4", "4.0", "20", "4,080"},
            {"Buick LeSabre", "5,788", "18", "3", "4.0", "21", "3,670"},
            {"Buick Opel", "4,453", "26", ".", "3.0", "10", "2,230"},
            {"Buick Regal", "5,189", "20", "3", "2.0", "16", "3,280"},
            {"Buick Riviera", "10,372", "16", "3", "3.5", "17", "3,880"},
            {"Buick Skylark", "4,082", "19", "3", "3.5", "13", "3,400"},
            {"Cad. Deville", "11,385", "14", "3", "4.0", "20", "4,330"},
            {"Cad. Eldorado", "14,500", "14", "2", "3.5", "16", "3,900"}
         };
         this.rows = this.previewValues.length;
         this.cols = this.names.size();
         this.fireTableStructureChanged();
      }

      @Override
      public int getRowCount() {
         return this.rows;
      }

      @Override
      public int getColumnCount() {
         return this.cols;
      }

      @Override
      public String getColumnName(int var1) {
         return this.names.get(var1);
      }

      @Override
      public boolean isCellEditable(int var1, int var2) {
         return false;
      }

      @Override
      public Object getValueAt(int var1, int var2) {
         if (this.previewValues != null) {
            return this.previewValues[var1][var2];
         } else {
            long var3 = this.visibleObservations == null ? var1 + 1L : this.visibleObservations.get(var1);
            return HxWorkbench.safe(() -> Data.getFormattedValue(var2 + 1, var3, true), "");
         }
      }
   }

   private static final class DatasetSnapshot {
      private static final int CELL_LIMIT = 120000;
      final long n;
      final int k;
      final int sampleRows;
      final int sampleCols;
      final List<String> names;
      final String[][] values;

      private DatasetSnapshot(long var1, int var3, int var4, int var5, List<String> var6, String[][] var7) {
         this.n = var1;
         this.k = var3;
         this.sampleRows = var4;
         this.sampleCols = var5;
         this.names = var6;
         this.values = var7;
      }

      static HxWorkbench.DatasetSnapshot capture() {
         int var0 = Data.getVarCount();
         int var1 = Math.max(0, Math.min(var0, 250));
         int var2 = var1 == 0 ? 0 : (int)Math.min(Data.getObsTotal(), (long)Math.max(1, 120000 / var1));
         return captureWithShape(var2, var1);
      }

      static HxWorkbench.DatasetSnapshot captureWithShape(int var0, int var1) {
         long var2 = Data.getObsTotal();
         int var4 = Data.getVarCount();
         int var5 = Math.min(var4, Math.max(0, var1));
         if (var5 > 0 && (long)var0 * var5 > 120000L) {
            var0 = 120000 / var5;
         }

         int var6 = (int)Math.min(var2, (long)Math.max(0, var0));
         ArrayList var7 = new ArrayList(var4);

         for (int var8 = 1; var8 <= var4; var8++) {
            final int varIndex = var8;
            var7.add(HxWorkbench.safe(() -> Data.getVarName(varIndex), "var" + varIndex));
         }

         String[][] var13 = new String[var6][var5];

         for (int var9 = 0; var9 < var6; var9++) {
            for (int var10 = 0; var10 < var5; var10++) {
               int var11 = var10;
               int var12 = var9;
               var13[var9][var10] = HxWorkbench.safe(() -> Data.getFormattedValue(var11 + 1, var12 + 1L, true), "");
            }
         }

         return new HxWorkbench.DatasetSnapshot(var2, var4, var6, var5, var7, var13);
      }

      String value(int var1, int var2) {
         return this.values[var1][var2];
      }

      Map<String, Integer> nameIndex() {
         LinkedHashMap var1 = new LinkedHashMap();

         for (int var2 = 0; var2 < this.names.size(); var2++) {
            var1.put(this.names.get(var2), var2);
         }

         return var1;
      }
   }

   private static final class ExternalFileProfile {
      final Path input;
      final String type;
      final String encoding;
      final List<String> sheetNames = new ArrayList<>();
      final List<Integer> leadingZeroColumns = new ArrayList<>();
      final LinkedHashSet<String> warnings = new LinkedHashSet<>();
      long n;
      int k;
      int numericVariables;
      int stringVariables;
      int possibleDates;
      int emptyColumns;

      private ExternalFileProfile(Path var1, String var2, String var3) {
         this.input = var1;
         this.type = var2;
         this.encoding = var3 == null ? "" : var3;
      }

      static HxWorkbench.ExternalFileProfile inspectRaw(Path var0, String var1, boolean var2) throws IOException {
         return inspectRaw(var0, var1, var2, "自动识别");
      }

      static HxWorkbench.ExternalFileProfile inspectRaw(Path var0, String var1, boolean var2, String var3) throws IOException {
         String var4 = HxWorkbench.WorkbenchFrame.externalType(var0);
         String var5 = var4.equals("delimited") ? resolveEncoding(var0, var3) : "";
         HxWorkbench.ExternalFileProfile var6 = new HxWorkbench.ExternalFileProfile(var0, var4, var5);
         if (var4.equals("excel")) {
            var6.sheetNames.addAll(HxWorkbench.XlsxInspector.sheetNames(var0));
            if (var0.toString().toLowerCase(Locale.ROOT).endsWith(".xls")) {
               var6.warnings.add("旧版 .xls 无法在 Java 预览层可靠读取工作表名；未指定工作表时由 Stata 读取默认工作表。");
            }

            return var6;
         } else {
            if ("自动识别".equals(var3) && !var5.isBlank() && !"UTF-8".equalsIgnoreCase(var5)) {
               var6.warnings.add("文件编码自动识别为 " + var5 + "；导入命令会显式使用该编码。");
            }

            inspectDelimited(var6, var1, var2, Charset.forName(var5));
            return var6;
         }
      }

      private static String resolveEncoding(Path var0, String var1) throws IOException {
         String var2 = var1 == null ? "自动识别" : var1.trim();
         if (!var2.isBlank() && !"自动识别".equals(var2)) {
            Charset.forName(var2);
            return var2;
         } else {
            byte[] var3;
            try (InputStream var4 = Files.newInputStream(var0)) {
               ByteArrayOutputStream var5 = new ByteArrayOutputStream();
               byte[] var6 = new byte[8192];
               int var8 = 65536;

               int var7;
               while (var8 > 0 && (var7 = var4.read(var6, 0, Math.min(var6.length, var8))) > 0) {
                  var5.write(var6, 0, var7);
                  var8 -= var7;
               }

               var3 = var5.toByteArray();
            }

            if (var3.length >= 3 && (var3[0] & 255) == 239 && (var3[1] & 255) == 187 && (var3[2] & 255) == 191) {
               return "UTF-8";
            } else if (decodesStrictly(var3, StandardCharsets.UTF_8)) {
               return "UTF-8";
            } else {
               Charset var11 = Charset.forName("GB18030");
               return decodesStrictly(var3, var11) ? "GB18030" : "Windows-1252";
            }
         }
      }

      private static boolean decodesStrictly(byte[] var0, Charset var1) {
         try {
            var1.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(var0));
            return true;
         } catch (CharacterCodingException var3) {
            return false;
         }
      }

      private static void inspectDelimited(HxWorkbench.ExternalFileProfile var0, String var1, boolean var2, Charset var3) throws IOException {
         ArrayList<List<String>> var4 = new ArrayList<>();

         try (BufferedReader var5 = Files.newBufferedReader(var0.input, var3)) {
            String var6 = var5.readLine();
            if (var6 == null) {
               return;
            }

            char var7 = delimiterCharacter(var1, var6);
            var4.add(parseDelimited(var6, var7));

            String var8;
            while (var4.size() < 300 && (var8 = var5.readLine()) != null) {
               var4.add(parseDelimited(var8, var7));
            }
         }

         if (!var4.isEmpty()) {
            int var18 = var4.stream().mapToInt(List::size).max().orElse(0);
            ArrayList<String> var19 = new ArrayList<>();
            if (var2) {
               var19.addAll((Collection)var4.get(0));
            }

            while (var19.size() < var18) {
               var19.add("v" + (var19.size() + 1));
            }

            HashSet<String> var20 = new HashSet<>();

            for (String var9 : var19) {
               String var10 = var9 == null ? "" : var9.trim();
               if (!var20.add(var10.toLowerCase(Locale.ROOT))) {
                  var0.warnings.add("发现重复变量名：" + var10);
               }

               if (var10.length() > 32) {
                  var0.warnings.add("变量名超过 32 个字符：" + var10);
               }

               if (!var10.matches("[A-Za-z_][A-Za-z0-9_]*")) {
                  var0.warnings.add("部分变量名含中文、空格或特殊字符；Stata 会生成合法变量名。原始文件不会修改。");
               }
            }

            int var22 = var2 ? 1 : 0;

            for (int var23 = 0; var23 < var18; var23++) {
               boolean var24 = false;
               boolean var11 = false;
               int var12 = 0;
               int var13 = 0;

               for (int var14 = var22; var14 < var4.size(); var14++) {
                  String var15 = var23 < ((List)var4.get(var14)).size() ? ((String)((List)var4.get(var14)).get(var23)).trim() : "";
                  if (!var15.isEmpty()) {
                     var11 = true;
                     if (var15.matches("0[0-9]+")) {
                        var24 = true;
                     }

                     if (isNumericText(var15)) {
                        var12++;
                     } else {
                        var13++;
                     }
                  }
               }

               if (var24) {
                  var0.leadingZeroColumns.add(var23 + 1);
                  var0.warnings.add("第 " + (var23 + 1) + " 列（" + (String)var19.get(var23) + "）检测到前导零，将按字符串读取。");
               }

               if (var12 > 0 && var13 > 0) {
                  var0.warnings.add("第 " + (var23 + 1) + " 列（" + (String)var19.get(var23) + "）同时包含数字和文本，建议作为字符串检查。");
               }

               if (!var11) {
                  var0.warnings.add("第 " + (var23 + 1) + " 列（" + (String)var19.get(var23) + "）在预览样本中完全为空。");
               }
            }
         }
      }

      void enrichFromFrame(Frame var1) {
         this.n = var1.getObsTotal();
         this.k = var1.getVarCount();
         long var2 = Math.min(this.n, 5000L);

         for (int var4 = 1; var4 <= this.k; var4++) {
            int var5 = var4;
            boolean var6 = var1.isVarTypeString(var4);
            if (var6) {
               this.stringVariables++;
            } else {
               this.numericVariables++;
            }

            String var7 = HxWorkbench.safe(() -> var1.getVarName(var5), "v" + var4);
            boolean var8 = false;
            boolean var9 = var7.toLowerCase(Locale.ROOT).matches(".*(date|time|year|month|日期|年份).*");
            boolean var10 = false;

            for (long var11 = 1L; var11 <= var2; var11++) {
               long var13 = var11;
               if (var6) {
                  String var15 = HxWorkbench.safe(() -> var1.getStr(var5, var13), "");
                  if (var15 != null && !var15.isBlank()) {
                     var8 = true;
                     if (var15.trim().matches("0[0-9]+")) {
                        var10 = true;
                     }

                     if (var15.matches("\\d{4}[-/]\\d{1,2}[-/]\\d{1,2}.*")) {
                        var9 = true;
                     }
                  }
               } else if (!Missing.isMissing(var1.getNum(var4, var11))) {
                  var8 = true;
               }
            }

            if (!var8) {
               this.emptyColumns++;
            }

            if (var9) {
               this.possibleDates++;
            }

            if (var10 && !this.leadingZeroColumns.contains(var4)) {
               this.leadingZeroColumns.add(var4);
               this.warnings.add("变量 " + var7 + " 检测到前导零；建议保留为字符串。");
            }

            if (!var6 && var7.toLowerCase(Locale.ROOT).matches(".*(stkcd|stockcode|code|id|代码).*")) {
               this.warnings.add("变量 " + var7 + " 看起来像代码但被识别为数值；请核对是否需要保留前导零。");
            }
         }
      }

      String firstSheet() {
         return this.sheetNames.isEmpty() ? "" : this.sheetNames.get(0);
      }

      String detectedSummary() {
         String var1 = this.type.equals("excel") ? "Excel" : (this.input.toString().toLowerCase(Locale.ROOT).endsWith(".csv") ? "CSV" : "文本");
         return "已识别：" + var1 + "　预计 " + this.n + " 行 × " + this.k + " 列";
      }

      String previewSummary() {
         return "转换前预览 | 预计观测数：" + this.n + " | 预计变量数：" + this.k + " | 数值：" + this.numericVariables + " | 字符串：" + this.stringVariables;
      }

      String issueSummary() {
         StringBuilder var1 = new StringBuilder();
         var1.append("检测摘要\n\n数值变量：")
            .append(this.numericVariables)
            .append("\n字符串变量：")
            .append(this.stringVariables)
            .append("\n可能的日期变量：")
            .append(this.possibleDates)
            .append("\n完全空列：")
            .append(this.emptyColumns)
            .append("\n\n");
         if (this.warnings.isEmpty()) {
            return var1.append("没有发现明显的类型风险。转换仍建议抽查关键代码列。").toString();
         } else {
            var1.append("发现 ").append(this.warnings.size()).append(" 个需要注意的问题：\n\n");
            int var2 = 1;

            for (String var4 : this.warnings) {
               var1.append(var2++).append(". ").append(var4).append("\n\n");
            }

            var1.append("工具只提示风险，不会修改原始文件。");
            return var1.toString();
         }
      }

      private static boolean isNumericText(String var0) {
         String var1 = var0.replace(",", "").replace("%", "");
         return var1.matches("[+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)(?:[eE][+-]?\\d+)?");
      }

      private static char delimiterCharacter(String var0, String var1) {
         switch (var0) {
            case "Tab":
               return '\t';
            case "逗号":
               return ',';
            case "分号":
               return ';';
            case "空格":
               return ' ';
            case "竖线":
               return '|';
            default:
               char[] var4 = new char[]{',', '\t', ';', '|'};
               char var5 = ',';
               int var6 = -1;

               for (char var10 : var4) {
                  int var11 = 0;

                  for (int var12 = 0; var12 < var1.length(); var12++) {
                     if (var1.charAt(var12) == var10) {
                        var11++;
                     }
                  }

                  if (var11 > var6) {
                     var6 = var11;
                     var5 = var10;
                  }
               }

               return var5;
         }
      }

      private static List<String> parseDelimited(String var0, char var1) {
         ArrayList var2 = new ArrayList();
         StringBuilder var3 = new StringBuilder();
         boolean var4 = false;

         for (int var5 = 0; var5 < var0.length(); var5++) {
            char var6 = var0.charAt(var5);
            if (var6 == '"') {
               if (var4 && var5 + 1 < var0.length() && var0.charAt(var5 + 1) == '"') {
                  var3.append('"');
                  var5++;
               } else {
                  var4 = !var4;
               }
            } else if (var6 == var1 && !var4) {
               var2.add(var3.toString());
               var3.setLength(0);
            } else {
               var3.append(var6);
            }
         }

         var2.add(var3.toString());
         return var2;
      }
   }

   private static final class GraphPreviewPanel extends JPanel {
      private String title = "选择图形命令和变量后显示即时预览";
      private String mode = "message";
      private List<Double> x = Collections.emptyList();
      private List<Double> y = Collections.emptyList();
      private List<Double> group = Collections.emptyList();
      private boolean fitted;

      GraphPreviewPanel() {
         this.setBackground(Color.WHITE);
         this.setBorder(new EmptyBorder(14, 14, 14, 14));
      }

      void showMessage(String var1) {
         this.title = var1;
         this.mode = "message";
         this.x = this.y = this.group = Collections.emptyList();
         this.repaint();
      }

      void loadDistribution(String var1, String var2) {
         this.y = numericSample(var1, 1800);
         this.x = Collections.emptyList();
         this.mode = "graph_box".equals(var2) ? "box" : "distribution";
         this.title = var1.isBlank() ? "请选择数值变量" : var1 + ("kdensity".equals(var2) ? " · 核密度近似预览" : " · 分布预览");
         this.repaint();
      }

      void loadXY(String var1, String var2, boolean var3) {
         List var4 = numericPairs(var2, var1, 1200);
         this.x = (List<Double>)var4.get(0);
         this.y = (List<Double>)var4.get(1);
         this.group = Collections.emptyList();
         this.fitted = var3;
         this.mode = "xy";
         this.title = var1 + " 与 " + var2 + (var3 ? " · 线性拟合" : " · 散点关系");
         this.repaint();
      }

      void setPreviewXY(List<Double> var1, List<Double> var2, boolean var3, String var4) {
         this.x = new ArrayList<>(var1);
         this.y = new ArrayList<>(var2);
         this.group = Collections.emptyList();
         this.fitted = var3;
         this.mode = "xy";
         this.title = var4;
         this.repaint();
      }

      void loadTrend(String var1, String var2, String var3) {
         int var4 = HxWorkbench.safe(() -> Data.getVarIndex(var1), -1);
         int var5 = HxWorkbench.safe(() -> Data.getVarIndex(var2), -1);
         int var6 = HxWorkbench.safe(() -> Data.getVarIndex(var3), -1);
         TreeMap<String, double[]> var7 = new TreeMap<>((var0, var1x) -> {
            try {
               return Double.compare(Double.parseDouble(var0.split("\\|")[0]), Double.parseDouble(var1x.split("\\|")[0]));
            } catch (Exception var3x) {
               return var0.compareTo(var1x);
            }
         });
         if (var4 > 0 && var5 > 0 && var6 > 0 && !Data.isVarTypeString(var4) && !Data.isVarTypeString(var5) && !Data.isVarTypeString(var6)) {
            long var8 = Math.min(Data.getObsTotal(), 200000L);

            for (long var10 = 1L; var10 <= var8; var10++) {
               long var12 = var10;
               double var14 = HxWorkbench.safe(() -> Data.getNum(var4, var12), Double.NaN);
               double var16 = HxWorkbench.safe(() -> Data.getNum(var5, var12), Double.NaN);
               double var18 = HxWorkbench.safe(() -> Data.getNum(var6, var12), Double.NaN);
               if (!Missing.isMissing(var14) && !Missing.isMissing(var16) && !Missing.isMissing(var18)) {
                  String var20 = var16 + "|" + var18;
                  double[] var21 = var7.computeIfAbsent(var20, var0 -> new double[2]);
                  var21[0] += var14;
                  var21[1]++;
               }
            }
         }

         this.x = new ArrayList<>();
         this.y = new ArrayList<>();
         this.group = new ArrayList<>();

         for (Entry<String, double[]> var9 : var7.entrySet()) {
            String[] var23 = ((String)var9.getKey()).split("\\|");
            this.x.add(Double.parseDouble(var23[0]));
            this.group.add(Double.parseDouble(var23[1]));
            this.y.add(((double[])var9.getValue())[0] / ((double[])var9.getValue())[1]);
         }

         this.mode = "trend";
         this.title = "处理组 / 对照组平均趋势预览";
         this.repaint();
      }

      @Override
      protected void paintComponent(Graphics var1) {
         super.paintComponent(var1);
         Graphics2D var2 = (Graphics2D)var1.create();
         var2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
         var2.setColor(new Color(24, 34, 48));
         var2.setFont(var2.getFont().deriveFont(1, 13.0F));
         drawMultiline(var2, this.title, 8, 20);
         byte var3 = 48;
         byte var4 = 56;
         int var5 = Math.max(80, this.getWidth() - 72);
         int var6 = Math.max(80, this.getHeight() - 94);
         if (!"message".equals(this.mode) && !this.y.isEmpty()) {
            var2.setColor(new Color(222, 227, 234));
            var2.drawLine(var3, var4 + var6, var3 + var5, var4 + var6);
            var2.drawLine(var3, var4, var3, var4 + var6);
            if ("distribution".equals(this.mode)) {
               this.paintHistogram(var2, var3, var4, var5, var6);
            } else if ("box".equals(this.mode)) {
               this.paintBox(var2, var3, var4, var5, var6);
            } else if ("xy".equals(this.mode)) {
               this.paintXY(var2, var3, var4, var5, var6);
            } else {
               this.paintTrend(var2, var3, var4, var5, var6);
            }

            var2.dispose();
         } else {
            var2.setColor(new Color(99, 112, 131));
            var2.drawString("选择有效数值变量后显示；正式结果仍由 Stata Graph 窗口输出。", 8, 58);
            var2.dispose();
         }
      }

      private void paintHistogram(Graphics2D var1, int var2, int var3, int var4, int var5) {
         double var6 = min(this.y);
         double var8 = max(this.y);
         if (var8 <= var6) {
            var8 = var6 + 1.0;
         }

         int var10 = Math.max(8, Math.min(28, (int)Math.sqrt(this.y.size())));
         int[] var11 = new int[var10];

         for (double var13 : this.y) {
            var11[Math.min(var10 - 1, (int)((var13 - var6) / (var8 - var6) * var10))]++;
         }

         int var16 = Arrays.stream(var11).max().orElse(1);
         var1.setColor(new Color(74, 128, 198));

         for (int var17 = 0; var17 < var10; var17++) {
            int var14 = (int)((double)(var5 * var11[var17]) / var16);
            int var15 = var2 + var17 * var4 / var10;
            var1.fillRect(var15 + 1, var3 + var5 - var14, Math.max(2, var4 / var10 - 2), var14);
         }
      }

      private void paintBox(Graphics2D var1, int var2, int var3, int var4, int var5) {
         ArrayList var6 = new ArrayList<>(this.y);
         Collections.sort(var6);
         double var7 = (Double)var6.get(0);
         double var9 = (Double)var6.get(var6.size() - 1);
         if (var9 <= var7) {
            var9 = var7 + 1.0;
         }

         double var11 = (Double)var6.get(var6.size() / 4);
         double var13 = (Double)var6.get(var6.size() / 2);
         double var15 = (Double)var6.get(var6.size() * 3 / 4);
         int var17 = var3 + var5 / 2;
         int var18 = Math.min(90, var5 / 3);
         int var19 = map(var7, var7, var9, var2, var2 + var4);
         int var20 = map(var9, var7, var9, var2, var2 + var4);
         int var21 = map(var11, var7, var9, var2, var2 + var4);
         int var22 = map(var13, var7, var9, var2, var2 + var4);
         int var23 = map(var15, var7, var9, var2, var2 + var4);
         var1.setColor(new Color(74, 128, 198));
         var1.drawLine(var19, var17, var20, var17);
         var1.setColor(new Color(223, 235, 251));
         var1.fillRect(var21, var17 - var18 / 2, Math.max(1, var23 - var21), var18);
         var1.setColor(new Color(42, 102, 190));
         var1.drawRect(var21, var17 - var18 / 2, Math.max(1, var23 - var21), var18);
         var1.drawLine(var22, var17 - var18 / 2, var22, var17 + var18 / 2);
      }

      private void paintXY(Graphics2D var1, int var2, int var3, int var4, int var5) {
         double var6 = min(this.x);
         double var8 = max(this.x);
         double var10 = min(this.y);
         double var12 = max(this.y);
         if (var8 <= var6) {
            var8 = var6 + 1.0;
         }

         if (var12 <= var10) {
            var12 = var10 + 1.0;
         }

         var1.setColor(new Color(42, 102, 190, 125));

         for (int var14 = 0; var14 < Math.min(this.x.size(), this.y.size()); var14++) {
            int var15 = map(this.x.get(var14), var6, var8, var2, var2 + var4);
            int var16 = map(this.y.get(var14), var10, var12, var3 + var5, var3);
            var1.fillOval(var15 - 2, var16 - 2, 4, 4);
         }

         if (this.fitted && this.x.size() > 1) {
            double var26 = this.x.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
            double var27 = this.y.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
            double var18 = 0.0;
            double var20 = 0.0;

            for (int var22 = 0; var22 < this.x.size(); var22++) {
               var18 += (this.x.get(var22) - var26) * (this.y.get(var22) - var27);
               var20 += (this.x.get(var22) - var26) * (this.x.get(var22) - var26);
            }

            double var28 = var20 == 0.0 ? 0.0 : var18 / var20;
            double var24 = var27 - var28 * var26;
            var1.setColor(new Color(190, 54, 54));
            var1.setStroke(new BasicStroke(2.0F));
            var1.drawLine(
               var2, map(var24 + var28 * var6, var10, var12, var3 + var5, var3), var2 + var4, map(var24 + var28 * var8, var10, var12, var3 + var5, var3)
            );
         }
      }

      private void paintTrend(Graphics2D var1, int var2, int var3, int var4, int var5) {
         double var6 = min(this.x);
         double var8 = max(this.x);
         double var10 = min(this.y);
         double var12 = max(this.y);
         if (var8 <= var6) {
            var8 = var6 + 1.0;
         }

         if (var12 <= var10) {
            var12 = var10 + 1.0;
         }

         ArrayList var14 = new ArrayList<>(new TreeSet<>(this.group));
         Color[] var15 = new Color[]{new Color(42, 102, 190), new Color(220, 105, 56), new Color(34, 133, 79)};

         for (int var16 = 0; var16 < var14.size(); var16++) {
            Double var17 = (Double)var14.get(var16);
            int var18 = -1;
            int var19 = -1;
            var1.setColor(var15[var16 % var15.length]);
            var1.setStroke(new BasicStroke(2.0F));

            for (int var20 = 0; var20 < this.x.size(); var20++) {
               if (this.group.get(var20).equals(var17)) {
                  int var21 = map(this.x.get(var20), var6, var8, var2, var2 + var4);
                  int var22 = map(this.y.get(var20), var10, var12, var3 + var5, var3);
                  if (var18 >= 0) {
                     var1.drawLine(var18, var19, var21, var22);
                  }

                  var1.fillOval(var21 - 3, var22 - 3, 6, 6);
                  var18 = var21;
                  var19 = var22;
               }
            }

            var1.drawString("组 " + String.format(Locale.ROOT, "%.0f", var17), var2 + 8 + var16 * 70, var3 + 14);
         }
      }

      private static List<Double> numericSample(String var0, int var1) {
         int var2 = HxWorkbench.safe(() -> Data.getVarIndex(var0), -1);
         ArrayList var3 = new ArrayList();
         if (var2 > 0 && !Data.isVarTypeString(var2)) {
            long var4 = Data.getObsTotal();
            long var6 = Math.max(1L, var4 / Math.max(1, var1));

            for (long var8 = 1L; var8 <= var4 && var3.size() < var1; var8 += var6) {
               long var10 = var8;
               double var12 = HxWorkbench.safe(() -> Data.getNum(var2, var10), Double.NaN);
               if (!Missing.isMissing(var12)) {
                  var3.add(var12);
               }
            }

            return var3;
         } else {
            return var3;
         }
      }

      private static List<List<Double>> numericPairs(String var0, String var1, int var2) {
         int var3 = HxWorkbench.safe(() -> Data.getVarIndex(var0), -1);
         int var4 = HxWorkbench.safe(() -> Data.getVarIndex(var1), -1);
         ArrayList var5 = new ArrayList();
         ArrayList var6 = new ArrayList();
         if (var3 > 0 && var4 > 0 && !Data.isVarTypeString(var3) && !Data.isVarTypeString(var4)) {
            long var7 = Data.getObsTotal();
            long var9 = Math.max(1L, var7 / Math.max(1, var2));

            for (long var11 = 1L; var11 <= var7 && var5.size() < var2; var11 += var9) {
               long var13 = var11;
               double var15 = HxWorkbench.safe(() -> Data.getNum(var3, var13), Double.NaN);
               double var17 = HxWorkbench.safe(() -> Data.getNum(var4, var13), Double.NaN);
               if (!Missing.isMissing(var15) && !Missing.isMissing(var17)) {
                  var5.add(var15);
                  var6.add(var17);
               }
            }

            return Arrays.asList(var5, var6);
         } else {
            return Arrays.asList(var5, var6);
         }
      }

      private static int map(double var0, double var2, double var4, int var6, int var7) {
         return var6 + (int)Math.round((var0 - var2) / (var4 - var2) * (var7 - var6));
      }

      private static double min(List<Double> var0) {
         return var0.stream().mapToDouble(Double::doubleValue).min().orElse(0.0);
      }

      private static double max(List<Double> var0) {
         return var0.stream().mapToDouble(Double::doubleValue).max().orElse(1.0);
      }

      private static void drawMultiline(Graphics2D var0, String var1, int var2, int var3) {
         for (String var7 : var1.split("\\n")) {
            var0.drawString(var7, var2, var3);
            var3 += 18;
         }
      }
   }

   private static final class GroupAggregate {
      final HxWorkbench.GroupKey key;
      final long[] missingByVariable;
      long n;

      GroupAggregate(HxWorkbench.GroupKey var1, int var2) {
         this.key = var1;
         this.missingByVariable = new long[var2];
      }

      void add(boolean[] var1) {
         this.n++;

         for (int var2 = 0; var2 < var1.length; var2++) {
            if (var1[var2]) {
               this.missingByVariable[var2]++;
            }
         }
      }

      long missingTotal() {
         long var1 = 0L;

         for (long var6 : this.missingByVariable) {
            var1 += var6;
         }

         return var1;
      }

      int missingVariableCount() {
         int var1 = 0;

         for (long var5 : this.missingByVariable) {
            if (var5 > 0L) {
               var1++;
            }
         }

         return var1;
      }

      double rate() {
         return this.n != 0L && this.missingByVariable.length != 0 ? 100.0 * this.missingTotal() / (this.n * this.missingByVariable.length) : 0.0;
      }
   }

   private static final class GroupKey {
      final List<String> values;

      GroupKey(List<String> var1) {
         this.values = new ArrayList<>(var1);
      }

      String display() {
         return String.join(" | ", this.values);
      }

      @Override
      public boolean equals(Object var1) {
         return var1 instanceof HxWorkbench.GroupKey && this.values.equals(((HxWorkbench.GroupKey)var1).values);
      }

      @Override
      public int hashCode() {
         return this.values.hashCode();
      }
   }

   private static final class HistogramPanel extends JPanel {
      private List<Double> values = Collections.emptyList();
      private String name = "";

      HistogramPanel() {
         this.setPreferredSize(new Dimension(300, 190));
         this.setBackground(Color.WHITE);
         this.setBorder(new EmptyBorder(8, 8, 8, 8));
      }

      void setValues(List<Double> var1, String var2) {
         this.values = var1 == null ? Collections.emptyList() : var1;
         this.name = var2 == null ? "" : var2;
         this.repaint();
      }

      @Override
      protected void paintComponent(Graphics var1) {
         super.paintComponent(var1);
         Graphics2D var2 = (Graphics2D)var1.create();
         var2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
         int var3 = this.getWidth();
         int var4 = this.getHeight();
         var2.setColor(new Color(70, 75, 82));
         var2.drawString(this.values.isEmpty() ? "数值变量选中后显示抽样分布" : this.name + " 的抽样分布", 8, 16);
         if (this.values.isEmpty()) {
            var2.dispose();
         } else {
            double var5 = this.values.stream().mapToDouble(Double::doubleValue).min().orElse(0.0);
            double var7 = this.values.stream().mapToDouble(Double::doubleValue).max().orElse(0.0);
            if (var7 <= var5) {
               var7 = var5 + 1.0;
            }

            int var9 = Math.max(6, Math.min(24, (int)Math.sqrt(this.values.size())));
            int[] var10 = new int[var9];

            for (double var12 : this.values) {
               int var14 = (int)((var12 - var5) / (var7 - var5) * var9);
               var10[Math.min(var9 - 1, Math.max(0, var14))]++;
            }

            int var24 = Arrays.stream(var10).max().orElse(1);
            byte var25 = 12;
            byte var13 = 8;
            byte var26 = 28;
            byte var15 = 25;
            int var16 = Math.max(1, var3 - var25 - var13);
            int var17 = Math.max(1, var4 - var26 - var15);
            var2.setColor(new Color(220, 225, 232));
            var2.drawLine(var25, var26 + var17, var25 + var16, var26 + var17);
            double var18 = (double)var16 / var9;
            var2.setColor(new Color(66, 133, 188));

            for (int var20 = 0; var20 < var9; var20++) {
               int var21 = (int)((double)(var17 * var10[var20]) / var24);
               int var22 = var25 + (int)Math.floor(var20 * var18);
               int var23 = Math.max(1, (int)Math.ceil(var18) - 1);
               var2.fillRect(var22, var26 + var17 - var21, var23, var21);
            }

            var2.setColor(new Color(90, 95, 102));
            var2.drawString(String.format(Locale.ROOT, "%.3g", var5), var25, var4 - 6);
            String var27 = String.format(Locale.ROOT, "%.3g", var7);
            var2.drawString(var27, Math.max(var25, var3 - var13 - var2.getFontMetrics().stringWidth(var27)), var4 - 6);
            var2.dispose();
         }
      }
   }

   private static final class ImportPreviewTableModel extends AbstractTableModel {
      private List<String> columns = Collections.emptyList();
      private Object[][] values = new Object[0][0];

      void load(Frame var1, int var2, int var3) {
         int var4 = Math.min(var1.getVarCount(), var3);
         int var5 = (int)Math.min(var1.getObsTotal(), (long)var2);
         ArrayList var6 = new ArrayList(var4);

         for (int var7 = 1; var7 <= var4; var7++) {
            var6.add(var1.getVarName(var7));
         }

         Object[][] var10 = new Object[var5][var4];

         for (int var8 = 0; var8 < var5; var8++) {
            for (int var9 = 0; var9 < var4; var9++) {
               var10[var8][var9] = var1.getFormattedValue(var9 + 1, var8 + 1L, true);
            }
         }

         this.columns = var6;
         this.values = var10;
         this.fireTableStructureChanged();
      }

      void loadRows(String[] var1, List<Object[]> var2) {
         this.columns = Arrays.asList(var1);
         this.values = var2.toArray(new Object[0][]);
         this.fireTableStructureChanged();
      }

      void clear() {
         this.columns = Collections.emptyList();
         this.values = new Object[0][0];
         this.fireTableStructureChanged();
      }

      @Override
      public int getRowCount() {
         return this.values.length;
      }

      @Override
      public int getColumnCount() {
         return this.columns.size();
      }

      @Override
      public String getColumnName(int var1) {
         return this.columns.get(var1);
      }

      @Override
      public Object getValueAt(int var1, int var2) {
         return this.values[var1][var2];
      }

      @Override
      public boolean isCellEditable(int var1, int var2) {
         return false;
      }
   }

   private static final class MissingAnalysisResult {
      final List<String> checkedNames;
      final List<String> groupNames;
      final String[] overallColumns = new String[]{"变量", "总观测数", "缺失数", "非缺失数", "缺失率(%)"};
      final List<Object[]> overallRows = new ArrayList<>();
      final String[] separateColumns = new String[]{"分类值", "组内观测数", "缺失单元格", "非缺失单元格", "缺失率(%)"};
      final LinkedHashMap<String, List<Object[]>> separateRows = new LinkedHashMap<>();
      String[] jointColumns = new String[0];
      final List<Object[]> jointRows = new ArrayList<>();
      String[] recordColumns = new String[0];
      final List<Object[]> recordRows = new ArrayList<>();
      final List<Long> recordObservationNumbers = new ArrayList<>();
      final List<String> variableChartLabels = new ArrayList<>();
      final List<Double> variableChartRates = new ArrayList<>();
      final List<String> groupChartLabels = new ArrayList<>();
      final List<Double> groupChartRates = new ArrayList<>();
      boolean[][] matrix;

      private MissingAnalysisResult(List<String> var1, List<String> var2) {
         this.checkedNames = var1;
         this.groupNames = var2;
      }

      static HxWorkbench.MissingAnalysisResult compute(
         List<String> var0, List<String> var1, int var2, boolean var3, boolean var4, int var5, double var6, String var8
      ) {
         long var9 = Data.getObsTotal();
         List<Integer> var11 = variableIndices(var0);
         List<Integer> var12 = variableIndices(var1);
         if (var11.isEmpty()) {
            throw new IllegalArgumentException("没有找到可检查的变量。");
         } else {
            HxWorkbench.MissingAnalysisResult var13 = new HxWorkbench.MissingAnalysisResult(new ArrayList<>(var0), new ArrayList<>(var1));
            long[] var14 = new long[var11.size()];
            LinkedHashMap<String, LinkedHashMap<HxWorkbench.GroupKey, HxWorkbench.GroupAggregate>> var15 = new LinkedHashMap<>();
            if (var2 == 1 || var2 == 3 || var3) {
               for (String var17 : var1) {
                  var15.put(var17, new LinkedHashMap());
               }
            }

            LinkedHashMap<HxWorkbench.GroupKey, HxWorkbench.GroupAggregate> var29 = new LinkedHashMap<>();
            int var30 = (int)Math.min(80L, var9);
            var13.matrix = new boolean[var30][var11.size()];

            for (long var18 = 1L; var18 <= var9; var18++) {
               boolean[] var20 = new boolean[var11.size()];
               int var21 = 0;

               for (int var22 = 0; var22 < var11.size(); var22++) {
                  var20[var22] = isMissing((Integer)var11.get(var22), var18);
                  if (var20[var22]) {
                     var14[var22]++;
                     var21++;
                  }

                  if (var18 <= var30) {
                     var13.matrix[(int)var18 - 1][var22] = var20[var22];
                  }
               }

               ArrayList<String> var41 = new ArrayList<>(var12.size());

               for (int var24 : var12) {
                  var41.add(formattedGroupValue(var24, var18));
               }

               if (var2 > 0) {
                  for (int var45 = 0; var45 < var12.size(); var45++) {
                     LinkedHashMap<HxWorkbench.GroupKey, HxWorkbench.GroupAggregate> var51 = var15.get(var1.get(var45));
                     if (var51 != null) {
                        HxWorkbench.GroupKey var25 = new HxWorkbench.GroupKey(Collections.singletonList((String)var41.get(var45)));
                        var51.computeIfAbsent(var25, var2x -> new HxWorkbench.GroupAggregate(var25, var11.size())).add(var20);
                     }
                  }

                  if (var2 != 3) {
                     HxWorkbench.GroupKey var46 = new HxWorkbench.GroupKey(var41);
                     if (var29.size() < 200000 || var29.containsKey(var46)) {
                        var29.computeIfAbsent(var46, var2x -> new HxWorkbench.GroupAggregate(var46, var11.size())).add(var20);
                     }
                  }
               }

               double var47 = 100.0 * var21 / var11.size();
               boolean var55 = (!var4 || var21 > 0) && var21 >= var5 && var47 + 1.0E-12 >= var6;
               if (var55 && var13.recordRows.size() < 100000) {
                  ArrayList var26 = new ArrayList();
                  var26.add(var18);
                  var26.addAll(var41);
                  ArrayList var27 = new ArrayList();

                  for (int var28 = 0; var28 < var20.length; var28++) {
                     if (var20[var28]) {
                        var27.add((String)var0.get(var28));
                     }
                  }

                  var26.add(String.join("、", var27));
                  var26.add(var21);
                  var26.add(round2(var47));
                  var13.recordRows.add(var26.toArray());
                  var13.recordObservationNumbers.add(var18);
               }
            }

            for (int var31 = 0; var31 < var0.size(); var31++) {
               double var19 = var9 == 0L ? 0.0 : 100.0 * var14[var31] / var9;
               var13.overallRows.add(new Object[]{var0.get(var31), var9, var14[var31], var9 - var14[var31], round2(var19)});
               var13.variableChartLabels.add((String)var0.get(var31));
               var13.variableChartRates.add(var19);
            }

            Comparator<HxWorkbench.GroupAggregate> var32 = groupComparator(var8);

            for (Entry<String, LinkedHashMap<HxWorkbench.GroupKey, HxWorkbench.GroupAggregate>> var36 : var15.entrySet()) {
               ArrayList<HxWorkbench.GroupAggregate> var38 = new ArrayList<>(var36.getValue().values());
               var38.removeIf(var4x -> !passes(var4x, var4, var5, var6));
               var38.sort(var32);
               ArrayList var42 = new ArrayList();

               for (HxWorkbench.GroupAggregate var52 : var38) {
                  long var56 = var52.n * var0.size();
                  var42.add(new Object[]{var52.key.values.get(0), var52.n, var52.missingTotal(), var56 - var52.missingTotal(), round2(var52.rate())});
               }

               var13.separateRows.put((String)var36.getKey(), var42);
               if (var13.groupChartLabels.isEmpty()) {
                  for (HxWorkbench.GroupAggregate var53 : var38) {
                     var13.groupChartLabels.add(var53.key.values.get(0));
                     var13.groupChartRates.add(var53.rate());
                  }
               }
            }

            if (!var29.isEmpty()) {
               ArrayList<String> var34 = new ArrayList<>(var1);
               var34.addAll(var0);
               var34.add("检查变量数");
               var34.add("缺失变量数");
               var34.add("缺失比例(%)");
               var13.jointColumns = var34.toArray(new String[0]);
               ArrayList<HxWorkbench.GroupAggregate> var37 = new ArrayList<>(var29.values());
               var37.removeIf(var4x -> !passes(var4x, var4, var5, var6));
               var37.sort(var32);
               if (var13.groupChartLabels.isEmpty()) {
                  for (HxWorkbench.GroupAggregate var43 : var37) {
                     var13.groupChartLabels.add(var43.key.display());
                     var13.groupChartRates.add(var43.rate());
                  }
               }

               for (HxWorkbench.GroupAggregate var44 : var37) {
                  ArrayList var50 = new ArrayList<>(var44.key.values);

                  for (long var59 : var44.missingByVariable) {
                     var50.add(var59 == 0L ? "有数据" : (var59 == var44.n ? "缺失" : "缺失 " + var59 + "/" + var44.n));
                  }

                  var50.add(var0.size());
                  var50.add(var44.missingVariableCount());
                  var50.add(round2(var44.rate()));
                  var13.jointRows.add(var50.toArray());
               }
            }

            ArrayList<String> var35 = new ArrayList<>();
            var35.add("观测序号");
            var35.addAll(var1);
            var35.add("缺失变量");
            var35.add("缺失变量数");
            var35.add("缺失比例(%)");
            var13.recordColumns = var35.toArray(new String[0]);
            return var13;
         }
      }

      private static List<Integer> variableIndices(List<String> var0) {
         ArrayList var1 = new ArrayList();

         for (String var3 : var0) {
            int var4 = Data.getVarIndex(var3);
            if (var4 > 0) {
               var1.add(var4);
            }
         }

         return var1;
      }

      private static boolean isMissing(int var0, long var1) {
         if (!Data.isVarTypeString(var0)) {
            return Missing.isMissing(Data.getNum(var0, var1));
         } else {
            String var3 = HxWorkbench.safe(() -> Data.getStr(var0, var1), "");
            return var3 == null || var3.isBlank();
         }
      }

      private static String formattedGroupValue(int var0, long var1) {
         String var3 = HxWorkbench.safe(() -> Data.getFormattedValue(var0, var1, true), "");
         return var3 != null && !var3.isBlank() ? var3 : "(缺失/空白)";
      }

      private static boolean passes(HxWorkbench.GroupAggregate var0, boolean var1, int var2, double var3) {
         return (!var1 || var0.missingTotal() > 0L) && var0.missingVariableCount() >= var2 && var0.rate() + 1.0E-12 >= var3;
      }

      private static Comparator<HxWorkbench.GroupAggregate> groupComparator(String var0) {
         if (var0.startsWith("缺失数")) {
            return Comparator.comparingLong(HxWorkbench.GroupAggregate::missingTotal).reversed().thenComparing(var0x -> var0x.key.display());
         } else {
            return var0.startsWith("分类值")
               ? Comparator.comparing(var0x -> var0x.key.display())
               : Comparator.comparingDouble(HxWorkbench.GroupAggregate::rate).reversed().thenComparing(var0x -> var0x.key.display());
         }
      }

      private static double round2(double var0) {
         return Math.round(var0 * 100.0) / 100.0;
      }
   }

   private static final class MissingRunOutcome {
      final int rc;
      final String command;
      final HxWorkbench.MissingAnalysisResult analysis;
      final String error;

      private MissingRunOutcome(int var1, String var2, HxWorkbench.MissingAnalysisResult var3, String var4) {
         this.rc = var1;
         this.command = var2;
         this.analysis = var3;
         this.error = var4;
      }

      static HxWorkbench.MissingRunOutcome success(String var0, HxWorkbench.MissingAnalysisResult var1) {
         return new HxWorkbench.MissingRunOutcome(0, var0, var1, "");
      }

      static HxWorkbench.MissingRunOutcome failure(String var0, int var1, String var2) {
         return new HxWorkbench.MissingRunOutcome(var1, var0, null, var2 == null ? "未知错误" : var2);
      }
   }

   private static final class RunResult {
      private static final Set<String> ESTIMATION_COMMANDS = new HashSet<>(
         Arrays.asList(
            "regress",
            "areg",
            "reghdfe",
            "qreg",
            "xtreg",
            "xtlogit",
            "xtprobit",
            "logit",
            "logistic",
            "probit",
            "poisson",
            "nbreg",
            "ivregress",
            "ivreg2",
            "ivreghdfe",
            "didregress",
            "xtdidregress",
            "ppmlhdfe",
            "glm",
            "tobit",
            "heckman",
            "sem",
            "gsem"
         )
      );
      final String command;
      final int rc;
      final String historyStatus;
      final String error;
      final double estimationN;
      final double r2;
      final double r2Adjusted;

      private RunResult(String var1, int var2, String var3, String var4, double var5, double var7, double var9) {
         this.command = var1;
         this.rc = var2;
         this.historyStatus = var3;
         this.error = var4;
         this.estimationN = var5;
         this.r2 = var7;
         this.r2Adjusted = var9;
      }

      static HxWorkbench.RunResult capture(String var0, int var1, String var2) {
         double var3 = Double.NaN;
         double var5 = Double.NaN;
         double var7 = Double.NaN;
         if (var1 == 0 && isEstimationCommand(var0)) {
            var3 = scalar("e(N)");
            var5 = scalar("e(r2)");
            var7 = scalar("e(r2_a)");
         }

         return new HxWorkbench.RunResult(var0, var1, var2, var1 == 0 ? "" : errorText(var1), var3, var5, var7);
      }

      static HxWorkbench.RunResult failure(String var0, int var1, String var2) {
         return new HxWorkbench.RunResult(var0, var1, "写入状态未知", var2, Double.NaN, Double.NaN, Double.NaN);
      }

      private static boolean isEstimationCommand(String var0) {
         String var1 = var0 == null ? "" : var0.trim().toLowerCase(Locale.ROOT);

         while (var1.startsWith("quietly ") || var1.startsWith("capture ") || var1.startsWith("noisily ")) {
            var1 = var1.substring(var1.indexOf(32) + 1).trim();
         }

         String var2 = var1.split("[\\s,:]", 2)[0];
         return ESTIMATION_COMMANDS.contains(var2);
      }

      private static double scalar(String var0) {
         double var1 = HxWorkbench.safe(() -> Scalar.getValue(var0), Double.NaN);
         return Missing.isMissing(var1) ? Double.NaN : var1;
      }

      private static String errorText(int var0) {
         if (var0 == 111) {
            return "变量或对象未找到。";
         } else if (var0 == 198) {
            return "命令语法或必填设置不完整。";
         } else {
            return var0 == 459 ? "当前数据状态不满足该命令的要求。" : "Stata 返回 r(" + var0 + ")。";
         }
      }
   }

   private static final class RunShape {
      final long n;
      final int k;
      final List<String> names;

      private RunShape(long var1, int var3, List<String> var4) {
         this.n = var1;
         this.k = var3;
         this.names = var4;
      }

      static HxWorkbench.RunShape capture() {
         long var0 = HxWorkbench.safe(Data::getObsTotal, 0L);
         int var2 = HxWorkbench.safe(Data::getVarCount, 0);
         ArrayList var3 = new ArrayList(var2);

         for (int var4 = 1; var4 <= var2; var4++) {
            int var5 = var4;
            var3.add(HxWorkbench.safe(() -> Data.getVarName(var5), "var" + var4));
         }

         return new HxWorkbench.RunShape(var0, var2, var3);
      }
   }

   private static final class SimpleDocumentListener implements DocumentListener {
      private final Runnable runnable;

      SimpleDocumentListener(Runnable var1) {
         this.runnable = var1;
      }

      @Override
      public void insertUpdate(DocumentEvent var1) {
         this.runnable.run();
      }

      @Override
      public void removeUpdate(DocumentEvent var1) {
         this.runnable.run();
      }

      @Override
      public void changedUpdate(DocumentEvent var1) {
         this.runnable.run();
      }
   }

   private static final class StataBridge {
      static int execute(String var0, boolean var1) {
         try {
            return SFIToolkit.executeCommand(var0, var1);
         } catch (Throwable var3) {
            SFIToolkit.errorln("工作台调用 Stata 失败：" + var0 + "\n" + var3.getMessage());
            return 459;
         }
      }

      static String lastNativeOutput() {
         String path = characteristic("hxtoolbox_last_results_file");
         if (path == null || path.isBlank()) {
            return "";
         }

         try {
            Path resultPath = Paths.get(path);
            if (!Files.isRegularFile(resultPath)) {
               return "";
            }

            final int maxBytes = 2 * 1024 * 1024;
            long fileSize = Files.size(resultPath);
            byte[] bytes;
            try (InputStream in = Files.newInputStream(resultPath)) {
               bytes = in.readNBytes(maxBytes);
            }

            Charset charset = StandardCharsets.UTF_8;
            int offset = 0;
            if (bytes.length >= 3 && (bytes[0] & 255) == 0xEF && (bytes[1] & 255) == 0xBB && (bytes[2] & 255) == 0xBF) {
               offset = 3;
            } else if (bytes.length >= 2 && (bytes[0] & 255) == 0xFF && (bytes[1] & 255) == 0xFE) {
               charset = StandardCharsets.UTF_16LE;
               offset = 2;
            } else if (bytes.length >= 2 && (bytes[0] & 255) == 0xFE && (bytes[1] & 255) == 0xFF) {
               charset = StandardCharsets.UTF_16BE;
               offset = 2;
            }

            String text = new String(bytes, offset, Math.max(0, bytes.length - offset), charset).replace("\u0000", "").stripTrailing();
            if (fileSize > bytes.length) {
               text += "\n\n[输出过长：工具箱仅显示前 2 MB；完整内容仍保留在 Stata Results。]";
            }
            return text;
         } catch (Throwable var2) {
            return "";
         }
      }

      static String characteristic(String var0) {
         try {
            String var1 = Characteristic.getDtaChar(var0);
            return var1 == null ? "" : var1;
         } catch (Throwable var2) {
            return "";
         }
      }

      static void clearRunAudit() {
         execute("quietly char _dta[hxtoolbox_last_native_command] \"\"", false);
         execute("quietly char _dta[hxtoolbox_history_status] \"\"", false);
         execute("quietly char _dta[hxtoolbox_last_results_file] \"\"", false);
      }

      static List<String> variableNames() {
         int var0 = Data.getVarCount();
         ArrayList var1 = new ArrayList(var0);

         for (int var2 = 1; var2 <= var0; var2++) {
            int var3 = var2;
            var1.add(HxWorkbench.safe(() -> Data.getVarName(var3), "var" + var3));
         }

         return var1;
      }

      static List<String> words(String var0) {
         return var0 != null && !var0.trim().isEmpty() ? Arrays.asList(var0.trim().split("\\s+")) : Collections.emptyList();
      }

      static String methodCode(String var0) {
         switch (var0) {
            case "导入与转换":
               return "import_convert";
            case "数据检查":
               return "data_check";
            case "变量处理":
               return "variable_processing";
            case "样本处理":
               return "sample_processing";
            case "合并与追加":
               return "merge_append";
            case "数据结构":
               return "data_structure";
            case "汇总，表格和假设检验":
               return "summary_tests";
            case "线性模型及相关":
               return "linear_related";
            case "序数结果":
               return "ordinal_outcomes";
            case "分类结果":
               return "categorical_outcomes";
            case "计数结果":
               return "count_outcomes";
            case "分数结果":
               return "fractional_outcomes";
            case "广义线性模型":
               return "glm_models";
            case "选择模型":
               return "selection_models";
            case "时间序列":
               return "time_series";
            case "多元时间序列":
               return "multivariate_ts";
            case "空间自回归模型":
               return "spatial_ar";
            case "纵向/面板数据":
               return "panel_longitudinal";
            case "多层混合效应模型":
               return "mixed_effects";
            case "生存分析":
               return "survival";
            case "流行病学及相关":
               return "epidemiology";
            case "内生协变量":
               return "endogenous_covariates";
            case "样本选择模型":
               return "sample_selection";
            case "因果推断/处理效应":
               return "causal_treatment";
            case "结构方程模型(SEM)":
               return "sem";
            case "潜在类别分析(LCA)":
               return "lca";
            case "有限混合模型(FMM)":
               return "fmm";
            case "项目反应理论(IRT)":
               return "irt";
            case "多元分析":
               return "multivariate";
            case "调查数据分析":
               return "survey";
            case "Lasso回归":
               return "lasso";
            case "Meta分析":
               return "meta";
            case "多重插补":
               return "mi";
            case "非参数分析":
               return "nonparametric";
            case "精确统计":
               return "exact_stats";
            case "重抽样":
               return "resampling";
            case "效能，精度和样品含量":
               return "power_precision";
            case "贝叶斯分析":
               return "bayes";
            case "贝叶斯模型平均":
               return "bma";
            case "二维图(散点图，折线图等)":
               return "twoway_graphs";
            case "条形图":
               return "bar_graph";
            case "点图":
               return "dot_graph";
            case "饼图":
               return "pie_graph";
            case "直方图":
               return "histogram_graph";
            case "箱线图":
               return "box_graph";
            case "等高线图":
               return "contour_graph";
            case "散点图矩阵":
               return "matrix_graph";
            case "分布图":
               return "distribution_graph";
            case "平滑和密度":
               return "smooth_density";
            case "回归诊断图":
               return "reg_diagnostic_graph";
            case "时间序列图":
               return "ts_graph";
            case "面板数据折线图":
               return "panel_line_graph";
            case "生存分析图":
               return "survival_graph";
            case "ROC分析":
               return "roc_graph";
            case "多元分析图":
               return "multivariate_graph";
            case "质量控制":
               return "quality_graph";
            case "更多统计图形":
               return "more_stat_graph";
            case "图形组合":
               return "graph_combine";
            case "管理图形":
               return "graph_manage";
            case "更改方案/大小":
               return "graph_scheme";
            case "描述统计":
               return "descriptive";
            case "相关分析":
               return "correlation";
            case "均值检验":
               return "mean_test";
            case "频数列联":
               return "frequency";
            case "普通线性回归":
               return "linear_ols";
            case "固定效应线性回归":
               return "linear_fe";
            case "稳健与特殊线性回归":
               return "linear_special";
            case "分位数回归":
               return "linear_quantile";
            case "时间序列线性回归":
               return "linear_ts";
            case "线性模型":
               return "linear";
            case "面板模型":
               return "panel";
            case "二元结果":
               return "binary_outcomes";
            case "计数模型":
               return "count";
            case "工具变量":
               return "iv";
            case "双重差分":
               return "did";
            case "DID分步构建":
               return "did_build";
            case "DID模型构建":
               return "did_model";
            case "系数检验":
               return "coefficient";
            case "预测边际":
               return "prediction";
            case "数据分布":
               return "graph_distribution";
            case "变量关系":
               return "graph_relation";
            case "分组趋势":
               return "graph_trend";
            case "回归结果":
               return "graph_estimation";
            case "平行趋势与动态图":
               return "did_graph";
            case "DID与事件研究":
               return "graph_did";
            case "控制变量组合筛选":
               return "oneclick_screen";
            case "控制变量组合稳健性":
               return "oneclick_robustness";
            default:
               return var0.matches("[A-Za-z_][A-Za-z0-9_]*") ? var0 : "";
         }
      }

      static String quote(String var0) {
         String var1 = var0 == null ? "" : var0.replace("\"", "\"\"");
         return "`\"" + var1 + "\"'";
      }
   }

   private interface UnsafeSupplier<T> {
      T get() throws Exception;
   }

   private static final class VariableSummary {
      final String name;
      final String text;
      final List<Double> numericValues;

      private VariableSummary(String var1, String var2, List<Double> var3) {
         this.name = var1;
         this.text = var2;
         this.numericValues = var3;
      }

      static HxWorkbench.VariableSummary compute(int var0) {
         String var1 = HxWorkbench.safe(() -> Data.getVarName(var0), "");
         String var2 = HxWorkbench.safe(() -> Data.getVarLabel(var0), "");
         String var3 = HxWorkbench.safe(() -> Data.getVarFormat(var0), "");
         long var4 = Data.getObsTotal();
         short var6 = 10000;
         long var7 = Math.max(1L, var4 / var6);
         if (Data.isVarTypeString(var0)) {
            long var30 = 0L;
            long var31 = 0L;
            LinkedHashSet var32 = new LinkedHashSet();

            for (long var14 = 1L; var14 <= var4 && var30 < var6; var30++) {
               long var16 = var14;
               String var18 = HxWorkbench.safe(() -> Data.getStr(var0, var16), "");
               if (var18 != null && !var18.isBlank()) {
                  if (var32.size() < 8) {
                     var32.add(var18);
                  }
               } else {
                  var31++;
               }

               var14 += var7;
            }

            String var33 = "变量：" + var1 + "\n标签：" + var2 + "\n类型：字符串\n格式：" + var3 + "\n抽样观测：" + var30 + "，其中空值：" + var31 + "\n示例值：" + String.join("、", var32);
            return new HxWorkbench.VariableSummary(var1, var33, Collections.emptyList());
         } else {
            long var9 = 0L;
            long var11 = 0L;
            long var13 = 0L;
            double var15 = 0.0;
            double var17 = 0.0;
            double var19 = Double.POSITIVE_INFINITY;
            double var21 = Double.NEGATIVE_INFINITY;
            ArrayList var23 = new ArrayList();

            for (long var24 = 1L; var24 <= var4 && var9 < var6; var9++) {
               double var26 = Data.getNum(var0, var24);
               if (Missing.isMissing(var26)) {
                  var11++;
               } else {
                  var13++;
                  double var28 = var26 - var15;
                  var15 += var28 / var13;
                  var17 += var28 * (var26 - var15);
                  var19 = Math.min(var19, var26);
                  var21 = Math.max(var21, var26);
                  var23.add(var26);
               }

               var24 += var7;
            }

            double var34 = var13 > 1L ? Math.sqrt(var17 / (var13 - 1L)) : Double.NaN;
            String var35 = var13 == 0L
               ? "没有可计算的非缺失值。"
               : String.format(Locale.ROOT, "非缺失：%d，缺失：%d\n均值：%.4f，标准差：%.4f\n最小值：%.4f，最大值：%.4f", var13, var11, var15, var34, var19, var21);
            String var27 = "变量：" + var1 + "\n标签：" + var2 + "\n类型：数值\n格式：" + var3 + "\n抽样观测：" + var9 + "（完整 N=" + var4 + "）\n" + var35;
            return new HxWorkbench.VariableSummary(var1, var27, var23);
         }
      }
   }

   private static final class WorkbenchFrame extends JFrame {
      private static final Color APP_BG = new Color(248, 250, 253);
      private static final Color SURFACE = new Color(255, 255, 255);
      private static final Color SIDEBAR = new Color(247, 249, 251);
      private static final Color TEXT = new Color(23, 35, 59);
      private static final Color MUTED = new Color(105, 120, 145);
      private static final Color BORDER = new Color(221, 228, 239);
      private static final Color ACCENT = new Color(34, 109, 246);
      private static final Color ACCENT_HOVER = new Color(32, 87, 166);
      private static final Color ACCENT_SOFT = new Color(234, 243, 255);
      private static final Color PALE_GREEN = new Color(225, 247, 232);
      private static final Color PALE_YELLOW = new Color(255, 247, 205);
      private static final Color SUCCESS = new Color(34, 133, 79);
      private static final Color DANGER = new Color(190, 54, 54);
      private static final Color CODE_BG = new Color(246, 248, 251);
      private static final Color COMMAND_BG = new Color(238, 244, 252);
      private final DefaultListModel<HxWorkbench.Category> categoryModel = new DefaultListModel<>();
      private final DefaultListModel<String> methodModel = new DefaultListModel<>();
      private final DefaultListModel<String> commandModel = new DefaultListModel<>();
      private final JList<HxWorkbench.Category> categoryList = new JList<>(this.categoryModel);
      private final JList<String> methodList = new JList<>(this.methodModel);
      private final JList<String> commandList = new JList<>(this.commandModel);
      private final JTextField searchField = new JTextField();
      private final JPanel homeRecentPanel = new JPanel();
      private final JLabel homeDatasetStatus = new JLabel("尚未载入数据");
      private final JLabel homeDatasetDetail = new JLabel("载入数据后显示样本数与变量数");
      private final JPanel homeAllFunctionsPanel = new JPanel();
      private final Map<String, JButton> sidebarButtons = new LinkedHashMap<>();
      private JPanel sidebarPanel;
      private JPanel sidebarBottomPanel;
      private JButton sidebarToggleButton;
      private boolean sidebarCollapsed = false;
      private String draggedDataVariable = "";
      private JComboBox<String> xtregPanelVar;
      private JComboBox<String> xtregTimeVar;
      private JComboBox<String> xtregDepVar;
      private JList<String> xtregIndepList;
      private Runnable xtregPreviewUpdater;
      private JTextArea xtregCommandPreview;
      private JRadioButton xtregFeButton;
      private JRadioButton xtregReButton;
      private JRadioButton xtregBeButton;
      private JRadioButton xtregPaButton;
      private JComboBox<String> xtregSeCombo;
      private boolean xtregSyncingFromCommand;
      private String xtregClusterVar = "";
      private String xtregExtraOptions = "";
      private String xtregCustomXText = "";
      private boolean xtregPreserveCustomX;
      private String xtregCommandPrefix = "";
      private String activeSidebarKey = "home";
      private final JTextArea exactOneClickCommand = new JTextArea();
      private final JTextField exactOneClickModelOptions = new JTextField();
      private final JTextField exactOneClickOtherOptions = new JTextField();
      private final JTextField exactOneClickCandidatesDisplay = new JTextField();
      private final JTextField exactOneClickRequiredDisplay = new JTextField();
      private JPanel exactOneClickRoot;
      private final JPanel exactOneClickInspectorHost = new JPanel(new BorderLayout());
      private JComponent sharedDataInspector;
      private static final Preferences PREFS = Preferences.userRoot().node("com/hexie/stata/hxempirical");
      private static final String PREF_RECENT_COUNT = "recent.count";
      private static final int MAX_RECENT_SNAPSHOTS = 3;
      private final JLabel methodCaption = new JLabel("先选择功能分类");
      private final JLabel commandCaption = new JLabel("再选择方法");
      private final JPanel formPanel = new HxWorkbench.WorkbenchFrame.WidthTrackingPanel();
      private final JScrollPane formScroll = new JScrollPane(this.formPanel);
      private final JPanel breadcrumbBar = new JPanel(new FlowLayout(FlowLayout.LEFT, 0, 0));
      private final JLabel commandTitle = new JLabel("选择一个 Stata 命令");
      private final JLabel exampleLabel = new JLabel("选择一项工作开始");
      private final JTextArea insightArea = readonlyArea();
      private final JTextArea syntaxArea = readonlyArea();
      private final JTextArea previewArea = new JTextArea(3, 30);
      private final JButton runButton = new JButton("运行命令");
      private final JButton copyCommandButton = new JButton("复制命令");
      private final JLabel commandDockTitle = new JLabel("即将执行的 Stata 命令");
      private final JLabel commandDockHint = new JLabel("可修改，完整命令写入 History");
      private final JLabel commandDockStatus = new JLabel("等待执行");
      private final JProgressBar commandDockProgress = new JProgressBar();
      private final JButton refreshButton = new JButton("刷新");
      private final JButton homeButton = new JButton("首页");
      private final JToggleButton inspectorToggle = new JToggleButton("隐藏数据 / 结果");
      private final JButton changeMethodButton = new JButton("← 上一级");
      private final JTabbedPane commandTabs = new JTabbedPane();
      private JPanel commandDock;
      private final CardLayout stageLayout = new CardLayout();
      private final JPanel stageCards = new JPanel(this.stageLayout);
      private final JPanel chooserContent = new JPanel();
      private final JPanel chooserBreadcrumbBar = new JPanel(new FlowLayout(FlowLayout.LEFT, 0, 0));
      private final JLabel chooserTitle = new JLabel("选择具体命令");
      private final JLabel chooserHint = new JLabel("选择后进入该命令自己的设置页面");
      private final JButton chooserBackButton = new JButton("← 上一级");
      private final JButton chooserHomeButton = new JButton("首页");
      private String activeCategoryCode = "";
      private String activeCategoryName = "";
      private String activeMethodName = "";
      private boolean chooserReady;
      private boolean chooserAtCategoryLevel;
      private final HxWorkbench.DataTableModel dataModel = new HxWorkbench.DataTableModel();
      private final JTable dataTable = new JTable(this.dataModel);
      private final JLabel dataLabel = new JLabel();
      private final JTextArea summaryArea = readonlyArea();
      private final HxWorkbench.HistogramPanel histogram = new HxWorkbench.HistogramPanel();
      private final HxWorkbench.GraphPreviewPanel graphPreview = new HxWorkbench.GraphPreviewPanel();
      private final JTextArea changeArea = readonlyArea();
      private final JTabbedPane dataTabs = new JTabbedPane();
      private final CardLayout resultLayout = new CardLayout();
      private final JPanel resultCards = new JPanel(this.resultLayout);
      private final JTextArea resultSummaryArea = readonlyArea();
      private final JLabel rightPaneTitle = new JLabel("当前数据");
      private final DefaultTableModel inspectorVariableModel = new DefaultTableModel(new String[]{"名称", "标签"}, 0) {
         @Override
         public boolean isCellEditable(int row, int column) { return false; }
      };
      private final JTable inspectorVariableTable = new JTable(this.inspectorVariableModel);
      private final JTextField inspectorVariableFilter = new JTextField();
      private final JLabel inspectorRoleLabel = new JLabel("当前模型角色：未使用");
      private final JTextArea inspectorPropertyArea = readonlyArea();
      private final JLabel inspectorOverviewLabel = new JLabel("数据概览：尚未载入数据");
      private final JTabbedPane oneClickResultTabs = new JTabbedPane();
      private final JTextArea oneClickOverview = readonlyArea();
      private final JLabel monitorStatus = new JLabel("等待执行");
      private final JLabel monitorElapsed = new JLabel("已运行：00:00:00.0");
      private final JLabel monitorStart = new JLabel("开始时间：-");
      private final JLabel monitorEnd = new JLabel("结束时间：-");
      private final JLabel monitorDuration = new JLabel("总耗时：-");
      private final JLabel monitorReturnCode = new JLabel("Return code：-");
      private final JLabel monitorHistory = new JLabel("History：等待执行");
      private final JLabel monitorProcessors = new JLabel("处理器：-");
      private final JTextArea monitorCommand = readonlyArea();
      private final JTextArea monitorOutcome = readonlyArea();
      private final JTextArea monitorLog = readonlyArea();
      private final JProgressBar monitorProgress = new JProgressBar();
      private final DefaultTableModel runQueueModel = new DefaultTableModel(new String[]{"序号", "状态", "命令 / 任务", "耗时", "RC"}, 0) {
         @Override
         public boolean isCellEditable(int var1, int var2) {
            return false;
         }
      };
      private final JTable runQueueTable = new JTable(this.runQueueModel);
      private final JTabbedPane missingResultTabs = new JTabbedPane();
      private final HxWorkbench.WorkbenchFrame.MissingChartPanel missingChart = new HxWorkbench.WorkbenchFrame.MissingChartPanel();
      private final JComboBox<String> missingChartType = new JComboBox<>(new String[]{"各变量缺失率", "按分类变量趋势", "缺失率最高的20组", "缺失矩阵"});
      private final JLabel statusLabel = new JLabel("就绪");
      private final JSplitPane commandDataSplit;
      private JSplitPane dataSummarySplit;
      private JSplitPane inspectorLowerSplit;
      private JSplitPane inspectorDataSplit;
      private JTabbedPane variableTabs;
      private final CardLayout currentDataLayout = new CardLayout();
      private final JPanel currentDataCards = new JPanel(this.currentDataLayout);
      private final JComboBox<String> depvar = variableCombo();
      private final JList<String> variables = variableList();
      private final JTextField newvar = new JTextField();
      private final JTextField expression = new JTextField();
      private final JComboBox<String> model = new JComboBox<>();
      private final JTextField usingFile = new JTextField();
      private final JComboBox<String> panel = variableCombo();
      private final JComboBox<String> time = variableCombo();
      private final JList<String> absorb = variableList();
      private final JList<String> endog = variableList();
      private final JList<String> instruments = variableList();
      private final JComboBox<String> vce = new JComboBox<>();
      private final JComboBox<String> cluster = variableCombo();
      private final JTextField ifCondition = new JTextField();
      private final JTextField inCondition = new JTextField();
      private final JTextField options = new JTextField();
      private final JComboBox<String> genericWeightType = new JComboBox<>(new String[]{"无", "fweight", "aweight", "pweight", "iweight"});
      private final JComboBox<String> genericWeightVar = variableCombo();
      private final JComboBox<String> regressX = variableCombo();
      private final JList<String> regressControls = variableList();
      private final JComboBox<String> regressFactor = variableCombo();
      private final JComboBox<String> regressInteractionA = variableCombo();
      private final JComboBox<String> regressInteractionB = variableCombo();
      private final JComboBox<String> regressInteractionType = new JComboBox<>(new String[]{"连续 × 连续", "连续 × 分类", "分类 × 连续", "分类 × 分类"});
      private final JComboBox<String> regressLagVar = variableCombo();
      private final JSpinner regressLagOrder = new JSpinner(new SpinnerNumberModel(1, 1, 24, 1));
      private final DefaultListModel<String> regressSpecialTermsModel = new DefaultListModel<>();
      private final JList<String> regressSpecialTerms = new JList<>(this.regressSpecialTermsModel);
      private final JComboBox<String> regressWeightType = new JComboBox<>(new String[]{"无", "fweight", "aweight", "pweight", "iweight"});
      private final JComboBox<String> regressWeightVar = variableCombo();
      private final JCheckBox regressNoConstant = new JCheckBox("不估计常数项 noconstant", false);
      private final JCheckBox regressBeta = new JCheckBox("报告标准化系数 beta", false);
      private final JSpinner regressLevel = new JSpinner(new SpinnerNumberModel(95, 50, 99, 1));
      private final JTextField regressAdvancedOptions = new JTextField();
      private JPanel regressClusterFieldBlock;
      private JPanel regressWeightVarFieldBlock;
      private boolean regressWorkspaceActive;
      private final JComboBox<String> baselineEstimator = new JComboBox<>(new String[]{"xtreg", "reghdfe", "areg", "regress"});
      private final JComboBox<String> baselineXtModel = new JComboBox<>(new String[]{"固定效应（FE）", "随机效应（RE）", "组间效应（BE）"});
      private final JLabel baselineEstimatorSource = new JLabel("Stata 官方");
      private JPanel baselineEstimatorHeader;
      private JPanel baselineXtModelFieldBlock;
      private JPanel baselineAbsorbFieldBlock;
      private boolean baselineTaskActive;
      private final JLabel usingLabel = new JLabel();
      private final JToggleButton advancedToggle = new JToggleButton("更多设置  +");
      private final JPanel advancedContent = new JPanel();
      private JPanel clusterFieldBlock;
      private JPanel genericWeightVarFieldBlock;
      private final JComboBox<String> oneClickY = variableCombo();
      private final JComboBox<String> oneClickX = variableCombo();
      private final JList<String> oneClickRequired = variableList();
      private final JList<String> oneClickCandidates = variableList();
      private final JComboBox<String> oneClickEstimator = new JComboBox<>(new String[]{"regress", "reghdfe", "logit", "probit"});
      private final JComboBox<String> oneClickP = new JComboBox<>(new String[]{"0.01（1%）", "0.05（5%）", "0.10（10%）"});
      private final JList<String> oneClickAbsorb = variableList();
      private final JComboBox<String> oneClickVce = new JComboBox<>(new String[]{"默认", "robust", "cluster"});
      private final JComboBox<String> oneClickCluster = variableCombo();
      private JPanel oneClickAbsorbFieldBlock;
      private JPanel oneClickClusterFieldBlock;
      private final JLabel oneClickScale = new JLabel("请选择候选控制变量");
      private final JTextArea oneClickNotice = readonlyArea();
      private String oneClickGeneratedCommand = "";
      private final HxWorkbench.ImportPreviewTableModel oneClickExternalModel = new HxWorkbench.ImportPreviewTableModel();
      private final JTable oneClickExternalTable = new JTable(this.oneClickExternalModel);
      private final List<List<String>> oneClickExternalControls = new ArrayList<>();
      private String oneClickExternalFrameName = "";
      private final JComboBox<String> didAction = new JComboBox<>(
         new String[]{"生成政策后变量 post", "生成交互项 did", "生成相对政策时间 event_time", "生成事件研究编码 event_code", "DID 交互回归", "事件研究回归", "政策前联合显著性检验"}
      );
      private final JComboBox<String> didEstimator = new JComboBox<>(new String[]{"reghdfe", "regress"});
      private final JComboBox<String> didUnit = variableCombo();
      private final JComboBox<String> didTime = variableCombo();
      private final JComboBox<String> didTreat = variableCombo();
      private final JComboBox<String> didPost = variableCombo();
      private final JComboBox<String> didEvent = variableCombo();
      private final JComboBox<String> didEventCode = variableCombo();
      private final JTextField didNewVar = new JTextField("post");
      private final JTextField didPolicyTime = new JTextField("2020");
      private final JSpinner didBasePeriod = new JSpinner(new SpinnerNumberModel(-1, -100, 100, 1));
      private final JCheckBox didUnitFE = new JCheckBox("个体固定效应", true);
      private final JCheckBox didTimeFE = new JCheckBox("年份固定效应", true);
      private final JRadioButton missingAllVariables = new JRadioButton("全部变量", true);
      private final JRadioButton missingChooseVariables = new JRadioButton("自己选择");
      private final JList<String> missingVariables = variableList();
      private final JComboBox<String> missingMode = new JComboBox<>(new String[]{"整体", "按一个变量分类", "按多个变量联合分类", "各分类变量分别汇总"});
      private final JList<String> missingGroups = variableList();
      private final JCheckBox missingSeparateSummary = new JCheckBox("同时生成各分类变量的独立汇总", true);
      private final JCheckBox missingOnly = new JCheckBox("仅显示存在缺失的组", true);
      private final JSpinner missingMinCount = new JSpinner(new SpinnerNumberModel(1, 0, 9999, 1));
      private final JSpinner missingMinRate = new JSpinner(new SpinnerNumberModel(0.0, 0.0, 100.0, 1.0));
      private final JComboBox<String> missingSort = new JComboBox<>(new String[]{"缺失率从高到低", "缺失数从高到低", "分类值顺序"});
      private List<Long> missingRecordRows = Collections.emptyList();
      private final JRadioButton convertSingleMode = new JRadioButton("单个文件", true);
      private final JRadioButton convertBatchMode = new JRadioButton("批量转换");
      private final CardLayout convertModeLayout = new CardLayout();
      private final JPanel convertModeCards = new JPanel(this.convertModeLayout);
      private final JTextField convertInputFile = new JTextField();
      private final JTextField convertOutputFile = new JTextField();
      private final JLabel convertDetected = new JLabel("尚未选择文件");
      private final CardLayout convertFormatLayout = new CardLayout();
      private final JPanel convertFormatCards = new JPanel(this.convertFormatLayout);
      private final JComboBox<String> convertSheet = new JComboBox<>();
      private final JCheckBox convertExcelFirstRow = new JCheckBox("第一行作为变量名", true);
      private final JTextField convertCellRange = new JTextField();
      private final JCheckBox convertExcelAllString = new JCheckBox("全部按字符串读取（适合代码列或混合类型）", false);
      private final JComboBox<String> convertDelimiter = new JComboBox<>(new String[]{"自动识别", "Tab", "逗号", "分号", "空格", "竖线"});
      private final JComboBox<String> convertEncoding = new JComboBox<>(new String[]{"自动识别", "UTF-8", "GB18030", "Windows-1252"});
      private final JCheckBox convertDelimitedFirstRow = new JCheckBox("第一行作为变量名", true);
      private final JCheckBox convertProtectLeadingZeros = new JCheckBox("保护检测到的前导零列（推荐）", true);
      private final JCheckBox convertLoadAfter = new JCheckBox("转换完成后立即载入 Stata", false);
      private final JTextField batchInputFolder = new JTextField();
      private final JTextField batchOutputFolder = new JTextField();
      private final JCheckBox batchXlsx = new JCheckBox("Excel (.xlsx/.xls)", true);
      private final JCheckBox batchCsv = new JCheckBox("CSV (.csv)", true);
      private final JCheckBox batchTxt = new JCheckBox("文本 (.txt/.tsv)", true);
      private final JCheckBox batchExcelFirstRow = new JCheckBox("Excel 第一行作为变量名", true);
      private final JCheckBox batchExcelAllString = new JCheckBox("Excel 全部按字符串读取", false);
      private final JCheckBox batchDelimitedFirstRow = new JCheckBox("CSV/TXT 第一行作为变量名", true);
      private final JComboBox<String> batchDelimiter = new JComboBox<>(new String[]{"自动识别", "Tab", "逗号", "分号", "空格", "竖线"});
      private final JComboBox<String> batchEncoding = new JComboBox<>(new String[]{"自动识别", "UTF-8", "GB18030", "Windows-1252"});
      private final JCheckBox batchProtectLeadingZeros = new JCheckBox("保护检测到的前导零列（推荐）", true);
      private final JCheckBox batchSkipExisting = new JCheckBox("目标 DTA 已存在时跳过", true);
      private final JButton batchStopButton = new JButton("停止批量任务");
      private volatile boolean batchStopRequested;
      private final HxWorkbench.ImportPreviewTableModel importPreviewModel = new HxWorkbench.ImportPreviewTableModel();
      private final JTable importPreviewTable = new JTable(this.importPreviewModel);
      private final JTextArea importIssues = readonlyArea();
      private final JLabel importPreviewLabel = new JLabel("选择文件后显示转换前预览");
      private final AtomicInteger importFrameCounter = new AtomicInteger();
      private HxWorkbench.ExternalFileProfile currentExternalProfile;
      private final Timer previewTimer;
      private final Timer runElapsedTimer = new Timer(100, var1x -> this.updateRunElapsed());
      private final Timer previewFlashTimer = new Timer(420, var1x -> this.previewArea.setBackground(COMMAND_BG));
      private boolean rebuilding;
      private boolean runInProgress;
      private long runStartedNanos;
      private LocalDateTime runStartedAt;
      private int activeQueueRow = -1;
      private int runSequence;
      private HxWorkbench.RunShape activeRunBefore;
      private boolean searchResultsMode;
      private String currentCommand = "";
      private String lastExecutedCommand = "";
      private HxWorkbench.DatasetSnapshot beforeSnapshot;
      private final Set<String> changedCells = new HashSet<>();
      private final Set<String> addedVariables = new HashSet<>();
      private final Set<String> declinedDependencies = new HashSet<>();
      private final boolean previewMode;
      private static final Set<String> OPTIONAL_DEPENDENCIES = new HashSet<>(
         Arrays.asList("reghdfe", "winsor2", "ivreghdfe", "ppmlhdfe", "coefplot", "event_plot")
      );
      private static final Map<String, HxWorkbench.WorkbenchFrame.CommandGuide> COMMAND_GUIDES = buildCommandGuides();

      private static Map<String, HxWorkbench.WorkbenchFrame.CommandGuide> buildCommandGuides() {
         LinkedHashMap var0 = new LinkedHashMap();
         addGuide(var0, "hxconvert", "转换为 DTA", "把 Excel、CSV 或文本文件转换为 Stata 数据。", "刚拿到外部原始表，需要安全预览并保存为 .dta。", "选择文件后自动生成导入与 save 命令", "保留原文件，并重点检查代码列的前导零。");
         addGuide(var0, "缺失值分析", "缺失值分析", "集中查看变量、分组和具体记录中的缺失。", "论文数据清洗前，需要判断缺失发生在哪里。", "选择变量和分组后运行", "比单独 misstable 提供更多分组结果与数据联动。");
         addGuide(var0, "generate", "创建新变量", "根据表达式生成一个新的变量。", "计算对数、比率、交互项或论文指标。", "generate lnx = ln(x)", "新变量名必须尚未存在；修改已有变量请用 replace。");
         addGuide(var0, "replace", "修改已有变量", "按条件更新一个已经存在的变量。", "修正编码、处理异常值或替换满足条件的观测。", "replace y = 1 if year >= 2020", "直接改变原变量；需要保留原值时先 generate 新变量。");
         addGuide(
            var0, "encode", "字符串编码", "把类别字符串转成带值标签的数值变量。", "地区、行业等文字类别需要进入回归或面板设定。", "encode industry, generate(industry_id)", "保留类别标签；纯数字字符串转数值通常用 destring。"
         );
         addGuide(
            var0,
            "decode",
            "值标签转字符串",
            "把带值标签的数值变量还原成文字变量。",
            "需要导出可读类别名称或检查标签含义。",
            "decode industry_id, generate(industry_name)",
            "依据值标签转换；普通数值转字符串请用 tostring。"
         );
         addGuide(var0, "destring", "数字文本转数值", "把看起来像数字的字符串变量转换成数值。", "Excel 导入后金额、年份等被识别为字符串。", "destring income, replace", "不适合股票代码等依赖前导零的标识变量。");
         addGuide(var0, "tostring", "数值转字符串", "把数值变量转换成字符串表示。", "拼接代码、导出文本或构造标识符。", "tostring firm_id, generate(firm_code)", "显示格式会影响结果；类别标签转换优先用 decode。");
         addGuide(var0, "winsor2", "缩尾处理", "按指定分位点限制极端值的影响。", "连续财务变量存在少量极端观测。", "winsor2 roa lev, cuts(1 99) replace", "缩尾会改变尾部数值，需要报告阈值并保留原始变量备查。");
         addGuide(var0, "duplicates", "重复记录检查", "查找或标记重复的观测和键值。", "合并、面板设定或回归前检查企业年份是否唯一。", "duplicates report firm year", "只识别重复；删除前应先确认哪条记录应保留。");
         addGuide(var0, "misstable", "缺失模式统计", "汇总变量缺失数量、比例和缺失组合。", "快速了解数据整体缺失结构。", "misstable summarize y x c", "适合整体诊断；需要分组和记录联动时用缺失值分析。");
         addGuide(var0, "keep", "保留样本或变量", "只保留满足条件的观测或指定变量。", "限定研究样本、年份或行业范围。", "keep if year >= 2015", "会从内存中移除其余数据，正式操作前应保存原始数据。");
         addGuide(var0, "drop", "删除样本或变量", "删除满足条件的观测或不再使用的变量。", "剔除缺失、异常样本或整理变量集合。", "drop if missing(y)", "条件中的 Stata 缺失值比较需要特别谨慎。");
         addGuide(
            var0,
            "merge",
            "横向合并数据",
            "按关联键把主表与副表的变量合并到同一行。",
            "企业基本信息、财务指标和政策数据按代码年份匹配。",
            "merge 1:1 firm year using other.dta",
            "合并后必须检查 _merge；纵向堆叠数据请用 append。"
         );
         addGuide(var0, "append", "纵向追加数据", "把结构相近的数据表按行连接。", "多个年份、地区或批次文件需要合成一张长表。", "append using data_2023.dta", "要求变量含义和类型一致；按键补充变量请用 merge。");
         addGuide(
            var0, "reshape", "宽长表转换", "在宽格式和长格式之间重排重复测量数据。", "年份分列的数据需要转换为企业年份面板，或反向展开。", "reshape long sales, i(firm) j(year)", "必须明确唯一标识 i() 与重复维度 j()。"
         );
         addGuide(
            var0, "collapse", "分组汇总数据", "把明细数据压缩为分组统计量。", "构造企业年、城市年等层级的均值、总和或计数。", "collapse (mean) y x, by(firm year)", "会替换内存中的明细数据，建议先 preserve 或另存结果。"
         );
         addGuide(var0, "xtset", "声明面板结构", "指定面板个体变量和时间变量。", "运行 xtreg、滞后项或面板诊断前。", "xtset firm year", "只声明数据结构，不会自动解决重复键或时间缺口。");
         addGuide(var0, "summarize", "基础描述统计", "快速报告非缺失样本数、均值、标准差、最小值和最大值。", "先了解连续变量的尺度、分布和异常范围。", "summarize y x c1 c2", "输出快捷；自定义统计量或分组表格请用 tabstat。");
         addGuide(
            var0,
            "tabstat",
            "自定义描述统计表",
            "选择统计量并按组生成紧凑的描述统计表。",
            "论文需要 N、均值、标准差、分位数或分组比较。",
            "tabstat y x, statistics(n mean sd min max)",
            "比 summarize 更灵活，设置项也更多。"
         );
         addGuide(var0, "correlate", "普通相关系数", "计算变量之间的 Pearson 相关系数矩阵。", "只想查看同一完整样本中的变量相关程度。", "correlate y x c", "采用完整样本删除，默认不报告显著性。");
         addGuide(var0, "pwcorr", "成对相关与显著性", "计算成对相关系数，并可报告 p 值、星号和样本量。", "论文相关性分析需要系数及显著性水平。", "pwcorr y x c, sig", "默认逐对使用可用样本；各相关系数的样本量可能不同。");
         addGuide(var0, "ttest", "均值差异检验", "检验一个变量的均值是否等于给定值或两组均值是否相同。", "比较处理组与对照组、国企与民企等组间差异。", "ttest y, by(treat)", "比较均值；多变量条件控制通常需要回归模型。");
         addGuide(
            var0, "tabulate", "频数与列联表", "查看类别分布、交叉频数和卡方检验。", "研究变量是行业、地区、处理状态等离散类别。", "tabulate treat region, row col chi2", "适合类别变量；连续变量分布请用 summarize 或图形。"
         );
         addGuide(
            var0, "regress", "普通线性回归", "用 OLS 估计连续因变量与解释变量的线性关系。", "横截面或已明确处理结构的连续结果数据。", "regress y x c1 c2, vce(robust)", "不自动吸收多维固定效应；高维固定效应优先考虑 reghdfe。"
         );
         addGuide(
            var0,
            "areg",
            "单组固定效应回归",
            "在线性回归中吸收一组大量类别固定效应。",
            "只有一组高维固定效应，例如企业固定效应。",
            "areg y x c, absorb(firm) vce(cluster firm)",
            "只能直接吸收一组固定效应；多组固定效应用 reghdfe。"
         );
         addGuide(
            var0,
            "reghdfe",
            "高维固定效应回归",
            "高效吸收多组固定效应并支持聚类标准误。",
            "企业年份、城市年份等多维固定效应面板数据。",
            "reghdfe y x c, absorb(firm year) vce(cluster firm)",
            "功能强且适合多维固定效应，需要安装第三方命令。"
         );
         addGuide(var0, "qreg", "分位数回归", "估计解释变量对条件分布不同分位点的影响。", "效应可能在低水平与高水平样本之间不同。", "qreg y x c, quantile(.5)", "关注条件分位数，不等同于 OLS 的条件均值效应。");
         addGuide(var0, "xtreg", "面板线性模型", "估计面板固定效应、随机效应或组间模型。", "已 xtset 的连续因变量面板数据。", "xtreg y x c, fe vce(cluster firm)", "适合标准面板模型；多维固定效应通常用 reghdfe 更方便。");
         addGuide(var0, "xtlogit", "面板 Logit", "估计二元结果的面板 Logit 模型。", "同一个体被重复观察，因变量取 0 或 1。", "xtlogit y x c, fe", "固定效应估计会排除组内因变量没有变化的个体。");
         addGuide(var0, "xtprobit", "面板 Probit", "估计二元结果的面板 Probit 模型。", "具有个体随机效应假设的二元面板数据。", "xtprobit y x c, re", "常用于随机效应设定；固定效应二元模型通常考虑 xtlogit, fe。");
         addGuide(var0, "logit", "二元 Logit 回归", "估计二元结果发生概率与解释变量的关系。", "因变量为 0/1 的横截面或合并数据。", "logit y x c, vce(robust)", "系数是对数优势比尺度；概率解释通常结合 margins。");
         addGuide(
            var0, "probit", "二元 Probit 回归", "用标准正态链接估计二元结果发生概率。", "因变量为 0/1，研究传统上采用 Probit 设定。", "probit y x c, vce(robust)", "与 Logit 的链接函数不同，边际效应通常更便于比较。"
         );
         addGuide(var0, "poisson", "Poisson 计数回归", "估计非负计数结果的条件均值。", "专利数、事件数等非负整数结果。", "poisson y x c, vce(robust)", "要求条件均值设定合理；明显过度离散时可比较 nbreg。");
         addGuide(var0, "nbreg", "负二项计数回归", "为存在过度离散的计数结果建模。", "计数变量方差明显大于均值。", "nbreg y x c, vce(robust)", "比 Poisson 增加离散参数，模型假设也更强。");
         addGuide(
            var0,
            "ppmlhdfe",
            "高维固定效应 PPML",
            "用 PPML 估计含零值和多维固定效应的非负结果。",
            "贸易流、金额或其他含大量零值的非负数据。",
            "ppmlhdfe y x c, absorb(firm year) cluster(firm)",
            "适合乘法均值模型，需要安装第三方命令。"
         );
         addGuide(
            var0,
            "ivregress",
            "工具变量回归",
            "使用 2SLS、LIML 或 GMM 处理解释变量内生性。",
            "有可信工具变量并能说明相关性与排除限制。",
            "ivregress 2sls y c (x = z), vce(robust)",
            "需要报告第一阶段和弱工具变量诊断。"
         );
         addGuide(
            var0,
            "ivreghdfe",
            "高维固定效应 IV",
            "在工具变量回归中吸收多组高维固定效应。",
            "面板数据同时存在内生变量和多维固定效应。",
            "ivreghdfe y c (x = z), absorb(firm year) cluster(firm)",
            "结合 IV 与 reghdfe 能力，需要安装第三方命令。"
         );
         addGuide(var0, "test", "联合系数检验", "对一个或多个估计系数实施 Wald 联合检验。", "回归后检验一组政策前系数或类别变量是否共同显著。", "test x1 x2", "检验系数限制；特定线性组合的估计值用 lincom。");
         addGuide(var0, "lincom", "线性组合估计", "计算回归系数的线性组合、标准误和置信区间。", "需要解释主效应与交互项之和等组合效应。", "lincom x + 1.treat#c.x", "一次处理一个线性组合；多项联合限制用 test。");
         addGuide(var0, "predict", "生成预测与残差", "根据最近一次估计生成预测值、残差或其他统计量。", "模型诊断、拟合值分析或构造后续变量。", "predict yhat, xb", "依赖最近一次估计结果，具体可用统计量随模型变化。");
         addGuide(var0, "margins", "边际效应与预测", "计算调整后的预测值、边际效应和情景比较。", "Logit、Probit、交互项或非线性模型需要直观解释。", "margins, dydx(x)", "基于当前模型计算；图形展示通常继续使用 marginsplot。");
         addGuide(var0, "histogram", "直方图", "按区间显示数值变量的频数或密度分布。", "查看偏态、长尾、多峰和异常范围。", "histogram y, normal", "形状受分箱选择影响；平滑分布可用 kdensity。");
         addGuide(var0, "kdensity", "核密度图", "用平滑曲线展示连续变量的经验分布。", "比较变量或组间分布形状。", "kdensity y", "形状受带宽影响；原始频数结构用 histogram 更直观。");
         addGuide(var0, "graph_box", "箱线图", "展示中位数、四分位距和潜在异常值。", "比较连续变量在不同组中的分布。", "graph box y, over(group)", "信息紧凑，但不会展示完整分布形状。");
         addGuide(var0, "scatter", "散点图", "展示两个数值变量的原始关系和离群点。", "回归前检查线性关系、异方差和异常观测。", "scatter y x", "显示原始点；需要拟合方向可叠加 lfit。");
         addGuide(var0, "lfit", "线性拟合图", "显示 Y 对 X 的线性拟合关系。", "快速查看相关方向和近似线性趋势。", "twoway lfit y x", "只显示拟合线，通常与 scatter 叠加使用。");
         addGuide(var0, "twoway", "二维叠加图", "自由组合散点、线、置信区间等多个图层。", "需要制作结构较复杂的论文二维图形。", "twoway (scatter y x) (lfit y x)", "表达能力强，图层语法也更灵活。");
         addGuide(var0, "coefplot", "回归系数图", "把一个或多个已存模型的系数和置信区间画成图。", "展示基准、稳健性、异质性或动态效应结果。", "coefplot model1 model2, drop(_cons)", "依赖已存估计结果，需要安装第三方命令。");
         addGuide(var0, "marginsplot", "边际效应图", "把 margins 结果转换为预测值或边际效应图。", "展示交互项、非线性效应和情景比较。", "marginsplot", "必须先成功运行 margins。");
         addGuide(
            var0,
            "didregress",
            "官方双重差分（重复截面）",
            "使用 Stata 官方 didregress 估计 DID / DDD 的平均处理效应。",
            "不同时间抽取不同个体的重复截面数据，处理在组层级发生。",
            "didregress (y x1 x2) (treat), group(group) time(year)",
            "Stata 17+ 官方命令；面板数据应改用 xtdidregress。"
         );
         addGuide(
            var0,
            "xtdidregress",
            "官方面板双重差分",
            "使用 Stata 官方 xtdidregress 在纵向 / 面板数据中估计 DID。",
            "同一个体或企业被重复观察的面板数据；运行前先用 xtset 声明面板结构。",
            "xtdidregress (y x1 x2) (treat), group(group) time(year)",
            "Stata 17+ 官方命令；重复截面数据使用 didregress。"
         );
         addGuide(var0, "did_trends", "处理组与对照组趋势", "比较政策前后两组平均结果的时间走势。", "含处理组、时间变量和结果变量的面板或重复截面数据。", "选择 Y、处理组和年份后绘图", "用于直观诊断，正式平行趋势还需要回归检验。");
         addGuide(var0, "event_plot", "事件研究动态图", "展示政策前后各相对时期的估计系数和置信区间。", "已经完成事件研究估计并保留系数结果。", "event_plot, default_look", "集中展示动态效应，基准期和置信区间必须说明。");
         addGuide(
            var0, "did_builder", "DID 与事件研究构建器", "分步生成变量、运行 DID 回归、检验政策前系数并绘图。", "有明确处理组、政策时点和时间变量的研究设计。", "按数据准备、回归、检验和图形逐步运行", "每一步生成真实 Stata 命令，便于检查研究设定。"
         );
         addGuide(var0, "oneclick", "控制变量组合筛选", "遍历候选控制变量组合并保留满足规则的模型。", "已有理论候选集，需要系统检查核心系数对组合的敏感性。", "选择 Y、核心 X、必备项与候选项后运行", "组合数增长很快，结果用于稳健性审计，不能替代理论选择。");
         addGuide(var0, "oneclick_robustness", "控制变量组合稳健性", "比较全部组合中的系数、显著性、样本量和拟合度。", "需要规格曲线和完整模型审计。", "设置模型与候选控制变量后运行全部组合", "强调结果分布和稳定性，不只保留显著组合。");
         return Collections.unmodifiableMap(var0);
      }

      private static void addGuide(
         Map<String, HxWorkbench.WorkbenchFrame.CommandGuide> var0, String var1, String var2, String var3, String var4, String var5, String var6
      ) {
         var0.put(var1, new HxWorkbench.WorkbenchFrame.CommandGuide(var2, var3, var4, var5, var6));
      }

      WorkbenchFrame() {
         this(false);
      }

      WorkbenchFrame(boolean var1) {
         super("我的实证工具箱");
         this.previewMode = var1;
         this.setDefaultCloseOperation(1);
         this.setMinimumSize(new Dimension(1280, 720));
         this.setSize(new Dimension(1672, 941));
         this.setLocationRelativeTo(null);
         this.setLayout(new BorderLayout());
         this.getContentPane().setBackground(APP_BG);
         this.previewTimer = new Timer(260, var1x -> this.updatePreview());
         this.previewTimer.setRepeats(false);
         this.previewFlashTimer.setRepeats(false);
         this.buildNavigation();
         this.buildCommandPanel();
         this.buildDataPanel();
         this.oneClickP.setSelectedIndex(1);
         this.wireEvents();

         this.sharedDataInspector = this.buildDataContainer();
         this.sharedDataInspector.setMinimumSize(new Dimension(260, 0));
         JComponent commandPane = this.buildCommandContainer();
         commandPane.setMinimumSize(new Dimension(0, 0));
         this.commandDataSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, commandPane, this.sharedDataInspector);
         this.commandDataSplit.setResizeWeight(0.60);
         this.commandDataSplit.setContinuousLayout(true);
         this.commandDataSplit.setOneTouchExpandable(true);
         this.commandDataSplit.setBorder(null);
         this.commandDataSplit.setDividerSize(8);
         this.commandDataSplit.setBackground(APP_BG);

         this.stageCards.setBackground(APP_BG);
         this.stageCards.add(this.buildHomeContainer(), "home");
         this.stageCards.add(this.buildChooserContainer(), "chooser");
         this.stageCards.add(this.buildExactLinearContainer(), "linear_exact");
         this.stageCards.add(this.buildExactOneClickContainer(), "oneclick_exact");
         this.stageCards.add(this.commandDataSplit, "workspace");

         JPanel center = new JPanel(new BorderLayout());
         center.setBackground(APP_BG);
         center.add(this.stageCards, BorderLayout.CENTER);
         center.add(this.buildStatusBar(), BorderLayout.SOUTH);

         JPanel shell = new JPanel(new BorderLayout());
         shell.setBackground(APP_BG);
         shell.add(this.buildSidebarToggleBar(), BorderLayout.NORTH);
         shell.add(this.buildSidebar(), BorderLayout.WEST);
         shell.add(center, BorderLayout.CENTER);
         this.add(shell, BorderLayout.CENTER);
         this.addComponentListener(new java.awt.event.ComponentAdapter() {
            @Override
            public void componentResized(java.awt.event.ComponentEvent e) {
               SwingUtilities.invokeLater(() -> WorkbenchFrame.this.clampInspectorDividers());
            }
         });

         stylePrimaryButton(this.runButton);
         SwingUtilities.invokeLater(this::applyDividerRatios);
         if (var1) {
            this.populatePreviewState();
         } else {
            this.populateCategories();
            HxWorkbench.StataBridge.execute("quietly hxrefresh", false);
            this.refreshDataset(false);
            this.showHomePage();
         }
      }

      private void populatePreviewState() {
         this.rebuilding = true;
         this.activeCategoryCode = "reg";
         this.activeCategoryName = "回归模型";
         this.activeMethodName = "线性模型";
         this.categoryModel.clear();
         this.categoryModel.addElement(new HxWorkbench.Category("开始", "home"));
         this.categoryModel.addElement(new HxWorkbench.Category("数据处理", "data"));
         this.categoryModel.addElement(new HxWorkbench.Category("统计", "stats"));
         this.categoryModel.addElement(new HxWorkbench.Category("回归模型", "reg"));
         this.categoryModel.addElement(new HxWorkbench.Category("后估计", "post"));
         this.categoryModel.addElement(new HxWorkbench.Category("图形", "graph"));
         this.categoryModel.addElement(new HxWorkbench.Category("OneClick 专区", "oneclick"));
         this.categoryModel.addElement(new HxWorkbench.Category("测试数据", "test"));
         this.categoryModel.addElement(new HxWorkbench.Category("性能设置", "performance"));
         this.categoryModel.addElement(new HxWorkbench.Category("常用命令", "favorites"));
         this.categoryModel.addElement(new HxWorkbench.Category("最近使用", "recent"));
         this.categoryList.setSelectedIndex(3);
         this.methodModel.clear();

         for (String var2 : Arrays.asList("线性模型", "面板模型", "二元结果", "计数模型", "工具变量", "双重差分")) {
            this.methodModel.addElement(var2);
         }

         this.methodList.setSelectedIndex(0);
         this.methodCaption.setText("当前：回归模型");
         this.commandCaption.setText("当前：线性模型");
         this.commandModel.clear();

         for (String var11 : Arrays.asList("regress", "areg", "reghdfe", "qreg")) {
            this.commandModel.addElement(var11);
         }

         this.commandList.setSelectedIndex(0);
         this.setWorkspaceBreadcrumb("回归模型  ›  线性模型  ›  regress");
         this.commandTitle.setText("regress - 普通线性回归");
         this.exampleLabel.setText("<html><b>最简单例子：</b> regress y x c　　用 x 和 c 解释 y</html>");
         this.insightArea
            .setText("主要用途\n估计连续因变量与一个或多个解释变量之间的线性关系。\n\n推荐数据\n横截面数据、合并横截面数据，或已妥善处理结构的面板数据。\n\n优点\n系数容易解释，估计和诊断工具成熟。\n\n局限\n对函数形式、异常值和遗漏变量较敏感；因果解释需要额外识别条件。");
         this.syntaxArea.setText("界面解析：完整\nregress depvar indepvars [if] [in] [weight] [, options]");
         this.previewArea.setText("regress price mpg weight, vce(robust)");
         replaceComboItems(this.depvar, Arrays.asList("price", "mpg", "weight", "length", "foreign"));
         this.depvar.setSelectedItem("price");
         replaceListItems(this.variables, Arrays.asList("mpg", "weight", "length", "turn", "foreign"));
         this.variables.setSelectedIndices(new int[]{0, 1});
         this.vce.removeAllItems();
         this.vce.addItem("default");
         this.vce.addItem("robust");
         this.vce.addItem("cluster");
         this.vce.setSelectedItem("robust");
         replaceComboItems(this.cluster, Arrays.asList("foreign", "rep78"));
         this.formPanel.removeAll();
         int var4 = 0;
         this.addField(var4++, "因变量（解释谁）", this.depvar);
         this.addField(var4++, "解释变量（影响因变量）", this.listPane(this.variables));
         this.addField(var4++, "标准误方式", this.vce);
         this.clusterFieldBlock = this.addField(var4++, "聚类变量（仅 Cluster 时需要）", this.cluster);
         this.clusterFieldBlock.setVisible(false);
         this.addAdvancedSettings(var4++, true, true, true);
         GridBagConstraints var12 = this.constraints(0, var4);
         var12.gridwidth = 2;
         var12.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), var12);
         this.dataModel.loadPreview();
         this.dataLabel.setText("74 行 × 12 列 | 表格只读，可横向和纵向滚动");
         this.configureColumnWidths();
         this.summaryArea.setText("变量：price\n标签：Price\n类型：数值\n\n非缺失：74，缺失：0\n均值：6165.26，标准差：2949.50\n最小值：3291，最大值：15906");
         this.histogram.setValues(Arrays.asList(4099.0, 4749.0, 3799.0, 4816.0, 7827.0, 5788.0, 4453.0, 5189.0), "price");
         this.changeArea.setText("运行数据处理命令后，这里会显示样本数、变量数和具体变化。");
         this.statusLabel.setText("当前数据：auto.dta | 样本数：74 | 变量数：12 | 处理器：2 / 2");
         this.rebuilding = false;
         this.showWorkspacePage();
         this.selectResultView("general", false);
         this.selectDataView();
      }

      private void populateClusterPreviewState() {
         this.vce.setSelectedItem("cluster");
         replaceComboItems(this.cluster, Arrays.asList("foreign", "rep78"));
         this.cluster.setSelectedItem("foreign");
         this.updateConditionalFields();
         this.previewArea.setText("regress price mpg weight, vce(cluster foreign)");
         this.statusLabel.setText("Cluster 已选择 | 聚类变量字段按条件显示");
      }

      private void populateMonitorPreviewState() {
         this.monitorStatus.setText("● 已完成");
         this.monitorStatus.setForeground(SUCCESS);
         this.monitorProgress.setIndeterminate(false);
         this.monitorProgress.setMaximum(100);
         this.monitorProgress.setValue(100);
         this.monitorProgress.setString("执行完成");
         this.monitorElapsed.setText("已运行：00:00:18.4");
         this.monitorStart.setText("开始时间：20:25:31");
         this.monitorEnd.setText("结束时间：20:25:49");
         this.monitorDuration.setText("总耗时：18.4s");
         this.monitorReturnCode.setText("Return code：0");
         this.monitorHistory.setText("History：已写入");
         this.monitorProcessors.setText("处理器：2 / 2");
         String var1 = "reghdfe y x c1 c2, absorb(firm year) vce(cluster firm)";
         this.monitorCommand.setText(var1);
         this.monitorOutcome.setText("执行成功\n\n回归结果：\nN = 8,936\n原数据样本：9,837\n未进入回归：901\nR² = 0.3270");
         this.monitorLog.setText("20:25:31  开始执行\n20:25:31  命令已写入 History\n20:25:32  Stata 开始计算\n20:25:49  执行完成，return code 0");
         this.runQueueModel.setRowCount(0);
         this.runQueueModel.addRow(new Object[]{1, "完成", "regress y x", "0.2s", 0});
         this.runQueueModel.addRow(new Object[]{2, "完成", "regress y x c1", "0.3s", 0});
         this.runQueueModel.addRow(new Object[]{3, "完成", shortenCommand(var1), "18.4s", 0});
         this.commandDockStatus.setText("● 成功 · 18.4s");
         this.commandDockStatus.setForeground(SUCCESS);
         this.commandDockProgress.setVisible(true);
         this.commandDockProgress.setIndeterminate(false);
         this.commandDockProgress.setMaximum(100);
         this.commandDockProgress.setValue(100);
         this.commandDockProgress.setString("执行完成 · 18.4s");
         this.selectRunView();
         this.statusLabel.setText("执行完成 | Return code 0 | History 已写入");
      }

      private void populateMonitorDetailsPreviewState() {
         this.dataTabs.setSelectedIndex(2);
         this.syncRightPaneTitle();
      }

      private void populateGraphPreviewState() {
         this.rebuilding = true;
         this.categoryList.setSelectedIndex(5);
         this.methodModel.clear();

         for (String var2 : Arrays.asList("数据分布", "变量关系", "分组趋势", "回归结果")) {
            this.methodModel.addElement(var2);
         }

         this.methodList.setSelectedIndex(1);
         this.commandModel.clear();

         for (String var9 : Arrays.asList("scatter", "lfit", "twoway")) {
            this.commandModel.addElement(var9);
         }

         this.commandList.setSelectedIndex(1);
         this.currentCommand = "lfit";
         this.commandDock.setVisible(true);
         this.runButton.setText("绘制图形");
         this.commandTitle.setText("lfit - 线性拟合图");
         this.setWorkspaceBreadcrumb("图形  ›  变量关系  ›  lfit");
         this.exampleLabel.setText("<html><b>最简单例子：</b> twoway lfit price mpg</html>");
         this.insightArea.setText("主要意图：观察两个变量的线性拟合关系。\n\n推荐数据：至少包含两个数值变量。\n\n优点：方向和离群点直观。\n\n缺点与注意：拟合关系不自动代表因果效应。");
         this.syntaxArea.setText("twoway lfit y x [if] [, options]");
         replaceComboItems(this.depvar, Arrays.asList("price", "mpg", "weight", "length"));
         this.depvar.setSelectedItem("price");
         replaceListItems(this.variables, Arrays.asList("mpg", "weight", "length"));
         this.variables.setSelectedIndex(0);
         this.formPanel.removeAll();
         int var4 = 0;
         this.addField(var4++, "纵轴变量 Y", this.depvar);
         this.addField(var4++, "横轴变量 X", this.listPane(this.variables));
         this.addField(var4++, "筛选条件 if（可选）", this.ifCondition);
         this.addField(var4++, "其他图形选项", this.options);
         this.previewArea.setText("twoway lfit price mpg");
         this.graphPreview
            .setPreviewXY(
               Arrays.asList(12.0, 14.0, 18.0, 20.0, 22.0, 25.0, 29.0, 31.0),
               Arrays.asList(14800.0, 12100.0, 9300.0, 7900.0, 7100.0, 5700.0, 4300.0, 3500.0),
               true,
               "price 与 mpg · 线性拟合即时预览"
            );
         this.selectResultView("graph", true);
         this.rebuilding = false;
      }

      private void populateDidPreviewState() {
         this.rebuilding = true;
         this.categoryList.setSelectedIndex(3);
         this.methodModel.clear();
         this.methodModel.addElement("DID分步构建");
         this.methodModel.addElement("平行趋势与动态图");
         this.methodList.setSelectedIndex(0);
         this.commandModel.clear();
         this.commandModel.addElement("did_builder");
         this.commandList.setSelectedIndex(0);
         List var1 = Arrays.asList("y", "treat", "post", "year", "event_time", "event_code", "Size", "Lev", "ROA", "firm");
         replaceComboItems(this.depvar, var1);
         this.depvar.setSelectedItem("y");
         replaceComboItems(this.didUnit, var1);
         this.didUnit.setSelectedItem("firm");
         replaceComboItems(this.didTime, var1);
         this.didTime.setSelectedItem("year");
         replaceComboItems(this.didTreat, var1);
         this.didTreat.setSelectedItem("treat");
         replaceComboItems(this.didPost, var1);
         this.didPost.setSelectedItem("post");
         replaceComboItems(this.didEvent, var1);
         this.didEvent.setSelectedItem("event_time");
         replaceComboItems(this.didEventCode, var1);
         this.didEventCode.setSelectedItem("event_code");
         replaceComboItems(this.cluster, var1);
         this.cluster.setSelectedItem("firm");
         replaceListItems(this.variables, var1);
         setListSelectedValues(this.variables, Arrays.asList("Size", "Lev", "ROA"));
         replaceListItems(this.absorb, var1);
         setListSelectedValues(this.absorb, Arrays.asList("firm", "year"));
         this.didAction.setSelectedItem("DID 交互回归");
         this.didEstimator.setSelectedItem("reghdfe");
         this.rebuilding = false;
         this.showDidBuilderPage();
         this.vce.setSelectedItem("cluster");
         this.updateDidBuilderPreview();
      }

      private void populateDidActionPreviewState(String var1) {
         this.populateDidPreviewState();
         this.rebuilding = true;
         this.didAction.setSelectedItem(var1);
         this.rebuilding = false;
         this.showDidBuilderPage();
         this.updateDidBuilderPreview();
      }

      private void populateOneClickPreviewState() {
         this.rebuilding = true;
         this.categoryList.setSelectedIndex(6);
         this.methodModel.clear();
         this.methodModel.addElement("控制变量组合筛选");
         this.methodModel.addElement("控制变量组合稳健性");
         this.methodList.setSelectedIndex(0);
         this.commandModel.clear();
         this.commandModel.addElement("oneclick");
         this.commandList.setSelectedIndex(0);
         replaceComboItems(this.oneClickY, Arrays.asList("y", "x", "Size", "Lev", "ROA", "Growth", "Cash"));
         this.oneClickY.setSelectedItem("y");
         replaceComboItems(this.oneClickX, Arrays.asList("y", "x", "Size", "Lev", "ROA", "Growth", "Cash"));
         this.oneClickX.setSelectedItem("x");
         replaceComboItems(this.oneClickCluster, Arrays.asList("firm", "year"));
         this.oneClickCluster.setSelectedItem("firm");
         List vars = Arrays.asList("Size", "Lev", "ROA", "Growth", "Cash", "Age");
         replaceListItems(this.oneClickRequired, vars);
         replaceListItems(this.oneClickCandidates, vars);
         this.oneClickCandidates.clearSelection();
         this.oneClickRequired.clearSelection();
         replaceListItems(this.oneClickAbsorb, Arrays.asList("firm", "year"));
         this.oneClickAbsorb.clearSelection();
         this.oneClickEstimator.setSelectedItem("regress");
         this.oneClickP.setSelectedIndex(1);
         this.oneClickVce.setSelectedItem("默认");
         this.exactOneClickCandidatesDisplay.setText("");
         this.exactOneClickRequiredDisplay.setText("");
         this.rebuilding = false;
         this.showOneClickPage("oneclick");
         this.updateOneClickPreview();
      }

      private void populateOneClickResultsPreviewState() {
         this.populateOneClickPreviewState();
         ArrayList var1 = new ArrayList();
         var1.add(new Object[]{"Size", 1});
         var1.add(new Object[]{"Lev", 1});
         var1.add(new Object[]{"Size ROA", 1});
         var1.add(new Object[]{"Lev Growth", 0});
         this.oneClickExternalModel.loadRows(new String[]{"subset", "positive"}, var1);
         this.oneClickExternalControls.clear();
         this.oneClickExternalControls.add(Arrays.asList("Size"));
         this.oneClickExternalControls.add(Arrays.asList("Lev"));
         this.oneClickExternalControls.add(Arrays.asList("Size", "ROA"));
         this.oneClickExternalControls.add(Arrays.asList("Lev", "Growth"));
         this.oneClickOverview.setText("外部 oneclick 结果预览\n\n结果记录：4\n正向显著：3\n负向显著：1\n\n实际运行时直接读取作者命令生成的 subset.dta。");
         this.configureExternalOneClickWidths();
         this.oneClickResultTabs.setSelectedIndex(1);
         this.selectResultView("oneclick", true);
      }

      private void populateMissingPreviewState() {
         this.rebuilding = true;
         this.categoryList.setSelectedIndex(1);
         this.methodModel.clear();

         for (String var2 : Arrays.asList("导入与转换", "数据检查", "变量处理", "样本处理", "合并与追加", "数据结构")) {
            this.methodModel.addElement(var2);
         }

         this.methodList.setSelectedIndex(1);
         this.commandModel.clear();
         this.commandModel.addElement("缺失值分析");
         this.commandModel.addElement("duplicates");
         this.commandList.setSelectedIndex(0);
         this.currentCommand = "__missing_analysis__";
         this.previewArea.setEditable(false);
         this.setWorkspaceBreadcrumb("数据处理  ›  数据检查  ›  缺失值分析");
         this.commandTitle.setText("缺失值分析");
         this.exampleLabel.setText("最简单操作：选择检查变量；面板数据可再选择 firm 和 year 分类查看。");
         this.insightArea
            .setText("主要用途\n检查当前数据中哪些变量存在缺失，并按企业、年份或企业×年份汇总。\n\n推荐数据\n横截面、面板、重复横截面和企业-年份数据。\n\n优点\n同时提供总体、分类汇总、联合明细、具体记录和图形。\n\n局限\n超大型数据的完整扫描需要一定时间。");
         this.syntaxArea.setText("只读分析 | History 记录 misstable summarize | 不修改当前数据");
         List var8 = Arrays.asList("firm", "year", "Size", "Lev", "ROA", "Growth", "CashFlow");
         replaceListItems(this.missingVariables, var8);
         replaceListItems(this.missingGroups, var8);
         this.missingAllVariables.setSelected(false);
         this.missingChooseVariables.setSelected(true);
         this.missingVariables.setEnabled(true);
         this.missingVariables.setSelectedIndices(new int[]{2, 3, 4, 5});
         this.missingMode.setSelectedIndex(2);
         this.missingGroups.setEnabled(true);
         this.missingGroups.setSelectedIndices(new int[]{0, 1});
         this.missingSeparateSummary.setEnabled(true);
         this.formPanel.removeAll();
         int var9 = 0;
         JPanel var3 = new JPanel(new FlowLayout(0, 12, 0));
         var3.setOpaque(false);
         var3.add(this.missingAllVariables);
         var3.add(this.missingChooseVariables);
         JPanel var4 = new JPanel(new BorderLayout(0, 7));
         var4.setOpaque(false);
         var4.add(var3, "North");
         var4.add(this.listPane(this.missingVariables), "Center");
         this.addField(var9++, "检查变量", var4);
         this.addField(var9++, "如何查看缺失值", this.missingMode);
         this.addField(var9++, "分类变量（可多选）", this.listPane(this.missingGroups));
         JPanel var5 = new JPanel(new GridLayout(0, 1, 5, 5));
         var5.setOpaque(false);
         var5.add(this.missingSeparateSummary);
         var5.add(this.missingOnly);
         this.addField(var9++, "结果范围", var5);
         JPanel var6 = new JPanel(new GridLayout(1, 4, 7, 0));
         var6.setOpaque(false);
         var6.add(new JLabel("缺失变量数 ≥"));
         var6.add(this.missingMinCount);
         var6.add(new JLabel("缺失比例 ≥ (%)"));
         var6.add(this.missingMinRate);
         this.addField(var9++, "筛选阈值", var6);
         this.addField(var9++, "排序", this.missingSort);
         GridBagConstraints var7 = this.constraints(0, var9);
         var7.gridwidth = 2;
         var7.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), var7);
         this.previewArea.setText("misstable summarize Size Lev ROA Growth");
         this.runButton.setText("分析缺失值");
         this.runButton.setEnabled(true);
         this.statusLabel.setText("缺失值分析只读 | 当前数据：企业-年份面板 | N=10,000");
         this.rebuilding = false;
      }

      private void populateMissingResultsPreviewState() {
         HxWorkbench.MissingAnalysisResult var1 = new HxWorkbench.MissingAnalysisResult(
            Arrays.asList("Size", "Lev", "ROA", "Growth"), Arrays.asList("firm", "year")
         );
         var1.overallRows.add(new Object[]{"Size", 10000L, 25L, 9975L, 0.25});
         var1.overallRows.add(new Object[]{"Lev", 10000L, 81L, 9919L, 0.81});
         var1.overallRows.add(new Object[]{"ROA", 10000L, 320L, 9680L, 3.2});
         var1.overallRows.add(new Object[]{"Growth", 10000L, 114L, 9886L, 1.14});
         var1.separateRows.put("firm", Arrays.asList(new Object[]{"000004", 12L, 8L, 40L, 16.67}, new Object[]{"000002", 17L, 3L, 65L, 4.41}));
         var1.separateRows.put("year", Arrays.asList(new Object[]{"2020", 856L, 73L, 3351L, 2.13}, new Object[]{"2019", 841L, 16L, 3348L, 0.48}));
         var1.jointColumns = new String[]{"firm", "year", "Size", "Lev", "ROA", "Growth", "检查变量数", "缺失变量数", "缺失比例(%)"};
         var1.jointRows.add(new Object[]{"000001", "2020", "有数据", "缺失", "有数据", "缺失", 4, 2, 50.0});
         var1.jointRows.add(new Object[]{"000001", "2021", "有数据", "有数据", "有数据", "缺失", 4, 1, 25.0});
         var1.jointRows.add(new Object[]{"000002", "2020", "缺失", "缺失", "有数据", "缺失", 4, 3, 75.0});
         var1.recordColumns = new String[]{"观测序号", "firm", "year", "缺失变量", "缺失变量数", "缺失比例(%)"};
         var1.recordRows.add(new Object[]{138L, "000001", "2020", "Lev、Growth", 2, 50.0});
         var1.recordRows.add(new Object[]{155L, "000002", "2020", "Size、Lev、Growth", 3, 75.0});
         var1.recordObservationNumbers.add(138L);
         var1.recordObservationNumbers.add(155L);
         var1.variableChartLabels.addAll(var1.checkedNames);
         var1.variableChartRates.addAll(Arrays.asList(0.25, 0.81, 3.2, 1.14));
         var1.groupChartLabels.addAll(Arrays.asList("2018", "2019", "2020", "2021"));
         var1.groupChartRates.addAll(Arrays.asList(1.2, 1.9, 8.5, 2.4));
         var1.matrix = new boolean[][]{{false, false, false, false}, {false, true, false, true}, {true, true, false, true}, {false, false, false, false}};
         this.populateMissingResults(var1);
         this.missingResultTabs.setSelectedIndex(3);
      }

      private void populateHomePreviewState() {
         this.rebuilding = true;
         this.categoryModel.clear();
         this.categoryModel.addElement(new HxWorkbench.Category("开始", "home"));
         this.categoryModel.addElement(new HxWorkbench.Category("数据处理", "data"));
         this.categoryModel.addElement(new HxWorkbench.Category("统计", "stats"));
         this.categoryModel.addElement(new HxWorkbench.Category("回归模型", "reg"));
         this.categoryModel.addElement(new HxWorkbench.Category("后估计", "post"));
         this.categoryModel.addElement(new HxWorkbench.Category("图形", "graph"));
         this.categoryModel.addElement(new HxWorkbench.Category("OneClick 专区", "oneclick"));
         this.categoryModel.addElement(new HxWorkbench.Category("测试数据", "test"));
         this.categoryModel.addElement(new HxWorkbench.Category("性能设置", "performance"));
         this.categoryModel.addElement(new HxWorkbench.Category("常用命令", "favorites"));
         this.categoryModel.addElement(new HxWorkbench.Category("最近使用", "recent"));
         this.categoryList.setSelectedIndex(0);
         this.rebuilding = false;
         this.showHomePage();
         this.dataLabel.setText("尚未载入数据");
         this.currentDataLayout.show(this.currentDataCards, "empty");
         this.statusLabel.setText("尚未载入数据 | 从开始页选择下一步");
      }

      private void populateConvertPreviewState() {
         this.rebuilding = true;
         this.categoryList.setSelectedIndex(1);
         this.methodModel.clear();

         for (String var2 : Arrays.asList("导入与转换", "数据检查", "变量处理", "样本处理", "合并与追加", "数据结构")) {
            this.methodModel.addElement(var2);
         }

         this.methodList.setSelectedIndex(0);
         this.commandModel.clear();
         this.commandModel.addElement("hxconvert");
         this.commandList.setSelectedIndex(0);
         this.rebuilding = false;
         this.showConvertDtaPage();
         this.rebuilding = true;
         this.convertInputFile.setText("data/企业数据.xlsx");
         this.convertOutputFile.setText("data/企业数据.dta");
         this.convertSheet.removeAllItems();
         this.convertSheet.addItem("Sheet1");
         this.convertFormatLayout.show(this.convertFormatCards, "excel");
         this.convertDetected.setText("已识别：Excel　预计 10,236 行 × 42 列");
         this.previewArea.setText("import excel using \"data/企业数据.xlsx\", sheet(\"Sheet1\") firstrow clear\nsave \"data/企业数据.dta\"");
         this.importPreviewModel
            .loadRows(
               new String[]{"stkcd", "year", "Size", "Lev", "ROA"},
               Arrays.asList(
                  new Object[]{"000001", 2020, 22.43, 0.53, 0.041},
                  new Object[]{"000001", 2021, 22.61, 0.55, 0.038},
                  new Object[]{"000002", 2020, 21.88, 0.47, 0.052},
                  new Object[]{"600000", 2020, 23.1, 0.62, 0.034}
               )
            );
         this.importPreviewLabel.setText("转换前预览 | 预计观测数：10,236 | 预计变量数：42 | 数值：31 | 字符串：11");
         this.importIssues.setText("发现 3 个需要注意的问题：\n\n1. stkcd 检测到前导零，将保留为字符串。\n\n2. year 已识别为数值年份。\n\n3. 第 7 列同时包含数字和文本，建议作为字符串检查。\n\n原始文件不会被修改。");
         this.configureImportPreviewWidths();
         this.selectResultView("convert", true);
         this.statusLabel.setText("转换预览只读 | 原始文件不会修改 | 前导零保护已开启");
         this.rebuilding = false;
      }

      private void clampInspectorDividers() {
         if (this.dataSummarySplit != null) {
            int height = this.dataSummarySplit.getHeight();
            if (height > 0) {
               int dividerSize = Math.max(0, this.dataSummarySplit.getDividerSize());
               int minData = 135;
               int minSummary = 105;
               int current = this.dataSummarySplit.getDividerLocation();
               if (current <= 0 || current >= height - dividerSize) current = (int)Math.round(height * 0.68);
               int max = Math.max(minData, height - minSummary - dividerSize);
               int target = Math.max(minData, Math.min(current, max));
               if (target != this.dataSummarySplit.getDividerLocation()) this.dataSummarySplit.setDividerLocation(target);
            }
         }
         if (this.inspectorLowerSplit != null) {
            int height = this.inspectorLowerSplit.getHeight();
            if (height > 0) {
               int dividerSize = Math.max(0, this.inspectorLowerSplit.getDividerSize());
               int minVariable = 120;
               int minProperty = 120;
               int current = this.inspectorLowerSplit.getDividerLocation();
               if (current <= 0 || current >= height - dividerSize) current = (int)Math.round(height * 0.54);
               int max = Math.max(minVariable, height - minProperty - dividerSize);
               int target = Math.max(minVariable, Math.min(current, max));
               if (target != this.inspectorLowerSplit.getDividerLocation()) this.inspectorLowerSplit.setDividerLocation(target);
            }
         }
         if (this.inspectorDataSplit != null) {
            int width = this.inspectorDataSplit.getWidth();
            if (width > 0) {
               int dividerSize = Math.max(0, this.inspectorDataSplit.getDividerSize());
               int minMiddle = 210;
               int minData = 300;
               int current = this.inspectorDataSplit.getDividerLocation();
               if (current <= 0 || current >= width - dividerSize) current = Math.min(250, Math.max(minMiddle, width / 3));
               int max = Math.max(minMiddle, width - minData - dividerSize);
               int target = Math.max(minMiddle, Math.min(current, max));
               if (target != this.inspectorDataSplit.getDividerLocation()) this.inspectorDataSplit.setDividerLocation(target);
            }
         }
      }

      void applyDividerRatios() {
         SwingUtilities.invokeLater(() -> {
            int total = this.commandDataSplit.getWidth();
            if (total > 0) {
               int minInspector = total < 1050 ? 535 : 610;
               int inspector = Math.max(minInspector, Math.min(720, (int)Math.round(total * 0.48)));
               int minCommand = total < 1050 ? 420 : 520;
               int divider = Math.max(minCommand, total - inspector);
               divider = Math.min(divider, Math.max(minCommand, total - 510));
               this.commandDataSplit.setDividerLocation(Math.max(0, divider));
            }
            if (this.inspectorDataSplit != null && this.inspectorDataSplit.getWidth() > 0) {
               this.inspectorDataSplit.setDividerLocation(Math.min(250, Math.max(210, this.inspectorDataSplit.getWidth() / 3)));
            }
            this.clampInspectorDividers();
         });
      }

      private JComponent buildAppHeader() {
         JPanel var1 = new JPanel(new BorderLayout(16, 0));
         var1.setBackground(SURFACE);
         var1.setBorder(BorderFactory.createCompoundBorder(BorderFactory.createMatteBorder(0, 0, 1, 0, BORDER), new EmptyBorder(10, 16, 10, 16)));
         JLabel var2 = new JLabel("实证工作台");
         var2.setForeground(TEXT);
         var2.setFont(var2.getFont().deriveFont(1, 16.0F));
         JLabel var3 = new JLabel("选择方法、设置参数、查看数据，然后运行 Stata 命令");
         var3.setForeground(MUTED);
         var3.setFont(var3.getFont().deriveFont(11.0F));
         JPanel var4 = new JPanel();
         var4.setOpaque(false);
         var4.setLayout(new BoxLayout(var4, 1));
         var4.add(var2);
         var4.add(Box.createVerticalStrut(2));
         var4.add(var3);
         var1.add(var4, "West");
         JLabel var5 = new JLabel("完整命令会写入 Stata History");
         var5.setForeground(MUTED);
         var5.setFont(var5.getFont().deriveFont(11.0F));
         this.inspectorToggle.setVisible(false);
         JPanel var6 = new JPanel(new FlowLayout(2, 10, 0));
         var6.setOpaque(false);
         var6.add(var5);
         var6.add(this.inspectorToggle);
         var1.add(var6, "East");
         return var1;
      }

      private void toggleInspector() {
         boolean var1 = this.inspectorToggle.isSelected();
         Component var2 = this.commandDataSplit.getRightComponent();
         if (var2 != null) {
            var2.setVisible(!var1);
         }

         this.commandDataSplit.setDividerSize(var1 ? 0 : 1);
         this.inspectorToggle.setText(var1 ? "显示数据 / 结果" : "隐藏数据 / 结果");
         if (!var1) {
            this.applyDividerRatios();
         } else {
            this.commandDataSplit.setDividerLocation(1.0);
         }

         this.commandDataSplit.revalidate();
         this.commandDataSplit.repaint();
      }

      private void buildNavigation() {
         this.categoryList.setSelectionMode(0);
         this.categoryList.setFixedCellHeight(28);
         this.categoryList.setCellRenderer(new HxWorkbench.WorkbenchFrame.CategoryRenderer());
         this.methodList.setSelectionMode(0);
         this.commandList.setSelectionMode(0);
         this.methodList.setCellRenderer(new HxWorkbench.WorkbenchFrame.SoftListRenderer());
         this.commandList.setCellRenderer(new HxWorkbench.WorkbenchFrame.CommandListRenderer());
         this.methodList.setFixedCellHeight(28);
         this.commandList.setFixedCellHeight(28);
         this.methodList.setVisibleRowCount(5);
         this.commandList.setVisibleRowCount(10);
         this.categoryList.setBackground(SIDEBAR);
         this.methodList.setBackground(SIDEBAR);
         this.commandList.setBackground(SIDEBAR);

         for (JLabel var2 : Arrays.asList(this.methodCaption, this.commandCaption)) {
            var2.setForeground(MUTED);
            var2.setFont(var2.getFont().deriveFont(1, 10.5F));
            var2.setBorder(new EmptyBorder(0, 2, 5, 0));
         }
      }

      private JComponent buildNavigationContainer() {
         JPanel var1 = new JPanel(new BorderLayout(6, 10));
         var1.setBorder(BorderFactory.createCompoundBorder(BorderFactory.createMatteBorder(0, 0, 0, 1, BORDER), new EmptyBorder(14, 12, 12, 12)));
         var1.setBackground(SIDEBAR);
         JLabel var2 = new JLabel("功能与命令");
         var2.setForeground(TEXT);
         var2.setFont(var2.getFont().deriveFont(1, 14.0F));
         JPanel var3 = new JPanel(new BorderLayout(4, 0));
         var3.setOpaque(false);
         JButton var4 = new JButton("查找");
         styleSecondaryButton(var4);
         var4.addActionListener(var1x -> this.searchCommands());
         this.searchField.addActionListener(var1x -> this.searchCommands());
         this.searchField.setToolTipText("输入中文用途或 Stata 命令名");
         styleTextField(this.searchField);
         var3.putClientProperty("button", var4);
         var3.add(this.searchField, "Center");
         var3.add(var4, "East");
         JPanel var5 = new JPanel(new BorderLayout(0, 8));
         var5.setOpaque(false);
         var5.add(var2, "North");
         var5.add(var3, "South");
         var1.add(var5, "North");
         JPanel var6 = new JPanel();
         var6.setOpaque(false);
         var6.setLayout(new BoxLayout(var6, 1));
         JScrollPane var7 = navigationScroll(this.categoryList);
         var7.setPreferredSize(new Dimension(205, 286));
         var7.setMaximumSize(new Dimension(Integer.MAX_VALUE, 286));
         var6.add(var7);
         var6.add(Box.createVerticalStrut(12));
         var6.add(this.methodCaption);
         var6.add(sectionCaption("方法"));
         JScrollPane var8 = navigationScroll(this.methodList);
         var8.setPreferredSize(new Dimension(205, 116));
         var8.setMaximumSize(new Dimension(Integer.MAX_VALUE, 116));
         var6.add(var8);
         var6.add(Box.createVerticalStrut(12));
         var6.add(this.commandCaption);
         var6.add(sectionCaption("命令"));
         var6.add(navigationScroll(this.commandList));
         var1.add(var6, "Center");
         return var1;
      }


      private JComponent buildSidebarToggleBar() {
         JPanel bar = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 8));
         bar.setOpaque(false);
         bar.setPreferredSize(new Dimension(0, 46));
         bar.setMinimumSize(new Dimension(0, 46));
         this.sidebarToggleButton = new JButton("☰");
         this.sidebarToggleButton.setToolTipText("隐藏左侧导航");
         this.sidebarToggleButton.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(247, 250, 254), new Color(239, 244, 250), TEXT, new Color(226, 232, 240)));
         this.sidebarToggleButton.setBorder(new EmptyBorder(7, 11, 7, 11));
         this.sidebarToggleButton.setFocusPainted(false);
         this.sidebarToggleButton.setContentAreaFilled(false);
         this.sidebarToggleButton.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         this.sidebarToggleButton.setPreferredSize(new Dimension(42, 32));
         this.sidebarToggleButton.addActionListener(e -> this.toggleSidebarCollapsed());
         bar.add(this.sidebarToggleButton);
         return bar;
      }

      private JComponent buildSidebar() {
         this.sidebarButtons.clear();
         JPanel sidebar = new JPanel(new BorderLayout());
         sidebar.setBackground(SURFACE);
         sidebar.setPreferredSize(new Dimension(205, 0));
         this.sidebarPanel = sidebar;
         sidebar.setBorder(BorderFactory.createMatteBorder(0, 0, 0, 1, new Color(226, 232, 240)));

         JPanel nav = new JPanel();
         nav.setOpaque(false);
         nav.setBorder(new EmptyBorder(22, 11, 8, 11));
         nav.setLayout(new BoxLayout(nav, BoxLayout.Y_AXIS));
         nav.add(this.sidebarButton("home", "⌂", "工作台", this::showHomePage));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("data", "▤", "数据", () -> this.browseCategoryOverview("data")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("stats", "▥", "统计", () -> this.browseCategoryOverview("stats")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("graph", "▧", "图形", () -> this.browseCategoryOverview("graph")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("oneclick", "◇", "OneClick", () -> this.browseMethodCategory("oneclick")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("history", "◷", "历史", () -> this.browseCommandCategory("recent", "最近任务")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("settings", "⚙", "设置", () -> this.openHomeTask("special", "performance")));
         sidebar.add(nav, BorderLayout.NORTH);

         JPanel bottom = new JPanel();
         bottom.setOpaque(false);
         bottom.setBorder(new EmptyBorder(8, 18, 20, 18));
         bottom.setLayout(new BoxLayout(bottom, BoxLayout.Y_AXIS));
         JButton guide = new JButton("<html><div style='text-align:left'><b>新手指引</b><br><span style='font-size:9px;color:#718096'>5 分钟快速上手</span><br><span style='font-size:9px;color:#226df6'>立即查看  →</span></div></html>");
         guide.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(new Color(248, 251, 255), new Color(242, 247, 255), new Color(234, 242, 255), TEXT, new Color(210, 225, 248)));
         guide.setBorder(new EmptyBorder(12, 14, 12, 14));
         guide.setHorizontalAlignment(SwingConstants.LEFT);
         guide.setVerticalAlignment(SwingConstants.TOP);
         guide.setFocusPainted(false);
         guide.setContentAreaFilled(false);
         guide.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         guide.setMaximumSize(new Dimension(Integer.MAX_VALUE, 176));
         guide.setPreferredSize(new Dimension(168, 176));
         guide.setAlignmentX(0.0F);
         guide.addActionListener(e -> {
            HxWorkbench.StataBridge.execute("help hxempirical", false);
            HxWorkbench.StataBridge.execute("window manage forward viewer", false);
         });
         bottom.add(guide);
         bottom.add(Box.createVerticalStrut(22));
         JLabel version = new JLabel("版本：" + VERSION);
         version.setForeground(MUTED);
         version.setFont(version.getFont().deriveFont(10.0F));
         version.setAlignmentX(0.0F);
         bottom.add(version);
         bottom.add(Box.createVerticalStrut(5));
         JLabel policy = new JLabel("隐私政策   意见反馈");
         policy.setForeground(ACCENT);
         policy.setFont(policy.getFont().deriveFont(10.0F));
         policy.setAlignmentX(0.0F);
         bottom.add(policy);
         this.sidebarBottomPanel = bottom;
         sidebar.add(bottom, BorderLayout.SOUTH);
         this.setSidebarActive("home");
         this.applySidebarCollapsedState();
         return sidebar;
      }

      private void toggleSidebarCollapsed() {
         this.sidebarCollapsed = !this.sidebarCollapsed;
         this.applySidebarCollapsedState();
      }

      private void applySidebarCollapsedState() {
         if (this.sidebarPanel == null) return;
         this.sidebarPanel.setVisible(!this.sidebarCollapsed);
         int width = this.sidebarCollapsed ? 0 : 205;
         this.sidebarPanel.setPreferredSize(new Dimension(width, 0));
         this.sidebarPanel.setMinimumSize(new Dimension(width, 0));
         if (this.sidebarBottomPanel != null) this.sidebarBottomPanel.setVisible(!this.sidebarCollapsed);
         if (this.sidebarToggleButton != null) {
            this.sidebarToggleButton.setText("☰");
            this.sidebarToggleButton.setToolTipText(this.sidebarCollapsed ? "打开左侧导航" : "隐藏左侧导航");
         }
         for (JButton button : this.sidebarButtons.values()) {
            String label = Objects.toString(button.getClientProperty("hx.sidebar.label"), "");
            String glyph = Objects.toString(button.getClientProperty("hx.sidebar.glyph"), "");
            String expanded = glyph.isBlank() ? label : glyph + "   " + label;
            button.setText("<html><b>" + html(expanded) + "</b></html>");
            button.setHorizontalAlignment(SwingConstants.LEFT);
            button.setBorder(new EmptyBorder(11, 14, 11, 14));
            button.setToolTipText(null);
         }
         this.sidebarPanel.revalidate();
         this.sidebarPanel.repaint();
         Container parent = this.sidebarPanel.getParent();
         if (parent != null) { parent.revalidate(); parent.repaint(); }
      }

      private JButton sidebarButton(String key, String glyph, String label, Runnable action) {
         JButton button = new JButton("<html><b>" + html(label) + "</b></html>");
         button.putClientProperty("hx.sidebar.key", key);
         button.putClientProperty("hx.sidebar.label", label);
         button.putClientProperty("hx.sidebar.glyph", glyph);
         button.setHorizontalAlignment(SwingConstants.LEFT);
         button.setBorder(new EmptyBorder(11, 14, 11, 14));
         button.setMaximumSize(new Dimension(Integer.MAX_VALUE, 46));
         button.setAlignmentX(0.0F);
         button.setFocusPainted(false);
         button.setContentAreaFilled(false);
         button.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         this.sidebarButtons.put(key, button);
         button.addActionListener(e -> {
            this.setSidebarActive(key);
            action.run();
         });
         this.applySidebarStyle(button, key.equals(this.activeSidebarKey));
         return button;
      }

      private void applySidebarStyle(JButton button, boolean active) {
         Color bg = active ? new Color(232, 241, 255) : SURFACE;
         Color hover = active ? new Color(224, 236, 253) : new Color(247, 249, 252);
         Color pressed = active ? new Color(213, 229, 251) : new Color(238, 243, 249);
         Color fg = active ? new Color(20, 96, 214) : new Color(43, 55, 73);
         button.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(bg, hover, pressed, fg, active ? new Color(210, 226, 249) : SURFACE));
      }

      private void setSidebarActive(String key) {
         this.activeSidebarKey = key == null || key.isBlank() ? "home" : key;
         for (Entry<String, JButton> entry : this.sidebarButtons.entrySet()) {
            this.applySidebarStyle(entry.getValue(), entry.getKey().equals(this.activeSidebarKey));
         }
      }

      private void syncSidebarFromContext() {
         String key = "home";
         if ("data".equals(this.activeCategoryCode)) key = "data";
         else if ("stats".equals(this.activeCategoryCode) || "reg".equals(this.activeCategoryCode) || "post".equals(this.activeCategoryCode)) key = "stats";
         else if ("graph".equals(this.activeCategoryCode)) key = "graph";
         else if ("oneclick".equals(this.activeCategoryCode) || "did".equals(this.activeCategoryCode)) key = "oneclick";
         else if ("recent".equals(this.activeCategoryCode)) key = "history";
         else if ("performance".equals(this.activeCategoryCode) || "test".equals(this.activeCategoryCode)) key = "settings";
         this.setSidebarActive(key);
      }

      private JButton homeQuickButton(String title, String glyph, Runnable action) {
         JButton button = new JButton("<html><div style='text-align:center'><span style='font-size:18px;color:#2563d9'>" + html(glyph) + "</span><br><b>" + html(title) + "</b></div></html>");
         button.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(247, 250, 255), new Color(236, 244, 255), TEXT, new Color(216, 225, 238)));
         button.setBorder(new EmptyBorder(10, 8, 10, 8));
         button.setFocusPainted(false);
         button.setContentAreaFilled(false);
         button.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         button.addActionListener(e -> action.run());
         return button;
      }

      private JButton homeFeatureButton(String title, String subtitle, String glyph, Runnable action) {
         JButton button = new JButton("<html><div style='text-align:center'><span style='font-size:16px;color:#2a66be'>" + html(glyph) + "</span><br><b>" + html(title) + "</b><br><span style='font-size:8px;color:#637083'>" + html(subtitle) + "</span></div></html>");
         button.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 250, 253), new Color(239, 244, 250), TEXT, new Color(222, 228, 237)));
         button.setBorder(new EmptyBorder(10, 8, 10, 8));
         button.setFocusPainted(false);
         button.setContentAreaFilled(false);
         button.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         button.addActionListener(e -> action.run());
         return button;
      }

      private static String taskGlyph(String title) {
         if (title.contains("导入")) return "▤";
         if (title.contains("描述")) return "▥";
         if (title.contains("基准")) return "↗";
         if (title.contains("固定")) return "◆";
         if (title.contains("双重")) return "DID";
         if (title.contains("OneClick")) return "⚡";
         return "→";
      }


      private JPanel refCard() {
         JPanel p = new JPanel();
         p.setBackground(SURFACE);
         p.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220, 228, 240), 10), new EmptyBorder(14, 16, 14, 16)));
         return p;
      }

      private JButton refButton(String text, boolean primary) {
         JButton b = new JButton(text);
         Color bg = primary ? new Color(34, 109, 246) : SURFACE;
         Color hover = primary ? new Color(28, 94, 222) : new Color(247, 250, 254);
         Color pressed = primary ? new Color(24, 82, 198) : new Color(239, 244, 250);
         Color fg = primary ? Color.WHITE : TEXT;
         Color border = primary ? new Color(34, 109, 246) : new Color(215, 224, 237);
         b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(bg, hover, pressed, fg, border));
         b.setBorder(new EmptyBorder(8, 15, 8, 15));
         b.setFocusPainted(false);
         b.setContentAreaFilled(false);
         b.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         return b;
      }

      private JButton refTask(String glyph, String title, String subtitle, Color accent, Runnable action) {
         JButton b = new JButton("<html><div style='text-align:left'><b>" + html(title) + "</b><br><span style='font-size:9px;color:#6b7890'>" + html(subtitle) + "</span></div></html>");
         b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(249, 251, 254), new Color(240, 245, 252), TEXT, new Color(221, 228, 239)));
         b.setBorder(new EmptyBorder(11, 14, 11, 14));
         b.setHorizontalAlignment(SwingConstants.LEFT);
         b.setFocusPainted(false);
         b.setContentAreaFilled(false);
         b.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         b.addActionListener(e -> action.run());
         return b;
      }

      private JButton refQuick(String glyph, String title, Runnable action) {
         JButton b = new JButton("<html><div style='text-align:center'><b>" + html(title) + "</b></div></html>");
         b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 251, 255), new Color(239, 245, 253), TEXT, new Color(221, 228, 239)));
         b.setBorder(new EmptyBorder(8, 6, 8, 6));
         b.setFocusPainted(false);
         b.setContentAreaFilled(false);
         b.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         b.addActionListener(e -> action.run());
         return b;
      }

      private static String colorHex(Color c) {
         return String.format(Locale.ROOT, "#%02x%02x%02x", c.getRed(), c.getGreen(), c.getBlue());
      }

      private JPanel refSectionTitle(String text) {
         JPanel row = new JPanel(new BorderLayout());
         row.setOpaque(false);
         JLabel label = new JLabel(text);
         label.setForeground(TEXT);
         label.setFont(label.getFont().deriveFont(Font.BOLD, 14.0F));
         row.add(label, BorderLayout.WEST);
         return row;
      }

      private JPanel buildChooserRecommendationPanel() {
         JPanel right = this.refCard();
         right.setLayout(new BoxLayout(right, BoxLayout.Y_AXIS));
         right.setPreferredSize(new Dimension(240, 0));
         JLabel t = new JLabel("▥  推荐路径");
         t.setForeground(TEXT);
         t.setFont(t.getFont().deriveFont(Font.BOLD, 15.0F));
         t.setAlignmentX(0.0F);
         right.add(t);
         right.add(Box.createVerticalStrut(24));
         String[][] steps = {
            {"1", "先用常用命令", "从常用命令入手，快速完成基础分析。"},
            {"2", "看示例与说明", "查看示例与说明，理解命令用法与适用场景。"},
            {"3", "再进入进阶命令", "根据需求选择进阶命令，满足更复杂的分析。"}
         };
         Color[] colors = {new Color(34,109,246), new Color(31,169,105), new Color(118,83,224)};
         for (int i=0; i<steps.length; i++) {
            JPanel row = new JPanel(new BorderLayout(10, 0));
            row.setOpaque(false);
            JLabel n = new JLabel(steps[i][0], SwingConstants.CENTER);
            n.setOpaque(true); n.setBackground(colors[i]); n.setForeground(Color.WHITE);
            n.setFont(n.getFont().deriveFont(Font.BOLD, 12.0F));
            n.setPreferredSize(new Dimension(30,30));
            JPanel txt = new JPanel(); txt.setOpaque(false); txt.setLayout(new BoxLayout(txt, BoxLayout.Y_AXIS));
            JLabel a = new JLabel(steps[i][1]); a.setForeground(TEXT); a.setFont(a.getFont().deriveFont(Font.BOLD, 12.0F));
            JLabel d = new JLabel("<html><div style='width:145px;color:#718096'>"+html(steps[i][2])+"</div></html>");
            txt.add(a); txt.add(Box.createVerticalStrut(6)); txt.add(d);
            row.add(n, BorderLayout.WEST); row.add(txt, BorderLayout.CENTER);
            row.setMaximumSize(new Dimension(Integer.MAX_VALUE, 120));
            right.add(row);
            if (i < 2) { right.add(Box.createVerticalStrut(18)); }
         }
         right.add(Box.createVerticalGlue());
         JPanel tip = new JPanel(new BorderLayout(8,8));
         tip.setBackground(new Color(255,250,241));
         tip.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(255,219,166), 9), new EmptyBorder(13,13,13,13)));
         JLabel tipText = new JLabel("<html><b><span style='color:#f59e0b'>☼ 小贴士</span></b><br><br><span style='color:#68758b'>命令太多时，优先从常用命令开始，逐步深入更高阶方法！</span></html>");
         tip.add(tipText, BorderLayout.CENTER);
         tip.setMaximumSize(new Dimension(Integer.MAX_VALUE, 145));
         right.add(tip);
         return right;
      }

      private JButton chooserCommandCard(String cmd, String title, String desc, String example, Color accent) {
         JButton b = new JButton("<html><div style='text-align:left'><span style='font-size:10px;color:"+colorHex(accent)+"'><b>"+html(cmd)+"</b></span><br><span style='font-size:13px'><b>"+html(title)+"</b></span><br><span style='font-size:9px;color:#6f7d94'>"+html(desc)+"</span><br><span style='font-size:8px;color:"+colorHex(accent)+"'>示例："+html(example)+"</span></div></html>");
         b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(249,251,254), new Color(240,245,252), TEXT, new Color(220,228,239)));
         b.setBorder(new EmptyBorder(12, 16, 12, 16));
         b.setHorizontalAlignment(SwingConstants.LEFT);
         b.setVerticalAlignment(SwingConstants.TOP);
         b.setFocusPainted(false); b.setContentAreaFilled(false);
         b.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         b.addActionListener(e -> this.openCommandPage(cmd));
         return b;
      }

      private JPanel chooserGroup(String title, String[][] rows, Color accent) {
         JPanel g = this.refCard();
         g.setLayout(new BoxLayout(g, BoxLayout.Y_AXIS));
         JLabel h = new JLabel(title); h.setForeground(TEXT); h.setFont(h.getFont().deriveFont(Font.BOLD, 12.0F)); h.setAlignmentX(0.0F);
         g.add(h); g.add(Box.createVerticalStrut(8));
         for (String[] row : rows) {
            JButton b = new JButton("<html><div style='text-align:left'><b>"+html(row[0])+"</b>&nbsp;&nbsp;<span style='color:#68758b'>"+html(row[1])+"</span><span style='float:right'> ›</span></div></html>");
            b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(249,251,254), new Color(242,246,251), TEXT, SURFACE));
            b.setBorder(new EmptyBorder(5, 2, 5, 2)); b.setHorizontalAlignment(SwingConstants.LEFT); b.setFocusPainted(false); b.setContentAreaFilled(false);
            String cmd = row[0]; b.addActionListener(e -> this.openCommandPage(cmd));
            g.add(b);
         }
         return g;
      }


      private JComponent buildHomeContainerV130Marker() {
         return null;
      }

      private JPanel homeCardV130() {
         JPanel card = cardPanel();
         card.setBackground(SURFACE);
         card.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(219, 226, 237), 12),
            new EmptyBorder(14, 16, 14, 16)
         ));
         return card;
      }

      private JButton homeQuickTileV130(String title, String detail, String glyph, Runnable action) {
         JButton b = new JButton(
            "<html><div style='text-align:center'><span style='font-size:22px;color:#2f6fe4'>" + html(glyph) + "</span><br>"
               + "<b>" + html(title) + "</b><br><span style='font-size:9px;color:#718096'>" + html(detail) + "</span></div></html>"
         );
         b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(247, 250, 255), new Color(240, 246, 255), TEXT, SURFACE));
         b.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220, 227, 238), 10));
         b.setFocusPainted(false);
         b.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         b.setPreferredSize(new Dimension(122, 104));
         b.addActionListener(e -> action.run());
         return b;
      }

      private JButton homeListRowV130(String title, String detail, String glyph, Runnable action) {
         JButton row = new JButton(
            "<html><table width='360' cellpadding='0' cellspacing='0'><tr>"
               + "<td width='42'><span style='font-size:17px;color:#2f6fe4'>" + html(glyph) + "</span></td>"
               + "<td><b>" + html(title) + "</b><br><span style='font-size:9px;color:#718096'>" + html(detail) + "</span></td>"
               + "<td width='18' align='right'><span style='color:#607089'>›</span></td>"
               + "</tr></table></html>"
         );
         row.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 251, 255), new Color(241, 246, 253), TEXT, SURFACE));
         row.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createMatteBorder(1, 0, 0, 0, new Color(234, 238, 244)),
            new EmptyBorder(5, 8, 5, 8)
         ));
         row.setHorizontalAlignment(SwingConstants.LEFT);
         row.setFocusPainted(false);
         row.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         row.setMaximumSize(new Dimension(Integer.MAX_VALUE, 54));
         row.setPreferredSize(new Dimension(360, 54));
         row.addActionListener(e -> action.run());
         return row;
      }

      private JPanel homeListSectionV130(String title, Object[][] rows) {
         JPanel card = this.homeCardV130();
         card.setLayout(new BorderLayout(0, 10));
         JLabel head = new JLabel(title);
         head.setForeground(TEXT);
         head.setFont(head.getFont().deriveFont(Font.BOLD, 14.0F));
         card.add(head, BorderLayout.NORTH);
         JPanel list = new JPanel();
         list.setBackground(SURFACE);
         list.setLayout(new BoxLayout(list, BoxLayout.Y_AXIS));
         boolean first = true;
         for (Object[] spec : rows) {
            JButton row = this.homeListRowV130((String)spec[0], (String)spec[1], (String)spec[2], (Runnable)spec[3]);
            if (first) {
               row.setBorder(new EmptyBorder(5, 8, 5, 8));
               first = false;
            }
            list.add(row);
         }
         card.add(list, BorderLayout.CENTER);
         return card;
      }

      private JComponent buildHomeContainer() {
         JPanel root = new JPanel(new BorderLayout());
         root.setBackground(APP_BG);

         JPanel body = new JPanel();
         body.setBackground(APP_BG);
         body.setLayout(new BoxLayout(body, BoxLayout.Y_AXIS));
         body.setBorder(new EmptyBorder(20, 24, 16, 24));

         JPanel header = new JPanel(new BorderLayout());
         header.setOpaque(false);
         JPanel heading = new JPanel();
         heading.setOpaque(false);
         heading.setLayout(new BoxLayout(heading, BoxLayout.Y_AXIS));
         JLabel title = new JLabel("实证工作台");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD, 28.0F));
         JLabel sub = new JLabel("选择任务或直接搜索 Stata 命令");
         sub.setForeground(MUTED);
         sub.setFont(sub.getFont().deriveFont(10.5F));
         heading.add(title);
         heading.add(Box.createVerticalStrut(4));
         heading.add(sub);
         header.add(heading, BorderLayout.WEST);
         JPanel topActions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 0));
         topActions.setOpaque(false);
         JButton openStata = this.refButton("打开 Stata", false);
         openStata.addActionListener(e -> this.setState(JFrame.ICONIFIED));
         JButton help = this.refButton("帮助", false);
         help.addActionListener(e -> this.openHelp());
         topActions.add(openStata);
         topActions.add(help);
         header.add(topActions, BorderLayout.EAST);
         header.setMaximumSize(new Dimension(Integer.MAX_VALUE, 66));
         body.add(header);
         body.add(Box.createVerticalStrut(14));

         JPanel searchWrap = this.homeCardV130();
         searchWrap.setLayout(new BorderLayout(10, 0));
         searchWrap.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(213, 222, 236), 11),
            new EmptyBorder(6, 12, 6, 12)
         ));
         JLabel searchIcon = new JLabel("⌕");
         searchIcon.setForeground(new Color(72, 92, 125));
         searchIcon.setFont(searchIcon.getFont().deriveFont(Font.BOLD, 18.0F));
         searchWrap.add(searchIcon, BorderLayout.WEST);
         this.searchField.setText("");
         this.searchField.setToolTipText("搜索功能或直接输入 Stata 命令，例如 reg y x1 x2");
         this.searchField.setBorder(null);
         this.searchField.setBackground(SURFACE);
         this.searchField.setFont(this.searchField.getFont().deriveFont(12.0F));
         this.searchField.addActionListener(e -> this.smartHomeSearch());
         searchWrap.add(this.searchField, BorderLayout.CENTER);
         JLabel shortcut = new JLabel("Ctrl + K");
         shortcut.setForeground(MUTED);
         shortcut.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220, 227, 238), 7), new EmptyBorder(3, 8, 3, 8)));
         searchWrap.add(shortcut, BorderLayout.EAST);
         searchWrap.setMaximumSize(new Dimension(Integer.MAX_VALUE, 50));
         body.add(searchWrap);
         body.add(Box.createVerticalStrut(14));

         JPanel top = new JPanel(new GridBagLayout());
         top.setOpaque(false);
         GridBagConstraints tc = new GridBagConstraints();
         tc.gridy = 0; tc.fill = GridBagConstraints.BOTH; tc.weighty = 1.0;

         JPanel quick = this.homeCardV130();
         quick.setLayout(new BorderLayout(0, 12));
         JLabel quickTitle = new JLabel("快捷操作");
         quickTitle.setForeground(TEXT);
         quickTitle.setFont(quickTitle.getFont().deriveFont(Font.BOLD, 14.0F));
         quick.add(quickTitle, BorderLayout.NORTH);
         JPanel quickGrid = new JPanel(new GridLayout(1, 6, 10, 0));
         quickGrid.setOpaque(false);
         quickGrid.add(this.homeQuickTileV130("导入数据", "Excel / CSV / DTA", "▣", () -> this.navigateTo("data", "导入与转换", "hxconvert")));
         quickGrid.add(this.homeQuickTileV130("描述统计", "summarize / tabstat", "▥", () -> this.openCommandPage("summarize")));
         quickGrid.add(this.homeQuickTileV130("基准回归", "xtreg / reghdfe", "↗", () -> this.openBaselineRegressionWorkspace()));
         quickGrid.add(this.homeQuickTileV130("固定效应", "areg / reghdfe", "▦", () -> this.openCommandPage("reghdfe")));
         quickGrid.add(this.homeQuickTileV130("双重差分", "didregress", "⌘", () -> this.openCommandPage("didregress")));
         quickGrid.add(this.homeQuickTileV130("OneClick", "控制变量组合", "✦", () -> this.openCommandPage("oneclick")));
         quick.add(quickGrid, BorderLayout.CENTER);
         tc.gridx = 0; tc.weightx = 0.70; tc.insets = new Insets(0, 0, 0, 12);
         top.add(quick, tc);

         JPanel data = this.homeCardV130();
         data.setLayout(new BorderLayout(0, 12));
         JLabel dataTitle = new JLabel("当前数据");
         dataTitle.setForeground(TEXT);
         dataTitle.setFont(dataTitle.getFont().deriveFont(Font.BOLD, 14.0F));
         data.add(dataTitle, BorderLayout.NORTH);
         JPanel dataCenter = new JPanel();
         dataCenter.setOpaque(false);
         dataCenter.setLayout(new BoxLayout(dataCenter, BoxLayout.Y_AXIS));
         this.homeDatasetStatus.setHorizontalAlignment(SwingConstants.CENTER);
         this.homeDatasetStatus.setAlignmentX(0.5F);
         this.homeDatasetStatus.setForeground(TEXT);
         this.homeDatasetStatus.setFont(this.homeDatasetStatus.getFont().deriveFont(Font.BOLD, 14.0F));
         this.homeDatasetDetail.setHorizontalAlignment(SwingConstants.CENTER);
         this.homeDatasetDetail.setAlignmentX(0.5F);
         this.homeDatasetDetail.setForeground(MUTED);
         this.homeDatasetDetail.setFont(this.homeDatasetDetail.getFont().deriveFont(9.5F));
         dataCenter.add(Box.createVerticalGlue());
         dataCenter.add(this.homeDatasetStatus);
         dataCenter.add(Box.createVerticalStrut(6));
         dataCenter.add(this.homeDatasetDetail);
         dataCenter.add(Box.createVerticalGlue());
         data.add(dataCenter, BorderLayout.CENTER);
         JPanel dataButtons = new JPanel(new GridLayout(1, 3, 8, 0));
         dataButtons.setOpaque(false);
         JButton dta = this.refButton("打开 DTA", true);
         dta.addActionListener(e -> this.chooseAndLoadDta());
         JButton excel = this.refButton("导入 Excel/CSV", false);
         excel.addActionListener(e -> this.navigateTo("data", "导入与转换", "hxconvert"));
         JButton auto = this.refButton("auto 示例", false);
         auto.addActionListener(e -> this.runUtility("sysuse auto, clear", true));
         dataButtons.add(dta); dataButtons.add(excel); dataButtons.add(auto);
         data.add(dataButtons, BorderLayout.SOUTH);
         tc.gridx = 1; tc.weightx = 0.30; tc.insets = new Insets(0, 0, 0, 0);
         top.add(data, tc);
         top.setMaximumSize(new Dimension(Integer.MAX_VALUE, 220));
         body.add(top);
         body.add(Box.createVerticalStrut(14));

         Object[][] commonRows = new Object[][]{
            {"导入数据", "Excel / CSV / DTA", "▣", (Runnable)() -> this.navigateTo("data", "导入与转换", "hxconvert")},
            {"描述统计", "summarize / tabstat", "▥", (Runnable)() -> this.openCommandPage("summarize")},
            {"基准回归", "xtreg / reghdfe / regress", "↗", (Runnable)() -> this.openBaselineRegressionWorkspace()},
            {"固定效应", "areg / reghdfe / xtreg", "▦", (Runnable)() -> this.openCommandPage("reghdfe")},
            {"双重差分", "didregress / xtdidregress", "⌘", (Runnable)() -> this.openCommandPage("didregress")},
            {"OneClick", "控制变量组合", "✦", (Runnable)() -> this.openCommandPage("oneclick")}
         };
         JPanel common = this.homeListSectionV130("常用任务", commonRows);

         JPanel recent = this.homeCardV130();
         recent.setLayout(new BorderLayout(0, 10));
         JLabel recentTitle = new JLabel("最近任务");
         recentTitle.setForeground(TEXT);
         recentTitle.setFont(recentTitle.getFont().deriveFont(Font.BOLD, 14.0F));
         recent.add(recentTitle, BorderLayout.NORTH);
         this.homeRecentPanel.setOpaque(false);
         recent.add(this.homeRecentPanel, BorderLayout.CENTER);
         JButton history = this.refButton("查看全部历史 →", false);
         history.addActionListener(e -> this.browseCategoryOverview("recent"));
         recent.add(history, BorderLayout.SOUTH);

         Object[][] moreRows = new Object[][]{
            {"导入与转换", "Excel / CSV / DTA", "⇄", (Runnable)() -> this.navigateTo("data", "导入与转换", "hxconvert")},
            {"数据检查", "缺失 / 重复 / 唯一键", "◎", (Runnable)() -> this.browseMethod("data", "数据检查")},
            {"变量处理", "generate / replace", "✣", (Runnable)() -> this.browseMethod("data", "变量处理")},
            {"样本处理", "keep / drop", "⌑", (Runnable)() -> this.browseMethod("data", "样本处理")},
            {"合并与追加", "merge / append", "⇆", (Runnable)() -> this.browseMethod("data", "合并与追加")},
            {"数据结构", "reshape / xtset / tsset", "▤", (Runnable)() -> this.browseMethod("data", "数据结构")},
            {"相关分析", "correlate / pwcorr", "⌁", (Runnable)() -> this.openCommandPage("pwcorr")},
            {"均值检验", "ttest", "⌗", (Runnable)() -> this.openCommandPage("ttest")},
            {"频数列联", "tabulate", "▦", (Runnable)() -> this.openCommandPage("tabulate")}
         };
         JPanel more = this.homeListSectionV130("更多功能", moreRows);

         JPanel lower = new JPanel(new GridLayout(1, 3, 12, 0));
         lower.setOpaque(false);
         lower.add(common);
         lower.add(recent);
         lower.add(more);
         lower.setMaximumSize(new Dimension(Integer.MAX_VALUE, 382));
         body.add(lower);
         body.add(Box.createVerticalGlue());

         JScrollPane scroll = new JScrollPane(body);
         scroll.setBorder(null);
         scroll.getVerticalScrollBar().setUnitIncrement(18);
         scroll.setBackground(APP_BG);
         root.add(scroll, BorderLayout.CENTER);
         return root;
      }

      private JComponent buildHomeContainerLegacy() {
         JPanel root = new JPanel(new BorderLayout(0, 14));
         root.setBackground(APP_BG);
         root.setBorder(new EmptyBorder(20, 24, 16, 24));

         JPanel header = new JPanel(new BorderLayout());
         header.setOpaque(false);
         JPanel heading = new JPanel();
         heading.setOpaque(false);
         heading.setLayout(new BoxLayout(heading, BoxLayout.Y_AXIS));
         JLabel title = new JLabel("实证工作台");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD, 27.0F));
         JLabel sub = new JLabel("选择任务或直接搜索 Stata 命令");
         sub.setForeground(MUTED);
         sub.setFont(sub.getFont().deriveFont(10.5F));
         heading.add(title);
         heading.add(Box.createVerticalStrut(3));
         heading.add(sub);
         header.add(heading, BorderLayout.WEST);
         JPanel topActions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 0));
         topActions.setOpaque(false);
         JButton openStata = this.refButton("打开 Stata", false);
         openStata.addActionListener(e -> this.setState(JFrame.ICONIFIED));
         JButton help = this.refButton("帮助", false);
         help.addActionListener(e -> this.openHelp());
         topActions.add(openStata);
         topActions.add(help);
         header.add(topActions, BorderLayout.EAST);
         root.add(header, BorderLayout.NORTH);

         JPanel body = new JPanel();
         body.setOpaque(false);
         body.setLayout(new BoxLayout(body, BoxLayout.Y_AXIS));

         JPanel topRow = new JPanel(new GridBagLayout());
         topRow.setOpaque(false);
         topRow.setAlignmentX(0.0F);
         topRow.setMaximumSize(new Dimension(Integer.MAX_VALUE, 235));
         GridBagConstraints gc = new GridBagConstraints();
         gc.gridy = 0;
         gc.fill = GridBagConstraints.BOTH;
         gc.weighty = 1.0;

         JPanel hero = this.refCard();
         hero.setLayout(new GridLayout(1, 2, 18, 0));
         hero.setBackground(new Color(246,250,255));
         JPanel search = new JPanel();
         search.setOpaque(false);
         search.setLayout(new BoxLayout(search, BoxLayout.Y_AXIS));
         JLabel start = new JLabel("开始分析");
         start.setForeground(TEXT);
         start.setFont(start.getFont().deriveFont(Font.BOLD, 20.0F));
         search.add(start);
         search.add(Box.createVerticalStrut(12));
         JPanel searchLine = new JPanel(new BorderLayout(8,0));
         searchLine.setOpaque(false);
         styleTextField(this.searchField);
         this.searchField.setToolTipText("搜索任务或命令");
         JButton startBtn = this.refButton("开始", true);
         startBtn.addActionListener(e -> this.smartHomeSearch());
         this.searchField.addActionListener(e -> this.smartHomeSearch());
         searchLine.add(this.searchField, BorderLayout.CENTER);
         searchLine.add(startBtn, BorderLayout.EAST);
         search.add(searchLine);
         hero.add(search);

         JPanel quick = new JPanel(new BorderLayout(0,10));
         quick.setOpaque(false);
         JLabel quickTitle = new JLabel("快速开始");
         quickTitle.setForeground(TEXT);
         quickTitle.setFont(quickTitle.getFont().deriveFont(Font.BOLD, 13.0F));
         quick.add(quickTitle, BorderLayout.NORTH);
         JPanel quickGrid = new JPanel(new GridLayout(1,5,8,0));
         quickGrid.setOpaque(false);
         quickGrid.add(this.refQuick("", "基准回归", this::openBaselineRegressionWorkspace));
         quickGrid.add(this.refQuick("", "固定效应", () -> this.browseMethod("reg", "固定效应线性回归")));
         quickGrid.add(this.refQuick("", "双重差分", () -> this.browseMethod("reg", "双重差分")));
         quickGrid.add(this.refQuick("", "描述统计", () -> this.browseMethod("stats", "描述统计")));
         quickGrid.add(this.refQuick("", "OneClick", () -> this.browseMethodCategory("oneclick")));
         quick.add(quickGrid, BorderLayout.CENTER);
         hero.add(quick);

         gc.gridx = 0;
         gc.weightx = 0.72;
         gc.insets = new Insets(0,0,0,12);
         topRow.add(hero, gc);

         JPanel data = this.refCard();
         data.setLayout(new BorderLayout(0, 10));
         JLabel dataTitle = new JLabel("当前数据");
         dataTitle.setForeground(TEXT);
         dataTitle.setFont(dataTitle.getFont().deriveFont(Font.BOLD, 14.0F));
         data.add(dataTitle, BorderLayout.NORTH);
         JPanel dataCenter = new JPanel();
         dataCenter.setOpaque(false);
         dataCenter.setLayout(new BoxLayout(dataCenter, BoxLayout.Y_AXIS));
         this.homeDatasetStatus.setHorizontalAlignment(SwingConstants.CENTER);
         this.homeDatasetStatus.setForeground(TEXT);
         this.homeDatasetStatus.setFont(this.homeDatasetStatus.getFont().deriveFont(Font.BOLD, 14.0F));
         this.homeDatasetStatus.setAlignmentX(0.5F);
         this.homeDatasetDetail.setHorizontalAlignment(SwingConstants.CENTER);
         this.homeDatasetDetail.setForeground(MUTED);
         this.homeDatasetDetail.setFont(this.homeDatasetDetail.getFont().deriveFont(9.5F));
         this.homeDatasetDetail.setAlignmentX(0.5F);
         dataCenter.add(Box.createVerticalGlue());
         dataCenter.add(this.homeDatasetStatus);
         dataCenter.add(Box.createVerticalStrut(5));
         dataCenter.add(this.homeDatasetDetail);
         dataCenter.add(Box.createVerticalGlue());
         data.add(dataCenter, BorderLayout.CENTER);
         JPanel dataButtons = new JPanel(new GridLayout(1,3,7,0));
         dataButtons.setOpaque(false);
         JButton dta = this.refButton("打开 DTA", true);
         dta.addActionListener(e -> this.chooseAndLoadDta());
         JButton excel = this.refButton("导入 Excel/CSV", false);
         excel.addActionListener(e -> this.navigateTo("data", "导入与转换", "hxconvert"));
         JButton auto = this.refButton("auto 示例", false);
         auto.addActionListener(e -> this.runUtility("sysuse auto, clear", true));
         dataButtons.add(dta); dataButtons.add(excel); dataButtons.add(auto);
         data.add(dataButtons, BorderLayout.SOUTH);
         gc.gridx = 1;
         gc.weightx = 0.28;
         gc.insets = new Insets(0,0,0,0);
         topRow.add(data, gc);
         body.add(topRow);
         body.add(Box.createVerticalStrut(14));

         JPanel middleRow = new JPanel(new GridBagLayout());
         middleRow.setOpaque(false);
         middleRow.setAlignmentX(0.0F);
         middleRow.setMaximumSize(new Dimension(Integer.MAX_VALUE, 305));
         GridBagConstraints gm = new GridBagConstraints();
         gm.gridy = 0; gm.fill = GridBagConstraints.BOTH; gm.weighty = 1.0;
         JPanel common = this.refCard();
         common.setLayout(new BorderLayout(0,10));
         JLabel commonTitle = new JLabel("常用任务");
         commonTitle.setForeground(TEXT);
         commonTitle.setFont(commonTitle.getFont().deriveFont(Font.BOLD, 14.0F));
         common.add(commonTitle, BorderLayout.NORTH);
         JPanel taskGrid = new JPanel(new GridLayout(2,3,12,12));
         taskGrid.setOpaque(false);
         taskGrid.add(this.refTask("", "导入数据", "Excel / CSV / DTA", new Color(33,176,93), () -> this.navigateTo("data", "导入与转换", "hxconvert")));
         taskGrid.add(this.refTask("", "描述统计", "summarize / tabstat", new Color(57,125,242), () -> this.browseMethod("stats", "描述统计")));
         taskGrid.add(this.refTask("", "基准回归", "xtreg / reghdfe / regress", new Color(142,91,230), this::openBaselineRegressionWorkspace));
         taskGrid.add(this.refTask("", "固定效应", "areg / reghdfe / xtreg", new Color(245,138,45), () -> this.browseMethod("reg", "固定效应线性回归")));
         taskGrid.add(this.refTask("", "双重差分", "didregress / xtdidregress", new Color(31,180,151), () -> this.browseMethod("reg", "双重差分")));
         taskGrid.add(this.refTask("", "OneClick", "控制变量组合", new Color(57,120,244), () -> this.browseMethodCategory("oneclick")));
         common.add(taskGrid, BorderLayout.CENTER);
         gm.gridx = 0; gm.weightx = 0.72; gm.insets = new Insets(0,0,0,12);
         middleRow.add(common, gm);

         JPanel recent = this.refCard();
         recent.setLayout(new BorderLayout(0,8));
         JLabel recentTitle = new JLabel("最近任务");
         recentTitle.setForeground(TEXT);
         recentTitle.setFont(recentTitle.getFont().deriveFont(Font.BOLD,14.0F));
         recent.add(recentTitle, BorderLayout.NORTH);
         this.homeRecentPanel.setOpaque(false);
         this.homeRecentPanel.setLayout(new BoxLayout(this.homeRecentPanel, BoxLayout.Y_AXIS));
         recent.add(this.homeRecentPanel, BorderLayout.CENTER);
         JButton resume = this.refButton("继续上次工作", false);
         resume.addActionListener(e -> { List<WorkSnapshot> snaps=this.loadRecentSnapshots(); if(!snaps.isEmpty()) this.restoreWorkSnapshot(snaps.get(0)); });
         recent.add(resume, BorderLayout.SOUTH);
         gm.gridx = 1; gm.weightx = 0.28; gm.insets = new Insets(0,0,0,0);
         middleRow.add(recent, gm);
         body.add(middleRow);
         body.add(Box.createVerticalStrut(14));

         JPanel more = this.refCard();
         more.setLayout(new BorderLayout(0,10));
         more.setAlignmentX(0.0F);
         more.setMaximumSize(new Dimension(Integer.MAX_VALUE, 250));
         JLabel moreTitle = new JLabel("更多功能");
         moreTitle.setForeground(TEXT);
         moreTitle.setFont(moreTitle.getFont().deriveFont(Font.BOLD,14.0F));
         more.add(moreTitle, BorderLayout.NORTH);
         JPanel moreGrid = new JPanel(new GridLayout(3,3,10,10));
         moreGrid.setOpaque(false);
         moreGrid.add(this.refTask("", "导入与转换", "Excel / CSV / DTA", new Color(87,140,245), () -> this.navigateTo("data", "导入与转换", "hxconvert")));
         moreGrid.add(this.refTask("", "数据检查", "缺失 / 重复 / 唯一键", new Color(37,180,144), () -> this.browseMethod("data", "数据检查")));
         moreGrid.add(this.refTask("", "变量处理", "generate / replace", new Color(229,170,52), () -> this.browseMethod("data", "变量处理")));
         moreGrid.add(this.refTask("", "样本处理", "keep / drop", new Color(159,91,225), () -> this.browseMethod("data", "样本处理")));
         moreGrid.add(this.refTask("", "合并与追加", "merge / append", new Color(87,140,245), () -> this.browseMethod("data", "合并与追加")));
         moreGrid.add(this.refTask("", "数据结构", "reshape / xtset / tsset", new Color(37,180,144), () -> this.browseMethod("data", "数据结构")));
         moreGrid.add(this.refTask("", "相关分析", "correlate / pwcorr", new Color(57,125,242), () -> this.browseMethod("stats", "相关分析")));
         moreGrid.add(this.refTask("", "均值检验", "ttest", new Color(245,138,45), () -> this.browseMethod("stats", "均值检验")));
         moreGrid.add(this.refTask("", "频数列联", "tabulate", new Color(142,91,230), () -> this.browseMethod("stats", "频数列联")));
         more.add(moreGrid, BorderLayout.CENTER);
         body.add(more);

         JScrollPane scroll = softScroll(body);
         scroll.setBorder(null);
         scroll.getVerticalScrollBar().setUnitIncrement(18);
         root.add(scroll, BorderLayout.CENTER);
         return root;
      }

      private JButton homeLauncherButton(String var1, String var2, Runnable var3, boolean var4) {
         JButton var5 = new JButton(
            "<html><div style='text-align:left'><b>" + html(var1) + "</b><br><span style='font-size:9px;color:#637083'>" + html(var2) + "</span></div></html>"
         );
         Color var6 = SURFACE;
         Color var7 = var4 ? new Color(244, 248, 255) : new Color(249, 251, 253);
         Color var8 = var4 ? new Color(233, 241, 253) : new Color(241, 246, 249);
         var5.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(var6, var7, var8, TEXT, new Color(220, 227, 237)));
         var5.setBorder(new EmptyBorder(13, 14, 13, 14));
         var5.setHorizontalAlignment(SwingConstants.LEFT);
         var5.setVerticalAlignment(SwingConstants.TOP);
         var5.setPreferredSize(new Dimension(200, 78));
         var5.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         var5.setFocusPainted(false);
         var5.setContentAreaFilled(false);
         var5.addActionListener(var1x -> var3.run());
         return var5;
      }

      private static JPanel cardPanel() {
         JPanel var0 = new JPanel();
         var0.setBackground(SURFACE);
         var0.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(BORDER, 10), new EmptyBorder(14, 16, 14, 16)));
         return var0;
      }

      private static JLabel sectionTitle(String var0) {
         JLabel var1 = new JLabel(var0);
         var1.setForeground(TEXT);
         var1.setFont(var1.getFont().deriveFont(1, 13.0F));
         return var1;
      }

      private JButton secondary(String var1) {
         JButton var2 = new JButton(var1);
         styleSecondaryButton(var2);
         return var2;
      }

      private void addHomeSection(JPanel var1, String var2, String[][] var3, boolean var4) {
         JPanel var5 = new JPanel(new BorderLayout(20, 0));
         var5.setOpaque(false);
         var5.setAlignmentX(0.0F);
         var5.setBorder(BorderFactory.createCompoundBorder(BorderFactory.createMatteBorder(1, 0, 0, 0, BORDER), new EmptyBorder(14, 0, 14, 0)));
         JLabel var6 = new JLabel(var2);
         var6.setForeground(var4 ? ACCENT : TEXT);
         var6.setFont(var6.getFont().deriveFont(1, 13.0F));
         var6.setPreferredSize(new Dimension(128, 58));
         var6.setVerticalAlignment(1);
         var5.add(var6, "West");
         JPanel var7 = new JPanel(new GridLayout(1, var3.length, 10, 0));
         var7.setOpaque(false);

         for (String[] var11 : var3) {
            JButton var12 = this.homeTaskButton(var11[0], var11[1], var4);
            var12.addActionListener(var2x -> this.openHomeTask(var11[2], var11[3]));
            var7.add(var12);
         }

         var5.add(var7, "Center");
         var1.add(var5);
      }

      private JButton homeTaskButton(String var1, String var2, boolean var3) {
         JButton var4 = new JButton(
            "<html><div style='text-align:left'><b>" + html(var1) + "</b><br><span style='font-size:9px;color:#637083'>" + html(var2) + "</span></div></html>"
         );
         Color var5 = var3 ? ACCENT_SOFT : SURFACE;
         Color var6 = var3 ? new Color(220, 233, 251) : new Color(248, 250, 253);
         Color var7 = var3 ? new Color(207, 224, 247) : new Color(239, 243, 248);
         Color var8 = var3 ? ACCENT : TEXT;
         var4.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(var5, var6, var7, var8, BORDER));
         var4.setBorder(new EmptyBorder(10, 13, 10, 13));
         var4.setHorizontalAlignment(2);
         var4.setVerticalAlignment(0);
         var4.setPreferredSize(new Dimension(170, 62));
         var4.setCursor(Cursor.getPredefinedCursor(12));
         var4.setFocusPainted(false);
         var4.setContentAreaFilled(false);
         return var4;
      }

      private void openHomeTask(String var1, String var2) {
         if ("special".equals(var1)) {
            this.activeCategoryCode = var2;
            this.activeCategoryName = "test".equals(var2) ? "测试数据" : "性能设置";
            this.activeMethodName = this.activeCategoryName;
            this.chooserReady = false;
            this.showWorkspacePage();
            this.showSpecialPage(var2);
         } else if ("category".equals(var1)) {
            this.browseCommandCategory(var2, "favorites".equals(var2) ? "常用命令" : "最近使用");
         } else if ("methodcategory".equals(var1)) {
            this.browseMethodCategory(var2);
         } else {
            this.browseMethod(var1, var2);
         }
      }

      private void smartHomeSearch() {
         String var1 = this.searchField.getText().trim();
         if (var1.isBlank()) {
            JOptionPane.showMessageDialog(this, "输入一个命令名或分析关键词，例如“固定效应”或“缺失值”。", "请输入搜索内容", 1);
         } else {
            String var2 = var1.toLowerCase(Locale.ROOT).replaceAll("\\s+", "");
            if (containsAny(var2, "基准回归", "普通回归", "ols", "普通线性", "线性回归")) {
               this.openBaselineRegressionWorkspace();
               this.statusLabel.setText("已按“" + var1 + "”打开基准回归工作区。");
            } else if (!containsAny(var2, "固定效应", "双向固定", "企业年份", "企业和年份", "reghdfe", "areg")
               && (!var2.contains("企业") || !var2.contains("年份") || !var2.contains("控制") && !var2.contains("效应"))) {
               if (containsAny(var2, "缺失", "missing", "misstable")) {
                  this.navigateTo("data", "数据检查", "缺失值分析");
               } else if (containsAny(var2, "相关", "pwcorr", "correlate", "相关系数")) {
                  this.browseMethod("stats", "相关分析");
               } else if (containsAny(var2, "异方差", "vif", "多重共线", "共线性", "遗漏变量", "reset", "cook", "杠杆", "残差诊断", "回归诊断")) {
                  this.showCommand("regress");
                  this.selectResultView("regresspost", true);
                  this.statusLabel.setText("这些诊断属于普通线性回归的后估计工具；请先运行 regress，再点击右侧诊断。");
               } else if (containsAny(var2, "平行趋势", "事件研究", "eventstudy", "did", "双重差分")) {
                  this.browseMethod("reg", "双重差分");
               } else if (!containsAny(var2, "oneclick", "控制变量组合", "组合稳健", "规格稳健", "稳健性组合", "控制变量怎么加", "结果稳不稳")
                  && (!var2.contains("控制变量") || !var2.contains("稳") && !var2.contains("组合") && !var2.contains("敏感"))) {
                  if (containsAny(var2, "导入", "excel", "csv", "转换dta", "转dta", "数据转换")) {
                     this.navigateTo("data", "导入与转换", "hxconvert");
                  } else if (containsAny(var2, "面板回归", "xtreg", "随机效应", "面板固定")) {
                     this.browseMethod("reg", "面板模型");
                  } else if (containsAny(var2, "工具变量", "2sls", "内生性", "ivregress", "ivreghdfe")) {
                     this.browseMethod("reg", "工具变量");
                  } else if (containsAny(var2, "描述统计", "均值标准差", "summarize", "tabstat")) {
                     this.browseMethod("stats", "描述统计");
                  } else {
                     this.searchCommands();
                  }
               } else {
                  this.browseMethodCategory("oneclick");
               }
            } else {
               this.browseMethod("reg", "固定效应线性回归");
               this.statusLabel.setText("已找到固定效应相关方法。");
            }
         }
      }

      private static boolean containsAny(String var0, String... var1) {
         for (String var5 : var1) {
            if (var0.contains(var5.toLowerCase(Locale.ROOT).replaceAll("\\s+", ""))) {
               return true;
            }
         }

         return false;
      }

      private void refreshHomeContext() {
         long var1 = this.previewMode ? 0L : Data.getObsTotal();
         int var3 = this.previewMode ? 0 : Data.getVarCount();
         if (var1 > 0L && var3 > 0) {
            this.homeDatasetStatus.setText(var1 + " 行 × " + var3 + " 变量");
            this.homeDatasetDetail.setText("当前 Stata 内存数据 · 点击任务即可直接使用");
         } else {
            this.homeDatasetStatus.setText("尚未载入数据");
            this.homeDatasetDetail.setText("可打开 DTA、导入 Excel/CSV，或载入 auto 示例");
         }

         this.rebuildHomeRecentPanel();
      }

      private void rebuildHomeRecentPanel() {
         this.homeRecentPanel.removeAll();
         List<HxWorkbench.WorkbenchFrame.WorkSnapshot> var1 = this.loadRecentSnapshots();
         if (this.previewMode && var1.isEmpty()) {
            HxWorkbench.WorkbenchFrame.WorkSnapshot a = new HxWorkbench.WorkbenchFrame.WorkSnapshot();
            a.command = "reghdfe"; a.label = "固定效应回归分析"; a.depvar = "ROA"; a.x = "TPU"; a.method = "基准回归";
            HxWorkbench.WorkbenchFrame.WorkSnapshot b = new HxWorkbench.WorkbenchFrame.WorkSnapshot();
            b.command = "xtdidregress"; b.label = "双重差分分析"; b.depvar = "y"; b.x = "treat"; b.method = "双重差分";
            var1 = Arrays.asList(a, b);
         }
         if (var1.isEmpty()) {
            JLabel empty = new JLabel("<html><span style='color:#637083'>运行一次分析后，这里会保存最近 3 个设置。<br>点击即可恢复参数，不会自动运行。</span></html>");
            empty.setAlignmentX(0.0F);
            this.homeRecentPanel.add(empty);
         } else {
            for (HxWorkbench.WorkbenchFrame.WorkSnapshot item : var1) {
               String title = item.label.isBlank() ? item.command : item.label;
               String detail = item.depvar.isBlank() && item.x.isBlank() ? item.command : (item.depvar.isBlank() ? "" : "Y=" + item.depvar) + (item.x.isBlank() ? "" : " · X=" + item.x);
               JButton button = new JButton("<html><div style='text-align:left'><b>" + html(title) + "</b><br><span style='font-size:9px;color:#637083'>" + html(detail) + "</span></div></html>");
               button.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 250, 253), new Color(239, 244, 250), TEXT, new Color(229, 233, 239)));
               button.setBorder(new EmptyBorder(8, 10, 8, 10));
               button.setHorizontalAlignment(SwingConstants.LEFT);
               button.setMaximumSize(new Dimension(Integer.MAX_VALUE, 52));
               button.setAlignmentX(0.0F);
               button.setFocusPainted(false);
               button.setContentAreaFilled(false);
               button.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
               button.addActionListener(e -> this.restoreWorkSnapshot(item));
               this.homeRecentPanel.add(button);
               this.homeRecentPanel.add(Box.createVerticalStrut(5));
            }
         }
         this.homeRecentPanel.revalidate();
         this.homeRecentPanel.repaint();
      }

      private void rememberCurrentWork() {
         if (!this.previewMode && this.currentCommand != null && !this.currentCommand.isBlank()) {
            HxWorkbench.WorkbenchFrame.WorkSnapshot var1 = this.captureWorkSnapshot();
            if (var1 != null) {
               List<HxWorkbench.WorkbenchFrame.WorkSnapshot> var2 = this.loadRecentSnapshots();
               ArrayList<HxWorkbench.WorkbenchFrame.WorkSnapshot> var3 = new ArrayList<>();
               var3.add(var1);

               for (HxWorkbench.WorkbenchFrame.WorkSnapshot var5 : var2) {
                  if (var3.size() >= 3) {
                     break;
                  }

                  if (!snapshotSignature(var5).equals(snapshotSignature(var1))) {
                     var3.add(var5);
                  }
               }

               this.saveRecentSnapshots(var3);
               this.rebuildHomeRecentPanel();
            }
         }
      }

      private HxWorkbench.WorkbenchFrame.WorkSnapshot captureWorkSnapshot() {
         HxWorkbench.WorkbenchFrame.WorkSnapshot var1 = new HxWorkbench.WorkbenchFrame.WorkSnapshot();
         var1.command = this.currentCommand;
         var1.category = this.activeCategoryCode;
         var1.method = this.activeMethodName;
         HxWorkbench.WorkbenchFrame.CommandGuide var2 = COMMAND_GUIDES.get(this.currentCommand);
         var1.label = var2 == null ? this.currentCommand : var2.title;
         if (this.baselineTaskActive) {
            var1.label = "基准回归 · " + this.currentCommand;
            var1.depvar = selected(this.depvar);
            var1.x = selected(this.regressX);
            var1.controls = String.join(" ", this.regressControls.getSelectedValuesList());
            var1.extraTerms = this.joinSpecialTerms("|");
            var1.vce = selected(this.vce);
            var1.cluster = selected(this.cluster);
            var1.ifcond = this.ifCondition.getText().trim();
            var1.incond = this.inCondition.getText().trim();
            var1.options = this.regressAdvancedOptions.getText().trim();
            var1.weightType = selected(this.regressWeightType);
            var1.weightVar = selected(this.regressWeightVar);
            var1.flags = "baseline=1;xtmodel=" + selected(this.baselineXtModel) + ";absorb=" + String.join(",", this.absorb.getSelectedValuesList())
               + ";" + (this.regressNoConstant.isSelected() ? "noconstant;" : "")
               + (this.regressBeta.isSelected() ? "beta;" : "") + "level=" + this.regressLevel.getValue();
         } else if ("regress".equals(this.currentCommand) && this.regressWorkspaceActive) {
            var1.depvar = selected(this.depvar);
            var1.x = selected(this.regressX);
            var1.controls = String.join(" ", this.regressControls.getSelectedValuesList());
            var1.extraTerms = this.joinSpecialTerms("|");
            var1.vce = selected(this.vce);
            var1.cluster = selected(this.cluster);
            var1.ifcond = this.ifCondition.getText().trim();
            var1.incond = this.inCondition.getText().trim();
            var1.options = this.regressAdvancedOptions.getText().trim();
            var1.weightType = selected(this.regressWeightType);
            var1.weightVar = selected(this.regressWeightVar);
            var1.flags = (this.regressNoConstant.isSelected() ? "noconstant " : "")
               + (this.regressBeta.isSelected() ? "beta " : "")
               + "level="
               + this.regressLevel.getValue();
         } else if (this.currentCommand.startsWith("oneclick")) {
            var1.oneY = selected(this.oneClickY);
            var1.oneX = selected(this.oneClickX);
            var1.oneRequired = String.join(" ", this.oneClickRequired.getSelectedValuesList());
            var1.oneCandidates = String.join(" ", this.oneClickCandidates.getSelectedValuesList());
            var1.oneEstimator = selected(this.oneClickEstimator);
            var1.oneAbsorb = String.join(" ", this.oneClickAbsorb.getSelectedValuesList());
            var1.oneVce = selected(this.oneClickVce);
            var1.oneCluster = selected(this.oneClickCluster);
         } else if ("did_builder".equals(this.currentCommand)) {
            var1.didAction = selected(this.didAction);
            var1.depvar = selected(this.depvar);
            var1.controls = String.join(" ", this.variables.getSelectedValuesList());
            var1.didUnit = selected(this.didUnit);
            var1.didTime = selected(this.didTime);
            var1.didTreat = selected(this.didTreat);
            var1.didPost = selected(this.didPost);
            var1.didEvent = selected(this.didEvent);
            var1.didEventCode = selected(this.didEventCode);
            var1.didPolicyTime = this.didPolicyTime.getText().trim();
            var1.didBase = String.valueOf(this.didBasePeriod.getValue());
         } else {
            var1.depvar = selected(this.depvar);
            var1.controls = String.join(" ", this.variables.getSelectedValuesList());
            var1.vce = selected(this.vce);
            var1.cluster = selected(this.cluster);
            var1.ifcond = this.ifCondition.getText().trim();
            var1.incond = this.inCondition.getText().trim();
            var1.options = this.options.getText().trim();
         }

         return var1;
      }

      private void restoreWorkSnapshot(HxWorkbench.WorkbenchFrame.WorkSnapshot var1) {
         if (var1 != null && !var1.command.isBlank()) {
            if ("基准回归".equals(var1.method) || var1.flags.contains("baseline=1")) {
               this.openBaselineRegressionWorkspace();
               this.rebuilding = true;
               this.setComboValue(this.baselineEstimator, var1.command);
               this.setComboValue(this.depvar, var1.depvar);
               this.setComboValue(this.regressX, var1.x);
               setListSelectedValues(this.regressControls, splitWords(var1.controls));
               this.regressSpecialTermsModel.clear();
               for (String term : splitPipeTerms(var1.extraTerms)) this.regressSpecialTermsModel.addElement(term);
               this.setComboValue(this.vce, var1.vce);
               this.setComboValue(this.cluster, var1.cluster);
               this.ifCondition.setText(var1.ifcond);
               this.inCondition.setText(var1.incond);
               this.setComboValue(this.regressWeightType, var1.weightType);
               this.setComboValue(this.regressWeightVar, var1.weightVar);
               this.regressAdvancedOptions.setText(var1.options);
               Matcher xtMatcher = Pattern.compile("xtmodel=([^;]+)").matcher(var1.flags);
               if (xtMatcher.find()) this.setComboValue(this.baselineXtModel, xtMatcher.group(1));
               Matcher absorbMatcher = Pattern.compile("absorb=([^;]*)").matcher(var1.flags);
               if (absorbMatcher.find() && !absorbMatcher.group(1).isBlank()) {
                  setListSelectedValues(this.absorb, Arrays.asList(absorbMatcher.group(1).split(",")));
               }
               this.regressNoConstant.setSelected(var1.flags.contains("noconstant"));
               this.regressBeta.setSelected(var1.flags.contains("beta"));
               Matcher levelMatcher = Pattern.compile("level=([0-9]+)").matcher(var1.flags);
               if (levelMatcher.find()) this.regressLevel.setValue(Integer.parseInt(levelMatcher.group(1)));
               this.rebuilding = false;
               this.switchBaselineEstimator();
            } else if ("regress".equals(var1.command)) {
               this.showCommand("regress");
               this.rebuilding = true;
               this.setComboValue(this.depvar, var1.depvar);
               this.setComboValue(this.regressX, var1.x);
               setListSelectedValues(this.regressControls, splitWords(var1.controls));
               this.regressSpecialTermsModel.clear();

               for (String var3 : splitPipeTerms(var1.extraTerms)) {
                  this.regressSpecialTermsModel.addElement(var3);
               }

               this.setComboValue(this.vce, var1.vce);
               this.setComboValue(this.cluster, var1.cluster);
               this.ifCondition.setText(var1.ifcond);
               this.inCondition.setText(var1.incond);
               this.setComboValue(this.regressWeightType, var1.weightType);
               this.setComboValue(this.regressWeightVar, var1.weightVar);
               this.regressAdvancedOptions.setText(var1.options);
               this.regressNoConstant.setSelected(var1.flags.contains("noconstant"));
               this.regressBeta.setSelected(var1.flags.contains("beta"));
               Matcher var5 = Pattern.compile("level=(\\d+)").matcher(var1.flags);
               if (var5.find()) {
                  this.regressLevel.setValue(Integer.parseInt(var5.group(1)));
               }

               this.rebuilding = false;
               this.updateRegressPreview();
            } else if (var1.command.startsWith("oneclick")) {
               this.browseMethodCategory("oneclick");
               this.openCommandPage(var1.command);
               this.rebuilding = true;
               this.setComboValue(this.oneClickY, var1.oneY);
               this.setComboValue(this.oneClickX, var1.oneX);
               setListSelectedValues(this.oneClickRequired, splitWords(var1.oneRequired));
               setListSelectedValues(this.oneClickCandidates, splitWords(var1.oneCandidates));
               this.setComboValue(this.oneClickEstimator, var1.oneEstimator);
               setListSelectedValues(this.oneClickAbsorb, splitWords(var1.oneAbsorb));
               this.setComboValue(this.oneClickVce, var1.oneVce);
               this.setComboValue(this.oneClickCluster, var1.oneCluster);
               this.rebuilding = false;
               this.updateOneClickPreview();
            } else if ("did_builder".equals(var1.command)) {
               this.browseMethodCategory("did");
               this.openCommandPage("did_builder");
               this.rebuilding = true;
               this.setComboValue(this.didAction, var1.didAction);
               this.setComboValue(this.depvar, var1.depvar);
               setListSelectedValues(this.variables, splitWords(var1.controls));
               this.setComboValue(this.didUnit, var1.didUnit);
               this.setComboValue(this.didTime, var1.didTime);
               this.setComboValue(this.didTreat, var1.didTreat);
               this.setComboValue(this.didPost, var1.didPost);
               this.setComboValue(this.didEvent, var1.didEvent);
               this.setComboValue(this.didEventCode, var1.didEventCode);
               this.didPolicyTime.setText(var1.didPolicyTime);

               try {
                  if (!var1.didBase.isBlank()) {
                     this.didBasePeriod.setValue(Integer.parseInt(var1.didBase));
                  }
               } catch (Exception var4) {
               }

               this.rebuilding = false;
               this.showDidBuilderPage();
            } else {
               if (!var1.category.isBlank() && !var1.method.isBlank()) {
                  this.browseMethod(var1.category, var1.method);
               }

               this.openCommandPage(var1.command);
               this.rebuilding = true;
               this.setComboValue(this.depvar, var1.depvar);
               setListSelectedValues(this.variables, splitWords(var1.controls));
               this.setComboValue(this.vce, var1.vce);
               this.setComboValue(this.cluster, var1.cluster);
               this.ifCondition.setText(var1.ifcond);
               this.inCondition.setText(var1.incond);
               this.options.setText(var1.options);
               this.rebuilding = false;
               this.schedulePreview();
            }

            this.statusLabel.setText("已恢复上次设置；请核对底部 Stata 命令后再运行。");
         }
      }

      private List<HxWorkbench.WorkbenchFrame.WorkSnapshot> loadRecentSnapshots() {
         ArrayList var1 = new ArrayList();

         try {
            int var2 = Math.min(3, PREFS.getInt("recent.count", 0));

            for (int var3 = 0; var3 < var2; var3++) {
               HxWorkbench.WorkbenchFrame.WorkSnapshot var4 = HxWorkbench.WorkbenchFrame.WorkSnapshot.decode(PREFS.get("recent." + var3, ""));
               if (var4 != null && !var4.command.isBlank()) {
                  var1.add(var4);
               }
            }
         } catch (Throwable var5) {
         }

         return var1;
      }

      private void saveRecentSnapshots(List<HxWorkbench.WorkbenchFrame.WorkSnapshot> var1) {
         try {
            int var2 = Math.min(3, var1.size());
            PREFS.putInt("recent.count", var2);

            for (int var3 = 0; var3 < var2; var3++) {
               PREFS.put("recent." + var3, ((HxWorkbench.WorkbenchFrame.WorkSnapshot)var1.get(var3)).encode());
            }

            for (int var5 = var2; var5 < 3; var5++) {
               PREFS.remove("recent." + var5);
            }

            PREFS.flush();
         } catch (Throwable var4) {
         }
      }

      private static String snapshotSignature(HxWorkbench.WorkbenchFrame.WorkSnapshot var0) {
         return var0.command + "|" + var0.depvar + "|" + var0.x + "|" + var0.controls + "|" + var0.extraTerms + "|" + var0.oneCandidates + "|" + var0.didAction;
      }

      private static List<String> splitWords(String var0) {
         return var0 != null && !var0.trim().isEmpty() ? Arrays.asList(var0.trim().split("\\s+")) : Collections.emptyList();
      }

      private static List<String> splitPipeTerms(String var0) {
         return var0 != null && !var0.trim().isEmpty() ? Arrays.asList(var0.split("\\s*\\|\\s*")) : Collections.emptyList();
      }

      private void setComboValue(JComboBox<String> var1, String var2) {
         if (var1 != null && var2 != null && !var2.isBlank()) {
            for (int var3 = 0; var3 < var1.getItemCount(); var3++) {
               String var4 = (String)var1.getItemAt(var3);
               if (var2.equals(var4)) {
                  var1.setSelectedIndex(var3);
                  return;
               }
            }
         }
      }

      private void openRegressWorkspace() {
         this.openBaselineRegressionWorkspace();
      }

      private void browseMethodCategory(String var1) {
         this.browseCategoryOverview(var1);
      }

      private static String statsMethodPreview(String method) {
         switch (method) {
            case "汇总，表格和假设检验": return "summarize · tabstat · tabulate · ttest";
            case "线性模型及相关": return "regress · areg · reghdfe · qreg";
            case "二元结果": return "logit · logistic · probit · cloglog";
            case "序数结果": return "ologit · oprobit";
            case "分类结果": return "mlogit · mprobit · asclogit";
            case "计数结果": return "poisson · nbreg · ppmlhdfe · zinb";
            case "分数结果": return "fracreg · betareg";
            case "广义线性模型": return "glm";
            case "选择模型": return "heckman · heckprobit · heckpoisson";
            case "时间序列": return "arima · newey · prais · dfuller";
            case "多元时间序列": return "var · svar · vec · irf";
            case "空间自回归模型": return "spregress · spivregress · spxtregress";
            case "纵向/面板数据": return "xtreg · xtlogit · xtprobit · xtpoisson";
            case "多层混合效应模型": return "mixed · melogit · meprobit · mepoisson";
            case "生存分析": return "stset · sts · stcox · streg";
            case "流行病学及相关": return "cc · cs · ir";
            case "内生协变量": return "eregress · eprobit · eoprobit · epoisson";
            case "样本选择模型": return "heckman · heckprobit · heckoprobit";
            case "因果推断/处理效应": return "teffects · didregress · xtdidregress";
            case "结构方程模型(SEM)": return "sem · gsem";
            case "潜在类别分析(LCA)": return "gsem";
            case "有限混合模型(FMM)": return "fmm";
            case "项目反应理论(IRT)": return "irt";
            case "多元分析": return "factor · pca · manova · cluster";
            case "调查数据分析": return "svy";
            case "Lasso回归": return "lasso · elasticnet · sqrtlasso";
            case "Meta分析": return "meta";
            case "多重插补": return "mi";
            case "非参数分析": return "npregress · kdensity · lowess · lpoly";
            case "精确统计": return "bitesti · tabi";
            case "重抽样": return "bootstrap · jackknife · permute · simulate";
            case "效能，精度和样品含量": return "power";
            case "贝叶斯分析": return "bayes · bayesmh · bayespredict";
            case "贝叶斯模型平均": return "bma";
            case "工具变量与内生性": return "ivregress · ivreghdfe";
            case "估计后分析": return "test · lincom · predict · margins";
            default: return "查看该分类下的 Stata 命令";
         }
      }

      private static String graphMethodPreview(String method) {
         switch (method) {
            case "二维图(散点图，折线图等)": return "twoway · scatter · line · connected";
            case "条形图": return "graph bar · graph hbar";
            case "点图": return "graph dot · dotplot";
            case "饼图": return "graph pie";
            case "直方图": return "histogram";
            case "箱线图": return "graph box · graph hbox";
            case "等高线图": return "twoway contour";
            case "散点图矩阵": return "graph matrix";
            case "分布图": return "histogram · kdensity";
            case "平滑和密度": return "kdensity · lowess · lpoly";
            case "回归诊断图": return "rvfplot · rvpplot · avplot";
            case "时间序列图": return "tsline";
            case "面板数据折线图": return "xtline";
            case "生存分析图": return "sts graph";
            case "ROC分析": return "roctab · rocfit · roccomp";
            case "多元分析图": return "pca · factor · cluster";
            case "质量控制": return "质量控制相关图形";
            case "更多统计图形": return "marginsplot · 更多统计图形";
            case "图形组合": return "graph combine";
            case "管理图形": return "graph display · graph save · graph export";
            case "更改方案/大小": return "set scheme · graph set";
            default: return "查看该分类下的 Stata 图形命令";
         }
      }

      private static String dataMethodPreview(String method) {
         switch (method) {
            case "导入与转换": return "Excel · CSV · TXT → DTA";
            case "数据检查": return "misstable · duplicates";
            case "变量处理": return "generate · replace · encode · winsor2";
            case "样本处理": return "keep · drop · if · in";
            case "合并与追加": return "merge · append";
            case "数据结构": return "reshape · collapse · xtset · tsset";
            default: return "查看该分类下的 Stata 命令";
         }
      }

      private static String genericMethodPreview(String category, String method) {
         if ("graph".equals(category)) return graphMethodPreview(method);
         if ("data".equals(category)) return dataMethodPreview(method);
         if ("stats".equals(category)) return statsMethodPreview(method);
         return methodSummary(method);
      }

      private JButton groupedMethodRow(String category, String number, String method, String preview, Color accent) {
         JButton row = new JButton(
            "<html><table width='930' cellpadding='0' cellspacing='0'><tr>"
               + "<td width='58'><span style='color:#7b8aa3'>" + html(number) + "</span></td>"
               + "<td width='315'><b>" + html(method) + "</b></td>"
               + "<td><span style='font-family:monospace;color:#65758f'>" + html(preview) + "</span></td>"
               + "<td width='22'><span style='color:#607089'>›</span></td>"
               + "</tr></table></html>"
         );
         row.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 251, 255), new Color(241, 246, 253), TEXT, SURFACE));
         row.setBorder(BorderFactory.createCompoundBorder(BorderFactory.createMatteBorder(1, 0, 0, 0, new Color(232, 237, 244)), new EmptyBorder(2, 10, 2, 10)));
         row.setHorizontalAlignment(SwingConstants.LEFT);
         row.setFocusPainted(false);
         row.setContentAreaFilled(false);
         row.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         row.setMaximumSize(new Dimension(Integer.MAX_VALUE, 34));
         row.setPreferredSize(new Dimension(960, 34));
         row.addActionListener(e -> this.browseMethod(category, method));
         return row;
      }

      private JComponent groupedCategoryBand(String category, String title, String subtitle, Color accent, String[] methods, List<String> available, int groupNo) {
         JPanel group = new JPanel(new BorderLayout());
         group.setBackground(SURFACE);
         group.setBorder(new EmptyBorder(0, 0, 0, 0));
         group.setAlignmentX(0.0F);

         JPanel head = new JPanel(new BorderLayout(12, 0));
         head.setBackground(new Color(249, 251, 254));
         head.setBorder(new EmptyBorder(10, 14, 9, 14));
         JLabel dot = new JLabel("●");
         dot.setForeground(accent);
         dot.setFont(dot.getFont().deriveFont(Font.BOLD, 15.0F));
         head.add(dot, BorderLayout.WEST);
         JPanel text = new JPanel();
         text.setOpaque(false);
         text.setLayout(new BoxLayout(text, BoxLayout.X_AXIS));
         JLabel name = new JLabel(title);
         name.setForeground(TEXT);
         name.setFont(name.getFont().deriveFont(Font.BOLD, 15.0F));
         JLabel desc = new JLabel("   " + subtitle);
         desc.setForeground(MUTED);
         desc.setFont(desc.getFont().deriveFont(10.5F));
         text.add(name);
         text.add(desc);
         head.add(text, BorderLayout.CENTER);
         group.add(head, BorderLayout.NORTH);

         JPanel rows = new JPanel();
         rows.setBackground(SURFACE);
         rows.setLayout(new BoxLayout(rows, BoxLayout.Y_AXIS));
         int itemNo = 1;
         for (String method : methods) {
            if (available.isEmpty() || available.contains(method)) {
               rows.add(this.groupedMethodRow(category, groupNo + "." + itemNo, method, genericMethodPreview(category, method), accent));
               itemNo++;
            }
         }
         group.add(rows, BorderLayout.CENTER);
         group.setMaximumSize(new Dimension(Integer.MAX_VALUE, 46 + Math.max(1, itemNo - 1) * 34));
         return group;
      }

      private JComponent groupedOverviewSearch(String tooltip) {
         JPanel searchLine = new JPanel(new BorderLayout(10, 0));
         searchLine.setOpaque(false);
         searchLine.setBorder(new EmptyBorder(0, 0, 8, 0));
         JTextField find = new JTextField();
         styleTextField(find);
         find.setToolTipText(tooltip);
         find.setPreferredSize(new Dimension(620, 36));
         JButton go = this.refButton("搜索", false);
         ActionListener doSearch = e -> {
            String q = find.getText().trim();
            if (!q.isBlank()) {
               this.searchField.setText(q);
               this.smartHomeSearch();
            }
         };
         find.addActionListener(doSearch);
         go.addActionListener(doSearch);
         searchLine.add(find, BorderLayout.CENTER);
         searchLine.add(go, BorderLayout.EAST);
         searchLine.setMaximumSize(new Dimension(Integer.MAX_VALUE, 48));
         searchLine.setAlignmentX(0.0F);
         return searchLine;
      }

      private void finishGroupedOverview() {
         this.chooserContent.add(Box.createVerticalGlue());
         this.chooserReady = true;
         this.chooserAtCategoryLevel = true;
         this.configureChooserBack();
         this.homeButton.setVisible(true);
         this.homeButton.setEnabled(true);
         this.inspectorToggle.setVisible(false);
         this.chooserContent.revalidate();
         this.chooserContent.repaint();
         this.stageLayout.show(this.stageCards, "chooser");
         this.syncSidebarFromContext();
      }

      private void renderGraphGroupedOverview(List<String> available) {
         this.setChooserBreadcrumb("首页  >  图形");
         this.chooserTitle.setText("图形");
         this.chooserHint.setText("按 Stata 原图形分类浏览；大类只负责视觉分组，小项保持 Stata 的原始顺序与名称。");
         this.chooserContent.removeAll();
         this.chooserContent.add(this.groupedOverviewSearch("搜索图形方法或命令"));

         Object[][] groups = new Object[][]{
            {"基础图形", "二维图、条形图、点图、饼图与常见分布图", new Color(54, 114, 236), new String[]{"二维图(散点图，折线图等)", "条形图", "点图", "饼图", "直方图", "箱线图", "等高线图", "散点图矩阵"}},
            {"分布与平滑", "分布展示、密度估计与平滑关系", new Color(35, 169, 105), new String[]{"分布图", "平滑和密度"}},
            {"模型与诊断", "回归、时间序列、面板、生存与 ROC 图形", new Color(128, 92, 220), new String[]{"回归诊断图", "时间序列图", "面板数据折线图", "生存分析图", "ROC分析"}},
            {"多元与统计图", "多元分析、质量控制及其他统计图形", new Color(235, 151, 39), new String[]{"多元分析图", "质量控制", "更多统计图形"}},
            {"组合与管理", "组合、保存、导出及图形方案设置", new Color(222, 92, 112), new String[]{"图形组合", "管理图形", "更改方案/大小"}}
         };

         int groupNo = 1;
         for (Object[] spec : groups) {
            this.chooserContent.add(this.groupedCategoryBand("graph", (String)spec[0], (String)spec[1], (Color)spec[2], (String[])spec[3], available, groupNo++));
            this.chooserContent.add(Box.createVerticalStrut(10));
         }
         this.finishGroupedOverview();
      }

      private void renderDataGroupedOverview(List<String> available) {
         this.setChooserBreadcrumb("首页  >  数据");
         this.chooserTitle.setText("数据");
         this.chooserHint.setText("按数据处理任务浏览；常用 Stata 命令直接显示在小项右侧。");
         this.chooserContent.removeAll();
         this.chooserContent.add(this.groupedOverviewSearch("搜索数据处理方法或命令"));

         Object[][] groups = new Object[][]{
            {"导入与检查", "先把数据读进来，再检查缺失与重复", new Color(54, 114, 236), new String[]{"导入与转换", "数据检查"}},
            {"变量与样本", "生成变量、清洗变量以及筛选样本", new Color(35, 169, 105), new String[]{"变量处理", "样本处理"}},
            {"合并与结构", "合并数据并设置宽长表、面板与时间结构", new Color(128, 92, 220), new String[]{"合并与追加", "数据结构"}}
         };

         int groupNo = 1;
         for (Object[] spec : groups) {
            this.chooserContent.add(this.groupedCategoryBand("data", (String)spec[0], (String)spec[1], (Color)spec[2], (String[])spec[3], available, groupNo++));
            this.chooserContent.add(Box.createVerticalStrut(10));
         }
         this.finishGroupedOverview();
      }

      private void renderCompactGroupedOverview(String category, String title, List<String> methods) {
         this.setChooserBreadcrumb("首页  >  " + title);
         this.chooserTitle.setText(title);
         this.chooserHint.setText("选择具体方法进入下一步；统一采用列表式导航。");
         this.chooserContent.removeAll();
         this.chooserContent.add(this.groupedOverviewSearch("搜索方法或命令"));
         JPanel section = new JPanel(new BorderLayout());
         section.setBackground(SURFACE);
         section.setAlignmentX(0.0F);
         JLabel head = new JLabel("可用方法");
         head.setForeground(TEXT);
         head.setFont(head.getFont().deriveFont(Font.BOLD, 14.0F));
         head.setBorder(new EmptyBorder(10, 14, 8, 14));
         section.add(head, BorderLayout.NORTH);
         JPanel rows = new JPanel();
         rows.setBackground(SURFACE);
         rows.setLayout(new BoxLayout(rows, BoxLayout.Y_AXIS));
         int i = 1;
         for (String method : methods) {
            rows.add(this.groupedMethodRow(category, Integer.toString(i++), method, genericMethodPreview(category, method), new Color(54, 114, 236)));
         }
         section.add(rows, BorderLayout.CENTER);
         this.chooserContent.add(section);
         this.finishGroupedOverview();
      }

      private JButton statsMethodRow(String number, String method, Color accent) {
         String commands = statsMethodPreview(method);
         JButton row = new JButton(
            "<html><table width='930' cellpadding='0' cellspacing='0'><tr>"
               + "<td width='58'><span style='color:#7b8aa3'>" + html(number) + "</span></td>"
               + "<td width='315'><b>" + html(method) + "</b></td>"
               + "<td><span style='font-family:monospace;color:#65758f'>" + html(commands) + "</span></td>"
               + "<td width='22'><span style='color:#607089'>›</span></td>"
               + "</tr></table></html>"
         );
         row.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 251, 255), new Color(241, 246, 253), TEXT, SURFACE));
         row.setBorder(BorderFactory.createCompoundBorder(BorderFactory.createMatteBorder(1, 0, 0, 0, new Color(232, 237, 244)), new EmptyBorder(2, 10, 2, 10)));
         row.setHorizontalAlignment(SwingConstants.LEFT);
         row.setFocusPainted(false);
         row.setContentAreaFilled(false);
         row.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         row.setMaximumSize(new Dimension(Integer.MAX_VALUE, 34));
         row.setPreferredSize(new Dimension(960, 34));
         row.addActionListener(e -> this.browseMethod("stats", method));
         return row;
      }

      private JComponent statsGroupBand(String title, String subtitle, Color accent, String[] methods, List<String> available, int groupNo) {
         JPanel group = new JPanel(new BorderLayout());
         group.setBackground(SURFACE);
         group.setBorder(new EmptyBorder(0, 0, 0, 0));
         group.setAlignmentX(0.0F);

         JPanel head = new JPanel(new BorderLayout(12, 0));
         head.setBackground(new Color(249, 251, 254));
         head.setBorder(new EmptyBorder(10, 14, 9, 14));
         JLabel dot = new JLabel("●");
         dot.setForeground(accent);
         dot.setFont(dot.getFont().deriveFont(Font.BOLD, 15.0F));
         head.add(dot, BorderLayout.WEST);
         JPanel text = new JPanel();
         text.setOpaque(false);
         text.setLayout(new BoxLayout(text, BoxLayout.X_AXIS));
         JLabel name = new JLabel(title);
         name.setForeground(TEXT);
         name.setFont(name.getFont().deriveFont(Font.BOLD, 15.0F));
         JLabel desc = new JLabel("   " + subtitle);
         desc.setForeground(MUTED);
         desc.setFont(desc.getFont().deriveFont(10.5F));
         text.add(name);
         text.add(desc);
         head.add(text, BorderLayout.CENTER);
         group.add(head, BorderLayout.NORTH);

         JPanel rows = new JPanel();
         rows.setBackground(SURFACE);
         rows.setLayout(new BoxLayout(rows, BoxLayout.Y_AXIS));
         int itemNo = 1;
         for (String method : methods) {
            if (available.isEmpty() || available.contains(method)) {
               rows.add(this.statsMethodRow(groupNo + "." + itemNo, method, accent));
               itemNo++;
            }
         }
         group.add(rows, BorderLayout.CENTER);
         group.setMaximumSize(new Dimension(Integer.MAX_VALUE, 46 + Math.max(1, itemNo - 1) * 34));
         return group;
      }

      private void renderStatsGroupedOverview(List<String> available) {
         this.setChooserBreadcrumb("首页  >  统计");
         this.chooserTitle.setText("统计");
         this.chooserHint.setText("按 Stata 原分类浏览；大类只负责视觉分组，小项保持 Stata 的原始顺序与名称。");
         this.chooserContent.removeAll();

         JPanel searchLine = new JPanel(new BorderLayout(10, 0));
         searchLine.setOpaque(false);
         searchLine.setBorder(new EmptyBorder(0, 0, 8, 0));
         JTextField find = new JTextField();
         styleTextField(find);
         find.setToolTipText("搜索统计方法或命令");
         find.setPreferredSize(new Dimension(620, 36));
         JButton go = this.refButton("搜索", false);
         ActionListener doSearch = e -> {
            String q = find.getText().trim();
            if (!q.isBlank()) {
               this.searchField.setText(q);
               this.smartHomeSearch();
            }
         };
         find.addActionListener(doSearch);
         go.addActionListener(doSearch);
         searchLine.add(find, BorderLayout.CENTER);
         searchLine.add(go, BorderLayout.EAST);
         searchLine.setMaximumSize(new Dimension(Integer.MAX_VALUE, 48));
         searchLine.setAlignmentX(0.0F);
         this.chooserContent.add(searchLine);

         Object[][] groups = new Object[][]{
            {"描述与比较", "汇总、表格和假设检验", new Color(54, 114, 236), new String[]{"汇总，表格和假设检验"}},
            {"回归与模型", "常见结果变量、广义模型与选择模型", new Color(35, 169, 105), new String[]{"线性模型及相关", "二元结果", "序数结果", "分类结果", "计数结果", "分数结果", "广义线性模型", "选择模型"}},
            {"时间与面板数据", "时间序列、空间、纵向与多层数据", new Color(128, 92, 220), new String[]{"时间序列", "多元时间序列", "空间自回归模型", "纵向/面板数据", "多层混合效应模型"}},
            {"进阶与结构", "生存、流行病学、内生性与样本选择", new Color(235, 151, 39), new String[]{"生存分析", "流行病学及相关", "内生协变量", "样本选择模型"}},
            {"因果与结构模型", "处理效应、SEM、潜在类别与多元分析", new Color(222, 92, 112), new String[]{"因果推断/处理效应", "结构方程模型(SEM)", "潜在类别分析(LCA)", "有限混合模型(FMM)", "项目反应理论(IRT)", "多元分析", "调查数据分析"}},
            {"扩展方法", "正则化、插补、重抽样、效能与贝叶斯", new Color(57, 145, 183), new String[]{"Lasso回归", "Meta分析", "多重插补", "非参数分析", "精确统计", "重抽样", "效能，精度和样品含量", "贝叶斯分析", "贝叶斯模型平均"}},
            {"扩展与第三方", "工具变量、内生性与估计后分析", new Color(71, 126, 188), new String[]{"工具变量与内生性", "估计后分析"}}
         };

         int groupNo = 1;
         for (Object[] spec : groups) {
            JComponent band = this.statsGroupBand((String)spec[0], (String)spec[1], (Color)spec[2], (String[])spec[3], available, groupNo++);
            this.chooserContent.add(band);
            this.chooserContent.add(Box.createVerticalStrut(10));
         }
         this.chooserContent.add(Box.createVerticalGlue());
         this.chooserReady = true;
         this.chooserAtCategoryLevel = true;
         this.configureChooserBack();
         this.homeButton.setVisible(true);
         this.homeButton.setEnabled(true);
         this.inspectorToggle.setVisible(false);
         this.chooserContent.revalidate();
         this.chooserContent.repaint();
         this.stageLayout.show(this.stageCards, "chooser");
      }

      private void browseCategoryOverview(String var1) {
         this.activeCategoryCode = var1;
         this.activeCategoryName = categoryLabel(var1);
         this.syncSidebarFromContext();
         this.syncSidebarFromContext();
         this.activeMethodName = "";
         this.selectCategoryCode(var1);
         ArrayList<String> var2 = new ArrayList<>();
         if (this.previewMode) {
            var2.addAll(previewMethodsForCategory(var1));
         } else {
            int var3 = HxWorkbench.StataBridge.execute("quietly hxregistry, category(" + var1 + ")", false);
            if (var3 == 0) {
               var2.addAll(HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_method_view")));
            }
         }

         if ("stats".equals(var1)) {
            this.renderStatsGroupedOverview(var2);
            return;
         }

         if ("graph".equals(var1)) {
            this.renderGraphGroupedOverview(var2);
            return;
         }

         if ("data".equals(var1)) {
            this.renderDataGroupedOverview(var2);
            return;
         }

         this.renderCompactGroupedOverview(var1, this.activeCategoryName, var2);
      }



      private JComponent exactNumberBadge(String number, Color color) {
         JComponent badge=new JComponent(){
            @Override protected void paintComponent(Graphics g0){
               Graphics2D g=(Graphics2D)g0.create(); g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON); int d=Math.min(getWidth(),getHeight())-2; int x=(getWidth()-d)/2; int y=(getHeight()-d)/2; g.setColor(color); g.fillOval(x,y,d,d); g.setColor(Color.WHITE); g.setFont(getFont().deriveFont(Font.BOLD,11.0F)); java.awt.FontMetrics fm=g.getFontMetrics(); int tx=(getWidth()-fm.stringWidth(number))/2; int ty=(getHeight()-fm.getHeight())/2+fm.getAscent(); g.drawString(number,tx,ty); g.dispose();
            }
         }; badge.setPreferredSize(new Dimension(31,31)); badge.setMinimumSize(new Dimension(31,31)); badge.setMaximumSize(new Dimension(31,31)); return badge;
      }

      private JPanel exactLinearStep(String number, String title, String detail, Color color) {
         JPanel row=new JPanel(new BorderLayout(10,0)); row.setOpaque(false);
         JComponent n=this.exactNumberBadge(number,color);
         JPanel text=new JPanel(); text.setOpaque(false); text.setLayout(new BoxLayout(text,BoxLayout.Y_AXIS));
         JLabel a=new JLabel(title); a.setForeground(TEXT); a.setFont(a.getFont().deriveFont(Font.BOLD,11.0F));
         JLabel d=new JLabel("<html><div style='width:145px;color:#718096'>"+html(detail)+"</div></html>"); d.setFont(d.getFont().deriveFont(9.5F));
         text.add(a); text.add(Box.createVerticalStrut(6)); text.add(d); row.add(n,BorderLayout.WEST); row.add(text,BorderLayout.CENTER); return row;
      }

      private JComponent exactLinearMainCard(String glyph, String command, String title, String desc, String example, Color accent) {
         JPanel card = new JPanel(new BorderLayout(12, 6));
         card.setBackground(SURFACE);
         card.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220,228,239),9),
            new EmptyBorder(14,16,14,16)
         ));
         JPanel text = new JPanel();
         text.setOpaque(false);
         text.setLayout(new BoxLayout(text, BoxLayout.Y_AXIS));
         JLabel cmd = new JLabel(command);
         cmd.setForeground(accent);
         cmd.setFont(new Font("Monospaced", Font.BOLD, 12));
         JLabel name = new JLabel(title);
         name.setForeground(TEXT);
         name.setFont(name.getFont().deriveFont(Font.BOLD, 13.0F));
         text.add(cmd);
         text.add(Box.createVerticalStrut(4));
         text.add(name);
         card.add(text, BorderLayout.CENTER);
         JButton enter = this.refButton("进入设置", true);
         enter.addActionListener(e -> this.openCommandPage(command));
         card.add(enter, BorderLayout.EAST);
         card.setPreferredSize(new Dimension(500, 82));
         return card;
      }

      private JComponent exactLinearGroup(String glyph, String title, String[][] entries, Color accent) {
         JPanel card = new JPanel(new BorderLayout(0, 8));
         card.setBackground(SURFACE);
         card.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(225,231,240),8),
            new EmptyBorder(12,12,12,12)
         ));
         JLabel h = new JLabel(title);
         h.setForeground(TEXT);
         h.setFont(h.getFont().deriveFont(Font.BOLD, 11.0F));
         card.add(h, BorderLayout.NORTH);
         JPanel list = new JPanel();
         list.setOpaque(false);
         list.setLayout(new BoxLayout(list, BoxLayout.Y_AXIS));
         for (String[] e : entries) {
            JButton b = new JButton("<html><b>" + html(e[0]) + "</b>&nbsp;&nbsp;<span style='color:#6e7b91'>" + html(e[1]) + "</span></html>");
            b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE,new Color(249,251,254),new Color(242,246,251),TEXT,SURFACE));
            b.setBorder(new EmptyBorder(4,4,4,4));
            b.setHorizontalAlignment(SwingConstants.LEFT);
            b.setFocusPainted(false);
            b.setContentAreaFilled(false);
            b.setMaximumSize(new Dimension(Integer.MAX_VALUE, 30));
            String cmd = e[0];
            b.addActionListener(ev -> this.openCommandPage(cmd));
            list.add(b);
         }
         card.add(list, BorderLayout.CENTER);
         return card;
      }

      private JComponent buildExactLinearContainer() {
         JPanel root = new JPanel(new BorderLayout(0, 12));
         root.setBackground(APP_BG);
         root.setBorder(new EmptyBorder(18, 24, 16, 24));

         JPanel header = new JPanel(new BorderLayout());
         header.setOpaque(false);
         JPanel heading = new JPanel();
         heading.setOpaque(false);
         heading.setLayout(new BoxLayout(heading, BoxLayout.Y_AXIS));
         JLabel crumb = new JLabel("首页 / 回归 / 线性模型");
         crumb.setForeground(new Color(84,107,144));
         crumb.setFont(crumb.getFont().deriveFont(10.5F));
         JLabel title = new JLabel("线性模型");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD,27.0F));
         heading.add(crumb);
         heading.add(Box.createVerticalStrut(5));
         heading.add(title);
         header.add(heading, BorderLayout.WEST);
         JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT,7,0));
         actions.setOpaque(false);
         JButton back=this.refButton("← 上一级",false); back.addActionListener(e->this.showHomePage());
         JButton home=this.refButton("首页",false); home.addActionListener(e->this.showHomePage());
         JButton help=this.refButton("帮助",false); help.addActionListener(e->this.openHelp());
         actions.add(back); actions.add(home); actions.add(help);
         header.add(actions, BorderLayout.EAST);
         root.add(header, BorderLayout.NORTH);

         JPanel body = new JPanel();
         body.setOpaque(false);
         body.setLayout(new BoxLayout(body, BoxLayout.Y_AXIS));

         JPanel search = this.refCard();
         search.setLayout(new BorderLayout(8,0));
         search.setAlignmentX(0.0F);
         JTextField find = new JTextField();
         styleTextField(find);
         find.setToolTipText("搜索命令");
         JButton searchButton = this.refButton("搜索", true);
         ActionListener doSearch = e -> {
            String q = find.getText().trim();
            if (!q.isBlank()) {
               this.searchField.setText(q);
               this.smartHomeSearch();
            }
         };
         find.addActionListener(doSearch);
         searchButton.addActionListener(doSearch);
         search.add(find, BorderLayout.CENTER);
         search.add(searchButton, BorderLayout.EAST);
         search.setMaximumSize(new Dimension(Integer.MAX_VALUE, 62));
         body.add(search);
         body.add(Box.createVerticalStrut(12));

         JPanel commonCard=this.refCard();
         commonCard.setLayout(new BorderLayout(0,10));
         commonCard.setAlignmentX(0.0F);
         JLabel ct=new JLabel("常用命令"); ct.setForeground(TEXT); ct.setFont(ct.getFont().deriveFont(Font.BOLD,14.0F));
         commonCard.add(ct, BorderLayout.NORTH);
         JPanel commonGrid = new JPanel(new GridLayout(2,2,12,12));
         commonGrid.setOpaque(false);
         commonGrid.add(this.exactLinearMainCard("","regress","普通线性回归","","",new Color(54,114,236)));
         commonGrid.add(this.exactLinearMainCard("","areg","单组固定效应","","",new Color(29,164,101)));
         commonGrid.add(this.exactLinearMainCard("","reghdfe","高维固定效应回归","","",new Color(245,125,30)));
         commonGrid.add(this.exactLinearMainCard("","qreg","分位数回归","","",new Color(134,84,225)));
         commonCard.add(commonGrid, BorderLayout.CENTER);
         commonCard.setMaximumSize(new Dimension(Integer.MAX_VALUE, 230));
         body.add(commonCard);
         body.add(Box.createVerticalStrut(12));

         JPanel more=this.refCard();
         more.setLayout(new BorderLayout(0,10));
         more.setAlignmentX(0.0F);
         JLabel mt=new JLabel("更多线性模型"); mt.setForeground(TEXT); mt.setFont(mt.getFont().deriveFont(Font.BOLD,14.0F));
         more.add(mt, BorderLayout.NORTH);
         JPanel groups = new JPanel(new GridLayout(2,2,12,12));
         groups.setOpaque(false);
         groups.add(this.exactLinearGroup("","稳健与异常值处理",new String[][]{{"rreg","稳健回归"},{"cnsreg","约束线性回归"},{"newey","Newey-West"}},new Color(47,104,213)));
         groups.add(this.exactLinearGroup("","加权与广义最小二乘",new String[][]{{"regressw","加权最小二乘"},{"vwls","可变权重"},{"gls","广义最小二乘"},{"prais","Prais-Winsten"}},new Color(37,172,92)));
         groups.add(this.exactLinearGroup("","工具变量与内生性",new String[][]{{"ivregress","工具变量"},{"ivreg","2SLS"},{"ivprobit","IV Probit"},{"control","控制函数"}},new Color(245,128,30)));
         groups.add(this.exactLinearGroup("","其他线性扩展",new String[][]{{"sureg","SUR"},{"seemingly","SUR"},{"seemingly2","SUR 扩展"},{"ml","最大似然"}},new Color(132,85,220)));
         more.add(groups, BorderLayout.CENTER);
         body.add(more);

         JScrollPane scroll = softScroll(body);
         scroll.setBorder(null);
         scroll.getVerticalScrollBar().setUnitIncrement(18);
         root.add(scroll, BorderLayout.CENTER);
         return root;
      }

      private void showExactLinearPage() {
         this.activeCategoryCode="reg"; this.activeCategoryName="回归"; this.activeMethodName="线性模型"; this.chooserReady=false; this.setSidebarActive("reg"); this.inspectorToggle.setVisible(false); this.stageLayout.show(this.stageCards,"linear_exact"); this.statusLabel.setText("数据检查不停歇保障数据质量，仅用于质量评估与诊断。");
      }

      private JPanel buildChooserTipPanel() {
         JPanel right = this.refCard();
         right.setLayout(new BoxLayout(right, BoxLayout.Y_AXIS));
         right.setPreferredSize(new Dimension(190, 0));
         right.setMaximumSize(new Dimension(190, Integer.MAX_VALUE));
         JLabel title = new JLabel("☼  小贴士");
         title.setForeground(new Color(225, 133, 18));
         title.setFont(title.getFont().deriveFont(Font.BOLD, 12.5F));
         title.setAlignmentX(0.0F);
         right.add(title);
         right.add(Box.createVerticalStrut(12));
         JLabel text = new JLabel("<html><div style='width:145px;color:#718096'>命令太多时，先从常用命令开始，再逐步深入。</div></html>");
         text.setFont(text.getFont().deriveFont(10.0F));
         text.setAlignmentX(0.0F);
         right.add(text);
         right.add(Box.createVerticalGlue());
         return right;
      }

      private JComponent buildChooserContainer() {
         JPanel root = new JPanel(new BorderLayout(18, 0));
         root.setBackground(APP_BG);
         root.setBorder(new EmptyBorder(18, 22, 14, 22));

         JPanel center = new JPanel(new BorderLayout(0, 12)); center.setOpaque(false);
         JPanel header = new JPanel(); header.setOpaque(false); header.setLayout(new BoxLayout(header, BoxLayout.Y_AXIS));
         this.chooserBreadcrumbBar.setOpaque(false); this.chooserBreadcrumbBar.setAlignmentX(0.0F); header.add(this.chooserBreadcrumbBar); header.add(Box.createVerticalStrut(8));
         JPanel titleRow = new JPanel(new BorderLayout()); titleRow.setOpaque(false);
         JPanel titles = new JPanel(); titles.setOpaque(false); titles.setLayout(new BoxLayout(titles, BoxLayout.Y_AXIS));
         this.chooserTitle.setForeground(TEXT); this.chooserTitle.setFont(this.chooserTitle.getFont().deriveFont(Font.BOLD, 26.0F)); titles.add(this.chooserTitle); titles.add(Box.createVerticalStrut(5));
         this.chooserHint.setForeground(MUTED); this.chooserHint.setFont(this.chooserHint.getFont().deriveFont(11.0F)); titles.add(this.chooserHint); titleRow.add(titles, BorderLayout.WEST);
         JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT,8,0)); actions.setOpaque(false);
         JButton back = this.refButton("←  返回上一级", false); back.addActionListener(e -> this.showHomePage());
         JButton home = this.refButton("⌂  首页", false); home.addActionListener(e -> this.showHomePage());
         JButton help = this.refButton("?  帮助", false); help.addActionListener(e -> this.openHelp()); actions.add(back); actions.add(home); actions.add(help); titleRow.add(actions, BorderLayout.EAST);
         header.add(titleRow); center.add(header, BorderLayout.NORTH);

         this.chooserContent.setOpaque(false); this.chooserContent.setLayout(new BoxLayout(this.chooserContent, BoxLayout.Y_AXIS));
         JScrollPane scroll = new JScrollPane(this.chooserContent); scroll.setBorder(null); scroll.setOpaque(false); scroll.getViewport().setOpaque(false); scroll.getVerticalScrollBar().setUnitIncrement(18); center.add(scroll, BorderLayout.CENTER);
         root.add(center, BorderLayout.CENTER);
         root.add(this.buildChooserTipPanel(), BorderLayout.EAST);
         return root;
      }

      private void browseMethod(String var1, String var2) {
         if ("reg".equals(var1) && "线性模型".equals(var2)) { this.showExactLinearPage(); return; }
         this.activeCategoryCode = var1;
         this.activeCategoryName = categoryLabel(var1);
         this.syncSidebarFromContext();
         this.syncSidebarFromContext();
         this.activeMethodName = var2;
         this.selectCategoryCode(var1);
         this.setBusy(true, "正在读取“" + var2 + "”…");
         this.rebuilding = true;
         this.commandList.clearSelection();
         this.commandModel.clear();
         if (this.previewMode) {
            for (String var4 : previewCommandsForMethod(var2)) {
               this.commandModel.addElement(var4);
            }
         } else {
            int var6 = HxWorkbench.StataBridge.execute("quietly hxregistry, method(" + HxWorkbench.StataBridge.methodCode(var2) + ")", false);
            if (var6 == 0) {
               for (String var5 : HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_command_view"))) {
                  this.commandModel.addElement(var5);
               }
            }
         }

         this.rebuilding = false;
         this.renderCommandChooser(this.activeCategoryName, var2, Collections.list(this.commandModel.elements()));
         this.setBusy(false, this.commandModel.isEmpty() ? "该方法暂时没有可用命令。" : "请选择具体命令。");
      }

      private void browseCommandCategory(String var1, String var2) {
         this.activeCategoryCode = var1;
         this.activeCategoryName = var2;
         this.activeMethodName = var2;
         this.rebuilding = true;
         this.commandModel.clear();
         if (this.previewMode) {
            for (String var4 : Arrays.asList("regress", "xtreg", "reghdfe", "merge", "summarize", "margins")) {
               this.commandModel.addElement(var4);
            }
         } else {
            int var6 = HxWorkbench.StataBridge.execute("quietly hxregistry, category(" + var1 + ")", false);
            if (var6 == 0) {
               for (String var5 : HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_command_view"))) {
                  this.commandModel.addElement(var5);
               }
            }
         }

         this.rebuilding = false;
         this.renderCommandChooser(var2, "", Collections.list(this.commandModel.elements()));
      }

      private List<String> preferredCommandsForMethod(String method, List<String> commands) {
         ArrayList<String> picks = new ArrayList<>();
         List<String> wanted;
         if ("线性模型及相关".equals(method)) {
            wanted = Arrays.asList("regress", "areg", "reghdfe", "qreg", "correlate");
         } else if ("汇总，表格和假设检验".equals(method)) {
            wanted = Arrays.asList("summarize", "tabstat", "tabulate", "ttest");
         } else if ("二元结果".equals(method)) {
            wanted = Arrays.asList("logit", "logistic", "probit", "cloglog");
         } else if ("序数结果".equals(method)) {
            wanted = Arrays.asList("ologit", "oprobit");
         } else if ("分类结果".equals(method)) {
            wanted = Arrays.asList("mlogit", "mprobit", "asclogit");
         } else if ("计数结果".equals(method)) {
            wanted = Arrays.asList("poisson", "nbreg", "ppmlhdfe", "zip", "zinb");
         } else if ("工具变量与内生性".equals(method)) {
            wanted = Arrays.asList("ivregress", "ivreghdfe");
         } else if ("估计后分析".equals(method)) {
            wanted = Arrays.asList("test", "lincom", "predict", "margins");
         } else if ("分数结果".equals(method)) {
            wanted = Arrays.asList("fracreg", "betareg");
         } else if ("时间序列".equals(method)) {
            wanted = Arrays.asList("arima", "newey", "prais", "dfuller");
         } else if ("纵向/面板数据".equals(method)) {
            wanted = Arrays.asList("xtreg", "xtlogit", "xtprobit", "xtpoisson");
         } else if ("生存分析".equals(method)) {
            wanted = Arrays.asList("stset", "sts", "stcox", "streg");
         } else if ("因果推断/处理效应".equals(method)) {
            wanted = Arrays.asList("teffects", "didregress", "xtdidregress");
         } else {
            wanted = Collections.emptyList();
         }

         for (String cmd : wanted) {
            if (commands.contains(cmd) && !picks.contains(cmd)) picks.add(cmd);
         }
         if (picks.isEmpty()) {
            for (String cmd : commands) {
               picks.add(cmd);
               if (picks.size() >= Math.min(4, commands.size())) break;
            }
         }
         return picks;
      }

      private JComponent chooserMethodLead(String detail) {
         JPanel lead = new JPanel(new BorderLayout(12, 0));
         lead.setBackground(new Color(248, 251, 255));
         lead.setBorder(new EmptyBorder(10, 14, 10, 14));
         lead.setAlignmentX(0.0F);
         JLabel dot = new JLabel("●");
         dot.setForeground(new Color(54, 114, 236));
         dot.setFont(dot.getFont().deriveFont(Font.BOLD, 14.0F));
         lead.add(dot, BorderLayout.WEST);
         JLabel text = new JLabel("<html><b>这一页怎么用</b>&nbsp;&nbsp;<span style='color:#637083'>" + html(detail) + "</span></html>");
         text.setForeground(TEXT);
         text.setFont(text.getFont().deriveFont(10.5F));
         lead.add(text, BorderLayout.CENTER);
         lead.setMaximumSize(new Dimension(Integer.MAX_VALUE, 54));
         return lead;
      }

      private JButton chooserListCommandRow(String command, boolean featured) {
         CommandGuide guide = commandGuide(command);
         String title = guide == null ? command : guide.title;
         String purpose = guide == null ? "进入命令设置页查看参数。" : guide.purpose;
         String example = guide == null ? command : guide.example;
         String source = commandSource(command);
         String body;
         if (featured) {
            body = "<html><table width='960' cellpadding='0' cellspacing='0'><tr>"
               + "<td width='155'><span style='font-family:monospace;font-size:17px;color:#2b63c5'><b>" + html(command) + "</b></span><br>"
               + "<span style='font-size:9px;color:#2b63c5'>" + html(source) + "</span></td>"
               + "<td><span style='font-size:15px'><b>" + html(title) + "</b></span><br>"
               + "<span style='font-size:10px;color:#5e6d82'>" + html(purpose) + "</span><br>"
               + "<span style='font-size:9px;color:#7c8899'>示例：" + html(example) + "</span></td>"
               + "<td width='82' align='right'><span style='font-size:10px;color:#53657d'>进入设置  ›</span></td>"
               + "</tr></table></html>";
         } else {
            body = "<html><table width='960' cellpadding='0' cellspacing='0'><tr>"
               + "<td width='145'><span style='font-family:monospace;font-size:13px;color:#2b63c5'><b>" + html(command) + "</b></span></td>"
               + "<td width='215'><span style='font-size:12px'><b>" + html(title) + "</b></span></td>"
               + "<td><span style='font-size:9px;color:#5e6d82'>" + html(purpose) + "</span></td>"
               + "<td width='84' align='right'><span style='font-size:9px;color:#7c8899'>" + html(source) + "  ›</span></td>"
               + "</tr></table></html>";
         }
         JButton row = new JButton(body);
         row.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 251, 255), new Color(241, 246, 253), TEXT, SURFACE));
         row.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createMatteBorder(1, 0, 0, 0, new Color(232, 237, 244)),
            new EmptyBorder(featured ? 7 : 4, 10, featured ? 7 : 4, 10)
         ));
         row.setHorizontalAlignment(SwingConstants.LEFT);
         row.setFocusPainted(false);
         row.setContentAreaFilled(false);
         row.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         row.setMaximumSize(new Dimension(Integer.MAX_VALUE, featured ? 72 : 38));
         row.setPreferredSize(new Dimension(980, featured ? 72 : 38));
         row.addActionListener(e -> this.openCommandPage(command));
         return row;
      }

      private JComponent chooserListSection(String title, String caption, List<String> commands, boolean featured) {
         JPanel section = this.refCard();
         section.setLayout(new BorderLayout(0, 8));
         section.setAlignmentX(0.0F);
         JPanel head = new JPanel();
         head.setOpaque(false);
         head.setLayout(new BoxLayout(head, BoxLayout.Y_AXIS));
         JLabel name = new JLabel(title);
         name.setForeground(TEXT);
         name.setFont(name.getFont().deriveFont(Font.BOLD, 14.0F));
         JLabel desc = new JLabel(caption);
         desc.setForeground(MUTED);
         desc.setFont(desc.getFont().deriveFont(9.5F));
         head.add(name);
         head.add(Box.createVerticalStrut(2));
         head.add(desc);
         section.add(head, BorderLayout.NORTH);
         JPanel rows = new JPanel();
         rows.setOpaque(false);
         rows.setLayout(new BoxLayout(rows, BoxLayout.Y_AXIS));
         boolean first = true;
         for (String cmd : commands) {
            JButton row = this.chooserListCommandRow(cmd, featured);
            if (first) {
               row.setBorder(new EmptyBorder(featured ? 7 : 4, 10, featured ? 7 : 4, 10));
               first = false;
            }
            rows.add(row);
         }
         section.add(rows, BorderLayout.CENTER);
         return section;
      }

      private void renderCommandChooser(String var1, String var2, List<String> var3) {
         this.setChooserBreadcrumb("首页  /  " + (this.activeCategoryName.isBlank() ? var1 : this.activeCategoryName) + (var2.isBlank() ? "" : "  /  " + var2));
         boolean linear = "reg".equals(this.activeCategoryCode) && ("线性模型".equals(var2) || "线性模型".equals(var1));
         this.chooserTitle.setText(linear ? "线性模型" : (var2.isBlank() ? var1 : var2));
         this.chooserHint.setText(linear ? "先选分析目的，再进入具体命令。常用命令优先展示，其余命令按类别收纳。" : "先看常用命令，再继续浏览完整命令列表。");
         this.chooserContent.removeAll();

         JPanel search = this.refCard(); search.setLayout(new BorderLayout(12,0)); search.setMaximumSize(new Dimension(Integer.MAX_VALUE, 58)); search.setAlignmentX(0.0F);
         JTextField field = new JTextField(); styleTextField(field); field.setToolTipText("搜索命令或分析目的"); field.setPreferredSize(new Dimension(600,38)); search.add(field, BorderLayout.CENTER);
         JPanel filters = new JPanel(new FlowLayout(FlowLayout.RIGHT,6,0)); filters.setOpaque(false); filters.add(this.refButton("全部", true)); filters.add(this.refButton("常用", false)); filters.add(this.refButton("进阶", false)); filters.add(this.refButton("筛选排序", false)); search.add(filters, BorderLayout.EAST);
         this.chooserContent.add(search); this.chooserContent.add(Box.createVerticalStrut(10));

         if (linear) {
            JPanel choose = this.refCard(); choose.setLayout(new FlowLayout(FlowLayout.LEFT,10,2)); choose.setMaximumSize(new Dimension(Integer.MAX_VALUE, 60)); choose.setAlignmentX(0.0F);
            JLabel how = new JLabel("●  怎么选？"); how.setForeground(TEXT); how.setFont(how.getFont().deriveFont(Font.BOLD,14.0F)); choose.add(how);
            choose.add(this.refButton("普通 OLS → regress", false)); choose.add(this.refButton("单组固定效应 → areg", false)); choose.add(this.refButton("多维固定效应 → reghdfe", false)); choose.add(this.refButton("关注分布位置 → qreg", false));
            this.chooserContent.add(choose); this.chooserContent.add(Box.createVerticalStrut(10));

            JPanel common = this.refCard(); common.setLayout(new BorderLayout(0,10)); common.setAlignmentX(0.0F);
            JLabel ct = new JLabel("常用命令"); ct.setForeground(TEXT); ct.setFont(ct.getFont().deriveFont(Font.BOLD,14.0F)); common.add(ct, BorderLayout.NORTH);
            JPanel grid = new JPanel(new GridLayout(2,2,16,12)); grid.setOpaque(false);
            grid.add(this.chooserCommandCard("regress", "普通线性回归", "用 OLS 估计连续因变量与解释变量的线性关系。", "regress y x c1 c2, vce(robust)", new Color(54,114,236)));
            grid.add(this.chooserCommandCard("areg", "单组固定效应", "在回归中吸收一组大量类别固定效应。", "areg y x c, absorb(firm)", new Color(29,164,101)));
            grid.add(this.chooserCommandCard("reghdfe", "高维固定效应回归", "高效吸收多组固定效应并支持聚类标准误。", "reghdfe y x c, absorb(firm year) vce(cluster firm)", new Color(245,125,30)));
            grid.add(this.chooserCommandCard("qreg", "分位数回归", "估计解释变量对条件分布不同分位点的影响。", "qreg y x c, quantile(.5)", new Color(134,84,225)));
            common.add(grid, BorderLayout.CENTER); common.setMaximumSize(new Dimension(Integer.MAX_VALUE, 292)); this.chooserContent.add(common); this.chooserContent.add(Box.createVerticalStrut(10));

            JPanel more = this.refCard(); more.setLayout(new BorderLayout(0,10)); more.setAlignmentX(0.0F); JLabel mt = new JLabel("更多线性模型"); mt.setForeground(TEXT); mt.setFont(mt.getFont().deriveFont(Font.BOLD,14.0F)); more.add(mt, BorderLayout.NORTH);
            JPanel groups = new JPanel(new GridLayout(1,4,12,0)); groups.setOpaque(false);
            groups.add(this.chooserGroup("◈  稳健与异常值处理", new String[][]{{"rreg","稳健回归（M-估计）"},{"cnsreg","截面回归（修正样本选择）"},{"newey","Newey-West 标准误"}}, new Color(47,104,213)));
            groups.add(this.chooserGroup("⚖  加权与广义最小二乘", new String[][]{{"regressw","加权最小二乘"},{"vwls","可变加权最小二乘"},{"gls","广义最小二乘"},{"prais","可行广义最小二乘"}}, new Color(37,172,92)));
            groups.add(this.chooserGroup("⚑  工具变量与内生性", new String[][]{{"ivregress","工具变量回归"},{"ivreg","2SLS 回归"},{"ivprobit","工具变量 Probit"},{"control","控制函数法"}}, new Color(245,128,30)));
            groups.add(this.chooserGroup("▦  其他线性扩展", new String[][]{{"sureg","联立方程回归"},{"seemingly","似不相关回归"},{"seemingly2","似不相关回归（扩展）"},{"ml","最大似然回归"}}, new Color(132,85,220)));
            more.add(groups, BorderLayout.CENTER); more.setMaximumSize(new Dimension(Integer.MAX_VALUE, 205)); this.chooserContent.add(more);
         } else {
            String methodName = var2.isBlank() ? var1 : var2;
            List<String> featured = this.preferredCommandsForMethod(methodName, var3);
            LinkedHashSet<String> restSet = new LinkedHashSet<>(var3);
            restSet.removeAll(featured);
            ArrayList<String> rest = new ArrayList<>(restSet);

            this.chooserContent.add(this.chooserMethodLead(
               "先从常用命令进入；需要完整目录时继续向下浏览。当前方法常见命令：" + statsMethodPreview(methodName)
            ));
            this.chooserContent.add(Box.createVerticalStrut(10));

            if (!featured.isEmpty()) {
               this.chooserContent.add(this.chooserListSection(
                  "常用命令", "优先展示更常用、更容易上手的命令。", featured, true
               ));
               this.chooserContent.add(Box.createVerticalStrut(10));
            }
            if (!rest.isEmpty()) {
               this.chooserContent.add(this.chooserListSection(
                  featured.isEmpty() ? "可用命令" : "全部命令",
                  featured.isEmpty() ? "当前方法下可直接使用的命令。" : "完整保留该方法下的其他 Stata 命令。",
                  rest, false
               ));
            }
         }
         this.chooserContent.add(Box.createVerticalGlue());
         this.chooserContent.revalidate(); this.chooserContent.repaint(); this.chooserReady = true; this.inspectorToggle.setVisible(false); this.stageLayout.show(this.stageCards, "chooser"); this.syncSidebarFromContext();
      }

      private JButton commandChoiceButton(String command, int cols) {
         HxWorkbench.WorkbenchFrame.CommandGuide guide = commandGuide(command);
         String width = cols == 1 ? "760px" : "410px";
         String source = commandSource(command);
         JButton button = new JButton(
            "<html><div style='width:" + width + ";text-align:left'>"
               + "<span style='font-family:monospace;font-size:13px'><b>" + html(command) + "</b></span>"
               + "&nbsp;&nbsp;<span style='font-size:11px'><b>" + html(guide.title) + "</b></span>"
               + "&nbsp;&nbsp;<span style='font-size:9px;color:#2a66be'>[" + html(source) + "]</span>"
               + "<br><span style='font-size:10px;color:#637083'>" + html(guide.purpose) + "</span>"
               + "</div></html>"
         );
         button.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 250, 253), new Color(238, 243, 249), TEXT, BORDER));
         button.setBorder(new EmptyBorder(9, 14, 9, 14));
         button.setHorizontalAlignment(2);
         button.setVerticalAlignment(0);
         button.setPreferredSize(new Dimension(320, 68));
         button.setToolTipText("进入 " + command + " 参数设置");
         button.setCursor(Cursor.getPredefinedCursor(12));
         button.setFocusPainted(false);
         button.setContentAreaFilled(false);
         button.addActionListener(event -> this.openCommandPage(command));
         return button;
      }

      private static String commandSource(String command) {
         if (command == null) return "";
         if (command.startsWith("oneclick") || "hxconvert".equals(command) || "缺失值分析".equals(command)) {
            return "HX Workflow";
         }
         if (Arrays.asList("reghdfe", "winsor2", "ivreghdfe", "ppmlhdfe", "coefplot", "event_plot").contains(command)) {
            return "第三方";
         }
         return "Stata 官方";
      }

      private void handleChooserBack() {
         if (!this.chooserAtCategoryLevel
            && !this.activeCategoryCode.isBlank()
            && !"search".equals(this.activeCategoryCode)
            && !"favorites".equals(this.activeCategoryCode)
            && !"recent".equals(this.activeCategoryCode)) {
            this.browseCategoryOverview(this.activeCategoryCode);
         } else {
            this.showHomePage();
         }
      }

      private void configureChooserBack() {
         this.chooserBackButton.setVisible(true);
         this.chooserBackButton.setText("← 上一级");
         this.chooserBackButton.setToolTipText(this.chooserAtCategoryLevel ? "返回首页" : "返回上一级选择");
         this.chooserHomeButton.setVisible(true);
         this.chooserHomeButton.setToolTipText("返回首页");
      }

      private void selectCategoryCode(String var1) {
         for (int var2 = 0; var2 < this.categoryModel.size(); var2++) {
            if (var1.equals(this.categoryModel.get(var2).code)) {
               this.rebuilding = true;
               this.categoryList.setSelectedIndex(var2);
               this.rebuilding = false;
               return;
            }
         }
      }

      private void showWorkspacePage() {
         this.attachSharedInspectorToWorkspace();
         this.homeButton.setVisible(true);
         this.homeButton.setEnabled(true);
         this.inspectorToggle.setVisible(false);
         this.configureWorkspaceBack();
         this.syncSidebarFromContext();
         this.stageLayout.show(this.stageCards, "workspace");
      }

      private void configureWorkspaceBack() {
         this.changeMethodButton.setText("← 上一级");
         String var1 = this.activeMethodName == null ? "" : this.activeMethodName.trim();
         this.changeMethodButton.setToolTipText(!var1.isBlank() && !var1.equals(this.activeCategoryName) ? "返回当前方法的命令选择页" : "返回上一级选择");
         this.homeButton.setText("首页");
         this.homeButton.setToolTipText("返回首页");
      }

      private void setWorkspaceBreadcrumb(String path) {
         this.renderBreadcrumb(this.breadcrumbBar, path);
      }

      private void setChooserBreadcrumb(String path) {
         this.renderBreadcrumb(this.chooserBreadcrumbBar, path);
      }

      private void renderBreadcrumb(JPanel bar, String path) {
         bar.removeAll();
         ArrayList<String> parts = new ArrayList<>();
         for (String raw : path.split("\\s*[›>/]\\s*")) {
            String part = raw.trim();
            if (!part.isBlank() && !"开始".equals(part) && !"首页".equals(part)) {
               parts.add(part);
            }
         }

         this.addBreadcrumbItem(bar, "首页", this::showHomePage, parts.isEmpty());
         for (int i = 0; i < parts.size(); i++) {
            JLabel sep = new JLabel("  ›  ");
            sep.setForeground(MUTED);
            sep.setFont(sep.getFont().deriveFont(11.0F));
            bar.add(sep);
            Runnable action = null;
            boolean current = i == parts.size() - 1;
            if (!current && i == 0) {
               action = this::openActiveCategoryFromBreadcrumb;
            } else if (!current && i == 1 && this.activeMethodName != null && !this.activeMethodName.isBlank() && !this.activeMethodName.equals(this.activeCategoryName)) {
               action = () -> this.browseMethod(this.activeCategoryCode, this.activeMethodName);
            }
            this.addBreadcrumbItem(bar, parts.get(i), action, current);
         }
         bar.revalidate();
         bar.repaint();
      }

      private void openActiveCategoryFromBreadcrumb() {
         if (this.activeCategoryCode == null || this.activeCategoryCode.isBlank() || "search".equals(this.activeCategoryCode)) {
            this.showHomePage();
         } else if ("favorites".equals(this.activeCategoryCode) || "recent".equals(this.activeCategoryCode)) {
            this.browseCommandCategory(this.activeCategoryCode, this.activeCategoryName);
         } else if ("test".equals(this.activeCategoryCode) || "performance".equals(this.activeCategoryCode)) {
            this.showHomePage();
         } else {
            this.browseCategoryOverview(this.activeCategoryCode);
         }
      }

      private void addBreadcrumbItem(JPanel bar, String text, Runnable action, boolean current) {
         JLabel item = new JLabel(text);
         item.setFont(item.getFont().deriveFont(current ? Font.BOLD : Font.PLAIN, 11.0F));
         item.setForeground(current ? TEXT : ACCENT);
         if (action != null && !current) {
            item.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
            item.setToolTipText("打开“" + text + "”");
            item.addMouseListener(new MouseAdapter() {
               @Override
               public void mouseClicked(MouseEvent event) {
                  action.run();
               }

               @Override
               public void mouseEntered(MouseEvent event) {
                  item.setForeground(ACCENT.darker());
               }

               @Override
               public void mouseExited(MouseEvent event) {
                  item.setForeground(ACCENT);
               }
            });
         }
         bar.add(item);
      }

      private static List<String> previewCommandsForMethod(String var0) {
         if ("汇总，表格和假设检验".equals(var0)) {
            return Arrays.asList("summarize", "tabstat", "tabulate", "table", "ttest", "prtest", "sdtest", "oneway", "anova", "ranksum", "median", "signrank", "signtest");
         }          else if ("线性模型及相关".equals(var0)) {
            return Arrays.asList("regress", "areg", "reghdfe", "cnsreg", "rreg", "qreg", "iqreg", "bsqreg", "vwls", "eivreg", "sureg", "mvreg", "correlate", "pwcorr");
         }          else if ("二元结果".equals(var0)) {
            return Arrays.asList("logit", "logistic", "probit", "hetprobit", "scobit", "cloglog");
         }          else if ("序数结果".equals(var0)) {
            return Arrays.asList("ologit", "oprobit");
         }          else if ("分类结果".equals(var0)) {
            return Arrays.asList("mlogit", "mprobit", "asclogit", "asmprobit");
         }          else if ("计数结果".equals(var0)) {
            return Arrays.asList("poisson", "nbreg", "ppmlhdfe", "zip", "zinb", "tpoisson", "tnbreg");
         }          else if ("分数结果".equals(var0)) {
            return Arrays.asList("fracreg", "betareg");
         }          else if ("广义线性模型".equals(var0)) {
            return Collections.singletonList("glm");
         }          else if ("选择模型".equals(var0)) {
            return Arrays.asList("heckman", "heckprobit", "heckoprobit", "heckpoisson");
         }          else if ("时间序列".equals(var0)) {
            return Arrays.asList("arima", "newey", "prais", "arch", "ucm", "dfuller", "pperron", "corrgram", "pergram");
         }          else if ("多元时间序列".equals(var0)) {
            return Arrays.asList("var", "svar", "vec", "varsoc", "vargranger", "varstable", "irf");
         }          else if ("空间自回归模型".equals(var0)) {
            return Arrays.asList("spregress", "spivregress", "spxtregress");
         }          else if ("纵向/面板数据".equals(var0)) {
            return Arrays.asList("xtreg", "xtlogit", "xtprobit", "xtpoisson", "xtnbreg", "xtgee", "xttobit", "xtcloglog", "xtintreg", "xtoprobit", "xtmlogit", "xtfrontier", "xtabond", "xtdpdsys");
         }          else if ("多层混合效应模型".equals(var0)) {
            return Arrays.asList("mixed", "melogit", "meprobit", "mepoisson", "menbreg", "meologit", "meoprobit", "mestreg", "metobit", "meglm");
         }          else if ("生存分析".equals(var0)) {
            return Arrays.asList("stset", "sts", "stcox", "streg", "stcrreg");
         }          else if ("流行病学及相关".equals(var0)) {
            return Arrays.asList("cc", "cs", "ir");
         }          else if ("内生协变量".equals(var0)) {
            return Arrays.asList("eregress", "eprobit", "eoprobit", "epoisson", "eintreg");
         }          else if ("样本选择模型".equals(var0)) {
            return Arrays.asList("heckman", "heckprobit", "heckoprobit", "heckpoisson");
         }          else if ("因果推断/处理效应".equals(var0)) {
            return Arrays.asList("teffects", "etregress", "etpoisson", "didregress", "xtdidregress");
         }          else if ("结构方程模型(SEM)".equals(var0)) {
            return Arrays.asList("sem", "gsem");
         }          else if ("潜在类别分析(LCA)".equals(var0)) {
            return Collections.singletonList("gsem");
         }          else if ("有限混合模型(FMM)".equals(var0)) {
            return Collections.singletonList("fmm");
         }          else if ("项目反应理论(IRT)".equals(var0)) {
            return Collections.singletonList("irt");
         }          else if ("多元分析".equals(var0)) {
            return Arrays.asList("factor", "pca", "canon", "cca", "manova", "mvreg", "discrim", "cluster");
         }          else if ("调查数据分析".equals(var0)) {
            return Collections.singletonList("svy");
         }          else if ("Lasso回归".equals(var0)) {
            return Arrays.asList("lasso", "elasticnet", "sqrtlasso", "dsregress", "poivregress", "xporegress", "xpoivregress");
         }          else if ("Meta分析".equals(var0)) {
            return Collections.singletonList("meta");
         }          else if ("多重插补".equals(var0)) {
            return Collections.singletonList("mi");
         }          else if ("非参数分析".equals(var0)) {
            return Arrays.asList("ranksum", "median", "signrank", "signtest", "npregress", "kdensity", "lowess", "lpoly");
         }          else if ("精确统计".equals(var0)) {
            return Arrays.asList("bitesti", "tabi");
         }          else if ("重抽样".equals(var0)) {
            return Arrays.asList("bootstrap", "jackknife", "permute", "simulate", "statsby");
         }          else if ("效能，精度和样品含量".equals(var0)) {
            return Collections.singletonList("power");
         }          else if ("贝叶斯分析".equals(var0)) {
            return Arrays.asList("bayes", "bayesmh", "bayespredict", "bayesstats", "bayesgraph");
         }          else if ("贝叶斯模型平均".equals(var0)) {
            return Collections.singletonList("bma");
         }          else if ("工具变量与内生性".equals(var0)) {
            return Arrays.asList("ivregress", "ivreghdfe");
         }          else if ("估计后分析".equals(var0)) {
            return Arrays.asList("test", "lincom", "predict", "margins");
         }          else if ("二维图(散点图，折线图等)".equals(var0)) {
            return Arrays.asList("twoway", "scatter", "line", "connected", "lfit", "qfit", "lowess", "lpoly");
         }          else if ("条形图".equals(var0)) {
            return Collections.singletonList("twoway");
         }          else if ("点图".equals(var0)) {
            return Collections.singletonList("dotplot");
         }          else if ("饼图".equals(var0)) {
            return Collections.singletonList("graph");
         }          else if ("直方图".equals(var0)) {
            return Collections.singletonList("histogram");
         }          else if ("箱线图".equals(var0)) {
            return Collections.singletonList("graph_box");
         }          else if ("等高线图".equals(var0)) {
            return Collections.singletonList("twoway");
         }          else if ("散点图矩阵".equals(var0)) {
            return Collections.singletonList("graph");
         }          else if ("分布图".equals(var0)) {
            return Arrays.asList("histogram", "kdensity");
         }          else if ("平滑和密度".equals(var0)) {
            return Arrays.asList("kdensity", "lowess", "lpoly");
         }          else if ("回归诊断图".equals(var0)) {
            return Arrays.asList("rvfplot", "rvpplot", "avplot", "avplots", "lvr2plot", "cprplot", "acprplot");
         }          else if ("时间序列图".equals(var0)) {
            return Collections.singletonList("tsline");
         }          else if ("面板数据折线图".equals(var0)) {
            return Collections.singletonList("xtline");
         }          else if ("生存分析图".equals(var0)) {
            return Collections.singletonList("sts");
         }          else if ("ROC分析".equals(var0)) {
            return Arrays.asList("roctab", "rocfit", "roccomp", "rocgold", "rocreg");
         }          else if ("多元分析图".equals(var0)) {
            return Arrays.asList("pca", "factor", "cluster");
         }          else if ("质量控制".equals(var0)) {
            return Collections.singletonList("graph");
         }          else if ("更多统计图形".equals(var0)) {
            return Arrays.asList("marginsplot", "coefplot", "event_plot");
         }          else if ("图形组合".equals(var0)) {
            return Collections.singletonList("graph");
         }          else if ("管理图形".equals(var0)) {
            return Collections.singletonList("graph");
         }          else if ("更改方案/大小".equals(var0)) {
            return Collections.singletonList("graph");
         } else if ("导入与转换".equals(var0)) {
            return Collections.singletonList("hxconvert");
         } else if ("数据检查".equals(var0)) {
            return Arrays.asList("misstable", "duplicates");
         } else if ("变量处理".equals(var0)) {
            return Arrays.asList("generate", "replace", "encode", "decode", "destring", "tostring", "winsor2");
         } else if ("样本处理".equals(var0)) {
            return Arrays.asList("keep", "drop");
         } else if ("合并与追加".equals(var0)) {
            return Arrays.asList("merge", "append");
         } else if ("数据结构".equals(var0)) {
            return Arrays.asList("reshape", "collapse", "xtset", "tsset");
         } else if ("描述统计".equals(var0)) {
            return Arrays.asList("summarize", "tabstat");
         } else if ("相关分析".equals(var0)) {
            return Arrays.asList("correlate", "pwcorr");
         } else if ("均值检验".equals(var0)) {
            return Collections.singletonList("ttest");
         } else if ("频数列联".equals(var0)) {
            return Collections.singletonList("tabulate");
         } else if ("线性模型".equals(var0)) {
            return Arrays.asList("regress", "areg", "reghdfe", "qreg");
         } else if ("面板模型".equals(var0)) {
            return Arrays.asList("xtreg", "xtlogit", "xtprobit");
         } else if ("二元结果".equals(var0)) {
            return Arrays.asList("logit", "probit");
         } else if ("线性模型及相关".equals(var0)) {
            return Arrays.asList("regress", "areg", "reghdfe", "qreg", "correlate");
         } else if ("计数结果".equals(var0)) {
            return Arrays.asList("poisson", "nbreg", "ppmlhdfe", "zip", "zinb");
         } else if ("工具变量与内生性".equals(var0)) {
            return Arrays.asList("ivregress", "ivreghdfe");
         } else if ("估计后分析".equals(var0)) {
            return Arrays.asList("test", "lincom", "predict", "margins");
         } else if ("计数模型".equals(var0)) {
            return Arrays.asList("poisson", "nbreg", "ppmlhdfe");
         } else if ("工具变量".equals(var0)) {
            return Arrays.asList("ivregress", "ivreghdfe");
         } else if ("双重差分".equals(var0)) {
            return Arrays.asList("didregress", "xtdidregress");
         } else if ("系数检验".equals(var0)) {
            return Arrays.asList("test", "lincom");
         } else if ("预测边际".equals(var0)) {
            return Arrays.asList("predict", "margins");
         } else if ("数据分布".equals(var0)) {
            return Arrays.asList("histogram", "kdensity", "graph_box");
         } else if ("变量关系".equals(var0)) {
            return Arrays.asList("scatter", "lfit", "twoway");
         } else if ("回归结果".equals(var0)) {
            return Arrays.asList("coefplot", "marginsplot");
         } else if ("DID分步构建".equals(var0)) {
            return Collections.singletonList("did_builder");
         } else if ("平行趋势与动态图".equals(var0)) {
            return Arrays.asList("did_trends", "event_plot");
         } else if ("控制变量组合筛选".equals(var0)) {
            return Collections.singletonList("oneclick");
         } else {
            return "控制变量组合稳健性".equals(var0) ? Collections.singletonList("oneclick_robustness") : Collections.emptyList();
         }
      }

      private static List<String> previewMethodsForCategory(String var0) {
         if ("data".equals(var0)) {
            return Arrays.asList("导入与转换", "数据检查", "变量处理", "样本处理", "合并与追加", "数据结构");
         } else if ("stats".equals(var0)) {
            return Arrays.asList(
               "汇总，表格和假设检验", "线性模型及相关", "二元结果", "序数结果", "分类结果", "计数结果", "分数结果", "广义线性模型", "选择模型",
               "时间序列", "多元时间序列", "空间自回归模型", "纵向/面板数据", "多层混合效应模型", "生存分析", "流行病学及相关", "内生协变量", "样本选择模型",
               "因果推断/处理效应", "结构方程模型(SEM)", "潜在类别分析(LCA)", "有限混合模型(FMM)", "项目反应理论(IRT)", "多元分析", "调查数据分析",
               "Lasso回归", "Meta分析", "多重插补", "非参数分析", "精确统计", "重抽样", "效能，精度和样品含量", "贝叶斯分析", "贝叶斯模型平均", "工具变量与内生性", "估计后分析"
            );
         } else if ("reg".equals(var0)) {
            return Arrays.asList("线性模型", "面板模型", "二元结果", "计数模型", "工具变量", "双重差分");
         } else if ("post".equals(var0)) {
            return Arrays.asList("系数检验", "预测边际");
         } else if ("graph".equals(var0)) {
            return Arrays.asList(
               "二维图(散点图，折线图等)", "条形图", "点图", "饼图", "直方图", "箱线图", "等高线图", "散点图矩阵", "分布图", "平滑和密度",
               "回归诊断图", "时间序列图", "面板数据折线图", "生存分析图", "ROC分析", "多元分析图", "质量控制", "更多统计图形", "图形组合", "管理图形", "更改方案/大小"
            );
         } else if ("did".equals(var0)) {
            return Arrays.asList("DID分步构建", "平行趋势与动态图");
         } else {
            return "oneclick".equals(var0) ? Arrays.asList("控制变量组合筛选", "控制变量组合稳健性") : Collections.emptyList();
         }
      }

      private static String methodSummary(String var0) {
         if ("导入与转换".equals(var0)) {
            return "把外部文件转换为可分析的 Stata 数据";
         } else if ("数据检查".equals(var0)) {
            return "检查缺失、重复和关键键值";
         } else if ("变量处理".equals(var0)) {
            return "生成、修改、缩尾和转换变量类型";
         } else if ("样本处理".equals(var0)) {
            return "按研究条件保留或删除样本";
         } else if ("合并与追加".equals(var0)) {
            return "横向匹配主副表或纵向连接数据";
         } else if ("数据结构".equals(var0)) {
            return "转换宽长格式、汇总或声明面板";
         } else if ("描述统计".equals(var0)) {
            return "查看均值、标准差、分位数和样本量";
         } else if ("相关分析".equals(var0)) {
            return "比较变量相关程度及其显著性";
         } else if ("均值检验".equals(var0)) {
            return "检验单样本或两组均值差异";
         } else if ("频数列联".equals(var0)) {
            return "查看类别频数、比例和交叉关系";
         } else if ("线性模型".equals(var0)) {
            return "OLS、固定效应和分位数回归";
         } else if ("面板模型".equals(var0)) {
            return "固定效应、随机效应和面板二元模型";
         } else if ("二元结果".equals(var0)) {
            return "分析 0/1 结果的发生概率";
         } else if ("计数模型".equals(var0)) {
            return "分析非负计数或含零值的结果";
         } else if ("工具变量".equals(var0)) {
            return "处理解释变量内生性";
         } else if ("双重差分".equals(var0)) {
            return "使用 Stata 官方 didregress / xtdidregress 估计标准 DID";
         } else if ("系数检验".equals(var0)) {
            return "检验系数限制和线性组合";
         } else if ("预测边际".equals(var0)) {
            return "生成预测值并解释边际效应";
         } else if ("数据分布".equals(var0)) {
            return "查看分布形状、尾部和异常值";
         } else if ("变量关系".equals(var0)) {
            return "查看散点、拟合与二维叠加关系";
         } else if ("分组趋势".equals(var0)) {
            return "比较处理组与对照组的时间走势";
         } else if ("回归结果".equals(var0)) {
            return "把系数或边际效应画成论文图形";
         } else if ("DID分步构建".equals(var0)) {
            return "生成变量并完成 DID 或事件研究回归";
         } else if ("平行趋势与动态图".equals(var0)) {
            return "检查政策前趋势并绘制动态效应";
         } else if ("控制变量组合筛选".equals(var0)) {
            return "寻找满足显著性条件的控制变量组合";
         } else {
            return "控制变量组合稳健性".equals(var0) ? "比较大量模型组合与规格曲线" : "查看该方法包含的 Stata 命令";
         }
      }

      private static String methodRecommendation(String var0) {
         if ("描述统计".equals(var0)) {
            return "快速检查变量先用 summarize；论文表格需要自定义统计量或分组时用 tabstat。";
         } else if ("相关分析".equals(var0)) {
            return "论文需要相关系数和显著性时通常用 pwcorr；希望所有系数基于同一完整样本时用 correlate。";
         } else if ("线性模型".equals(var0)) {
            return "普通 OLS 用 regress；一组固定效应用 areg；多组高维固定效应用 reghdfe；关注分布不同位置时用 qreg。";
         } else if ("面板模型".equals(var0)) {
            return "连续结果通常从 xtreg 开始；0/1 结果根据链接函数与个体效应设定选择 xtlogit 或 xtprobit。";
         } else if ("二元结果".equals(var0)) {
            return "Logit 和 Probit 的边际效应通常接近，优先遵循研究传统，并使用 margins 解释概率变化。";
         } else if ("计数模型".equals(var0)) {
            return "计数结果先检查均值和方差；过度离散可比较 nbreg，含多维固定效应和大量零值可考虑 ppmlhdfe。";
         } else if ("工具变量".equals(var0)) {
            return "普通 IV 用 ivregress；同时需要吸收多组高维固定效应时用 ivreghdfe。";
         } else if ("双重差分".equals(var0)) {
            return "重复截面使用 Stata 官方 didregress；面板数据先 xtset，再使用 xtdidregress。";
         } else if ("合并与追加".equals(var0)) {
            return "按键补充变量用 merge；把多个结构相同的文件按行堆叠用 append。";
         } else if ("变量处理".equals(var0)) {
            return "创建新变量用 generate；修改已有变量用 replace；代码列含前导零时谨慎使用 destring。";
         } else if ("预测边际".equals(var0)) {
            return "需要生成逐条预测或残差用 predict；解释平均边际效应和情景差异用 margins。";
         } else if ("系数检验".equals(var0)) {
            return "多项限制的联合显著性用 test；需要某个线性组合的估计值和置信区间用 lincom。";
         } else if ("数据分布".equals(var0)) {
            return "频数结构用 histogram，平滑密度用 kdensity，分组中位数和异常值用箱线图。";
         } else if ("变量关系".equals(var0)) {
            return "原始关系用 scatter，拟合方向用 lfit，需要叠加多个图层时用 twoway。";
         } else if ("DID分步构建".equals(var0)) {
            return "先核对处理组、政策时点和基准期，再按数据准备、回归、检验、图形顺序执行。";
         } else if ("平行趋势与动态图".equals(var0)) {
            return "先用组间趋势图检查原始走势，再用事件研究系数图报告动态效应和政策前估计。";
         } else if ("控制变量组合筛选".equals(var0)) {
            return "候选变量应先由理论确定，组合筛选用于敏感性检查。";
         } else {
            return "控制变量组合稳健性".equals(var0) ? "完整保留全部规格，重点查看系数方向、区间和样本变化。" : "";
         }
      }

      private static HxWorkbench.WorkbenchFrame.CommandGuide commandGuide(String var0) {
         HxWorkbench.WorkbenchFrame.CommandGuide var1 = COMMAND_GUIDES.get(var0);
         if (var1 != null) {
            return var1;
         } else {
            String var2 = commandDescription(var0);
            return new HxWorkbench.WorkbenchFrame.CommandGuide(
               var2, "打开统一参数页面并生成真实 Stata 命令。", "已经知道该命令名称，需要通过界面完成参数设置。", var0, "可在命令页面查看解析到的 Syntax、Options 和 Examples。"
            );
         }
      }

      private void buildCommandPanel() {
         this.formPanel.setBorder(new EmptyBorder(16, 16, 20, 16));
         this.formPanel.setBackground(SURFACE);
         this.formScroll.setBorder(null);
         this.formScroll.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
         this.formScroll.getVerticalScrollBar().setUnitIncrement(16);
         this.commandTitle.setForeground(TEXT);
         this.commandTitle.setFont(this.commandTitle.getFont().deriveFont(1, 16.0F));
         this.breadcrumbBar.setOpaque(false);
         this.breadcrumbBar.setAlignmentX(0.0F);
         this.exampleLabel.setForeground(new Color(55, 67, 84));
         this.exampleLabel.setFont(this.exampleLabel.getFont().deriveFont(0, 11.0F));
         this.insightArea.setRows(10);
         this.insightArea.setForeground(TEXT);
         this.insightArea.setBackground(SURFACE);
         this.syntaxArea.setRows(3);
         this.syntaxArea.setForeground(MUTED);
         this.syntaxArea.setBackground(CODE_BG);
         this.previewArea.setRows(3);
         this.previewArea.setLineWrap(true);
         this.previewArea.setWrapStyleWord(true);
         this.previewArea.setFont(new Font("Monospaced", 1, 13));
         this.previewArea.setForeground(TEXT);
         this.previewArea.setBackground(COMMAND_BG);
         this.previewArea.setBorder(new EmptyBorder(11, 12, 11, 12));
         this.previewArea.getDocument().addDocumentListener(new HxWorkbench.SimpleDocumentListener(() -> {
            if (!this.rebuilding) {
               this.statusLabel.setText("命令预览可以直接修改；运行时以框中内容为准。");
               this.flashCommandPreview();
            }
         }));
         JPanel var1 = new JPanel(new BorderLayout(0, 10));
         var1.setBackground(SURFACE);
         var1.setBorder(new EmptyBorder(14, 14, 14, 14));
         var1.add(softScroll(this.insightArea), "Center");
         JPanel var2 = new JPanel(new BorderLayout(0, 5));
         var2.setOpaque(false);
         var2.add(sectionCaption("解析依据"), "North");
         JScrollPane var3 = softScroll(this.syntaxArea);
         var3.setPreferredSize(new Dimension(100, 76));
         var2.add(var3, "Center");
         var1.add(var2, "South");
         this.commandTabs.addTab("参数设置", this.formScroll);
         this.commandTabs.addTab("方法说明", var1);
         this.commandTabs.setBackground(SURFACE);
         this.commandTabs.setForeground(TEXT);
         this.commandTabs.setBorder(null);

         for (JTextField var5 : Arrays.asList(
            this.newvar,
            this.expression,
            this.usingFile,
            this.ifCondition,
            this.inCondition,
            this.options,
            this.convertInputFile,
            this.convertOutputFile,
            this.convertCellRange,
            this.batchInputFolder,
            this.batchOutputFolder
         )) {
            styleTextField(var5);
         }

         for (JComboBox var10 : Arrays.asList(this.depvar, this.model, this.panel, this.time, this.vce, this.cluster, this.genericWeightType, this.genericWeightVar)) {
            styleCombo(var10);
         }

         styleCombo(this.baselineEstimator);
         styleCombo(this.baselineXtModel);
         this.vce.setRenderer(new HxWorkbench.WorkbenchFrame.VceRenderer());
         styleCombo(this.missingMode);
         styleCombo(this.missingSort);
         styleCombo(this.missingChartType);
         styleCombo(this.convertSheet);
         styleCombo(this.convertDelimiter);
         styleCombo(this.convertEncoding);
         ButtonGroup var9 = new ButtonGroup();
         var9.add(this.missingAllVariables);
         var9.add(this.missingChooseVariables);

         for (AbstractButton var6 : Arrays.asList(
            this.missingAllVariables,
            this.missingChooseVariables,
            this.missingSeparateSummary,
            this.missingOnly,
            this.convertSingleMode,
            this.convertBatchMode,
            this.convertExcelFirstRow,
            this.convertExcelAllString,
            this.convertDelimitedFirstRow,
            this.convertProtectLeadingZeros,
            this.convertLoadAfter,
            this.batchXlsx,
            this.batchCsv,
            this.batchTxt,
            this.batchSkipExisting
         )) {
            var6.setOpaque(false);
            var6.setForeground(TEXT);
         }

         ButtonGroup var12 = new ButtonGroup();
         var12.add(this.convertSingleMode);
         var12.add(this.convertBatchMode);

         for (JList var7 : Arrays.asList(this.variables, this.absorb, this.endog, this.instruments, this.missingVariables, this.missingGroups)) {
            var7.setCellRenderer(new HxWorkbench.WorkbenchFrame.SoftListRenderer());
            var7.setBackground(SURFACE);
            var7.setSelectionBackground(ACCENT_SOFT);
            var7.setSelectionForeground(ACCENT);
         }

         this.summaryArea.setBackground(SURFACE);
         this.summaryArea.setForeground(TEXT);
         this.changeArea.setBackground(SURFACE);
         this.changeArea.setForeground(TEXT);
         this.advancedContent.setOpaque(false);
         this.advancedContent.setLayout(new BoxLayout(this.advancedContent, BoxLayout.Y_AXIS));
         this.advancedContent.setVisible(true);
         this.advancedToggle.setVisible(false);
         styleSecondaryButton(this.copyCommandButton);
      }

      private JComponent buildCommandContainer() {
         JPanel root = new JPanel(new BorderLayout());
         root.setBackground(APP_BG);

         JPanel header = new JPanel(new BorderLayout(10, 8));
         header.setOpaque(false);
         header.setBorder(new EmptyBorder(18, 20, 10, 12));
         JPanel heading = new JPanel();
         heading.setOpaque(false);
         heading.setLayout(new BoxLayout(heading, BoxLayout.Y_AXIS));
         this.breadcrumbBar.setAlignmentX(0.0F);
         this.breadcrumbBar.setMaximumSize(new Dimension(Integer.MAX_VALUE, 22));
         heading.add(this.breadcrumbBar);
         heading.add(Box.createVerticalStrut(7));
         this.commandTitle.setFont(this.commandTitle.getFont().deriveFont(Font.BOLD, 22.0F));
         this.commandTitle.setAlignmentX(0.0F);
         heading.add(this.commandTitle);
         heading.add(Box.createVerticalStrut(5));
         this.exampleLabel.setForeground(MUTED);
         this.exampleLabel.setFont(this.exampleLabel.getFont().deriveFont(10.5F));
         this.exampleLabel.setAlignmentX(0.0F);
         heading.add(this.exampleLabel);
         header.add(heading, BorderLayout.CENTER);

         styleSecondaryButton(this.changeMethodButton);
         styleSecondaryButton(this.homeButton);
         this.homeButton.addActionListener(var1x -> this.showHomePage());
         this.changeMethodButton.addActionListener(var1x -> {
            if (this.chooserReady) {
               this.stageLayout.show(this.stageCards, "chooser");
               this.syncSidebarFromContext();
            } else {
               this.showHomePage();
            }
         });
         JButton help = new JButton("查看帮助");
         styleSecondaryButton(help);
         help.addActionListener(var1x -> this.openHelp());

         this.baselineEstimatorHeader = new JPanel(new FlowLayout(FlowLayout.LEFT, 6, 0));
         this.baselineEstimatorHeader.setOpaque(false);
         JLabel estimatorLabel = new JLabel("估计方法");
         estimatorLabel.setForeground(MUTED);
         estimatorLabel.setFont(estimatorLabel.getFont().deriveFont(Font.BOLD, 10.5F));
         this.baselineEstimator.setPreferredSize(new Dimension(120, 31));
         this.baselineEstimatorSource.setForeground(ACCENT);
         this.baselineEstimatorSource.setFont(this.baselineEstimatorSource.getFont().deriveFont(Font.BOLD, 10.0F));
         this.baselineEstimatorHeader.add(estimatorLabel);
         this.baselineEstimatorHeader.add(this.baselineEstimator);
         this.baselineEstimatorHeader.add(this.baselineEstimatorSource);
         this.baselineEstimatorHeader.setVisible(false);

         JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 7, 0));
         actions.setOpaque(false);
         actions.add(this.baselineEstimatorHeader);
         actions.add(this.changeMethodButton);
         actions.add(this.homeButton);
         actions.add(help);
         header.add(actions, BorderLayout.EAST);
         root.add(header, BorderLayout.NORTH);

         JPanel contentWrap = new JPanel(new BorderLayout());
         contentWrap.setOpaque(false);
         contentWrap.setBorder(new EmptyBorder(0, 18, 10, 8));
         JPanel contentCard = cardPanel();
         contentCard.setLayout(new BorderLayout());
         contentCard.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(216, 224, 235), 11), new EmptyBorder(2, 2, 2, 2)));
         contentCard.add(this.commandTabs, BorderLayout.CENTER);
         contentWrap.add(contentCard, BorderLayout.CENTER);
         root.add(contentWrap, BorderLayout.CENTER);

         this.commandDock = cardPanel();
         this.commandDock.setLayout(new BorderLayout(10, 7));
         this.commandDock.setBackground(SURFACE);
         this.commandDock.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(216, 224, 235), 11), new EmptyBorder(12, 14, 12, 14)));
         this.commandDockTitle.setForeground(TEXT);
         this.commandDockTitle.setFont(this.commandDockTitle.getFont().deriveFont(Font.BOLD, 12.5F));
         this.commandDockHint.setForeground(MUTED);
         this.commandDockHint.setFont(this.commandDockHint.getFont().deriveFont(9.5F));
         this.commandDockStatus.setForeground(MUTED);
         this.commandDockStatus.setFont(this.commandDockStatus.getFont().deriveFont(Font.BOLD, 10.0F));
         JPanel dockHeader = new JPanel(new BorderLayout());
         dockHeader.setOpaque(false);
         JPanel dockTitle = new JPanel();
         dockTitle.setOpaque(false);
         dockTitle.setLayout(new BoxLayout(dockTitle, BoxLayout.Y_AXIS));
         dockTitle.add(this.commandDockTitle);
         dockTitle.add(Box.createVerticalStrut(2));
         dockTitle.add(this.commandDockHint);
         dockHeader.add(dockTitle, BorderLayout.CENTER);
         dockHeader.add(this.commandDockStatus, BorderLayout.EAST);
         this.commandDock.add(dockHeader, BorderLayout.NORTH);
         JScrollPane preview = softScroll(this.previewArea);
         preview.setPreferredSize(new Dimension(100, 70));
         this.commandDock.add(preview, BorderLayout.CENTER);
         JPanel dockActions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 7, 0));
         dockActions.setOpaque(false);
         dockActions.add(this.copyCommandButton);
         dockActions.add(this.runButton);
         this.commandDockProgress.setVisible(false);
         this.commandDockProgress.setStringPainted(true);
         this.commandDockProgress.setPreferredSize(new Dimension(180, 16));
         JPanel dockSouth = new JPanel(new BorderLayout(10, 0));
         dockSouth.setOpaque(false);
         dockSouth.add(this.commandDockProgress, BorderLayout.CENTER);
         dockSouth.add(dockActions, BorderLayout.EAST);
         this.commandDock.add(dockSouth, BorderLayout.SOUTH);
         JPanel dockWrap = new JPanel(new BorderLayout());
         dockWrap.setOpaque(false);
         dockWrap.setBorder(new EmptyBorder(0, 18, 16, 8));
         dockWrap.add(this.commandDock, BorderLayout.CENTER);
         root.add(dockWrap, BorderLayout.SOUTH);
         return root;
      }

      private void buildDataPanel() {
         this.dataTable.setAutoResizeMode(0);
         this.dataTable.setRowHeight(26);
         this.dataTable.setCellSelectionEnabled(true);
         this.dataTable.setSelectionMode(0);
         this.dataTable.setDefaultRenderer(Object.class, new HxWorkbench.WorkbenchFrame.ChangeRenderer());
         this.dataTable.getTableHeader().setReorderingAllowed(false);
         this.dataTable.setFillsViewportHeight(true);
         this.dataTable.setShowVerticalLines(false);
         this.dataTable.setShowHorizontalLines(true);
         this.dataTable.setGridColor(new Color(232, 236, 241));
         this.dataTable.setSelectionBackground(ACCENT_SOFT);
         this.dataTable.setSelectionForeground(TEXT);
         this.dataTable.getTableHeader().setBackground(new Color(247, 249, 252));
         this.dataTable.getTableHeader().setForeground(TEXT);
         this.dataTable.getTableHeader().setFont(this.dataTable.getTableHeader().getFont().deriveFont(1, 11.0F));
         this.dataTable.getTableHeader().setPreferredSize(new Dimension(0, 28));
         this.installDataHeaderDragSupport();
         JScrollPane var1 = softScroll(this.dataTable);
         var1.getVerticalScrollBar().setUnitIncrement(20);
         var1.setColumnHeaderView(this.dataTable.getTableHeader());
         JPanel var2 = new JPanel(new BorderLayout());
         var2.setBackground(SURFACE);
         this.variableTabs = new JTabbedPane();
         this.variableTabs.addTab("变量摘要", softScroll(this.summaryArea));
         this.variableTabs.addTab("分布图", this.histogram);
         this.variableTabs.setBackground(SURFACE);
         this.variableTabs.setMinimumSize(new Dimension(0, 0));
         var1.setMinimumSize(new Dimension(0, 0));
         this.currentDataCards.setBackground(SURFACE);
         this.currentDataCards.setMinimumSize(new Dimension(0, 90));
         this.currentDataCards.add(var1, "table");
         this.currentDataCards.add(this.buildEmptyDataPanel(), "empty");

         this.dataSummarySplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT, this.currentDataCards, this.variableTabs);
         this.dataSummarySplit.setResizeWeight(0.68);
         this.dataSummarySplit.setContinuousLayout(true);
         this.dataSummarySplit.setMinimumSize(new Dimension(0, 0));
         this.dataSummarySplit.setBorder(null);
         this.dataSummarySplit.setDividerSize(5);
         var2.add(this.dataSummarySplit, BorderLayout.CENTER);
         this.dataTabs.addTab("数据", var2);
         SwingUtilities.invokeLater(() -> {
            if (this.dataSummarySplit != null) this.dataSummarySplit.setDividerLocation(0.68);
         });
         JPanel var3 = new JPanel(new BorderLayout(0, 8));
         var3.setBackground(SURFACE);
         JLabel var4 = new JLabel("请从 数据处理 > 数据检查 > 缺失值分析 开始。", 0);
         var4.setForeground(MUTED);
         this.missingResultTabs.addTab("说明", var4);
         var3.add(this.missingResultTabs, "Center");
         this.resultSummaryArea.setText("选择命令并运行后，这里会显示与当前任务有关的结果摘要。\n\n回归命令显示样本数和拟合信息；数据处理显示前后变化；专题工作流显示自己的结果页面。");
         this.resultSummaryArea.setBackground(SURFACE);
         // Stata tables depend on fixed columns. Never word-wrap the raw Results mirror.
         this.resultSummaryArea.setLineWrap(false);
         this.resultSummaryArea.setWrapStyleWord(false);
         this.resultSummaryArea.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 12));
         this.resultCards.setBackground(SURFACE);
         this.resultCards.add(softScroll(this.resultSummaryArea), "general");
         this.resultCards.add(softScroll(this.changeArea), "changes");
         this.resultCards.add(var3, "missing");
         this.resultCards.add(this.buildImportPreviewPanel(), "convert");
         this.resultCards.add(this.graphPreview, "graph");
         this.resultCards.add(this.buildOneClickResultsPanel(), "oneclick");
         this.resultCards.add(this.buildRegressPostPanel(), "regresspost");
         this.resultLayout.show(this.resultCards, "general");
         this.dataTabs.addTab("结果", this.resultCards);
         this.dataTabs.addTab("日志", this.buildRunMonitorPanel());
         this.dataTabs.setBackground(SURFACE);
         this.syncRightPaneTitle();
      }

      private JComponent buildOneClickResultsPanel() {
         this.styleResultTable(this.oneClickExternalTable);
         this.oneClickOverview.setText("运行外部 OneClick 后，这里会读取它生成的 subset.dta，并把结果直接显示出来。\n\nhxempirical 不重新实现 OneClick 算法；底部看到的 oneclick 命令就是实际执行的命令。");
         this.oneClickResultTabs.removeAll();
         this.oneClickResultTabs.addTab("结果概览", softScroll(this.oneClickOverview));
         this.oneClickResultTabs.addTab("外部结果表", softScroll(this.oneClickExternalTable));
         JButton var1 = new JButton("送入普通回归");
         stylePrimaryButton(var1);
         var1.addActionListener(var1x -> this.sendSelectedOneClickToRegression());
         JPanel var2 = new JPanel(new FlowLayout(2));
         var2.setBackground(SURFACE);
         var2.add(var1);
         JPanel var3 = new JPanel(new BorderLayout());
         var3.setBackground(SURFACE);
         var3.add(this.oneClickResultTabs, "Center");
         var3.add(var2, "South");
         return var3;
      }

      private JComponent buildRegressPostPanel() {
         JPanel var1 = new JPanel(new BorderLayout());
         var1.setBackground(SURFACE);
         JPanel var2 = new JPanel();
         var2.setOpaque(false);
         var2.setBorder(new EmptyBorder(14, 16, 16, 16));
         var2.setLayout(new BoxLayout(var2, 1));
         JLabel var3 = new JLabel("普通线性回归：常用下一步");
         var3.setForeground(TEXT);
         var3.setFont(var3.getFont().deriveFont(1, 17.0F));
         var3.setAlignmentX(0.0F);
         var2.add(var3);
         var2.add(Box.createVerticalStrut(5));
         JLabel var4 = new JLabel("这些按钮调用 Stata 官方 regress 后估计命令；完整输出仍保留在 Stata Results。");
         var4.setForeground(MUTED);
         var4.setAlignmentX(0.0F);
         var2.add(var4);
         var2.add(Box.createVerticalStrut(14));
         this.addRegressPostGroup(
            var2, "模型诊断", new String[][]{{"多重共线性 VIF", "vif"}, {"异方差 BP/CW", "hettest"}, {"White 异方差", "white"}, {"RESET 设定检验", "ovtest"}, {"AIC / BIC", "ic"}}
         );
         this.addRegressPostGroup(
            var2,
            "预测与影响诊断",
            new String[][]{
               {"生成拟合值", "fitted"}, {"生成残差", "resid"}, {"标准化残差", "rstandard"}, {"学生化残差", "rstudent"}, {"Cook's D", "cooksd"}, {"杠杆值 leverage", "leverage"}
            }
         );
         this.addRegressPostGroup(var2, "系数检验", new String[][]{{"联合检验 test", "test"}, {"线性组合 lincom", "lincom"}});
         JPanel var5 = new JPanel(new BorderLayout());
         var5.setOpaque(false);
         JLabel var6 = new JLabel(
            "<html><span style='color:#637083'>提示：rstandard、rstudent、Cook's D 和 leverage 适用于默认 OLS VCE。如果正式模型使用 robust/cluster，工具会阻止不适用的影响诊断。</span></html>"
         );
         var5.add(var6, "Center");
         var5.setAlignmentX(0.0F);
         var2.add(var5);
         var1.add(softScroll(var2), "Center");
         return var1;
      }

      private void addRegressPostGroup(JPanel var1, String var2, String[][] var3) {
         JLabel var4 = sectionCaption(var2);
         var4.setAlignmentX(0.0F);
         var1.add(var4);
         JPanel var5 = new JPanel(new GridLayout(0, 2, 8, 8));
         var5.setOpaque(false);

         for (String[] var9 : var3) {
            JButton var10 = this.secondary(var9[0]);
            var10.addActionListener(var2x -> this.runRegressPostAction(var9[1]));
            var5.add(var10);
         }

         var5.setAlignmentX(0.0F);
         var5.setMaximumSize(new Dimension(Integer.MAX_VALUE, (var3.length + 1) / 2 * 42));
         var1.add(var5);
         var1.add(Box.createVerticalStrut(14));
      }

      private void runRegressPostAction(String var1) {
         boolean var3 = false;
         String var2;
         if ("vif".equals(var1)) {
            int var8 = HxWorkbench.StataBridge.execute("quietly hxregpost, status", false);
            if (var8 != 0) {
               JOptionPane.showMessageDialog(this, "请先运行一条普通 regress 回归。", "没有可用的 regress 结果", 1);
               return;
            }

            String var11 = HxWorkbench.StataBridge.characteristic("hxtoolbox_regress_hascons");
            var2 = "0".equals(var11) ? "estat vif, uncentered" : "estat vif";
         } else if ("hettest".equals(var1)) {
            var2 = "estat hettest";
         } else if ("white".equals(var1)) {
            var2 = "estat imtest, white";
         } else if ("ovtest".equals(var1)) {
            var2 = "estat ovtest";
         } else if ("ic".equals(var1)) {
            var2 = "estat ic";
         } else if (!"test".equals(var1) && !"lincom".equals(var1)) {
            String var7;
            String var10;
            if ("fitted".equals(var1)) {
               var7 = "hx_yhat";
               var10 = "xb";
            } else if ("resid".equals(var1)) {
               var7 = "hx_resid";
               var10 = "residuals";
            } else if ("rstandard".equals(var1)) {
               var7 = "hx_rstandard";
               var10 = "rstandard";
            } else if ("rstudent".equals(var1)) {
               var7 = "hx_rstudent";
               var10 = "rstudent";
            } else if ("cooksd".equals(var1)) {
               var7 = "hx_cooksd";
               var10 = "cooksd";
            } else {
               var7 = "hx_leverage";
               var10 = "leverage";
            }

            String var6 = JOptionPane.showInputDialog(this, "新变量名（已有同名变量时 Stata 会提示）：", var7);
            if (var6 == null || var6.trim().isEmpty()) {
               return;
            }

            var2 = "predict " + var6.trim() + ", " + var10;
            var3 = true;
         } else {
            String var4 = "test".equals(var1) ? "输入要检验的系数或限制，例如：x1 x2" : "输入线性组合，例如：x + 1.group#c.x";
            String var5 = JOptionPane.showInputDialog(this, var4, var1 + " 设置", 3);
            if (var5 == null || var5.trim().isEmpty()) {
               return;
            }

            var2 = var1 + " " + var5.trim();
         }

         boolean var9 = var3;
         String var12 = "hxregpost, command(" + HxWorkbench.StataBridge.quote(var2) + ")";
         this.executeMonitoredCommand(var2, var12, var9, var2x -> {
            if (var2x.rc == 0) {
               if (var9) {
                  this.refreshDataset(true);
               }

               this.selectResultView("regresspost", true);
            }
         });
      }

      private void styleResultTable(JTable var1) {
         var1.setAutoResizeMode(0);
         var1.setRowHeight(25);
         var1.setSelectionMode(0);
         var1.setAutoCreateRowSorter(true);
         var1.setShowVerticalLines(false);
         var1.setGridColor(new Color(232, 236, 241));
         var1.getTableHeader().setReorderingAllowed(true);
      }

      private JComponent buildRunMonitorPanel() {
         JPanel var1 = new JPanel(new BorderLayout());
         var1.setBackground(SURFACE);
         JPanel var2 = new JPanel();
         var2.setBackground(SURFACE);
         var2.setBorder(new EmptyBorder(14, 16, 16, 16));
         var2.setLayout(new BoxLayout(var2, 1));
         this.monitorStatus.setForeground(TEXT);
         this.monitorStatus.setFont(this.monitorStatus.getFont().deriveFont(1, 18.0F));
         this.monitorStatus.setAlignmentX(0.0F);
         var2.add(this.monitorStatus);
         var2.add(Box.createVerticalStrut(7));
         this.monitorProgress.setAlignmentX(0.0F);
         this.monitorProgress.setMaximumSize(new Dimension(Integer.MAX_VALUE, 18));
         this.monitorProgress.setStringPainted(true);
         this.monitorProgress.setString("等待执行");
         var2.add(this.monitorProgress);
         var2.add(Box.createVerticalStrut(8));
         this.monitorElapsed.setForeground(MUTED);
         this.monitorElapsed.setAlignmentX(0.0F);
         var2.add(this.monitorElapsed);
         var2.add(Box.createVerticalStrut(12));
         JLabel var3 = sectionCaption("当前命令 / 任务");
         var3.setAlignmentX(0.0F);
         var2.add(var3);
         this.monitorCommand.setRows(3);
         this.monitorCommand.setLineWrap(true);
         this.monitorCommand.setWrapStyleWord(true);
         this.monitorCommand.setFont(new Font("Monospaced", 0, 12));
         this.monitorCommand.setBackground(CODE_BG);
         JScrollPane var4 = softScroll(this.monitorCommand);
         var4.setPreferredSize(new Dimension(100, 82));
         var4.setMaximumSize(new Dimension(Integer.MAX_VALUE, 92));
         var4.setAlignmentX(0.0F);
         var2.add(var4);
         var2.add(Box.createVerticalStrut(12));
         JPanel var5 = new JPanel(new GridLayout(0, 2, 8, 6));
         var5.setOpaque(false);

         for (JLabel var7 : Arrays.asList(
            this.monitorStart, this.monitorEnd, this.monitorDuration, this.monitorReturnCode, this.monitorHistory, this.monitorProcessors
         )) {
            var7.setForeground(TEXT);
            var5.add(var7);
         }

         var5.setAlignmentX(0.0F);
         var5.setMaximumSize(new Dimension(Integer.MAX_VALUE, 78));
         var2.add(var5);
         var2.add(Box.createVerticalStrut(12));
         JLabel var9 = sectionCaption("执行结果摘要");
         var9.setAlignmentX(0.0F);
         var2.add(var9);
         this.monitorOutcome.setRows(6);
         this.monitorOutcome.setBackground(SURFACE);
         JScrollPane var10 = softScroll(this.monitorOutcome);
         var10.setPreferredSize(new Dimension(100, 125));
         var10.setMaximumSize(new Dimension(Integer.MAX_VALUE, 150));
         var10.setAlignmentX(0.0F);
         var2.add(var10);
         var2.add(Box.createVerticalStrut(10));
         JLabel var8 = sectionCaption("执行记录");
         var8.setAlignmentX(0.0F);
         var2.add(var8);
         var2.add(Box.createVerticalStrut(7));
         this.monitorLog.setRows(10);
         this.monitorLog.setBackground(CODE_BG);
         this.monitorLog.setFont(new Font("Monospaced", 0, 11));
         JScrollPane var11 = softScroll(this.monitorLog);
         var11.setAlignmentX(0.0F);
         var11.setPreferredSize(new Dimension(100, 210));
         var11.setMaximumSize(new Dimension(Integer.MAX_VALUE, 230));
         var2.add(var11);
         var2.add(Box.createVerticalStrut(12));
         JLabel queueTitle = sectionCaption("运行队列");
         queueTitle.setAlignmentX(0.0F);
         var2.add(queueTitle);
         var2.add(Box.createVerticalStrut(7));
         this.styleResultTable(this.runQueueTable);
         this.runQueueTable.setFillsViewportHeight(true);
         JScrollPane queueScroll = softScroll(this.runQueueTable);
         queueScroll.setAlignmentX(0.0F);
         queueScroll.setPreferredSize(new Dimension(100, 150));
         queueScroll.setMaximumSize(new Dimension(Integer.MAX_VALUE, 170));
         var2.add(queueScroll);
         this.monitorCommand.setText("尚未执行命令");
         this.monitorOutcome.setText("运行后显示数据变化、回归样本和核心估计结果。\n普通 Stata 命令使用不确定进度，不显示虚假百分比。");
         var1.add(softScroll(var2), "Center");
         return var1;
      }

      private JComponent buildEmptyDataPanel() {
         JPanel var1 = new JPanel(new GridBagLayout());
         var1.setBackground(SURFACE);
         JPanel var2 = new JPanel();
         var2.setOpaque(false);
         var2.setLayout(new BoxLayout(var2, 1));
         JLabel var3 = new JLabel("尚未载入数据");
         var3.setForeground(TEXT);
         var3.setFont(var3.getFont().deriveFont(1, 18.0F));
         var3.setAlignmentX(0.5F);
         JLabel var4 = new JLabel("选择一种方式开始，载入后这里会显示可滚动的只读数据表。");
         var4.setForeground(MUTED);
         var4.setAlignmentX(0.5F);
         var2.add(var3);
         var2.add(Box.createVerticalStrut(8));
         var2.add(var4);
         var2.add(Box.createVerticalStrut(20));
         JPanel var5 = new JPanel(new GridLayout(0, 1, 0, 9));
         var5.setOpaque(false);
         JButton var6 = new JButton("载入 auto 测试数据");
         JButton var7 = new JButton("载入自己的 DTA");
         JButton var8 = new JButton("Excel / CSV 转换为 DTA");

         for (JButton var10 : Arrays.asList(var6, var7, var8)) {
            styleSecondaryButton(var10);
         }

         var6.addActionListener(var1x -> this.runUtility("sysuse auto, clear", true));
         var7.addActionListener(var1x -> this.chooseAndLoadDta());
         var8.addActionListener(var1x -> this.navigateTo("data", "导入与转换", "hxconvert"));
         var5.add(var6);
         var5.add(var7);
         var5.add(var8);
         var5.setMaximumSize(new Dimension(280, 130));
         var5.setAlignmentX(0.5F);
         var2.add(var5);
         var2.add(Box.createVerticalStrut(16));
         JLabel var11 = new JLabel("左侧路径：数据处理 → 导入与转换");
         var11.setForeground(MUTED);
         var11.setFont(var11.getFont().deriveFont(10.5F));
         var11.setAlignmentX(0.5F);
         var2.add(var11);
         var1.add(var2);
         return var1;
      }

      private JComponent buildImportPreviewPanel() {
         this.importPreviewTable.setAutoResizeMode(0);
         this.importPreviewTable.setRowHeight(25);
         this.importPreviewTable.setFillsViewportHeight(true);
         this.importPreviewTable.setShowVerticalLines(false);
         this.importPreviewTable.setGridColor(new Color(232, 236, 241));
         this.importPreviewTable.setSelectionBackground(ACCENT_SOFT);
         this.importPreviewTable.setSelectionForeground(TEXT);
         this.importPreviewTable.getTableHeader().setBackground(new Color(247, 249, 252));
         this.importPreviewTable.getTableHeader().setFont(this.importPreviewTable.getTableHeader().getFont().deriveFont(1, 11.0F));
         JPanel var1 = new JPanel(new BorderLayout(0, 8));
         var1.setBackground(SURFACE);
         JPanel var2 = new JPanel(new BorderLayout());
         var2.setOpaque(false);
         var2.setBorder(new EmptyBorder(7, 10, 0, 10));
         this.importPreviewLabel.setForeground(MUTED);
         var2.add(this.importPreviewLabel, "Center");
         var1.add(var2, "North");
         JTabbedPane var3 = new JTabbedPane();
         var3.addTab("数据预览", softScroll(this.importPreviewTable));
         var3.addTab("类型与问题", softScroll(this.importIssues));
         var1.add(var3, "Center");
         return var1;
      }

      private JComponent buildVariableInspectorPanel() {
         JPanel root = new JPanel(new BorderLayout(0, 7));
         root.setBackground(SURFACE);
         root.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220, 227, 237), 9),
            new EmptyBorder(9, 10, 9, 10)
         ));

         JPanel header = new JPanel(new BorderLayout(8, 0));
         header.setOpaque(false);
         JLabel title = new JLabel("变量窗口");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD, 13.0F));
         JLabel hint = new JLabel("拖到左侧变量框");
         hint.setForeground(MUTED);
         hint.setFont(hint.getFont().deriveFont(9.5F));
         header.add(title, BorderLayout.WEST);
         header.add(hint, BorderLayout.EAST);

         this.inspectorVariableFilter.putClientProperty("JTextField.placeholderText", "过滤变量（名称 / 标签）");
         this.inspectorVariableFilter.setToolTipText("按变量名或变量标签过滤；可直接拖动变量到左侧参数框");
         this.inspectorVariableTable.setRowHeight(24);
         this.inspectorVariableTable.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
         this.inspectorVariableTable.setFillsViewportHeight(true);
         this.inspectorVariableTable.setShowVerticalLines(false);
         this.inspectorVariableTable.setGridColor(new Color(235, 239, 245));
         this.inspectorVariableTable.getTableHeader().setReorderingAllowed(false);
         this.inspectorVariableTable.getTableHeader().setBackground(new Color(248, 250, 253));
         this.inspectorVariableTable.getColumnModel().getColumn(0).setPreferredWidth(118);
         this.inspectorVariableTable.getColumnModel().getColumn(1).setPreferredWidth(210);
         this.installInspectorVariableDragSupport();

         this.inspectorVariableFilter.getDocument().addDocumentListener(new HxWorkbench.SimpleDocumentListener(this::refreshInspectorVariables));
         this.inspectorVariableTable.getSelectionModel().addListSelectionListener(e -> {
            if (!e.getValueIsAdjusting()) this.syncInspectorSelectionFromVariableWindow();
         });

         JPanel top = new JPanel(new BorderLayout(0, 6));
         top.setOpaque(false);
         top.add(header, BorderLayout.NORTH);
         top.add(this.inspectorVariableFilter, BorderLayout.SOUTH);
         root.add(top, BorderLayout.NORTH);
         root.add(softScroll(this.inspectorVariableTable), BorderLayout.CENTER);
         return root;
      }

      private JComponent buildPropertyInspectorPanel() {
         JPanel root = new JPanel(new BorderLayout(0, 7));
         root.setBackground(SURFACE);
         root.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220, 227, 237), 9),
            new EmptyBorder(9, 10, 9, 10)
         ));
         JPanel header = new JPanel(new BorderLayout(8, 2));
         header.setOpaque(false);
         JLabel title = new JLabel("属性窗口");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD, 13.0F));
         this.inspectorRoleLabel.setForeground(ACCENT);
         this.inspectorRoleLabel.setFont(this.inspectorRoleLabel.getFont().deriveFont(Font.BOLD, 10.0F));
         header.add(title, BorderLayout.WEST);
         header.add(this.inspectorRoleLabel, BorderLayout.SOUTH);
         root.add(header, BorderLayout.NORTH);
         this.inspectorPropertyArea.setRows(8);
         this.inspectorPropertyArea.setBackground(SURFACE);
         this.inspectorPropertyArea.setForeground(TEXT);
         this.inspectorPropertyArea.setFont(this.inspectorPropertyArea.getFont().deriveFont(10.5F));
         JPanel body = new JPanel(new BorderLayout(0, 7));
         body.setOpaque(false);
         body.add(softScroll(this.inspectorPropertyArea), BorderLayout.CENTER);
         this.inspectorOverviewLabel.setForeground(MUTED);
         this.inspectorOverviewLabel.setFont(this.inspectorOverviewLabel.getFont().deriveFont(9.5F));
         body.add(this.inspectorOverviewLabel, BorderLayout.SOUTH);
         root.add(body, BorderLayout.CENTER);
         return root;
      }

      private void refreshInspectorVariables() {
         if (this.inspectorVariableModel == null) return;
         String selectedName = this.selectedInspectorVariable();
         String q = this.inspectorVariableFilter.getText() == null ? "" : this.inspectorVariableFilter.getText().trim().toLowerCase(Locale.ROOT);
         this.inspectorVariableModel.setRowCount(0);
         List<String> names = new ArrayList<>();
         if (this.previewMode && this.dataModel.getColumnCount() > 0) {
            for (int i = 0; i < this.dataModel.getColumnCount(); i++) names.add(this.dataModel.getColumnName(i));
         } else {
            names.addAll(HxWorkbench.StataBridge.variableNames());
         }
         for (String name : names) {
            int index = this.previewMode ? -1 : HxWorkbench.safe(() -> Data.getVarIndex(name), -1);
            String label = index > 0 ? HxWorkbench.safe(() -> Data.getVarLabel(index), "") : "";
            String hay = (name + " " + label).toLowerCase(Locale.ROOT);
            if (q.isBlank() || hay.contains(q)) this.inspectorVariableModel.addRow(new Object[]{name, label});
         }
         if (!selectedName.isBlank()) {
            for (int r = 0; r < this.inspectorVariableModel.getRowCount(); r++) {
               if (selectedName.equals(Objects.toString(this.inspectorVariableModel.getValueAt(r, 0), ""))) {
                  this.inspectorVariableTable.setRowSelectionInterval(r, r);
                  break;
               }
            }
         } else if (this.inspectorVariableModel.getRowCount() > 0) {
            this.inspectorVariableTable.setRowSelectionInterval(0, 0);
         }
      }

      private String selectedInspectorVariable() {
         int row = this.inspectorVariableTable.getSelectedRow();
         if (row >= 0 && row < this.inspectorVariableModel.getRowCount()) {
            return Objects.toString(this.inspectorVariableModel.getValueAt(row, 0), "").trim();
         }
         int viewCol = this.dataTable.getSelectedColumn();
         if (viewCol >= 0) return this.dataTable.getColumnName(viewCol);
         return "";
      }

      private void syncInspectorSelectionFromVariableWindow() {
         String variable = this.selectedInspectorVariable();
         if (variable.isBlank()) {
            this.refreshInspectorRole();
            return;
         }
         for (int view = 0; view < this.dataTable.getColumnCount(); view++) {
            if (variable.equals(this.dataTable.getColumnName(view))) {
               this.dataTable.setColumnSelectionInterval(view, view);
               if (this.dataTable.getRowCount() > 0) this.dataTable.setRowSelectionInterval(0, 0);
               break;
            }
         }
         if (this.previewMode && HxWorkbench.safe(() -> Data.getVarIndex(variable), -1) <= 0) {
            this.summaryArea.setText("变量：" + variable + "\n\n预览模式下仅展示变量结构；载入真实 Stata 数据后显示类型、标签、缺失值和描述统计。");
            this.inspectorPropertyArea.setText(this.summaryArea.getText());
            this.histogram.setValues(Collections.emptyList(), variable);
            this.refreshInspectorRole();
         } else {
            this.updateSelectedColumnSummary();
         }
      }

      private void syncVariableWindowFromDataTable() {
         int viewColumn = this.dataTable.getSelectedColumn();
         if (viewColumn < 0) {
            this.updateSelectedColumnSummary();
            return;
         }
         String variable = this.dataTable.getColumnName(viewColumn);
         if (!variable.equals(this.selectedInspectorVariable())) {
            int matchedRow = -1;
            for (int row = 0; row < this.inspectorVariableModel.getRowCount(); row++) {
               if (variable.equals(Objects.toString(this.inspectorVariableModel.getValueAt(row, 0), ""))) {
                  matchedRow = row;
                  break;
               }
            }
            if (matchedRow >= 0) {
               this.inspectorVariableTable.setRowSelectionInterval(matchedRow, matchedRow);
               Rectangle cell = this.inspectorVariableTable.getCellRect(matchedRow, 0, true);
               this.inspectorVariableTable.scrollRectToVisible(cell);
            } else {
               this.inspectorVariableTable.clearSelection();
            }
         }
         this.updateSelectedColumnSummary();
      }

      private void installInspectorVariableDragSupport() {
         this.inspectorVariableTable.setTransferHandler(new TransferHandler() {
            @Override
            protected Transferable createTransferable(JComponent c) {
               String variable = WorkbenchFrame.this.selectedInspectorVariable();
               return variable.isBlank() ? null : new StringSelection(variable);
            }
            @Override public int getSourceActions(JComponent c) { return COPY; }
         });
         if (!GraphicsEnvironment.isHeadless()) this.inspectorVariableTable.setDragEnabled(true);
         this.inspectorVariableTable.setToolTipText("按住变量行拖到左侧 Y / X / 面板 ID / 时间变量框");
      }

      private String inspectorRoleFor(String variable) {
         if (variable == null || variable.isBlank()) return "未使用";
         if ("xtreg".equals(this.currentCommand)) {
            if (this.xtregPanelVar != null && variable.equals(Objects.toString(this.xtregPanelVar.getSelectedItem(), ""))) return "面板 ID";
            if (this.xtregTimeVar != null && variable.equals(Objects.toString(this.xtregTimeVar.getSelectedItem(), ""))) return "时间变量";
            if (this.xtregDepVar != null && variable.equals(Objects.toString(this.xtregDepVar.getSelectedItem(), ""))) return "因变量 Y";
            if (this.xtregIndepList != null && this.xtregIndepList.getSelectedValuesList().contains(variable)) return "解释变量 X";
         }
         if (variable.equals(selected(this.depvar))) return "因变量 Y";
         if (this.variables.getSelectedValuesList().contains(variable)) return "解释变量 X";
         if (this.absorb.getSelectedValuesList().contains(variable)) return "固定效应 FE";
         if (variable.equals(selected(this.cluster))) return "聚类变量";
         if (variable.equals(selected(this.panel))) return "面板 ID";
         if (variable.equals(selected(this.time))) return "时间变量";
         return "未使用";
      }

      private void refreshInspectorRole() {
         String variable = this.selectedInspectorVariable();
         this.inspectorRoleLabel.setText("当前模型角色：" + this.inspectorRoleFor(variable));
      }

      private JComponent buildDataContainer() {
         JPanel root = new JPanel(new BorderLayout());
         root.setBackground(APP_BG);
         root.setBorder(new EmptyBorder(18, 6, 16, 18));

         JComponent variableWindow = this.buildVariableInspectorPanel();
         JComponent propertyWindow = this.buildPropertyInspectorPanel();
         variableWindow.setMinimumSize(new Dimension(0, 120));
         propertyWindow.setMinimumSize(new Dimension(0, 120));
         this.inspectorLowerSplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT, variableWindow, propertyWindow);
         this.inspectorLowerSplit.setResizeWeight(0.54);
         this.inspectorLowerSplit.setContinuousLayout(true);
         this.inspectorLowerSplit.setBorder(null);
         this.inspectorLowerSplit.setDividerSize(5);
         JPanel middle = new JPanel(new BorderLayout());
         middle.setBackground(APP_BG);
         middle.setBorder(new EmptyBorder(0, 0, 0, 6));
         middle.setPreferredSize(new Dimension(250, 0));
         middle.setMinimumSize(new Dimension(210, 0));
         middle.add(this.inspectorLowerSplit, BorderLayout.CENTER);

         JPanel card = cardPanel();
         card.setLayout(new BorderLayout());
         card.setMinimumSize(new Dimension(300, 0));
         card.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(216, 224, 235), 11), new EmptyBorder(0, 0, 0, 0)));
         JPanel header = new JPanel(new BorderLayout(10, 4));
         header.setOpaque(false);
         header.setBorder(new EmptyBorder(14, 15, 9, 15));
         this.rightPaneTitle.setForeground(TEXT);
         this.rightPaneTitle.setFont(this.rightPaneTitle.getFont().deriveFont(Font.BOLD, 15.0F));
         styleSecondaryButton(this.refreshButton);
         header.add(this.rightPaneTitle, BorderLayout.WEST);
         header.add(this.refreshButton, BorderLayout.EAST);
         this.dataLabel.setForeground(MUTED);
         this.dataLabel.setFont(this.dataLabel.getFont().deriveFont(10.0F));
         header.add(this.dataLabel, BorderLayout.SOUTH);
         card.add(header, BorderLayout.NORTH);
         this.dataTabs.setBorder(new EmptyBorder(0, 6, 6, 6));
         card.add(this.dataTabs, BorderLayout.CENTER);

         this.inspectorDataSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, middle, card);
         this.inspectorDataSplit.setResizeWeight(0.0);
         this.inspectorDataSplit.setContinuousLayout(true);
         this.inspectorDataSplit.setOneTouchExpandable(false);
         this.inspectorDataSplit.setDividerSize(6);
         this.inspectorDataSplit.setBorder(null);
         root.add(this.inspectorDataSplit, BorderLayout.CENTER);
         SwingUtilities.invokeLater(() -> this.inspectorDataSplit.setDividerLocation(250));
         return root;
      }

      private void attachSharedInspectorToOneClick() {
         if (this.sharedDataInspector == null) {
            return;
         }
         Container parent = this.sharedDataInspector.getParent();
         if (parent != null) {
            parent.remove(this.sharedDataInspector);
         }
         this.exactOneClickInspectorHost.removeAll();
         this.exactOneClickInspectorHost.add(this.sharedDataInspector, BorderLayout.CENTER);
         this.sharedDataInspector.setVisible(true);
         this.exactOneClickInspectorHost.revalidate();
         this.exactOneClickInspectorHost.repaint();
      }

      private void attachSharedInspectorToWorkspace() {
         if (this.sharedDataInspector == null || this.commandDataSplit == null) {
            return;
         }
         if (this.commandDataSplit.getRightComponent() != this.sharedDataInspector) {
            Container parent = this.sharedDataInspector.getParent();
            if (parent != null) {
               parent.remove(this.sharedDataInspector);
            }
            this.commandDataSplit.setRightComponent(this.sharedDataInspector);
         }
         this.sharedDataInspector.setVisible(true);
         this.commandDataSplit.setDividerSize(8);
         this.commandDataSplit.revalidate();
         this.commandDataSplit.repaint();
         SwingUtilities.invokeLater(this::applyDividerRatios);
      }

      private void syncRightPaneTitle() {
         int index = this.dataTabs.getSelectedIndex();
         if (index == 1) {
            this.rightPaneTitle.setText("结果");
            this.refreshButton.setVisible(false);
            String command = this.lastExecutedCommand == null ? "" : this.lastExecutedCommand.trim();
            this.dataLabel.setText(command.isBlank() ? "运行命令后显示 Stata 原始输出与执行摘要" : "最近命令：" + shortenCommand(command));
         } else if (index == 2) {
            this.rightPaneTitle.setText("运行日志");
            this.refreshButton.setVisible(false);
            this.dataLabel.setText(this.runInProgress ? "命令执行中 · 查看实时计时与状态" : "执行状态、耗时、Return code 与 History");
         } else {
            this.rightPaneTitle.setText("当前数据");
            this.refreshButton.setVisible(true);
            long n = Data.getObsTotal();
            int k = Data.getVarCount();
            String dataHint = "xtreg".equals(this.currentCommand) ? " | 可从中间变量窗口或表头拖入左侧变量框" : " | 表格只读，可横向和纵向滚动";
            this.dataLabel.setText(n != 0L && k != 0 ? n + " 行 × " + k + " 列" + dataHint : "尚未载入数据");
         }
      }

      private void selectDataView() {
         this.dataTabs.setSelectedIndex(0);
         this.syncRightPaneTitle();
      }

      private void selectResultView(String var1, boolean var2) {
         this.resultLayout.show(this.resultCards, var1);
         if (var2) {
            this.dataTabs.setSelectedIndex(1);
         }
         this.syncRightPaneTitle();
      }

      private void selectRunView() {
         this.dataTabs.setSelectedIndex(2);
         this.syncRightPaneTitle();
      }

      private JComponent buildStatusBar() {
         JPanel var1 = new JPanel(new BorderLayout(10, 0));
         var1.setBorder(BorderFactory.createCompoundBorder(BorderFactory.createMatteBorder(1, 0, 0, 0, BORDER), new EmptyBorder(7, 18, 8, 18)));
         var1.setBackground(SURFACE);
         this.statusLabel.setForeground(MUTED);
         this.statusLabel.setFont(this.statusLabel.getFont().deriveFont(10.5F));
         var1.add(this.statusLabel, BorderLayout.CENTER);
         JLabel var2 = new JLabel("●  Stata 已连接   ·   数据只读，修改统一通过 Stata 命令");
         var2.setForeground(new Color(50, 126, 88));
         var2.setFont(var2.getFont().deriveFont(10.0F));
         var1.add(var2, BorderLayout.EAST);
         return var1;
      }

      private void wireEvents() {
         this.categoryList.addListSelectionListener(var1x -> {
            if (!var1x.getValueIsAdjusting() && !this.rebuilding) {
               this.categoryChanged();
            }
         });
         this.methodList.addListSelectionListener(var1x -> {
            if (!var1x.getValueIsAdjusting() && !this.rebuilding) {
               this.methodChanged();
            }
         });
         this.commandList.addListSelectionListener(var1x -> {
            if (!var1x.getValueIsAdjusting() && !this.rebuilding) {
               String var2x = this.commandList.getSelectedValue();
               if (var2x != null && !var2x.isBlank()) {
                  this.openCommandPage(var2x);
               }
            }
         });
         this.refreshButton.addActionListener(var1x -> this.refreshDataset(false));
         this.dataTabs.addChangeListener(var1x -> this.syncRightPaneTitle());
         this.runButton.addActionListener(var1x -> this.runCurrentCommand());
         this.copyCommandButton.addActionListener(var1x -> this.copyCurrentCommand());
         this.dataTable.getSelectionModel().addListSelectionListener(var1x -> {
            if (!var1x.getValueIsAdjusting()) this.syncVariableWindowFromDataTable();
         });
         this.dataTable.getColumnModel().getSelectionModel().addListSelectionListener(var1x -> {
            if (!var1x.getValueIsAdjusting()) this.syncVariableWindowFromDataTable();
         });
         this.dataTable.getTableHeader().addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent var1) {
               int var2 = WorkbenchFrame.this.dataTable.columnAtPoint(var1.getPoint());
               if (var2 >= 0) {
                  WorkbenchFrame.this.dataTable.setColumnSelectionInterval(var2, var2);
                  if (WorkbenchFrame.this.dataTable.getRowCount() > 0) {
                     WorkbenchFrame.this.dataTable.setRowSelectionInterval(0, 0);
                  }

                  WorkbenchFrame.this.updateSelectedColumnSummary();
               }
            }
         });
         this.missingChartType.addActionListener(var1x -> this.missingChart.setChartType(selected(this.missingChartType)));
         ActionListener var1 = var1x -> {
            this.missingVariables.setEnabled(this.missingChooseVariables.isSelected());
            boolean var2x = this.missingMode.getSelectedIndex() > 0;
            this.missingGroups.setEnabled(var2x);
            this.missingSeparateSummary.setEnabled(var2x && this.missingGroups.getSelectedIndices().length > 1);
            this.updateMissingPreview();
         };
         this.missingAllVariables.addActionListener(var1);
         this.missingChooseVariables.addActionListener(var1);
         this.missingMode.addActionListener(var1);
         this.missingSeparateSummary.addActionListener(var1);
         this.missingOnly.addActionListener(var1);
         this.missingSort.addActionListener(var1);
         this.missingVariables.addListSelectionListener(var1x -> {
            if (!var1x.getValueIsAdjusting()) {
               this.updateMissingPreview();
            }
         });
         this.missingGroups.addListSelectionListener(var1x -> {
            if (!var1x.getValueIsAdjusting()) {
               this.missingSeparateSummary.setEnabled(this.missingMode.getSelectedIndex() > 0 && this.missingGroups.getSelectedIndices().length > 1);
               this.updateMissingPreview();
            }
         });
         this.missingMinCount.addChangeListener(var1x -> this.updateMissingPreview());
         this.missingMinRate.addChangeListener(var1x -> this.updateMissingPreview());
         ActionListener var2 = var1x -> {
            boolean var2x = this.convertBatchMode.isSelected();
            this.convertModeLayout.show(this.convertModeCards, var2x ? "batch" : "single");
            this.runButton.setText(var2x ? "开始批量转换" : "转换为 DTA");
            this.updateConversionPreview();
         };
         this.convertSingleMode.addActionListener(var2);
         this.convertBatchMode.addActionListener(var2);
         this.convertInputFile.addActionListener(var1x -> {
            try {
               Path var2x = Paths.get(this.convertInputFile.getText().trim()).toAbsolutePath();
               this.detectExternalFile(var2x);
               if (this.convertOutputFile.getText().isBlank()) {
                  this.convertOutputFile.setText(replaceExtension(var2x, ".dta").toString());
               }

               this.previewSelectedExternalFile();
            } catch (Exception var3) {
            }
         });
         this.convertOutputFile.getDocument().addDocumentListener(new HxWorkbench.SimpleDocumentListener(this::updateConversionPreview));

         for (AbstractButton var4 : Arrays.asList(
            this.convertExcelFirstRow,
            this.convertExcelAllString,
            this.convertDelimitedFirstRow,
            this.convertProtectLeadingZeros,
            this.convertLoadAfter,
            this.batchXlsx,
            this.batchCsv,
            this.batchTxt,
            this.batchSkipExisting
         )) {
            var4.addActionListener(var1x -> this.updateConversionPreview());
         }

         this.convertSheet.addActionListener(var1x -> this.updateConversionPreview());
         this.convertDelimiter.addActionListener(var1x -> this.updateConversionPreview());
         this.convertEncoding.addActionListener(var1x -> this.updateConversionPreview());
         this.vce.addActionListener(var1x -> {
            this.updateConditionalFields();
            if (this.regressWorkspaceActive || this.baselineTaskActive) {
               this.updateRegressConditionalFields();
            }
         });
         this.genericWeightType.addActionListener(var1x -> {
            this.updateGenericWeightConditionalFields();
            this.schedulePreview();
         });
         this.addPreviewListeners(
            this.depvar,
            this.variables,
            this.newvar,
            this.expression,
            this.model,
            this.usingFile,
            this.panel,
            this.time,
            this.absorb,
            this.endog,
            this.instruments,
            this.vce,
            this.cluster,
            this.ifCondition,
            this.inCondition,
            this.genericWeightType,
            this.genericWeightVar,
            this.options
         );
         this.addPreviewListeners(
            this.regressX,
            this.regressControls,
            this.regressFactor,
            this.regressInteractionA,
            this.regressInteractionB,
            this.regressInteractionType,
            this.regressLagVar,
            this.regressWeightType,
            this.regressWeightVar,
            this.regressAdvancedOptions
         );
         this.regressLagOrder.addChangeListener(var1x -> this.schedulePreview());
         this.regressLevel.addChangeListener(var1x -> this.schedulePreview());
         this.regressNoConstant.addActionListener(var1x -> this.schedulePreview());
         this.regressBeta.addActionListener(var1x -> this.schedulePreview());
         this.regressWeightType.addActionListener(var1x -> this.updateRegressConditionalFields());
         this.baselineEstimator.addActionListener(var1x -> {
            if (!this.rebuilding && this.baselineTaskActive) {
               this.switchBaselineEstimator();
            }
         });
         this.baselineXtModel.addActionListener(var1x -> {
            if (!this.rebuilding && this.baselineTaskActive) {
               this.updateBaselinePreview();
            }
         });
         this.depvar.addActionListener(var1x -> {
            if (this.regressWorkspaceActive || this.baselineTaskActive) {
               this.sanitizeRegressControls();
               this.schedulePreview();
            }
         });
         this.regressX.addActionListener(var1x -> {
            if (this.regressWorkspaceActive || this.baselineTaskActive) {
               this.sanitizeRegressControls();
               this.schedulePreview();
            }
         });
         this.addPreviewListeners(
            this.oneClickY,
            this.oneClickX,
            this.oneClickRequired,
            this.oneClickCandidates,
            this.oneClickEstimator,
            this.oneClickP,
            this.oneClickAbsorb,
            this.oneClickVce,
            this.oneClickCluster
         );
         this.oneClickEstimator.addActionListener(var1x -> this.updateOneClickConditionalFields());
         this.oneClickVce.addActionListener(var1x -> this.updateOneClickConditionalFields());
         this.addPreviewListeners(
            this.didAction,
            this.didEstimator,
            this.didUnit,
            this.didTime,
            this.didTreat,
            this.didPost,
            this.didEvent,
            this.didEventCode,
            this.didNewVar,
            this.didPolicyTime
         );
         this.didBasePeriod.addChangeListener(var1x -> this.schedulePreview());
         this.didUnitFE.addActionListener(var1x -> this.schedulePreview());
         this.didTimeFE.addActionListener(var1x -> this.schedulePreview());
         this.didUnit.addActionListener(var1x -> {
            if (!this.rebuilding && "did_builder".equals(this.currentCommand)) {
               if ("cluster".equals(selected(this.vce))) {
                  this.cluster.setSelectedItem(selected(this.didUnit));
               }

               this.schedulePreview();
            }
         });
         this.didEstimator.addActionListener(var1x -> {
            if (!this.rebuilding && "did_builder".equals(this.currentCommand)) {
               this.showDidBuilderPage();
            }
         });
         this.vce.addActionListener(var1x -> {
            if (!this.rebuilding && "did_builder".equals(this.currentCommand)) {
               this.showDidBuilderPage();
            }
         });
         this.didAction.addActionListener(var1x -> {
            if (!this.rebuilding && "did_builder".equals(this.currentCommand)) {
               String var2x = selected(this.didAction);
               if (var2x.startsWith("生成政策后")) {
                  this.didNewVar.setText("post");
               } else if (var2x.startsWith("生成交互项")) {
                  this.didNewVar.setText("did");
               } else if (var2x.startsWith("生成相对")) {
                  this.didNewVar.setText("event_time");
               } else if (var2x.startsWith("生成事件研究编码")) {
                  this.didNewVar.setText("event_code");
               }

               this.showDidBuilderPage();
            }
         });
      }

      private void populateCategories() {
         this.rebuilding = true;
         this.categoryModel.clear();
         this.categoryModel.addElement(new HxWorkbench.Category("开始", "home"));
         this.categoryModel.addElement(new HxWorkbench.Category("数据处理", "data"));
         this.categoryModel.addElement(new HxWorkbench.Category("统计", "stats"));
         this.categoryModel.addElement(new HxWorkbench.Category("回归模型", "reg"));
         this.categoryModel.addElement(new HxWorkbench.Category("后估计", "post"));
         this.categoryModel.addElement(new HxWorkbench.Category("图形", "graph"));
         this.categoryModel.addElement(new HxWorkbench.Category("OneClick 专区", "oneclick"));
         this.categoryModel.addElement(new HxWorkbench.Category("测试数据", "test"));
         this.categoryModel.addElement(new HxWorkbench.Category("性能设置", "performance"));
         this.categoryModel.addElement(new HxWorkbench.Category("常用命令", "favorites"));
         this.categoryModel.addElement(new HxWorkbench.Category("最近使用", "recent"));
         this.categoryList.setSelectedIndex(0);
         this.rebuilding = false;
         this.showHomePage();
      }

      private void categoryChanged() {
         HxWorkbench.Category var1 = this.categoryList.getSelectedValue();
         if (var1 != null) {
            this.searchResultsMode = false;
            if (var1.code.equals("home")) {
               this.showHomePage();
            } else if (var1.code.equals("test")) {
               this.showSpecialPage("test");
            } else if (var1.code.equals("performance")) {
               this.showSpecialPage("performance");
            } else {
               this.loadCategory(var1.code);
            }
         }
      }

      private void loadCategory(String var1) {
         this.searchResultsMode = false;
         this.commandList.setFixedCellHeight(30);
         HxWorkbench.Category var2 = this.categoryList.getSelectedValue();
         String var3 = var2 == null ? categoryLabel(var1) : var2.label;
         this.methodCaption.setText("当前：" + var3);
         this.commandCaption.setText("选择方法后显示命令");
         this.setBusy(true, "正在读取命令目录…");
         int var4 = HxWorkbench.StataBridge.execute("quietly hxregistry, category(" + var1 + ")", false);
         this.rebuilding = true;
         this.methodModel.clear();
         this.commandModel.clear();

         for (String var6 : HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_method_view"))) {
            this.methodModel.addElement(var6);
         }

         for (String var9 : HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_command_view"))) {
            this.commandModel.addElement(var9);
         }

         if (!this.methodModel.isEmpty()) {
            this.methodList.setSelectedIndex(0);
         } else if (!this.commandModel.isEmpty()) {
            this.commandList.setSelectedIndex(0);
         }

         String var8 = this.methodList.getSelectedValue();
         String var10 = this.commandList.getSelectedValue();
         this.rebuilding = false;
         if (var8 != null) {
            this.methodChanged();
         } else if (var10 != null) {
            this.openCommandPage(var10);
         }

         this.setBusy(false, var4 == 0 ? "已读取命令目录。" : "读取命令目录失败，返回码 " + var4);
      }

      private void methodChanged() {
         String var1 = this.methodList.getSelectedValue();
         if (var1 != null) {
            HxWorkbench.Category var2 = this.categoryList.getSelectedValue();
            this.browseMethod(var2 == null ? this.activeCategoryCode : var2.code, var1);
         }
      }

      private void searchCommands() {
         String var1 = this.searchField.getText().trim();
         if (!var1.isEmpty()) {
            this.searchResultsMode = true;
            this.commandList.setFixedCellHeight(44);
            this.methodCaption.setText("搜索：" + var1);
            this.commandCaption.setText("结果（悬停可查看所属路径）");
            this.setBusy(true, "正在搜索“" + var1 + "”…");
            int var2 = HxWorkbench.StataBridge.execute("quietly hxregistry, search(" + HxWorkbench.StataBridge.quote(var1) + ")", false);
            this.rebuilding = true;
            this.methodModel.clear();
            this.commandModel.clear();

            for (String var4 : HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_command_view"))) {
               this.commandModel.addElement(var4);
            }

            String var7 = var1.toLowerCase(Locale.ROOT);
            LinkedHashSet var8 = new LinkedHashSet<>(Collections.list(this.commandModel.elements()));

            for (Entry var6 : COMMAND_GUIDES.entrySet()) {
               if (((HxWorkbench.WorkbenchFrame.CommandGuide)var6.getValue()).searchableText((String)var6.getKey()).contains(var7)
                  && var8.add((String)var6.getKey())) {
                  this.commandModel.addElement((String)var6.getKey());
               }
            }

            this.rebuilding = false;
            if (this.commandModel.isEmpty() && var1.matches("[A-Za-z_][A-Za-z0-9_]*")) {
               this.commandModel.addElement(var1);
            }

            this.activeCategoryCode = "search";
            this.activeCategoryName = "搜索结果";
            this.activeMethodName = var1;
            this.renderCommandChooser("搜索结果", var1, Collections.list(this.commandModel.elements()));
            this.setBusy(false, var2 == 0 ? "搜索完成。" : "搜索失败，返回码 " + var2);
         }
      }

      private void showCommand(String var1) {
         if ("regress".equals(var1)) {
            this.showRegressPage();
         } else {
            this.regressWorkspaceActive = false;
            this.showWorkspacePage();
            this.selectResultView("general", false);
            this.selectDataView();
            this.commandDock.setVisible(true);
            this.commandTabs.setVisible(true);
            this.runButton.setText("运行命令");
            this.previewArea.setEditable(true);
            this.setBusy(true, "正在解析 " + var1 + "…");
            int var2 = HxWorkbench.StataBridge.execute("quietly hxresolve " + var1, false);
            if (var2 != 0) {
               this.setBusy(false, "解析失败，返回码 " + var2 + "。可以在搜索框输入其他命令。");
            } else {
               this.offerOptionalDependency(var1);
               this.currentCommand = var1;
               String var3 = visibleText(HxWorkbench.StataBridge.characteristic("hxtoolbox_sem_title"));
               this.commandTitle.setText(var3);
               this.commandTitle.setToolTipText(var3);
               this.setWorkspaceBreadcrumb(commandPath(var1));
               String var4 = visibleText(HxWorkbench.StataBridge.characteristic("hxtoolbox_sem_example1"));
               String var5 = visibleText(HxWorkbench.StataBridge.characteristic("hxtoolbox_sem_explain1"));
               this.exampleLabel.setText("<html><b>最简单例子：</b> " + html(var4) + (var5.isBlank() ? "" : "　　" + html(var5)) + "</html>");
               this.insightArea
                  .setText(
                     visibleText(
                        String.join(
                           "\n\n",
                           HxWorkbench.StataBridge.characteristic("hxtoolbox_insight_intent"),
                           HxWorkbench.StataBridge.characteristic("hxtoolbox_insight_data"),
                           HxWorkbench.StataBridge.characteristic("hxtoolbox_insight_advantages"),
                           HxWorkbench.StataBridge.characteristic("hxtoolbox_insight_limitations")
                        )
                     )
                  );
               this.syntaxArea
                  .setText(
                     HxWorkbench.StataBridge.characteristic("hxtoolbox_resolve_quality")
                        + "\n"
                        + HxWorkbench.StataBridge.characteristic("hxtoolbox_resolve_syntax")
                  );
               this.rebuildForm();
               this.updatePreview();
               this.setBusy(false, "已由统一解析流程生成 " + var1 + " 页面。");
            }
         }
      }

      private void openBaselineRegressionWorkspace() {
         this.activeCategoryCode = "reg";
         this.activeCategoryName = "回归模型";
         this.activeMethodName = "基准回归";
         this.chooserReady = false;
         this.showBaselineRegressionPage(true);
      }

      private void showBaselineRegressionPage(boolean resetEstimator) {
         this.regressWorkspaceActive = false;
         this.baselineTaskActive = true;
         this.showWorkspacePage();
         this.selectDataView();
         this.commandDock.setVisible(true);
         this.commandTabs.setVisible(true);
         this.commandTabs.setSelectedIndex(0);
         this.previewArea.setEditable(true);
         this.runButton.setText("运行基准回归");
         this.commandTitle.setText("基准回归");
         this.commandTitle.setToolTipText("在同一个任务页面切换 xtreg / reghdfe / areg / regress");
         this.setWorkspaceBreadcrumb("回归模型  ›  基准回归");
         this.exampleLabel.setText("<html>先设定研究问题，再选择估计方法。默认使用 xtreg；切换估计器时公共变量设置保持不变。</html>");
         this.insightArea.setText("基准回归工作区把研究任务放在前面。默认使用 xtreg（固定效应），也可以在同一页切换 reghdfe、areg 或 regress。切换时保留 Y、核心 X、Controls、样本条件和标准误等公共设置，只替换估计器特有参数和最终 Stata 命令。");
         this.syntaxArea.setText("任务工作区：xtreg / reghdfe / areg / regress；最终仍执行所选估计器的真实 Stata 命令。");
         if (this.baselineEstimatorHeader != null) this.baselineEstimatorHeader.setVisible(true);
         this.refreshVariableControls();
         this.refreshRegressVariables(true);
         if (resetEstimator) {
            this.rebuilding = true;
            this.baselineEstimator.setSelectedItem("xtreg");
            this.baselineXtModel.setSelectedItem("固定效应（FE）");
            this.rebuilding = false;
         }
         this.switchBaselineEstimator();
         this.statusLabel.setText("基准回归：默认 xtreg；可在右上角切换估计方法，公共变量设置不会清空。");
      }

      private void switchBaselineEstimator() {
         if (!this.baselineTaskActive) return;
         String estimator = selected(this.baselineEstimator);
         if (estimator.isBlank()) return;
         this.currentCommand = estimator;
         this.baselineEstimatorSource.setText(commandSource(estimator));
         this.baselineEstimatorSource.setForeground("第三方".equals(commandSource(estimator)) ? new Color(143, 91, 24) : ACCENT);
         if (!this.previewMode) {
            HxWorkbench.StataBridge.execute("quietly hxresolve " + estimator, false);
            this.offerOptionalDependency(estimator);
         }
         this.rebuilding = true;
         String previousWeight = selected(this.regressWeightType);
         this.regressWeightType.removeAllItems();
         this.regressWeightType.addItem("无");
         this.regressWeightType.addItem("fweight");
         this.regressWeightType.addItem("aweight");
         this.regressWeightType.addItem("pweight");
         if (!"reghdfe".equals(estimator) && !"areg".equals(estimator)) this.regressWeightType.addItem("iweight");
         this.setComboValue(this.regressWeightType, previousWeight);
         if (selected(this.regressWeightType).isBlank()) this.regressWeightType.setSelectedItem("无");
         this.rebuilding = false;
         this.rebuildBaselineForm();
         this.updateBaselinePreview();
      }

      private void rebuildBaselineForm() {
         String estimator = selected(this.baselineEstimator);
         this.formPanel.removeAll();
         int row = 0;
         this.addField(row++, "因变量 Y", this.depvar);
         this.addField(row++, "核心解释变量 X", this.regressX);
         this.addField(row++, "控制变量 Controls（可多选）", this.listPane(this.regressControls));
         this.baselineXtModelFieldBlock = null;
         this.baselineAbsorbFieldBlock = null;
         if ("xtreg".equals(estimator)) {
            this.baselineXtModelFieldBlock = this.addField(row++, "模型", this.baselineXtModel);
         } else if ("reghdfe".equals(estimator) || "areg".equals(estimator)) {
            this.absorb.setSelectionMode("areg".equals(estimator) ? 0 : 2);
            this.baselineAbsorbFieldBlock = this.addField(row++, "固定效应 absorb()", this.listPane(this.absorb));
         }
         this.addField(row++, "标准误", this.vce);
         this.regressClusterFieldBlock = this.addField(row++, "聚类变量", this.cluster);

         JPanel moreSettings = this.buildBaselineMoreSettings(estimator);
         JToggleButton moreToggle = new JToggleButton("展开更多设置  +");
         styleSecondaryButton(moreToggle);
         moreSettings.setVisible(false);
         moreToggle.addActionListener(event -> {
            boolean expanded = moreToggle.isSelected();
            moreToggle.setText(expanded ? "收起更多设置  −" : "展开更多设置  +");
            moreSettings.setVisible(expanded);
            this.formPanel.revalidate();
            this.formPanel.repaint();
         });
         JPanel moreBlock = new JPanel();
         moreBlock.setOpaque(false);
         moreBlock.setLayout(new BoxLayout(moreBlock, BoxLayout.Y_AXIS));
         moreToggle.setAlignmentX(0.0F);
         moreSettings.setAlignmentX(0.0F);
         moreBlock.add(moreToggle);
         moreBlock.add(Box.createVerticalStrut(7));
         moreBlock.add(moreSettings);
         this.addField(row++, "更多设置", moreBlock);
         GridBagConstraints filler = this.constraints(0, row);
         filler.gridwidth = 2;
         filler.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), filler);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.updateRegressConditionalFields();
      }

      private JPanel buildBaselineMoreSettings(String estimator) {
         JPanel panel = new JPanel();
         panel.setOpaque(false);
         panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
         JPanel sampleRow = new JPanel(new GridLayout(1, 2, 8, 0));
         sampleRow.setOpaque(false);
         sampleRow.add(this.miniLabeled("样本条件 if", this.ifCondition));
         sampleRow.add(this.miniLabeled("观测范围 in", this.inCondition));
         panel.add(sampleRow);
         panel.add(Box.createVerticalStrut(12));
         JLabel termsTitle = new JLabel("分类变量、交互项与滞后项");
         termsTitle.setForeground(MUTED);
         termsTitle.setFont(termsTitle.getFont().deriveFont(Font.BOLD));
         termsTitle.setAlignmentX(0.0F);
         panel.add(termsTitle);
         panel.add(Box.createVerticalStrut(7));
         panel.add(this.buildRegressTermBuilder());
         panel.add(Box.createVerticalStrut(12));
         JPanel weightRow = new JPanel(new GridLayout(1, 2, 8, 0));
         weightRow.setOpaque(false);
         weightRow.add(this.miniLabeled("权重类型", this.regressWeightType));
         weightRow.add(this.miniLabeled("权重变量", this.regressWeightVar));
         this.regressWeightVarFieldBlock = weightRow;
         panel.add(weightRow);
         if ("regress".equals(estimator)) {
            panel.add(Box.createVerticalStrut(10));
            JPanel reportRow = new JPanel(new GridLayout(1, 3, 8, 0));
            reportRow.setOpaque(false);
            reportRow.add(this.regressNoConstant);
            reportRow.add(this.regressBeta);
            reportRow.add(this.miniLabeled("置信水平", this.regressLevel));
            panel.add(reportRow);
         }
         panel.add(Box.createVerticalStrut(10));
         panel.add(this.labeledInline("其他 Stata options（高级）", this.regressAdvancedOptions));
         return panel;
      }

      private void updateBaselinePreview() {
         if (!this.baselineTaskActive || this.rebuilding) return;
         String estimator = selected(this.baselineEstimator);
         String y = selected(this.depvar);
         String x = selected(this.regressX);
         LinkedHashSet<String> rhs = new LinkedHashSet<>();
         if (!x.isBlank()) rhs.add(x);
         for (String control : this.regressControls.getSelectedValuesList()) {
            if (!control.equals(y) && !control.equals(x)) rhs.add(control);
         }
         for (int i = 0; i < this.regressSpecialTermsModel.size(); i++) rhs.add(this.regressSpecialTermsModel.get(i));
         StringBuilder command = new StringBuilder(estimator);
         if (!y.isBlank()) command.append(" ").append(y);
         if (!rhs.isEmpty()) command.append(" ").append(String.join(" ", rhs));
         String weight = selected(this.regressWeightType);
         String weightVar = selected(this.regressWeightVar);
         if (!"无".equals(weight) && !weightVar.isBlank()) command.append(" [").append(weight).append("=").append(weightVar).append("]");
         if (!this.ifCondition.getText().trim().isBlank()) command.append(" if ").append(this.ifCondition.getText().trim());
         if (!this.inCondition.getText().trim().isBlank()) command.append(" in ").append(this.inCondition.getText().trim());
         ArrayList<String> opts = new ArrayList<>();
         if ("xtreg".equals(estimator)) {
            String modelText = selected(this.baselineXtModel);
            opts.add(modelText.startsWith("固定") ? "fe" : modelText.startsWith("随机") ? "re" : "be");
         } else if ("reghdfe".equals(estimator) && !this.absorb.getSelectedValuesList().isEmpty()) {
            opts.add("absorb(" + String.join(" ", this.absorb.getSelectedValuesList()) + ")");
         } else if ("areg".equals(estimator) && !this.absorb.getSelectedValuesList().isEmpty()) {
            opts.add("absorb(" + this.absorb.getSelectedValuesList().get(0) + ")");
         }
         if ("robust".equals(selected(this.vce))) opts.add("vce(robust)");
         else if ("cluster".equals(selected(this.vce)) && !selected(this.cluster).isBlank()) opts.add("vce(cluster " + selected(this.cluster) + ")");
         if ("regress".equals(estimator)) {
            if (this.regressNoConstant.isSelected()) opts.add("noconstant");
            if (this.regressBeta.isSelected()) opts.add("beta");
            int level = ((Number)this.regressLevel.getValue()).intValue();
            if (level != 95) opts.add("level(" + level + ")");
         }
         if (!this.regressAdvancedOptions.getText().trim().isBlank()) opts.add(this.regressAdvancedOptions.getText().trim());
         if (!opts.isEmpty()) command.append(", ").append(String.join(" ", opts));
         this.currentCommand = estimator;
         this.rebuilding = true;
         this.previewArea.setText(command.toString().trim());
         this.previewArea.setCaretPosition(0);
         this.rebuilding = false;
         this.flashCommandPreview();
      }

      private boolean validateBaselineBeforeRun() {
         String y = selected(this.depvar);
         String x = selected(this.regressX);
         if (y.isBlank() || x.isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择因变量 Y 和核心解释变量 X。", "基准回归设置尚未完整", 1);
            return false;
         }
         if (y.equals(x)) {
            JOptionPane.showMessageDialog(this, "Y 和核心 X 不能是同一个变量。", "变量角色重复", 2);
            return false;
         }
         if (this.regressControls.getSelectedValuesList().contains(y) || this.regressControls.getSelectedValuesList().contains(x)) {
            JOptionPane.showMessageDialog(this, "Controls 中重复选择了 Y 或核心 X。", "变量角色重复", 2);
            return false;
         }
         String estimator = selected(this.baselineEstimator);
         if ("reghdfe".equals(estimator) && this.absorb.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "reghdfe 至少需要选择 1 个固定效应 absorb()。", "固定效应缺失", 1);
            return false;
         }
         if ("areg".equals(estimator) && this.absorb.getSelectedValuesList().size() != 1) {
            JOptionPane.showMessageDialog(this, "areg 需要且只能选择 1 个固定效应 absorb()。", "固定效应设置尚未完整", 1);
            return false;
         }
         if ("cluster".equals(selected(this.vce)) && selected(this.cluster).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择 Cluster 后，请指定聚类变量。", "聚类变量缺失", 1);
            return false;
         }
         if (!"无".equals(selected(this.regressWeightType)) && selected(this.regressWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后，请指定权重变量。", "权重变量缺失", 1);
            return false;
         }
         return true;
      }

      private void showRegressPage() {
         this.baselineTaskActive = false;
         if (this.baselineEstimatorHeader != null) this.baselineEstimatorHeader.setVisible(false);
         this.regressWorkspaceActive = true;
         this.showWorkspacePage();
         this.selectDataView();
         this.currentCommand = "regress";
         this.activeCategoryCode = "reg";
         this.activeCategoryName = "回归模型";
         if (this.activeMethodName.isBlank()) {
            this.activeMethodName = "普通线性回归";
         }

         this.commandDock.setVisible(true);
         this.commandTabs.setVisible(true);
         this.commandTabs.setSelectedIndex(0);
         this.previewArea.setEditable(true);
         this.runButton.setText("运行回归");
         this.setWorkspaceBreadcrumb("回归模型  ›  普通线性回归  ›  regress");
         this.commandTitle.setText("regress - 普通线性回归");
         this.commandTitle.setToolTipText("Stata 官方普通最小二乘回归");
         this.exampleLabel.setText("<html><b>最简单：</b> 选择 Y、核心 X 和控制变量；底部会自动生成 regress 命令。</html>");
         this.insightArea.setText("适合连续因变量的普通最小二乘回归。\n\n先填写最常用的 Y、核心解释变量 X、Controls 和标准误设置。\n\n样本条件、分类变量、交互项、滞后项、权重和其他低频选项统一放在“更多设置”中；底部始终保留真实 Stata 命令。");
         this.syntaxArea.setText("regress depvar indepvars [if] [in] [weight] [, vce(...) beta level(#) noconstant ...]");
         this.refreshRegressVariables(false);

         this.rebuilding = true;
         this.vce.removeAllItems();
         this.vce.addItem("default");
         this.vce.addItem("robust");
         this.vce.addItem("cluster");
         if (selected(this.vce).isBlank()) {
            this.vce.setSelectedItem("default");
         }
         this.rebuilding = false;

         this.formPanel.removeAll();
         int row = 0;
         this.addField(row++, "因变量 Y", this.depvar);
         this.addField(row++, "核心解释变量 X", this.regressX);
         this.addField(row++, "控制变量 Controls（可多选）", this.listPane(this.regressControls));
         this.addField(row++, "标准误", this.vce);
         this.regressClusterFieldBlock = this.addField(row++, "聚类变量", this.cluster);

         JPanel moreSettings = this.buildRegressMoreSettings();
         JToggleButton moreToggle = new JToggleButton("展开更多设置  +");
         styleSecondaryButton(moreToggle);
         moreSettings.setVisible(false);
         moreToggle.addActionListener(event -> {
            boolean expanded = moreToggle.isSelected();
            moreToggle.setText(expanded ? "收起更多设置  −" : "展开更多设置  +");
            moreSettings.setVisible(expanded);
            this.formPanel.revalidate();
            this.formPanel.repaint();
         });

         JPanel moreBlock = new JPanel();
         moreBlock.setOpaque(false);
         moreBlock.setLayout(new BoxLayout(moreBlock, BoxLayout.Y_AXIS));
         moreToggle.setAlignmentX(0.0F);
         moreSettings.setAlignmentX(0.0F);
         moreBlock.add(moreToggle);
         moreBlock.add(Box.createVerticalStrut(7));
         moreBlock.add(moreSettings);
         this.addField(row++, "更多设置", moreBlock);

         GridBagConstraints filler = this.constraints(0, row);
         filler.gridwidth = 2;
         filler.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), filler);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.updateRegressConditionalFields();
         this.updateRegressPreview();
         this.statusLabel.setText("普通线性回归：常用参数在前；需要时再展开更多设置。");
      }

      private JPanel buildRegressTermBuilder() {
         JPanel var1 = new JPanel();
         var1.setOpaque(false);
         var1.setLayout(new BoxLayout(var1, 1));
         JPanel var2 = new JPanel(new BorderLayout(8, 0));
         var2.setOpaque(false);
         JButton var3 = this.secondary("加入分类变量");
         var3.addActionListener(var1x -> {
            String var2x = selected(this.regressFactor);
            if (!var2x.isBlank()) {
               this.addRegressSpecialTerm("i." + var2x);
            }
         });
         var2.add(this.regressFactor, "Center");
         var2.add(var3, "East");
         var1.add(this.labeledInline("分类变量", var2));
         var1.add(Box.createVerticalStrut(8));
         JPanel var4 = new JPanel(new GridLayout(1, 4, 7, 0));
         var4.setOpaque(false);
         var4.add(this.regressInteractionA);
         var4.add(this.regressInteractionB);
         var4.add(this.regressInteractionType);
         JButton var5 = this.secondary("加入交互");
         var5.addActionListener(var1x -> {
            String var2x = selected(this.regressInteractionA);
            String var3x = selected(this.regressInteractionB);
            if (!var2x.isBlank() && !var3x.isBlank() && !var2x.equals(var3x)) {
               this.addRegressSpecialTerm(buildInteractionTerm(var2x, var3x, selected(this.regressInteractionType)));
            } else {
               JOptionPane.showMessageDialog(this, "请选择两个不同变量构造交互项。", "交互项尚未完整", 1);
            }
         });
         var4.add(var5);
         var1.add(this.labeledInline("交互项", var4));
         var1.add(Box.createVerticalStrut(8));
         JPanel var6 = new JPanel(new GridLayout(1, 3, 7, 0));
         var6.setOpaque(false);
         var6.add(this.regressLagVar);
         var6.add(this.regressLagOrder);
         JButton var7 = this.secondary("加入滞后");
         var7.addActionListener(var1x -> {
            String var2x = selected(this.regressLagVar);
            if (!var2x.isBlank()) {
               int var3x = ((Number)this.regressLagOrder.getValue()).intValue();
               this.addRegressSpecialTerm((var3x == 1 ? "L." : "L" + var3x + ".") + var2x);
            }
         });
         var6.add(var7);
         var1.add(this.labeledInline("滞后项（需先 tsset/xtset）", var6));
         var1.add(Box.createVerticalStrut(8));
         this.regressSpecialTerms.setVisibleRowCount(3);
         this.regressSpecialTerms.setSelectionMode(0);
         JPanel var8 = new JPanel(new BorderLayout(7, 0));
         var8.setOpaque(false);
         var8.add(softScroll(this.regressSpecialTerms), "Center");
         JPanel var9 = new JPanel(new GridLayout(0, 1, 0, 6));
         var9.setOpaque(false);
         JButton var10 = this.secondary("删除所选");
         JButton var11 = this.secondary("清空");
         var10.addActionListener(var1x -> {
            int var2x = this.regressSpecialTerms.getSelectedIndex();
            if (var2x >= 0) {
               this.regressSpecialTermsModel.remove(var2x);
            }

            this.updateRegressPreview();
         });
         var11.addActionListener(var1x -> {
            this.regressSpecialTermsModel.clear();
            this.updateRegressPreview();
         });
         var9.add(var10);
         var9.add(var11);
         var8.add(var9, "East");
         var1.add(this.labeledInline("已加入模型", var8));
         return var1;
      }

      private JPanel buildRegressMoreSettings() {
         JPanel panel = new JPanel();
         panel.setOpaque(false);
         panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));

         JPanel sampleRow = new JPanel(new GridLayout(1, 2, 8, 0));
         sampleRow.setOpaque(false);
         sampleRow.add(this.miniLabeled("样本条件 if", this.ifCondition));
         sampleRow.add(this.miniLabeled("观测范围 in", this.inCondition));
         panel.add(sampleRow);
         panel.add(Box.createVerticalStrut(12));

         JLabel termsTitle = new JLabel("分类变量、交互项与滞后项");
         termsTitle.setForeground(MUTED);
         termsTitle.setFont(termsTitle.getFont().deriveFont(Font.BOLD));
         termsTitle.setAlignmentX(0.0F);
         panel.add(termsTitle);
         panel.add(Box.createVerticalStrut(7));
         JPanel termBuilder = this.buildRegressTermBuilder();
         termBuilder.setAlignmentX(0.0F);
         panel.add(termBuilder);
         panel.add(Box.createVerticalStrut(12));

         JPanel weightRow = new JPanel(new GridLayout(1, 2, 8, 0));
         weightRow.setOpaque(false);
         weightRow.add(this.miniLabeled("权重类型", this.regressWeightType));
         weightRow.add(this.miniLabeled("权重变量", this.regressWeightVar));
         this.regressWeightVarFieldBlock = weightRow;
         panel.add(weightRow);
         panel.add(Box.createVerticalStrut(10));

         JPanel reportRow = new JPanel(new GridLayout(1, 3, 8, 0));
         reportRow.setOpaque(false);
         reportRow.add(this.regressNoConstant);
         reportRow.add(this.regressBeta);
         reportRow.add(this.miniLabeled("置信水平", this.regressLevel));
         panel.add(reportRow);
         panel.add(Box.createVerticalStrut(10));
         panel.add(this.labeledInline("其他 Stata options（高级）", this.regressAdvancedOptions));
         return panel;
      }

      private JPanel labeledInline(String var1, JComponent var2) {
         JPanel var3 = new JPanel(new BorderLayout(8, 0));
         var3.setOpaque(false);
         JLabel var4 = new JLabel(var1);
         var4.setForeground(MUTED);
         var4.setPreferredSize(new Dimension(138, 30));
         var3.add(var4, "West");
         var3.add(var2, "Center");
         var3.setMaximumSize(new Dimension(Integer.MAX_VALUE, Math.max(36, var2.getPreferredSize().height + 4)));
         return var3;
      }

      private JPanel miniLabeled(String var1, JComponent var2) {
         JPanel var3 = new JPanel(new BorderLayout(0, 4));
         var3.setOpaque(false);
         JLabel var4 = new JLabel(var1);
         var4.setForeground(MUTED);
         var4.setFont(var4.getFont().deriveFont(10.0F));
         var3.add(var4, "North");
         var3.add(var2, "Center");
         return var3;
      }

      private void refreshRegressVariables(boolean var1) {
         List var2 = this.previewMode ? Arrays.asList("price", "mpg", "weight", "length", "turn", "foreign", "rep78") : HxWorkbench.StataBridge.variableNames();
         Object var3 = this.depvar.getSelectedItem();
         Object var4 = this.regressX.getSelectedItem();
         ArrayList var5 = new ArrayList<>(this.regressControls.getSelectedValuesList());
         replaceComboItems(this.depvar, var2);
         replaceComboItems(this.regressX, var2);
         replaceListItems(this.regressControls, var2);
         replaceComboItems(this.regressFactor, var2);
         replaceComboItems(this.regressInteractionA, var2);
         replaceComboItems(this.regressInteractionB, var2);
         replaceComboItems(this.regressLagVar, var2);
         replaceComboItems(this.regressWeightVar, var2);
         replaceComboItems(this.cluster, var2);
         if (var1) {
            if (var3 != null) {
               this.depvar.setSelectedItem(var3);
            }

            if (var4 != null) {
               this.regressX.setSelectedItem(var4);
            }

            setListSelectedValues(this.regressControls, var5);
         }

         if (selected(this.depvar).isBlank() && !var2.isEmpty()) {
            this.depvar.setSelectedItem(var2.get(0));
         }

         if (selected(this.regressX).isBlank() && var2.size() > 1) {
            this.regressX.setSelectedItem(var2.get(1));
         }
      }

      private void addRegressSpecialTerm(String var1) {
         if (var1 != null && !var1.isBlank()) {
            for (int var2 = 0; var2 < this.regressSpecialTermsModel.size(); var2++) {
               if (var1.equals(this.regressSpecialTermsModel.get(var2))) {
                  return;
               }
            }

            this.regressSpecialTermsModel.addElement(var1);
            if (this.baselineTaskActive) this.updateBaselinePreview();
            else this.updateRegressPreview();
         }
      }

      private static String buildInteractionTerm(String var0, String var1, String var2) {
         String var3 = var2.startsWith("分类") ? "i." + var0 : "c." + var0;
         String var4 = var2.endsWith("分类") ? "i." + var1 : "c." + var1;
         return var3 + "##" + var4;
      }

      private String joinSpecialTerms(String var1) {
         ArrayList var2 = new ArrayList();

         for (int var3 = 0; var3 < this.regressSpecialTermsModel.size(); var3++) {
            var2.add(this.regressSpecialTermsModel.get(var3));
         }

         return String.join(var1, var2);
      }

      private void sanitizeRegressControls() {
         if ((this.regressWorkspaceActive || this.baselineTaskActive) && !this.rebuilding) {
            String var1 = selected(this.depvar);
            String var2 = selected(this.regressX);
            ArrayList var3 = new ArrayList();

            for (String var5 : this.regressControls.getSelectedValuesList()) {
               if (!var5.equals(var1) && !var5.equals(var2)) {
                  var3.add(var5);
               }
            }

            if (var3.size() != this.regressControls.getSelectedValuesList().size()) {
               this.rebuilding = true;
               setListSelectedValues(this.regressControls, var3);
               this.rebuilding = false;
            }
         }
      }

      private void updateRegressConditionalFields() {
         boolean useCluster = "cluster".equalsIgnoreCase(selected(this.vce));
         this.cluster.setEnabled(useCluster);
         if (this.regressClusterFieldBlock != null) {
            this.regressClusterFieldBlock.setVisible(useCluster);
         }

         boolean useWeight = !"无".equals(selected(this.regressWeightType));
         this.regressWeightVar.setEnabled(useWeight);
         this.formPanel.revalidate();
         this.formPanel.repaint();
      }

      private void updateRegressPreview() {
         if (!this.rebuilding && "regress".equals(this.currentCommand)) {
            String var1 = selected(this.depvar);
            String var2 = selected(this.regressX);
            ArrayList<String> var3 = new ArrayList<>(this.regressControls.getSelectedValuesList());
            LinkedHashSet var4 = new LinkedHashSet();
            if (!var2.isBlank()) {
               var4.add(var2);
            }

            for (String var6 : var3) {
               if (!var6.equals(var1) && !var6.equals(var2)) {
                  var4.add(var6);
               }
            }

            for (int var10 = 0; var10 < this.regressSpecialTermsModel.size(); var10++) {
               var4.add(this.regressSpecialTermsModel.get(var10));
            }

            StringBuilder var11 = new StringBuilder("regress");
            if (!var1.isBlank()) {
               var11.append(" ").append(var1);
            }

            if (!var4.isEmpty()) {
               var11.append(" ").append(String.join(" ", var4));
            }

            String var12 = selected(this.regressWeightType);
            String var7 = selected(this.regressWeightVar);
            if (!"无".equals(var12) && !var7.isBlank()) {
               var11.append(" [").append(var12).append("=").append(var7).append("]");
            }

            if (!this.ifCondition.getText().trim().isBlank()) {
               var11.append(" if ").append(this.ifCondition.getText().trim());
            }

            if (!this.inCondition.getText().trim().isBlank()) {
               var11.append(" in ").append(this.inCondition.getText().trim());
            }

            ArrayList var8 = new ArrayList();
            if ("robust".equals(selected(this.vce))) {
               var8.add("vce(robust)");
            } else if ("cluster".equals(selected(this.vce)) && !selected(this.cluster).isBlank()) {
               var8.add("vce(cluster " + selected(this.cluster) + ")");
            }

            if (this.regressNoConstant.isSelected()) {
               var8.add("noconstant");
            }

            if (this.regressBeta.isSelected()) {
               var8.add("beta");
            }

            int var9 = ((Number)this.regressLevel.getValue()).intValue();
            if (var9 != 95) {
               var8.add("level(" + var9 + ")");
            }

            if (!this.regressAdvancedOptions.getText().trim().isBlank()) {
               var8.add(this.regressAdvancedOptions.getText().trim());
            }

            if (!var8.isEmpty()) {
               var11.append(", ").append(String.join(" ", var8));
            }

            this.rebuilding = true;
            this.previewArea.setText(var11.toString());
            this.previewArea.setCaretPosition(0);
            this.rebuilding = false;
            this.flashCommandPreview();
         }
      }

      private boolean validateRegressBeforeRun() {
         String var1 = selected(this.depvar);
         String var2 = selected(this.regressX);
         if (var1.isBlank() || var2.isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择因变量 Y 和核心解释变量 X。", "回归设置尚未完整", 1);
            return false;
         } else if (var1.equals(var2)) {
            JOptionPane.showMessageDialog(this, "Y 和核心 X 不能是同一个变量。", "变量角色重复", 2);
            return false;
         } else if (this.regressControls.getSelectedValuesList().contains(var1) || this.regressControls.getSelectedValuesList().contains(var2)) {
            JOptionPane.showMessageDialog(this, "控制变量中重复选择了 Y 或核心 X，请取消重复项。", "变量角色重复", 2);
            return false;
         } else if ("cluster".equals(selected(this.vce)) && selected(this.cluster).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择 Cluster 后，请指定聚类变量。", "聚类变量缺失", 1);
            return false;
         } else if (!"无".equals(selected(this.regressWeightType)) && selected(this.regressWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后，请指定权重变量。", "权重变量缺失", 1);
            return false;
         } else {
            return true;
         }
      }

      private void showHomePage() {
         this.currentCommand = "";
         this.regressWorkspaceActive = false;
         this.baselineTaskActive = false;
         if (this.baselineEstimatorHeader != null) this.baselineEstimatorHeader.setVisible(false);
         this.searchResultsMode = false;
         this.runButton.setEnabled(false);
         this.homeButton.setEnabled(false);
         this.homeButton.setVisible(false);
         this.inspectorToggle.setVisible(false);
         this.setSidebarActive("home");
         this.stageLayout.show(this.stageCards, "home");
         this.refreshHomeContext();
         this.statusLabel.setText("从常用任务开始，或直接搜索研究任务 / Stata 命令。");
      }


      private JComponent xtregCircleBadge(String text, boolean active, int size) {
         JComponent badge = new JComponent() {
            @Override
            protected void paintComponent(Graphics g0) {
               Graphics2D g = (Graphics2D)g0.create();
               g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
               int d = Math.min(getWidth(), getHeight()) - 2;
               int x = (getWidth() - d) / 2;
               int y = (getHeight() - d) / 2;
               g.setColor(active ? new Color(47, 111, 228) : new Color(239, 243, 248));
               g.fillOval(x, y, d, d);
               if (!active) {
                  g.setColor(new Color(225, 231, 239));
                  g.drawOval(x, y, d - 1, d - 1);
               }
               g.setColor(active ? Color.WHITE : new Color(75, 88, 108));
               g.setFont(getFont().deriveFont(Font.BOLD, size >= 28 ? 12.0F : 10.5F));
               java.awt.FontMetrics fm = g.getFontMetrics();
               int tx = (getWidth() - fm.stringWidth(text)) / 2;
               int ty = (getHeight() - fm.getHeight()) / 2 + fm.getAscent();
               g.drawString(text, tx, ty);
               g.dispose();
            }
         };
         Dimension d = new Dimension(size, size);
         badge.setPreferredSize(d);
         badge.setMinimumSize(d);
         badge.setMaximumSize(d);
         return badge;
      }

      private JPanel xtregWizardCardV130(int step, String title, String subtitle) {
         JPanel card = cardPanel();
         card.setBackground(SURFACE);
         card.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 11),
            new EmptyBorder(12, 14, 12, 14)
         ));
         card.setLayout(new BorderLayout(0, 10));
         card.setMinimumSize(new Dimension(0, 0));

         JPanel header = new JPanel(new BorderLayout(10, 0));
         header.setOpaque(false);
         JComponent badge = this.xtregCircleBadge(Integer.toString(step), true, 28);
         header.add(badge, BorderLayout.WEST);

         JPanel head = new JPanel();
         head.setOpaque(false);
         head.setLayout(new BoxLayout(head, BoxLayout.Y_AXIS));
         JLabel t = new JLabel(title);
         t.setForeground(TEXT);
         t.setFont(t.getFont().deriveFont(Font.BOLD, 13.5F));
         JLabel st = new JLabel("<html>" + html(subtitle) + "</html>");
         st.setForeground(MUTED);
         st.setFont(st.getFont().deriveFont(9.5F));
         st.setMinimumSize(new Dimension(0, 0));
         head.add(t);
         head.add(Box.createVerticalStrut(3));
         head.add(st);
         header.add(head, BorderLayout.CENTER);
         card.add(header, BorderLayout.NORTH);
         return card;
      }

      private JComponent xtregStepStripV130() {
         JPanel strip = cardPanel();
         strip.setBackground(SURFACE);
         strip.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 11),
            new EmptyBorder(9, 10, 9, 10)
         ));
         strip.setLayout(new GridLayout(1, 4, 8, 0));
         String[][] steps = new String[][]{
            {"1", "面板设定", "指定个体与时间维度"},
            {"2", "选择变量", "选择因变量与解释变量"},
            {"3", "估计选项", "模型与标准误设置"},
            {"4", "预览运行", "预览命令并运行估计"}
         };
         for (int i = 0; i < steps.length; i++) {
            JPanel p = new JPanel(new BorderLayout(6, 0));
            p.setOpaque(false);
            p.setMinimumSize(new Dimension(0, 0));
            JComponent n = this.xtregCircleBadge(steps[i][0], i == 0, 24);
            p.add(n, BorderLayout.WEST);
            JLabel label = new JLabel("<html><b>" + html(steps[i][1]) + "</b></html>");
            label.setForeground(TEXT);
            label.setFont(label.getFont().deriveFont(10.5F));
            label.setToolTipText(steps[i][2]);
            label.setMinimumSize(new Dimension(0, 0));
            p.add(label, BorderLayout.CENTER);
            strip.add(p);
         }
         strip.setPreferredSize(new Dimension(0, 52));
         strip.setMinimumSize(new Dimension(0, 52));
         strip.setMaximumSize(new Dimension(Integer.MAX_VALUE, 52));
         return strip;
      }

      private List<String> xtregAvailableVariables() {
         if (this.previewMode) {
            return Arrays.asList("make", "price", "mpg", "rep78", "headroom", "trunk", "weight", "length", "turn", "displacement", "gear_ratio", "foreign");
         }
         return HxWorkbench.StataBridge.variableNames();
      }

      private void refreshXtregVariableControls() {
         if (!"xtreg".equals(this.currentCommand)
            || this.xtregPanelVar == null || this.xtregTimeVar == null
            || this.xtregDepVar == null || this.xtregIndepList == null) return;

         List<String> vars = this.xtregAvailableVariables();
         boolean oldRebuilding = this.rebuilding;
         this.rebuilding = true;
         replaceComboItems(this.xtregPanelVar, vars);
         replaceComboItems(this.xtregTimeVar, vars);
         replaceComboItems(this.xtregDepVar, vars);
         replaceListItems(this.xtregIndepList, vars);
         this.rebuilding = oldRebuilding;
         if (!this.rebuilding && this.xtregPreviewUpdater != null) this.xtregPreviewUpdater.run();
      }

      private void installDataHeaderDragSupport() {
         final javax.swing.table.JTableHeader header = this.dataTable.getTableHeader();
         header.setReorderingAllowed(false);
         header.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         header.setToolTipText("拖动变量名到左侧变量输入框，可直接完成选择");
         header.setTransferHandler(new TransferHandler() {
            @Override
            protected Transferable createTransferable(JComponent c) {
               return WorkbenchFrame.this.draggedDataVariable == null || WorkbenchFrame.this.draggedDataVariable.isBlank()
                  ? null : new StringSelection(WorkbenchFrame.this.draggedDataVariable);
            }

            @Override
            public int getSourceActions(JComponent c) {
               return COPY;
            }
         });

         MouseAdapter dragger = new MouseAdapter() {
            private boolean started;

            @Override
            public void mousePressed(MouseEvent e) {
               int viewColumn = header.columnAtPoint(e.getPoint());
               this.started = false;
               if (viewColumn >= 0) {
                  WorkbenchFrame.this.draggedDataVariable = WorkbenchFrame.this.dataTable.getColumnName(viewColumn);
                  WorkbenchFrame.this.dataTable.setColumnSelectionInterval(viewColumn, viewColumn);
               } else {
                  WorkbenchFrame.this.draggedDataVariable = "";
               }
            }

            @Override
            public void mouseDragged(MouseEvent e) {
               if (!this.started && WorkbenchFrame.this.draggedDataVariable != null && !WorkbenchFrame.this.draggedDataVariable.isBlank()) {
                  this.started = true;
                  header.getTransferHandler().exportAsDrag(header, e, TransferHandler.COPY);
               }
            }

            @Override
            public void mouseReleased(MouseEvent e) {
               this.started = false;
               WorkbenchFrame.this.draggedDataVariable = "";
            }
         };
         header.addMouseListener(dragger);
         header.addMouseMotionListener(dragger);
      }

      private void enableVariableDrop(JComboBox<String> target, String role) {
         target.setToolTipText("可从右侧数据表表头拖入变量：" + role);
         target.setTransferHandler(new TransferHandler() {
            @Override
            public boolean canImport(TransferSupport support) {
               return support.isDataFlavorSupported(DataFlavor.stringFlavor);
            }

            @Override
            public boolean importData(TransferSupport support) {
               if (!canImport(support)) return false;
               try {
                  String variable = ((String)support.getTransferable().getTransferData(DataFlavor.stringFlavor)).trim();
                  for (int i = 0; i < target.getItemCount(); i++) {
                     if (variable.equals(target.getItemAt(i))) {
                        target.setSelectedIndex(i);
                        WorkbenchFrame.this.statusLabel.setText("已将变量 " + variable + " 拖入“" + role + "”。");
                        return true;
                     }
                  }
               } catch (Exception ex) {
                  WorkbenchFrame.this.statusLabel.setText("拖入变量失败：" + ex.getMessage());
               }
               return false;
            }
         });
      }

      private void enableVariableDrop(JList<String> target, String role) {
         target.setToolTipText("可从右侧数据表表头拖入变量：" + role);
         target.setTransferHandler(new TransferHandler() {
            @Override
            public boolean canImport(TransferSupport support) {
               return support.isDataFlavorSupported(DataFlavor.stringFlavor);
            }

            @Override
            public boolean importData(TransferSupport support) {
               if (!canImport(support)) return false;
               try {
                  String variable = ((String)support.getTransferable().getTransferData(DataFlavor.stringFlavor)).trim();
                  ListModel<String> model = target.getModel();
                  for (int i = 0; i < model.getSize(); i++) {
                     if (variable.equals(model.getElementAt(i))) {
                        target.addSelectionInterval(i, i);
                        target.ensureIndexIsVisible(i);
                        WorkbenchFrame.this.statusLabel.setText("已将变量 " + variable + " 拖入“" + role + "”。");
                        return true;
                     }
                  }
               } catch (Exception ex) {
                  WorkbenchFrame.this.statusLabel.setText("拖入变量失败：" + ex.getMessage());
               }
               return false;
            }
         });
      }

      private void showXtregWizardPageV130() {
         this.regressWorkspaceActive = false;
         this.baselineTaskActive = false;
         this.activeCategoryCode = "stats";
         this.activeCategoryName = "统计";
         this.activeMethodName = "纵向/面板数据";
         this.currentCommand = "xtreg";
         this.showWorkspacePage();
         this.syncSidebarFromContext();
         this.selectDataView();
         this.commandDock.setVisible(false);
         this.commandTabs.setVisible(true);
         this.commandTabs.setSelectedIndex(0);
         this.setWorkspaceBreadcrumb("统计  >  纵向/面板数据  >  xtreg");
         this.commandTitle.setText("xtreg · 面板数据回归");
         this.commandTitle.setToolTipText("Stata 官方面板数据回归命令");
         this.exampleLabel.setText("使用 xtreg 进行面板数据回归分析，分四步完成模型设定与估计。");
         this.insightArea.setText("xtreg 用于面板数据模型。先指定面板 ID 与时间变量，再选择因变量、解释变量和 FE/RE 等估计方式。右侧可随时查看当前数据、结果与日志。");
         this.syntaxArea.setText("常用语法：xtset panelvar timevar；xtreg y x1 x2, fe vce(robust)；或 xtreg y x1 x2, re。\n建议：常规企业面板研究可先从固定效应（FE）开始，再按研究设计调整标准误与模型设定。");

         this.formPanel.removeAll();
         this.formPanel.setLayout(new GridBagLayout());
         this.formPanel.setBackground(APP_BG);
         this.formPanel.setBorder(new EmptyBorder(12, 12, 16, 12));

         List<String> vars = this.xtregAvailableVariables();
         String[] choices = new String[vars.size() + 1];
         choices[0] = "";
         for (int i = 0; i < vars.size(); i++) choices[i + 1] = vars.get(i);

         this.xtregPanelVar = new JComboBox<>(choices);
         this.xtregTimeVar = new JComboBox<>(choices);
         this.xtregDepVar = new JComboBox<>(choices);
         DefaultListModel<String> indepModel = new DefaultListModel<>();
         for (String v : vars) indepModel.addElement(v);
         this.xtregIndepList = new JList<>(indepModel);
         JComboBox<String> panelVar = this.xtregPanelVar;
         JComboBox<String> timeVar = this.xtregTimeVar;
         JComboBox<String> dep = this.xtregDepVar;
         JList<String> indep = this.xtregIndepList;
         indep.setSelectionMode(2);
         indep.setVisibleRowCount(4);
         panelVar.setMinimumSize(new Dimension(0, 30));
         timeVar.setMinimumSize(new Dimension(0, 30));
         dep.setMinimumSize(new Dimension(0, 30));
         this.enableVariableDrop(panelVar, "个体变量（面板 ID）");
         this.enableVariableDrop(timeVar, "时间变量");
         this.enableVariableDrop(dep, "因变量（Y）");
         this.enableVariableDrop(indep, "解释变量（X，可多选）");
         JPanel chipZone = new JPanel(new BorderLayout());
         chipZone.setBackground(Color.WHITE);
         chipZone.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(190, 210, 238), 8));
         chipZone.setPreferredSize(new Dimension(220, 72));
         chipZone.setMinimumSize(new Dimension(0, 72));
         JPanel chips = new JPanel(new FlowLayout(FlowLayout.LEFT, 6, 6));
         chips.setOpaque(false);
         JLabel chipHint = new JLabel("将右侧变量拖到这里");
         chipHint.setForeground(MUTED);
         chipHint.setBorder(new EmptyBorder(9, 8, 8, 8));
         Runnable refreshChips = () -> {
            chips.removeAll();
            List<String> selectedVars = indep.getSelectedValuesList();
            if (selectedVars.isEmpty()) {
               chips.add(chipHint);
            } else {
               for (String variable : selectedVars) {
                  JButton chip = new JButton(variable + "  ×");
                  chip.setFocusPainted(false);
                  chip.setBorder(new EmptyBorder(4, 8, 4, 8));
                  chip.setBackground(ACCENT_SOFT);
                  chip.setForeground(TEXT);
                  chip.setToolTipText("点击移除 " + variable);
                  chip.addActionListener(e -> {
                     ListModel<String> model = indep.getModel();
                     for (int i = 0; i < model.getSize(); i++) {
                        if (variable.equals(model.getElementAt(i))) {
                           indep.removeSelectionInterval(i, i);
                           break;
                        }
                     }
                  });
                  chips.add(chip);
               }
            }
            chips.revalidate();
            chips.repaint();
         };
         TransferHandler xDrop = new TransferHandler() {
            @Override public boolean canImport(TransferSupport support) { return support.isDataFlavorSupported(DataFlavor.stringFlavor); }
            @Override public boolean importData(TransferSupport support) {
               if (!canImport(support)) return false;
               try {
                  String variable = ((String)support.getTransferable().getTransferData(DataFlavor.stringFlavor)).trim();
                  ListModel<String> model = indep.getModel();
                  for (int i = 0; i < model.getSize(); i++) {
                     if (variable.equals(model.getElementAt(i))) {
                        indep.addSelectionInterval(i, i);
                        WorkbenchFrame.this.statusLabel.setText("已将变量 " + variable + " 拖入“解释变量 X”。");
                        return true;
                     }
                  }
               } catch (Exception ex) {
                  WorkbenchFrame.this.statusLabel.setText("拖入变量失败：" + ex.getMessage());
               }
               return false;
            }
         };
         chipZone.setTransferHandler(xDrop);
         chips.setTransferHandler(xDrop);
         chipHint.setTransferHandler(xDrop);
         chipZone.add(chips, BorderLayout.CENTER);
         indep.addListSelectionListener(e -> { if (!e.getValueIsAdjusting()) refreshChips.run(); });
         refreshChips.run();

         JRadioButton fe = new JRadioButton("固定效应（FE）", true);
         JRadioButton re = new JRadioButton("随机效应（RE）");
         JRadioButton be = new JRadioButton("between");
         JRadioButton pa = new JRadioButton("population-averaged");
         this.xtregFeButton = fe; this.xtregReButton = re; this.xtregBeButton = be; this.xtregPaButton = pa;
         for (JRadioButton b : Arrays.asList(fe, re, be, pa)) { b.setOpaque(false); b.setForeground(TEXT); }
         ButtonGroup modelGroup = new ButtonGroup();
         modelGroup.add(fe); modelGroup.add(re); modelGroup.add(be); modelGroup.add(pa);
         JComboBox<String> se = new JComboBox<>(new String[]{"稳健标准误", "默认标准误", "按面板聚类"});
         this.xtregSeCombo = se;

         JTextArea commandPreview = new JTextArea();
         this.xtregCommandPreview = commandPreview;
         commandPreview.setEditable(true);
         commandPreview.setRows(2);
         commandPreview.setLineWrap(false);
         commandPreview.setToolTipText("可以直接修改 xtset / xtreg 命令；离开编辑框后，上方设置会自动同步");
         commandPreview.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 12));
         commandPreview.setBackground(new Color(247, 250, 255));
         JScrollPane commandPreviewScroll = softScroll(commandPreview);
         commandPreviewScroll.setPreferredSize(new Dimension(100, 62));
         commandPreviewScroll.setMinimumSize(new Dimension(0, 62));

         Runnable update = () -> {
            String pv = Objects.toString(panelVar.getSelectedItem(), "").trim();
            String tv = Objects.toString(timeVar.getSelectedItem(), "").trim();
            String y = Objects.toString(dep.getSelectedItem(), "").trim();
            List<String> xs = indep.getSelectedValuesList();
            String model = fe.isSelected() ? "fe" : re.isSelected() ? "re" : be.isSelected() ? "be" : "pa";
            StringBuilder xt = new StringBuilder(this.xtregCommandPrefix == null ? "" : this.xtregCommandPrefix);
            xt.append("xtreg");
            if (!y.isBlank()) xt.append(" ").append(y);
            if (this.xtregPreserveCustomX && this.xtregCustomXText != null && !this.xtregCustomXText.isBlank()) {
               xt.append(" ").append(this.xtregCustomXText.trim());
            } else {
               for (String x : xs) xt.append(" ").append(x);
            }
            xt.append(", ").append(model);
            String sem = Objects.toString(se.getSelectedItem(), "");
            if ("稳健标准误".equals(sem)) xt.append(" vce(robust)");
            if ("按面板聚类".equals(sem) && !pv.isBlank()) {
               String cluster = this.xtregClusterVar == null || this.xtregClusterVar.isBlank() ? pv : this.xtregClusterVar.trim();
               xt.append(" vce(cluster ").append(cluster).append(")");
            }
            if (this.xtregExtraOptions != null && !this.xtregExtraOptions.isBlank()) xt.append(" ").append(this.xtregExtraOptions.trim());
            String setup = pv.isBlank() ? "xtset panelvar timevar" : "xtset " + pv + (tv.isBlank() ? "" : " " + tv);
            String shown = setup + "\n" + xt;
            commandPreview.setText(shown);
            this.previewArea.setText(xt.toString());
            this.refreshInspectorRole();
         };
         this.xtregPreviewUpdater = update;
         commandPreview.addFocusListener(new java.awt.event.FocusAdapter() {
            @Override public void focusLost(java.awt.event.FocusEvent e) { WorkbenchFrame.this.syncXtregControlsFromCommand(); }
         });
         panelVar.addActionListener(e -> { if (!this.rebuilding) update.run(); });
         timeVar.addActionListener(e -> { if (!this.rebuilding) update.run(); });
         dep.addActionListener(e -> { if (!this.rebuilding) update.run(); });
         indep.addListSelectionListener(e -> { if (!this.rebuilding && !e.getValueIsAdjusting()) { this.xtregPreserveCustomX = false; this.xtregCustomXText = ""; update.run(); } });
         for (JRadioButton b : Arrays.asList(fe, re, be, pa)) b.addActionListener(e -> { if (!this.rebuilding) update.run(); });
         se.addActionListener(e -> { if (!this.rebuilding) { this.xtregClusterVar = ""; update.run(); } });
         update.run();

         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0; c.gridy = 0; c.weightx = 1.0; c.fill = GridBagConstraints.HORIZONTAL; c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.xtregStepStripV130(), c);

         JPanel step1 = this.xtregWizardCardV130(1, "面板设定（xtset）", "先设置面板结构：指定个体变量（面板 ID）和时间变量（时间维度）。");
         JPanel s1Fields = new JPanel(new GridLayout(1, 2, 12, 0)); s1Fields.setOpaque(false);
         JPanel p1 = new JPanel(new BorderLayout(0, 5)); p1.setOpaque(false); p1.add(new JLabel("<html>个体变量（面板 ID） <span style='color:#2f6fe4'>· 可拖入</span></html>"), BorderLayout.NORTH); p1.add(panelVar, BorderLayout.CENTER);
         JPanel p2 = new JPanel(new BorderLayout(0, 5)); p2.setOpaque(false); p2.add(new JLabel("<html>时间变量 <span style='color:#2f6fe4'>· 可拖入</span></html>"), BorderLayout.NORTH); p2.add(timeVar, BorderLayout.CENTER);
         s1Fields.add(p1); s1Fields.add(p2);
         step1.add(s1Fields, BorderLayout.CENTER);
         JPanel advice1 = new JPanel(); advice1.setBackground(new Color(246, 250, 255)); advice1.setBorder(new EmptyBorder(8, 10, 8, 10));
         advice1.add(new JLabel("建议：企业面板常见设置为 firm + year。"));
         step1.add(advice1, BorderLayout.SOUTH);
         step1.setMinimumSize(new Dimension(0, step1.getPreferredSize().height));
         c.gridy++; this.formPanel.add(step1, c);

         JPanel step2 = this.xtregWizardCardV130(2, "选择变量", "选择因变量和一个或多个解释变量。");
         JPanel s2Fields = new JPanel(new GridLayout(1, 2, 12, 0)); s2Fields.setOpaque(false);
         JPanel p3 = new JPanel(new BorderLayout(0, 5));
         p3.setOpaque(false);
         p3.add(new JLabel("<html>因变量（Y） <span style='color:#2f6fe4'>· 可拖入</span></html>"), BorderLayout.NORTH);
         dep.setPreferredSize(new Dimension(100, 32));
         dep.setMaximumSize(new Dimension(Integer.MAX_VALUE, 32));
         JPanel depWrap = new JPanel();
         depWrap.setOpaque(false);
         depWrap.setLayout(new BoxLayout(depWrap, BoxLayout.Y_AXIS));
         dep.setAlignmentX(0.0F);
         depWrap.add(dep);
         depWrap.add(Box.createVerticalGlue());
         p3.add(depWrap, BorderLayout.CENTER);
         JPanel p4 = new JPanel(new BorderLayout(0, 5)); p4.setOpaque(false); p4.add(new JLabel("<html>解释变量（X，可多选） <span style='color:#2f6fe4'>· 可拖入</span></html>"), BorderLayout.NORTH); p4.add(chipZone, BorderLayout.CENTER);
         s2Fields.add(p3); s2Fields.add(p4);
         step2.add(s2Fields, BorderLayout.CENTER);
         JPanel tip2 = new JPanel(); tip2.setBackground(new Color(244, 252, 248)); tip2.setBorder(new EmptyBorder(8, 10, 8, 10));
         tip2.add(new JLabel("提示：优先从中间“变量窗口”拖入；顶部数据表头也可直接拖入。"));
         step2.add(tip2, BorderLayout.SOUTH);
         step2.setMinimumSize(new Dimension(0, step2.getPreferredSize().height));
         c.gridy++; this.formPanel.add(step2, c);

         JPanel step3 = this.xtregWizardCardV130(3, "估计选项", "选择模型类型与标准误方式，并按需要继续调整高级选项。");
         JPanel s3 = new JPanel(); s3.setOpaque(false); s3.setLayout(new BoxLayout(s3, BoxLayout.Y_AXIS));
         JPanel models = new JPanel(null) {
            private int columns() { return this.getWidth() >= 520 ? 2 : 1; }
            @Override public Dimension getPreferredSize() { return new Dimension(0, this.columns() == 2 ? 62 : 116); }
            @Override public Dimension getMinimumSize() { return new Dimension(0, 116); }
            @Override public void doLayout() {
               int cols = this.columns();
               int rows = cols == 2 ? 2 : 4;
               int gapX = 16, gapY = 3;
               int cellW = Math.max(0, (this.getWidth() - (cols - 1) * gapX) / cols);
               int cellH = Math.max(27, (this.getHeight() - (rows - 1) * gapY) / rows);
               Component[] items = this.getComponents();
               for (int i = 0; i < items.length; i++) {
                  int row = i / cols, col = i % cols;
                  items[i].setBounds(col * (cellW + gapX), row * (cellH + gapY), cellW, cellH);
               }
            }
         };
         models.setOpaque(false);
         models.add(fe); models.add(re); models.add(be); models.add(pa);
         models.addComponentListener(new java.awt.event.ComponentAdapter() {
            @Override public void componentResized(java.awt.event.ComponentEvent e) { models.revalidate(); }
         });
         s3.add(models); s3.add(Box.createVerticalStrut(10));
         JPanel seLine = new JPanel(new BorderLayout(12, 0)); seLine.setOpaque(false); seLine.add(new JLabel("标准误方式"), BorderLayout.WEST); seLine.add(se, BorderLayout.CENTER);
         s3.add(seLine);
         step3.add(s3, BorderLayout.CENTER);
         JPanel tip3 = new JPanel(); tip3.setBackground(new Color(255, 249, 236)); tip3.setBorder(new EmptyBorder(8, 10, 8, 10));
         tip3.add(new JLabel("小贴士：不确定时可先用 FE + 稳健标准误。"));
         step3.add(tip3, BorderLayout.SOUTH);
         step3.setMinimumSize(new Dimension(0, step3.getPreferredSize().height));
         c.gridy++; this.formPanel.add(step3, c);

         JPanel step4 = this.xtregWizardCardV130(4, "预览并运行", "查看将要执行的命令，确认无误后运行模型。");
         JPanel previewWrap = new JPanel(new BorderLayout(10, 0)); previewWrap.setOpaque(false);
         JPanel previewLeft = new JPanel(new BorderLayout(0, 5)); previewLeft.setOpaque(false);
         JLabel commandPreviewLabel = new JLabel("<html>命令预览 <span style='color:#2f6fe4'>· 可编辑，编辑完成后自动同步上方设置</span></html>");
         previewLeft.add(commandPreviewLabel, BorderLayout.NORTH); previewLeft.add(commandPreviewScroll, BorderLayout.CENTER);
         JTextArea syntax = readonlyArea(); syntax.setRows(3); syntax.setText("语法说明\n• xtset：声明面板结构\n• fe / re：固定效应或随机效应\n• vce(robust)：稳健标准误");
         JScrollPane syntaxScroll = softScroll(syntax); syntaxScroll.setPreferredSize(new Dimension(0, 72));
         previewWrap.add(previewLeft, BorderLayout.CENTER); previewWrap.add(syntaxScroll, BorderLayout.SOUTH);
         step4.add(previewWrap, BorderLayout.CENTER);
         JPanel actions = new JPanel(new GridLayout(1, 3, 8, 0)); actions.setOpaque(false);
         JButton prev = this.refButton("上一步", false); prev.addActionListener(e -> this.formScroll.getVerticalScrollBar().setValue(0));
         JButton clear = this.refButton("清空设置", false); clear.addActionListener(e -> { this.xtregClusterVar = ""; this.xtregExtraOptions = ""; this.xtregCustomXText = ""; this.xtregPreserveCustomX = false; this.xtregCommandPrefix = ""; panelVar.setSelectedIndex(0); timeVar.setSelectedIndex(0); dep.setSelectedIndex(0); indep.clearSelection(); fe.setSelected(true); se.setSelectedIndex(0); update.run(); });
         JButton run = this.refButton("运行 xtreg", true);
         run.addActionListener(e -> {
            this.syncXtregControlsFromCommand();
            String pv = Objects.toString(panelVar.getSelectedItem(), "").trim();
            String y = Objects.toString(dep.getSelectedItem(), "").trim();
            String[] edited = this.extractXtregCommands(commandPreview.getText());
            String setup = edited[0];
            String cmd = edited[1];
            if (setup.isBlank() && !pv.isBlank()) {
               String tv = Objects.toString(timeVar.getSelectedItem(), "").trim();
               setup = "xtset " + pv + (tv.isBlank() ? "" : " " + tv);
            }
            if (pv.isBlank() || y.isBlank() || setup.isBlank() || cmd.isBlank() || setup.contains("panelvar")) {
               JOptionPane.showMessageDialog(this, "请至少完成面板 ID、因变量，并保留一条可执行的 xtreg 命令。", "设置尚未完成", JOptionPane.INFORMATION_MESSAGE);
               return;
            }
            int setupRc = HxWorkbench.StataBridge.execute(setup, false);
            if (setupRc != 0) {
               this.statusLabel.setText("xtset 失败，返回码：" + setupRc);
               return;
            }
            this.previewArea.setText(cmd);
            this.executeMonitoredCommand(
               cmd,
               "hxexecute, command(" + HxWorkbench.StataBridge.quote(cmd) + ")",
               false,
               result -> this.statusLabel.setText(
                  result.rc == 0 ? "xtreg 已运行；右侧‘结果’已同步 Stata Results。" : "xtreg 运行失败，返回码：" + result.rc
               )
            );
         });
         actions.add(prev); actions.add(clear); actions.add(run);
         step4.add(actions, BorderLayout.SOUTH);
         step4.setMinimumSize(new Dimension(0, step4.getPreferredSize().height));
         c.gridy++; this.formPanel.add(step4, c);

         c.gridy++; c.weighty = 1.0; c.fill = GridBagConstraints.BOTH;
         this.formPanel.add(Box.createVerticalGlue(), c);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         if (!this.previewMode) {
            long n = Data.getObsTotal();
            int k = Data.getVarCount();
            if (n > 0L && k > 0) this.dataLabel.setText(n + " 行 × " + k + " 列 | 可从中间变量窗口或表头拖入左侧变量框");
         }
         this.statusLabel.setText("xtreg：中间变量窗口是主要选变量入口；可把变量直接拖到 Y / X / 面板 ID / 时间变量。");
      }

      private boolean setXtregComboValue(JComboBox<String> combo, String value) {
         if (combo == null || value == null || value.isBlank()) return false;
         for (int i = 0; i < combo.getItemCount(); i++) {
            if (value.equals(Objects.toString(combo.getItemAt(i), ""))) {
               combo.setSelectedIndex(i);
               return true;
            }
         }
         return false;
      }

      private static String collapseStataContinuation(String raw) {
         if (raw == null) return "";
         return raw.replaceAll("///\\s*\\R\\s*", " ");
      }

      private static String stripStataCommandPrefix(String line) {
         String value = line == null ? "" : line.trim();
         Pattern prefix = Pattern.compile("(?i)^(quietly|qui|capture|cap|noisily|noi)\\s*:?\\s+");
         while (!value.isBlank()) {
            Matcher matcher = prefix.matcher(value);
            if (!matcher.find()) break;
            value = value.substring(matcher.end()).trim();
         }
         return value;
      }

      private String[] extractXtregCommands(String raw) {
         String setup = "";
         String model = "";
         String normalized = collapseStataContinuation(raw);
         for (String line : normalized.split("\\R")) {
            String original = line.trim();
            if (original.isBlank()) continue;
            String core = stripStataCommandPrefix(original);
            String lower = core.toLowerCase(Locale.ROOT);
            if (lower.startsWith("xtset ")) setup = original;
            if (lower.startsWith("xtreg ")) model = original;
         }
         return new String[]{setup, model};
      }

      private static String xtregCore(String command) {
         return stripStataCommandPrefix(command);
      }

      private List<String> xtregBaseVariables(String term) {
         List<String> out = new ArrayList<>();
         if (term == null || term.isBlank()) return out;
         for (String piece : term.split("#+")) {
            String item = piece.trim();
            if (item.isBlank()) continue;
            int dot = item.lastIndexOf('.');
            if (dot >= 0 && dot + 1 < item.length()) item = item.substring(dot + 1);
            item = item.replaceAll("^[()]+|[(),]+$", "");
            if (item.matches("[A-Za-z_][A-Za-z0-9_]*")) out.add(item);
         }
         return out;
      }

      private boolean xtregListContains(String value) {
         if (value == null || this.xtregIndepList == null) return false;
         ListModel<String> model = this.xtregIndepList.getModel();
         for (int i = 0; i < model.getSize(); i++) if (value.equals(model.getElementAt(i))) return true;
         return false;
      }

      private void selectXtregBaseVariable(String value) {
         if (value == null || this.xtregIndepList == null) return;
         ListModel<String> model = this.xtregIndepList.getModel();
         for (int i = 0; i < model.getSize(); i++) {
            if (value.equals(model.getElementAt(i))) {
               this.xtregIndepList.addSelectionInterval(i, i);
               return;
            }
         }
      }

      private void syncXtregControlsFromCommand() {
         if (this.xtregSyncingFromCommand || this.xtregCommandPreview == null
            || this.xtregPanelVar == null || this.xtregTimeVar == null || this.xtregDepVar == null
            || this.xtregIndepList == null || this.xtregFeButton == null || this.xtregSeCombo == null) return;
         String raw = this.xtregCommandPreview.getText() == null ? "" : this.xtregCommandPreview.getText().trim();
         if (raw.isBlank()) return;

         String[] commands = this.extractXtregCommands(raw);
         String xtsetLine = commands[0];
         String xtregLine = commands[1];
         if (xtregLine.isBlank()) {
            this.statusLabel.setText("命令编辑：未找到可执行的 xtreg 命令；上方设置未改变。");
            return;
         }

         String xtregCore = xtregCore(xtregLine);
         boolean oldRebuilding = this.rebuilding;
         this.xtregSyncingFromCommand = true;
         this.rebuilding = true;
         int synced = 0;
         try {
            if (!xtsetLine.isBlank()) {
               String setupCore = stripStataCommandPrefix(xtsetLine);
               String[] parts = setupCore.replaceFirst("(?i)^xtset\\s+", "").trim().split("\\s+");
               this.xtregPanelVar.setSelectedIndex(0);
               this.xtregTimeVar.setSelectedIndex(0);
               if (parts.length >= 1 && this.setXtregComboValue(this.xtregPanelVar, parts[0])) synced++;
               if (parts.length >= 2 && this.setXtregComboValue(this.xtregTimeVar, parts[1])) synced++;
            }

            int keyword = Pattern.compile("(?i)\\bxtreg\\b").matcher(xtregLine).find() ? xtregLine.toLowerCase(Locale.ROOT).indexOf("xtreg") : -1;
            this.xtregCommandPrefix = keyword > 0 ? xtregLine.substring(0, keyword) : "";

            int comma = xtregCore.indexOf(',');
            String lhs = comma >= 0 ? xtregCore.substring(0, comma).trim() : xtregCore.trim();
            String opts = comma >= 0 ? xtregCore.substring(comma + 1).trim() : "";
            String varsText = lhs.replaceFirst("(?i)^xtreg\\s+", "").trim();
            String[] terms = varsText.isBlank() ? new String[0] : varsText.split("\\s+");
            if (terms.length >= 1 && this.setXtregComboValue(this.xtregDepVar, terms[0])) synced++;

            this.xtregIndepList.clearSelection();
            boolean customX = false;
            List<String> rawX = new ArrayList<>();
            for (int t = 1; t < terms.length; t++) {
               String term = terms[t];
               rawX.add(term);
               if (this.xtregListContains(term)) {
                  this.selectXtregBaseVariable(term);
                  synced++;
               } else {
                  customX = true;
                  for (String base : this.xtregBaseVariables(term)) {
                     if (this.xtregListContains(base)) {
                        this.selectXtregBaseVariable(base);
                        synced++;
                     }
                  }
               }
            }
            this.xtregCustomXText = String.join(" ", rawX);
            this.xtregPreserveCustomX = customX;

            String padded = " " + opts.toLowerCase(Locale.ROOT).replaceAll("\\s+", " ") + " ";
            if (Pattern.compile("(^|\\s)fe(\\s|$)").matcher(padded).find()) this.xtregFeButton.setSelected(true);
            else if (Pattern.compile("(^|\\s)re(\\s|$)").matcher(padded).find()) this.xtregReButton.setSelected(true);
            else if (Pattern.compile("(^|\\s)(be|between)(\\s|$)").matcher(padded).find()) this.xtregBeButton.setSelected(true);
            else if (Pattern.compile("(^|\\s)(pa|population-averaged)(\\s|$)").matcher(padded).find()) this.xtregPaButton.setSelected(true);
            synced++;

            Matcher clusterMatcher = Pattern.compile("(?i)vce\\s*\\(\\s*cluster\\s+([^\\s\\)]+)\\s*\\)").matcher(opts);
            if (clusterMatcher.find()) {
               this.xtregClusterVar = clusterMatcher.group(1).trim();
               this.xtregSeCombo.setSelectedItem("按面板聚类");
            } else if (Pattern.compile("(?i)vce\\s*\\(\\s*robust\\s*\\)").matcher(opts).find()) {
               this.xtregClusterVar = "";
               this.xtregSeCombo.setSelectedItem("稳健标准误");
            } else {
               this.xtregClusterVar = "";
               this.xtregSeCombo.setSelectedItem("默认标准误");
            }
            synced++;

            String extras = opts;
            extras = extras.replaceAll("(?i)(^|\\s)(fe|re|be|between|pa|population-averaged)(?=\\s|$)", " ");
            extras = extras.replaceAll("(?i)vce\\s*\\([^\\)]*\\)", " ");
            this.xtregExtraOptions = extras.replaceAll("\\s+", " ").trim();

            this.previewArea.setText(xtregLine);
            this.previewArea.setCaretPosition(0);
            this.refreshInspectorRole();
         } finally {
            this.rebuilding = oldRebuilding;
            this.xtregSyncingFromCommand = false;
         }
         this.statusLabel.setText("已从编辑后的命令同步上方设置（" + synced + " 项）；因子/交互/滞后项与未映射高级选项保持原命令语义。");
      }

      private void openCommandPage(String var1) {
         this.baselineTaskActive = false;
         if ("xtreg".equals(var1)) {
            this.showXtregWizardPageV130();
            return;
         }
         if (this.baselineEstimatorHeader != null) this.baselineEstimatorHeader.setVisible(false);
         this.showWorkspacePage();
         if ("hxconvert".equals(var1)) {
            this.showConvertDtaPage();
         } else if ("缺失值分析".equals(var1)) {
            this.showMissingAnalysisPage();
         } else if (Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_box", "did_trends", "twoway").contains(var1)) {
            this.showSpecialGraphPage(var1);
         } else if ("did_builder".equals(var1)) {
            this.showDidBuilderPage();
         } else if (!"oneclick".equals(var1) && !"oneclick_robustness".equals(var1)) {
            this.showCommand(var1);
         } else {
            this.showOneClickPage(var1);
         }
      }

      private void showSpecialGraphPage(String var1) {
         this.showWorkspacePage();
         this.selectResultView("graph", true);
         this.currentCommand = var1;
         this.commandDock.setVisible(true);
         this.commandTabs.setVisible(true);
         this.commandTabs.setSelectedIndex(0);
         this.previewArea.setEditable(true);
         this.runButton.setText("绘制图形");
         this.runButton.setEnabled(true);
         this.setWorkspaceBreadcrumb(commandPath(var1));
         this.depvar.setSelectedItem(null);
         this.panel.setSelectedItem(null);
         this.time.setSelectedItem(null);
         this.variables.clearSelection();
         this.ifCondition.setText("");
         this.options.setText("");
         this.expression.setText("twoway".equals(var1) ? "(scatter y x) (lfit y x)" : "");
         this.formPanel.removeAll();
         int var2 = 0;
         if (Arrays.asList("histogram", "kdensity").contains(var1)) {
            this.commandTitle.setText(var1 + ("histogram".equals(var1) ? " - 直方图" : " - 核密度图"));
            this.exampleLabel.setText("<html><b>最简单例子：</b> " + var1 + " y</html>");
            this.insightArea.setText("主要意图：观察单个数值变量的分布形状、偏态和尾部。\n\n推荐数据：包含连续或有序数值变量的数据。\n\n优点：回归前快速发现长尾、多峰和异常值。\n\n缺点与注意：分箱或带宽会影响视觉结果，图形主要用于描述与诊断。");
            this.syntaxArea.setText(var1 + " varname [if] [, options]");
            this.addField(var2++, "要观察的变量", this.depvar);
            this.addSpecialGraphAdvancedSettings(var2++, true, "其他图形选项");
         } else if (Arrays.asList("scatter", "lfit").contains(var1)) {
            this.commandTitle.setText(var1 + ("scatter".equals(var1) ? " - 散点图" : " - 线性拟合图"));
            this.exampleLabel.setText("<html><b>最简单例子：</b> twoway " + var1 + " y x</html>");
            this.insightArea
               .setText(
                  "主要意图：观察 Y 与 X 的原始关系"
                     + ("lfit".equals(var1) ? "和线性拟合方向。" : "、离群点与可能的非线性。")
                     + "\n\n推荐数据：至少包含两个数值变量。\n\n优点：关系直观，适合核对模型设定。\n\n缺点与注意：图中关系是条件相关，不能自动解释为因果效应。"
               );
            this.syntaxArea.setText("twoway " + var1 + " y x [if] [, options]");
            this.addField(var2++, "纵轴变量 Y", this.depvar);
            this.addField(var2++, "横轴变量 X（选择一个）", this.listPane(this.variables));
            this.addSpecialGraphAdvancedSettings(var2++, true, "其他图形选项");
         } else if ("graph_box".equals(var1)) {
            this.commandTitle.setText("graph box - 分布与异常值箱线图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> graph box y, over(group)</html>");
            this.insightArea.setText("主要意图：观察变量分布、中位数、四分位距和潜在异常值。\n\n推荐数据：包含数值型结果变量；分组比较时再选择类别变量。\n\n优点：组间分布差异直观。\n\n缺点与注意：箱线图是描述性图形，分组样本过少时不稳定。");
            this.syntaxArea.setText("graph box y [, over(group) options]");
            this.addField(var2++, "要观察的变量", this.depvar);
            this.addField(var2++, "分组变量（可选）", this.panel);
            this.addSpecialGraphAdvancedSettings(var2++, true, "其他图形选项");
         } else if ("did_trends".equals(var1)) {
            this.commandTitle.setText("处理组 / 对照组趋势图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> hxtrendplot y, group(treat) time(year)</html>");
            this.insightArea
               .setText("主要意图：比较处理组与对照组在政策前后的平均结果走势。\n\n推荐数据：含结果变量、时间变量和 0/1 处理组变量的面板或重复截面数据。\n\n优点：平行趋势和动态变化一眼可见。\n\n缺点与注意：趋势图用于诊断；正式 DID 仍要明确处理时点、基准期和识别假设。");
            this.syntaxArea.setText("hxtrendplot y [if], group(treat) time(year) [policy(#) options()]");
            this.addField(var2++, "结果变量 Y", this.depvar);
            this.addField(var2++, "处理组变量（建议 0/1）", this.panel);
            this.addField(var2++, "时间变量", this.time);
            this.addSpecialGraphAdvancedSettings(var2++, true, "政策时点或其他选项");
         } else {
            this.commandTitle.setText("twoway - 自定义叠加图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> twoway (scatter y x) (lfit y x)</html>");
            this.insightArea.setText("主要意图：自由组合散点、拟合线、置信区间和其他二维图层。\n\n推荐数据：包含要绘制的数值型横轴和纵轴变量。\n\n优点：表达能力强，适合论文图形。\n\n缺点与注意：图层表达式需要遵循 Stata twoway 语法，可先从示例修改。");
            this.syntaxArea.setText("twoway (plottype ...) (plottype ...) [, options]");
            if (this.expression.getText().isBlank()) {
               this.expression.setText("(scatter y x) (lfit y x)");
            }

            this.addField(var2++, "图层表达式", this.expression);
            this.addSpecialGraphAdvancedSettings(var2++, false, "其他图形选项");
         }

         GridBagConstraints var3 = this.constraints(0, var2);
         var3.gridwidth = 2;
         var3.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), var3);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.updateSpecialGraphPreview();
         this.statusLabel.setText("图形页面已就绪；右侧“图形预览”会随变量选择更新。");
      }


      private void addSpecialGraphAdvancedSettings(int row, boolean includeIf, String optionLabel) {
         JPanel content = new JPanel();
         content.setOpaque(false);
         content.setLayout(new BoxLayout(content, BoxLayout.Y_AXIS));
         if (includeIf) {
            content.add(this.labeledInline("样本条件 if", this.ifCondition));
            content.add(Box.createVerticalStrut(8));
         }
         content.add(this.labeledInline(optionLabel, this.options));
         content.setVisible(false);
         JToggleButton toggle = new JToggleButton("展开更多设置  +");
         styleSecondaryButton(toggle);
         toggle.addActionListener(event -> {
            boolean expanded = toggle.isSelected();
            toggle.setText(expanded ? "收起更多设置  −" : "展开更多设置  +");
            content.setVisible(expanded);
            this.formPanel.revalidate();
            this.formPanel.repaint();
         });
         JPanel block = new JPanel();
         block.setOpaque(false);
         block.setLayout(new BoxLayout(block, BoxLayout.Y_AXIS));
         toggle.setAlignmentX(0.0F);
         content.setAlignmentX(0.0F);
         block.add(toggle);
         block.add(Box.createVerticalStrut(7));
         block.add(content);
         this.addField(row, "更多设置", block);
      }



      private void chooseExactOneClickValues(JList<String> source, JTextField display, String title) {
         DefaultListModel<String> model=new DefaultListModel<>();
         for(int i=0;i<source.getModel().getSize();i++) model.addElement(source.getModel().getElementAt(i));
         JList<String> list=new JList<>(model); list.setSelectionMode(2); list.setVisibleRowCount(Math.min(10,Math.max(4,model.size()))); setListSelectedValues(list,source.getSelectedValuesList());
         int rc=JOptionPane.showConfirmDialog(this,softScroll(list),title,JOptionPane.OK_CANCEL_OPTION,JOptionPane.PLAIN_MESSAGE);
         if(rc==JOptionPane.OK_OPTION){ setListSelectedValues(source,list.getSelectedValuesList()); display.setText(String.join("  ",list.getSelectedValuesList())); this.updateOneClickPreview(); }
      }

      private JComponent exactEmptyDataIllustration() {
         return new JComponent(){
            @Override protected void paintComponent(Graphics g0){
               super.paintComponent(g0); Graphics2D g=(Graphics2D)g0.create(); g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
               int w=getWidth(),h=getHeight(); int cx=w/2;
               g.setColor(new Color(242,247,255)); g.fillOval(cx-86,h/2-45,172,92);
               g.setColor(new Color(219,234,255)); g.fillRoundRect(cx-56,h/2-2,112,45,11,11);
               g.setColor(new Color(86,149,245)); g.fillRoundRect(cx-45,h/2-20,90,62,10,10);
               g.setColor(new Color(119,174,248)); g.fillRoundRect(cx-57,h/2-29,53,23,7,7);
               g.setColor(Color.WHITE); g.fillRect(cx-19,h/2-40,35,35); g.setColor(new Color(182,205,241)); g.drawLine(cx-14,h/2-29,cx+10,h/2-29); g.drawLine(cx-14,h/2-22,cx+8,h/2-22); g.drawLine(cx-14,h/2-15,cx+4,h/2-15);
               g.setColor(new Color(67,132,239)); int[] xs={cx+58,cx+86,cx+68}; int[] ys={h/2-46,h/2-61,h/2-31}; g.fillPolygon(xs,ys,3);
               g.setStroke(new BasicStroke(1.4f,BasicStroke.CAP_ROUND,BasicStroke.JOIN_ROUND,1f,new float[]{5f,5f},0f)); g.drawArc(cx+20,h/2-40,55,38,190,170);
               g.dispose();
            }
         };
      }

      private JComponent buildExactOneClickContainer() {
         JPanel root = new JPanel(new BorderLayout(14,0));
         root.setBackground(APP_BG);
         root.setBorder(new EmptyBorder(16,20,16,18));
         this.exactOneClickRoot = root;

         JPanel left = new JPanel(new BorderLayout(0,12));
         left.setOpaque(false);
         JPanel header = new JPanel(new BorderLayout());
         header.setOpaque(false);
         JPanel heading = new JPanel();
         heading.setOpaque(false);
         heading.setLayout(new BoxLayout(heading, BoxLayout.Y_AXIS));
         JLabel crumb = new JLabel("首页 / OneClick / oneclick");
         crumb.setForeground(new Color(91,111,144));
         crumb.setFont(crumb.getFont().deriveFont(10.5F));
         JLabel title = new JLabel("OneClick");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD,22.0F));
         heading.add(crumb);
         heading.add(Box.createVerticalStrut(5));
         heading.add(title);
         header.add(heading, BorderLayout.WEST);
         JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT,7,0));
         actions.setOpaque(false);
         JButton back = this.refButton("← 上一级", false); back.addActionListener(e -> this.browseMethodCategory("oneclick"));
         JButton home = this.refButton("首页", false); home.addActionListener(e -> this.showHomePage());
         JButton help = this.refButton("帮助", false); help.addActionListener(e -> this.openHelp());
         actions.add(back); actions.add(home); actions.add(help);
         header.add(actions, BorderLayout.EAST);
         left.add(header, BorderLayout.NORTH);

         JPanel form = new JPanel();
         form.setOpaque(false);
         form.setLayout(new BoxLayout(form, BoxLayout.Y_AXIS));
         JPanel settings = this.refCard();
         settings.setLayout(new BoxLayout(settings, BoxLayout.Y_AXIS));
         JLabel st = new JLabel("参数设置");
         st.setForeground(TEXT);
         st.setFont(st.getFont().deriveFont(Font.BOLD,13.0F));
         st.setAlignmentX(0.0F);
         settings.add(st);
         settings.add(Box.createVerticalStrut(10));

         styleCombo(this.oneClickY); styleCombo(this.oneClickX); styleCombo(this.oneClickP); styleCombo(this.oneClickEstimator);
         styleTextField(this.exactOneClickModelOptions); styleTextField(this.exactOneClickOtherOptions);
         styleTextField(this.exactOneClickCandidatesDisplay); styleTextField(this.exactOneClickRequiredDisplay);
         this.exactOneClickCandidatesDisplay.setEditable(false); this.exactOneClickRequiredDisplay.setEditable(false);

         JPanel yx = new JPanel(new GridLayout(1,4,10,0)); yx.setOpaque(false);
         yx.add(new JLabel("Y")); yx.add(this.oneClickY); yx.add(new JLabel("X")); yx.add(this.oneClickX);
         yx.setMaximumSize(new Dimension(Integer.MAX_VALUE,34)); settings.add(yx); settings.add(Box.createVerticalStrut(10));

         JPanel candidates = new JPanel(new BorderLayout(10,0)); candidates.setOpaque(false);
         JLabel lc = new JLabel("Candidates"); lc.setPreferredSize(new Dimension(110,28)); candidates.add(lc,BorderLayout.WEST);
         candidates.add(this.exactOneClickCandidatesDisplay,BorderLayout.CENTER);
         JButton cp=this.refButton("选择",false); cp.addActionListener(e->this.chooseExactOneClickValues(this.oneClickCandidates,this.exactOneClickCandidatesDisplay,"选择候选控制变量")); candidates.add(cp,BorderLayout.EAST);
         candidates.setMaximumSize(new Dimension(Integer.MAX_VALUE,34)); settings.add(candidates); settings.add(Box.createVerticalStrut(10));

         JPanel required = new JPanel(new BorderLayout(10,0)); required.setOpaque(false);
         JLabel lr = new JLabel("fix()" ); lr.setPreferredSize(new Dimension(110,28)); required.add(lr,BorderLayout.WEST);
         required.add(this.exactOneClickRequiredDisplay,BorderLayout.CENTER);
         JButton rp=this.refButton("选择",false); rp.addActionListener(e->this.chooseExactOneClickValues(this.oneClickRequired,this.exactOneClickRequiredDisplay,"选择固定变量")); required.add(rp,BorderLayout.EAST);
         required.setMaximumSize(new Dimension(Integer.MAX_VALUE,34)); settings.add(required); settings.add(Box.createVerticalStrut(10));

         JPanel pm = new JPanel(new GridLayout(1,4,10,0)); pm.setOpaque(false);
         pm.add(new JLabel("p()")); pm.add(this.oneClickP); pm.add(new JLabel("method")); pm.add(this.oneClickEstimator);
         pm.setMaximumSize(new Dimension(Integer.MAX_VALUE,34)); settings.add(pm); settings.add(Box.createVerticalStrut(10));

         JPanel opts = new JPanel(new GridLayout(1,4,10,0)); opts.setOpaque(false);
         opts.add(new JLabel("o()")); opts.add(this.exactOneClickModelOptions); opts.add(new JLabel("z")); opts.add(this.exactOneClickOtherOptions);
         opts.setMaximumSize(new Dimension(Integer.MAX_VALUE,34)); settings.add(opts);
         settings.setAlignmentX(0.0F);
         settings.setMaximumSize(new Dimension(Integer.MAX_VALUE, 250));
         form.add(settings);
         form.add(Box.createVerticalStrut(12));

         JPanel command = this.refCard();
         command.setLayout(new BorderLayout(10,8));
         JLabel ctitle=new JLabel("Stata 命令"); ctitle.setForeground(TEXT); ctitle.setFont(ctitle.getFont().deriveFont(Font.BOLD,12.0F)); command.add(ctitle,BorderLayout.NORTH);
         this.exactOneClickCommand.setEditable(false); this.exactOneClickCommand.setLineWrap(true); this.exactOneClickCommand.setWrapStyleWord(true);
         this.exactOneClickCommand.setBackground(new Color(244,248,255)); this.exactOneClickCommand.setForeground(TEXT); this.exactOneClickCommand.setFont(new Font("Monospaced",Font.PLAIN,11)); this.exactOneClickCommand.setBorder(new EmptyBorder(9,10,9,10));
         JScrollPane cs=softScroll(this.exactOneClickCommand); cs.setPreferredSize(new Dimension(100,70)); command.add(cs,BorderLayout.CENTER);
         JPanel ca = new JPanel(new FlowLayout(FlowLayout.RIGHT,7,0)); ca.setOpaque(false);
         JButton copy=this.refButton("复制命令",false); copy.addActionListener(e->{ Toolkit.getDefaultToolkit().getSystemClipboard().setContents(new StringSelection(this.exactOneClickCommand.getText()),null); });
         JButton run=this.refButton("运行 OneClick",true); run.addActionListener(e->this.runOneClick()); ca.add(copy); ca.add(run); command.add(ca,BorderLayout.SOUTH);
         command.setAlignmentX(0.0F); command.setMaximumSize(new Dimension(Integer.MAX_VALUE,145)); form.add(command);

         HxWorkbench.SimpleDocumentListener exactListener = new HxWorkbench.SimpleDocumentListener(() -> this.updateOneClickPreview());
         this.exactOneClickModelOptions.getDocument().addDocumentListener(exactListener);
         this.exactOneClickOtherOptions.getDocument().addDocumentListener(exactListener);

         JScrollPane formScroll = softScroll(form); formScroll.setBorder(null); formScroll.getVerticalScrollBar().setUnitIncrement(18);
         left.add(formScroll, BorderLayout.CENTER);
         root.add(left, BorderLayout.CENTER);

         this.exactOneClickInspectorHost.removeAll();
         this.exactOneClickInspectorHost.setOpaque(false);
         this.exactOneClickInspectorHost.setPreferredSize(new Dimension(410,0));
         root.add(this.exactOneClickInspectorHost, BorderLayout.EAST);
         return root;
      }

      private void showOneClickPage(String var1) {
         this.currentCommand = var1;
         this.activeCategoryCode = "oneclick";
         this.activeCategoryName = "OneClick 专区";
         this.activeMethodName = "oneclick_robustness".equals(var1) ? "控制变量组合稳健性" : "控制变量组合筛选";
         this.regressWorkspaceActive = false;
         this.baselineTaskActive = false;
         this.refreshVariableControls();
         this.syncSidebarFromContext();
         this.setSidebarActive("oneclick");
         if (!this.previewMode) {
            HxWorkbench.StataBridge.execute("quietly hxresolve " + var1, false);
            this.offerOptionalDependency(var1);
         }
         this.stageLayout.show(this.stageCards, "oneclick_exact");
         this.attachSharedInspectorToOneClick();
         this.selectDataView();
         this.updateOneClickConditionalFields();
         this.updateOneClickPreview();
         this.statusLabel.setText("OneClick 页面已就绪：只显示当前回归方法真正需要的设置。");
      }

      private void updateOneClickConditionalFields() {
         boolean var1 = "oneclick_robustness".equals(this.currentCommand);
         boolean var2 = "reghdfe".equals(selected(this.oneClickEstimator));
         boolean var3 = "cluster".equals(selected(this.oneClickVce));
         if (this.oneClickAbsorbFieldBlock != null) {
            this.oneClickAbsorbFieldBlock.setVisible(!var1 && var2);
         }

         if (this.oneClickClusterFieldBlock != null) {
            this.oneClickClusterFieldBlock.setVisible(!var1 && var3);
         }

         this.formPanel.revalidate();
         this.formPanel.repaint();
      }

      private void showDidBuilderPage() {
         this.showWorkspacePage();
         this.selectResultView("general", false);
         this.selectDataView();
         this.currentCommand = "did_builder";
         this.commandDock.setVisible(true);
         this.commandTabs.setVisible(true);
         this.commandTabs.setSelectedIndex(0);
         this.previewArea.setEditable(true);
         this.runButton.setText("运行当前步骤");
         this.runButton.setEnabled(true);
         this.setWorkspaceBreadcrumb(commandPath("did_builder"));
         this.commandTitle.setText("DID 与事件研究 - 统一政策时点 · 分步构建");
         this.exampleLabel.setText("<html><b>操作逻辑：</b> 先选当前要做的一步；页面只显示这一步真正需要的变量。</html>");
         this.insightArea
            .setText(
               "当前构建器适用于处理组在同一政策时点进入处理的 DID / Event Study。\n\n个体、时间、处理组、post、event_time 和 event_code 各自独立；treat/post 会在运行前检查是否为 0/1。\n\nevent_time 保留直观的 -3、-2、-1、0、1…；event_code 自动转换成 Stata 因子变量可接受的非负编码。\n\n分期处理（staggered DID）需要专门方法，当前页面不会把它自动当作共同政策时点 DID 运行。"
            );
         this.syntaxArea
            .setText(
               "常用步骤：\ngenerate post = year >= 2020\ngenerate did = treat * post\ngenerate event_time = year - 2020\nhxdidencode event_time, generate(event_code) base(-1)\nreghdfe y i.treat##i.post controls, absorb(firm year) vce(cluster firm)\nreghdfe y i.treat##i.event_code controls, absorb(firm year) vce(cluster firm)\ntestparm 1.treat#<政策前事件期编码>.event_code"
            );
         this.chooseFirstExisting(this.didUnit, "firm", "firmid", "id", "stkcd", "company_id");
         this.chooseFirstExisting(this.didTime, "year", "time", "t");
         this.chooseFirstExisting(this.didTreat, "treat", "treated", "treatment");
         this.chooseFirstExisting(this.didPost, "post");
         this.chooseFirstExisting(this.didEvent, "event_time");
         this.chooseFirstExisting(this.didEventCode, "event_code");
         this.rebuilding = true;
         String var1 = selected(this.vce);
         this.vce.removeAllItems();
         this.vce.addItem("default");
         this.vce.addItem("robust");
         this.vce.addItem("cluster");
         if (!var1.isBlank() && !"default".equals(var1)) {
            this.vce.setSelectedItem(var1);
         } else {
            this.vce.setSelectedItem("cluster");
         }

         if ("cluster".equals(selected(this.vce)) && selected(this.cluster).isBlank() && !selected(this.didUnit).isBlank()) {
            this.cluster.setSelectedItem(selected(this.didUnit));
         }

         this.rebuilding = false;
         String var2 = selected(this.didAction);
         this.formPanel.removeAll();
         int var15 = 0;
         this.addField(var15++, "当前只做哪一步", this.didAction);
         if (var2.startsWith("生成政策后")) {
            if (this.didNewVar.getText().isBlank()) {
               this.didNewVar.setText("post");
            }

            JPanel var4 = new JPanel(new GridLayout(1, 3, 9, 0));
            var4.setOpaque(false);
            var4.add(this.labeled("时间变量（如 year）", this.didTime));
            var4.add(this.labeled("政策发生年份", this.didPolicyTime));
            var4.add(this.labeled("新变量名", this.didNewVar));
            this.addField(var15++, "生成 post", var4);
         } else if (var2.startsWith("生成交互项")) {
            if (this.didNewVar.getText().isBlank()) {
               this.didNewVar.setText("did");
            }

            JPanel var21 = new JPanel(new GridLayout(1, 3, 9, 0));
            var21.setOpaque(false);
            var21.add(this.labeled("处理组变量 treat（0/1）", this.didTreat));
            var21.add(this.labeled("政策后变量 post（0/1）", this.didPost));
            var21.add(this.labeled("新变量名", this.didNewVar));
            this.addField(var15++, "生成 did", var21);
         } else if (var2.startsWith("生成相对")) {
            if (this.didNewVar.getText().isBlank()) {
               this.didNewVar.setText("event_time");
            }

            JPanel var22 = new JPanel(new GridLayout(1, 3, 9, 0));
            var22.setOpaque(false);
            var22.add(this.labeled("时间变量（如 year）", this.didTime));
            var22.add(this.labeled("政策发生年份", this.didPolicyTime));
            var22.add(this.labeled("新变量名", this.didNewVar));
            this.addField(var15++, "生成 event_time", var22);
         } else if (var2.startsWith("生成事件研究编码")) {
            if (this.didNewVar.getText().isBlank() || Arrays.asList("post", "did", "event_time").contains(this.didNewVar.getText().trim())) {
               this.didNewVar.setText("event_code");
            }

            JPanel var23 = new JPanel(new GridLayout(1, 3, 9, 0));
            var23.setOpaque(false);
            var23.add(this.labeled("相对政策时间 event_time", this.didEvent));
            var23.add(this.labeled("基准期（原始相对时间）", this.didBasePeriod));
            var23.add(this.labeled("新编码变量名", this.didNewVar));
            this.addField(var15++, "生成可用于回归的 event_code", var23);
            JLabel var5 = new JLabel("工具会先确认所选基准期确实存在，再自动平移编码；你不需要自己计算编码值。");
            var5.setForeground(MUTED);
            this.addField(var15++, "为什么需要这一步", var5);
         } else if (var2.startsWith("DID 交互回归")) {
            JPanel var24 = new JPanel(new GridLayout(1, 3, 9, 0));
            var24.setOpaque(false);
            var24.add(this.labeled("结果变量 Y", this.depvar));
            var24.add(this.labeled("处理组 treat（0/1）", this.didTreat));
            var24.add(this.labeled("政策后 post（0/1）", this.didPost));
            this.addField(var15++, "DID 核心变量", var24);
            var15 = this.addDidPanelStructure(var15);
            this.addField(var15++, "控制变量（可多选）", this.listPane(this.variables));
            this.addDidModelSettings(var15++);
            this.addField(var15++, "样本条件 if（可选）", this.ifCondition);
            this.addField(var15++, "更多估计选项（可选）", this.options);
         } else if (var2.startsWith("事件研究回归")) {
            JPanel var25 = new JPanel(new GridLayout(1, 3, 9, 0));
            var25.setOpaque(false);
            var25.add(this.labeled("结果变量 Y", this.depvar));
            var25.add(this.labeled("处理组 treat（0/1）", this.didTreat));
            var25.add(this.labeled("事件研究编码 event_code", this.didEventCode));
            this.addField(var15++, "事件研究核心变量", var25);
            var15 = this.addDidPanelStructure(var15);
            JLabel var28 = new JLabel("event_code 请先用上一步生成；基准期已经写入变量设置，回归时无需再次手算。");
            var28.setForeground(MUTED);
            this.addField(var15++, "基准期说明", var28);
            this.addField(var15++, "控制变量（可多选）", this.listPane(this.variables));
            this.addDidModelSettings(var15++);
            this.addField(var15++, "样本条件 if（可选）", this.ifCondition);
            this.addField(var15++, "更多估计选项（可选）", this.options);
         } else {
            JPanel var26 = new JPanel(new GridLayout(1, 2, 9, 0));
            var26.setOpaque(false);
            var26.add(this.labeled("处理组 treat（0/1）", this.didTreat));
            var26.add(this.labeled("事件研究编码 event_code", this.didEventCode));
            this.addField(var15++, "自动识别政策前交互项", var26);
            JLabel var29 = new JLabel("工具会根据之前生成 event_code 时记录的 event_time、平移量和基准期，自动生成 testparm；无需复制系数名。");
            var29.setForeground(MUTED);
            this.addField(var15++, "检验说明", var29);
         }

         GridBagConstraints var27 = this.constraints(0, var15);
         var27.gridwidth = 2;
         var27.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), var27);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.updateDidBuilderPreview();
         this.statusLabel.setText("DID 当前只显示本步骤需要的字段；共同政策时点设定下，常用双向固定效应和按个体聚类已作为默认项。");
      }

      private int addDidPanelStructure(int var1) {
         JPanel var2 = new JPanel(new GridLayout(1, 2, 9, 0));
         var2.setOpaque(false);
         var2.add(this.labeled("个体变量（如 firm）", this.didUnit));
         var2.add(this.labeled("时间变量（如 year）", this.didTime));
         this.addField(var1++, "面板结构", var2);
         JPanel var3 = new JPanel(new FlowLayout(0, 14, 0));
         var3.setOpaque(false);
         var3.add(this.didUnitFE);
         var3.add(this.didTimeFE);
         this.addField(var1++, "常用固定效应", var3);
         return var1;
      }

      private void addDidModelSettings(int var1) {
         boolean var2 = "cluster".equals(selected(this.vce));
         JPanel var3 = new JPanel(new GridLayout(1, var2 ? 3 : 2, 9, 0));
         var3.setOpaque(false);
         var3.add(this.labeled("估计方法", this.didEstimator));
         var3.add(this.labeled("标准误", this.vce));
         if (var2) {
            var3.add(this.labeled("聚类变量", this.cluster));
         }

         this.addField(var1, "回归设置", var3);
      }

      private JComponent labeled(String var1, JComponent var2) {
         JPanel var3 = new JPanel(new BorderLayout(0, 5));
         var3.setOpaque(false);
         JLabel var4 = new JLabel(var1);
         var4.setForeground(MUTED);
         var3.add(var4, "North");
         var3.add(var2, "Center");
         return var3;
      }

      private void offerOptionalDependency(String var1) {
         if (OPTIONAL_DEPENDENCIES.contains(var1)
            && !"1".equals(HxWorkbench.StataBridge.characteristic("hxtoolbox_resolve_installed_flag"))
            && !this.declinedDependencies.contains(var1)) {
            int var2 = JOptionPane.showConfirmDialog(this, var1 + " 尚未安装。\n现在从 SSC 安装它及所需依赖吗？", "安装可选命令", 0, 3);
            if (var2 != 0) {
               this.declinedDependencies.add(var1);
            } else {
               this.setBusy(true, "正在安装 " + var1 + "…");
               int var3 = HxWorkbench.StataBridge.execute("hxdependency install " + var1, false);
               if (var3 == 0) {
                  HxWorkbench.StataBridge.execute("quietly hxresolve " + var1 + ", refresh", false);
                  JOptionPane.showMessageDialog(this, var1 + " 已安装。", "安装完成", 1);
               } else {
                  this.declinedDependencies.add(var1);
                  JOptionPane.showMessageDialog(this, "安装未完成，Stata 返回码 " + var3 + "。\n命令资料页仍可查看。", "安装失败", 2);
               }
            }
         }
      }

      private void rebuildForm() {
         this.rebuilding = true;
         this.formPanel.removeAll();
         this.depvar.setSelectedItem(null);
         this.panel.setSelectedItem(null);
         this.time.setSelectedItem(null);
         this.cluster.setSelectedItem(null);
         this.genericWeightType.setSelectedItem("无");
         this.genericWeightVar.setSelectedItem(null);
         this.variables.clearSelection();
         this.absorb.clearSelection();
         this.endog.clearSelection();
         this.instruments.clearSelection();
         this.newvar.setText("");
         this.expression.setText("");
         this.usingFile.setText("");
         this.ifCondition.setText("");
         this.inCondition.setText("");
         this.options.setText("");
         this.refreshVariableControls();
         this.absorb.setSelectionMode("areg".equals(this.currentCommand) ? 0 : 2);
         String defaultExpression = visibleText(HxWorkbench.StataBridge.characteristic("hxtoolbox_sem_default_expression"));
         if (!defaultExpression.isBlank()) {
            this.expression.setText(defaultExpression);
         }
         this.model.removeAllItems();

         for (String var2 : HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_schema_models"))) {
            this.model.addItem(var2);
         }

         String var3 = visibleText(HxWorkbench.StataBridge.characteristic("hxtoolbox_schema_default_model"));
         if (!var3.isBlank() && comboContains(this.model, var3)) {
            this.model.setSelectedItem(var3);
         }

         this.vce.removeAllItems();
         this.vce.addItem("default");

         for (String var8 : HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_schema_vces"))) {
            if (!"default".equals(var8)) {
               this.vce.addItem(var8);
            }
         }

         if (this.flag("has_cluster") && !comboContains(this.vce, "cluster")) {
            this.vce.addItem("cluster");
         }

         int var4 = 0;
         if (this.flag("has_depvar")) {
            this.addField(var4++, this.sem("dep_label"), this.depvar);
         }

         if (this.flag("has_varlist")) {
            this.addField(var4++, this.sem("vars_label"), this.listPane(this.variables));
         }

         if (this.flag("has_newvar")) {
            this.addField(var4++, this.sem("newvar_label"), this.newvar);
         }

         if (this.flag("has_expression")) {
            this.addField(var4++, this.sem("expr_label"), this.expression);
         }

         if (this.flag("has_iv")) {
            this.addField(var4++, this.sem("endog_label"), this.listPane(this.endog));
            this.addField(var4++, this.sem("inst_label"), this.listPane(this.instruments));
         }

         if (this.model.getItemCount() > 0) {
            this.addField(var4++, this.sem("model_label"), this.model);
         }

         if (this.flag("has_using")) {
            this.usingLabel.setText(this.sem("using_label"));
            this.addField(var4++, this.usingLabel.getText(), this.usingChooser());
         }

         if (this.flag("needs_panel") && !Arrays.asList(
            "reghdfe", "ppmlhdfe", "ivreghdfe", "xtreg", "xtlogit", "xtprobit", "xtpoisson"
         ).contains(this.currentCommand)) {
            this.addField(var4++, this.sem("panel_label"), this.panel);
            this.addField(var4++, this.sem("time_label"), this.time);
         }

         if (this.flag("has_absorb")) {
            this.addField(var4++, this.sem("absorb_label"), this.listPane(this.absorb));
         }

         if (this.flag("has_vce")) {
            this.addField(var4++, "标准误方式", this.vce);
         }

         this.clusterFieldBlock = this.flag("has_cluster") ? this.addField(var4++, "聚类变量（仅 Cluster 时需要）", this.cluster) : null;
         this.addAdvancedSettings(var4++, this.flag("has_if"), this.flag("has_in"), this.flag("has_weight"));
         GridBagConstraints var9 = this.constraints(0, var4);
         var9.gridwidth = 2;
         var9.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), var9);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.rebuilding = false;
         this.updateConditionalFields();
      }

      private void showSpecialPage(String var1) {
         this.showWorkspacePage();
         this.selectResultView("general", false);
         this.selectDataView();
         this.commandDock.setVisible(false);
         this.runButton.setText("运行命令");
         this.previewArea.setEditable(false);
         this.currentCommand = "";
         this.rebuilding = true;
         this.commandTabs.setSelectedIndex(0);
         this.formPanel.removeAll();
         this.commandModel.clear();
         this.methodModel.clear();
         this.insightArea.setText("");
         this.syntaxArea.setText("");
         this.previewArea.setText("");
         this.runButton.setEnabled(false);
         int var2 = 0;
         if (var1.equals("test")) {
            this.setWorkspaceBreadcrumb("测试数据");
            this.commandTitle.setText("测试数据 - 载入或创建练习数据");
            this.exampleLabel.setText("选择一份练习数据，载入后右侧立即显示真实数据网格。");
            this.insightArea.setText("载入练习数据后，右侧数据表会自动刷新。载入操作会清除当前内存数据；请先保存正式数据。");
            JPanel var3 = new JPanel(new GridLayout(0, 2, 8, 8));

            for (String[] var7 : new String[][]{
               {"汽车横截面 auto", "auto"},
               {"劳动数据 nlsw88", "nlsw88"},
               {"长面板 nlswork", "nlswork"},
               {"企业面板 grunfeld", "grunfeld"},
               {"工会面板 union", "union"},
               {"创建 merge 练习表", "merge"},
               {"创建 append 练习表", "append"}
            }) {
               JButton var8 = new JButton(var7[0]);
               styleSecondaryButton(var8);
               var8.addActionListener(var2x -> this.runUtility("hxtestdata " + var7[1], true));
               var3.add(var8);
            }

            this.addField(var2++, "选择练习数据", var3);
         } else {
            this.setWorkspaceBreadcrumb("性能设置");
            this.commandTitle.setText("性能设置 - 切换 Stata/MP 处理器");
            this.exampleLabel.setText("开启时使用许可证允许的处理器上限；关闭时使用 1 个处理器。");
            this.insightArea.setText("开启时动态使用当前许可证允许的最大处理器数；关闭时使用 1 个处理器。每次操作都会进入 Stata History。");
            JPanel var10 = new JPanel(new GridLayout(0, 1, 8, 8));
            JButton var12 = new JButton("开启多线程（许可证上限）");
            JButton var13 = new JButton("关闭多线程（1 个处理器）");
            JButton var14 = new JButton("查看当前线程状态");
            stylePrimaryButton(var12);
            styleSecondaryButton(var13);
            styleSecondaryButton(var14);
            var12.addActionListener(var1x -> this.runUtility("hxthreads on", false));
            var13.addActionListener(var1x -> this.runUtility("hxthreads off", false));
            var14.addActionListener(var1x -> this.runUtility("hxthreads status", false));
            var10.add(var12);
            var10.add(var13);
            var10.add(var14);
            this.addField(var2++, "性能操作", var10);
         }

         GridBagConstraints var11 = this.constraints(0, var2);
         var11.gridwidth = 2;
         var11.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), var11);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.rebuilding = false;
         this.statusLabel.setText("已打开" + (var1.equals("test") ? "测试数据" : "性能设置") + "页面。");
      }

      private void showConvertDtaPage() {
         this.showWorkspacePage();
         this.selectResultView("convert", true);
         this.currentCommand = "__convert_dta__";
         this.commandDock.setVisible(true);
         this.rebuilding = true;
         this.previewArea.setEditable(false);
         this.commandTabs.setSelectedIndex(0);
         this.formPanel.removeAll();
         this.setWorkspaceBreadcrumb("数据处理  ›  导入与转换  ›  转换为 DTA");
         this.commandTitle.setText("转换为 Stata 数据（.dta）");
         this.exampleLabel.setText("最简单操作：选择 Excel / CSV → 查看预览 → 选择保存位置 → 转换为 DTA");
         this.insightArea
            .setText(
               "主要用途\n把 Excel、CSV、TXT 或 TSV 文件安全转换为 Stata .dta。\n\n推荐数据\n企业、年份、财务指标等经管研究原始表。股票代码、证券代码和其他含前导零的列会重点检查。\n\n优点\n自动识别文件格式、显示转换前预览、提示类型风险，并支持单文件和批量转换。\n\n安全规则\n原始文件始终只读；目标已存在时必须明确选择覆盖、另存或取消。"
            );
         this.syntaxArea.setText("Excel 使用 import excel；CSV/TXT 使用 import delimited；转换在独立 frame 中完成，当前数据不会被替换。");
         if (this.convertModeCards.getComponentCount() == 0) {
            this.initializeConvertCards();
         }

         JPanel var1 = new JPanel(new FlowLayout(0, 12, 0));
         var1.setOpaque(false);
         var1.add(this.convertSingleMode);
         var1.add(this.convertBatchMode);
         int var2 = 0;
         this.addField(var2++, "转换方式", var1);
         this.addField(var2++, "文件与读取设置", this.convertModeCards);
         GridBagConstraints var3 = this.constraints(0, var2);
         var3.gridwidth = 2;
         var3.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), var3);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.runButton.setText(this.convertSingleMode.isSelected() ? "转换为 DTA" : "开始批量转换");
         this.runButton.setEnabled(true);
         this.rebuilding = false;
         this.updateConversionPreview();
         this.statusLabel.setText("选择原始文件后会自动识别格式并在右侧显示只读预览。");
      }

      private void initializeConvertCards() {
         this.convertModeCards.setOpaque(false);
         this.convertFormatCards.setOpaque(false);
         this.convertSheet.setEditable(true);
         JPanel var1 = new JPanel();
         var1.setOpaque(false);
         var1.setLayout(new BoxLayout(var1, 1));
         var1.add(this.fieldBlock("1. 选择原始文件", this.pathChooser(this.convertInputFile, "浏览…", this::chooseConvertInput)));
         this.convertDetected.setForeground(MUTED);
         this.convertDetected.setBorder(new EmptyBorder(3, 2, 9, 2));
         var1.add(this.convertDetected);
         JPanel var2 = new JPanel();
         var2.setOpaque(false);
         var2.setLayout(new BoxLayout(var2, 1));
         var2.add(this.fieldBlock("工作表", this.convertSheet));
         var2.add(Box.createVerticalStrut(6));
         var2.add(this.convertExcelFirstRow);
         var2.add(Box.createVerticalStrut(6));
         var2.add(this.fieldBlock("读取范围（可选，如 A1:F100）", this.convertCellRange));
         var2.add(Box.createVerticalStrut(6));
         var2.add(this.convertExcelAllString);
         JPanel var3 = new JPanel();
         var3.setOpaque(false);
         var3.setLayout(new BoxLayout(var3, 1));
         JPanel var4 = new JPanel(new GridLayout(1, 2, 8, 0));
         var4.setOpaque(false);
         var4.add(this.fieldBlock("分隔符", this.convertDelimiter));
         var4.add(this.fieldBlock("编码", this.convertEncoding));
         var3.add(var4);
         var3.add(Box.createVerticalStrut(6));
         var3.add(this.convertDelimitedFirstRow);
         var3.add(Box.createVerticalStrut(6));
         var3.add(this.convertProtectLeadingZeros);
         JLabel var5 = new JLabel("选择 .xlsx、.xls、.csv、.txt 或 .tsv 文件后显示对应设置。", 0);
         var5.setForeground(MUTED);
         this.convertFormatCards.add(var5, "unknown");
         this.convertFormatCards.add(var2, "excel");
         this.convertFormatCards.add(var3, "delimited");
         var1.add(this.fieldBlock("2. 数据读取设置", this.convertFormatCards));
         JButton var6 = new JButton("重新读取预览");
         styleSecondaryButton(var6);
         var6.addActionListener(var1x -> this.previewSelectedExternalFile());
         JPanel var7 = new JPanel(new FlowLayout(0, 0, 2));
         var7.setOpaque(false);
         var7.add(var6);
         var1.add(var7);
         var1.add(Box.createVerticalStrut(8));
         var1.add(this.fieldBlock("3. 保存位置", this.pathChooser(this.convertOutputFile, "浏览…", this::chooseConvertOutput)));
         var1.add(Box.createVerticalStrut(6));
         var1.add(this.convertLoadAfter);
         JPanel var8 = new JPanel();
         var8.setOpaque(false);
         var8.setLayout(new BoxLayout(var8, 1));
         var8.add(this.fieldBlock("输入文件夹", this.pathChooser(this.batchInputFolder, "选择…", () -> this.chooseDirectory(this.batchInputFolder))));
         var8.add(Box.createVerticalStrut(8));
         JPanel var9 = new JPanel(new GridLayout(0, 1, 4, 4));
         var9.setOpaque(false);
         var9.add(this.batchXlsx);
         var9.add(this.batchCsv);
         var9.add(this.batchTxt);
         var8.add(this.fieldBlock("文件类型", var9));
         var8.add(Box.createVerticalStrut(8));
         JPanel var10 = new JPanel();
         var10.setOpaque(false);
         var10.setLayout(new BoxLayout(var10, 1));
         var10.add(this.batchExcelFirstRow);
         var10.add(Box.createVerticalStrut(4));
         var10.add(this.batchExcelAllString);
         var10.add(Box.createVerticalStrut(6));
         JPanel var11 = new JPanel(new GridLayout(1, 2, 8, 0));
         var11.setOpaque(false);
         var11.add(this.fieldBlock("CSV/TXT 分隔符", this.batchDelimiter));
         var11.add(this.fieldBlock("CSV/TXT 编码", this.batchEncoding));
         var10.add(var11);
         var10.add(Box.createVerticalStrut(4));
         var10.add(this.batchDelimitedFirstRow);
         var10.add(Box.createVerticalStrut(4));
         var10.add(this.batchProtectLeadingZeros);
         var8.add(this.fieldBlock("批量读取设置", var10));
         var8.add(Box.createVerticalStrut(8));
         var8.add(this.fieldBlock("输出文件夹", this.pathChooser(this.batchOutputFolder, "选择…", () -> this.chooseDirectory(this.batchOutputFolder))));
         var8.add(Box.createVerticalStrut(6));
         var8.add(this.batchSkipExisting);
         var8.add(Box.createVerticalStrut(8));
         styleSecondaryButton(this.batchStopButton);
         this.batchStopButton.setEnabled(false);
         this.batchStopButton.addActionListener(var1x -> {
            this.batchStopRequested = true;
            this.batchStopButton.setEnabled(false);
            this.statusLabel.setText("已请求停止：当前文件完成后不再开始下一个文件。");
         });
         var8.add(this.batchStopButton);
         this.convertModeCards.add(var1, "single");
         this.convertModeCards.add(var8, "batch");
         this.convertModeLayout.show(this.convertModeCards, "single");
      }

      private JComponent fieldBlock(String var1, JComponent var2) {
         JPanel var3 = new JPanel(new BorderLayout(0, 5));
         var3.setOpaque(false);
         JLabel var4 = new JLabel(var1);
         var4.setForeground(new Color(55, 67, 84));
         var4.setFont(var4.getFont().deriveFont(1, 11.0F));
         var3.add(var4, "North");
         var3.add(var2, "Center");
         var3.setAlignmentX(0.0F);
         var3.setMaximumSize(new Dimension(Integer.MAX_VALUE, 150));
         return var3;
      }

      private JComponent pathChooser(JTextField var1, String var2, Runnable var3) {
         JPanel var4 = new JPanel(new BorderLayout(6, 0));
         var4.setOpaque(false);
         JButton var5 = new JButton(var2);
         styleSecondaryButton(var5);
         var5.addActionListener(var1x -> var3.run());
         var4.add(var1, "Center");
         var4.add(var5, "East");
         return var4;
      }

      private void chooseConvertInput() {
         JFileChooser var1 = new JFileChooser();
         var1.setDialogTitle("选择 Excel、CSV 或文本文件");
         if (var1.showOpenDialog(this) == 0) {
            Path var2 = var1.getSelectedFile().toPath().toAbsolutePath();
            this.convertInputFile.setText(var2.toString());
            this.convertOutputFile.setText(replaceExtension(var2, ".dta").toString());
            this.detectExternalFile(var2);
            this.previewSelectedExternalFile();
         }
      }

      private void chooseConvertOutput() {
         JFileChooser var1 = new JFileChooser();
         var1.setDialogTitle("选择 DTA 保存位置");
         var1.setSelectedFile(new File(this.convertOutputFile.getText().isBlank() ? "output.dta" : this.convertOutputFile.getText()));
         if (var1.showSaveDialog(this) == 0) {
            Path var2 = var1.getSelectedFile().toPath().toAbsolutePath();
            if (!var2.getFileName().toString().toLowerCase(Locale.ROOT).endsWith(".dta")) {
               var2 = Paths.get(var2.toString() + ".dta");
            }

            this.convertOutputFile.setText(var2.toString());
            this.updateConversionPreview();
         }
      }

      private void chooseDirectory(JTextField var1) {
         JFileChooser var2 = new JFileChooser();
         var2.setFileSelectionMode(1);
         if (var2.showOpenDialog(this) == 0) {
            var1.setText(var2.getSelectedFile().getAbsolutePath());
            if (var1 == this.batchInputFolder && this.batchOutputFolder.getText().isBlank()) {
               this.batchOutputFolder.setText(Paths.get(var1.getText(), "dta").toString());
            }

            this.updateConversionPreview();
         }
      }

      private void detectExternalFile(Path var1) {
         String var2 = externalType(var1);
         this.convertFormatLayout.show(this.convertFormatCards, var2.equals("excel") ? "excel" : (var2.equals("delimited") ? "delimited" : "unknown"));
         if (var2.equals("excel")) {
            List<String> var3 = HxWorkbench.XlsxInspector.sheetNames(var1);
            this.convertSheet.removeAllItems();
            if (var3.isEmpty()) {
               this.convertSheet.addItem("（默认工作表）");
            } else {
               for (String var5 : var3) {
                  this.convertSheet.addItem(var5);
               }
            }
         } else if (var1.toString().toLowerCase(Locale.ROOT).endsWith(".tsv")) {
            this.convertDelimiter.setSelectedItem("Tab");
         }
      }

      private void previewSelectedExternalFile() {
         Path var1;
         try {
            var1 = Paths.get(this.convertInputFile.getText().trim()).toAbsolutePath();
         } catch (Exception var17) {
            return;
         }

         if (!Files.isRegularFile(var1)) {
            JOptionPane.showMessageDialog(this, "请选择存在的原始数据文件。", "文件不存在", 1);
         } else {
            String var2 = externalType(var1);
            if ("unknown".equals(var2)) {
               JOptionPane.showMessageDialog(this, "第一版支持 .xlsx、.xls、.csv、.txt 和 .tsv。", "暂不支持该格式", 1);
            } else {
               this.setBusy(true, "正在只读预览 " + var1.getFileName() + "…");
               String var3 = this.nextImportFrameName();
               Frame var4 = null;

               try {
                  this.currentExternalProfile = HxWorkbench.ExternalFileProfile.inspectRaw(
                     var1,
                     selected(this.convertDelimiter),
                     var2.equals("excel") ? this.convertExcelFirstRow.isSelected() : this.convertDelimitedFirstRow.isSelected(),
                     var2.equals("delimited") ? selected(this.convertEncoding) : "自动识别"
                  );
                  var4 = Frame.create(var3);
                  String var5 = this.buildImportCommand(var1, this.currentExternalProfile, false);
                  int var6 = HxWorkbench.StataBridge.execute("quietly frame " + var3 + ": " + var5, false);
                  if (var6 != 0) {
                     throw new IllegalStateException("Stata 读取文件失败，返回码 " + var6);
                  }

                  var4 = Frame.connect(var3);
                  this.currentExternalProfile.enrichFromFrame(var4);
                  this.importPreviewModel.load(var4, 200, 60);
                  this.configureImportPreviewWidths();
                  this.importPreviewLabel.setText(this.currentExternalProfile.previewSummary());
                  this.importIssues.setText(this.currentExternalProfile.issueSummary());
                  this.importIssues.setCaretPosition(0);
                  this.convertDetected.setText(this.currentExternalProfile.detectedSummary());
                  this.selectResultView("convert", true);
                  this.updateConversionPreview();
                  this.setBusy(false, "预览完成；当前 Stata 数据没有改变。");
               } catch (Throwable var16) {
                  this.importPreviewModel.clear();
                  this.importIssues.setText("预览失败：\n" + var16.getMessage());
                  this.setBusy(false, "预览失败：" + var16.getMessage());
                  JOptionPane.showMessageDialog(this, "无法预览该文件：\n" + var16.getMessage(), "预览失败", 0);
               } finally {
                  if (var4 != null) {
                     try {
                        var4.drop();
                     } catch (Throwable var15) {
                     }
                  }
               }
            }
         }
      }

      private String buildImportCommand(Path var1, HxWorkbench.ExternalFileProfile var2, boolean var3) {
         return this.buildImportCommand(var1, var2, var3, null);
      }

      private String buildImportCommand(Path var1, HxWorkbench.ExternalFileProfile var2, boolean var3, HxWorkbench.BatchConversionConfig var4) {
         String var5 = externalType(var1);
         if (var5.equals("excel")) {
            StringBuilder var13 = new StringBuilder("import excel using ").append(commandQuote(var1.toString()));
            String var14 = var3 ? var2.firstSheet() : selected(this.convertSheet);
            if (var14.startsWith("（默认")) {
               var14 = "";
            }

            if (!var14.isBlank()) {
               var13.append(", sheet(").append(commandQuote(var14)).append(")");
            }

            boolean var15 = var3 && var4 != null ? var4.excelFirstRow : this.convertExcelFirstRow.isSelected();
            if (var15) {
               var13.append(var13.indexOf(",") < 0 ? ", firstrow" : " firstrow");
            }

            String var16 = var3 ? "" : this.convertCellRange.getText().trim();
            if (!var16.isBlank()) {
               if (!var16.matches("(?i)[A-Z]+[0-9]+(?::[A-Z]+[0-9]+)?")) {
                  throw new IllegalArgumentException("Excel 读取范围格式应类似 A1:F100。");
               }

               var13.append(var13.indexOf(",") < 0 ? ", " : " ").append("cellrange(").append(var16).append(")");
            }

            boolean var17 = var3 && var4 != null ? var4.excelAllString : this.convertExcelAllString.isSelected();
            if (var17) {
               var13.append(var13.indexOf(",") < 0 ? ", allstring" : " allstring");
            }

            var13.append(var13.indexOf(",") < 0 ? ", clear" : " clear");
            return var13.toString();
         } else {
            StringBuilder var6 = new StringBuilder("import delimited using ").append(commandQuote(var1.toString())).append(", clear");
            boolean var7 = var3 && var4 != null ? var4.delimitedFirstRow : this.convertDelimitedFirstRow.isSelected();
            var6.append(var7 ? " varnames(1)" : " varnames(nonames)");
            String var8 = var3 && var4 != null ? var4.delimiter : selected(this.convertDelimiter);
            if (var1.toString().toLowerCase(Locale.ROOT).endsWith(".tsv") && "自动识别".equals(var8)) {
               var8 = "Tab";
            }

            String var9 = delimiterOption(var8);
            if (!var9.isBlank()) {
               var6.append(" ").append(var9);
            }

            String var10 = var2.encoding;
            if (var10 == null || var10.isBlank()) {
               var10 = var3 && var4 != null ? var4.encoding : selected(this.convertEncoding);
               if ("自动识别".equals(var10)) {
                  var10 = "";
               }
            }

            if (!var10.isBlank()) {
               var6.append(" encoding(").append(commandQuote(var10)).append(")");
            }

            boolean var11 = var3 && var4 != null ? var4.protectLeadingZeros : this.convertProtectLeadingZeros.isSelected();
            if (var11 && !var2.leadingZeroColumns.isEmpty()) {
               var6.append(" stringcols(");

               for (int var12 = 0; var12 < var2.leadingZeroColumns.size(); var12++) {
                  if (var12 > 0) {
                     var6.append(" ");
                  }

                  var6.append(var2.leadingZeroColumns.get(var12));
               }

               var6.append(")");
            }

            return var6.toString();
         }
      }

      private void updateConversionPreview() {
         if (!this.rebuilding && "__convert_dta__".equals(this.currentCommand)) {
            if (this.convertBatchMode.isSelected()) {
               this.previewArea.setText("批量转换：逐个执行 import excel/import delimited，再 save 为同名 .dta");
               this.runButton.setText("开始批量转换");
               this.flashCommandPreview();
            } else {
               this.runButton.setText("转换为 DTA");
               String var1 = this.convertInputFile.getText().trim();
               String var2 = this.convertOutputFile.getText().trim();
               if (var1.isBlank()) {
                  this.previewArea.setText("选择文件后显示实际 Stata 命令");
                  this.flashCommandPreview();
               } else {
                  try {
                     Path var3 = Paths.get(var1).toAbsolutePath();
                     HxWorkbench.ExternalFileProfile var4 = this.currentExternalProfile == null
                        ? HxWorkbench.ExternalFileProfile.inspectRaw(
                           var3,
                           selected(this.convertDelimiter),
                           externalType(var3).equals("excel") ? this.convertExcelFirstRow.isSelected() : this.convertDelimitedFirstRow.isSelected(),
                           externalType(var3).equals("delimited") ? selected(this.convertEncoding) : "自动识别"
                        )
                        : this.currentExternalProfile;
                     String var5 = this.buildImportCommand(var3, var4, false);
                     String var6 = var2.isBlank() ? "save <选择保存位置>" : "save " + commandQuote(Paths.get(var2).toAbsolutePath().toString());
                     this.previewArea.setText(var5 + "\n" + var6);
                  } catch (Throwable var7) {
                     this.previewArea.setText("设置尚未完整：" + var7.getMessage());
                  }

                  this.previewArea.setCaretPosition(0);
                  this.flashCommandPreview();
               }
            }
         }
      }

      private void runConvertDta() {
         if (this.convertBatchMode.isSelected()) {
            this.runBatchConversion();
         } else {
            final Path var1;
            Path var2;
            try {
               var1 = Paths.get(this.convertInputFile.getText().trim()).toAbsolutePath();
               var2 = Paths.get(this.convertOutputFile.getText().trim()).toAbsolutePath();
            } catch (Exception var7) {
               JOptionPane.showMessageDialog(this, "请完整选择原始文件和 DTA 保存位置。", "设置尚未完整", 1);
               return;
            }

            if (Files.isRegularFile(var1) && !"unknown".equals(externalType(var1))) {
               final Path resolvedOutput = this.resolveExistingOutput(var2);
               if (resolvedOutput != null) {
                  final HxWorkbench.ExternalFileProfile var3;
                  try {
                     var3 = HxWorkbench.ExternalFileProfile.inspectRaw(
                        var1,
                        selected(this.convertDelimiter),
                        externalType(var1).equals("excel") ? this.convertExcelFirstRow.isSelected() : this.convertDelimitedFirstRow.isSelected(),
                        externalType(var1).equals("delimited") ? selected(this.convertEncoding) : "自动识别"
                     );
                  } catch (IOException var6) {
                     JOptionPane.showMessageDialog(this, "读取原文件失败：\n" + var6.getMessage(), "转换失败", 0);
                     return;
                  }

                  this.activeRunBefore = HxWorkbench.RunShape.capture();
                  HxWorkbench.StataBridge.clearRunAudit();
                  this.beginMonitoredRun("转换为 DTA\n" + this.previewArea.getText().trim(), false, 0);
                  SwingWorker var5 = new SwingWorker<HxWorkbench.ConversionOutcome, Void>() {
                     protected HxWorkbench.ConversionOutcome doInBackground() {
                        return WorkbenchFrame.this.convertOne(var1, resolvedOutput, var3, Files.exists(resolvedOutput), false);
                     }

                     @Override
                     protected void done() {
                        HxWorkbench.ConversionOutcome var1x;
                        try {
                           var1x = this.get();
                        } catch (Throwable var4) {
                           var1x = HxWorkbench.ConversionOutcome.failure(var1, resolvedOutput, 459, HxWorkbench.WorkbenchFrame.rootMessage(var4));
                        }

                        String var2x = HxWorkbench.StataBridge.characteristic("hxtoolbox_history_status");
                        if (var2x.isBlank()) {
                           var2x = "请在 History 核对导入与保存命令";
                        }

                        HxWorkbench.RunResult var3x = var1x.success
                           ? HxWorkbench.RunResult.capture(WorkbenchFrame.this.previewArea.getText().trim(), 0, var2x)
                           : HxWorkbench.RunResult.failure(WorkbenchFrame.this.previewArea.getText().trim(), var1x.rc, var1x.message);
                        HxWorkbench.StataBridge.execute("quietly hxrefresh", false);
                        WorkbenchFrame.this.refreshDataset(false);
                        WorkbenchFrame.this.finishMonitoredRun(var3x, HxWorkbench.RunShape.capture());
                        WorkbenchFrame.this.monitorOutcome
                           .setText(
                              var1x.success
                                 ? "转换成功\n\n输出："
                                    + var1x.output
                                    + "\n观测数："
                                    + var1x.n
                                    + "\n变量数："
                                    + var1x.k
                                    + "\n文件大小："
                                    + HxWorkbench.WorkbenchFrame.humanBytes(var1x.bytes)
                                    + "\n\n原始文件保持不变。"
                                 : "转换失败  r(" + var1x.rc + ")\n\n" + var1x.message
                           );
                        if (!var1x.success) {
                           JOptionPane.showMessageDialog(WorkbenchFrame.this, var1x.message, "转换失败", 0);
                        } else {
                           WorkbenchFrame.this.showConversionSummary(var1x);
                        }
                     }
                  };
                  var5.execute();
               }
            } else {
               JOptionPane.showMessageDialog(this, "请选择支持的 Excel、CSV 或文本文件。", "原始文件无效", 1);
            }
         }
      }

      private HxWorkbench.ConversionOutcome convertOne(Path var1, Path var2, HxWorkbench.ExternalFileProfile var3, boolean var4, boolean var5) {
         return this.convertOne(var1, var2, var3, var4, var5, null);
      }

      private HxWorkbench.ConversionOutcome convertOne(
         Path var1, Path var2, HxWorkbench.ExternalFileProfile var3, boolean var4, boolean var5, HxWorkbench.BatchConversionConfig var6
      ) {
         String var7 = this.nextImportFrameName();
         int var8 = this.runRecorded("frame create " + var7);
         if (var8 != 0) {
            return HxWorkbench.ConversionOutcome.failure(var1, var2, var8, "无法创建临时 frame，返回码 " + var8);
         } else {
            long var9 = 0L;
            int var11 = 0;

            HxWorkbench.ConversionOutcome var15;
            try {
               String var12 = "frame " + var7 + ": " + this.buildImportCommand(var1, var3, var5, var6);
               var8 = this.runRecorded(var12);
               if (var8 != 0) {
                  return HxWorkbench.ConversionOutcome.failure(var1, var2, var8, "导入失败，返回码 " + var8);
               }

               Frame var27 = Frame.connect(var7);
               var9 = var27.getObsTotal();
               var11 = var27.getVarCount();
               String var14 = "frame " + var7 + ": save " + commandQuote(var2.toString()) + (var4 ? ", replace" : "");
               var8 = this.runRecorded(var14);
               if (var8 == 0) {
                  long var29 = HxWorkbench.safe(() -> Files.size(var2), 0L);
                  return HxWorkbench.ConversionOutcome.success(var1, var2, var9, var11, var29);
               }

               var15 = HxWorkbench.ConversionOutcome.failure(var1, var2, var8, "保存 DTA 失败，返回码 " + var8);
            } catch (Throwable var21) {
               return HxWorkbench.ConversionOutcome.failure(var1, var2, 459, var21.getMessage());
            } finally {
               HxWorkbench.StataBridge.execute("capture frame drop " + var7, false);
            }

            return var15;
         }
      }

      private int runRecorded(String var1) {
         return HxWorkbench.StataBridge.execute("hxexecute, command(" + HxWorkbench.StataBridge.quote(var1) + ")", true);
      }

      private Path resolveExistingOutput(Path var1) {
         if (!Files.exists(var1)) {
            return var1;
         } else {
            Object[] var2 = new Object[]{"另存为新文件", "覆盖已有 DTA", "取消"};
            int var3 = JOptionPane.showOptionDialog(this, var1 + " 已存在。请选择处理方式。", "目标文件已存在", -1, 2, null, var2, var2[0]);
            if (var3 == 1) {
               return var1;
            } else if (var3 != 0) {
               return null;
            } else {
               JFileChooser var4 = new JFileChooser();
               var4.setSelectedFile(var1.toFile());
               if (var4.showSaveDialog(this) != 0) {
                  return null;
               } else {
                  Path var5 = var4.getSelectedFile().toPath().toAbsolutePath();
                  if (!var5.toString().toLowerCase(Locale.ROOT).endsWith(".dta")) {
                     var5 = Paths.get(var5 + ".dta");
                  }

                  return Files.exists(var5) ? this.resolveExistingOutput(var5) : var5;
               }
            }
         }
      }

      private void showConversionSummary(HxWorkbench.ConversionOutcome var1) {
         if (this.convertLoadAfter.isSelected()) {
            this.runRecorded("use " + commandQuote(var1.output.toString()) + ", clear");
            HxWorkbench.StataBridge.execute("quietly hxrefresh", false);
            this.refreshDataset(false);
         }

         String var2 = "转换完成\n\n原文件：" + var1.input + "\n输出：" + var1.output + "\n观测数：" + var1.n + "\n变量数：" + var1.k + "\n文件大小：" + humanBytes(var1.bytes);
         Object[] var3 = new Object[]{"载入这个 DTA", "打开数据表", "查看变量", "关闭"};
         int var4 = JOptionPane.showOptionDialog(this, var2, "转换完成", -1, 1, null, var3, var3[3]);
         if (var4 >= 0 && var4 <= 2) {
            this.runRecorded("use " + commandQuote(var1.output.toString()) + ", clear");
            HxWorkbench.StataBridge.execute("quietly hxrefresh", false);
            this.refreshDataset(false);
            if (var4 == 1) {
               HxWorkbench.StataBridge.execute("browse", true);
            }

            if (var4 == 2) {
               HxWorkbench.StataBridge.execute("describe", true);
            }

            this.selectDataView();
         }
      }

      private void setBatchControlsEnabled(boolean var1) {
         this.batchInputFolder.setEnabled(var1);
         this.batchOutputFolder.setEnabled(var1);
         this.batchXlsx.setEnabled(var1);
         this.batchCsv.setEnabled(var1);
         this.batchTxt.setEnabled(var1);
         this.batchExcelFirstRow.setEnabled(var1);
         this.batchExcelAllString.setEnabled(var1);
         this.batchDelimitedFirstRow.setEnabled(var1);
         this.batchDelimiter.setEnabled(var1);
         this.batchEncoding.setEnabled(var1);
         this.batchProtectLeadingZeros.setEnabled(var1);
         this.batchSkipExisting.setEnabled(var1);
      }

      private void runBatchConversion() {
         Path var1;
         final Path var2;
         try {
            var1 = Paths.get(this.batchInputFolder.getText().trim()).toAbsolutePath();
            var2 = Paths.get(this.batchOutputFolder.getText().trim()).toAbsolutePath();
         } catch (Exception var9) {
            JOptionPane.showMessageDialog(this, "请选择输入文件夹和输出文件夹。", "批量设置尚未完整", 1);
            return;
         }

         if (!Files.isDirectory(var1)) {
            JOptionPane.showMessageDialog(this, "输入文件夹不存在。", "批量设置无效", 1);
         } else {
            try {
               Files.createDirectories(var2);
            } catch (IOException var8) {
               JOptionPane.showMessageDialog(this, "无法创建输出文件夹：\n" + var8.getMessage(), "批量转换失败", 0);
               return;
            }

            final ArrayList<Path> var3 = new ArrayList<>();

            try (Stream<Path> var4 = Files.list(var1)) {
               var4.filter(var0 -> Files.isRegularFile(var0)).filter(this::batchTypeSelected).sorted().forEach(var3::add);
            } catch (IOException var11) {
               JOptionPane.showMessageDialog(this, "无法读取输入文件夹：\n" + var11.getMessage(), "批量转换失败", 0);
               return;
            }

            if (var3.isEmpty()) {
               JOptionPane.showMessageDialog(this, "没有发现符合勾选类型的文件。", "没有待转换文件", 1);
            } else {
               final HxWorkbench.BatchConversionConfig var5 = new HxWorkbench.BatchConversionConfig(
                  this.batchExcelFirstRow.isSelected(),
                  this.batchExcelAllString.isSelected(),
                  this.batchDelimitedFirstRow.isSelected(),
                  selected(this.batchDelimiter),
                  selected(this.batchEncoding),
                  this.batchProtectLeadingZeros.isSelected(),
                  this.batchSkipExisting.isSelected()
               );
               this.batchStopRequested = false;
               this.setBatchControlsEnabled(false);
               this.batchStopButton.setEnabled(true);
               this.activeRunBefore = HxWorkbench.RunShape.capture();
               HxWorkbench.StataBridge.clearRunAudit();
               this.beginMonitoredRun("批量转换为 DTA（" + var3.size() + " 个文件）", true, var3.size());
               SwingWorker var6 = new SwingWorker<HxWorkbench.BatchSummary, HxWorkbench.BatchProgress>() {
                  protected HxWorkbench.BatchSummary doInBackground() {
                     HxWorkbench.BatchSummary var1x = new HxWorkbench.BatchSummary(var3.size());
                     int var2x = 0;

                     for (Path var4 : var3) {
                        if (WorkbenchFrame.this.batchStopRequested) {
                           var1x.stopped = true;
                           break;
                        }

                        Path var5x = var2.resolve(HxWorkbench.WorkbenchFrame.stripExtension(var4.getFileName().toString()) + ".dta");
                        if (Files.exists(var5x) && var5.skipExisting) {
                           var1x.skipped++;
                           var1x.rows.add(new Object[]{var4.getFileName().toString(), var5x.getFileName().toString(), "跳过", "目标已存在"});
                           this.publish(
                              new HxWorkbench.BatchProgress[]{
                                 new HxWorkbench.BatchProgress(++var2x, var3.size(), var4.getFileName().toString(), "○ 跳过", "目标已存在", 0)
                              }
                           );
                        } else {
                           HxWorkbench.ConversionOutcome var6x;
                           try {
                              HxWorkbench.ExternalFileProfile var7 = HxWorkbench.ExternalFileProfile.inspectRaw(
                                 var4,
                                 var5.delimiter,
                                 HxWorkbench.WorkbenchFrame.externalType(var4).equals("excel") ? var5.excelFirstRow : var5.delimitedFirstRow,
                                 HxWorkbench.WorkbenchFrame.externalType(var4).equals("delimited") ? var5.encoding : "自动识别"
                              );
                              var6x = WorkbenchFrame.this.convertOne(var4, var5x, var7, Files.exists(var5x), true, var5);
                           } catch (Throwable var8) {
                              var6x = HxWorkbench.ConversionOutcome.failure(var4, var5x, 459, HxWorkbench.WorkbenchFrame.rootMessage(var8));
                           }

                           if (var6x.success) {
                              var1x.success++;
                              var1x.rows
                                 .add(new Object[]{var4.getFileName().toString(), var5x.getFileName().toString(), "成功", var6x.n + " 行 × " + var6x.k + " 列"});
                              this.publish(
                                 new HxWorkbench.BatchProgress[]{
                                    new HxWorkbench.BatchProgress(
                                       ++var2x, var3.size(), var4.getFileName().toString(), "完成", var6x.n + " 行 × " + var6x.k + " 列", 0
                                    )
                                 }
                              );
                           } else {
                              var1x.failed++;
                              if (var1x.firstRc == 0) {
                                 var1x.firstRc = var6x.rc;
                              }

                              var1x.failures.add(var4.getFileName() + "：" + var6x.message);
                              var1x.rows.add(new Object[]{var4.getFileName().toString(), var5x.getFileName().toString(), "失败", var6x.message});
                              this.publish(
                                 new HxWorkbench.BatchProgress[]{
                                    new HxWorkbench.BatchProgress(++var2x, var3.size(), var4.getFileName().toString(), "失败", var6x.message, var6x.rc)
                                 }
                              );
                           }
                        }
                     }

                     return var1x;
                  }

                  @Override
                  protected void process(List<HxWorkbench.BatchProgress> var1) {
                     for (HxWorkbench.BatchProgress var3x : var1) {
                        WorkbenchFrame.this.updateBatchMonitor(var3x);
                     }
                  }

                  @Override
                  protected void done() {
                     WorkbenchFrame.this.setBatchControlsEnabled(true);
                     WorkbenchFrame.this.batchStopButton.setEnabled(false);

                     HxWorkbench.BatchSummary var1x;
                     try {
                        var1x = this.get();
                     } catch (Throwable var5x) {
                        var1x = HxWorkbench.BatchSummary.crashed(var3.size(), HxWorkbench.WorkbenchFrame.rootMessage(var5x));
                     }

                     String var2x = HxWorkbench.StataBridge.characteristic("hxtoolbox_history_status");
                     if (var1x.success == 0 && var1x.failed == 0) {
                        var2x = "未执行（全部跳过）";
                     } else if (var2x.isBlank()) {
                        var2x = "逐条写入；请在 History 核对";
                     }

                     int var3x = var1x.failed == 0 ? 0 : (var1x.firstRc == 0 ? 459 : var1x.firstRc);
                     HxWorkbench.RunResult var4 = var3x == 0
                        ? HxWorkbench.RunResult.capture("批量转换为 DTA（" + var3.size() + " 个文件）", 0, var2x)
                        : HxWorkbench.RunResult.failure("批量转换为 DTA（" + var3.size() + " 个文件）", var3x, var1x.failed + " 个文件转换失败。");
                     WorkbenchFrame.this.finishMonitoredRun(var4, HxWorkbench.RunShape.capture());
                     WorkbenchFrame.this.monitorOutcome
                        .setText(
                           (var1x.stopped ? "批量转换已按请求停止" : "批量转换完成")
                              + "\n\n共发现："
                              + var3.size()
                              + "\n成功："
                              + var1x.success
                              + "\n失败："
                              + var1x.failed
                              + "\n跳过："
                              + var1x.skipped
                              + (var1x.failures.isEmpty() ? "" : "\n\n失败文件已列在“转换预览”。")
                        );
                     WorkbenchFrame.this.importPreviewModel.loadRows(new String[]{"原文件", "DTA 文件", "状态", "说明"}, var1x.rows);
                     WorkbenchFrame.this.configureImportPreviewWidths();
                     WorkbenchFrame.this.importPreviewLabel
                        .setText("批量转换：发现 " + var3.size() + "，成功 " + var1x.success + "，失败 " + var1x.failed + "，跳过 " + var1x.skipped);
                     WorkbenchFrame.this.importIssues.setText(var1x.failures.isEmpty() ? "没有失败文件。" : "失败文件\n\n" + String.join("\n", var1x.failures));
                     JOptionPane.showMessageDialog(
                        WorkbenchFrame.this,
                        "共发现：" + var3.size() + " 个文件\n成功：" + var1x.success + "\n失败：" + var1x.failed + "\n跳过：" + var1x.skipped,
                        "批量转换完成",
                        var1x.failed == 0 ? 1 : 2
                     );
                  }
               };
               var6.execute();
            }
         }
      }

      private void updateBatchMonitor(HxWorkbench.BatchProgress var1) {
         this.monitorProgress.setIndeterminate(false);
         this.monitorProgress.setMaximum(var1.total);
         this.monitorProgress.setValue(var1.completed);
         this.monitorProgress.setString(var1.completed + " / " + var1.total + "（" + Math.round(100.0 * var1.completed / Math.max(1, var1.total)) + "%）");
         this.commandDockProgress.setIndeterminate(false);
         this.commandDockProgress.setMaximum(var1.total);
         this.commandDockProgress.setValue(var1.completed);
         this.commandDockProgress.setString(var1.completed + " / " + var1.total);
         this.monitorCommand.setText("批量转换为 DTA\n当前文件：" + var1.fileName);
         this.appendMonitorLog(var1.completed + "/" + var1.total + "  " + var1.fileName + "  " + var1.status);
         this.runQueueModel.addRow(new Object[]{++this.runSequence, var1.status, var1.fileName, var1.detail, var1.rc == 0 ? "-" : var1.rc});
         if (this.activeQueueRow >= 0 && this.activeQueueRow < this.runQueueModel.getRowCount()) {
            this.runQueueModel.setValueAt("● " + var1.completed + "/" + var1.total, this.activeQueueRow, 1);
         }
      }

      private boolean batchTypeSelected(Path var1) {
         String var2 = var1.getFileName().toString().toLowerCase(Locale.ROOT);
         if ((var2.endsWith(".xlsx") || var2.endsWith(".xls")) && this.batchXlsx.isSelected()) {
            return true;
         } else {
            return var2.endsWith(".csv") && this.batchCsv.isSelected() ? true : (var2.endsWith(".txt") || var2.endsWith(".tsv")) && this.batchTxt.isSelected();
         }
      }

      private void configureImportPreviewWidths() {
         for (int var1 = 0; var1 < this.importPreviewTable.getColumnModel().getColumnCount(); var1++) {
            String var2 = this.importPreviewTable.getColumnName(var1);
            this.importPreviewTable.getColumnModel().getColumn(var1).setPreferredWidth(Math.max(95, Math.min(220, var2.length() * 12 + 36)));
         }
      }

      private String nextImportFrameName() {
         return "__hximp" + Integer.toString(this.importFrameCounter.incrementAndGet(), 36);
      }

      private static String externalType(Path var0) {
         String var1 = var0.getFileName().toString().toLowerCase(Locale.ROOT);
         if (var1.endsWith(".xlsx") || var1.endsWith(".xls")) {
            return "excel";
         } else {
            return !var1.endsWith(".csv") && !var1.endsWith(".txt") && !var1.endsWith(".tsv") ? "unknown" : "delimited";
         }
      }

      private static String delimiterOption(String var0) {
         switch (var0) {
            case "Tab":
               return "delimiter(tab)";
            case "逗号":
               return "delimiter(\",\")";
            case "分号":
               return "delimiter(\";\")";
            case "空格":
               return "delimiter(\" \")";
            case "竖线":
               return "delimiter(\"|\")";
            default:
               return "";
         }
      }

      private static Path replaceExtension(Path var0, String var1) {
         Path var2 = var0.getParent();
         String var3 = stripExtension(var0.getFileName().toString()) + var1;
         return var2 == null ? Paths.get(var3) : var2.resolve(var3);
      }

      private static String stripExtension(String var0) {
         int var1 = var0.lastIndexOf(46);
         return var1 <= 0 ? var0 : var0.substring(0, var1);
      }

      private static String humanBytes(long var0) {
         if (var0 < 1024L) {
            return var0 + " B";
         } else {
            return var0 < 1048576L ? String.format(Locale.ROOT, "%.1f KB", var0 / 1024.0) : String.format(Locale.ROOT, "%.1f MB", var0 / 1048576.0);
         }
      }

      private static String commandQuote(String var0) {
         return "\"" + (var0 == null ? "" : var0.replace("\"", "\"\"")) + "\"";
      }

      private void showMissingAnalysisPage() {
         this.showWorkspacePage();
         this.selectResultView("missing", false);
         this.selectDataView();
         this.currentCommand = "__missing_analysis__";
         this.commandDock.setVisible(true);
         this.previewArea.setEditable(false);
         this.rebuilding = true;
         this.commandTabs.setSelectedIndex(0);
         this.formPanel.removeAll();
         this.setWorkspaceBreadcrumb("数据处理  ›  数据检查  ›  缺失值分析");
         this.commandTitle.setText("缺失值分析");
         this.exampleLabel.setText("最简单操作：选择检查变量；面板数据可再选择 firm 和 year 分类查看。");
         this.insightArea
            .setText(
               "主要用途\n检查当前数据中哪些变量存在缺失，并按企业、年份、企业×年份或其他分类变量汇总。\n\n推荐数据\n横截面、面板、重复横截面和企业-年份数据。面板数据建议同时选择企业标识与年份。\n\n优点\n同时提供总体、分类汇总、联合明细、具体缺失记录和图形；结果直接联动右侧只读数据表。\n\n局限\n超大型数据的完整扫描需要一定时间；高基数联合分类可能产生较多结果行。"
            );
         this.syntaxArea.setText("只读分析：底层执行并记录 misstable summarize；分类结果由工作台直接读取当前 Stata 数据计算，不修改数据。");
         List var1 = HxWorkbench.StataBridge.variableNames();
         replaceListItems(this.missingVariables, var1);
         replaceListItems(this.missingGroups, var1);
         this.missingVariables.clearSelection();
         this.missingGroups.clearSelection();
         this.missingAllVariables.setSelected(true);
         this.missingVariables.setEnabled(false);
         this.missingMode.setSelectedIndex(0);
         this.missingGroups.setEnabled(false);
         this.missingSeparateSummary.setEnabled(false);
         int var2 = 0;
         JPanel var3 = new JPanel(new FlowLayout(0, 12, 0));
         var3.setOpaque(false);
         var3.add(this.missingAllVariables);
         var3.add(this.missingChooseVariables);
         JPanel var4 = new JPanel(new BorderLayout(0, 7));
         var4.setOpaque(false);
         var4.add(var3, "North");
         var4.add(this.listPane(this.missingVariables), "Center");
         this.addField(var2++, "检查变量", var4);
         this.addField(var2++, "如何查看缺失值", this.missingMode);
         this.addField(var2++, "分类变量（可多选）", this.listPane(this.missingGroups));
         JPanel var5 = new JPanel(new GridLayout(0, 1, 5, 5));
         var5.setOpaque(false);
         var5.add(this.missingSeparateSummary);
         var5.add(this.missingOnly);
         this.addField(var2++, "结果范围", var5);
         JPanel var6 = new JPanel(new GridLayout(1, 4, 7, 0));
         var6.setOpaque(false);
         var6.add(new JLabel("缺失变量数 ≥"));
         var6.add(this.missingMinCount);
         var6.add(new JLabel("缺失比例 ≥ (%)"));
         var6.add(this.missingMinRate);
         this.addField(var2++, "筛选阈值", var6);
         this.addField(var2++, "排序", this.missingSort);
         GridBagConstraints var7 = this.constraints(0, var2);
         var7.gridwidth = 2;
         var7.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), var7);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.runButton.setText("分析缺失值");
         this.runButton.setEnabled(Data.getVarCount() > 0);
         this.rebuilding = false;
         this.updateMissingPreview();
         this.statusLabel.setText("请选择检查变量和分类方式，然后开始分析。分析过程只读。");
      }

      private List<String> selectedMissingVariables() {
         return this.missingAllVariables.isSelected() ? HxWorkbench.StataBridge.variableNames() : this.missingVariables.getSelectedValuesList();
      }

      private List<String> selectedMissingGroups() {
         List<String> var1 = this.missingGroups.getSelectedValuesList();
         return this.missingMode.getSelectedIndex() == 1 && var1.size() > 1 ? Collections.singletonList((String)var1.get(0)) : var1;
      }

      private void updateMissingPreview() {
         if (!this.rebuilding && "__missing_analysis__".equals(this.currentCommand)) {
            List<String> var1 = this.selectedMissingVariables();
            ArrayList<String> var2 = new ArrayList<>();

            for (String var4 : var1) {
               int var5 = Data.getVarIndex(var4);
               if (var5 > 0 && !Data.isVarTypeString(var5)) {
                  var2.add(var4);
               }
            }

            String var6 = String.join(" ", var2);
            this.previewArea.setText(var6.isBlank() ? "describe " + String.join(" ", var1) : "misstable summarize " + var6);
            this.previewArea.setCaretPosition(0);
            this.flashCommandPreview();
         }
      }

      private void runMissingAnalysis() {
         final List var1 = this.selectedMissingVariables();
         final List var2 = this.selectedMissingGroups();
         final int var3 = this.missingMode.getSelectedIndex();
         if (var1.isEmpty()) {
            JOptionPane.showMessageDialog(this, "请至少选择一个需要检查的变量。", "尚未选择变量", 1);
         } else if (var3 > 0 && var2.isEmpty()) {
            JOptionPane.showMessageDialog(this, "当前查看方式需要至少一个分类变量。", "尚未选择分类变量", 1);
         } else {
            this.updateMissingPreview();
            final String var4 = this.previewArea.getText().trim();
            final boolean var5 = this.missingSeparateSummary.isSelected();
            final boolean var6 = this.missingOnly.isSelected();
            final int var7 = ((Number)this.missingMinCount.getValue()).intValue();
            final double var8 = ((Number)this.missingMinRate.getValue()).doubleValue();
            final String var10 = selected(this.missingSort);
            this.activeRunBefore = HxWorkbench.RunShape.capture();
            HxWorkbench.StataBridge.clearRunAudit();
            this.beginMonitoredRun(var4, false, 0);
            SwingWorker var11 = new SwingWorker<HxWorkbench.MissingRunOutcome, Void>() {
               protected HxWorkbench.MissingRunOutcome doInBackground() {
                  int var1x = var4.isBlank() ? 198 : HxWorkbench.StataBridge.execute("hxexecute, command(" + HxWorkbench.StataBridge.quote(var4) + ")", true);
                  if (var1x != 0) {
                     return HxWorkbench.MissingRunOutcome.failure(var4, var1x, "Stata 只读检查命令执行失败。");
                  } else {
                     try {
                        HxWorkbench.MissingAnalysisResult var2x = HxWorkbench.MissingAnalysisResult.compute(var1, var2, var3, var5, var6, var7, var8, var10);
                        return HxWorkbench.MissingRunOutcome.success(var4, var2x);
                     } catch (Throwable var3x) {
                        return HxWorkbench.MissingRunOutcome.failure(var4, 459, HxWorkbench.WorkbenchFrame.rootMessage(var3x));
                     }
                  }
               }

               @Override
               protected void done() {
                  HxWorkbench.MissingRunOutcome var1x;
                  try {
                     var1x = this.get();
                  } catch (Throwable var4x) {
                     var1x = HxWorkbench.MissingRunOutcome.failure(var4, 459, HxWorkbench.WorkbenchFrame.rootMessage(var4x));
                  }

                  String var2x = HxWorkbench.StataBridge.characteristic("hxtoolbox_history_status");
                  if (var2x.isBlank()) {
                     var2x = "请在 History 核对";
                  }

                  HxWorkbench.RunResult var3x = var1x.rc == 0
                     ? HxWorkbench.RunResult.capture(var4, 0, var2x)
                     : HxWorkbench.RunResult.failure(var4, var1x.rc, var1x.error);
                  WorkbenchFrame.this.finishMonitoredRun(var3x, HxWorkbench.RunShape.capture());
                  if (var1x.rc == 0) {
                     WorkbenchFrame.this.populateMissingResults(var1x.analysis);
                     WorkbenchFrame.this.monitorOutcome.setText("缺失值分析完成\n\n检查变量：" + var1.size() + "\n分类变量：" + var2.size() + "\n当前数据未被修改。");
                  } else {
                     JOptionPane.showMessageDialog(WorkbenchFrame.this, "缺失值分析失败：\n" + var1x.error, "分析失败", 0);
                  }
               }
            };
            var11.execute();
         }
      }

      private void populateMissingResults(HxWorkbench.MissingAnalysisResult var1) {
         this.missingResultTabs.removeAll();
         this.missingResultTabs.addTab("总体", this.resultTable(var1.overallColumns, var1.overallRows));

         for (Entry var3 : var1.separateRows.entrySet()) {
            this.missingResultTabs.addTab("按" + (String)var3.getKey(), this.resultTable(var1.separateColumns, (List<Object[]>)var3.getValue()));
         }

         if (!var1.jointRows.isEmpty()) {
            this.missingResultTabs.addTab(var1.groupNames.size() > 1 ? "联合明细" : "分类明细", this.resultTable(var1.jointColumns, var1.jointRows));
         }

         final JTable var9 = this.createResultTable(var1.recordColumns, var1.recordRows);
         this.missingRecordRows = new ArrayList<>(var1.recordObservationNumbers);
         JButton var10 = new JButton("在当前数据表查看这些记录");
         JButton var4 = new JButton("恢复全部数据");
         stylePrimaryButton(var10);
         styleSecondaryButton(var4);
         var10.addActionListener(var1x -> this.showMissingRecords(this.missingRecordRows));
         var4.addActionListener(var1x -> {
            this.dataModel.clearRowFilter();
            this.refreshDataset(false);
            this.selectDataView();
         });
         var9.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent var1) {
               if (var1.getClickCount() == 2 && var9.getSelectedRow() >= 0) {
                  int var2 = var9.convertRowIndexToModel(var9.getSelectedRow());
                  Object var3 = var9.getModel().getValueAt(var2, 0);
                  if (var3 instanceof Number) {
                     WorkbenchFrame.this.showMissingRecords(Collections.singletonList(((Number)var3).longValue()));
                  }
               }
            }
         });
         JPanel var5 = new JPanel(new BorderLayout(0, 8));
         var5.setBackground(SURFACE);
         JPanel var6 = new JPanel(new FlowLayout(0, 8, 6));
         var6.setOpaque(false);
         var6.add(var10);
         var6.add(var4);
         var5.add(var6, "North");
         var5.add(softScroll(var9), "Center");
         this.missingResultTabs.addTab("具体缺失记录", var5);
         this.missingChart.setResult(var1);
         this.missingChart.setChartType(selected(this.missingChartType));
         JPanel var7 = new JPanel(new BorderLayout(0, 8));
         var7.setBackground(SURFACE);
         JPanel var8 = new JPanel(new FlowLayout(0, 8, 6));
         var8.setOpaque(false);
         var8.add(new JLabel("图形："));
         var8.add(this.missingChartType);
         var7.add(var8, "North");
         var7.add(this.missingChart, "Center");
         this.missingResultTabs.addTab("图形", var7);
         this.selectResultView("missing", true);
         this.missingResultTabs.setSelectedIndex(0);
      }

      private JScrollPane resultTable(String[] var1, List<Object[]> var2) {
         return softScroll(this.createResultTable(var1, var2));
      }

      private JTable createResultTable(String[] var1, List<Object[]> var2) {
         DefaultTableModel var3 = new DefaultTableModel(var1, 0) {
            @Override
            public boolean isCellEditable(int var1, int var2x) {
               return false;
            }
         };

         for (Object[] var5 : var2) {
            var3.addRow(var5);
         }

         JTable var6 = new JTable(var3);
         var6.setAutoCreateRowSorter(true);
         var6.setRowHeight(25);
         var6.setFillsViewportHeight(true);
         var6.setShowVerticalLines(false);
         var6.setGridColor(new Color(232, 236, 241));
         var6.setSelectionBackground(ACCENT_SOFT);
         var6.setSelectionForeground(TEXT);
         var6.getTableHeader().setBackground(new Color(247, 249, 252));
         var6.getTableHeader().setFont(var6.getTableHeader().getFont().deriveFont(1, 11.0F));
         return var6;
      }

      private void showMissingRecords(List<Long> var1) {
         if (var1 != null && !var1.isEmpty()) {
            this.dataModel.showRows(var1);
            this.configureColumnWidths();
            this.dataLabel.setText("正在查看 " + var1.size() + " 条缺失记录 | 双击结果可定位单条观测");
            this.selectDataView();
         } else {
            JOptionPane.showMessageDialog(this, "当前筛选条件下没有具体缺失记录。", "没有记录", 1);
         }
      }

      private void runUtility(String var1, boolean var2) {
         if (this.runInProgress) {
            JOptionPane.showMessageDialog(this, "当前仍有命令在运行，请等待本次执行结束。", "正在运行", 1);
         } else {
            if (var2 && Data.getObsTotal() > 0L) {
               int var3 = JOptionPane.showConfirmDialog(this, "该操作可能清除当前内存数据。请确认正式数据已经保存。\n\n继续执行：" + var1 + "？", "确认载入测试数据", 2, 2);
               if (var3 != 0) {
                  return;
               }
            }

            String var6 = var1.trim().toLowerCase(Locale.ROOT);
            boolean var4 = var6.startsWith("hxthreads ") || var6.startsWith("hxtestdata ");
            String var5 = var4 ? var1 : "hxexecute, command(" + HxWorkbench.StataBridge.quote(var1) + ")";
            this.executeMonitoredCommand(var1, var5, var2, var0 -> {});
         }
      }

      private void refreshVariableControls() {
         List var1 = HxWorkbench.StataBridge.variableNames();
         replaceComboItems(this.depvar, var1);
         replaceComboItems(this.panel, var1);
         replaceComboItems(this.time, var1);
         replaceComboItems(this.cluster, var1);
         replaceComboItems(this.genericWeightVar, var1);
         replaceListItems(this.variables, var1);
         replaceListItems(this.absorb, var1);
         replaceListItems(this.endog, var1);
         replaceListItems(this.instruments, var1);
         replaceComboItems(this.oneClickY, var1);
         replaceComboItems(this.oneClickX, var1);
         replaceComboItems(this.oneClickCluster, var1);
         replaceListItems(this.oneClickRequired, var1);
         replaceListItems(this.oneClickCandidates, var1);
         replaceListItems(this.oneClickAbsorb, var1);
         replaceComboItems(this.didUnit, var1);
         replaceComboItems(this.didTime, var1);
         replaceComboItems(this.didTreat, var1);
         replaceComboItems(this.didPost, var1);
         replaceComboItems(this.didEvent, var1);
         replaceComboItems(this.didEventCode, var1);
         replaceComboItems(this.regressX, var1);
         replaceListItems(this.regressControls, var1);
         replaceComboItems(this.regressFactor, var1);
         replaceComboItems(this.regressInteractionA, var1);
         replaceComboItems(this.regressInteractionB, var1);
         replaceComboItems(this.regressLagVar, var1);
         replaceComboItems(this.regressWeightVar, var1);
      }

      private void updatePreview() {
         if (!this.rebuilding && !this.currentCommand.isBlank()) {
            if (this.baselineTaskActive) {
               this.updateBaselinePreview();
            } else if ("regress".equals(this.currentCommand) && this.regressWorkspaceActive) {
               this.updateRegressPreview();
            } else if ("oneclick".equals(this.currentCommand) || "oneclick_robustness".equals(this.currentCommand)) {
               this.updateOneClickPreview();
            } else if ("did_builder".equals(this.currentCommand)) {
               this.updateDidBuilderPreview();
            } else if (Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_box", "did_trends", "twoway").contains(this.currentCommand)) {
               this.updateSpecialGraphPreview();
            } else {
               HxWorkbench.StataBridge.execute("quietly hxpick, target(all) action(clear)", false);
               this.pushSelections("vars", this.variables);
               this.pushSelections("absorb", this.absorb);
               this.pushSelections("endog", this.endog);
               this.pushSelections("inst", this.instruments);
               StringBuilder var1 = new StringBuilder("quietly hxpreview");
               this.appendOption(var1, "depvar", selected(this.depvar));
               this.appendOption(var1, "newvar", this.newvar.getText());
               this.appendOption(var1, "model", selected(this.model));
               this.appendOption(var1, "expression", this.expression.getText());
               this.appendOption(var1, "usingfile", this.usingFile.getText());
               this.appendOption(var1, "panel", selected(this.panel));
               this.appendOption(var1, "time", selected(this.time));
               this.appendOption(var1, "vce", selected(this.vce));
               this.appendOption(var1, "cluster", selected(this.cluster));
               this.appendOption(var1, "ifcond", this.ifCondition.getText());
               this.appendOption(var1, "incond", this.inCondition.getText());
               String genericWeight = selected(this.genericWeightType);
               if (!"无".equals(genericWeight)) {
                  this.appendOption(var1, "weight", genericWeight);
                  this.appendOption(var1, "weightvar", selected(this.genericWeightVar));
               }
               this.appendOption(var1, "options", this.options.getText());
               HxWorkbench.StataBridge.execute(var1.toString(), false);
               this.rebuilding = true;
               this.previewArea.setText(HxWorkbench.StataBridge.characteristic("hxtoolbox_preview"));
               this.previewArea.setCaretPosition(0);
               this.rebuilding = false;
               this.flashCommandPreview();
               this.updateGraphPreviewFromCurrentCommand();
            }
         }
      }

      private void updateSpecialGraphPreview() {
         String var1;
         if (Arrays.asList("histogram", "kdensity").contains(this.currentCommand)) {
            var1 = this.currentCommand + " " + selected(this.depvar);
            if (!this.ifCondition.getText().trim().isBlank()) {
               var1 = var1 + " if " + this.ifCondition.getText().trim();
            }

            if (!this.options.getText().trim().isBlank()) {
               var1 = var1 + ", " + this.options.getText().trim();
            }
         } else if (Arrays.asList("scatter", "lfit").contains(this.currentCommand)) {
            String var2 = this.variables.getSelectedValuesList().isEmpty() ? "" : this.variables.getSelectedValuesList().get(0);
            var1 = "twoway " + this.currentCommand + " " + selected(this.depvar) + " " + var2;
            if (!this.ifCondition.getText().trim().isBlank()) {
               var1 = var1 + " if " + this.ifCondition.getText().trim();
            }

            if (!this.options.getText().trim().isBlank()) {
               var1 = var1 + ", " + this.options.getText().trim();
            }
         } else if ("graph_box".equals(this.currentCommand)) {
            String var6 = selected(this.depvar);
            var1 = var6.isBlank() ? "graph box" : "graph box " + var6;
            if (!selected(this.panel).isBlank()) {
               var1 = var1 + ", over(" + selected(this.panel) + ")";
            }

            if (!this.ifCondition.getText().trim().isBlank()) {
               int var3 = var1.indexOf(44);
               String var4 = var3 >= 0 ? var1.substring(var3) : "";
               var1 = (var3 >= 0 ? var1.substring(0, var3) : var1) + " if " + this.ifCondition.getText().trim() + var4;
            }

            if (!this.options.getText().trim().isBlank()) {
               var1 = var1 + (var1.contains(",") ? " " : ", ") + this.options.getText().trim();
            }
         } else if ("did_trends".equals(this.currentCommand)) {
            var1 = "hxtrendplot " + selected(this.depvar);
            if (!this.ifCondition.getText().trim().isBlank()) {
               var1 = var1 + " if " + this.ifCondition.getText().trim();
            }

            var1 = var1 + ", group(" + selected(this.panel) + ") time(" + selected(this.time) + ")";
            if (!this.options.getText().trim().isBlank()) {
               var1 = var1 + " " + this.options.getText().trim();
            }
         } else {
            var1 = "twoway " + this.expression.getText().trim();
            if (!this.options.getText().trim().isBlank()) {
               var1 = var1 + ", " + this.options.getText().trim();
            }
         }

         this.rebuilding = true;
         this.previewArea.setText(var1.trim());
         this.rebuilding = false;
         this.flashCommandPreview();
         this.updateGraphPreviewFromCurrentCommand();
      }

      private void updateGraphPreviewFromCurrentCommand() {
         if (!this.previewMode) {
            String var1 = selected(this.depvar);
            String var2 = this.variables.getSelectedValuesList().isEmpty() ? "" : this.variables.getSelectedValuesList().get(0);
            if ("graph_box".equals(this.currentCommand)) {
               var2 = selected(this.panel);
            }

            if ("did_trends".equals(this.currentCommand)) {
               this.graphPreview.loadTrend(var1, selected(this.time), selected(this.panel));
            } else if (Arrays.asList("scatter", "lfit").contains(this.currentCommand)) {
               this.graphPreview.loadXY(var1, var2, "lfit".equals(this.currentCommand));
            } else if (Arrays.asList("histogram", "kdensity", "graph_box").contains(this.currentCommand)) {
               this.graphPreview.loadDistribution(var1, this.currentCommand);
            } else {
               this.graphPreview.showMessage("运行图形命令后，Stata 正式图形会在 Graph 窗口显示。\n当前预览用于核对变量与大致关系。");
            }

            if ("graph".equals(this.activeCategoryCode) || "did".equals(this.activeCategoryCode)) {
               this.selectResultView("graph", true);
            }
         }
      }

      private void updateOneClickPreview() {
         List var1 = this.oneClickCandidates.getSelectedValuesList();
         int var2 = var1.size();
         BigInteger var3 = var2 <= 0 ? BigInteger.ZERO : BigInteger.ONE.shiftLeft(var2).subtract(BigInteger.ONE);
         String var4 = "候选变量：" + var2 + " 个　预计组合：" + var3 + " 个";
         if (var2 == 1) {
            var4 = var4 + "　⚠ 至少再选择 1 个候选控制变量";
         }

         if (var3.compareTo(BigInteger.valueOf(4096L)) > 0) {
            var4 = var4 + "　⚠ 组合较多，外部命令可能运行较久";
         }

         this.oneClickScale.setText(var4);
         this.oneClickScale.setForeground(var3.compareTo(BigInteger.valueOf(65536L)) > 0 ? DANGER : TEXT);
         String var5 = selected(this.oneClickY);
         String var6 = selected(this.oneClickX);
         boolean var7 = "oneclick_robustness".equals(this.currentCommand);
         StringBuilder var8 = new StringBuilder(var7 ? "oneclick_robustness" : "oneclick");
         if (!var5.isBlank()) {
            var8.append(" ").append(var5);
         }

         if (!var1.isEmpty()) {
            var8.append(" ").append(String.join(" ", var1));
         }

         ArrayList var9 = new ArrayList();
         if (!var6.isBlank()) {
            var9.add(var6);
         }

         var9.addAll(this.oneClickRequired.getSelectedValuesList());
         var8.append(",");
         if (!var9.isEmpty()) {
            var8.append(" fix(").append(String.join(" ", var9)).append(")");
         }

         if (!var7) {
            double var10 = this.parseOneClickAlpha();
            String var12 = selected(this.oneClickEstimator);
            String var13 = "regress".equals(var12) ? "reg" : var12;
            var8.append(" p(").append(String.format(Locale.ROOT, "%.2f", var10)).append(")");
            if (!var13.isBlank()) {
               var8.append(" m(").append(var13).append(")");
            }

            String var14 = this.buildOneClickModelOptions();
            if (!var14.isBlank()) {
               var8.append(" o(").append(var14).append(")");
            }

            if (Arrays.asList("logit", "probit").contains(var12)) {
               var8.append(" z");
            }
         }

         this.oneClickGeneratedCommand = var8.toString().trim();
         this.rebuilding = true;
         this.previewArea.setText(this.oneClickGeneratedCommand);
         this.rebuilding = false;
         this.flashCommandPreview();
         this.exactOneClickCommand.setText(this.previewArea.getText());
         String hxO = this.exactOneClickModelOptions.getText().trim();
         String hxZ = this.exactOneClickOtherOptions.getText().trim();
         if (!hxO.isBlank()) this.exactOneClickCommand.append(" o(" + hxO + ")");
         if (!hxZ.isBlank()) this.exactOneClickCommand.append(" " + hxZ);
      }

      private void updateDidBuilderPreview() {
         String var1 = selected(this.didAction);
         String var2 = "";
         String var3 = this.didNewVar.getText().trim();
         if (var1.startsWith("生成政策后")) {
            if (var3.isBlank()) {
               var3 = "post";
            }

            String var4 = selected(this.didTime);
            if (!var4.isBlank() && !this.didPolicyTime.getText().trim().isBlank()) {
               var2 = "generate byte " + var3 + " = " + var4 + " >= " + this.didPolicyTime.getText().trim() + " if !missing(" + var4 + ")";
            }
         } else if (var1.startsWith("生成交互项")) {
            if (var3.isBlank()) {
               var3 = "did";
            }

            String var13 = selected(this.didTreat);
            String var5 = selected(this.didPost);
            if (!var13.isBlank() && !var5.isBlank()) {
               var2 = "generate byte " + var3 + " = " + var13 + " * " + var5 + " if !missing(" + var13 + ", " + var5 + ")";
            }
         } else if (var1.startsWith("生成相对")) {
            if (var3.isBlank()) {
               var3 = "event_time";
            }

            String var14 = selected(this.didTime);
            if (!var14.isBlank() && !this.didPolicyTime.getText().trim().isBlank()) {
               var2 = "generate int " + var3 + " = " + var14 + " - " + this.didPolicyTime.getText().trim() + " if !missing(" + var14 + ")";
            }
         } else if (var1.startsWith("生成事件研究编码")) {
            if (var3.isBlank()) {
               var3 = "event_code";
            }

            String var15 = selected(this.didEvent);
            if (!var15.isBlank()) {
               var2 = "hxdidencode " + var15 + ", generate(" + var3 + ") base(" + this.didBasePeriod.getValue() + ")";
            }
         } else if (var1.startsWith("政策前联合")) {
            var2 = this.buildAutomaticPretrendTestCommand();
            if (var2.isBlank() && !this.previewMode) {
               this.statusLabel.setText("请先完成事件研究编码，并选择 treat 与 event_code；工具会自动生成政策前联合检验。");
            }
         } else {
            String var16 = selected(this.didEstimator);
            String var17 = selected(this.depvar);
            String var6;
            if (var1.startsWith("事件研究")) {
               String var18 = selected(this.didTreat);
               String var20 = selected(this.didEventCode);
               String var9 = HxWorkbench.StataBridge.characteristic("hxtoolbox_event_code");
               if (!this.previewMode && !var20.isBlank() && !var20.equals(var9)) {
                  this.statusLabel.setText("事件研究回归前，请先用“生成事件研究编码”创建并选择 event_code。");
                  var6 = "";
               } else {
                  var6 = !var18.isBlank() && !var20.isBlank() ? "i." + var18 + "##i." + var20 : "";
               }
            } else {
               String var7 = selected(this.didTreat);
               String var8 = selected(this.didPost);
               var6 = !var7.isBlank() && !var8.isBlank() ? "i." + var7 + "##i." + var8 : "";
            }

            if (!var16.isBlank() && !var17.isBlank() && !var6.isBlank()) {
               ArrayList var19 = new ArrayList();
               var19.add(var6);
               var19.addAll(this.variables.getSelectedValuesList());
               String var21 = selected(this.didUnit);
               String var22 = selected(this.didTime);
               if ("regress".equals(var16)) {
                  if (this.didUnitFE.isSelected() && !var21.isBlank()) {
                     var19.add("i." + var21);
                  }

                  if (this.didTimeFE.isSelected() && !var22.isBlank()) {
                     var19.add("i." + var22);
                  }
               }

               StringBuilder var10 = new StringBuilder(var16).append(" ").append(var17).append(" ").append(String.join(" ", var19));
               if (!this.ifCondition.getText().trim().isBlank()) {
                  var10.append(" if ").append(this.ifCondition.getText().trim());
               }

               ArrayList var11 = new ArrayList();
               if ("reghdfe".equals(var16)) {
                  LinkedHashSet var12 = new LinkedHashSet();
                  if (this.didUnitFE.isSelected() && !var21.isBlank()) {
                     var12.add(var21);
                  }

                  if (this.didTimeFE.isSelected() && !var22.isBlank()) {
                     var12.add(var22);
                  }

                  if (!var12.isEmpty()) {
                     var11.add("absorb(" + String.join(" ", var12) + ")");
                  }
               }

               if ("robust".equals(selected(this.vce))) {
                  var11.add("vce(robust)");
               }

               if ("cluster".equals(selected(this.vce)) && !selected(this.cluster).isBlank()) {
                  var11.add("vce(cluster " + selected(this.cluster) + ")");
               }

               if (!this.options.getText().trim().isBlank()) {
                  var11.add(this.options.getText().trim());
               }

               if (!var11.isEmpty()) {
                  var10.append(", ").append(String.join(" ", var11));
               }

               var2 = var10.toString();
            }
         }

         this.rebuilding = true;
         this.previewArea.setText(var2.trim());
         this.rebuilding = false;
         this.flashCommandPreview();
      }

      private String buildAutomaticPretrendTestCommand() {
         String var1 = selected(this.didTreat);
         String var2 = selected(this.didEventCode);
         if (!var1.isBlank() && !var2.isBlank()) {
            String var3 = HxWorkbench.StataBridge.characteristic("hxtoolbox_event_code");
            String var4 = HxWorkbench.StataBridge.characteristic("hxtoolbox_event_source");
            String var5 = HxWorkbench.StataBridge.characteristic("hxtoolbox_event_shift");
            String var6 = HxWorkbench.StataBridge.characteristic("hxtoolbox_event_base_relative");
            if (this.previewMode || var2.equals(var3) && !var4.isBlank() && !var5.isBlank() && !var6.isBlank()) {
               if (!this.previewMode || !var4.isBlank() && !var5.isBlank() && !var6.isBlank()) {
                  int var7;
                  int var8;
                  try {
                     var7 = Integer.parseInt(var5.trim());
                     var8 = Integer.parseInt(var6.trim());
                  } catch (Exception var20) {
                     return "";
                  }

                  int var9 = HxWorkbench.safe(() -> Data.getVarIndex(var4), -1);
                  if (var9 > 0 && !Data.isVarTypeString(var9)) {
                     TreeSet<Integer> var10 = new TreeSet<>();
                     long var11 = Data.getObsTotal();

                     for (long var13 = 1L; var13 <= var11; var13++) {
                        long var15 = var13;
                        double var17 = HxWorkbench.safe(() -> Data.getNum(var9, var15), Double.NaN);
                        if (!Missing.isMissing(var17) && Math.rint(var17) == var17) {
                           int var19 = (int)var17;
                           if (var19 < 0 && var19 != var8) {
                              var10.add(var19 + var7);
                           }
                        }
                     }

                     if (var10.isEmpty()) {
                        return "";
                     } else {
                        ArrayList<String> var21 = new ArrayList<>();

                        for (Integer var22 : var10) {
                           var21.add("1." + var1 + "#" + var22 + "." + var2);
                        }

                        return "testparm " + String.join(" ", var21);
                     }
                  } else {
                     return "";
                  }
               } else {
                  return "testparm 1." + var1 + "#0." + var2 + " 1." + var1 + "#1." + var2;
               }
            } else {
               return "";
            }
         } else {
            return "";
         }
      }

      private double parseOneClickAlpha() {
         String var1 = selected(this.oneClickP);
         if (var1.startsWith("0.01")) {
            return 0.01;
         } else {
            return var1.startsWith("0.10") ? 0.1 : 0.05;
         }
      }

      private String buildOneClickModelOptions() {
         ArrayList var1 = new ArrayList();
         if ("reghdfe".equals(selected(this.oneClickEstimator)) && !this.oneClickAbsorb.getSelectedValuesList().isEmpty()) {
            var1.add("absorb(" + String.join(" ", this.oneClickAbsorb.getSelectedValuesList()) + ")");
         }

         if ("robust".equals(selected(this.oneClickVce))) {
            var1.add("vce(robust)");
         }

         if ("cluster".equals(selected(this.oneClickVce)) && !selected(this.oneClickCluster).isBlank()) {
            var1.add("vce(cluster " + selected(this.oneClickCluster) + ")");
         }

         return String.join(" ", var1);
      }

      private void runCurrentCommand() {
         if ("__convert_dta__".equals(this.currentCommand)) {
            this.runConvertDta();
         } else if ("__missing_analysis__".equals(this.currentCommand)) {
            this.runMissingAnalysis();
         } else if ("oneclick".equals(this.currentCommand) || "oneclick_robustness".equals(this.currentCommand)) {
            this.runOneClick();
         } else if (!"did_builder".equals(this.currentCommand) || this.validateDidBeforeRun()) {
            if (this.validateOrdinaryCommandBeforeRun()
               && (!this.baselineTaskActive || this.validateBaselineBeforeRun())
               && this.validateFocusedEstimationBeforeRun()
               && (!"regress".equals(this.currentCommand) || !this.regressWorkspaceActive || this.validateRegressBeforeRun())) {
               String var1 = this.previewArea.getText().trim();
               if (var1.isEmpty()) {
                  JOptionPane.showMessageDialog(this, "请先完整选择命令需要的变量或参数。", "命令尚未完整", 1);
               } else if ("did_builder".equals(this.currentCommand)) {
                  String var2 = selected(this.didAction);
                  String var3 = this.didNewVar.getText().trim();
                  this.executeMonitoredCommand(var1, "hxexecute, command(" + HxWorkbench.StataBridge.quote(var1) + ")", true, var3x -> {
                     if (var3x.rc == 0 && !var3.isBlank()) {
                        if (var2.startsWith("生成政策后")) {
                           this.didPost.setSelectedItem(var3);
                        } else if (var2.startsWith("生成相对")) {
                           this.didEvent.setSelectedItem(var3);
                        } else if (var2.startsWith("生成事件研究编码")) {
                           this.didEventCode.setSelectedItem(var3);
                        }

                        this.statusLabel.setText("已完成当前 DID 数据准备步骤；新变量已自动带入后续对应位置。");
                     }
                  });
               } else {
                  this.executeMonitoredCommand(var1, "hxexecute, command(" + HxWorkbench.StataBridge.quote(var1) + ")", true, var0 -> {});
               }
            }
         }
      }

      private boolean validateFocusedEstimationBeforeRun() {
         List<String> estimators = Arrays.asList(
            "areg", "reghdfe", "qreg", "rreg", "cnsreg", "vwls", "eivreg", "newey", "prais",
            "xtreg", "xtlogit", "xtprobit", "logit", "probit", "poisson", "nbreg", "ppmlhdfe", "ivregress", "ivreghdfe",
            "didregress", "xtdidregress"
         );
         if (!estimators.contains(this.currentCommand)) {
            return true;
         }

         if (this.flag("has_depvar") && selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择因变量。", "因变量缺失", 1);
            return false;
         }

         if (Arrays.asList("didregress", "xtdidregress").contains(this.currentCommand)) {
            String treatment = selected(this.panel);
            String didTime = selected(this.time);
            List<String> didGroups = this.absorb.getSelectedValuesList();
            if (treatment.isBlank() || didTime.isBlank() || didGroups.isEmpty()) {
               JOptionPane.showMessageDialog(this, "DID 需要选择处理变量、time() 时间变量和至少 1 个 group() 变量。", "DID 设置尚未完整", 1);
               return false;
            }
            String outcome = selected(this.depvar);
            if (treatment.equals(outcome) || didTime.equals(outcome) || didGroups.contains(outcome)) {
               JOptionPane.showMessageDialog(this, "结果变量不能同时作为处理变量、时间变量或 group() 变量。", "DID 变量角色重复", 2);
               return false;
            }
            if (didGroups.contains(treatment) || didGroups.contains(didTime) || treatment.equals(didTime)) {
               JOptionPane.showMessageDialog(this, "处理变量、时间变量和 group() 变量需要使用不同的数据角色。", "DID 变量角色重复", 2);
               return false;
            }
            LinkedHashSet<String> didControls = new LinkedHashSet<>(this.variables.getSelectedValuesList());
            didControls.retainAll(Arrays.asList(outcome, treatment, didTime));
            if (!didControls.isEmpty()) {
               JOptionPane.showMessageDialog(this, "协变量 / 控制变量中重复选择了 DID 核心变量：" + String.join("、", didControls), "DID 变量角色重复", 2);
               return false;
            }
         }

         if ("areg".equals(this.currentCommand) && this.absorb.getSelectedValuesList().size() != 1) {
            JOptionPane.showMessageDialog(this, "areg 需要且只能选择 1 个 absorb() 固定效应变量。", "固定效应设置尚未完整", 1);
            return false;
         }

         String structured = this.expression.getText().trim();
         if ("cnsreg".equals(this.currentCommand) && structured.isBlank()) {
            JOptionPane.showMessageDialog(this, "cnsreg 需要填写已经定义好的 constraint 编号。", "约束设置尚未完整", 1);
            return false;
         }
         if ("eivreg".equals(this.currentCommand) && structured.isBlank()) {
            JOptionPane.showMessageDialog(this, "eivreg 需要填写 reliab() 中的变量及可靠度。", "可靠度设置尚未完整", 1);
            return false;
         }
         if ("newey".equals(this.currentCommand)) {
            if (structured.isBlank() || !structured.matches("\\d+")) {
               JOptionPane.showMessageDialog(this, "newey 需要填写非负整数 lag 阶数，例如 4。", "lag 设置尚未完整", 1);
               return false;
            }
         }
         if ("qreg".equals(this.currentCommand) && !structured.isBlank()) {
            try {
               double q = Double.parseDouble(structured);
               if (!(q > 0.0 && q < 1.0)) {
                  throw new NumberFormatException();
               }
            } catch (NumberFormatException ex) {
               JOptionPane.showMessageDialog(this, "quantile() 请填写 0 到 1 之间的数值，例如 0.25。", "分位点无效", 1);
               return false;
            }
         }

         if (this.flag("has_iv")) {
            List<String> var1 = this.endog.getSelectedValuesList();
            List<String> var2 = this.instruments.getSelectedValuesList();
            if (var1.isEmpty() || var2.isEmpty()) {
               JOptionPane.showMessageDialog(this, "工具变量回归需要同时选择内生变量和工具变量。", "IV 设置尚未完整", 1);
               return false;
            }

            LinkedHashSet<String> var3 = new LinkedHashSet<>(var1);
            var3.retainAll(var2);
            if (!var3.isEmpty()) {
               JOptionPane.showMessageDialog(this, "同一变量不能同时作为内生变量和工具变量：" + String.join("、", var3), "IV 变量角色重复", 2);
               return false;
            }

            String var4 = selected(this.depvar);
            if (var1.contains(var4) || var2.contains(var4)) {
               JOptionPane.showMessageDialog(this, "因变量不能同时作为内生解释变量或工具变量。", "IV 变量角色重复", 2);
               return false;
            }

            LinkedHashSet<String> var5 = new LinkedHashSet<>(this.variables.getSelectedValuesList());
            var5.retainAll(var1);
            if (!var5.isEmpty()) {
               JOptionPane.showMessageDialog(this, "正常解释变量 / 控制中重复选择了内生变量：" + String.join("、", var5), "IV 变量角色重复", 2);
               return false;
            }

            var5 = new LinkedHashSet<>(this.variables.getSelectedValuesList());
            var5.retainAll(var2);
            if (!var5.isEmpty()) {
               JOptionPane.showMessageDialog(this, "正常解释变量 / 控制中重复选择了工具变量：" + String.join("、", var5), "IV 变量角色重复", 2);
               return false;
            }
         }

         if ("cluster".equalsIgnoreCase(selected(this.vce)) && selected(this.cluster).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择 Cluster 后，请指定聚类变量。", "聚类变量缺失", 1);
            return false;
         }

         if (this.flag("has_weight")
            && !"无".equals(selected(this.genericWeightType))
            && selected(this.genericWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后，请指定权重变量。", "权重变量缺失", 1);
            return false;
         }

         return true;
      }

      private boolean validateOrdinaryCommandBeforeRun() {
         String command = this.currentCommand;
         if (Arrays.asList("histogram", "kdensity", "graph_box").contains(command) && selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择要绘制的变量。", "图形设置尚未完整", 1);
            return false;
         }
         if (Arrays.asList("scatter", "lfit").contains(command)) {
            if (selected(this.depvar).isBlank() || this.variables.getSelectedValuesList().size() != 1) {
               JOptionPane.showMessageDialog(this, "请选择纵轴 Y，并且只选择 1 个横轴 X。", "图形设置尚未完整", 1);
               return false;
            }
         }
         if ("twoway".equals(command) && this.expression.getText().trim().isBlank()) {
            JOptionPane.showMessageDialog(this, "请填写 twoway 图层表达式。", "图形设置尚未完整", 1);
            return false;
         }
         if ("did_trends".equals(command)
            && (selected(this.depvar).isBlank() || selected(this.panel).isBlank() || selected(this.time).isBlank())) {
            JOptionPane.showMessageDialog(this, "趋势图需要结果变量、处理组变量和时间变量。", "趋势图设置尚未完整", 1);
            return false;
         }
         if ("generate".equals(command) && (this.newvar.getText().trim().isBlank() || this.expression.getText().trim().isBlank())) {
            JOptionPane.showMessageDialog(this, "generate 需要新变量名和计算公式。", "变量生成设置尚未完整", 1);
            return false;
         }
         if ("replace".equals(command) && (selected(this.depvar).isBlank() || this.expression.getText().trim().isBlank())) {
            JOptionPane.showMessageDialog(this, "replace 需要选择原变量并填写新的计算表达式。", "变量修改设置尚未完整", 1);
            return false;
         }
         if (Arrays.asList("encode", "decode").contains(command)
            && (selected(this.depvar).isBlank() || this.newvar.getText().trim().isBlank())) {
            JOptionPane.showMessageDialog(this, command + " 需要原变量和新变量名。", "转换设置尚未完整", 1);
            return false;
         }
         if (Arrays.asList("destring", "tostring").contains(command)) {
            if (selected(this.depvar).isBlank()) {
               JOptionPane.showMessageDialog(this, "请选择要转换的原变量。", "转换设置尚未完整", 1);
               return false;
            }
            if (!"覆盖原变量".equals(selected(this.model)) && this.newvar.getText().trim().isBlank()) {
               JOptionPane.showMessageDialog(this, "选择生成新变量时，请填写新变量名。", "转换设置尚未完整", 1);
               return false;
            }
         }
         if ("winsor2".equals(command) && this.variables.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "请选择至少 1 个需要缩尾的变量。", "缩尾设置尚未完整", 1);
            return false;
         }
         if (Arrays.asList("keep", "drop").contains(command)) {
            if ("处理变量".equals(selected(this.model)) && this.variables.getSelectedValuesList().isEmpty()) {
               JOptionPane.showMessageDialog(this, command + " 选择“处理变量”时，需要选择至少 1 个变量。", "样本/变量处理设置尚未完整", 1);
               return false;
            }
            if ("处理样本".equals(selected(this.model)) && this.ifCondition.getText().trim().isBlank()) {
               JOptionPane.showMessageDialog(this, command + " 选择“处理样本”时，需要填写 if 条件。", "样本/变量处理设置尚未完整", 1);
               return false;
            }
         }
         if ("merge".equals(command)
            && (this.variables.getSelectedValuesList().isEmpty() || this.usingFile.getText().trim().isBlank() || selected(this.model).isBlank())) {
            JOptionPane.showMessageDialog(this, "merge 需要合并关系、关联变量和 using 文件。", "合并设置尚未完整", 1);
            return false;
         }
         if ("append".equals(command) && this.usingFile.getText().trim().isBlank()) {
            JOptionPane.showMessageDialog(this, "append 需要选择 using 文件。", "追加设置尚未完整", 1);
            return false;
         }
         if ("reshape".equals(command)
            && (this.expression.getText().trim().isBlank() || selected(this.panel).isBlank() || selected(this.time).isBlank())) {
            JOptionPane.showMessageDialog(this, "reshape 需要 stub、i() 个体标识和 j() 维度变量。", "reshape 设置尚未完整", 1);
            return false;
         }
         if ("collapse".equals(command) && this.variables.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "collapse 需要选择至少 1 个汇总变量。", "汇总设置尚未完整", 1);
            return false;
         }
         if ("xtset".equals(command) && selected(this.panel).isBlank()) {
            JOptionPane.showMessageDialog(this, "xtset 需要选择面板变量。", "面板设置尚未完整", 1);
            return false;
         }
         if ("tsset".equals(command) && selected(this.time).isBlank()) {
            JOptionPane.showMessageDialog(this, "tsset 需要选择时间变量；纯时间序列时面板变量可以留空。", "时间设置尚未完整", 1);
            return false;
         }
         if ("tabstat".equals(command) && this.variables.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "tabstat 需要选择至少 1 个要汇总的变量。", "描述统计设置尚未完整", 1);
            return false;
         }
         if ("ttest".equals(command)) {
            if (this.variables.getSelectedValuesList().size() != 1 || this.expression.getText().trim().isBlank()) {
               JOptionPane.showMessageDialog(this, "ttest 需要选择 1 个被检验变量，并按检验方式填写比较值、分组变量或第二变量。", "t 检验设置尚未完整", 1);
               return false;
            }
         }
         if ("tabulate".equals(command)) {
            int nvars = this.variables.getSelectedValuesList().size();
            if (nvars < 1 || nvars > 2) {
               JOptionPane.showMessageDialog(this, "tabulate 请选择 1 个变量做频数表，或 2 个变量做列联表。", "频数列联设置尚未完整", 1);
               return false;
            }
         }
         if (Arrays.asList("test", "lincom").contains(command) && this.expression.getText().trim().isBlank()) {
            JOptionPane.showMessageDialog(this, command + " 需要填写要检验或计算的系数表达式。", "后估计设置尚未完整", 1);
            return false;
         }
         if ("predict".equals(command) && this.newvar.getText().trim().isBlank()) {
            JOptionPane.showMessageDialog(this, "predict 需要填写新变量名。", "预测设置尚未完整", 1);
            return false;
         }
         return true;
      }

      private boolean validateDidBeforeRun() {
         String var1 = selected(this.didAction);
         if (var1.startsWith("生成交互项")) {
            String var2 = selected(this.didTreat);
            String var3 = selected(this.didPost);
            if (!this.validateBinaryDidVariable(var2, "处理组 treat")) {
               return false;
            }

            if (!this.validateBinaryDidVariable(var3, "政策后 post")) {
               return false;
            }
         } else if (var1.startsWith("生成事件研究编码")) {
            String var9 = selected(this.didEvent);
            if (var9.isBlank()) {
               JOptionPane.showMessageDialog(this, "请选择相对政策时间 event_time。", "事件研究编码设置尚未完整", 1);
               return false;
            }

            if (!this.eventBaseExists(var9, ((Number)this.didBasePeriod.getValue()).intValue())) {
               return false;
            }
         } else if (var1.startsWith("DID 交互回归")) {
            String var10 = selected(this.depvar);
            String var13 = selected(this.didTreat);
            String var4 = selected(this.didPost);
            if (var10.isBlank() || var13.isBlank() || var4.isBlank()) {
               JOptionPane.showMessageDialog(this, "请选择 Y、处理组 treat 和政策后 post。", "DID 设置尚未完整", 1);
               return false;
            }

            if (!this.validateBinaryDidVariable(var13, "处理组 treat")) {
               return false;
            }

            if (!this.validateBinaryDidVariable(var4, "政策后 post")) {
               return false;
            }

            LinkedHashSet var5 = new LinkedHashSet<>(Arrays.asList(var10, var13, var4));
            if (var5.size() < 3) {
               JOptionPane.showMessageDialog(this, "Y、treat 和 post 必须使用不同变量。", "DID 变量角色重复", 2);
               return false;
            }

            if (!this.validateDidPanelSettings()) {
               return false;
            }

            for (String var7 : this.variables.getSelectedValuesList()) {
               if (var5.contains(var7)) {
                  JOptionPane.showMessageDialog(this, "控制变量中重复选择了 DID 核心变量：" + var7, "DID 变量角色重复", 2);
                  return false;
               }
            }
         } else if (var1.startsWith("事件研究回归")) {
            String var11 = selected(this.depvar);
            String var14 = selected(this.didTreat);
            String var16 = selected(this.didEventCode);
            if (var11.isBlank() || var14.isBlank() || var16.isBlank()) {
               JOptionPane.showMessageDialog(this, "请选择 Y、处理组 treat 和事件研究编码 event_code。", "事件研究设置尚未完整", 1);
               return false;
            }

            if (!this.validateBinaryDidVariable(var14, "处理组 treat")) {
               return false;
            }

            String var18 = HxWorkbench.StataBridge.characteristic("hxtoolbox_event_code");
            if (!this.previewMode && !var16.equals(var18)) {
               JOptionPane.showMessageDialog(this, "当前 event_code 不是由本工作台的“生成事件研究编码”步骤准备的变量。\n请先选择“生成事件研究编码 event_code”并运行一次，再回来做事件研究回归。", "请先准备 event_code", 1);
               return false;
            }

            LinkedHashSet var19 = new LinkedHashSet<>(Arrays.asList(var11, var14, var16));
            if (var19.size() < 3) {
               JOptionPane.showMessageDialog(this, "Y、treat 和 event_code 必须使用不同变量。", "事件研究变量角色重复", 2);
               return false;
            }

            if (!this.validateDidPanelSettings()) {
               return false;
            }

            for (String var8 : this.variables.getSelectedValuesList()) {
               if (var19.contains(var8)) {
                  JOptionPane.showMessageDialog(this, "控制变量中重复选择了事件研究核心变量：" + var8, "事件研究变量角色重复", 2);
                  return false;
               }
            }
         } else if (var1.startsWith("政策前联合")) {
            String var12 = selected(this.didTreat);
            String var15 = selected(this.didEventCode);
            if (!this.validateBinaryDidVariable(var12, "处理组 treat")) {
               return false;
            }

            if (var15.isBlank()) {
               JOptionPane.showMessageDialog(this, "请选择之前生成的 event_code。", "联合检验设置尚未完整", 1);
               return false;
            }

            String var17 = this.buildAutomaticPretrendTestCommand();
            if (var17.isBlank()) {
               JOptionPane.showMessageDialog(this, "当前无法识别可检验的政策前事件期。请确认已先生成 event_time 和 event_code，且政策前存在至少一个非基准期。", "没有可自动检验的政策前系数", 1);
               return false;
            }
         }

         return true;
      }

      private boolean eventBaseExists(String var1, int var2) {
         int var3 = HxWorkbench.safe(() -> Data.getVarIndex(var1), -1);
         if (var3 <= 0) {
            return this.previewMode;
         } else if (Data.isVarTypeString(var3)) {
            JOptionPane.showMessageDialog(this, "event_time 必须是数值型整数期。", "事件时间变量类型错误", 2);
            return false;
         } else {
            TreeSet var4 = new TreeSet();
            boolean var5 = false;
            long var6 = Data.getObsTotal();

            for (long var8 = 1L; var8 <= var6; var8++) {
               long var10 = var8;
               double var12 = HxWorkbench.safe(() -> Data.getNum(var3, var10), Double.NaN);
               if (!Missing.isMissing(var12) && Math.rint(var12) == var12) {
                  int var14 = (int)var12;
                  if (var4.size() < 40) {
                     var4.add(var14);
                  }

                  if (var14 == var2) {
                     var5 = true;
                  }
               }
            }

            if (var5) {
               return true;
            } else {
               JOptionPane.showMessageDialog(this, "当前样本中不存在所选基准期 " + var2 + "。\n当前可见事件期：" + var4 + "\n\n请选择一个实际存在的基准期。", "基准期不存在", 2);
               return false;
            }
         }
      }

      private void chooseFirstExisting(JComboBox<String> var1, String... var2) {
         if (var1 != null && selected(var1).isBlank()) {
            for (String var6 : var2) {
               for (int var7 = 0; var7 < var1.getItemCount(); var7++) {
                  String var8 = (String)var1.getItemAt(var7);
                  if (var8 != null && var8.equalsIgnoreCase(var6)) {
                     var1.setSelectedIndex(var7);
                     return;
                  }
               }
            }
         }
      }

      private boolean validateDidPanelSettings() {
         String var1 = selected(this.didUnit);
         String var2 = selected(this.didTime);
         if ((this.didUnitFE.isSelected() || "cluster".equals(selected(this.vce))) && var1.isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择个体变量（如 firm）。", "面板结构尚未完整", 1);
            return false;
         } else if (this.didTimeFE.isSelected() && var2.isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择时间变量（如 year）。", "面板结构尚未完整", 1);
            return false;
         } else if (!var1.isBlank() && var1.equals(var2)) {
            JOptionPane.showMessageDialog(this, "个体变量和时间变量必须不同。", "面板结构设置错误", 2);
            return false;
         } else if ("cluster".equals(selected(this.vce)) && selected(this.cluster).isBlank()) {
            JOptionPane.showMessageDialog(this, "当前选择了聚类标准误，请选择聚类变量。", "聚类变量尚未选择", 1);
            return false;
         } else {
            return true;
         }
      }

      private boolean validateBinaryDidVariable(String var1, String var2) {
         if (var1 != null && !var1.isBlank()) {
            int var3 = HxWorkbench.safe(() -> Data.getVarIndex(var1), -1);
            if (var3 <= 0) {
               return this.previewMode;
            } else if (Data.isVarTypeString(var3)) {
               JOptionPane.showMessageDialog(this, var2 + " 当前是字符串变量。\nDID 的该角色需要数值型 0/1 变量。", "需要 0/1 变量", 2);
               return false;
            } else {
               boolean var4 = false;
               boolean var5 = false;
               LinkedHashSet var6 = new LinkedHashSet();
               long var7 = Data.getObsTotal();

               for (long var9 = 1L; var9 <= var7; var9++) {
                  long var11 = var9;
                  double var13 = HxWorkbench.safe(() -> Data.getNum(var3, var11), Double.NaN);
                  if (!Missing.isMissing(var13)) {
                     if (Math.abs(var13) < 1.0E-12) {
                        var4 = true;
                     } else if (Math.abs(var13 - 1.0) < 1.0E-12) {
                        var5 = true;
                     } else if (var6.size() < 6) {
                        var6.add(formatDecimal(var13));
                     }
                  }
               }

               if (!var6.isEmpty()) {
                  JOptionPane.showMessageDialog(
                     this, var2 + " 需要使用 0/1 编码。\n当前检测到其他取值：" + String.join("、", var6) + "\n\n工具不会自动重编码，请先确认变量定义。", "DID 二元变量检查未通过", 2
                  );
                  return false;
               } else if (var4 && var5) {
                  return true;
               } else {
                  JOptionPane.showMessageDialog(this, var2 + " 当前没有同时出现 0 和 1。\n请确认样本中同时存在对照状态和处理状态后再运行。", "DID 二元变量缺少必要取值", 2);
                  return false;
               }
            }
         } else {
            JOptionPane.showMessageDialog(this, "请选择" + var2 + "。", "DID 设置尚未完整", 1);
            return false;
         }
      }

      private void runOneClick() {
         if (!this.runInProgress) {
            boolean var1 = "oneclick_robustness".equals(this.currentCommand);
            String var2 = var1 ? "oneclick_robustness" : "oneclick";
            String var3 = selected(this.oneClickY);
            String var4 = selected(this.oneClickX);
            ArrayList var5 = new ArrayList<>(this.oneClickCandidates.getSelectedValuesList());
            if (var3.isBlank() || var4.isBlank() || var5.size() < 2) {
               JOptionPane.showMessageDialog(this, "请选择 Y、核心 X 和至少两个候选控制变量。\n外部 OneClick 的基础语法要求 varlist 至少包含 Y + 2 个候选变量。", "设置尚未完整", 1);
            } else if (!var3.equals(var4) && !var5.contains(var3) && !var5.contains(var4)) {
               List var6 = this.oneClickRequired.getSelectedValuesList();
               LinkedHashSet var7 = new LinkedHashSet(var5);
               var7.retainAll(var6);
               if (var6.contains(var3) || var6.contains(var4) || !var7.isEmpty()) {
                  JOptionPane.showMessageDialog(this, "每次保留的其他变量不能与 Y、X 或候选控制变量重复。", "变量角色重复", 2);
               } else if (HxWorkbench.StataBridge.execute("quietly which " + var2, false) == 0) {
                  BigInteger var11 = BigInteger.ONE.shiftLeft(var5.size()).subtract(BigInteger.ONE);
                  if (var11.compareTo(BigInteger.valueOf(4096L)) <= 0
                     || JOptionPane.showConfirmDialog(this, "预计需要检查约 " + var11 + " 个控制变量组合。\n外部 OneClick 可能运行较久，继续吗？", "确认大规模组合检验", 2, 2) == 0) {
                     this.updateOneClickPreview();
                     String var9 = this.oneClickGeneratedCommand.trim();
                     if (!this.oneClickExternalFrameName.isBlank()) {
                        HxWorkbench.StataBridge.execute("capture frame drop " + this.oneClickExternalFrameName, false);
                        this.oneClickExternalFrameName = "";
                     }

                     this.oneClickExternalModel.clear();
                     this.oneClickExternalControls.clear();
                     this.oneClickOverview.setText("正在运行外部 " + var2 + "…\n\n实际命令：\n" + var9);
                     this.selectResultView("oneclick", true);
                     String var10 = "hxoneclickrun, command(" + HxWorkbench.StataBridge.quote(var9) + ")";
                     this.executeMonitoredCommand(var9, var10, true, var2x -> this.loadExternalOneClickResults(var2x, var1));
                  }
               } else {
                  if (!var1 && JOptionPane.showConfirmDialog(this, "当前没有安装 oneclick。现在从 SSC 安装吗？", "缺少 OneClick", 0) == 0) {
                     int var8 = HxWorkbench.StataBridge.execute("hxdependency install oneclick", true);
                     if (var8 == 0) {
                        this.runOneClick();
                     }
                  } else {
                     JOptionPane.showMessageDialog(this, var2 + " 尚未安装。请先安装作者提供的外部命令后再运行。", "缺少外部命令", 1);
                  }
               }
            } else {
               JOptionPane.showMessageDialog(this, "Y、核心 X 与候选控制变量必须使用不同变量。", "变量角色重复", 2);
            }
         }
      }

      private void loadExternalOneClickResults(HxWorkbench.RunResult var1, boolean var2) {
         if (var1.rc != 0) {
            this.oneClickOverview.setText("外部命令执行失败。\n\nReturn code：" + var1.rc + "\n请查看右侧‘日志’和 Stata Results 中的原始错误信息。");
            this.oneClickResultTabs.setSelectedIndex(0);
         } else {
            String var3 = HxWorkbench.StataBridge.characteristic("hxtoolbox_oneclick_frame");
            String var4 = HxWorkbench.StataBridge.characteristic("hxtoolbox_oneclick_result");
            if (var3 == null || var3.isBlank()) {
               var3 = this.oneClickExternalFrameName;
            }

            this.oneClickExternalFrameName = var3;

            Frame var5;
            try {
               var5 = Frame.connect(var3);
            } catch (Throwable var19) {
               this.oneClickOverview.setText("外部命令已完成，但没有可读取的结果表。\n\n" + (var4 == null ? "" : var4) + "\n请在 Stata Results 中查看外部命令的原始输出。");
               this.oneClickResultTabs.setSelectedIndex(0);
               return;
            }

            long var6 = var5.getObsTotal();
            int var8 = (int)Math.min(20000L, var6);
            this.oneClickExternalModel.load(var5, var8, Math.min(100, var5.getVarCount()));
            this.oneClickExternalControls.clear();
            int var9 = var5.getVarIndex("subset");
            int var10 = var5.getVarIndex("positive");
            long var11 = 0L;
            long var13 = 0L;

            for (int var15 = 1; var15 <= var8; var15++) {
               int var16 = var15;
               String var17 = var9 > 0 ? HxWorkbench.safe(() -> var5.getFormattedValue(var9, var16, true), "") : "";
               this.oneClickExternalControls.add(splitControls(var17));
               if (var10 > 0) {
                  String var18 = HxWorkbench.safe(() -> var5.getFormattedValue(var10, var16, true), "").trim();
                  if ("1".equals(var18) || "1.0".equals(var18)) {
                     var11++;
                  } else if ("0".equals(var18) || "0.0".equals(var18)) {
                     var13++;
                  }
               }
            }

            this.configureExternalOneClickWidths();
            StringBuilder var20 = new StringBuilder();
            var20.append("外部 ").append(var2 ? "oneclick_robustness" : "oneclick").append(" 已完成\n\n");
            var20.append("结果记录：").append(var6).append("\n");
            if (var10 > 0) {
               var20.append("正向显著：").append(var11).append("\n");
               var20.append("负向显著：").append(var13).append("\n");
            }

            if (var6 > var8) {
               var20.append("界面当前显示前 ").append(var8).append(" 行；完整结果仍保留在临时 frame 中。\n");
            }

            if (var4 != null && !var4.isBlank()) {
               var20.append("\n").append(var4);
            }

            var20.append("\n结果来自隔离临时目录；当前 Stata 数据与用户工作目录中的文件均未改变。");
            this.oneClickOverview.setText(var20.toString());
            this.oneClickOverview.setCaretPosition(0);
            this.oneClickResultTabs.setSelectedIndex(var6 > 0L ? 1 : 0);
         }
      }

      private static List<String> splitControls(String var0) {
         if (var0 == null) {
            return Collections.emptyList();
         } else {
            String var1 = var0.trim();
            return !var1.isEmpty() && !".".equals(var1) ? Arrays.asList(var1.split("\\s+")) : Collections.emptyList();
         }
      }

      private void configureExternalOneClickWidths() {
         for (int var1 = 0; var1 < this.oneClickExternalTable.getColumnModel().getColumnCount(); var1++) {
            String var2 = this.oneClickExternalTable.getColumnName(var1);
            this.oneClickExternalTable.getColumnModel().getColumn(var1).setPreferredWidth("subset".equalsIgnoreCase(var2) ? 360 : 110);
         }
      }

      private void sendSelectedOneClickToRegression() {
         int var1 = this.oneClickExternalTable.getSelectedRow();
         if (var1 < 0) {
            JOptionPane.showMessageDialog(this, "请先在‘外部结果表’中选择一行。", "尚未选择组合", 1);
         } else {
            int var2 = this.oneClickExternalTable.convertRowIndexToModel(var1);
            List var3 = var2 >= 0 && var2 < this.oneClickExternalControls.size() ? this.oneClickExternalControls.get(var2) : Collections.emptyList();
            String var4 = "oneclick_robustness".equals(this.currentCommand) ? "regress" : selected(this.oneClickEstimator);
            String var5 = selected(this.oneClickY);
            String var6 = selected(this.oneClickX);
            ArrayList var7 = new ArrayList();
            var7.add(var6);
            var7.addAll(this.oneClickRequired.getSelectedValuesList());
            var7.addAll(var3);
            String var8 = Arrays.asList("logit", "probit").contains(var4) ? "二元结果" : "线性模型";
            this.navigateTo("reg", var8, var4);
            this.depvar.setSelectedItem(var5);
            setListSelectedValues(this.variables, var7);
            if ("reghdfe".equals(var4)) {
               setListSelectedValues(this.absorb, this.oneClickAbsorb.getSelectedValuesList());
            }

            if ("robust".equals(selected(this.oneClickVce))) {
               this.vce.setSelectedItem("robust");
            } else if ("cluster".equals(selected(this.oneClickVce))) {
               this.vce.setSelectedItem("cluster");
               this.cluster.setSelectedItem(selected(this.oneClickCluster));
            }

            this.options.setText("");
            this.schedulePreview();
            JOptionPane.showMessageDialog(this, "已把所选控制变量组合填入 " + var4 + " 页面。\n请核对最终 Stata 命令后再运行。", "已送入普通回归", 1);
         }
      }

      private static void setListSelectedValues(JList<String> var0, List<String> var1) {
         ArrayList<Integer> var2 = new ArrayList<>();
         ListModel<String> var3 = var0.getModel();

         for (int var4 = 0; var4 < var3.getSize(); var4++) {
            if (var1.contains(var3.getElementAt(var4))) {
               var2.add(var4);
            }
         }

         int[] var5 = var2.stream().mapToInt(Integer::intValue).toArray();
         var0.setSelectedIndices(var5);
      }

      private void executeMonitoredCommand(final String var1, final String var2, final boolean var3, final Consumer<HxWorkbench.RunResult> var4) {
         if (this.runInProgress) {
            JOptionPane.showMessageDialog(this, "当前仍有命令在运行，请等待本次执行结束。", "正在运行", 1);
         } else {
            this.beforeSnapshot = HxWorkbench.DatasetSnapshot.capture();
            this.activeRunBefore = HxWorkbench.RunShape.capture();
            this.lastExecutedCommand = var1;
            HxWorkbench.StataBridge.clearRunAudit();
            this.beginMonitoredRun(var1, false, 0);
            SwingWorker var5 = new SwingWorker<HxWorkbench.RunResult, Void>() {
               protected HxWorkbench.RunResult doInBackground() {
                  int var1x = HxWorkbench.StataBridge.execute(var2, true);
                  String var2x = HxWorkbench.StataBridge.characteristic("hxtoolbox_last_native_command");
                  if (var2x.isBlank()) {
                     var2x = var1;
                  }

                  String var3x = HxWorkbench.StataBridge.characteristic("hxtoolbox_history_status");
                  if (var3x.isBlank()) {
                     var3x = "由命令自身记录；请在 History 核对";
                  }

                  return HxWorkbench.RunResult.capture(var2x, var1x, var3x);
               }

               @Override
               protected void done() {
                  HxWorkbench.RunResult var1x;
                  try {
                     var1x = this.get();
                  } catch (Throwable var3x) {
                     var1x = HxWorkbench.RunResult.failure(var1, 459, "无法取得执行结果：" + HxWorkbench.WorkbenchFrame.rootMessage(var3x));
                  }

                  HxWorkbench.StataBridge.execute("quietly hxrefresh", false);
                  WorkbenchFrame.this.refreshDataset(var3 && var1x.rc == 0);
                  HxWorkbench.RunShape var2x = HxWorkbench.RunShape.capture();
                  WorkbenchFrame.this.finishMonitoredRun(var1x, var2x);
                  if (var4 != null) {
                     var4.accept(var1x);
                  }
               }
            };
            var5.execute();
         }
      }

      private void beginMonitoredRun(String var1, boolean var2, int var3) {
         this.runInProgress = true;
         this.runStartedAt = LocalDateTime.now();
         this.runStartedNanos = System.nanoTime();
         this.activeRunBefore = this.activeRunBefore == null ? HxWorkbench.RunShape.capture() : this.activeRunBefore;
         this.monitorStatus.setText("● 正在运行");
         this.monitorStatus.setForeground(ACCENT);
         this.monitorCommand.setText(var1);
         this.monitorCommand.setCaretPosition(0);
         this.monitorStart.setText("开始时间：" + this.runStartedAt.format(DateTimeFormatter.ofPattern("HH:mm:ss")));
         this.monitorEnd.setText("结束时间：-");
         this.monitorDuration.setText("总耗时：-");
         this.monitorReturnCode.setText("Return code：-");
         this.monitorHistory.setText("History：等待确认");
         this.monitorProcessors.setText(this.processorText());
         this.monitorElapsed.setText("已运行：00:00:00.0");
         this.monitorOutcome.setText("Stata 正在计算。普通命令无法提供可信的内部完成百分比，当前显示真实计时。");
         this.monitorProgress.setIndeterminate(!var2);
         this.monitorProgress.setMinimum(0);
         this.monitorProgress.setMaximum(Math.max(1, var3));
         this.monitorProgress.setValue(0);
         this.monitorProgress.setString(var2 ? "0 / " + var3 : "正在运行（进度未知）");
         this.commandDockTitle.setText("正在执行的 Stata 命令");
         this.commandDockStatus.setText("● 正在执行");
         this.commandDockStatus.setForeground(ACCENT);
         this.commandDockProgress.setVisible(true);
         this.commandDockProgress.setIndeterminate(!var2);
         this.commandDockProgress.setMinimum(0);
         this.commandDockProgress.setMaximum(Math.max(1, var3));
         this.commandDockProgress.setValue(0);
         this.commandDockProgress.setString(var2 ? "0 / " + var3 : "已运行 0.0 秒");
         this.activeQueueRow = this.runQueueModel.getRowCount();
         this.runQueueModel.addRow(new Object[]{++this.runSequence, "● 正在运行", shortenCommand(var1), "0.0s", "-"});
         this.monitorLog.setText("");
         this.appendMonitorLog("开始执行");
         this.appendMonitorLog("命令已提交，等待 History 写入结果");
         this.appendMonitorLog("Stata 开始计算");
         this.selectRunView();
         this.runElapsedTimer.start();
         this.setBusy(true, "Stata 正在执行：" + shortenCommand(var1));
      }

      private void updateRunElapsed() {
         if (this.runInProgress) {
            long var1 = System.nanoTime() - this.runStartedNanos;
            String var3 = formatElapsed(var1);
            this.monitorElapsed.setText("已运行：" + formatClock(var1));
            if (this.activeQueueRow >= 0 && this.activeQueueRow < this.runQueueModel.getRowCount()) {
               this.runQueueModel.setValueAt(var3, this.activeQueueRow, 3);
            }

            if (this.commandDockProgress.isIndeterminate()) {
               this.commandDockProgress.setString("已运行 " + var3);
            }
         }
      }

      private void finishMonitoredRun(HxWorkbench.RunResult var1, HxWorkbench.RunShape var2) {
         long var3 = System.nanoTime() - this.runStartedNanos;
         this.runElapsedTimer.stop();
         this.runInProgress = false;
         String var5 = formatElapsed(var3);
         boolean var6 = var1.rc == 0;
         this.monitorStatus.setText(var6 ? "● 已完成" : "● 执行失败");
         this.monitorStatus.setForeground(var6 ? SUCCESS : DANGER);
         this.monitorCommand.setText(var1.command);
         this.monitorCommand.setCaretPosition(0);
         this.monitorEnd.setText("结束时间：" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss")));
         this.monitorDuration.setText("总耗时：" + var5);
         this.monitorReturnCode.setText("Return code：" + var1.rc);
         this.monitorHistory.setText("History：" + var1.historyStatus);
         this.monitorProcessors.setText(this.processorText());
         this.monitorElapsed.setText("已运行：" + formatClock(var3));
         this.monitorProgress.setIndeterminate(false);
         this.monitorProgress.setMaximum(100);
         this.monitorProgress.setValue(var6 ? 100 : 0);
         this.monitorProgress.setString(var6 ? "执行完成" : "执行失败  r(" + var1.rc + ")");
         String var7 = this.buildRunOutcome(var1, this.activeRunBefore, var2);
         this.monitorOutcome.setText(var7);
         this.monitorOutcome.setCaretPosition(0);
         String nativeOutput = HxWorkbench.StataBridge.lastNativeOutput();
         if (nativeOutput.isBlank()) {
            this.resultSummaryArea.setText(var7);
         } else {
            this.resultSummaryArea.setText("Stata 原始输出\n\n" + nativeOutput + "\n\n—— 执行摘要 ——\n" + var7);
         }
         this.resultSummaryArea.setCaretPosition(0);
         this.commandDockTitle.setText("即将执行的 Stata 命令");
         this.commandDockStatus.setText(var6 ? "● 成功 · " + var5 : "● 失败 r(" + var1.rc + ")");
         this.commandDockStatus.setForeground(var6 ? SUCCESS : DANGER);
         this.commandDockProgress.setIndeterminate(false);
         this.commandDockProgress.setMaximum(100);
         this.commandDockProgress.setValue(var6 ? 100 : 0);
         this.commandDockProgress.setString(var6 ? "执行完成 · " + var5 : "失败 · " + var5);
         if (this.activeQueueRow >= 0 && this.activeQueueRow < this.runQueueModel.getRowCount()) {
            this.runQueueModel.setValueAt(var6 ? "完成" : "失败", this.activeQueueRow, 1);
            this.runQueueModel.setValueAt(shortenCommand(var1.command), this.activeQueueRow, 2);
            this.runQueueModel.setValueAt(var5, this.activeQueueRow, 3);
            this.runQueueModel.setValueAt(var1.rc, this.activeQueueRow, 4);
         }

         this.appendMonitorLog("History：" + var1.historyStatus);
         this.appendMonitorLog(var6 ? "执行完成，return code 0" : "执行失败，return code " + var1.rc);
         if (!var1.error.isBlank()) {
            this.appendMonitorLog("错误：" + var1.error);
         }

         this.setBusy(false, var6 ? "执行完成；最终命令已写入 Stata History。" : "执行失败，返回码 " + var1.rc + "；请查看运行监控和 Stata Results。");
         if (var6) {
            this.rememberCurrentWork();
         }

         if (!var6) {
            // A failed Stata command can still have the most useful diagnosis in Results.
            if (!nativeOutput.isBlank()) {
               this.selectResultView("general", true);
            } else {
               this.selectRunView();
            }
         } else if ("regress".equals(this.currentCommand) && this.regressWorkspaceActive) {
            this.selectResultView("general", true);
         } else if ("__convert_dta__".equals(this.currentCommand)) {
            this.selectResultView("convert", true);
         } else if ("__missing_analysis__".equals(this.currentCommand)) {
            this.selectResultView("missing", true);
         } else if (this.currentCommand.startsWith("oneclick")) {
            this.selectResultView("oneclick", true);
         } else if (Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_box", "did_trends", "twoway", "marginsplot", "coefplot", "event_plot")
            .contains(this.currentCommand)) {
            this.selectResultView("graph", true);
         } else if ("data".equals(this.activeCategoryCode)) {
            this.selectResultView("changes", true);
         } else {
            this.selectResultView("general", true);
         }

         this.activeRunBefore = null;
      }

      private String buildRunOutcome(HxWorkbench.RunResult var1, HxWorkbench.RunShape var2, HxWorkbench.RunShape var3) {
         StringBuilder var4 = new StringBuilder();
         if (var1.rc != 0) {
            var4.append("执行失败  r(")
               .append(var1.rc)
               .append(")\n\n")
               .append(var1.error.isBlank() ? errorAdvice(var1.rc, var1.command) : var1.error)
               .append("\n\nStata 的完整报错保留在 Results 窗口；最终命令保留在 History。");
            return var4.toString();
         } else {
            var4.append("执行成功\n\n");
            if (var2 != null && var3 != null) {
               var4.append("数据变化：\n").append("观测数 ").append(var2.n).append(" → ").append(var3.n);
               long var5 = var3.n - var2.n;
               if (var5 != 0L) {
                  var4.append("（").append(var5 > 0L ? "+" : "").append(var5).append("）");
               }

               var4.append("\n变量数 ").append(var2.k).append(" → ").append(var3.k);
               ArrayList var7 = new ArrayList<>(var3.names);
               var7.removeAll(var2.names);
               if (!var7.isEmpty()) {
                  var4.append("\n新增变量：").append(String.join(" ", var7));
               }
            }

            if (!Double.isNaN(var1.estimationN)) {
               long var8 = var2 == null ? 0L : var2.n;
               var4.append("\n\n回归结果：\nN = ").append(formatNumber(var1.estimationN));
               if (var8 > 0L && var1.estimationN <= var8) {
                  var4.append("\n原数据样本：").append(var8).append("\n未进入回归：").append(Math.max(0L, var8 - Math.round(var1.estimationN)));
               }

               if (!Double.isNaN(var1.r2)) {
                  var4.append("\nR² = ").append(String.format(Locale.ROOT, "%.4f", var1.r2));
               }

               if (!Double.isNaN(var1.r2Adjusted)) {
                  var4.append("\n调整 R² = ").append(String.format(Locale.ROOT, "%.4f", var1.r2Adjusted));
               }
            }

            return var4.toString();
         }
      }

      private static String errorAdvice(int var0, String var1) {
         if (var0 == 459 && var1.trim().toLowerCase(Locale.ROOT).startsWith("xt")) {
            return "建议：当前数据可能尚未 xtset，或面板变量设置与命令要求不一致。";
         } else if (var0 == 111) {
            return "建议：检查变量名是否存在，或先刷新当前数据状态。";
         } else {
            return var0 == 198 ? "建议：检查必填变量、条件和 options 的语法。" : "建议：在 Stata Results 中查看该返回码对应的完整错误信息。";
         }
      }

      private String processorText() {
         String var1 = HxWorkbench.StataBridge.characteristic("hxtoolbox_status_cpu");
         return var1.isBlank() ? "处理器：-" : var1;
      }

      private void appendMonitorLog(String var1) {
         String var2 = LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss"));
         this.monitorLog.append((this.monitorLog.getText().isEmpty() ? "" : "\n") + var2 + "  " + var1);
         this.monitorLog.setCaretPosition(this.monitorLog.getDocument().getLength());
      }

      private void flashCommandPreview() {
         if (this.commandDock.isVisible() && !this.runInProgress) {
            this.commandDockTitle.setText("即将执行的 Stata 命令");
            this.commandDockStatus.setText("命令已更新");
            this.commandDockStatus.setForeground(MUTED);
            this.commandDockProgress.setVisible(false);
            this.previewFlashTimer.stop();
            this.previewArea.setBackground(PALE_YELLOW);
            this.previewFlashTimer.start();
         }
      }

      private static String shortenCommand(String var0) {
         if (var0 == null) {
            return "";
         } else {
            String var1 = var0.replaceAll("\\s+", " ").trim();
            return var1.length() <= 88 ? var1 : var1.substring(0, 85) + "…";
         }
      }

      private static String formatElapsed(long var0) {
         return String.format(Locale.ROOT, "%.1fs", Math.max(0L, var0) / 1.0E9);
      }

      private static String formatClock(long var0) {
         long var2 = Math.max(0L, var0 / 100000000L);
         long var4 = var2 / 36000L;
         long var6 = var2 / 600L % 60L;
         long var8 = var2 / 10L % 60L;
         long var10 = var2 % 10L;
         return String.format(Locale.ROOT, "%02d:%02d:%02d.%d", var4, var6, var8, var10);
      }

      private static String formatNumber(double var0) {
         return Math.rint(var0) == var0 ? Long.toString(Math.round(var0)) : String.format(Locale.ROOT, "%.3f", var0);
      }

      private static String formatDecimal(double var0) {
         return Double.isNaN(var0) ? "-" : String.format(Locale.ROOT, "%.6g", var0);
      }

      private static String rootMessage(Throwable var0) {
         Throwable var1 = var0;

         while (var1.getCause() != null) {
            var1 = var1.getCause();
         }

         return var1.getMessage() == null ? var1.getClass().getSimpleName() : var1.getMessage();
      }

      void refreshDataset(boolean var1) {
         this.dataModel.reload();
         this.refreshVariableControls();
         this.refreshXtregVariableControls();
         this.refreshInspectorVariables();
         long var2 = Data.getObsTotal();
         int var4 = Data.getVarCount();
         String dataHint = "xtreg".equals(this.currentCommand) ? " | 可从中间变量窗口或表头拖入左侧变量框" : " | 表格只读，可横向和纵向滚动";
         this.dataLabel.setText(var2 != 0L && var4 != 0 ? var2 + " 行 × " + var4 + " 列" + dataHint : "尚未载入数据");
         this.currentDataLayout.show(this.currentDataCards, var2 != 0L && var4 != 0 ? "table" : "empty");
         this.configureColumnWidths();
         if (var1 && this.beforeSnapshot != null) {
            this.compareSnapshots(this.beforeSnapshot);
         } else if (!var1) {
            this.changedCells.clear();
            this.addedVariables.clear();
            this.changeArea
               .setText(
                  "运行数据处理命令后，这里会显示样本数、变量数、新增变量和单元格变化。\n\n优先支持：generate、replace、keep、drop、merge、append、winsor2。\n为保证大型数据可用，单元格逐值对比最多抽取约 120,000 个可见值；样本数和变量数始终按完整数据报告。"
               );
         }

         this.updateSelectedColumnSummary();
         this.dataTable.repaint();
         this.statusLabel
            .setText(
               HxWorkbench.StataBridge.characteristic("hxtoolbox_status_data")
                  + "　"
                  + HxWorkbench.StataBridge.characteristic("hxtoolbox_status_nk")
                  + "　"
                  + HxWorkbench.StataBridge.characteristic("hxtoolbox_status_cpu")
            );
         this.syncRightPaneTitle();
         this.refreshHomeContext();
      }

      private void compareSnapshots(HxWorkbench.DatasetSnapshot var1) {
         this.changedCells.clear();
         this.addedVariables.clear();
         HxWorkbench.DatasetSnapshot var2 = HxWorkbench.DatasetSnapshot.captureWithShape(var1.sampleRows, var1.sampleCols);
         LinkedHashSet<String> var3 = new LinkedHashSet<>(var1.names);

         for (String var5 : var2.names) {
            if (!var3.contains(var5)) {
               this.addedVariables.add(var5);
            }
         }

         Map var14 = var1.nameIndex();
         Map var15 = var2.nameIndex();
         int var6 = 0;
         int var7 = 0;

         for (String var9 : var3) {
            Integer var10 = (Integer)var14.get(var9);
            Integer var11 = (Integer)var15.get(var9);
            if (var11 != null && var10 != null && var10 < var1.sampleCols && var11 < var2.sampleCols) {
               int var12 = Math.min(var1.sampleRows, var2.sampleRows);

               for (int var13 = 0; var13 < var12; var13++) {
                  var7++;
                  if (!Objects.equals(var1.value(var13, var10), var2.value(var13, var11))) {
                     this.changedCells.add(var13 + ":" + var11);
                     var6++;
                  }
               }
            }
         }

         long var16 = var2.n - var1.n;
         int var17 = var2.k - var1.k;
         StringBuilder var18 = new StringBuilder();
         if (!this.lastExecutedCommand.isBlank()) {
            var18.append("刚刚执行\n").append(this.lastExecutedCommand).append("\n\n变化\n");
         }

         var18.append("执行前：").append(var1.n).append(" 行 × ").append(var1.k).append(" 列\n");
         var18.append("执行后：").append(var2.n).append(" 行 × ").append(var2.k).append(" 列\n");
         var18.append("样本变化：").append(signed(var16)).append(" 行\n");
         if (var16 < 0L) {
            var18.append("删除样本：").append(-var16).append(" 行\n");
         }

         if (var16 > 0L) {
            var18.append("新增样本：").append(var16).append(" 行\n");
         }

         var18.append("变量变化：").append(signed(var17)).append(" 列\n\n");
         if (!this.addedVariables.isEmpty()) {
            var18.append("本次新增变量：").append(String.join("、", this.addedVariables)).append("\n\n");
         }

         var18.append("抽样逐值比较：比较 ").append(var7).append(" 个单元格，发现 ").append(var6).append(" 个变化。\n");
         var18.append("当前数据表中：绿色表示新增变量，黄色表示抽样范围内发生变化的值。\n\n");
         var18.append("说明：样本数和变量数来自完整数据；逐值高亮采用有上限的快照，避免大型数据占用过多内存。");
         this.changeArea.setText(var18.toString());
         this.changeArea.setCaretPosition(0);
         if (var16 != 0L || var17 != 0 || var6 > 0) {
            this.selectResultView("changes", true);
         }
      }

      private void updateSelectedColumnSummary() {
         int var1 = this.dataTable.getSelectedColumn();
         int var2 = var1 >= 0 ? this.dataTable.convertColumnIndexToModel(var1) : (this.dataModel.getColumnCount() > 0 ? 0 : -1);
         if (var2 < 0) {
            this.summaryArea.setText("当前没有变量。");
            this.inspectorPropertyArea.setText("当前没有变量。");
            this.histogram.setValues(Collections.emptyList(), "");
         } else {
            HxWorkbench.VariableSummary var3 = HxWorkbench.VariableSummary.compute(var2 + 1);
            this.summaryArea.setText(var3.text);
            this.summaryArea.setCaretPosition(0);
            this.inspectorPropertyArea.setText(var3.text);
            this.inspectorPropertyArea.setCaretPosition(0);
            this.histogram.setValues(var3.numericValues, var3.name);
         }
         this.inspectorOverviewLabel.setText("数据概览：" + Data.getObsTotal() + " 行 × " + Data.getVarCount() + " 列");
         this.refreshInspectorRole();
      }

      private void openHelp() {
         if (!this.currentCommand.isBlank()) {
            String var1 = "__missing_analysis__".equals(this.currentCommand)
               ? "misstable"
               : (
                  "__convert_dta__".equals(this.currentCommand)
                     ? (
                        externalType(Paths.get(this.convertInputFile.getText().isBlank() ? "file.csv" : this.convertInputFile.getText())).equals("excel")
                           ? "import excel"
                           : "import delimited"
                     )
                     : ("graph_box".equals(this.currentCommand) ? "graph box" : ("did_trends".equals(this.currentCommand) ? "hxtrendplot" : this.currentCommand))
               );
            int var2 = HxWorkbench.StataBridge.execute("help " + var1, true);
            if (var2 == 0) {
               HxWorkbench.StataBridge.execute("capture window manage forward viewer", false);
            }
         }
      }

      private void configureColumnWidths() {
         for (int var1 = 0; var1 < this.dataTable.getColumnModel().getColumnCount(); var1++) {
            String var2 = this.dataTable.getColumnName(var1);
            int var3 = Math.max(95, Math.min(220, var2.length() * 11 + 35));
            this.dataTable.getColumnModel().getColumn(var1).setPreferredWidth(var3);
         }
      }

      private JPanel addField(int var1, String var2, JComponent var3) {
         JPanel var4 = new JPanel(new BorderLayout(0, 6));
         var4.setOpaque(false);
         JLabel var5 = new JLabel(var2 != null && !var2.isBlank() ? var2 : "参数");
         var5.setForeground(new Color(55, 67, 84));
         var5.setFont(var5.getFont().deriveFont(1, 11.0F));
         var4.add(var5, "North");
         var4.add(var3, "Center");
         GridBagConstraints var6 = this.constraints(0, var1);
         var6.gridwidth = 2;
         var6.weightx = 1.0;
         var6.fill = 2;
         var6.insets = new Insets(0, 0, 13, 0);
         this.formPanel.add(var4, var6);
         return var4;
      }

      private void addAdvancedSettings(int var1, boolean var2, boolean var3, boolean var4) {
         this.rebuildGenericAdvancedContent(var2, var3, var4);
         this.advancedContent.setVisible(true);
         JPanel var5 = new JPanel();
         var5.setOpaque(false);
         var5.setLayout(new BoxLayout(var5, BoxLayout.Y_AXIS));
         JLabel title = sectionCaption("其他设置");
         title.setAlignmentX(0.0F);
         this.advancedContent.setAlignmentX(0.0F);
         var5.add(title);
         var5.add(Box.createVerticalStrut(7));
         var5.add(this.advancedContent);
         GridBagConstraints var6 = this.constraints(0, var1);
         var6.gridwidth = 2;
         var6.weightx = 1.0;
         var6.fill = GridBagConstraints.HORIZONTAL;
         this.formPanel.add(var5, var6);
      }

      private void rebuildGenericAdvancedContent(boolean var1, boolean var2, boolean var3) {
         this.advancedContent.removeAll();
         this.genericWeightVarFieldBlock = null;
         if (var3) {
            this.configureGenericWeightTypes();
         }
         if (var1) {
            this.advancedContent.add(this.labeledInline("样本条件 if", this.ifCondition));
            this.advancedContent.add(Box.createVerticalStrut(8));
         }

         if (var2) {
            this.advancedContent.add(this.labeledInline("观测范围 in", this.inCondition));
            this.advancedContent.add(Box.createVerticalStrut(8));
         }

         if (var3) {
            JPanel var4 = new JPanel(new GridLayout(1, 2, 8, 0));
            var4.setOpaque(false);
            var4.add(this.miniLabeled("权重类型", this.genericWeightType));
            var4.add(this.miniLabeled("权重变量", this.genericWeightVar));
            this.genericWeightVarFieldBlock = this.labeledInline("权重", var4);
            this.advancedContent.add(this.genericWeightVarFieldBlock);
            this.advancedContent.add(Box.createVerticalStrut(8));
         }

         JLabel var5 = new JLabel("其他 Stata options（高级，可留空）");
         var5.setForeground(MUTED);
         var5.setFont(var5.getFont().deriveFont(10.5F));
         var5.setAlignmentX(0.0F);
         this.options.setMaximumSize(new Dimension(Integer.MAX_VALUE, 32));
         this.advancedContent.add(var5);
         this.advancedContent.add(Box.createVerticalStrut(4));
         this.advancedContent.add(this.options);
         this.updateGenericWeightConditionalFields();
         this.advancedContent.revalidate();
         this.advancedContent.repaint();
      }

      private void configureGenericWeightTypes() {
         String var1 = selected(this.genericWeightType);
         List<String> var2;
         if (Arrays.asList("didregress", "xtdidregress").contains(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "aweight", "pweight");
         } else if ("ppmlhdfe".equals(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "pweight");
         } else if ("reghdfe".equals(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "aweight", "pweight");
         } else {
            var2 = Arrays.asList("无", "fweight", "aweight", "pweight", "iweight");
         }

         this.genericWeightType.removeAllItems();
         for (String var4 : var2) {
            this.genericWeightType.addItem(var4);
         }

         this.genericWeightType.setSelectedItem(var2.contains(var1) ? var1 : "无");
      }

      private void updateGenericWeightConditionalFields() {
         boolean var1 = !"无".equals(selected(this.genericWeightType));
         this.genericWeightVar.setEnabled(var1);
         if (!var1) {
            this.genericWeightVar.setSelectedItem(null);
         }
      }

      private void addTaskGroup(int var1, String var2, String[][] var3) {
         JPanel var4 = new JPanel(new GridLayout(0, 2, 8, 8));
         var4.setOpaque(false);

         for (String[] var8 : var3) {
            JButton var9 = new JButton(var8[0]);
            styleSecondaryButton(var9);
            var9.addActionListener(var2x -> this.navigateTo(var8[1], var8[2], var8[3]));
            var4.add(var9);
         }

         this.addField(var1, var2, var4);
      }

      private void navigateTo(String var1, String var2, String var3) {
         this.browseMethod(var1, var2);
         this.openCommandPage(var3);
      }

      private void chooseAndLoadDta() {
         JFileChooser var1 = new JFileChooser();
         var1.setDialogTitle("选择 Stata DTA 数据文件");
         if (var1.showOpenDialog(this) == 0) {
            Path var2 = var1.getSelectedFile().toPath().toAbsolutePath();
            if (!var2.toString().toLowerCase(Locale.ROOT).endsWith(".dta")) {
               JOptionPane.showMessageDialog(this, "请选择 .dta 文件。", "文件类型不符", 1);
            } else {
               this.runUtility("use " + commandQuote(var2.toString()) + ", clear", true);
            }
         }
      }

      private void copyCurrentCommand() {
         String var1 = this.previewArea.getText().trim();
         if (!var1.isBlank()) {
            Toolkit.getDefaultToolkit().getSystemClipboard().setContents(new StringSelection(var1), null);
            this.statusLabel.setText("已复制完整 Stata 命令。");
         }
      }

      private void updateConditionalFields() {
         if (this.clusterFieldBlock != null) {
            boolean var1 = "cluster".equalsIgnoreCase(selected(this.vce));
            this.clusterFieldBlock.setVisible(var1);
         }
         this.updateGenericWeightConditionalFields();
         this.formPanel.revalidate();
         this.formPanel.repaint();
      }

      private static boolean comboContains(JComboBox<String> var0, String var1) {
         for (int var2 = 0; var2 < var0.getItemCount(); var2++) {
            if (var1.equalsIgnoreCase(String.valueOf(var0.getItemAt(var2)))) {
               return true;
            }
         }

         return false;
      }

      private static String categoryLabel(String var0) {
         switch (var0) {
            case "data":
               return "数据处理";
            case "stats":
               return "统计";
            case "reg":
               return "回归模型";
            case "post":
               return "后估计";
            case "graph":
               return "图形";
            case "did":
               return "DID 专区";
            case "oneclick":
               return "OneClick 专区";
            case "test":
               return "测试数据";
            case "performance":
               return "性能设置";
            case "favorites":
               return "常用命令";
            case "recent":
               return "最近使用";
            default:
               return "开始";
         }
      }

      private static String commandMethod(String var0) {
         if ("hxconvert".equals(var0)) {
            return "数据处理|导入与转换";
         } else if (Arrays.asList("缺失值分析", "duplicates", "misstable").contains(var0)) {
            return "数据处理|数据检查";
         } else if (Arrays.asList("generate", "replace", "encode", "decode", "destring", "tostring", "winsor2").contains(var0)) {
            return "数据处理|变量处理";
         } else if (Arrays.asList("keep", "drop").contains(var0)) {
            return "数据处理|样本处理";
         } else if (Arrays.asList("merge", "append").contains(var0)) {
            return "数据处理|合并与追加";
         } else if (Arrays.asList("reshape", "collapse", "xtset", "tsset").contains(var0)) {
            return "数据处理|数据结构";
         } else if (Arrays.asList("summarize", "tabstat").contains(var0)) {
            return "统计|汇总，表格和假设检验";
         } else if (Arrays.asList("correlate", "pwcorr").contains(var0)) {
            return "统计|线性模型及相关";
         } else if ("ttest".equals(var0)) {
            return "统计|汇总，表格和假设检验";
         } else if ("tabulate".equals(var0)) {
            return "统计|汇总，表格和假设检验";
         } else if (Arrays.asList("regress", "areg", "reghdfe", "qreg", "rreg", "cnsreg", "vwls", "eivreg", "newey", "prais").contains(var0)) {
            return "统计|线性模型及相关";
         } else if (Arrays.asList("didregress", "xtdidregress").contains(var0)) {
            return "统计|因果推断/处理效应";
         } else if (Arrays.asList("xtreg", "xtlogit", "xtprobit").contains(var0)) {
            return "统计|纵向/面板数据";
         } else if (Arrays.asList("logit", "probit").contains(var0)) {
            return "统计|二元结果";
         } else if (Arrays.asList("poisson", "nbreg", "ppmlhdfe").contains(var0)) {
            return "统计|计数结果";
         } else if (Arrays.asList("ivregress", "ivreghdfe").contains(var0)) {
            return "回归模型|工具变量";
         } else if ("did_builder".equals(var0)) {
            return "DID 专区|DID分步构建";
         } else if (Arrays.asList("test", "lincom").contains(var0)) {
            return "后估计|系数检验";
         } else if (Arrays.asList("predict", "margins").contains(var0)) {
            return "后估计|预测边际";
         } else if (Arrays.asList("histogram", "kdensity", "graph_box").contains(var0)) {
            return "图形|分布图";
         } else if (Arrays.asList("scatter", "lfit", "twoway").contains(var0)) {
            return "图形|二维图(散点图，折线图等)";
         } else if ("did_trends".equals(var0)) {
            return "DID 专区|平行趋势与动态图";
         } else if (Arrays.asList("coefplot", "marginsplot").contains(var0)) {
            return "图形|更多统计图形";
         } else if ("event_plot".equals(var0)) {
            return "DID 专区|平行趋势与动态图";
         } else if ("oneclick".equals(var0)) {
            return "OneClick 专区|控制变量组合筛选";
         } else {
            return "oneclick_robustness".equals(var0) ? "OneClick 专区|控制变量组合稳健性" : "任意 Stata 命令|自动解析";
         }
      }

      private static String commandPath(String var0) {
         String[] var1 = commandMethod(var0).split("\\|", 2);
         return var1[0] + "  ›  " + var1[1] + "  ›  " + var0;
      }

      private static String commandDescription(String var0) {
         HxWorkbench.WorkbenchFrame.CommandGuide var1 = COMMAND_GUIDES.get(var0);
         return var1 == null ? var0 : var1.title;
      }

      private static String html(String var0) {
         return var0 == null ? "" : var0.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
      }

      private GridBagConstraints constraints(int var1, int var2) {
         GridBagConstraints var3 = new GridBagConstraints();
         var3.gridx = var1;
         var3.gridy = var2;
         var3.anchor = 18;
         var3.fill = 2;
         return var3;
      }

      private JComponent usingChooser() {
         JPanel var1 = new JPanel(new BorderLayout(5, 0));
         var1.setOpaque(false);
         JButton var2 = new JButton("浏览…");
         styleSecondaryButton(var2);
         var2.addActionListener(var1x -> {
            JFileChooser var2x = new JFileChooser();
            if (var2x.showOpenDialog(this) == 0) {
               this.usingFile.setText(var2x.getSelectedFile().getAbsolutePath());
            }
         });
         var1.add(this.usingFile, "Center");
         var1.add(var2, "East");
         return var1;
      }

      private JScrollPane listPane(JList<String> var1) {
         JScrollPane var2 = softScroll(var1);
         var2.setPreferredSize(new Dimension(280, 86));
         return var2;
      }

      private boolean flag(String var1) {
         return "1".equals(HxWorkbench.StataBridge.characteristic("hxtoolbox_schema_" + var1));
      }

      private String sem(String var1) {
         String var2 = HxWorkbench.StataBridge.characteristic("hxtoolbox_sem_" + var1);
         return var2.isBlank() ? var1 : var2;
      }

      private void pushSelections(String var1, JList<String> var2) {
         for (String var4 : var2.getSelectedValuesList()) {
            HxWorkbench.StataBridge.execute("quietly hxpick, target(" + var1 + ") action(add) value(" + HxWorkbench.StataBridge.quote(var4) + ")", false);
         }
      }

      private void appendOption(StringBuilder var1, String var2, String var3) {
         if (var3 != null && !var3.trim().isEmpty()) {
            var1.append(var1.indexOf(",") < 0 ? ", " : " ");
            var1.append(var2).append("(").append(HxWorkbench.StataBridge.quote(var3.trim())).append(")");
         }
      }

      private void addPreviewListeners(JComponent... var1) {
         for (JComponent var5 : var1) {
            if (var5 instanceof JTextField) {
               JTextField var6 = (JTextField)var5;
               var6.getDocument().addDocumentListener(new HxWorkbench.SimpleDocumentListener(this::schedulePreview));
            } else if (var5 instanceof JComboBox) {
               JComboBox var7 = (JComboBox)var5;
               var7.addActionListener(var1x -> this.schedulePreview());
            } else if (var5 instanceof JList) {
               JList var8 = (JList)var5;
               var8.addListSelectionListener(var1x -> {
                  if (!var1x.getValueIsAdjusting()) {
                     this.schedulePreview();
                  }
               });
            }
         }
      }

      private void schedulePreview() {
         if (!this.rebuilding && !this.currentCommand.isBlank()) {
            this.previewTimer.restart();
         }
      }

      private void setBusy(boolean var1, String var2) {
         this.setCursor(Cursor.getPredefinedCursor(var1 ? 3 : 0));
         this.statusLabel.setText(var2);
         this.runButton.setEnabled(!var1 && !this.currentCommand.isBlank());
      }

      private static String selected(JComboBox<String> var0) {
         Object var1 = var0.getSelectedItem();
         return var1 == null ? "" : var1.toString();
      }

      private static String signed(long var0) {
         return var0 > 0L ? "+" + var0 : Long.toString(var0);
      }

      private static String visibleText(String var0) {
         return var0 == null ? "" : var0.replace('—', '-').replace('–', '-');
      }

      private static JScrollPane softScroll(Component var0) {
         JScrollPane var1 = new JScrollPane(var0);
         var1.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(BORDER, 8));
         var1.getViewport().setBackground(SURFACE);
         var1.getVerticalScrollBar().setUnitIncrement(16);
         return var1;
      }

      private static JScrollPane navigationScroll(Component var0) {
         JScrollPane var1 = new JScrollPane(var0);
         var1.setAlignmentX(0.0F);
         var1.setBorder(BorderFactory.createMatteBorder(1, 0, 0, 0, BORDER));
         var1.getViewport().setBackground(SIDEBAR);
         var1.getVerticalScrollBar().setUnitIncrement(16);
         return var1;
      }

      private static JLabel sectionCaption(String var0) {
         JLabel var1 = new JLabel(var0);
         var1.setAlignmentX(0.0F);
         var1.setHorizontalAlignment(2);
         var1.setMaximumSize(new Dimension(Integer.MAX_VALUE, 22));
         var1.setForeground(MUTED);
         var1.setBorder(new EmptyBorder(0, 2, 4, 0));
         var1.setFont(var1.getFont().deriveFont(1, 10.5F));
         return var1;
      }

      private static void styleTextField(JTextField var0) {
         var0.setBackground(SURFACE);
         var0.setForeground(TEXT);
         var0.setCaretColor(ACCENT);
         var0.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(BORDER, 8), new EmptyBorder(6, 8, 6, 8)));
      }

      private static void styleCombo(JComboBox<?> var0) {
         var0.setBackground(SURFACE);
         var0.setForeground(TEXT);
         var0.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(BORDER, 8));
         var0.setMaximumRowCount(18);
      }

      private static void styleSecondaryButton(AbstractButton var0) {
         var0.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(246, 248, 251), new Color(238, 242, 247), TEXT, BORDER));
         var0.setBorder(new EmptyBorder(7, 12, 7, 12));
         var0.setCursor(Cursor.getPredefinedCursor(12));
         var0.setFocusPainted(false);
         var0.setContentAreaFilled(false);
         var0.setOpaque(false);
      }

      private static void stylePrimaryButton(JButton var0) {
         var0.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(ACCENT, ACCENT_HOVER, new Color(27, 75, 143), Color.WHITE, ACCENT));
         var0.setBorder(new EmptyBorder(8, 18, 8, 18));
         var0.setFont(var0.getFont().deriveFont(1));
         var0.setCursor(Cursor.getPredefinedCursor(12));
         var0.setFocusPainted(false);
         var0.setContentAreaFilled(false);
         var0.setOpaque(false);
      }

      private static JTextArea readonlyArea() {
         JTextArea var0 = new JTextArea();
         var0.setEditable(false);
         var0.setLineWrap(true);
         var0.setWrapStyleWord(true);
         var0.setBackground(SURFACE);
         var0.setForeground(TEXT);
         var0.setBorder(new EmptyBorder(9, 10, 9, 10));
         return var0;
      }

      private static JComboBox<String> variableCombo() {
         JComboBox var0 = new JComboBox();
         var0.setMaximumRowCount(18);
         return var0;
      }

      private static JList<String> variableList() {
         JList var0 = new JList(new DefaultListModel());
         var0.setSelectionMode(2);
         var0.setVisibleRowCount(3);
         return var0;
      }

      private static void replaceComboItems(JComboBox<String> var0, List<String> var1) {
         Object var2 = var0.getSelectedItem();
         var0.removeAllItems();
         var0.addItem("");

         for (String var4 : var1) {
            var0.addItem(var4);
         }

         if (var2 != null && var1.contains(var2.toString())) {
            var0.setSelectedItem(var2.toString());
         }
      }

      private static void replaceListItems(JList<String> var0, List<String> var1) {
         ArrayList var2 = new ArrayList(var0.getSelectedValuesList());
         DefaultListModel var3 = (DefaultListModel)var0.getModel();
         var3.clear();

         for (String var5 : var1) {
            var3.addElement(var5);
         }

         if (!var2.isEmpty()) {
            setListSelectedValues(var0, var2);
         }
      }

      private static final class CategoryRenderer extends DefaultListCellRenderer {
         @Override
         public Component getListCellRendererComponent(JList<?> var1, Object var2, int var3, boolean var4, boolean var5) {
            JLabel var6 = (JLabel)super.getListCellRendererComponent(var1, var2, var3, var4, var5);
            var6.setBorder(new EmptyBorder(5, 10, 5, 9));
            var6.setForeground(var4 ? HxWorkbench.WorkbenchFrame.ACCENT : HxWorkbench.WorkbenchFrame.TEXT);
            var6.setBackground(var4 ? HxWorkbench.WorkbenchFrame.ACCENT_SOFT : HxWorkbench.WorkbenchFrame.SIDEBAR);
            var6.setFont(var6.getFont().deriveFont(var4 ? 1 : 0, 11.5F));
            return var6;
         }
      }

      private final class ChangeRenderer extends DefaultTableCellRenderer {
         @Override
         public Component getTableCellRendererComponent(JTable var1, Object var2, boolean var3, boolean var4, int var5, int var6) {
            Component var7 = super.getTableCellRendererComponent(var1, var2, var3, var4, var5, var6);
            if (!var3) {
               int var8 = var1.convertColumnIndexToModel(var6);
               String var9 = WorkbenchFrame.this.dataModel.getColumnName(var8);
               if (WorkbenchFrame.this.addedVariables.contains(var9)) {
                  var7.setBackground(HxWorkbench.WorkbenchFrame.PALE_GREEN);
               } else if (WorkbenchFrame.this.changedCells.contains(var5 + ":" + var8)) {
                  var7.setBackground(HxWorkbench.WorkbenchFrame.PALE_YELLOW);
               } else {
                  var7.setBackground(var5 % 2 == 0 ? Color.WHITE : new Color(248, 250, 252));
               }
            }

            return var7;
         }
      }

      private static final class CommandGuide {
         final String title;
         final String purpose;
         final String bestFor;
         final String example;
         final String difference;

         CommandGuide(String var1, String var2, String var3, String var4, String var5) {
            this.title = var1;
            this.purpose = var2;
            this.bestFor = var3;
            this.example = var4;
            this.difference = var5;
         }

         String searchableText(String var1) {
            return String.join(" ", var1, this.title, this.purpose, this.bestFor, this.example, this.difference).toLowerCase(Locale.ROOT);
         }
      }

      private final class CommandListRenderer extends DefaultListCellRenderer {
         @Override
         public Component getListCellRendererComponent(JList<?> var1, Object var2, int var3, boolean var4, boolean var5) {
            JLabel var6 = (JLabel)super.getListCellRendererComponent(var1, var2, var3, var4, var5);
            String var7 = String.valueOf(var2);
            if (WorkbenchFrame.this.searchResultsMode) {
               var6.setText(
                  "<html><b>"
                     + HxWorkbench.WorkbenchFrame.html(var7)
                     + "</b>　"
                     + HxWorkbench.WorkbenchFrame.html(HxWorkbench.WorkbenchFrame.commandDescription(var7))
                     + "<br><span style='color:#637083'>"
                     + HxWorkbench.WorkbenchFrame.html(HxWorkbench.WorkbenchFrame.commandPath(var7))
                     + "</span></html>"
               );
            } else {
               var6.setText(var7 + "  ·  " + HxWorkbench.WorkbenchFrame.commandDescription(var7));
            }

            var6.setToolTipText(HxWorkbench.WorkbenchFrame.commandPath(var7));
            var6.setBorder(new EmptyBorder(4, 9, 4, 8));
            var6.setForeground(var4 ? HxWorkbench.WorkbenchFrame.ACCENT : HxWorkbench.WorkbenchFrame.TEXT);
            var6.setBackground(var4 ? HxWorkbench.WorkbenchFrame.ACCENT_SOFT : var1.getBackground());
            var6.setFont(var6.getFont().deriveFont(var4 ? 1 : 0, 10.5F));
            return var6;
         }
      }


      private static final class JSeparatorLike extends JComponent {
         JSeparatorLike() { setOpaque(false); }
         @Override protected void paintComponent(Graphics g) { super.paintComponent(g); g.setColor(new Color(225,231,239)); g.fillRect(0,0,Math.max(1,getWidth()),getHeight()); }
      }

      private static final class FlatButtonUI extends BasicButtonUI {
         private final Color normal;
         private final Color hover;
         private final Color pressed;
         private final Color foreground;
         private final Color outline;

         private FlatButtonUI(Color var1, Color var2, Color var3, Color var4, Color var5) {
            this.normal = var1;
            this.hover = var2;
            this.pressed = var3;
            this.foreground = var4;
            this.outline = var5;
         }

         @Override
         public void paint(Graphics var1, JComponent var2) {
            AbstractButton var3 = (AbstractButton)var2;
            Graphics2D var4 = (Graphics2D)var1.create();
            var4.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            ButtonModel var5 = var3.getModel();
            Color var6 = !var3.isEnabled() ? new Color(232, 235, 240) : (var5.isPressed() ? this.pressed : (var5.isRollover() ? this.hover : this.normal));
            var4.setColor(var6);
            var4.fillRoundRect(0, 0, var2.getWidth(), var2.getHeight(), 8, 8);
            var4.setColor(var3.isEnabled() ? this.outline : new Color(220, 224, 230));
            var4.drawRoundRect(0, 0, var2.getWidth() - 1, var2.getHeight() - 1, 8, 8);
            var4.dispose();
            var3.setForeground(var3.isEnabled() ? this.foreground : HxWorkbench.WorkbenchFrame.MUTED);
            super.paint(var1, var2);
         }
      }

      private static final class MissingChartPanel extends JPanel {
         private HxWorkbench.MissingAnalysisResult result;
         private String chartType = "各变量缺失率";

         MissingChartPanel() {
            this.setBackground(HxWorkbench.WorkbenchFrame.SURFACE);
            this.setPreferredSize(new Dimension(420, 320));
            this.setBorder(new EmptyBorder(12, 12, 12, 12));
         }

         void setResult(HxWorkbench.MissingAnalysisResult var1) {
            this.result = var1;
            this.repaint();
         }

         void setChartType(String var1) {
            this.chartType = var1 == null ? "各变量缺失率" : var1;
            this.repaint();
         }

         @Override
         protected void paintComponent(Graphics var1) {
            super.paintComponent(var1);
            Graphics2D var2 = (Graphics2D)var1.create();
            var2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            if (this.result == null) {
               var2.setColor(HxWorkbench.WorkbenchFrame.MUTED);
               var2.drawString("完成缺失值分析后显示图形。", 14, 24);
               var2.dispose();
            } else {
               if ("缺失矩阵".equals(this.chartType)) {
                  this.paintMatrix(var2);
               } else if ("各变量缺失率".equals(this.chartType)) {
                  this.paintBars(var2, this.result.variableChartLabels, this.result.variableChartRates, false);
               } else if ("缺失率最高的20组".equals(this.chartType)) {
                  this.paintBars(var2, this.result.groupChartLabels, this.result.groupChartRates, true);
               } else {
                  this.paintTrend(var2);
               }

               var2.dispose();
            }
         }

         private void paintBars(Graphics2D var1, List<String> var2, List<Double> var3, boolean var4) {
            ArrayList<Integer> var5 = new ArrayList<>();

            for (int var6 = 0; var6 < var2.size(); var6++) {
               var5.add(var6);
            }

            if (var4) {
               var5.sort(Comparator.<Integer>comparingDouble(var1x -> (Double)var3.get(var1x)).reversed());
            }

            if (var5.size() > 20) {
               var5 = new ArrayList(var5.subList(0, 20));
            }

            if (var5.isEmpty()) {
               var1.setColor(HxWorkbench.WorkbenchFrame.MUTED);
               var1.drawString("当前分类方式没有可绘制的分组结果。", 14, 24);
            } else {
               double var18 = 1.0;

               for (int var9 : var5) {
                  var18 = Math.max(var18, (Double)var3.get(var9));
               }

               int var19 = Math.min(150, Math.max(72, this.getWidth() / 4));
               byte var20 = 28;
               int var10 = Math.max(1, this.getHeight() - var20 - 18);
               int var11 = Math.max(8, Math.min(22, var10 / var5.size() - 3));
               int var12 = Math.max(3, var10 / var5.size() - var11);
               var1.setColor(HxWorkbench.WorkbenchFrame.TEXT);
               var1.setFont(var1.getFont().deriveFont(1));
               var1.drawString(var4 ? "缺失率最高的分组" : "各变量缺失率", 4, 16);
               var1.setFont(var1.getFont().deriveFont(0));

               for (int var13 = 0; var13 < var5.size(); var13++) {
                  int var14 = (Integer)var5.get(var13);
                  int var15 = var20 + var13 * (var11 + var12);
                  String var16 = shorten((String)var2.get(var14), 18);
                  var1.setColor(HxWorkbench.WorkbenchFrame.TEXT);
                  var1.drawString(var16, 4, var15 + var11 - 2);
                  int var17 = (int)((this.getWidth() - var19 - 58) * (Double)var3.get(var14) / var18);
                  var1.setColor(HxWorkbench.WorkbenchFrame.ACCENT_SOFT);
                  var1.fillRoundRect(var19, var15, Math.max(1, this.getWidth() - var19 - 58), var11, 6, 6);
                  var1.setColor(HxWorkbench.WorkbenchFrame.ACCENT);
                  var1.fillRoundRect(var19, var15, Math.max(1, var17), var11, 6, 6);
                  var1.setColor(HxWorkbench.WorkbenchFrame.MUTED);
                  var1.drawString(String.format(Locale.ROOT, "%.2f%%", var3.get(var14)), this.getWidth() - 52, var15 + var11 - 2);
               }
            }
         }

         private void paintTrend(Graphics2D var1) {
            ArrayList<Integer> var2 = new ArrayList<>();

            for (int var3 = 0; var3 < this.result.groupChartLabels.size(); var3++) {
               var2.add(var3);
            }

            var2.sort(Comparator.comparing(var1x -> this.result.groupChartLabels.get(var1x), HxWorkbench.WorkbenchFrame.MissingChartPanel::naturalCompare));
            if (var2.isEmpty()) {
               var1.setColor(HxWorkbench.WorkbenchFrame.MUTED);
               var1.drawString("请选择分类变量后查看缺失趋势。", 14, 24);
            } else {
               byte var16 = 52;
               byte var4 = 18;
               byte var5 = 34;
               byte var6 = 42;
               int var7 = Math.max(1, this.getWidth() - var16 - var4);
               int var8 = Math.max(1, this.getHeight() - var5 - var6);
               double var9 = 1.0;

               for (int var12 : var2) {
                  var9 = Math.max(var9, this.result.groupChartRates.get(var12));
               }

               var1.setColor(HxWorkbench.WorkbenchFrame.TEXT);
               var1.setFont(var1.getFont().deriveFont(1));
               var1.drawString("按 " + (this.result.groupNames.isEmpty() ? "分类变量" : this.result.groupNames.get(0)) + " 的缺失率", 4, 16);
               var1.setColor(HxWorkbench.WorkbenchFrame.BORDER);
               var1.drawLine(var16, var5, var16, var5 + var8);
               var1.drawLine(var16, var5 + var8, var16 + var7, var5 + var8);
               java.awt.geom.Path2D.Double var17 = new java.awt.geom.Path2D.Double();

               for (int var18 = 0; var18 < var2.size(); var18++) {
                  int var13 = (Integer)var2.get(var18);
                  int var14 = var16 + (var2.size() == 1 ? var7 / 2 : var18 * var7 / (var2.size() - 1));
                  int var15 = var5 + var8 - (int)(var8 * this.result.groupChartRates.get(var13) / var9);
                  if (var18 == 0) {
                     var17.moveTo(var14, var15);
                  } else {
                     var17.lineTo(var14, var15);
                  }

                  var1.setColor(HxWorkbench.WorkbenchFrame.ACCENT);
                  var1.fillOval(var14 - 3, var15 - 3, 6, 6);
                  if (var18 == 0 || var18 == var2.size() - 1 || var18 % Math.max(1, var2.size() / 6) == 0) {
                     var1.setColor(HxWorkbench.WorkbenchFrame.MUTED);
                     var1.drawString(shorten(this.result.groupChartLabels.get(var13), 10), var14 - 12, var5 + var8 + 18);
                  }
               }

               var1.setColor(HxWorkbench.WorkbenchFrame.ACCENT);
               var1.setStroke(new BasicStroke(2.0F));
               var1.draw(var17);
               var1.setColor(HxWorkbench.WorkbenchFrame.MUTED);
               var1.drawString(String.format(Locale.ROOT, "最高 %.2f%%", var9), 4, var5 + 4);
            }
         }

         private void paintMatrix(Graphics2D var1) {
            boolean[][] var2 = this.result.matrix;
            if (var2 != null && var2.length != 0 && !this.result.checkedNames.isEmpty()) {
               byte var3 = 54;
               byte var4 = 42;
               byte var5 = 16;
               byte var6 = 24;
               int var7 = this.result.checkedNames.size();
               int var8 = var2.length;
               double var9 = Math.max(2.0, (double)(this.getWidth() - var3 - var5) / var7);
               double var11 = Math.max(2.0, (double)(this.getHeight() - var4 - var6) / var8);
               var1.setColor(HxWorkbench.WorkbenchFrame.TEXT);
               var1.setFont(var1.getFont().deriveFont(1));
               var1.drawString("缺失矩阵（前 " + var8 + " 条观测）", 4, 16);
               var1.setFont(var1.getFont().deriveFont(9.0F));

               for (int var13 = 0; var13 < var7; var13++) {
                  if (var13 % Math.max(1, var7 / 12) == 0) {
                     int var14 = var3 + (int)(var13 * var9);
                     var1.drawString(shorten(this.result.checkedNames.get(var13), 8), var14, 34);
                  }
               }

               for (int var17 = 0; var17 < var8; var17++) {
                  for (int var18 = 0; var18 < var7; var18++) {
                     var1.setColor(var2[var17][var18] ? new Color(218, 83, 83) : new Color(223, 235, 249));
                     int var15 = var3 + (int)Math.floor(var18 * var9);
                     int var16 = var4 + (int)Math.floor(var17 * var11);
                     var1.fillRect(var15, var16, Math.max(1, (int)Math.ceil(var9)), Math.max(1, (int)Math.ceil(var11)));
                  }
               }

               var1.setColor(HxWorkbench.WorkbenchFrame.MUTED);
               var1.drawString("蓝色=有数据   红色=缺失", 4, this.getHeight() - 5);
            } else {
               var1.setColor(HxWorkbench.WorkbenchFrame.MUTED);
               var1.drawString("当前没有可绘制的缺失矩阵。", 14, 24);
            }
         }

         private static int naturalCompare(String var0, String var1) {
            try {
               return Double.compare(Double.parseDouble(var0.replace(",", "")), Double.parseDouble(var1.replace(",", "")));
            } catch (NumberFormatException var3) {
               return var0.compareToIgnoreCase(var1);
            }
         }

         private static String shorten(String var0, int var1) {
            if (var0 != null && var0.length() > var1) {
               return var0.substring(0, Math.max(1, var1 - 1)) + "…";
            } else {
               return var0 == null ? "" : var0;
            }
         }
      }

      private static final class WidthTrackingPanel extends JPanel implements Scrollable {
         private WidthTrackingPanel() {
            super(new GridBagLayout());
         }

         @Override
         public Dimension getPreferredScrollableViewportSize() {
            return this.getPreferredSize();
         }

         @Override
         public int getScrollableUnitIncrement(Rectangle visibleRect, int orientation, int direction) {
            return 18;
         }

         @Override
         public int getScrollableBlockIncrement(Rectangle visibleRect, int orientation, int direction) {
            return Math.max(18, visibleRect.height - 18);
         }

         @Override
         public boolean getScrollableTracksViewportWidth() {
            return true;
         }

         @Override
         public boolean getScrollableTracksViewportHeight() {
            return false;
         }
      }

      private static final class RoundedBorder extends AbstractBorder {
         private final Color color;
         private final int radius;

         private RoundedBorder(Color var1, int var2) {
            this.color = var1;
            this.radius = var2;
         }

         @Override
         public void paintBorder(Component var1, Graphics var2, int var3, int var4, int var5, int var6) {
            Graphics2D var7 = (Graphics2D)var2.create();
            var7.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            var7.setColor(this.color);
            var7.drawRoundRect(var3, var4, var5 - 1, var6 - 1, this.radius, this.radius);
            var7.dispose();
         }

         @Override
         public Insets getBorderInsets(Component var1) {
            return new Insets(1, 1, 1, 1);
         }
      }

      private static final class SoftListRenderer extends DefaultListCellRenderer {
         @Override
         public Component getListCellRendererComponent(JList<?> var1, Object var2, int var3, boolean var4, boolean var5) {
            JLabel var6 = (JLabel)super.getListCellRendererComponent(var1, var2, var3, var4, var5);
            if ("hxconvert".equals(String.valueOf(var2))) {
               var6.setText("转换为 DTA");
            }

            var6.setBorder(new EmptyBorder(4, 9, 4, 8));
            var6.setForeground(var4 ? HxWorkbench.WorkbenchFrame.ACCENT : HxWorkbench.WorkbenchFrame.TEXT);
            var6.setBackground(var4 ? HxWorkbench.WorkbenchFrame.ACCENT_SOFT : var1.getBackground());
            var6.setFont(var6.getFont().deriveFont(var4 ? 1 : 0, 11.0F));
            return var6;
         }
      }

      private static final class VceRenderer extends DefaultListCellRenderer {
         @Override
         public Component getListCellRendererComponent(JList<?> var1, Object var2, int var3, boolean var4, boolean var5) {
            JLabel var6 = (JLabel)super.getListCellRendererComponent(var1, var2, var3, var4, var5);
            String var7 = String.valueOf(var2);
            if ("default".equalsIgnoreCase(var7)) {
               var6.setText("默认");
            } else if ("robust".equalsIgnoreCase(var7)) {
               var6.setText("Robust（稳健标准误）");
            } else if ("cluster".equalsIgnoreCase(var7)) {
               var6.setText("Cluster（按组聚类）");
            }

            return var6;
         }
      }

      private static final class WorkSnapshot {
         String command = "";
         String category = "";
         String method = "";
         String label = "";
         String depvar = "";
         String x = "";
         String controls = "";
         String extraTerms = "";
         String vce = "";
         String cluster = "";
         String ifcond = "";
         String incond = "";
         String options = "";
         String weightType = "";
         String weightVar = "";
         String flags = "";
         String oneY = "";
         String oneX = "";
         String oneRequired = "";
         String oneCandidates = "";
         String oneEstimator = "";
         String oneAbsorb = "";
         String oneVce = "";
         String oneCluster = "";
         String didAction = "";
         String didUnit = "";
         String didTime = "";
         String didTreat = "";
         String didPost = "";
         String didEvent = "";
         String didEventCode = "";
         String didPolicyTime = "";
         String didBase = "";

         String encode() {
            return String.join(
               "|",
               e(this.command),
               e(this.category),
               e(this.method),
               e(this.label),
               e(this.depvar),
               e(this.x),
               e(this.controls),
               e(this.extraTerms),
               e(this.vce),
               e(this.cluster),
               e(this.ifcond),
               e(this.incond),
               e(this.options),
               e(this.weightType),
               e(this.weightVar),
               e(this.flags),
               e(this.oneY),
               e(this.oneX),
               e(this.oneRequired),
               e(this.oneCandidates),
               e(this.oneEstimator),
               e(this.oneAbsorb),
               e(this.oneVce),
               e(this.oneCluster),
               e(this.didAction),
               e(this.didUnit),
               e(this.didTime),
               e(this.didTreat),
               e(this.didPost),
               e(this.didEvent),
               e(this.didEventCode),
               e(this.didPolicyTime),
               e(this.didBase)
            );
         }

         static HxWorkbench.WorkbenchFrame.WorkSnapshot decode(String var0) {
            if (var0 != null && !var0.isBlank()) {
               String[] var1 = var0.split("\\|", -1);
               if (var1.length < 33) {
                  return null;
               } else {
                  HxWorkbench.WorkbenchFrame.WorkSnapshot var2 = new HxWorkbench.WorkbenchFrame.WorkSnapshot();
                  int var3 = 0;
                  var2.command = d(var1[var3++]);
                  var2.category = d(var1[var3++]);
                  var2.method = d(var1[var3++]);
                  var2.label = d(var1[var3++]);
                  var2.depvar = d(var1[var3++]);
                  var2.x = d(var1[var3++]);
                  var2.controls = d(var1[var3++]);
                  var2.extraTerms = d(var1[var3++]);
                  var2.vce = d(var1[var3++]);
                  var2.cluster = d(var1[var3++]);
                  var2.ifcond = d(var1[var3++]);
                  var2.incond = d(var1[var3++]);
                  var2.options = d(var1[var3++]);
                  var2.weightType = d(var1[var3++]);
                  var2.weightVar = d(var1[var3++]);
                  var2.flags = d(var1[var3++]);
                  var2.oneY = d(var1[var3++]);
                  var2.oneX = d(var1[var3++]);
                  var2.oneRequired = d(var1[var3++]);
                  var2.oneCandidates = d(var1[var3++]);
                  var2.oneEstimator = d(var1[var3++]);
                  var2.oneAbsorb = d(var1[var3++]);
                  var2.oneVce = d(var1[var3++]);
                  var2.oneCluster = d(var1[var3++]);
                  var2.didAction = d(var1[var3++]);
                  var2.didUnit = d(var1[var3++]);
                  var2.didTime = d(var1[var3++]);
                  var2.didTreat = d(var1[var3++]);
                  var2.didPost = d(var1[var3++]);
                  var2.didEvent = d(var1[var3++]);
                  var2.didEventCode = d(var1[var3++]);
                  var2.didPolicyTime = d(var1[var3++]);
                  var2.didBase = d(var1[var3++]);
                  return var2;
               }
            } else {
               return null;
            }
         }

         private static String e(String var0) {
            String var1 = var0 == null ? "" : var0;
            return Base64.getUrlEncoder().withoutPadding().encodeToString(var1.getBytes(StandardCharsets.UTF_8));
         }

         private static String d(String var0) {
            if (var0 != null && !var0.isBlank()) {
               try {
                  return new String(Base64.getUrlDecoder().decode(var0), StandardCharsets.UTF_8);
               } catch (IllegalArgumentException var2) {
                  return "";
               }
            } else {
               return "";
            }
         }
      }
   }

   private static final class XlsxInspector {
      static List<String> sheetNames(Path var0) {
         if (!var0.toString().toLowerCase(Locale.ROOT).endsWith(".xlsx")) {
            return Collections.emptyList();
         } else {
            try {
               ArrayList var14;
               try (ZipFile var1 = new ZipFile(var0.toFile())) {
                  ZipEntry var2 = var1.getEntry("xl/workbook.xml");
                  if (var2 == null) {
                     return Collections.emptyList();
                  }

                  DocumentBuilderFactory var3 = DocumentBuilderFactory.newInstance();
                  var3.setNamespaceAware(false);

                  try {
                     var3.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
                  } catch (Exception var10) {
                  }

                  Document var4 = var3.newDocumentBuilder().parse(var1.getInputStream(var2));
                  NodeList var5 = var4.getElementsByTagName("sheet");
                  ArrayList var6 = new ArrayList();

                  for (int var7 = 0; var7 < var5.getLength(); var7++) {
                     String var8 = var5.item(var7).getAttributes().getNamedItem("name").getNodeValue();
                     if (var8 != null && !var8.isBlank()) {
                        var6.add(var8);
                     }
                  }

                  var14 = var6;
               }

               return var14;
            } catch (Exception var12) {
               return Collections.emptyList();
            }
         }
      }
   }
}
