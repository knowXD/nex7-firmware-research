import urllib.request, re, urllib.parse
page = urllib.request.urlopen(urllib.request.Request(
    "https://xiazai.zol.com.cn/detail/59/583541.shtml",
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"}), timeout=25).read().decode("utf-8","ignore")
m = re.search(r"downloadInstaller\?cid=1144[^\"]*", page)
link = "https://soft-api.safe.360.cn/main/v1/tools/downloadInstaller?" + m.group(0)
q = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
real = q["url"][0]; rand = q.get("rand",[""])[0]; sign = q.get("sign",[""])[0]
sep = "&" if "?" in real else "?"
signed = real + sep + "rand=" + rand + "&sign=" + sign
print("signed:", signed)
try:
    req = urllib.request.Request(signed, headers={"User-Agent":"Mozilla/5.0","Referer":"https://xiazai.zol.com.cn/","Range":"bytes=0-63"})
    r = urllib.request.urlopen(req, timeout=25)
    print("ok", r.status, r.headers.get("Content-Range"), r.read(8).hex())
except Exception as e:
    print("ERR", str(e)[:120])
