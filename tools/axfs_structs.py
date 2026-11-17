import re
p = "nex7/dl/axfs-master/kernel/fs/axfs/axfs_fs.h"
d = open(p).read()
# print struct definitions
for m in re.finditer(r"struct axfs_\w+\s*\{[^}]*\};", d, re.S):
    print(m.group(0)[:1200])
    print("-----")
