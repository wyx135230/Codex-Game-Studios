"""Generate complete skill/role inventory for the bilingual README."""
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
lines = ['# Complete catalog / 完整目录\n', '74 migrated workflows plus the plugin-only `$studio-setup` entrypoint.\n',
         '## Workflows / 工作流\n', '| Skill | Purpose |', '| --- | --- |']
for file in sorted((ROOT / '.agents/skills').glob('*/SKILL.md')):
    front = file.read_text(encoding='utf-8').split('---', 2)[1]
    desc = re.search(r'^description:\s*(.+)$', front, re.M)[1].strip().strip('"').replace('|', '\\|')
    lines.append(f'| [${file.parent.name}](../.agents/skills/{file.parent.name}/SKILL.md) | {desc} |')
lines += ['\n## Roles / 角色\n', '| Role | Purpose |', '| --- | --- |']
for file in sorted((ROOT / '.codex/agents').glob('*.toml')):
    role = tomllib.loads(file.read_text(encoding='utf-8'))
    desc = role['description'].replace('|', '\\|')
    lines.append(f'| [{role["name"]}](../.codex/agents/{file.name}) | {desc} |')
lines += ['\n## Helpers / 辅助工具\n',
          'Run shell helpers with `python scripts/studio.py run <basename> [arguments]` or directly with Bash.\n']
lines += ['- `' + f.name + '`' for f in sorted((ROOT / '.codex/scripts').iterdir()) if f.is_file()]
(ROOT / 'docs/CATALOG.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('Catalog written')
