from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


class RepositoryTests(unittest.TestCase):
    def test_all_nine_skills_have_matching_names(self):
        skills = sorted((ROOT / "skills").glob("motion-film*/SKILL.md"))
        self.assertEqual(len(skills), 9)
        for skill in skills:
            self.assertIn(f"\nname: {skill.parent.name}\n", skill.read_text())

    def test_local_markdown_links_resolve(self):
        files = [ROOT / "README.md", *sorted((ROOT / "skills").rglob("*.md"))]
        for file in files:
            for link in re.findall(r"\]\(([^)]+)\)", file.read_text()):
                target = link.split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                with self.subTest(file=file.relative_to(ROOT), link=link):
                    self.assertTrue((file.parent / target).exists())

    def test_diagrams_are_valid_svg(self):
        for file in (ROOT / "assets").glob("*.svg"):
            self.assertEqual(ET.parse(file).getroot().tag, "{http://www.w3.org/2000/svg}svg")

    def test_required_dependency_not_in_optional_table(self):
        entry = (ROOT / "skills/motion-film/SKILL.md").read_text()
        optional = entry.split("## Companion skills", 1)[1].split("## Lessons", 1)[0]
        self.assertNotRegex(optional, r"\|[^\n]*ffmpeg-skill[^\n]*\|")
        self.assertIn("not an optional companion", entry)


if __name__ == "__main__":
    unittest.main()
