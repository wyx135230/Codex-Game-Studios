"""Reproducible, non-destructive import of the upstream studio template."""
from pathlib import Path
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def transform(text):
    text = text.replace('.claude/skills', '.agents/skills')
    text = text.replace('.claude', '.codex').replace('CLAUDE.md', 'AGENTS.md')
    text = text.replace('CLAUDE_PROJECT_DIR', 'STUDIO_PROJECT_DIR')
    text = text.replace('CLAUDE_SKILL_DIR', 'STUDIO_SKILL_DIR')
    text = text.replace('CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS', 'STUDIO_PARALLEL_AGENTS')
    text = text.replace('Claude Code Game Studios', 'Codex Game Studios')
    text = text.replace('Claude-Code-Game-Studios', 'Codex-Game-Studios')
    text = text.replace('claude-code-game-studios', 'codex-game-studios')
    text = text.replace('Claude Code', 'Codex').replace('Claude', 'Codex')
    # Repository skills moved one level deeper than the shell helpers.
    text = re.sub(r'\$\{STUDIO_SKILL_DIR\}/../../hooks/yaml-helper.sh',
                  '.codex/hooks/yaml-helper.sh', text)
    text = re.sub(r'(?m)^!`(.*)`$',
                  lambda m: 'Before proceeding, run this command from the repository root and use its output:\n\n```bash\n' + m[1] + '\n```', text)
    return text


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--overwrite-imported', action='store_true')
    args = parser.parse_args()
    source = args.source.resolve()
    if source == ROOT or not (source / '.claude/skills').is_dir():
        parser.error('source must be the original studio template, outside this repository')
    entries = []
    for src in sorted(source.rglob('*')):
        if not src.is_file() or '.git' in src.relative_to(source).parts:
            continue
        rel = src.relative_to(source).as_posix()
        if rel == '.claude/settings.json':
            # Keep its full event and permission contract as adapter input, never as Codex config.
            dest = ROOT / '.codex/compat/upstream-settings.json'
            data = json.loads(src.read_text(encoding='utf-8-sig'))
            write(dest, json.dumps(data, indent=2) + '\n')
        else:
            target = rel.replace('.claude/skills/', '.agents/skills/')
            target = target.replace('.claude/', '.codex/').replace('CLAUDE.md', 'AGENTS.md')
            if rel in ('README.md', 'CHANGELOG.md', 'UPGRADING.md'):
                target = 'docs/upstream/' + rel
            dest = ROOT / target
            if dest.exists() and not args.overwrite_imported:
                raise SystemExit(f'refusing to overwrite {dest}; use --overwrite-imported deliberately')
            raw = src.read_bytes()
            try:
                text = transform(raw.decode('utf-8-sig'))
            except UnicodeDecodeError:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
            else:
                if rel.startswith('.claude/skills/') and src.name == 'SKILL.md':
                    front, body = text.split('---', 2)[1:]
                    name = re.search(r'^name:\s*(.+)$', front, re.M)[1].strip()
                    desc = re.search(r'^description:\s*(.+)$', front, re.M)[1].strip()
                    explicit = bool(re.search(r'^disable-model-invocation:\s*true', front, re.M))
                    # Keep upstream metadata separately; do not imply Claude fields are enforced.
                    meta_path = ROOT / '.codex/compat/skill-metadata' / (name + '.yaml')
                    write(meta_path, front.strip() + '\n')
                    text = f'---\nname: {name}\ndescription: {desc}\n---\n\n' + (
                        'Read `.codex/docs/runtime.md` before executing this workflow. '
                        'Arguments are the text following the skill invocation; substitute them '
                        'where `$ARGUMENTS` appears.\n\n') + body.lstrip()
                    if explicit:
                        write(dest.parent / 'agents/openai.yaml',
                              'policy:\n  allow_implicit_invocation: false\n')
                write(dest, text)
        entries.append({'source': rel, 'target': dest.relative_to(ROOT).as_posix(),
                        'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest()})
    write(ROOT / 'docs/migration-manifest.json', json.dumps(entries, indent=2) + '\n')
    print(f'Imported {len(entries)} source files')


if __name__ == '__main__':
    main()
