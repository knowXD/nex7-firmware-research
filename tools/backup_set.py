#!/usr/bin/env python3
"""Set a Backup.bin property and fix the checksum."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Sony-PMCA-RE-master"))
from pmca.backup import BackupFile

def main():
    if len(sys.argv) < 5:
        print("usage: backup_set.py in.bin out.bin <id-hex> <data-hex>")
        return
    src, dst, pid, data = sys.argv[1], sys.argv[2], int(sys.argv[3], 16), bytes.fromhex(sys.argv[4])
    b = BackupFile(open(src, "rb"))
    old = b.getProperty(pid).data
    if len(data) != len(old):
        print("size mismatch: property is %d bytes, got %d" % (len(old), len(data)))
        return
    b.setProperty(pid, data)
    b.updateChecksum()
    out = open(dst, "wb")
    f = b.file
    f.seek(0)
    out.write(f.read())
    out.close()
    print("0x%08x: %s -> %s" % (pid, old.hex(), data.hex()))
    print("written", dst)

if __name__ == "__main__":
    main()
