import os
for ver,u in [("1.01","nex7/fw101/unpacked"),("1.02","nex7/fw102/unpacked"),("1.03","nex7/unpacked")]:
    d=os.path.join(u,"firmware.tar_unpacked/0700_part_image/dev")
    for f in ["nflasha3_unpacked","nflasha8_unpacked"]:
        p=os.path.join(d,f)
        if os.path.exists(p):
            print(ver,f,os.path.getsize(p), "=", round(os.path.getsize(p)/1048576,2), "MB")
