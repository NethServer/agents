#!/usr/bin/env python3
"""Generate references/components-api.md from a checkout of nethesis/vue-components.

Usage: python extract_api.py <path-to-vue-components-repo> > references/components-api.md

It copies, for every component, the exported types, props, emits, v-model and slot
names straight from the source, so the reference never drifts from the real API.
"""
import json, re, sys
from pathlib import Path

repo = Path(sys.argv[1])
comp_dir = repo / "src" / "components"
version = json.loads((repo / "package.json").read_text())["version"]
main_ts = (repo / "src" / "main.ts").read_text()

deprecated = set(re.findall(r"@deprecated[^\n]*\n\s*\*/\s*\nexport \{ default as (\w+) \}", main_ts))
exported = re.findall(r"export \{ default as (\w+) \}", main_ts)


def balanced(text, start):
    """Return text from start up to the matching closing bracket of the first ( { or <."""
    pairs = {"(": ")", "{": "}", "<": ">"}
    i = start
    while i < len(text) and text[i] not in pairs:
        i += 1
    if i >= len(text):
        return ""
    open_c, close_c, depth = text[i], pairs[text[i]], 0
    for j in range(i, len(text)):
        if text[j] == open_c:
            depth += 1
        elif text[j] == close_c:
            depth -= 1
            if depth == 0:
                return text[start : j + 1]
    return text[start:]


out = [f"# @nethesis/vue-components API reference (v{version})", "",
       "Auto-generated from the component sources by `scripts/extract_api.py`. "
       "Props, emits, models and slots are copied verbatim. Comments are stripped.", "",
       "## Table of contents", ""]
for name in exported:
    out.append(f"- {name}{' (deprecated)' if name in deprecated else ''}")
out.append("")

for name in exported:
    src = (comp_dir / f"{name}.vue").read_text()
    script = "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", src, re.S))
    script = re.sub(r"/\*.*?\*/", "", script, flags=re.S)
    script = re.sub(r"^\s*//.*$", "", script, flags=re.M)
    template = src.split("<template>", 1)[1] if "<template>" in src else ""
    blocks = []
    for m in re.finditer(r"^(?:export )?(?:type|interface) \w+", script, re.M):
        start = m.start()
        line_end = script.find("\n", start)
        snippet = script[start:line_end]
        if "{" in snippet and "}" not in snippet or snippet.rstrip().endswith("="):
            snippet = balanced(script, start) if "{" in snippet else script[start:script.find("\n\n", start)]
        blocks.append(snippet.strip())
    for kw in ["withDefaults(", "defineProps", "defineEmits", "defineModel"]:
        for m in re.finditer(re.escape(kw), script):
            # include destructuring `const { a = 1 } = defineProps<...>()`
            seg_start = script.rfind("\n", 0, m.start()) + 1
            prefix = script[seg_start:m.start()]
            if kw == "defineProps" and "withDefaults(" in script[max(0, m.start()-40):m.start()]:
                continue
            if prefix.strip().startswith("const {"):
                seg_start = seg_start
                body = script[seg_start:m.start()] + balanced(script, m.start())
            elif "} = " in prefix or prefix.strip() == "} =":
                seg_start = script.rfind("const {", 0, m.start())
                body = script[seg_start:m.start()] + balanced(script, m.start())
            else:
                body = script[seg_start:m.start()] + balanced(script, m.start())
            # defineProps<...>() → also grab the call parens
            if body.endswith(">"):
                body += "()"
            blocks.append(body.strip())
    slots = set()
    for tag in re.findall(r"<slot\b[^>]*>", template):
        m = re.search(r'\bname="([\w-]+)"', tag)
        slots.add(m.group(1) if m else "default")
    slots = sorted(slots)
    out.append(f"## {name}{' — DEPRECATED, do not use in new code' if name in deprecated else ''}")
    out.append("")
    if blocks:
        out.append("```ts")
        out.append("\n\n".join(re.sub(r"\n\s*\n", "\n", b) for b in blocks))
        out.append("```")
    out.append(f"Slots: {', '.join(slots) if slots else 'none'}")
    out.append("")

print("\n".join(out))
