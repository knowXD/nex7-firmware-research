import urllib.request, re
urls = [
 "https://www.sony.com.br/electronics/support/e-mount-body-nex-7-series/nex-7k/downloads/W0008925",
 "https://www.sony-latin.com/es/electronics/support/e-mount-body-nex-7-series/nex-7k/downloads/W0008925",
]
for u in urls:
    try:
        req = urllib.request.Request(u, headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
            "Accept":"text/html,application/xhtml+xml",
            "Accept-Language":"pt-BR,pt;q=0.9,en;q=0.8",
        })
        r = urllib.request.urlopen(req, timeout=25)
        c = r.read().decode("utf-8","ignore")
        print(u, r.status, len(c))
        exes = re.findall(r"https?://[^\"'\s<>]+\.(?:exe|dmg|zip)", c)
        print(" ", list(dict.fromkeys(exes))[:5])
        m = re.search(r"(Ver\.?\s*\d\.\d\d)", c)
        print("  version:", m.group(1) if m else None)
    except Exception as e:
        print(u, "ERR", str(e)[:80])
