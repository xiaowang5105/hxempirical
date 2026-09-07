package com.hexie.stata;

import java.io.IOException;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;

/** File-side planning and publication; independent of Swing and live Stata. */
final class DataWorkflow {
    static Map<Path,Path> batchOutputs(List<Path> inputs, Path directory) throws IOException {
        Map<Path,Path> outputs = new LinkedHashMap<>();
        Map<String,Path> names = new HashMap<>();
        for (Path input : inputs) {
            String name = input.getFileName().toString();
            int dot = name.lastIndexOf('.');
            String target = (dot < 0 ? name : name.substring(0,dot)) + ".dta";
            // Use portable case-insensitive names even on case-sensitive systems.
            Path previous = names.putIfAbsent(target.toLowerCase(Locale.ROOT), input);
            if (previous != null) throw new IOException("多个原文件指向同一个 DTA：\n"+previous+"\n"+input+"\n请重命名原文件或分开转换。");
            outputs.put(input,directory.resolve(target).toAbsolutePath().normalize());
        }
        return outputs;
    }

    static final class OutputTarget {
        final Path path;
        private final BasicFileAttributes before;

        OutputTarget(Path target, boolean overwriteApproved) throws IOException {
            path = target.toAbsolutePath().normalize();
            before = attributes(path);
            if (before != null && !overwriteApproved) throw new FileAlreadyExistsException(path.toString());
        }

        boolean replacesExisting() { return before != null; }

        private static BasicFileAttributes attributes(Path path) throws IOException {
            try {
                BasicFileAttributes a = Files.readAttributes(path,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
                if (!a.isRegularFile() || a.isSymbolicLink()) throw new IOException("目标必须为普通文件："+path);
                return a;
            } catch (NoSuchFileException e) { return null; }
        }

        void publish(Path staged) throws IOException {
            BasicFileAttributes now = attributes(path);
            if (before == null && now != null) throw new IOException("转换期间目标文件已出现，已保留该文件："+path);
            if (before != null && (now == null || before.size()!=now.size()
                    || !before.lastModifiedTime().equals(now.lastModifiedTime())
                    || !Objects.equals(before.fileKey(),now.fileKey())))
                throw new IOException("确认覆盖后目标文件发生变化，已停止替换："+path);
            try (FileChannel channel=FileChannel.open(staged,StandardOpenOption.WRITE)) { channel.force(true); }
            if (before == null) {
                // ATOMIC_MOVE may replace an existing target even without REPLACE_EXISTING.
                Files.move(staged,path);
            } else {
                Files.move(staged,path,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
            }
        }
    }

    static String conversionScript(String importCommand, Path output) throws IOException {
        return "* Recreate converted DTA; inspect the output path before replay.\n"
            + "tempname hx_conversion_frame\nframe create `hx_conversion_frame'\n"
            + "capture noisily {\n    frame `hx_conversion_frame': " + importCommand
            + "\n    frame `hx_conversion_frame': save " + ResearchProject.stataQuote(output.toString()) + ", replace\n}\n"
            + "local hx_conversion_rc = _rc\nframe drop `hx_conversion_frame'\n"
            + "if `hx_conversion_rc' error `hx_conversion_rc'";
    }
}
