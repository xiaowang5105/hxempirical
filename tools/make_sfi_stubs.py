from pathlib import Path
p=Path('test-stubs/com/stata/sfi'); p.mkdir(parents=True, exist_ok=True)
files={
'Characteristic.java':'''package com.stata.sfi; public final class Characteristic { public static String getDtaChar(String n){return "";} }''',
'Data.java':'''package com.stata.sfi; public final class Data { public static long getObsTotal(){return 0L;} public static int getVarCount(){return 0;} public static String getVarName(int i){return "";} public static int getVarIndex(String n){return -1;} public static String getFormattedValue(int v,long o,boolean f){return "";} public static double getNum(int v,long o){return Double.NaN;} public static String getStr(int v,long o){return "";} public static String getVarFormat(int v){return "";} public static String getVarLabel(int v){return "";} public static boolean isVarTypeString(int v){return false;} }''',
'Frame.java':'''package com.stata.sfi; public class Frame { public static Frame connect(String n){return new Frame();} public static Frame create(String n){return new Frame();} public void drop(){} public long getObsTotal(){return 0L;} public int getVarCount(){return 0;} public String getVarName(int i){return "";} public int getVarIndex(String n){return -1;} public boolean isVarTypeString(int i){return false;} public double getNum(int v,long o){return Double.NaN;} public String getStr(int v,long o){return "";} public String getFormattedValue(int v,long o,boolean f){return "";} public String getVarLabel(int v){return "";} public String getVarFormat(int v){return "";} }''',
'Macro.java':'''package com.stata.sfi; public final class Macro { public static String getGlobal(String n){return "";} }''',
'Missing.java':'''package com.stata.sfi; public final class Missing { public static boolean isMissing(double v){return Double.isNaN(v);} }''',
'SFIToolkit.java':'''package com.stata.sfi; public final class SFIToolkit { public static void displayln(String s){} public static void errorln(String s){} public static int executeCommand(String s, boolean b){return 0;} public static String stackTraceToString(Throwable t){return t==null?"":t.toString();} }''',
'Scalar.java':'''package com.stata.sfi; public final class Scalar { public static double getValue(String n){return Double.NaN;} }'''
}
for n,c in files.items(): (p/n).write_text(c,encoding='utf-8')
print('SFI_STUBS_OK')
