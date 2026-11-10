#!/usr/bin/env bash
# Mechanical checks of a frontend against the Nebula Design System, for
# references/review.md. Every match is a candidate, not a certain problem:
# read it before reporting it.
#
# Usage: review-checks.sh [--text-only] [--en FILE] [PATH...]
#
# Run it from the frontend folder, the one with package.json. PATH is the
# files or folders in scope (default: src). The script finds the English i18n
# file and the kind of project from package.json; --en and --text-only
# override them. It needs bash, grep, awk, perl, jq and curl.

set -uo pipefail

SITE=https://nethesis.github.io
text_only=false
en=
scope=()
while [ $# -gt 0 ]; do
  case $1 in
    --text-only) text_only=true ;;
    --en) en=$2; shift ;;
    -h | --help) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) scope+=("$1") ;;
  esac
  shift
done
[ ${#scope[@]} -gt 0 ] || scope=(src)

section() { printf '\n## %s\n' "$1"; }
# print the input, or "none" when it is empty
report() { local out; out=$(cat); if [ -n "$out" ]; then printf '%s\n' "$out"; else echo none; fi; }

# the kind of project, from package.json
deps=
[ -f package.json ] && deps=$(jq -r '[.name // "", (.dependencies // {} | keys[]), (.devDependencies // {} | keys[])] | join(" ")' package.json)
has() { [[ " $deps " == *" $1 "* ]]; }
library=false
has_vc=false
if [[ "$deps" == @nethesis/vue-components\ * ]]; then library=true; has_vc=true
elif has @nethesis/vue-components; then has_vc=true; fi
if has @carbon/vue || has carbon-components || has carbon-components-vue || has @nethserver/ns8-ui-lib; then
  text_only=true
fi
if has react; then
  views=(--include='*.tsx' --include='*.jsx')
  code=(--include='*.tsx' --include='*.jsx' --include='*.ts' --include='*.js')
else
  views=(--include='*.vue')
  code=(--include='*.vue' --include='*.ts' --include='*.js')
fi
if [ -z "$en" ]; then
  for f in src/i18n/en/translation.json src/i18n/en.json src/locales/en.json \
    public/i18n/en/translation.json public/locales/en/translation.json; do
    [ -f "$f" ] && { en=$f; break; }
  done
fi

echo "# Review checks"
echo "scope: ${scope[*]}"
echo "project: $( $library && echo '@nethesis/vue-components' || { $has_vc && echo 'uses @nethesis/vue-components' || echo 'no @nethesis/vue-components'; })$( $text_only && echo ', text checks only')"
echo "English i18n file: ${en:-not found}"

# ---------------------------------------------------------------- text checks

if [ -n "$en" ]; then
  section "i18n keys the code uses that the English file lacks (keys built at run time show up cut: ignore them)"
  grep -rhoE "\bt\(['\"][a-zA-Z0-9_.-]+['\"]" "${scope[@]}" "${code[@]}" |
    sed -E "s/.*\(['\"]//; s/['\"]$//" | sort -u |
    while read -r k; do
      jq -e --arg k "$k" 'getpath($k | split("."))' "$en" >/dev/null 2>&1 || echo "missing: $k"
    done | report

  section "terms the glossary lists under avoid, in the English file (a word avoided for an action can be right in another meaning)"
  glossary=$(curl -fsS "$SITE/nebula-design-system/glossary.json" 2>/dev/null)
  if [ -z "$glossary" ]; then
    echo "skipped: cannot download glossary.json"
  else
    jq -r '[.terms[].en] as $ok | [.terms[] | .en as $t | .avoid.en[]? | {avoid: ., term: $t}]
      | group_by(.avoid)[] | select(.[0].avoid as $a | $ok | index($a) | not)
      | "\(.[0].avoid)\t\(map(.term) | join("|"))"' <<<"$glossary" |
      while IFS=$'\t' read -r avoid terms; do
        grep -nwF -- "$avoid" "$en" | grep -vF -f <(tr '|' '\n' <<<"$terms") |
          sed "s/^/[$avoid → ${terms//|/ or }] /"
      done | report
  fi
else
  section "i18n checks"
  echo "skipped: no English i18n file found; pass it with --en"
fi

$text_only && exit 0

# ------------------------------------------- components, colors, icons, code

section "font weights the design system does not use"
grep -rnE 'font-(semibold|bold|extrabold|black)\b' "${scope[@]}" "${views[@]}" | report

section "hex, rgb() or arbitrary colors"
grep -rnE '#[0-9a-fA-F]{3,8}\b|rgba?\(|(bg|text|border|ring|fill|stroke)-\[#' "${scope[@]}" "${views[@]}" | report

section "styles outside Tailwind classes, and arbitrary values"
grep -rnE '\bstyle=["{]|\b[a-z-]+-\[[0-9.]+(px|rem)\]' "${scope[@]}" "${views[@]}" | report

section "text dimmed with opacity (skips disabled controls and transitions; an archived or turned-off item is text, not a disabled control)"
grep -rnE '\btext-[a-z]+-[0-9]+/[0-9]+|\bopacity-[0-9]+\b' "${scope[@]}" "${views[@]}" |
  grep -vE 'disabled|cursor-not-allowed|enter-|leave-' | report

section "click handlers on an element that is not a button or a link (the tag is the last one opened on the line or before it)"
grep -rlE '@click|v-on:click|onClick=' "${scope[@]}" "${views[@]}" | while read -r f; do
  awk -v f="$f" '/<[A-Za-z]/ { if (match($0, /<[A-Za-z][A-Za-z0-9.-]*/)) tag = substr($0, RSTART + 1, RLENGTH - 1) }
    /@click|v-on:click|onClick=/ && tag !~ /^(NeButton|NeLink|button|a|RouterLink|router-link|Button|Link)$/ {
      print f ":" FNR ": <" tag ">" }' "$f"
done | report

# Opening tags and elements are matched over several lines: an attribute value
# in quotes can contain ">", as in @click="() => open()".
section "links without an address: the keyboard skips an <a> or NeLink with no href (use a button for an action)"
grep -rlE '<(NeLink|a)\b' "${scope[@]}" "${views[@]}" | while read -r f; do
  perl -0777 -ne '
    while (/<(NeLink|a)\b((?:[^>"\x27]|"[^"]*"|\x27[^\x27]*\x27)*)>/g) {
      my ($tag, $attrs, $at) = ($1, $2, $-[0]);
      next if $attrs =~ /(?:^|\s)(?::|v-bind:)?(?:href|to)\s*=/;
      my $line = 1 + (substr($_, 0, $at) =~ tr/\n//);
      print "$ARGV:$line: <$tag> without href\n";
    }' "$f"
done | report

section "aria-label on an element that shows text: the label replaces the text, so it must contain the visible text, best at its start"
grep -rlE 'aria-label|ariaLabel' "${scope[@]}" "${views[@]}" | while read -r f; do
  perl -0777 -ne '
    while (/<(NeLink|NeButton|RouterLink|router-link|a|button|Link|Button)\b((?:[^>"\x27]|"[^"]*"|\x27[^\x27]*\x27)*)>(.*?)<\/\1>/gs) {
      my ($tag, $attrs, $inner, $at) = ($1, $2, $3, $-[0]);
      next unless $attrs =~ /(?:^|\s)(?::|v-bind:)?aria-label\s*=\s*"([^"]*)"|ariaLabel=\{?"?([^"}]*)/;
      my $label = defined $1 ? $1 : $2;
      (my $text = $inner) =~ s/<(?:[^>"\x27]|"[^"]*"|\x27[^\x27]*\x27)*>//g;
      next unless $text =~ /\S/;
      $text =~ s/\s+/ /g; $text =~ s/^ | $//g;
      # the label is the same expression as the visible text
      next if $text eq "{{ $label }}" || $text eq "{{$label}}" || $text eq "{$label}";
      my $line = 1 + (substr($_, 0, $at) =~ tr/\n//);
      print "$ARGV:$line: <$tag> shows \"" . substr($text, 0, 60) . "\"\n";
    }' "$f"
done | report

section "icons not imported one by one: whole packs, library.add(), icons named by string"
grep -rnE "import \{ (fas|far|fab|fal) \}|[lL]ibrary\.add\(|['\"]fa[srlb]['\"], *['\"][a-z0-9-]+['\"]|['\"]fa-(solid|regular|light|brands) fa-" "${scope[@]}" "${code[@]}" | report

$has_vc || exit 0

if ! $library; then
  section "raw elements that usually have a component"
  grep -rnE '<(button|input|select|textarea|table)\b' "${scope[@]}" "${views[@]}" | report
fi

section "deprecated components, from components.json"
deprecated=$(curl -fsS "$SITE/vue-components/components.json" 2>/dev/null |
  jq -r '[.components[] | select(.deprecated) | .name] | join("|")' 2>/dev/null)
if [ -z "$deprecated" ]; then
  echo "skipped: cannot download components.json, or no component is deprecated"
else
  grep -rnE "\b($deprecated)\b" "${scope[@]}" "${code[@]}" | report
fi

section "deprecated props, types and functions (search the files in scope for each name)"
if $library; then
  grep -rn -A3 @deprecated src | report
elif [ -d node_modules/@nethesis/vue-components/dist ]; then
  grep -rn -A3 @deprecated node_modules/@nethesis/vue-components/dist --include='*.d.ts' | report
else
  echo "skipped: @nethesis/vue-components is not installed"
fi
