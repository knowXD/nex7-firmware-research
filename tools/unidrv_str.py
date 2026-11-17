import re
d = open("nex7/initrd_unpacked/kmod/unidrv1.ko", "rb").read()
print("== BOOTDATA / partinf / update 相关 ==")
seen = set()
for m in re.finditer(rb"[ -~]{5,}", d):
    s = m.group().decode("latin1")
    if re.search(r"BOOTDATA|partinf|partconf|bootdata|BOOT|flag|update|dlmode|dmode|dmode", s) and s not in seen:
        seen.add(s)
        print("   ", s[:120])
print("\n== 物理/逻辑 设备相关 ==")
for m in re.finditer(rb"[ -~]{8,}", d):
    s = m.group().decode("latin1")
    if re.search(r"physical|logical|number of", s, re.I):
        print("   ", s[:120])
