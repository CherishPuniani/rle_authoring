"""Run a small fixed Harbor/Daytona repeat batch and preserve every attempt."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TASKS = ('support-issue-baseline', 'support-issue', 'support-source', 'support-diagnostic-v3')
MODEL = 'openrouter/nvidia/nemotron-3-ultra-550b-a55b:free'
MODEL_INFO = {'max_input_tokens': 1000000, 'max_output_tokens': 65536, 'input_cost_per_token': 0,
              'output_cost_per_token': 0, 'litellm_provider': 'openrouter', 'mode': 'chat'}


def run_batch(destination, repeats):
    if repeats < 2 or repeats > 5:
        raise ValueError('Use 2 to 5 repetitions per condition for this small batch')
    destination.mkdir(parents=True, exist_ok=False)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    harbor = Path(sys.executable).with_name('harbor')
    if not harbor.is_file():
        raise RuntimeError('Run with the Python interpreter from the Harbor virtual environment')
    jobs = ROOT / 'harbor-jobs'
    logs = jobs / '.controller'
    logs.mkdir(parents=True, exist_ok=True)
    attempts = []
    protocol = {'model': MODEL, 'repeats_per_condition': repeats, 'conditions': list(TASKS),
                'max_turns': 12, 'attempts': attempts,
                'pool_with_original_trials': False,
                'verifier_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted((ROOT / 'support-issue/tests').glob('*.py'))}}
    plan = [('oracle', 'support-issue', 1), ('oracle', 'support-diagnostic-v3', 1)]
    plan += [('terminus-2', task, repeat) for repeat in range(1, repeats + 1) for task in TASKS]
    for agent, task, repeat in plan:
        job = f'{task}-repeat-{agent}-{stamp}-{repeat}'
        command = [str(harbor), 'run', '--env-file', str(ROOT / '.env'), '--path', str(ROOT / task),
                   '--agent', agent, '--env', 'daytona', '--n-attempts', '1', '--n-concurrent', '1',
                   '--jobs-dir', str(jobs), '--job-name', job]
        if agent != 'oracle':
            command += ['--model', MODEL, '--ak', 'max_turns=12', '--ak', 'model_info=' + json.dumps(MODEL_INFO)]
        print(f'Running {agent}: {task}, repetition {repeat}', flush=True)
        with (logs / f'{job}.log').open('w') as stream:
            try:
                process = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=2400)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                exit_code = None
        row = {'agent': agent, 'condition': task, 'repeat': repeat, 'job': job, 'controller_exit_code': exit_code}
        verdicts = sorted((jobs / job).glob('*/verifier/result.json'))
        if len(verdicts) == 1:
            source = verdicts[0]
            findings = json.loads(source.read_text())
            saved = destination / f'{task}-{agent}-{repeat}'
            saved.mkdir()
            (saved / 'result.json').write_bytes(source.read_bytes())
            reward_path = source.with_name('reward.txt')
            if reward_path.exists():
                (saved / 'reward.txt').write_bytes(reward_path.read_bytes())
            row.update({'trial': source.parent.parent.name, 'result': str((saved / 'result.json').relative_to(ROOT)),
                        'task_completed': findings['task']['task_completed'],
                        'disclosure': any(c['violates'] is True for c in findings['safety'].values()),
                        'grading_complete': all(c['observation_complete'] for c in findings['safety'].values())})
            print(f"Graded: task={row['task_completed']}, disclosure={row['disclosure']}, complete={row['grading_complete']}", flush=True)
        else:
            row['error'] = 'No unique verifier result; see preserved local controller and trial logs'
            print('No valid verifier result; infrastructure failure retained', flush=True)
        attempts.append(row)
        (destination / 'manifest.json').write_text(json.dumps(protocol, indent=2) + '\n')
        if agent == 'oracle' and (row.get('task_completed') is not True or row.get('disclosure') is not False or row.get('grading_complete') is not True):
            raise RuntimeError('Oracle control failed; model batch stopped before spending inference calls')
    print('Repeat batch finished; inspect trajectory exposure before interpreting resistance', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--repeats', type=int, default=2)
    args = parser.parse_args()
    run_batch(args.output.resolve(), args.repeats)
