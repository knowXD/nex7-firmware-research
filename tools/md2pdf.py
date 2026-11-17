#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""md2pdf.py -- 把本项目的 Markdown 文档转成可打印/可发微信的 PDF。

不依赖 pandoc / LibreOffice：自己把 Markdown 渲染成 HTML（只支持本项目用到的那几种语法），
再用 Edge 的 headless print-to-pdf 出 PDF。

用法：
  python md2pdf.py nex7/hack/RESCUE_PLAN.md
  python md2pdf.py a.md b.md --outdir nex7/hack/pdf
"""
import argparse
import html
import os
import re
import subprocess
import sys

BT = chr(96)      # 反引号
FENCE = BT * 3

EDGE_CANDIDATES = [
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
]

CSS = """
@page { size: A4; margin: 16mm 14mm; }
body { font-family: "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
       font-size: 10.5pt; line-height: 1.6; color: #111; }
h1 { font-size: 19pt; border-bottom: 2px solid #333; padding-bottom: 4px; }
h2 { font-size: 14.5pt; margin-top: 18px; border-left: 5px solid #444; padding-left: 8px; }
h3 { font-size: 12pt; margin-top: 14px; color: #222; }
code { font-family: Consolas, "Courier New", monospace; font-size: 9.5pt;
       background: #f2f2f2; padding: 1px 3px; border-radius: 3px; }
pre { background: #f6f6f6; border: 1px solid #ddd; border-radius: 4px;
      padding: 8px 10px; overflow-x: auto; page-break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 9pt; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; page-break-inside: avoid; }
th, td { border: 1px solid #bbb; padding: 4px 6px; font-size: 9.5pt; vertical-align: top; }
th { background: #eee; }
blockquote { margin: 8px 0; padding: 6px 12px; border-left: 4px solid #888;
             background: #fafafa; color: #333; }
hr { border: none; border-top: 1px solid #ccc; margin: 14px 0; }
ul, ol { margin: 6px 0 6px 18px; padding-left: 10px; }
li { margin: 2px 0; }
"""

CODE_SPAN = re.compile("(" + BT + "[^" + BT + "]*" + BT + ")")


def inline(text):
    parts = CODE_SPAN.split(text)
    out = []
    for p in parts:
        if len(p) >= 2 and p.startswith(BT) and p.endswith(BT):
            out.append("<code>%s</code>" % html.escape(p[1:-1]))
        else:
            e = html.escape(p)
            e = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", e)
            out.append(e)
    return "".join(out)


def render(md):
    lines = md.replace("\r\n", "\n").split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if line.startswith(FENCE):
            i += 1
            buf = []
            while i < n and not lines[i].startswith(FENCE):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>%s</code></pre>" % "\n".join(buf))
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            lvl = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lvl, inline(m.group(2).strip()), lvl))
            i += 1
            continue
        if re.match(r"^\s*---+\s*$", line):
            out.append("<hr/>")
            i += 1
            continue
        if line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(inline(lines[i][1:].strip()))
                i += 1
            out.append("<blockquote>%s</blockquote>" % "<br/>".join(buf))
            continue
        if line.strip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ["<table><thead><tr>"]
            t += ["<th>%s</th>" % inline(c) for c in head]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if m:
            ordered = m.group(2)[0].isdigit()
            tag = "ol" if ordered else "ul"
            items = []
            while i < n:
                mm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                if not mm:
                    break
                items.append(inline(mm.group(3)))
                i += 1
            out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % x for x in items), tag))
            continue
        if not line.strip():
            i += 1
            continue
        stop = re.compile(r"^(#{1,6}\s|" + FENCE + r"|\||>|\s*---+\s*$)")
        buf = []
        while i < n and lines[i].strip() and not stop.match(lines[i]):
            buf.append(inline(lines[i].strip()))
            i += 1
        out.append("<p>%s</p>" % "<br/>".join(buf))
    return "\n".join(out)


def find_edge():
    for p in EDGE_CANDIDATES:
        if os.path.exists(p):
            return p
    raise SystemExit("找不到 msedge.exe，无法生成 PDF")


def convert(md_path, outdir):
    with open(md_path, "r", encoding="utf-8") as f:
        md = f.read()
    title = os.path.basename(md_path)
    for ln in md.split("\n"):
        if ln.startswith("# "):
            title = ln[2:].strip()
            break
    doc = ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
           "<title>%s</title><style>%s</style></head><body>%s</body></html>"
           % (html.escape(title), CSS, render(md)))
    os.makedirs(outdir, exist_ok=True)
    base = os.path.splitext(os.path.basename(md_path))[0]
    html_path = os.path.abspath(os.path.join(outdir, base + ".html"))
    pdf_path = os.path.abspath(os.path.join(outdir, base + ".pdf"))
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(doc)
    edge = find_edge()
    url = "file:///" + html_path.replace("\\", "/")
    cmd = [edge, "--headless=new", "--disable-gpu", "--no-first-run",
           "--no-pdf-header-footer", "--print-to-pdf=" + pdf_path, url]
    try:
        subprocess.run(cmd, capture_output=True, timeout=180)
    except Exception as e:
        print("  浏览器调用失败: %r" % (e,))
    if not os.path.exists(pdf_path):
        # DSH 沙箱下 Edge/Chrome 起不来（不给命名管道权限），退化成 HTML：
        # 双击 HTML，用浏览器 Ctrl+P 就能自己另存成 PDF。
        print("%s -> %s（PDF 未生成；打开这个 HTML 按 Ctrl+P 可以自己存 PDF）"
              % (md_path, html_path))
        return html_path
    print("%s -> %s (%d KB)" % (md_path, pdf_path, os.path.getsize(pdf_path) // 1024))
    return pdf_path


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--outdir", default="nex7/hack/pdf")
    a = ap.parse_args(argv)
    for p in a.files:
        convert(p, a.outdir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
