import os
root = "nex7/initrd_unpacked"
for dp, dn, fn in os.walk(root):
    rel = os.path.relpath(dp, root)
    for f in fn:
        p = os.path.join(dp, f)
        print(os.path.join(rel, f).replace("\\","/"), os.path.getsize(p))
