"""Validate the documented portable package and local marketplace contracts offline.

Development dependency: PyYAML. The installed plugin itself uses only the Python standard library.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
import yaml
from build_plugin import ROOT, NAME, VERSION


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_plugin(archive):
    with zipfile.ZipFile(archive) as z:
        names = set(z.namelist())
        require(z.testzip() is None, 'corrupt ZIP member')
        for name in names:
            p = PurePosixPath(name)
            require(not p.is_absolute() and '..' not in p.parts and '\\' not in name,
                    'unsafe ZIP member: ' + name)
        require('plugin.json' in names, 'upload ZIP must contain one plugin manifest at root')
        require('.agents/plugins/marketplace.json' not in names,
                'marketplace catalog cannot be uploaded as a single plugin')
        obj = json.loads(z.read('plugin.json'))
        require(obj.get('$schema') == 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json', 'portable schema declaration')
        require(obj.get('name') == NAME, 'plugin identity mismatch')
        require(re.fullmatch(r'\d+\.\d+\.\d+', obj.get('version', '')), 'invalid release version')
        ext = obj['extensions']['com.openai']
        interface = ext['interface']
        require(0 < len(interface['displayName']) <= 30, 'invalid display name')
        require(0 < len(interface['shortDescription']) <= 30, 'invalid subtitle')
        require(isinstance(interface.get('capabilities'), list), 'capabilities must be an array')
        require(isinstance(interface.get('developerName'), str) and interface['developerName'].strip(), 'publisher display name required')
        def resolve(value):
            require(isinstance(value, str) and value.startswith('./'), 'component path must start ./')
            p = PurePosixPath(value[2:])
            require('..' not in p.parts and not p.is_absolute() and str(p) in names, 'missing/unsafe component: ' + value)
            return str(p)
        for key in ('composerIcon', 'logo'):
            file = resolve(interface[key])
            require(len(z.read(file)) <= 5 * 1024 * 1024, 'icon exceeds limit')
            svg = ET.fromstring(z.read(file))
            view = [float(v) for v in svg.attrib['viewBox'].split()]
            require(view[2] == view[3] and view[2] >= 48, 'icon must be square and >=48px')
        setup = resolve(ext['onboardingSkill'])
        hooks = json.loads(z.read(resolve(ext['hooks'])))
        require(isinstance(hooks['hooks'], dict), 'invalid hook config')
        overlay = json.loads(z.read('.codex-plugin/plugin.json'))
        require(overlay['name'] == obj['name'] and overlay['version'] == obj['version'], 'compatibility identity mismatch')
        require(overlay['interface'] == interface, 'compatibility presentation mismatch')
        skills = sorted(n for n in names if len(PurePosixPath(n).parts) == 3 and n.startswith('skills/') and n.endswith('/SKILL.md'))
        require(len(skills) == 75 and setup in skills, 'expected 74 workflows plus setup skill')
        seen = set()
        for name in skills:
            raw = z.read(name)
            require(len(raw) <= 1024 * 1024, 'oversized skill')
            text = raw.decode('utf-8')
            require(text.startswith('---\n'), 'skill must begin with YAML frontmatter')
            front = yaml.safe_load(text.split('---', 2)[1])
            for field in ('name', 'description'):
                require(isinstance(front.get(field), str) and front[field].strip(), 'invalid skill ' + field)
            require(front['name'] == PurePosixPath(name).parts[1], 'skill name mismatch')
            require(front['name'] not in seen, 'duplicate skill name')
            seen.add(front['name'])
            metadata = str(PurePosixPath(name).parent / 'agents/openai.yaml')
            if metadata in names:
                meta = yaml.safe_load(z.read(metadata))
                require(isinstance(meta, dict), 'invalid skill metadata')
                implicit = meta.get('policy', {}).get('allow_implicit_invocation', True)
                require(isinstance(implicit, bool), 'invocation policy must be boolean')
        require(not ({'install.ps1', 'uninstall.ps1', 'scripts/plugin_manager.py'} & names),
                'native distribution should not require a custom installer')
        manifest = json.loads(z.read('framework/docs/migration-manifest.json'))
        resource_map = json.loads(z.read('framework/resource-map.json'))
        require(all(resource_map.get(row['target']) in names for row in manifest), 'missing migrated functionality')
        require(not any(n.startswith(('template/', 'framework/.agents/skills/')) for n in names), 'duplicated skill library')
        require(all('plugin entrypoint' not in z.read(n).decode('utf-8') for n in skills), 'expected full installed workflows')
        return {'version': obj['version'], 'skills': len(skills), 'source_files': len(manifest), 'members': len(names)}


def validate_marketplace(directory, plugin_archive):
    directory = Path(directory).resolve()
    require(not (directory / '.codex/hooks.json').exists(), 'catalog must not activate project hooks')
    obj = json.loads((directory / '.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
    require(isinstance(obj['plugins'], list) and len(obj['plugins']) == 1, 'expected single-plugin marketplace')
    entry = obj['plugins'][0]
    require(entry['name'] == NAME and entry['source']['source'] == 'local', 'invalid local source')
    path = entry['source']['path']
    require(path.startswith('./'), 'market source must be root-relative')
    target = (directory / path).resolve()
    require(target.is_relative_to(directory) and target.is_dir(), 'market source escapes or is absent')
    with zipfile.ZipFile(plugin_archive) as z:
        for name in z.namelist():
            if not name.endswith('/'):
                require((target / name).read_bytes() == z.read(name), 'market differs from upload ZIP: ' + name)
    return {'marketplace': obj['name'], 'source': path}


def main():
    archive = ROOT / 'dist' / f'{NAME}-{VERSION}.zip'
    marketplace = ROOT / 'dist/codex-game-studios-marketplace'
    report = {'plugin': validate_plugin(archive), 'marketplace': validate_marketplace(marketplace, archive)}
    for file in (archive, ROOT / 'dist' / f'{NAME}-marketplace-{VERSION}.zip'):
        require(hashlib.sha256(file.read_bytes()).hexdigest() == file.with_suffix('.zip.sha256').read_text().split()[0], 'hash mismatch')
    with zipfile.ZipFile(ROOT / 'dist' / f'{NAME}-marketplace-{VERSION}.zip') as z:
        require(z.testzip() is None and '.agents/plugins/marketplace.json' in z.namelist(), 'invalid marketplace ZIP')
        require('plugin.json' not in z.namelist(), 'catalog ZIP must remain distinct from upload ZIP')
    report['passed'] = True
    report['limitations'] = ['Documented structural checks, not an OpenAI backend validation result.',
                             'Desktop archive-upload UI was not automated.']
    (ROOT / 'docs/distribution-verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
