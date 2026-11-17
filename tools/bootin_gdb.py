import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/bin/bootin.elf"
d = open(p,"rb").read()
for m in re.finditer(rb"[\x20-\x7e]{4,}", d):
    s = m.group().decode("latin1")
    if any(k in s.lower() for k in ["gdb","hostname","ifconfig","usb0","ip ","route","10000","gdbs","appfw","/setting/"]):
        print(hex(m.start()), s[:160])
