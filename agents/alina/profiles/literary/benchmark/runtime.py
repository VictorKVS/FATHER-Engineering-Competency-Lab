from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import shutil
import subprocess
import time
import urllib.request

import yaml

from agents.alina.profiles.literary.runtime import AlinaLiteraryRuntime


class LiteraryBenchmark:
    def __init__(self, repo_root='.', output_root='benchmark_results/alina_literary'):
        self.root=Path(repo_root)
        self.profile=self.root/'agents'/'alina'/'profiles'/'literary'
        self.output_root=Path(output_root)
        self.output_root.mkdir(parents=True,exist_ok=True)

    def _yaml(self, rel):
        return yaml.safe_load((self.profile/rel).read_text(encoding='utf-8'))

    @staticmethod
    def _ready(url, timeout=2):
        try:
            with urllib.request.urlopen(url,timeout=timeout) as r:
                return r.status==200
        except Exception:
            return False

    def _start_server(self, model, port=8080, context=4096):
        exe=shutil.which('llama-server')
        if not exe:
            raise RuntimeError('llama-server not found in PATH')
        path=Path(model['path'])
        if not path.exists():
            raise FileNotFoundError(str(path))
        args=[exe,'-m',str(path),'--host','127.0.0.1','--port',str(port),'--cors-origins','localhost','-ngl','99','-c',str(context),'-np','1']
        overrides=model.get('runtime_overrides') or {}
        if overrides.get('no_jinja'):
            args.append('--no-jinja')
        if overrides.get('chat_template'):
            args.extend(['--chat-template',str(overrides['chat_template'])])
        log_path=self.output_root/f"server-{model['model_id']}.log"
        log=log_path.open('w',encoding='utf-8')
        proc=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,text=True)
        deadline=time.time()+180
        while time.time()<deadline:
            if proc.poll() is not None:
                log.close()
                raise RuntimeError(f"llama-server exited for {model['model_id']}; see {log_path}")
            if self._ready(f'http://127.0.0.1:{port}/v1/models'):
                return proc,log,log_path
            time.sleep(2)
        proc.terminate(); log.close()
        raise TimeoutError(f"model did not become ready: {model['model_id']}")

    @staticmethod
    def _stop_server(proc, log):
        if proc.poll() is None:
            proc.terminate()
            try: proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=5)
        log.close()

    def run(self):
        suite=self._yaml('benchmark/GENRE_SUITE.yaml')['suite']
        matrix=self._yaml('benchmark/MODEL_MATRIX.yaml')['benchmark_models']
        run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        run_dir=self.output_root/run_id
        run_dir.mkdir(parents=True,exist_ok=False)
        results=[]
        runtime=AlinaLiteraryRuntime(repo_root=self.root,evidence_dir=run_dir/'evidence')

        for model in [m for m in matrix['candidates'] if m.get('enabled',True)]:
            model_result={'model_id':model['model_id'],'label':model['label'],'status':'PENDING','cases':[]}
            proc=log=None
            try:
                proc,log,log_path=self._start_server(model)
                model_result['server_log']=str(log_path)
                for case in suite['cases']:
                    try:
                        record=runtime.run(
                            story_text=case['story_text'],
                            endpoint='http://127.0.0.1:8080/v1/chat/completions',
                            model_id=model['model_id'],
                            target_length=min(suite.get('max_target_words',450),450),
                            constraints=case.get('constraints',[]),
                        )
                        model_result['cases'].append({
                            'case_id':case['id'],
                            'genre':case['genre'],
                            'title':case['title'],
                            'status':'PASS' if record['contract_valid'] else 'CONTRACT_FAIL',
                            'generator':model['model_id'],
                            'agent':'AG-001',
                            'profile':'ALINA_LITERARY',
                            'prompt_version':'0.2.0',
                            'rag_version':'ALINA_LITERARY_RAG_V02',
                            'kb_version':'0.2.0',
                            'expert_review':'PENDING_CHATGPT_REVIEW',
                            'evidence_path':record['evidence_path'],
                            'output':record['output'],
                        })
                    except Exception as exc:
                        model_result['cases'].append({'case_id':case['id'],'genre':case['genre'],'status':'ERROR','error':repr(exc),'generator':model['model_id']})
                model_result['status']='COMPLETE'
            except Exception as exc:
                model_result['status']='MODEL_RUNTIME_FAIL'
                model_result['error']=repr(exc)
            finally:
                if proc is not None and log is not None:
                    self._stop_server(proc,log)
            results.append(model_result)

        manifest={
            'benchmark_id':'ALINA_LITERARY_BENCHMARK_V1',
            'run_id':run_id,
            'created_at':datetime.now(timezone.utc).isoformat(),
            'agent':'AG-001',
            'profile':'ALINA_LITERARY',
            'suite':'ALINA_LITERARY_GENRE_SUITE_V1',
            'automatic_model_count':len([m for m in matrix['candidates'] if m.get('enabled',True)]),
            'results':results,
        }
        (run_dir/'summary.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        self._write_review_bundle(run_dir,manifest)
        return run_dir,manifest

    @staticmethod
    def _write_review_bundle(run_dir, manifest):
        lines=[
            '# ALINA Literary Expert Review Bundle',
            '',
            f"Run: {manifest['run_id']}",
            f"Models: {manifest['automatic_model_count']}",
            '',
            'Review status: PENDING_CHATGPT_REVIEW',
            '',
        ]
        for model in manifest['results']:
            lines += [f"## {model['model_id']} — {model['status']}",'']
            for case in model.get('cases',[]):
                lines += [f"### {case.get('case_id')} / {case.get('genre')}",
                          f"Generator: {case.get('generator')}",
                          f"Agent: {case.get('agent','AG-001')}",
                          f"Expert review: {case.get('expert_review','PENDING')}",'']
                output=case.get('output') or {}
                if output.get('continuation'):
                    lines += [output['continuation'],'']
                if case.get('error'):
                    lines += [f"ERROR: {case['error']}",'']
        (run_dir/'REVIEW_BUNDLE.md').write_text('\n'.join(lines),encoding='utf-8')

    def publish_git(self, run_dir):
        subprocess.run(['git','add',str(run_dir)],cwd=self.root,check=True)
        subprocess.run(['git','commit','-m',f'literary benchmark: publish {run_dir.name} review bundle'],cwd=self.root,check=True)
        subprocess.run(['git','push'],cwd=self.root,check=True)
