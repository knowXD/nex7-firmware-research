import re
p = "nex7/fw101/Sony_Update_NEX7V101/Sony_Update_NEX7V101.exe"
d = open(p,"rb").read()
urls = re.findall(rb"https?://[\x20-\x7e]{5,120}", d)
seen=[]
for u in urls:
    s=u.decode("latin1")
    if s not in seen: seen.append(s)
print("urls", len(seen))
for s in seen[:15]: print(" ", s)
# PE resources / .NET?
print("MZ", d[:2], "PE", d.find(b"PE\x00\x00"))
print(".NET", d.find(b"mscoree"), "CLR", d.find(b"BSJB"))
