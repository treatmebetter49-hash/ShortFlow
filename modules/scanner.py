import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScanResult:
    projects: list[str] = field(default_factory=list)
    total_shorts: int = 0
    max_short_num: int = 0
    next_short_num: int = 1
    existing_hooks: list[str] = field(default_factory=list)

    @property
    def status_text(self) -> str:
        if self.total_shorts == 0:
            return "Keine Shorts gefunden"
        return (
            f"✓ Projekte: {len(self.projects)}   "
            f"✓ Shorts: {self.total_shorts}   "
            f"✓ Nächster Short: Short{self.next_short_num}"
        )


def scan_shorts_base(base: Path) -> ScanResult:
    """Read-only scan of base/<topic>/MM.MonthName'YY/Short<N>/ structure. base is already the Shorts root."""
    result = ScanResult()
    shorts_root = base

    if not shorts_root.is_dir():
        return result

    try:
        topic_dirs = [d for d in shorts_root.iterdir() if d.is_dir()]
    except OSError:
        return result

    for topic_dir in sorted(topic_dirs):
        topic_has_shorts = False

        try:
            month_dirs = [d for d in topic_dir.iterdir() if d.is_dir()]
        except OSError:
            continue

        for month_dir in sorted(month_dirs):
            try:
                short_dirs = [d for d in month_dir.iterdir() if d.is_dir()]
            except OSError:
                continue

            for short_dir in short_dirs:
                m = re.fullmatch(r'Short(\d+)', short_dir.name)
                if m is None:
                    continue
                num = int(m.group(1))
                result.total_shorts += 1
                topic_has_shorts = True
                if num > result.max_short_num:
                    result.max_short_num = num

        if topic_has_shorts:
            result.projects.append(topic_dir.name)

    result.next_short_num = result.max_short_num + 1

    hook_pattern = re.compile(r'class="hook-text">([^<]+)<')
    for html_file in shorts_root.rglob("*.html"):
        try:
            text = html_file.read_text(encoding="utf-8", errors="ignore")
            result.existing_hooks.extend(hook_pattern.findall(text))
        except OSError:
            continue

    return result
