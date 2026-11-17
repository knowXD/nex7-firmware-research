import re
p = "nex7/fw101/Sony_Update_NEX7V101/Sony_Update_NEX7V101.exe"
d = open(p, "rb").read()
for sig, name in [(b"PK\x03\x04","local"), (b"PK\x01\x02","central"), (b"PK\x05\x06","eocd")]:
    offs = [m.start() for m in re.finditer(re.escape(sig), d)]
    print(name, len(offs), offs[:8], offs[-3:] if offs else "")
for tag in [b"Nullsoft", b"Inno Setup", b"InstallShield", b"UDTR", b"FIRM", b"firmware", b"Firmware"]:
    print(tag, d.find(tag))
