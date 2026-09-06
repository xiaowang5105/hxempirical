package com.hexie.stata;
import java.util.Base64;
import java.nio.charset.StandardCharsets;

final class WorkSnapshot {
         String command = "";
         String nativeCommand = "";
         String endog = "", instruments = "", absorb = "", panel = "", time = "";
         String model = "", expression = "", newvar = "", usingFile = "";
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

         String signature() {
            return encode();
         }

         String summary() {
            String sample = ifcond.isBlank() ? "全样本" : "if " + ifcond;
            if (!incond.isBlank()) sample += " · in " + incond;
            String error = vce.isBlank() ? "默认标准误" : vce;
            if (!cluster.isBlank()) error += "(" + cluster + ")";
            return sample + " · " + error + (weightType.isBlank() ? "" : " · " + weightType + "=" + weightVar);
         }

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
               e(this.didBase),
               e(this.nativeCommand),
               e(this.endog), e(this.instruments), e(this.absorb), e(this.panel), e(this.time),
               e(this.model), e(this.expression), e(this.newvar), e(this.usingFile)
            );
         }

         static WorkSnapshot decode(String var0) {
            if (var0 != null && !var0.isBlank()) {
               String[] var1 = var0.split("\\|", -1);
               if (var1.length < 33) {
                  return null;
               } else {
                  WorkSnapshot var2 = new WorkSnapshot();
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
                  if (var1.length > 33) var2.nativeCommand = d(var1[33]);
                  if (var1.length > 34) var2.endog = d(var1[34]);
                  if (var1.length > 35) var2.instruments = d(var1[35]);
                  if (var1.length > 36) var2.absorb = d(var1[36]);
                  if (var1.length > 37) var2.panel = d(var1[37]);
                  if (var1.length > 38) var2.time = d(var1[38]);
                  if (var1.length > 39) var2.model = d(var1[39]);
                  if (var1.length > 40) var2.expression = d(var1[40]);
                  if (var1.length > 41) var2.newvar = d(var1[41]);
                  if (var1.length > 42) var2.usingFile = d(var1[42]);
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
