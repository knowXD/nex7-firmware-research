import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libInfraExtCmdSvc.so"
d = open(p,"rb").read()
for m in re.finditer(rb"[A-Za-z0-9_./%-]{4,}\.so", d):
    print(hex(m.start()), m.group().decode())
# also check libInfraPtpExtCmd for plugin libs
p2 = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libInfraPtpExtCmd.so"
d2 = open(p2,"rb").read()
print("== ptpextcmd")
for m in re.finditer(rb"[A-Za-z0-9_./%-]{4,}\.so", d2):
    print(hex(m.start()), m.group().decode())
