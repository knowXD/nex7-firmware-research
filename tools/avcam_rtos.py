import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
seg = d[0x1000:0x1400]
print("0x1000-0x1400 strings:")
for m in re.finditer(rb"[\x20-\x7e]{3,}", seg):
    print("  ", hex(0x1000+m.start()), m.group().decode("latin1"))
print("--- global RTOS-ish tokens ---")
for tok in [b"Tsk", b"Mbx", b"Sem", b"Flg", b"Mtx", b"Cyc", b"Alm", b"Mem", b"Sync", b"OSAL", b"msgq", b"MsgQ"]:
    offs = [m.start() for m in re.finditer(re.escape(tok), d)]
    print(tok, len(offs), [hex(o) for o in offs[:6]])
