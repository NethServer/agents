import re
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPOSITORY = SKILL_DIR.parents[1]


class SkillContractTests(unittest.TestCase):
    def test_router_metadata_and_forbidden_artifacts(self):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        self.assertIn("name: nethvoice-admin", frontmatter)
        self.assertIn("version: 0.1.2", frontmatter)
        self.assertIn("author: NethServer project contributors", frontmatter)
        self.assertIn("license: GPLv3", frontmatter)
        self.assertNotRegex(frontmatter, r"(?m)^model:")
        self.assertFalse((SKILL_DIR / "agents" / "openai.yaml").exists())
        self.assertFalse((SKILL_DIR / "README.md").exists())
        self.assertFalse(any(SKILL_DIR.glob("**/*icon*")))

    def test_every_relative_instruction_reference_exists(self):
        references = set()
        instruction_files = [SKILL_DIR / "SKILL.md", *sorted((SKILL_DIR / "references").glob("*.md"))]
        for instruction_file in instruction_files:
            text = instruction_file.read_text(encoding="utf-8")
            paths = set(
                re.findall(
                    r"`((?:(?:\.\./)+)?(?:references/|scripts/)?[A-Za-z0-9._/-]+\.(?:md|py))`",
                    text,
                )
            )
            for relative in paths:
                references.add((instruction_file, relative))
                self.assertTrue((instruction_file.parent / relative).is_file(), f"{instruction_file}: {relative}")
        self.assertTrue(references)

    def test_parent_skill_handoff_and_readme_listing(self):
        parent = (REPOSITORY / "skills" / "nethserver-admin" / "SKILL.md").read_text(encoding="utf-8")
        quick_entry = (
            REPOSITORY / "skills" / "nethserver-admin" / "references" / "nethvoice.md"
        ).read_text(encoding="utf-8")
        readme = (REPOSITORY / "README.md").read_text(encoding="utf-8")
        self.assertIn("version: 1.3.0", parent)
        self.assertIn("Activate `nethvoice-admin`", quick_entry)
        self.assertIn("/nethvoice-admin", readme)
        self.assertIn("Administration and Development", readme)
        external_collector = (
            REPOSITORY
            / "skills"
            / "nethserver-admin"
            / "references"
            / "../../nethvoice-admin/scripts/collect_diagnostics.py"
        )
        self.assertTrue(external_collector.is_file())

    def test_quick_entry_does_not_restore_unsafe_raw_diagnostics(self):
        text = (
            REPOSITORY / "skills" / "nethserver-admin" / "references" / "nethvoice.md"
        ).read_text(encoding="utf-8")
        forbidden = (
            "pjsip show contacts",
            "database show",
            "queue show",
            "openssl s_client",
            "/var/log/asterisk",
            "mysql -u",
            "psql -u",
        )
        for value in forbidden:
            self.assertNotIn(value, text)

    def test_quick_entry_inventory_filter_avoids_jq_keyword_shorthand(self):
        text = (
            REPOSITORY / "skills" / "nethserver-admin" / "references" / "nethvoice.md"
        ).read_text(encoding="utf-8")
        self.assertIn("module: .module", text)
        self.assertNotIn("{id, module,", text)

    def test_rtpengine_diagnostics_are_single_session_and_read_only(self):
        text = (SKILL_DIR / "references" / "diagnostics.md").read_text(encoding="utf-8")
        self.assertIn("rtpengine-ctl --help", text)
        self.assertIn("rtpengine-ctl list sessions <call-id>", text)
        self.assertIn("Keep the lookup scoped to one Call-ID", text)
        self.assertIn("Do not replace it with an aggregate selector", text)
        self.assertIn("or use `terminate`, configuration, debug, or other mutating control verbs", text)


if __name__ == "__main__":
    unittest.main()
