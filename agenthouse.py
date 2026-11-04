"""Run the sibling AgentHouse tools with this project's configuration and outputs."""
from pathlib import Path
import json
import os
import subprocess
import sys

PROJECT = Path(__file__).resolve().parent
SETTINGS = json.loads((PROJECT / '.agenthouse.json').read_text(encoding='utf-8'))
TOOLS = (PROJECT / SETTINGS['tool_root']).resolve()
PYTHON = TOOLS / ('.venv/Scripts/python.exe' if os.name == 'nt' else '.venv/bin/python')
CHANNEL = PROJECT / SETTINGS['channel_config']

def main():
    if not PYTHON.is_file():
        raise SystemExit(f'AgentHouse Python is missing: {PYTHON}. See docs/AGENTHOUSE.md.')
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print('agenthouse.py doctor | models | journalism <args> | intake <args> | episode <args> | tool <AgentHouse-relative.py> <args>')
        return 0
    if Path(sys.executable).resolve() != PYTHON.resolve():
        return subprocess.call([str(PYTHON), str(Path(__file__).resolve()), *args], cwd=PROJECT)
    os.environ['AGENTHOUSE_PROJECT_ROOT'] = str(PROJECT)
    os.environ['PYTHONUTF8'] = '1'
    os.environ['PYTHONPATH'] = str(TOOLS) + (os.pathsep + os.environ['PYTHONPATH'] if os.environ.get('PYTHONPATH') else '')
    from dotenv import load_dotenv
    load_dotenv(TOOLS / '.env')
    command, *rest = args
    if command == 'doctor':
        import yaml
        sys.path.insert(0, str(TOOLS))
        from v5.lib.llm_config import resolve_role
        if not CHANNEL.is_file():
            raise SystemExit(f'Copy {CHANNEL.with_suffix(".example.yaml")} to {CHANNEL}, then configure the local sender.')
        channel = yaml.safe_load(CHANNEL.read_text(encoding='utf-8-sig'))
        calls = {}
        for phase, task in channel.get('journalism', {}).get('tasks', {}).items():
            template = (CHANNEL.parent / task['template']).resolve()
            if not template.is_file():
                raise SystemExit(f'Missing phase template: {template}')
            call = resolve_role(channel, task['role'])
            calls[phase] = {'role':task['role'], 'model':call.model, 'harness':call.harness_kind}
        print(json.dumps({'project':str(PROJECT),'tool_root':str(TOOLS),
            'python':str(PYTHON),'channel':channel['id'],'phases':calls,
            'external_calls':False}, ensure_ascii=False, indent=2))
        return 0
    scripts = {'models':'v5/scripts/print_resolved_llm.py',
        'journalism':'v5/skills/journalism_desk/scripts/journalism_desk.py',
        'intake':'v5/skills/youtube_source_intake/scripts/youtube_source_intake.py',
        'episode':'v5/scripts/run_v5_episode.py'}
    if command == 'tool':
        if not rest:
            raise SystemExit('tool requires an AgentHouse-relative Python script path')
        script = (TOOLS / rest.pop(0)).resolve()
        if not script.is_relative_to(TOOLS):
            raise SystemExit('Tool path must stay inside AgentHouse')
    elif command in scripts:
        script = TOOLS / scripts[command]
    else:
        raise SystemExit(f'Unknown command: {command}')
    if not script.is_file():
        raise SystemExit(f'Missing shared tool: {script}')
    def supplied(flag):
        return any(a == flag or a.startswith(flag+'=') for a in rest)
    if command in ('models','episode') and not supplied('--channel-config'):
        rest += ['--channel-config', str(CHANNEL)]
    if command == 'episode' and not supplied('--episodes-dir'):
        rest += ['--episodes-dir', str(PROJECT/'v5/workspace/episodes')]
    return subprocess.call([str(PYTHON),str(script),*rest],cwd=PROJECT,env=os.environ.copy())

if __name__ == '__main__':
    raise SystemExit(main())
