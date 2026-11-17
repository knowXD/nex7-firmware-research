import re
for name in ["libInfraExtCmdSvc.so", "libInfraPtpExtCmd.so", "libInfraMscServer.so"]:
    p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/" + name
    d = open(p,"rb").read()
    print("==", name, len(d))
    for m in re.finditer(rb"[\x20-\x7e]{5,}", d):
        s = m.group().decode("latin1")
        if any(k in s.lower() for k in ["senser", "packet", "cmd", "exec", "scenario", "plugin", "usb"]):
            print("   ", s[:100])
