import zipfile, io, os
p = "nex7/fw101/Sony_Update_NEX7V101/Sony_Update_NEX7V101.exe"
d = open(p, "rb").read()
i = d.find(b"PK\x03\x04")
print("zip at", i, "tail", len(d)-i)
blob = d[i:]
open("nex7/fw101/embedded.zip", "wb").write(blob)
try:
    z = zipfile.ZipFile(io.BytesIO(blob))
    for n in z.namelist():
        print(n, z.getinfo(n).file_size)
except Exception as e:
    print("zip ERR", str(e)[:150])
