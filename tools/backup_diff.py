#!/usr/bin/env python3
"""Compare two Backup.bin files and list changed properties."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Sony-PMCA-RE-master"))
from pmca.backup import BackupFile

def load(path):
    b = BackupFile(open(path, "rb"))
    props = {}
    for pid, p in b.listProperties():
        props[pid] = p.data
    return b, props

def main():
    if len(sys.argv) < 3:
        print("usage: backup_diff.py A.bin B.bin")
        return
    a, pa = load(sys.argv[1])
    b, pb = load(sys.argv[2])
    ids = sorted(set(pa) | set(pb))
    changed = 0
    for pid in ids:
        va = pa.get(pid)
        vb = pb.get(pid)
        if va != vb:
            changed += 1
            sa = va.hex() if va is not None else "<missing>"
            sb = vb.hex() if vb is not None else "<missing>"
            print("id=0x%08x  A=%s  B=%s" % (pid, sa[:80], sb[:80]))
    print("changed properties:", changed, "of", len(ids))

if __name__ == "__main__":
    main()
