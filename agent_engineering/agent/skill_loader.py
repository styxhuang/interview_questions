from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Skill:
    name: str
    version: str
    allowed_tools: tuple[str, ...]
    content: str


def _parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text
    _, frontmatter, body = text.split("---", 2)
    metadata: dict[str, object] = {}
    current_list: list[str] | None = None
    for raw_line in frontmatter.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("- ") and current_list is not None:
            current_list.append(line[2:].strip())
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            metadata[key] = value
            current_list = None
        else:
            current_list = []
            metadata[key] = current_list
    return metadata, body.strip()


class SkillLoader:
    def __init__(self, skills_dir: Path):
        self.skills_dir = Path(skills_dir)

    def load_all(self) -> list[Skill]:
        skills: list[Skill] = []
        for path in sorted(self.skills_dir.glob("*/SKILL.md")):
            metadata, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
            skills.append(
                Skill(
                    name=str(metadata.get("name", path.parent.name)),
                    version=str(metadata.get("version", "0")),
                    allowed_tools=tuple(metadata.get("allowed_tools", [])),
                    content=body,
                )
            )
        return skills

