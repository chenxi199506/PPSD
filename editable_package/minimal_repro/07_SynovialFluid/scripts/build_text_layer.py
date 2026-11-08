"""生成图版交付的文字层：图注 / 索引页 / 清单（含 MD5 与物理尺寸校验）。

图版本体保持纯英文；本脚本只产出图版之外的文本层，可双语。

用法
----
    python build_text_layer.py spec.json
    python build_text_layer.py spec.json --check      # 只做体检，不写文件

spec.json 结构（只需填有的字段，缺省值见 DEFAULTS）：

{
  "outdir": "E:/project/30_figure_package_20260101",
  "figdir": "figures",
  "gallery": "图版索引_20260101.html",
  "legends": "Figure_legends_20260101.md",
  "manifest": "图版交付清单_20260101.csv",
  "expect_width_mm": 180,
  "expect_dpi": 600,
  "title_en": "…", "title_cn": "…",
  "lede_en": "…", "lede_cn": "…",
  "footer_spec_en": "…", "footer_spec_cn": "…",
  "footer_unit_en": "…", "footer_unit_cn": "…",
  "figures": [
    {"file": "FigureS1_depth", "number": "Figure S1",
     "short_en": "…", "short_cn": "…",
     "supports_en": "…", "supports_cn": "…",
     "not_en": "…", "not_cn": "…",
     "panels": [["A", "英文说明", "中文说明"]],
     "caption_en": "…", "caption_cn": "…"}
  ]
}
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DEFAULTS = {
    "figdir": "figures",
    "gallery": "figure_index.html",
    "legends": "Figure_legends.md",
    "manifest": "figure_manifest.csv",
    "expect_width_mm": 180.0,
    "expect_dpi": 600,
    "bilingual": True,
}


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(png: Path, expect_w: float, expect_dpi: int) -> dict:
    """从 PNG 自身的 pHYs 反推物理尺寸——以文件为准，不信任脚本里的意图。"""
    from PIL import Image

    im = Image.open(png)
    dpi = im.info.get("dpi", (expect_dpi, expect_dpi))[0]
    w_mm = im.width / dpi * 25.4
    h_mm = im.height / dpi * 25.4
    problems = []
    if expect_w and abs(w_mm - expect_w) > 1.5:
        problems.append(f"width {w_mm:.0f} mm != {expect_w:.0f} mm")
    if expect_dpi and round(dpi) != expect_dpi:
        problems.append(f"dpi {dpi:.0f} != {expect_dpi}")
    return dict(width_mm=round(w_mm, 1), height_mm=round(h_mm, 1),
                dpi=int(round(dpi)), px=f"{im.width}x{im.height}", problems=problems)


def audit(spec: dict, figdir: Path) -> list[str]:
    errs, warns = [], []
    for f in spec["figures"]:
        stem = f["file"]
        png, pdf = figdir / f"{stem}.png", figdir / f"{stem}.pdf"
        tag = f.get("number", stem)
        if not png.exists():
            errs.append(f"{tag}: 缺 PNG {png.name}")
            continue
        if not pdf.exists():
            warns.append(f"{tag}: 缺矢量 PDF（期刊排版通常需要）")
        else:
            head = pdf.read_bytes()[:8]
            if b"Type3" in pdf.read_bytes()[-4000:]:
                warns.append(f"{tag}: PDF 可能含 Type 3 字体，投稿会拒")
            if not head.startswith(b"%PDF"):
                errs.append(f"{tag}: PDF 文件头异常")
        p = probe(png, spec["expect_width_mm"], spec["expect_dpi"])
        errs += [f"{tag}: {m}" for m in p["problems"]]
        for k, label in (("short_en", "标题"), ("supports_en", "supports"),
                         ("not_en", "does-not-support"), ("caption_en", "图注")):
            if not f.get(k):
                errs.append(f"{tag}: 缺 {label}（每张图必须写明支撑什么、不支撑什么）")
        if not f.get("panels"):
            warns.append(f"{tag}: 没有面板表")
        if spec.get("bilingual"):
            for k, label in (("short_cn", "中文标题"), ("supports_cn", "中文 supports"),
                             ("not_cn", "中文 does-not-support"), ("caption_cn", "中文图注")):
                if not f.get(k):
                    warns.append(f"{tag}: 缺 {label}")
    return errs, warns


def build(spec: dict, root: Path, figdir: Path) -> dict:
    rows = []
    for f in spec["figures"]:
        stem = f["file"]
        png, pdf = figdir / f"{stem}.png", figdir / f"{stem}.pdf"
        p = probe(png, spec["expect_width_mm"], spec["expect_dpi"])
        rows.append({
            "figure": f.get("number", stem),
            "title_en": f.get("short_en", ""),
            "title_cn": f.get("short_cn", ""),
            "file_png": png.name,
            "panels": len(f.get("panels", [])),
            "width_mm": p["width_mm"],
            "height_mm": p["height_mm"],
            "dpi": p["dpi"],
            "png_mb": round(png.stat().st_size / 1e6, 2),
            "pdf_kb": round(pdf.stat().st_size / 1e3, 1) if pdf.exists() else "",
            "md5_png": md5(png),
        })

    # ---------------- manifest
    import csv

    with open(root / spec["manifest"], "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # ---------------- legends (markdown)
    bi = spec.get("bilingual")
    L = [f"# Figure legends{ ' ｜ 图注（中英对照）' if bi else ''}", ""]
    if spec.get("title_en"):
        L += [spec["title_en"], ""]
    if bi and spec.get("title_cn"):
        L += [spec["title_cn"], ""]
    if bi:
        L += ["**Language note.** Plates are English-only for submission; legends and this index are bilingual.",
              "**语言说明.** 图版为投稿用纯英文版；图注与本索引为中英对照。", ""]
    for f in spec["figures"]:
        L += [f"## {f.get('number','')}. {f.get('short_en','')}", ""]
        if bi:
            L += [f"### {f.get('short_cn','')}", ""]
        L += [f"**What this figure supports.** {f.get('supports_en','')}", ""]
        if bi:
            L += [f"**本图支持什么.** {f.get('supports_cn','')}", ""]
        L += [f"**What it does not support.** {f.get('not_en','')}", ""]
        if bi:
            L += [f"**本图不支持什么.** {f.get('not_cn','')}", ""]
        if f.get("panels"):
            L += ["| Panel | Content (EN) | 内容（中文） |", "|---|---|---|"] if bi \
                else ["| Panel | Content |", "|---|---|"]
            for row in f["panels"]:
                L.append(f"| **{row[0]}** | {row[1]} | {row[2]} |" if bi and len(row) > 2
                         else f"| **{row[0]}** | {row[1]} |")
            L.append("")
        L += [f"**Caption.** {f.get('caption_en','')}", ""]
        if bi:
            L += [f"**图注.** {f.get('caption_cn','')}", ""]
    (root / spec["legends"]).write_text("\n".join(L), encoding="utf-8")

    # ---------------- gallery (html)
    cards = []
    for f in spec["figures"]:
        stem = f["file"]
        rows_html = "".join(
            f'<tr><td class="pl">{r[0]}</td><td>{r[1]}'
            + (f'<span class="cn">{r[2]}</span>' if bi and len(r) > 2 and r[2] else "")
            + "</td></tr>"
            for r in f.get("panels", []))
        cards.append(f"""
<section class="card">
  <header>
    <div class="num">{f.get('number','')}</div>
    <div class="ttl">
      <h2>{f.get('short_en','')}</h2>
      {f'<p class="h2cn">{f.get("short_cn","")}</p>' if bi else ''}
    </div>
  </header>
  <a class="plate" href="{spec['figdir']}/{stem}.png" target="_blank">
    <img src="{spec['figdir']}/{stem}.png" alt="{f.get('number','')}">
  </a>
  <div class="meta">
    <span class="pill ok">supports</span>
    <div><p>{f.get('supports_en','')}</p>{f'<p class="cn">{f.get("supports_cn","")}</p>' if bi else ''}</div>
  </div>
  <div class="meta">
    <span class="pill no">does not</span>
    <div><p>{f.get('not_en','')}</p>{f'<p class="cn">{f.get("not_cn","")}</p>' if bi else ''}</div>
  </div>
  {f'<table class="panels">{rows_html}</table>' if rows_html else ''}
  <p class="cap">{f.get('caption_en','')}</p>
  {f'<p class="cap cn">{f.get("caption_cn","")}</p>' if bi else ''}
  <p class="dl">Download ｜ 下载：<a href="{spec['figdir']}/{stem}.png">PNG {rows[0]['dpi']} dpi</a>
     · <a href="{spec['figdir']}/{stem}.pdf">PDF vector</a></p>
</section>""")

    n = len(spec["figures"])
    widths = sorted({r["width_mm"] for r in rows})
    dpis = sorted({r["dpi"] for r in rows})
    stats = [
        (str(n), "figures" + (f"<br>{n} 张图版" if bi else "")),
        (f"{widths[0]:.0f} mm" if len(widths) == 1 else " / ".join(f"{w:.0f}" for w in widths),
         "plate width" + ("<br>画幅" if bi else "")),
        (f"{dpis[0]} dpi" if len(dpis) == 1 else "mixed",
         "PNG + vector PDF" + ("<br>每张均附矢量 PDF" if bi else "")),
    ]
    stat_html = "".join(f'<div class="stat"><b>{a}</b><span>{b}</span></div>' for a, b in stats)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{spec.get('title_en','Figure package')}</title>
<style>
  :root {{ --ink:#1a1a1a; --muted:#6e6e6e; --line:#e2e2e2; --bg:#fff;
           --healthy:#4c78a8; --oa:#b4482f; --paper:#fafafa; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
         font-family:"Helvetica Neue",Helvetica,Arial,"PingFang SC","Microsoft YaHei",sans-serif;
         -webkit-font-smoothing:antialiased; }}
  .wrap {{ max-width:1120px; margin:0 auto; padding:56px 32px 96px; }}
  .kicker {{ font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); }}
  h1 {{ font-size:30px; line-height:1.28; font-weight:600; margin:10px 0 6px; letter-spacing:-.01em; }}
  h1 .cn {{ display:block; font-size:19px; font-weight:500; color:#3a3a3a; margin-top:8px; letter-spacing:0; }}
  .lede {{ font-size:14.5px; line-height:1.78; color:#3a3a3a; max-width:78ch; margin:12px 0 4px; }}
  .lede.cn {{ font-size:13.5px; color:#4a4a4a; }}
  .rule {{ height:1px; background:var(--line); margin:30px 0 0; }}
  .grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin:26px 0 44px; }}
  .stat {{ border:1px solid var(--line); padding:16px 18px; }}
  .stat b {{ display:block; font-size:22px; font-weight:600; letter-spacing:-.01em; }}
  .stat span {{ font-size:12px; color:var(--muted); display:block; line-height:1.6; }}
  .card {{ border-top:2px solid var(--ink); padding:26px 0 44px; }}
  .card header {{ display:flex; align-items:flex-start; gap:14px; margin-bottom:18px; }}
  .num {{ font-size:12px; font-weight:700; letter-spacing:.06em; white-space:nowrap;
          padding:3px 9px; border:1px solid var(--ink); margin-top:3px; }}
  h2 {{ font-size:17px; font-weight:600; margin:0; line-height:1.4; letter-spacing:-.01em; }}
  .h2cn {{ font-size:14.5px; color:#4a4a4a; margin:4px 0 0; line-height:1.5; }}
  .plate {{ display:block; border:1px solid var(--line); background:var(--paper); padding:10px; }}
  .plate img {{ display:block; width:100%; height:auto; }}
  .meta {{ display:flex; gap:12px; align-items:flex-start; margin-top:14px; }}
  .pill {{ font-size:10.5px; letter-spacing:.05em; text-transform:uppercase; padding:2px 8px;
           white-space:nowrap; margin-top:3px; }}
  .pill.ok {{ background:#eef3f7; color:var(--healthy); border:1px solid #cfdde9; }}
  .pill.no {{ background:#faf0ed; color:var(--oa); border:1px solid #efd6ce; }}
  .meta p {{ margin:0; font-size:13.5px; line-height:1.7; color:#2e2e2e; }}
  .cn {{ display:block; font-size:13px; line-height:1.85; color:#5c5c5c; margin-top:6px; }}
  table.panels {{ width:100%; border-collapse:collapse; margin:18px 0 0; font-size:13px; }}
  table.panels td {{ padding:9px 10px; border-bottom:1px solid var(--line); line-height:1.65; vertical-align:top; }}
  td.pl {{ width:44px; font-weight:700; color:var(--muted); }}
  .cap {{ font-size:12.5px; line-height:1.8; color:#4a4a4a; margin:16px 0 0; text-align:justify; }}
  .cap.cn {{ color:#666; }}
  .dl {{ font-size:12px; color:var(--muted); margin:14px 0 0; }}
  a {{ color:var(--healthy); }}
  footer {{ border-top:1px solid var(--line); padding-top:20px; font-size:12.5px;
            color:var(--muted); line-height:1.85; }}
  footer p {{ margin:0 0 10px; }}
  code {{ font-size:11.5px; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="kicker">{spec.get('kicker','Figure package')}</div>
  <h1>{spec.get('title_en','')}
    {f'<span class="cn">{spec.get("title_cn","")}</span>' if bi else ''}</h1>
  <p class="lede">{spec.get('lede_en','')}</p>
  {f'<p class="lede cn">{spec.get("lede_cn","")}</p>' if bi else ''}
  <div class="grid">{stat_html}</div>
  <div class="rule"></div>
  {''.join(cards)}
  <footer>
    <p><b>交付规格 ｜ specification</b><br>{spec.get('footer_spec_en','')}
    {f'<br>{spec.get("footer_spec_cn","")}' if bi else ''}</p>
    <p><b>统计口径 ｜ analytic unit</b><br>{spec.get('footer_unit_en','')}
    {f'<br>{spec.get("footer_unit_cn","")}' if bi else ''}</p>
    <p><b>文件 ｜ files</b><br>
    <code>{spec['figdir']}/*.png</code> · <code>{spec['figdir']}/*.pdf</code> ·
    <code>{spec['legends']}</code> · <code>{spec['manifest']}</code></p>
  </footer>
</div>
</body>
</html>"""
    (root / spec["gallery"]).write_text(html, encoding="utf-8")

    return {"rows": rows, "n": n}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check_only = "--check" in sys.argv
    if not args:
        print(__doc__)
        return 2
    spec_path = Path(args[0]).resolve()
    spec = {**DEFAULTS, **json.loads(spec_path.read_text(encoding="utf-8"))}
    root = Path(spec.get("outdir") or spec_path.parent).resolve()
    figdir = root / spec["figdir"]

    errs, warns = audit(spec, figdir)
    for w in warns:
        print(f"  warn  {w}")
    for e in errs:
        print(f"  ERROR {e}")
    if errs:
        print(f"\n{len(errs)} 个阻断问题，未写文件。")
        return 1
    if check_only:
        print("\n体检通过（未写文件）。")
        return 0

    out = build(spec, root, figdir)
    print(f"\n{out['n']} 张图版 → {root}")
    for name in (spec["gallery"], spec["legends"], spec["manifest"]):
        p = root / name
        print(f"  wrote {name}  ({p.stat().st_size/1024:.1f} KB)")
    for r in out["rows"]:
        print(f"    {r['figure']:<12} {r['width_mm']:>5.1f} x {r['height_mm']:>5.1f} mm"
              f"  {r['panels']} panels  md5 {r['md5_png'][:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
