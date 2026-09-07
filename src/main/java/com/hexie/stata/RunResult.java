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
            , "arima", "arch", "streg", "stcox", "xtpoisson", "xtnbreg", "intreg", "mlogit", "ologit", "oprobit"
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

      static boolean isEstimationCommand(String var0) {
         String var1 = var0 == null ? "" : var0.trim().toLowerCase(Locale.ROOT);

         if (var1.contains("\n") || var1.contains(";")) return false;
         for (int depth=0;depth<8;depth++) {
            String token=var1.split("[\\s,:]",2)[0];
            if (Arrays.asList("quietly","qui","capture","cap","noisily","noi").contains(token)) {
               var1=var1.substring(token.length()).trim();
               if(var1.startsWith(":")) var1=var1.substring(1).trim();
               continue;
            }
            if (Arrays.asList("bootstrap","bs","jackknife","jknife","svy","mi").contains(token)) {
               if(token.equals("mi") && !var1.matches("mi\\s+estimate(?:[\\s,:].*)?")) return false;
               boolean quoted=false; int parens=0, colon=-1;
               for(int i=0;i<var1.length();i++) {
                  char c=var1.charAt(i);
                  if(c=='"') quoted=!quoted;
                  if(!quoted) {
                     if(c=='(') parens++; if(c==')') parens--;
                     if(c==':' && parens==0) { colon=i; break; }
                  }
               }
               if(colon<0) return false;
               var1=var1.substring(colon+1).trim(); continue;
            }
            return ESTIMATION_COMMANDS.contains(token);
         }
         return false;
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
