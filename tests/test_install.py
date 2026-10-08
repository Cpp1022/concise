import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', BASE / 'install.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
SKILL = (BASE / 'skills/concise/SKILL.md').read_bytes()

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'config with spaces'
        self.root.mkdir()
    def tearDown(self):
        self.temp.cleanup()
    def put(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
    def snapshot(self):
        return {name: m.read(self.root, name) for name in m.FILES + (m.STATE,)}
    def install(self, platform='windows', fault=None, skill=SKILL):
        with contextlib.redirect_stdout(io.StringIO()):
            m.install(self.root, skill, platform, fault)
    def uninstall(self, fault=None):
        with contextlib.redirect_stdout(io.StringIO()):
            m.uninstall(self.root, fault)
    def populate(self):
        self.put('instructions.md', '用户原有指令\r\n保持完整'.encode('utf-8-sig'))
        self.put('hooks.json', b'{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"echo foreign"}]}]},"extra":17}')
        self.put('config.toml', b'# keep comments\r\nmodel = "test"\r\n[features] # features comment\r\ncodex_hooks = false # existing flag\r\nother = true\r\n[projects."C:/demo"]\r\ntrust_level = "trusted"\r\n')
    def test_exact_restore_and_idempotence_both_platforms(self):
        for platform in ('windows','unix'):
            with self.subTest(platform=platform):
                self.populate()
                # Foreign hooks force retaining a formerly false shared flag;
                # use an already enabled flag for exact round-trip expectation.
                self.put('config.toml', m.read(self.root,'config.toml').replace(b'false',b'true'))
                before=self.snapshot()
                self.install(platform)
                first=self.snapshot()
                self.install(platform)
                self.assertEqual(first,self.snapshot())
                self.uninstall()
                self.assertEqual(before,self.snapshot())
    def test_fresh_round_trip(self):
        for platform in ('windows','unix'):
            self.install(platform)
            self.uninstall()
            self.assertTrue(all(value is None for value in self.snapshot().values()))
    def test_existing_false_no_other_hooks(self):
        self.put('config.toml', b'model="x"\n[features]\ncodex_hooks=false # preserved\nother=true\n')
        before=self.snapshot()
        self.install()
        self.uninstall()
        self.assertEqual(before,self.snapshot())
    def test_user_edits_preserved_across_update(self):
        self.populate()
        self.put('config.toml', b'model="x"\n[features]\ncodex_hooks=true\n')
        self.install()
        self.put('instructions.md',m.read(self.root,'instructions.md')+b'\nUSER ADDED AFTER INSTALL\n')
        value=json.loads(m.read(self.root,'hooks.json'));value['new_user_setting']=42
        self.put('hooks.json',m.json_bytes(value))
        self.put('config.toml',m.read(self.root,'config.toml')+b'\n[custom]\nanswer=42\n')
        self.install(skill=SKILL+b'\nUpdated rule\n')
        self.uninstall()
        self.assertIn(b'USER ADDED AFTER INSTALL',m.read(self.root,'instructions.md'))
        self.assertEqual(42,json.loads(m.read(self.root,'hooks.json'))['new_user_setting'])
        self.assertIn(b'answer=42',m.read(self.root,'config.toml'))
        self.assertNotIn(m.BEGIN.encode(),m.read(self.root,'instructions.md'))
    def test_mixed_hook_group_preserved(self):
        self.install()
        value=json.loads(m.read(self.root,'hooks.json'))
        foreign={'type':'command','command':'echo foreign'}
        value['hooks']['UserPromptSubmit'][0]['hooks'].append(foreign)
        self.put('hooks.json',m.json_bytes(value))
        self.uninstall()
        self.assertEqual([foreign],json.loads(m.read(self.root,'hooks.json'))['hooks']['UserPromptSubmit'][0]['hooks'])
        self.assertTrue(m.config(m.read(self.root,'config.toml'))[1])
        self.assertEqual('retained-config',json.loads(m.read(self.root,m.STATE))['status'])
    def test_malformed_json_no_write(self):
        for value in (b'{broken',b'{"hooks":{},"hooks":{}}',b'{"hooks":{"UserPromptSubmit":false}}'):
            self.put('hooks.json',value);before=self.snapshot()
            with self.assertRaises(Exception):self.install()
            self.assertEqual(before,self.snapshot())
    def test_bad_toml_no_write(self):
        for value in (b'[features\ncodex_hooks=true',b'[features]\ncodex_hooks="true"',b'[features]\ncodex_hooks=false\ncodex_hooks=true'):
            self.put('config.toml',value);before=self.snapshot()
            with self.assertRaises(Exception):self.install()
            self.assertEqual(before,self.snapshot())
    def test_ambiguous_toml_refused(self):
        for value in (b'features.codex_hooks=false\n',b'features={codex_hooks=false}\n',b'x="""\n[features]\n"""\n'):
            self.put('config.toml',value);before=self.snapshot()
            with self.assertRaises(Exception):self.install()
            self.assertEqual(before,self.snapshot())
    def test_config_variants(self):
        variants=(b'',b'model="x"',b'[features]\nother=true\n[next]\nx=1\n',b'["features"] # yes\n"codex_hooks" = false # note\n',b"['features']\n'codex_hooks' = false",b'\xef\xbb\xbf[features]\r\ncodex_hooks=false\r\n')
        for original in variants:
            updated=m.config_edit(original,True)
            self.assertTrue(m.config(updated)[1])
            restored=m.config_edit(updated,m.config(original)[1])
            self.assertEqual(m.config(original)[1],m.config(restored)[1])
    def test_failure_rolls_back_every_write(self):
        self.populate();before=self.snapshot()
        for index in range(1,6):
            def fault(i):
                if i==index:raise OSError('simulated write failure')
            with self.assertRaises(OSError):self.install(fault=fault)
            self.assertEqual(before,self.snapshot())
            self.assertIsNone(m.read(self.root,m.PENDING))
    def test_update_failure_preserves_installed_version(self):
        self.install();before=self.snapshot()
        def fault(i):raise OSError('simulated update failure')
        with self.assertRaises(OSError):self.install(fault=fault,skill=SKILL+b'\nChanged\n')
        self.assertEqual(before,self.snapshot())
    def test_uninstall_failure_rolls_back(self):
        self.install();before=self.snapshot()
        for index in range(1,6):
            def fault(i):
                if i==index:raise OSError('simulated uninstall failure')
            with self.assertRaises(OSError):self.uninstall(fault=fault)
            self.assertEqual(before,self.snapshot())
    def test_backup_failure_before_changes(self):
        original=m.atomic
        def rejected(root,name,value):
            if name==m.PENDING:raise OSError('simulated backup failure')
            original(root,name,value)
        before=self.snapshot()
        m.atomic=rejected
        try:
            with self.assertRaises(OSError):self.install()
            self.assertEqual(before,self.snapshot())
        finally:m.atomic=original
    def test_modified_block_or_hook_refuses_without_changes(self):
        self.install()
        original=self.snapshot()
        for name in ('instructions.md','hooks/concise-user-prompt-submit.ps1'):
            self.put(name,m.read(self.root,name).replace(b'concise',b'edited',1))
            before=self.snapshot()
            with self.assertRaises(Exception):self.uninstall()
            self.assertEqual(before,self.snapshot())
            self.put(name,original[name])
    def test_legacy_refuses(self):
        for name,value in (('instructions.md',SKILL),('hooks/concise-user-prompt-submit.ps1',b'old hook')):
            self.put(name,value);before=self.snapshot()
            with self.assertRaises(Exception):self.install()
            self.assertEqual(before,self.snapshot())
            (self.root/name).unlink()
    def test_crash_recovery(self):
        self.populate();before=self.snapshot()
        code="import sys,os;sys.path.insert(0,sys.argv[1]);import install;from pathlib import Path;r=Path(sys.argv[2]);s=Path(sys.argv[3]).read_bytes();install.install(r,s,'windows',lambda i:os._exit(71) if i==2 else None)"
        result=subprocess.run([sys.executable,'-c',code,str(BASE),str(self.root),str(BASE/'skills/concise/SKILL.md')],capture_output=True)
        self.assertEqual(71,result.returncode,result.stderr)
        self.assertIsNotNone(m.read(self.root,m.PENDING))
        m.recover(self.root)
        self.assertEqual(before,self.snapshot())
    def test_recovery_conflict_preserves_new_edits(self):
        self.put('instructions.md',b'user newer edit')
        m.atomic(self.root,m.PENDING,m.json_bytes({'version':1,'changes':[{'name':'instructions.md','before':m.encode(b'old'),'after':m.encode(b'installed') }]}))
        with self.assertRaises(Exception):m.recover(self.root)
        self.assertEqual(b'user newer edit',m.read(self.root,'instructions.md'))
        self.assertIsNotNone(m.read(self.root,m.PENDING))
    def test_hook_payload_parses(self):
        platform = 'windows' if os.name == 'nt' else 'unix'
        self.install(platform)
        command = ['powershell','-NoProfile','-File',str(self.root/'hooks/concise-user-prompt-submit.ps1')] if os.name == 'nt' else ['sh',str(self.root/'hooks/concise-user-prompt-submit.sh')]
        result=subprocess.run(command,capture_output=True)
        self.assertEqual(0,result.returncode,result.stderr)
        self.assertEqual('UserPromptSubmit',json.loads(result.stdout.decode('utf-8-sig'))['hookSpecificOutput']['hookEventName'])
    def test_uninstall_preserves_user_config_flag_edit(self):
        self.install()
        self.put('config.toml',b'[features]\ncodex_hooks=false\n')
        self.uninstall()
        self.assertFalse(m.config(m.read(self.root,'config.toml'))[1])
        self.assertIsNotNone(m.read(self.root,m.STATE))

    def test_developer_append_restore_and_builtin_preservation(self):
        original = b'# keep\r\ndeveloper_instructions = "USER RULE" # note\r\nmodel_instructions_file = "existing.md"\r\n[features]\r\ncodex_hooks=true\r\n'
        self.put('config.toml', original)
        self.install()
        config = m.config(m.read(self.root, 'config.toml'))[0]
        self.assertTrue(config['developer_instructions'].startswith('USER RULE\n\n'))
        self.assertIn(SKILL.decode('utf-8').rstrip(), config['developer_instructions'])
        self.assertEqual('existing.md', config['model_instructions_file'])
        self.assertIn(b'# note', m.read(self.root, 'config.toml'))
        self.install()
        self.uninstall()
        self.assertEqual(original, m.read(self.root, 'config.toml'))

    def test_developer_user_edits_preserved_after_update_uninstall(self):
        self.install()
        config = m.read(self.root, 'config.toml')
        self.put('config.toml', m.developer_edit(config, 'USER PREFIX\n' + m.developer_value(config) + '\nUSER SUFFIX'))
        self.install(skill=SKILL+b'\nUpdated rule\n')
        self.uninstall()
        remaining = m.developer_value(m.read(self.root, 'config.toml'))
        self.assertIn('USER PREFIX', remaining)
        self.assertIn('USER SUFFIX', remaining)
        self.assertNotIn(m.BEGIN, remaining)

    def test_developer_modified_owned_block_stops_uninstall(self):
        self.install()
        config = m.read(self.root, 'config.toml')
        self.put('config.toml', m.developer_edit(config, m.developer_value(config).replace('name: concise', 'name: changed')))
        before = self.snapshot()
        with self.assertRaises(Exception): self.uninstall()
        self.assertEqual(before, self.snapshot())

    def test_developer_toml_string_forms(self):
        variants = ['developer_instructions = "simple" # comment\n', "'developer_instructions' = 'literal'\n", 'developer_instructions = """\nfirst\nsecond\n"""\n', "developer_instructions = '''\nfirst\nsecond\n'''\n"]
        for original in variants:
            with self.subTest(original=original):
                raw = original.encode('utf-8')
                value = m.developer_value(raw)
                updated = m.developer_edit(raw, value + '\nADDED')
                self.assertEqual(value + '\nADDED', m.developer_value(updated))
                self.assertEqual(value, m.developer_value(m.developer_edit(updated, value)))

    def test_profile_override_rejected_without_changes(self):
        self.put('config.toml', b'[profiles.custom]\ndeveloper_instructions="profile"\n')
        before = self.snapshot()
        with self.assertRaises(Exception): self.install()
        self.assertEqual(before, self.snapshot())

    def test_old_installation_record_upgrade(self):
        self.install()
        state = m.validate_state(m.read(self.root, m.STATE))
        for key in ('developer_managed', 'developer_restore'): state.pop(key)
        no_developer = m.developer_edit(m.read(self.root, 'config.toml'), None)
        self.put('config.toml', no_developer)
        state['files']['config.toml']['after'] = m.encode(no_developer)
        self.put(m.STATE, m.json_bytes(state))
        self.install()
        self.assertIn(SKILL.decode().rstrip(), m.developer_value(m.read(self.root, 'config.toml')))
        self.uninstall()
        self.assertIsNone(m.read(self.root, 'config.toml'))

if __name__=='__main__':unittest.main(verbosity=2)
