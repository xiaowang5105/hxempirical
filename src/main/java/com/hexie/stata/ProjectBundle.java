package com.hexie.stata;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.zip.*;

/** Portable project and replay script share exactly the same rewritten commands. */
final class ProjectBundle {
    static void write(ResearchProject project, Path output) throws IOException {
        Map<String,Path> files=new LinkedHashMap<>();
        files.put(project.baseline,project.asset(project.baseline));
        files.put(project.current,project.asset(project.current));
        for(ResearchProject.Run model:project.models())
            for(String suffix:Arrays.asList(".ster",".tsv",".sample"))
                files.put(model.model+suffix,project.asset(model.model+suffix));
        Map<Path,String> external=new LinkedHashMap<>();
        Path cwd=project.workingDirectory.isBlank()?project.file.getParent():Path.of(project.workingDirectory).toAbsolutePath().normalize();
        StringBuilder notes=new StringBuilder("Extract into a new folder. In Stata, cd to that folder and run replay.do.\n")
                .append("Open the .hxproj file to restore data and continue work. Commands and file settings use bundle-relative paths.\n")
                .append("Generated outputs are redirected into external. Review commands and data before running or sharing.\n")
                .append("Third-party commands, network resources and unsupported file commands require review.\n\n");
        StataFilePaths.Mapper mapper=(value,writing)->{
            Path source=Path.of(value);
            if(!source.isAbsolute()) source=cwd.resolve(source);
            source=source.toAbsolutePath().normalize();
            if(source.equals(project.asset(project.baseline))) return project.baseline;
            if(source.equals(project.asset(project.current))) return project.current;
            if(!Files.isRegularFile(source) && !writing && !external.containsKey(source))
                throw new IOException("项目文件依赖缺失，打包已停止："+source);
            String relative=external.get(source);
            if(relative==null) {
                String name=source.getFileName().toString();
                int dot=name.lastIndexOf('.');
                String suffix=dot>=0?name.substring(dot):".dta";
                if(!suffix.matches("\\.[a-zA-Z0-9]+")) throw new IOException("文件扩展名无法安全迁移："+source);
                relative="external/file-"+(external.size()+1)+suffix;
                external.put(source,relative);
                if(Files.isRegularFile(source)) files.put(relative,source);
                notes.append(Files.isRegularFile(source)?"Copied ":"Generated output ").append(source).append(" -> ").append(relative).append('\n');
            }
            return relative;
        };
        Properties properties=project.properties();
        properties.setProperty("portable","true");
        properties.setProperty("workingDirectory",".");
        List<String> commands=new ArrayList<>();
        for(int i=0;i<project.runs.size();i++) {
            ResearchProject.Run run=project.runs.get(i);
            String command=StataFilePaths.rewrite(run.command,mapper);
            commands.add(command); properties.setProperty("run."+i+".command",command);
            WorkSnapshot settings=WorkSnapshot.decode(run.settings);
            if(settings!=null) {
                settings.nativeCommand=StataFilePaths.rewrite(settings.nativeCommand,mapper);
                if(!settings.usingFile.isBlank()) settings.usingFile=mapper.map(settings.usingFile,false);
                properties.setProperty("run."+i+".settings",settings.encode());
            }
        }
        String original=project.exportDo();
        int start=original.indexOf("\n* Recorded steps start");
        if(start<0) throw new IOException("项目脚本缺少起始标记。");
        String header=original.substring(0,start);
        if(!project.workingDirectory.isBlank())
            header=header.replace("cd "+ResearchProject.stataQuote(project.workingDirectory)+"\n","");
        header=header.replace(ResearchProject.stataQuote(project.asset(project.baseline).toString()),ResearchProject.stataQuote(project.baseline));
        StringBuilder replay=new StringBuilder(header).append("\n* Recorded project steps.\n");
        for(int i=0;i<commands.size();i++) {
            ResearchProject.Run run=project.runs.get(i); String command=commands.get(i);
            replay.append("\n* ").append(run.time).append("; observed return code ").append(run.rc).append('\n');
            if(run.rc!=0 && command.contains("\n")) replay.append("capture noisily {\n").append(command).append("\n}\n");
            else { if(run.rc!=0) replay.append("capture noisily "); replay.append(command).append('\n'); }
        }
        Path temporary=Files.createTempFile(output.toAbsolutePath().getParent(),".hx-bundle-",".tmp");
        try {
            StringBuilder manifest=new StringBuilder("SHA256\tFile\n");
            try(ZipOutputStream zip=new ZipOutputStream(Files.newOutputStream(temporary))) {
                zip.putNextEntry(new ZipEntry("external/")); zip.closeEntry();
                byte[] buffer=new byte[65536];
                for(Map.Entry<String,Path> file:files.entrySet()) {
                    DelimitedData.interrupted();
                    zip.putNextEntry(new ZipEntry(file.getKey().replace('\\','/')));
                    MessageDigest digest=digest();
                    try(InputStream input=Files.newInputStream(file.getValue())) {
                        int count; while((count=input.read(buffer))!=-1) { zip.write(buffer,0,count); digest.update(buffer,0,count); DelimitedData.interrupted(); }
                    }
                    zip.closeEntry(); hash(manifest,file.getKey(),digest.digest());
                }
                entry(zip,manifest,project.file.getFileName().toString(),ResearchProject.serialize(properties));
                entry(zip,manifest,"replay.do",replay.toString());
                entry(zip,manifest,"README.txt",notes.toString());
                entry(zip,manifest,"environment.txt",project.environment+"\nThird-party command versions are not pinned.\n");
                entry(zip,null,"SHA256.tsv",manifest.toString());
            }
            try(FileChannel channel=FileChannel.open(temporary,StandardOpenOption.WRITE)) { channel.force(true); }
            Files.move(temporary,output,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
        } finally { Files.deleteIfExists(temporary); }
    }
    private static MessageDigest digest() throws IOException {
        try { return MessageDigest.getInstance("SHA-256"); } catch(NoSuchAlgorithmException e) { throw new IOException(e); }
    }
    private static void hash(StringBuilder manifest,String name,byte[] bytes) {
        for(byte b:bytes) manifest.append(String.format("%02x",b&255));
        manifest.append('\t').append(name).append('\n');
    }
    private static void entry(ZipOutputStream zip,StringBuilder manifest,String name,String text) throws IOException {
        byte[] bytes=text.getBytes(StandardCharsets.UTF_8);
        zip.putNextEntry(new ZipEntry(name)); zip.write(bytes); zip.closeEntry();
        if(manifest!=null) hash(manifest,name,digest().digest(bytes));
    }
}
