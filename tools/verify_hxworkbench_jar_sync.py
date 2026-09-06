"""Bind every Java source and the shipped binary to one build manifest."""
from pathlib import Path
import hashlib
import json
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'src/main/java/com/hexie/stata'
MARKER = SOURCES / 'HxWorkbench.jar-source'
JAR = ROOT / 'hxworkbench.jar'

def source_hash(path):
    raw = path.read_bytes().replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    return hashlib.sha256(raw).hexdigest()

def manifest():
    return {'format': 2, 'jar_sha256': hashlib.sha256(JAR.read_bytes()).hexdigest(),
            'sources': {p.name: source_hash(p) for p in sorted(SOURCES.glob('*.java'))}}

def verify_binary():
    with zipfile.ZipFile(JAR) as z:
        classes = [p for p in z.namelist() if p.endswith('.class')]
        assert classes and 'com/hexie/stata/HxWorkbench.class' in classes
        assert not any(p.startswith('com/stata/sfi/') for p in classes), 'SFI stubs bundled'
        levels = set()
        for p in classes:
            magic, minor, major = struct.unpack('>IHH', z.read(p)[:8])
            assert magic == 0xCAFEBABE and major <= 55, p
            levels.add(major)
        return levels

def main():
    try:
        levels = verify_binary()
        actual = manifest()
        if '--write-marker' in sys.argv:
            MARKER.write_text(json.dumps(actual, indent=2, sort_keys=True)+'\n', encoding='utf-8')
        expected = json.loads(MARKER.read_text(encoding='utf-8'))
        assert expected == actual, 'Java source or JAR changed; rebuild against the real Stata SFI API'
        print(f'HX_JAR_SYNC_OK sources={len(actual["sources"])} java_major={sorted(levels)} jar_sha256={actual["jar_sha256"]}')
    except (AssertionError, OSError, ValueError, zipfile.BadZipFile) as e:
        print('HX_JAR_SYNC_FAIL:', e, file=sys.stderr)
        raise SystemExit(1)

if __name__ == '__main__':
    main()
