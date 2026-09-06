package com.hexie.stata;
import java.util.*;
import com.stata.sfi.Scalar;
import com.stata.sfi.Missing;

final class RunResult {
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

      static RunResult capture(String var0, int var1, String var2) {
         double var3 = Double.NaN;
         double var5 = Double.NaN;
         double var7 = Double.NaN;
         if (var1 == 0 && isEstimationCommand(var0)) {
            var3 = scalar("e(N)");
            var5 = scalar("e(r2)");
            var7 = scalar("e(r2_a)");
         }

         return new RunResult(var0, var1, var2, var1 == 0 ? "" : errorText(var1), var3, var5, var7);
      }

      static RunResult failure(String var0, int var1, String var2) {
         return new RunResult(var0, var1, "写入状态未知", var2, Double.NaN, Double.NaN, Double.NaN);
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
         double var1;
         try { var1 = Scalar.getValue(var0); } catch (Exception e) { var1 = Double.NaN; }
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
