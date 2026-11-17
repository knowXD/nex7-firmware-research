import dnfile, os
p = "nex7/fw101/Sony_Update_NEX7V101/Sony_Update_NEX7V101.exe"
pe = dnfile.dnPE(p)
print("sections:")
for s in pe.sections:
    print("  ", s.Name.rstrip(b"\x00"), hex(s.VirtualAddress), hex(s.SizeOfRawData))
print("manifest resources:")
try:
    for r in pe.net.mdtables.ManifestResource.rows:
        print("  name=", r.Name, "offset=", r.Offset, "impl=", r.Implementation.row_index if r.Implementation else None)
except Exception as e:
    print("  err", e)
print("pe.net.resources:", type(pe.net.resources))
try:
    for res in pe.net.resources:
        data = res.data
        print("  ", res.name, len(data) if data else None, data[:8].hex() if data else "")
except Exception as e:
    print("  err", e)
