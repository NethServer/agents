#!/usr/bin/env python3
"""Mirror the Nebula Design System site into references/site/ of this skill.

The site (https://nethesis.github.io/nebula-design-system/) is built in the browser, but it
publishes its content as plain files for agents, listed in llms.txt. This script downloads
them and writes one markdown file per topic, so the skill always says what the site says.

Usage (from the skill folder):
    python scripts/sync_site.py                    # download from the published site
    python scripts/sync_site.py --from-dir DIR     # read a local build (dist/ of the site repo)
        [--components-json PATH]                   # and a local storybook-static/components.json

Without network access to github.io, build the site locally:
    git clone https://github.com/nethesis/nebula-design-system && cd nebula-design-system
    npm ci && npm run build   # then: --from-dir <repo>/dist

Never edit references/site/ by hand: change the site, then run this script again.
"""
import argparse, datetime, json, re, sys, urllib.request
from pathlib import Path

SITE = "https://nethesis.github.io/nebula-design-system/"
COMPONENTS_JSON = "https://nethesis.github.io/vue-components/components.json"
OUT = Path(__file__).resolve().parent.parent / "references" / "site"

# site file -> mirrored file in references/site/
LINKS = {
    "writing-guidelines.md": "writing-guidelines.md",
    "glossary.json": "glossary.md",
    "icons.json": "icons.md",
    "colors.json": "colors.md",
    "foundations.json": "foundations.md",
    "accessibility.md": "accessibility.md",
    "introduction.md": "introduction.md",
}


def reader(from_dir):
    def read(name, url=None):
        if from_dir and not url:
            return (Path(from_dir) / name).read_text(encoding="utf-8")
        with urllib.request.urlopen(url or SITE + name, timeout=30) as r:
            return r.read().decode("utf-8")
    return read


def header(title, source, today):
    return (f"# {title}\n\n"
            f"> Mirror of {source}, synced on {today} by `scripts/sync_site.py`. "
            "Do not edit: the site is the source of truth. If the live site disagrees, follow the site.\n\n")


def fix_links(md):
    # links between site files point to the mirrored files
    for src, dst in LINKS.items():
        md = md.replace(f"]({src}", f"]({dst}")
    return md


def cell(v):
    if v is None:
        return ""
    if isinstance(v, list):
        v = ", ".join(str(x) for x in v)
    return str(v).replace("|", "\\|").replace("\n", " ")


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def markdown_page(text, page, today):
    title = text.splitlines()[0].lstrip("# ").strip()
    body = "\n".join(text.splitlines()[1:]).lstrip()
    return header(title, f"{SITE}?page={page}", today) + fix_links(body)


def glossary(d, today):
    prods = d["products"]
    md = header("Glossary", d["source"], today) + d["note"] + "\n\n"
    md += "Use the English term in the UI copy of mockups; the Italian column is for translations and reviews.\n\n"
    rows = []
    for t in d["terms"]:
        it = "*Keep in English*" if t.get("untranslatable") else t.get("it", "")
        av = t.get("avoid", {})
        rows.append([f"**{t['en']}**", it, t["definition"], av.get("en"), av.get("it"),
                     [prods.get(p, p) for p in t["products"]], t.get("notes")])
    md += table(["Term", "Italian", "Definition", "Avoid (en)", "Avoid (it)", "Products", "Notes"], rows)
    return md


def icons(d, today):
    packs = d["packs"]
    md = header("Icons: which icon for which meaning", d["source"], today) + d["note"] + "\n\n"
    md += "Packages: " + "; ".join(f"{k} = {v['label']} (`{v['package']}`)" for k, v in packs.items()) + ".\n\n"
    md += "`icon` is the kebab-case name: in code it is `fa` + PascalCase (`circle-plus` → `faCirclePlus`).\n\n"
    md += "## Contents\n" + "\n".join(f"- {c['title']}" for c in d["categories"]) + "\n- Custom icons without a meaning\n\n"
    for c in d["categories"]:
        md += f"## {c['title']}\n\n{c.get('description', '')}\n\n"
        rows = []
        for i in d["icons"]:
            if i["category"] != c["id"]:
                continue
            pack = i.get("pack", "fa-solid")
            if i["category"] == "sidebar":
                pack = f"ns-light (inactive) + {pack} (active)"
            rows.append([f"**{i['meaning']}**", f"`{i['icon']}`", pack, i["use"], i.get("notFor"),
                         [f"`{a}`" for a in i.get("avoid", [])],
                         [d["products"].get(p, p) for p in i.get("products", [])] or "All",
                         i.get("notes")])
        md += table(["Meaning", "Icon", "Pack", "Use", "Not for", "Avoid", "Products", "Notes"], rows) + "\n"
    md += "## Custom icons without a meaning\n\nThey have no agreed meaning yet. The site says not to use them; the skill proposes them to the designer as candidates when a meaning is missing (see Pending decisions in SKILL.md), never uses them without asking.\n\n"
    for pack, names in d["customIconsWithoutMeaning"].items():
        if names:
            md += f"- {pack}: " + ", ".join(f"`{n}`" for n in names) + "\n"
    return md


def colors(d, today):
    md = header("Colors: semantic tokens", d["source"], today)
    md += d["note"] + f"\n\nExported from the Nebula Figma file on {d.get('exportedAt')}.\n\n"
    md += "## Contents\n" + "\n".join(f"- {g['name']}" for g in d["groups"]) + "\n\n"
    for g in d["groups"]:
        md += f"## {g['name']}\n\n{g.get('description', '')}\n\n"
        rows = []
        for t in g["tokens"]:
            lt, dk = t["light"], t["dark"]
            cls = t["classes"] or "—"
            rows.append([t["name"], f"{lt['ref']} ({lt.get('tailwind') or lt.get('hex')})",
                         f"{dk['ref']} ({dk.get('tailwind') or dk.get('hex')})", f"`{cls}`" if t["classes"] else cls,
                         t.get("description")])
        md += table(["Token", "Light", "Dark", "Classes", "Description"], rows) + "\n"
    return md


def foundations(d, today):
    md = header("Foundations: typography, iconography, spacing, border, focus ring, elevation, shadow",
                d["source"], today) + d["note"] + "\n\n"
    ty = d["typography"]
    md += f"## Typography\n\nSource: {ty['source']}\n\nTypeface **{ty['typeface']['family']}** "
    md += f"(load both {', '.join('`'+i+'`' for i in ty['typeface']['imports'])}).\n\n"
    md += table(["Weight", "Value", "Class", "Use"], [[w["name"], w["value"], f"`{w['className']}`", w["use"]] for w in ty["weights"]])
    md += "\nSizes:\n\n" + table(["Name", "Class", "Size px", "Line height px"],
                                 [[s["name"], s["className"] or "not a Tailwind size", s["size"], s["lineHeight"]] for s in ty["sizes"]])
    ll = ty["lineLength"]
    md += f"\nLine length: `{ll['className']}` ({ll['px']} px). {ll['note']}\n\n"
    for grp in ty["textStyles"]:
        md += f"Text styles, {grp['title']}:\n\n" + table(["Token", "Classes", "Size / line height px", "Weight"],
            [[s["token"], f"`{s['className']}`" if s["className"] else "no Tailwind class", f"{s['size']} / {s['lineHeight']}", s["weight"]] for s in grp["styles"]]) + "\n"
    ic = d["iconography"]
    md += f"## Iconography\n\nSource: {ic['source']}\n\n{ic['note']}\n\n"
    md += table(["Pack", "Package", "Version"], [[p["pack"], f"`{p['name']}`", p["version"]] for p in ic["packages"]])
    md += "\n" + table(["Size", "Class", "Use"], [[f"{s['px']} px", f"`{s['className']}`", s["use"]] for s in ic["sizes"]]) + "\n"
    sb = d["spacingAndBorder"]
    md += f"## Spacing and border\n\nSource: {sb['source']}\n\n"
    md += "Spacing is the Tailwind scale (step × 4 px): " + ", ".join(f"{s['step']}={s['px']}px" for s in sb["spacing"]) + ".\n\n"
    md += "Radius:\n\n" + table(["Token", "Class", "px"], [[r["token"], f"`{r['className']}`", r["px"]] for r in sb["radii"]])
    md += "\nBorder width:\n\n" + table(["Token", "Class", "px"], [[b["token"], f"`{b['className']}`", b["px"]] for b in sb["borderWidths"]])
    fr = sb["focusRing"]
    md += f"\n### Focus ring\n\n{fr['note']}\n\n"
    md += "\n".join(f"- {k}: `{v}`" for k, v in fr["styles"].items()) + "\n\n"
    md += table(["Product", "Palette", "Ring", "Primary"], [[p["name"], p["palette"], p["ring"], p["primary"]] for p in fr["products"]])
    md += "\nStatus colors (focus ring 2 on colored backgrounds):\n\n" + table(["Status", "Classes"], [[s["name"], f"`{s['className']}`"] for s in fr["status"]])
    el = d["elevationAndShadow"]
    md += f"\n## Elevation and shadow\n\nSource: {el['source']}\n\n{el['note']}\n\n"
    md += table(["Level", "Light", "Dark", "Classes"], [[e["level"], e["light"], e["dark"], f"`{e['className']}`"] for e in el["elevation"]])
    md += "\n" + table(["Token", "Class", "Light", "Dark"], [[s["token"], f"`{s['className']}`", s["light"], s["dark"]] for s in el["shadows"]])
    return md


def components_index(d, today):
    md = header(f"Components and patterns of {d['package']} (v{d['version']})", d["source"], today)
    md += d["note"] + "\n\n"
    md += "## Patterns\n\nStart from these when they cover the task.\n\n"
    md += table(["Pattern", "Main component", "What it is", "Storybook"],
                [[f"**{p['name']}**", p.get("component"), p["description"], p["link"]] for p in d["patterns"]])
    md += "\n## Components\n\n"
    rows = []
    for c in d["components"]:
        name = f"~~{c['name']}~~ → use {c['replacedBy']}" if c.get("deprecated") else f"**{c['name']}**"
        rows.append([name, c["description"], c.get("parts"), c["link"]])
    md += table(["Component", "What it is for", "Parts", "Storybook"], rows)
    return md


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-dir", help="local build of the site (dist/) instead of the published site")
    ap.add_argument("--components-json", help="local components.json (storybook-static/ of vue-components)")
    args = ap.parse_args()
    read = reader(args.from_dir)
    today = datetime.date.today().isoformat()
    OUT.mkdir(parents=True, exist_ok=True)

    llms = read("llms.txt")
    for name in LINKS:
        if name not in llms:
            print(f"warning: {name} is no longer listed in llms.txt: check the site", file=sys.stderr)
    new = sorted(set(re.findall(r"\]\(([\w.-]+\.(?:md|json))\)", llms)) - set(LINKS))
    if new:
        print(f"warning: llms.txt lists files this script doesn't mirror yet: {new}", file=sys.stderr)

    out = {
        "writing-guidelines.md": markdown_page(read("writing-guidelines.md"), "writing-guidelines", today),
        "accessibility.md": markdown_page(read("accessibility.md"), "accessibility", today),
        "introduction.md": markdown_page(read("introduction.md"), "introduction", today),
        "glossary.md": glossary(json.loads(read("glossary.json")), today),
        "icons.md": icons(json.loads(read("icons.json")), today),
        "colors.md": colors(json.loads(read("colors.json")), today),
        "foundations.md": foundations(json.loads(read("foundations.json")), today),
    }
    try:
        comp = json.loads(Path(args.components_json).read_text(encoding="utf-8") if args.components_json
                          else read("components.json", url=COMPONENTS_JSON))
        out["components-index.md"] = components_index(comp, today)
        api = OUT.parent / "components-api.md"
        m = re.search(r"\(v([\d.]+)\)", api.read_text(encoding="utf-8")) if api.exists() else None
        if m and m.group(1) != comp["version"]:
            print(f"note: components-api.md is v{m.group(1)}, the library is v{comp['version']}: "
                  "regenerate it with scripts/extract_api.py", file=sys.stderr)
    except Exception as e:  # components.json lives on another site: keep the old copy
        print(f"warning: components.json not updated ({e})", file=sys.stderr)

    for name, text in out.items():
        (OUT / name).write_text(text.rstrip() + "\n", encoding="utf-8")
        print(f"wrote references/site/{name}")


if __name__ == "__main__":
    main()
