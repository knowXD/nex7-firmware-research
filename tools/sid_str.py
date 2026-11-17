d = open("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libObj.so","rb").read()
import re
for m in re.finditer(rb"sid\x00", d):
    print("sid string at", hex(m.start()))
# also scenario_run string
for m in re.finditer(rb"scenario_run\x00", d):
    print("scenario_run string at", hex(m.start()))
