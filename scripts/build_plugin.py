"""Build a self-contained Codex desktop/CLI plugin, local marketplace and ZIP."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = 'codex-game-studios'
VERSION = '0.1.3'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def build():
    package = ROOT / 'plugins' / NAME
    # Only delete our generated build directory after checking its absolute boundary and marker.
    if package.exists():
        if package.is_symlink() or package.resolve() != (ROOT / 'plugins' / NAME).absolute() or not (package / '.studio-generated').is_file():
            raise ValueError('refusing to replace an unowned build directory')
        shutil.rmtree(package)
    package.mkdir(parents=True)
    write(package / '.studio-generated', NAME + '\n')
    interface = {'displayName': 'Codex Game Studios', 'shortDescription': 'Complete game studio workflows',
                 'longDescription': '74 game development workflows, 49 specialist roles, engine tooling and lifecycle checks for local Codex projects.',
                 'category': 'Productivity', 'capabilities': [], 'defaultPrompt': 'Set up this game project with Codex Game Studios.'}
    interface.update({'logo': './assets/icon.svg', 'composerIcon': './assets/icon.svg',
                      'developerName': 'Codex Game Studios contributors'})
    write(package / 'assets/icon.svg', '''<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
<rect width="128" height="128" rx="28" fill="#142b35"/>
<path d="M37 41h54c12 0 18 11 21 30l3 16c2 12-10 17-17 8L86 82H42L30 95c-7 9-19 4-17-8l3-16c3-19 9-30 21-30Z" fill="#63e6be"/>
<path d="M34 55v22m-11-11h22" stroke="#142b35" stroke-width="7" stroke-linecap="round"/>
<circle cx="89" cy="58" r="5" fill="#142b35"/><circle cx="101" cy="70" r="5" fill="#142b35"/>
<path d="m58 54-8 12 8 12m12-24 8 12-8 12" fill="none" stroke="#142b35" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>\n''')
    settings = {'interface': interface, 'hooks': './hooks/hooks.json',
                'onboardingSkill': './skills/studio-setup/SKILL.md'}
    manifest = {'$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
                'name': NAME, 'version': VERSION, 'description': interface['longDescription'],
                'license': 'MIT', 'extensions': {'com.openai': settings}}
    write(package / 'plugin.json', json.dumps(manifest, indent=2) + '\n')
    legacy = {'name': NAME, 'version': VERSION, 'description': interface['longDescription'],
              'skills': './skills/', 'interface': interface, 'hooks': './hooks/hooks.json',
              'extensions': {'com.openai': {'onboardingSkill': './skills/studio-setup/SKILL.md'}}}
    write(package / '.codex-plugin/plugin.json', json.dumps(legacy, indent=2) + '\n')
    for folder in ('.agents/skills', '.codex', '.github', 'design', 'docs', 'production', 'src', 'studio-tests'):
        shutil.copytree(ROOT / folder, package / 'template' / folder,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'session-logs', 'active.md', 'plugin-verification.json', 'distribution-verification.json'))
    (package / 'template/tests').mkdir(parents=True)
    shutil.copyfile(ROOT / 'tests/test_runtime.py', package / 'template/tests/test_runtime.py')
    for name in ('AGENTS.md', 'project.yaml', 'LICENSE', '.gitignore', '.gitattributes', '.worktreeinclude', 'README.md', 'README.en.md', 'CONTRIBUTING.md', 'SECURITY.md'):
        if (ROOT / name).exists():
            shutil.copyfile(ROOT / name, package / 'template' / name)
    (package / 'template/scripts').mkdir(parents=True, exist_ok=True)
    for name in ('studio.py', 'probe_codex.py', 'verify.py'):
        shutil.copyfile(ROOT / 'scripts' / name, package / 'template/scripts' / name)
    (package / 'scripts').mkdir(parents=True, exist_ok=True)
    for name in ('plugin_workspace.py', 'plugin_hook.py'):
        shutil.copyfile(ROOT / 'scripts' / name, package / 'scripts' / name)
    for file in sorted((ROOT / '.agents/skills').glob('*/SKILL.md')):
        text = file.read_text(encoding='utf-8')
        front = text.split('---', 2)[1]
        body = f'''# {file.parent.name} — plugin entrypoint

The complete workflow and references are bundled in `template/.agents/skills/{file.parent.name}/`.
Locate this plugin root from the loaded SKILL.md path (two parent directories above `skills/`).
Use that absolute path in commands; do not assume the shell expands a PLUGIN_ROOT variable.
First choose the current game workspace from the user's task. If no workspace is available,
ask for its path. Run `python "<plugin-root>/scripts/plugin_workspace.py" init --root "<workspace>"`.
This fills missing template files and preserves existing ones. Inspect any preserved conflicts.
If the result says `initialized: true`, run `python scripts/studio.py hook SessionStart` from
the workspace once, since the native start event preceded initialization.
Read `<workspace>/STUDIO.md`, `<workspace>/.codex/docs/runtime.md`, applicable AGENTS.md and rules.
Then read `<workspace>/.agents/skills/{file.parent.name}/SKILL.md` and follow ALL phases and referenced
files with the user's original arguments, from the workspace root. Do not invoke this wrapper recursively.
Hooks come from the plugin. On clients without hooks, use explicit lifecycle commands.
Roles are in workspace `.codex/agents/*.toml` (legacy registered role configs are also bundled).
If a named role is unavailable, give its full `.md` role contract to a generic child agent;
if no child tools exist, execute sequentially and disclose that limitation.
'''
        write(package / 'skills' / file.parent.name / 'SKILL.md', '---' + front + '---\n\n' + body)
        metadata = file.parent / 'agents/openai.yaml'
        if metadata.exists():
            target = package / 'skills' / file.parent.name / 'agents/openai.yaml'
            write(target, metadata.read_text(encoding='utf-8'))
    write(package / 'skills/studio-setup/SKILL.md', '''---
name: studio-setup
description: Initialize a writable game workspace using the complete Codex Game Studios plugin template.
---

Locate this plugin root from this skill file. Use the workspace already selected in Codex;
ask for a directory only if none is known. Run `python "<plugin-root>/scripts/plugin_workspace.py"
init --root "<workspace>"`. Read the result and preserved-file list, then read workspace
STUDIO.md, AGENTS.md and .codex/docs/runtime.md. Run `python scripts/studio.py doctor` from
the workspace. If newly initialized, run `python scripts/studio.py hook SessionStart` once.
Read and follow .agents/skills/start/SKILL.md for onboarding. All 74 original
workflows are available; consult docs/CATALOG.md. No network service or API key is required
by this plugin beyond the normal Codex sign-in. Existing project files are preserved.
''')
    events = ('SessionStart', 'PreToolUse', 'PostToolUse', 'PermissionRequest', 'PreCompact', 'Stop', 'SubagentStart', 'SubagentStop')
    hooks = {'hooks': {ev: [{'matcher': '', 'hooks': [{'type': 'command',
          'command': f'python3 "${{PLUGIN_ROOT}}/scripts/plugin_hook.py" {ev}',
          'commandWindows': 'python -c "import os,runpy,sys; sys.argv=[\'plugin_hook.py\',\'' + ev + '\']; runpy.run_path(os.path.join(os.environ[\'PLUGIN_ROOT\'],\'scripts\',\'plugin_hook.py\'),run_name=\'__main__\')"', 'timeout': 120}]}] for ev in events}}
    write(package / 'hooks/hooks.json', json.dumps(hooks, indent=2) + '\n')
    shutil.copyfile(ROOT / 'LICENSE', package / 'LICENSE')
    shutil.copytree(ROOT / 'docs', package / 'docs', ignore=shutil.ignore_patterns('plugin-verification.json', 'distribution-verification.json'))
    catalog = package / 'docs/CATALOG.md'
    write(catalog, catalog.read_text(encoding='utf-8').replace('../.agents/', '../template/.agents/').replace('../.codex/', '../template/.codex/'))
    for name in ('README.md', 'README.en.md'):
        if (ROOT / name).exists():
            shutil.copyfile(ROOT / name, package / name)
    marketplace = {'name': 'codex-game-studios-local', 'interface': {'displayName': 'Codex Game Studios'},
                   'plugins': [{'name': NAME, 'source': {'source': 'local', 'path': './plugins/' + NAME},
                                'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, 'category': 'Productivity'}]}
    write(ROOT / '.agents/plugins/marketplace.json', json.dumps(marketplace, indent=2) + '\n')
    archive = ROOT / 'dist' / f'{NAME}-{VERSION}.zip'
    archive.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in sorted(package.rglob('*')):
            if file.is_file():
                if file.name != '.studio-generated':
                    z.write(file, file.relative_to(package).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert 'plugin.json' in z.namelist()
        assert len([p for p in z.namelist() if p.startswith('skills/') and p.endswith('/SKILL.md')]) == 75
        assert 'template/.codex/agents/creative-director.toml' in z.namelist()
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    write(archive.with_suffix('.zip.sha256'), digest + '  ' + archive.name + '\n')
    # A separate market root contains no project-level hooks or instructions. Adding it
    # advertises the plugin without activating the studio template in the catalog itself.
    market_root = ROOT / 'dist/codex-game-studios-marketplace'
    if market_root.exists():
        if market_root.is_symlink() or market_root.resolve() != (ROOT / 'dist/codex-game-studios-marketplace').absolute() or not (market_root / '.studio-marketplace-generated').is_file():
            raise ValueError('refusing to replace an unowned marketplace build directory')
        shutil.rmtree(market_root)
    market_root.mkdir()
    write(market_root / '.studio-marketplace-generated', NAME + '\n')
    write(market_root / '.agents/plugins/marketplace.json', json.dumps(marketplace, indent=2) + '\n')
    shutil.copytree(package, market_root / 'plugins' / NAME, ignore=shutil.ignore_patterns('.studio-generated'))
    write(market_root / 'README.md', '''# Codex Game Studios marketplace

中文：在 Codex 的“添加 → 添加插件市场”对话框中填写：

| 字段 | 本地市场 |
| --- | --- |
| 来源 | 本目录的绝对路径；目录内直接包含 `.agents/plugins/marketplace.json` |
| Git 引用 | 留空 |
| 稀疏路径 | 留空 |

然后点击“添加市场”，在市场中安装 Codex Game Studios。不要把 ZIP 路径或 JSON 文件路径填入来源。
如果把本目录内容发布为自己的 Git 仓库，来源填写实际 owner/repo 或 Git URL；Git 引用可留空使用
默认分支，也可固定实际分支/标签/提交。稀疏路径可留空；若使用，必须同时包括 `.agents/plugins`
和 `plugins/codex-game-studios`，每行一项。不要照抄界面里的 `plugins/codex` 占位示例。
单插件 ZIP 才用于“上传插件压缩包”；不要上传市场 ZIP。

English: In Add → Add plugin marketplace, paste this directory's absolute path into Source.
Leave Git ref and Sparse paths empty for local sources. For a published Git source, enter its
actual owner/repo or URL; ref is optional. Sparse checkout is optional but must include both
`.agents/plugins` and `plugins/codex-game-studios`. Upload the separate single-plugin ZIP for
Upload plugin archive, not this marketplace ZIP.

CLI: `codex plugin marketplace add <absolute-path-to-this-directory>`, then `/plugins`.
After installation run `$studio-setup` in a game workspace. Uninstall through the plugin page.
''')
    market_archive = ROOT / 'dist' / f'{NAME}-marketplace-{VERSION}.zip'
    with zipfile.ZipFile(market_archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in sorted(market_root.rglob('*')):
            if file.is_file() and file.name != '.studio-marketplace-generated':
                z.write(file, file.relative_to(market_root).as_posix())
    market_digest = hashlib.sha256(market_archive.read_bytes()).hexdigest()
    write(market_archive.with_suffix('.zip.sha256'), market_digest + '  ' + market_archive.name + '\n')
    print(json.dumps({'archive': str(archive), 'sha256': digest, 'skills': 75,
                      'marketplace_directory': str(market_root), 'marketplace_archive': str(market_archive),
                      'template_roles': 49, 'size_bytes': archive.stat().st_size}, indent=2))


if __name__ == '__main__':
    build()
