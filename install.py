#!/usr/bin/env python3
"""Transactional Codex adapter. Never run the native installer against a test user's home."""
import argparse
import base64
import contextlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import urllib.request

if sys.version_info < (3, 11):
    raise SystemExit('concise requires Python 3.11+; no Codex configuration was changed.')
import tomllib

BEGIN = '<!-- concise:START -->'
END = '<!-- concise:END -->'
RAW = 'https://raw.githubusercontent.com/Cpp1022/concise/main/'
FILES = ('instructions.md', 'hooks.json', 'config.toml', 'hooks/concise-user-prompt-submit.sh', 'hooks/concise-user-prompt-submit.ps1')
STATE = '.concise-install/state.json'
PENDING = '.concise-install/pending.json'


def fail(message):
    raise RuntimeError(message)


def encode(data):
    return None if data is None else base64.b64encode(data).decode('ascii')


def decode(data):
    return None if data is None else base64.b64decode(data, validate=True)


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def target(root, name):
    if name not in (*FILES, STATE, PENDING):
        fail('Invalid managed path in installation record.')
    path = root / name
    for item in (root, *path.relative_to(root).parents):
        check = item if item == root else root / item
        if check.is_symlink():
            fail(f'Refusing symbolic link: {check}')
    if path.is_symlink() or (path.exists() and not path.is_file()):
        fail(f'Refusing non-regular file: {path}')
    return path


def read(root, name):
    path = target(root, name)
    return path.read_bytes() if path.exists() else None


def atomic(root, name, value):
    path = target(root, name)
    if value is None:
        if path.exists():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        if path.exists():
            os.chmod(temporary, path.stat().st_mode & 0o777)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        if name.endswith('concise-user-prompt-submit.sh'):
            os.chmod(temporary, 0o700)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def text(data):
    return (data or b'').decode('utf-8-sig')


def load_json(data, label):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                fail(f'{label}: duplicate JSON key {key!r}; refusing to rewrite.')
            result[key] = value
        return result
    result = json.loads(text(data), object_pairs_hook=unique)
    if not isinstance(result, dict):
        fail(f'{label}: expected a JSON object.')
    return result


def hooks(data):
    result = {} if data is None else load_json(data, 'hooks.json')
    entries = result.get('hooks', {})
    if not isinstance(entries, dict):
        fail('hooks.json: unsupported hooks shape.')
    for groups in entries.values():
        if not isinstance(groups, list):
            fail('hooks.json: unsupported event shape.')
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get('hooks'), list):
                fail('hooks.json: unsupported matcher shape.')
            if any(not isinstance(handler, dict) for handler in group['hooks']):
                fail('hooks.json: unsupported handler shape.')
    return result


def managed_handler(handler):
    # Only our generated hook type and exact command are owned.
    return handler.get('type') == 'command' and handler.get('command') in COMMANDS


def remove_hooks(value, expected):
    found = []
    for event, groups in list(value.get('hooks', {}).items()):
        kept_groups = []
        for group in groups:
            old = group['hooks']
            selected = [h for h in old if h.get('command') == expected['command'] or managed_handler(h)]
            for handler in selected:
                if event != 'UserPromptSubmit' or handler != expected:
                    fail('The concise hook entry was modified; refusing to remove it.')
            found.extend(selected)
            remaining = [h for h in old if h not in selected]
            if remaining or not selected:
                group['hooks'] = remaining
                kept_groups.append(group)
        if kept_groups:
            value['hooks'][event] = kept_groups
        else:
            del value['hooks'][event]
    if len(found) != 1:
        fail('The recorded concise hook entry is missing or duplicated; review hooks.json first.')
    return value


def other_hooks(value):
    return any(group.get('hooks') for groups in value.get('hooks', {}).values() for group in groups)


def config(data):
    value = tomllib.loads(text(data))
    features = value.get('features', {})
    if not isinstance(features, dict):
        fail('config.toml: features must be a table.')
    flag = features.get('codex_hooks')
    if flag is not None and not isinstance(flag, bool):
        fail('config.toml: codex_hooks must be a boolean.')
    return value, flag


def config_edit(data, desired):
    """Parse the complete TOML; edit only a verified standalone features key.

    Dotted and inline representations are refused rather than guessed at. Quoted
    table/key spelling, comments, UTF-8 BOM and CRLF are retained.
    """
    old = text(data)
    parsed, previous = config(data)
    if previous == desired:
        return data
    lines = old.splitlines(keepends=True)
    newline = '\r\n' if '\r\n' in old else '\n'
    table = re.compile(r'''^\s*\[\s*(?:features|"features"|'features')\s*\]\s*(?:#.*)?$''')
    key = re.compile(r'''^(\s*(?:codex_hooks|"codex_hooks"|'codex_hooks')\s*=\s*)(true|false)(\s*(?:#.*)?)(\r?\n)?$''')
    start = None
    end = len(lines)
    matches = []
    in_table = False
    # Refuse multiline strings before line-based edits: their contents can mimic
    # headers. This conservative limit is explicit; the source is never rewritten.
    if '\"\"\"' in old or "'''" in old:
        fail('config.toml contains multiline strings; automatic editing is unsupported. Configuration was not changed.')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('['):
            if in_table:
                end = i
                in_table = False
            if table.fullmatch(line.rstrip('\r\n')):
                if start is not None:
                    fail('Ambiguous features table.')
                start = i
                end = len(lines)
                in_table = True
        if in_table and key.fullmatch(line):
            matches.append(i)
    if previous is not None and len(matches) != 1:
        fail('config.toml uses a dotted or inline codex_hooks setting; automatic editing is unsupported. Configuration was not changed.')
    if len(matches) > 1:
        fail('Ambiguous codex_hooks setting.')
    if matches:
        index = matches[0]
        match = key.fullmatch(lines[index])
        lines[index] = '' if desired is None else match[1] + str(desired).lower() + match[3] + (match[4] or '')
    elif desired is not None:
        if start is not None:
            if end and not lines[end - 1].endswith(('\n', '\r')):
                lines[end - 1] += newline
            lines.insert(end, 'codex_hooks = ' + str(desired).lower() + newline)
        else:
            if 'features' in parsed:
                fail('config.toml uses an inline/dotted features table; automatic editing is unsupported.')
            if lines and not lines[-1].endswith(('\n', '\r')):
                lines[-1] += newline
            lines.extend([newline if lines else '', '[features]' + newline, 'codex_hooks = ' + str(desired).lower() + newline])
    result = ''.join(lines).encode('utf-8')
    if data and data.startswith(b'\xef\xbb\xbf'):
        result = b'\xef\xbb\xbf' + result
    actual, flag = config(result)
    expected = dict(parsed)
    expected['features'] = dict(parsed.get('features', {}))
    if desired is None:
        expected['features'].pop('codex_hooks', None)
    else:
        expected['features']['codex_hooks'] = desired
    if actual != expected or flag != desired:
        fail('TOML edit verification failed; configuration was not changed.')
    return result


def replace_block(data, expected, replacement):
    raw = data or b''
    begin, end = BEGIN.encode(), END.encode()
    if raw.count(begin) != 1 or raw.count(end) != 1:
        fail('Concise instruction markers are missing or duplicated; refusing to guess.')
    start = raw.index(begin)
    stop = raw.index(end) + len(end)
    if stop <= start or raw[start:stop] != expected:
        fail('Concise instruction block was modified; refusing to overwrite it.')
    return raw[:start] + replacement + raw[stop:]


def validate_state(data):
    state = load_json(data, 'concise installation record')
    if state.get('version') != 1 or state.get('status') not in ('installed', 'retained-config'):
        fail('Unsupported installation record.')
    for name, entry in state.get('files', {}).items():
        if name not in FILES or not isinstance(entry, dict):
            fail('Invalid installation record path.')
        decode(entry['before'])
        decode(entry['after'])
    return state


def recover(root):
    raw = read(root, PENDING)
    if raw is None:
        return
    pending = load_json(raw, 'pending transaction')
    if pending.get('version') != 1 or not isinstance(pending.get('changes'), list):
        fail('Invalid pending transaction; retained for manual recovery.')
    for entry in pending['changes']:
        name = entry['name']
        before, after = decode(entry['before']), decode(entry['after'])
        current = read(root, name)
        if current not in (before, after):
            fail(f'Interrupted transaction conflicts with newer edits to {name}; recovery data was retained.')
    for entry in reversed(pending['changes']):
        atomic(root, entry['name'], decode(entry['before']))
    atomic(root, PENDING, None)
    print('Recovered the interrupted concise transaction.')


def transaction(root, desired, fault=None):
    changes = [{'name': name, 'before': encode(read(root, name)), 'after': encode(value)}
               for name, value in desired.items() if read(root, name) != value]
    if not changes:
        return
    # Before any user configuration is touched, persist and verify a full byte
    # snapshot. It is also the durable recovery record after a killed process.
    atomic(root, PENDING, json_bytes({'version': 1, 'changes': changes}))
    persisted = load_json(read(root, PENDING), 'pending transaction')
    if persisted['changes'] != changes:
        fail('Backup verification failed.')
    try:
        for index, entry in enumerate(changes, 1):
            if read(root, entry['name']) != decode(entry['before']):
                fail(f'Concurrent edit detected: {entry["name"]}')
            atomic(root, entry['name'], decode(entry['after']))
            if fault:
                fault(index)
        atomic(root, PENDING, None)
    except BaseException:
        recover(root)
        raise


SH_COMMAND = '"$HOME/.codex/hooks/concise-user-prompt-submit.sh"'
# Legacy command signature, used only to detect untracked old installations.
PS_COMMAND = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "& (Join-Path $env:USERPROFILE ' + "'.codex\\hooks\\concise-user-prompt-submit.ps1')\""
COMMANDS = {SH_COMMAND, PS_COMMAND}
SUMMARY = 'concise: 先结论；1-2句；禁计划/禁tool旁白/禁Why-How清单。'


def hook_payload(platform, root):
    payload = {'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': SUMMARY}}
    if platform == 'windows':
        body = '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n' + "@'\n" + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + "\n'@\n"
        location = str(root / 'hooks' / 'concise-user-prompt-submit.ps1').replace("'", "''")
        command = 'powershell -NoProfile -ExecutionPolicy Bypass -Command ' + chr(34) + '& ' + chr(39) + location + chr(39) + chr(34)
        return 'hooks/concise-user-prompt-submit.ps1', body.encode('utf-8-sig'), command
    body = "#!/usr/bin/env sh\nprintf '%s\\n' '" + json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace("'", "'\\''") + "'\n"
    import shlex
    return 'hooks/concise-user-prompt-submit.sh', body.encode('utf-8'), shlex.quote(str(root / 'hooks' / 'concise-user-prompt-submit.sh'))


def install(root, skill, platform, fault=None):
    if not skill.startswith(b'---') or b'name: concise' not in skill or b'description:' not in skill:
        fail('Downloaded SKILL.md is not a concise skill.')
    if BEGIN.encode() in skill or END.encode() in skill:
        fail('Skill contains reserved instruction markers.')
    old_state = read(root, STATE)
    state = validate_state(old_state) if old_state else None
    if state and state['status'] != 'installed':
        fail('An earlier uninstall retained configuration recovery data; review it before reinstalling.')
    current = {name: read(root, name) for name in FILES}
    parsed_hooks = hooks(current['hooks.json'])
    config(current['config.toml'])
    hook_name, hook_body, command = hook_payload(platform, root)
    handler = {'type': 'command', 'command': command}
    block = BEGIN.encode() + b'\n' + skill.rstrip(b'\r\n') + b'\n' + END.encode()
    if state:
        if state['platform'] != platform:
            fail('Uninstall the existing platform adapter before switching platform.')
        previous_block = decode(state['block'])
        instructions = replace_block(current['instructions.md'], previous_block, block)
        if current[hook_name] != decode(state['files'][hook_name]['after']):
            fail('Concise hook script was modified; refusing to overwrite it.')
        parsed_hooks = remove_hooks(parsed_hooks, state['handler'])
        if config(current['config.toml'])[1] is not True:
            fail('codex_hooks changed after installation; review it before reinstalling.')
    else:
        old = current['instructions.md'] or b''
        if BEGIN.encode() in old or END.encode() in old:
            fail('Concise markers exist without an installation record; no automatic takeover.')
        # Prior untracked installs are retained, not misclassified as user text.
        if any(current[name] is not None for name in FILES if name.startswith('hooks/')):
            fail('Untracked concise hook file exists. Back it up and review the old installation first.')
        if any(managed_handler(h) or h.get('command') == command for groups in parsed_hooks.get('hooks', {}).values() for group in groups for h in group['hooks']):
            fail('Untracked concise hook entry exists; review the old installation first.')
        if b'concise:' in old or b'name: concise' in old:
            fail('Possible legacy concise instructions detected; retain and review them before installation.')
        separator = b'' if not old or old.endswith(b'\n\n') else (b'\n' if old.endswith(b'\n') else b'\n\n')
        instructions = old + separator + block + b'\n'
    parsed_hooks.setdefault('hooks', {}).setdefault('UserPromptSubmit', []).insert(0, {'hooks': [handler]})
    desired = {'instructions.md': instructions, hook_name: hook_body,
               'hooks.json': json_bytes(parsed_hooks), 'config.toml': config_edit(current['config.toml'], True)}
    files = {} if state is None else state['files']
    restore = {} if state is None else state['restore']
    restore['instructions.md'] = (encode(current['instructions.md']) if state is None else
        restore['instructions.md'] if current['instructions.md'] == decode(files['instructions.md']['after']) else
        encode(replace_block(current['instructions.md'], decode(state['block']), b'')))
    restore['hooks.json'] = (encode(current['hooks.json']) if state is None else
        restore['hooks.json'] if current['hooks.json'] == decode(files['hooks.json']['after']) else
        encode(json_bytes(remove_hooks(hooks(current['hooks.json']), state['handler']))))
    original_flag = config(decode(files['config.toml']['before']))[1] if state else config(current['config.toml'])[1]
    restore['config.toml'] = (encode(current['config.toml']) if state is None else
        restore['config.toml'] if current['config.toml'] == decode(files['config.toml']['after']) else
        encode(config_edit(current['config.toml'], original_flag)))
    for name, after in desired.items():
        files[name] = {'before': files[name]['before'] if name in files else encode(current[name]), 'after': encode(after)}
    next_state = {'version': 1, 'status': 'installed', 'platform': platform, 'block': encode(block), 'handler': handler, 'files': files, 'restore': restore}
    desired[STATE] = json_bytes(next_state)
    transaction(root, desired, fault)
    print('Installed concise; existing instructions and unrelated configuration were preserved.')


def uninstall(root, fault=None):
    raw = read(root, STATE)
    if raw is None:
        print('No recorded concise installation. Untracked legacy files were left untouched.')
        return
    state = validate_state(raw)
    if state['status'] != 'installed':
        fail('Only retained configuration recovery data remains; review .concise-install/state.json manually.')
    desired = {}
    files = state['files']
    old = read(root, 'instructions.md')
    stripped = replace_block(old, decode(state['block']), b'')
    desired['instructions.md'] = decode(state['restore']['instructions.md']) if old == decode(files['instructions.md']['after']) else stripped
    hook_name = 'hooks/concise-user-prompt-submit.' + ('ps1' if state['platform'] == 'windows' else 'sh')
    if read(root, hook_name) != decode(files[hook_name]['after']):
        fail('Concise hook script changed; uninstall stopped without deleting user edits.')
    desired[hook_name] = decode(files[hook_name]['before'])
    old_hooks = read(root, 'hooks.json')
    cleaned = remove_hooks(hooks(old_hooks), state['handler'])
    original_hooks = hooks(decode(files['hooks.json']['before']))
    if not cleaned.get('hooks') and 'hooks' not in original_hooks:
        cleaned.pop('hooks', None)
    elif 'hooks' in cleaned:
        for event in list(cleaned['hooks']):
            if not cleaned['hooks'][event] and event not in original_hooks.get('hooks', {}):
                del cleaned['hooks'][event]
    desired['hooks.json'] = decode(state['restore']['hooks.json']) if old_hooks == decode(files['hooks.json']['after']) else json_bytes(cleaned)
    current_config = read(root, 'config.toml')
    current_flag = config(current_config)[1]
    original_config = decode(files['config.toml']['before'])
    original_flag = config(original_config)[1]
    retain = current_flag is not True or (other_hooks(cleaned) and original_flag is not True)
    if retain:
        print('Kept codex_hooks: it was edited or other hooks may depend on it. Recovery data was retained.')
        retained = {'version': 1, 'status': 'retained-config', 'files': {'config.toml': files['config.toml']}}
        desired[STATE] = json_bytes(retained)
    else:
        desired['config.toml'] = decode(state['restore']['config.toml']) if current_config == decode(files['config.toml']['after']) else config_edit(current_config, original_flag)
        desired[STATE] = None
    transaction(root, desired, fault)
    print('Uninstalled concise; unrelated user changes were preserved.')


@contextlib.contextmanager
def lock(root):
    # Kernel-backed lock is released even if the process is killed; the persistent
    # pending journal then supplies recovery at the next invocation.
    directory = root / '.concise-install'
    if root.is_symlink() or directory.is_symlink():
        fail('Refusing symbolic-link configuration directory.')
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / 'lock'
    if path.is_symlink():
        fail('Refusing symbolic-link lock file.')
    with path.open('a+b') as stream:
        stream.seek(0, 2)
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            fail('Another concise installer is running.')
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', nargs='?', choices=('codex', 'uninstall'), default='codex')
    parser.add_argument('--codex-home', type=Path, default=None)
    parser.add_argument('--skill-file', type=Path, default=None)
    args = parser.parse_args()
    root = (args.codex_home or Path(os.environ.get('CODEX_HOME') or str(Path.home() / '.codex'))).absolute()
    skill = None
    if args.action == 'codex':
        candidate = args.skill_file or Path(__file__).parent / 'skills' / 'concise' / 'SKILL.md'
        if candidate.is_file():
            skill = candidate.read_bytes()
        elif args.skill_file:
            fail('Specified skill file does not exist.')
        else:
            with urllib.request.urlopen(RAW + 'skills/concise/SKILL.md', timeout=30) as response:
                skill = response.read()
    with lock(root):
        recover(root)
        if args.action == 'uninstall':
            uninstall(root)
        else:
            install(root, skill, 'windows' if os.name == 'nt' else 'unix')


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        print(f'concise: {error}', file=sys.stderr)
        sys.exit(1)
