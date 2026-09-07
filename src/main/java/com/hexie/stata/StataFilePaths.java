package com.hexie.stata;

import java.io.IOException;
import java.util.*;

/** Rewrites only file arguments of explicitly supported Stata commands. */
final class StataFilePaths {
    interface Mapper { String map(String path, boolean output) throws IOException; }
    private static final class Token {
        int start,end; String value; boolean quoted;
        Token(int start,int end,String value,boolean quoted) { this.start=start;this.end=end;this.value=value;this.quoted=quoted; }
    }
    static String rewrite(String script, Mapper mapper) throws IOException {
        String[] lines=script.split("\n",-1);
        boolean blockComment=false;
        for(int i=0;i<lines.length;i++) {
            String line=lines[i], trim=line.trim();
            if(blockComment || trim.startsWith("/*")) { blockComment=!trim.contains("*/"); continue; }
            if(trim.startsWith("*") || trim.startsWith("//")) continue;
            lines[i]=line(line,mapper);
        }
        return String.join("\n",lines);
    }
    private static String line(String line, Mapper mapper) throws IOException {
        List<Token> tokens=new ArrayList<>();
        for(int i=0;i<line.length();) {
            char ch=line.charAt(i);
            if(Character.isWhitespace(ch)) { i++;continue; }
            if(ch==',' || line.startsWith("//",i) || line.startsWith("/*",i)) break;
            int start=i;
            if(ch=='"') {
                int end=line.indexOf('"',i+1); if(end<0) return line;
                tokens.add(new Token(start,end+1,line.substring(i+1,end),true)); i=end+1;
            } else {
                while(i<line.length() && !Character.isWhitespace(line.charAt(i)) && line.charAt(i)!=',') i++;
                tokens.add(new Token(start,i,line.substring(start,i),false));
            }
        }
        int command=0;
        while(command<tokens.size()) {
            String token=tokens.get(command).value.toLowerCase(Locale.ROOT);
            if(Arrays.asList("capture","cap","quietly","qui","noisily","noi").contains(token.replace(":",""))) { command++; continue; }
            if(token.equals("frame") && command+1<tokens.size() && tokens.get(command+1).value.endsWith(":")) { command+=2;continue; }
            break;
        }
        if(command>=tokens.size() || tokens.get(command).quoted) return line;
        String cmd=tokens.get(command).value.toLowerCase(Locale.ROOT);
        if(cmd.equals("cd")) throw new IOException("项目命令含 cd；请先将文件引用改为明确路径并移除目录切换后打包。");
        boolean output=Arrays.asList("save","export","outsheet").contains(cmd);
        int file=-1;
        if(cmd.equals("save")) file=command+1;
        else if(cmd.equals("use")) file=command+1;
        else if(cmd.equals("import") || cmd.equals("export")) file=command+2;
        else if(cmd.equals("estimates") && command+1<tokens.size()) {
            String action=tokens.get(command+1).value;
            if(!Arrays.asList("use","save").contains(action)) return line;
            output=action.equals("save"); file=command+2;
        }
        boolean using=Arrays.asList("use","import","export","merge","append","joinby","cross","infile","infix","insheet","outsheet","hxproject").contains(cmd);
        if(using) for(int i=command+1;i+1<tokens.size();i++)
            if(!tokens.get(i).quoted && tokens.get(i).value.equalsIgnoreCase("using")) { file=i+1;break; }
        if(cmd.equals("hxproject") && command+1<tokens.size()) output=Arrays.asList("snapshot","model").contains(tokens.get(command+1).value);
        if(file<0 || file>=tokens.size()) return line;
        if(cmd.equals("append") && file+1<tokens.size())
            throw new IOException("append 使用多个文件；请拆成每条命令一个 using 文件后打包。");
        Token t=tokens.get(file);
        if(t.value.contains("`") || t.value.contains("$") || t.value.contains("\""))
            throw new IOException("文件参数含宏或复杂引号，无法可靠迁移："+t.value);
        String replacement=ResearchProject.stataQuote(mapper.map(t.value,output));
        return line.substring(0,t.start)+replacement+line.substring(t.end);
    }
}
