import re
for name in ["bin/sen.elf", "bin/bootin.elf", "lib/libsencore.so"]:
    p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/" + name
    d = open(p,"rb").read()
    print("==", name, len(d))
    strs = []
    for m in re.finditer(rb"[\x20-\x7e]{5,}", d):
        s = m.group().decode("latin1")
        if any(k in s for k in ["/usr","/setting","/lib","dlopen","dlsym","scenario","plugin","Plugin",".so"]):
            strs.append(s)
    for s in strs[:25]:
        print("   ", s[:100])
