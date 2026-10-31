from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
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
        self.catalog_path=self.root/'factory'/'model_fabric'/'LOCAL_MODEL_CATALOG.yaml'
        self.output_root=Path(output_root)
        self.output_root.mkdir(parents=True,exist_ok=True)

    def _yaml(self, path):
        return yaml.safe_load(Path(path).read_text(encoding='utf-8'))

    def catalog(self):
        return self._yaml(self.catalog_path)['catalog']

    def eligible_models(self):
        allowed={'ELIGIBLE','ELIGIBLE_EXPERIMENTAL'}
        return [x for x in self.catalog()['assets'] if x.get('alina_literary') in allowed]

    @staticmethod
    def _ready(url, timeout=2):
        try:
            with urllib.request.urlopen(url,timeout=timeout) as r:
                return r.status==200
        except Exception:
            return False

    def _launch_attempt(self, model, template, port, context):
        exe=shutil.which('llama-server')
        if not exe:
            raise RuntimeError('llama-server not found in PATH')
        model_path=Path(model['path'])
        if not model_path.exists():
            raise FileNotFoundError(str(model_path))

        alias=model['id']
        args=[
            exe,'-m',str(model_path),
            '--alias',alias,
            '--host','127.0.0.1','--port',str(port),
            '--cors-origins','localhost',
            '-ngl','99','-c',str(context),'-np','1',
        ]
        if template and template!='metadata':
            args.extend(['--chat-template',template])
        if model.get('launch',{}).get('no_jinja_fallback') and template!='metadata':
            args.append('--no-jinja')

        safe_template=(template or 'metadata').replace('/','_')
        log_path=self.output_root/f"server-{model['id']}-{safe_template}.log"
        log=log_path.open('w',encoding='utf-8')
        proc=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,text=True)
        return proc,log,log_path,alias

    def _start_server(self, model, port=8080, context=4096):
        launch=model.get('launch') or {}
        templates=[]
        primary=launch.get('primary_template')
        if primary:
            templates.append(primary)
        for item in launch.get('fallback_templates') or []:
            if item not in templates:
                templates.append(item)
        if not templates:
            templates=['metadata']

        errors=[]
        for template in templates:
            proc=log=None
            try:
                proc,log,log_path,alias=self._launch_attempt(model,template,port,context)
                deadline=time.time()+180
                while time.time()<deadline:
                    if proc.poll() is not None:
                        raise RuntimeError(f'process_exit template={template}')
                    if self._ready(f'http://127.0.0.1:{port}/v1/models'):
                        return proc,log,log_path,alias,template
                    time.sleep(2)
                raise TimeoutError(f'readiness_timeout template={template}')
            except Exception as exc:
                errors.append({'template':template,'error':repr(exc)})
                if proc is not None and proc.poll() is None:
                    proc.terminate()
                    try: proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        proc.kill(); proc.wait(timeout=5)
                if log is not None:
                    log.close()
        raise RuntimeError(json.dumps({'model':model['id'],'launch_attempts':errors},ensure_ascii=False))

    @staticmethod
    def _stop_server(proc, log):
        if proc.poll() is None:
            proc.terminate()
            try: proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=5)
        log.close()

    def run(self):
        suite=self._yaml(self.profile/'benchmark'/'GENRE_SUITE.yaml')['suite']
        models=self.eligible_models()
        run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        run_dir=self.output_root/run_id
        run_dir.mkdir(parents=True,exist_ok=False)
        results=[]
        runtime=AlinaLiteraryRuntime(repo_root=self.root,evidence_dir=run_dir/'evidence')

        for model in models:
            model_result={
                'model_id':model['id'],
                'file':model['file'],
                'class':model['class'],
                'eligibility':model['alina_literary'],
                'status':'PENDING',
                'cases':[],
            }
            proc=log=None
            try:
                proc,log,log_path,alias,template=self._start_server(model)
                model_result['server_log']=str(log_path)
                model_result['selected_template']=template
                model_result['api_alias']=alias
                for case in suite['cases']:
                    try:
                        record=runtime.run(
                            story_text=case['story_text'],
                            endpoint='http://127.0.0.1:8080/v1/chat/completions',
                            model_id=alias,
                            target_length=min(suite.get('max_target_words',450),450),
                            constraints=case.get('constraints',[]),
                        )
                        model_result['cases'].append({
                            'case_id':case['id'],
                            'genre':case['genre'],
                            'title':case['title'],
                            'status':'PASS' if record['contract_valid'] else 'CONTRACT_FAIL',
                            'generator':model['id'],
                            'generator_file':model['file'],
                            'agent':'AG-001',
                            'profile':'ALINA_LITERARY',
                            'prompt_version':'0.2.0',
                            'rag_version':'ALINA_LITERARY_RAG_V02',
                            'kb_version':'0.2.0',
                            'launch_template':template,
                            'expert_review':'PENDING_CHATGPT_REVIEW',
                            'evidence_path':record['evidence_path'],
                            'output':record['output'],
                        })
                    except Exception as exc:
                        model_result['cases'].append({
                            'case_id':case['id'],'genre':case['genre'],
                            'status':'INFERENCE_OR_CONTRACT_ERROR',
                            'error':repr(exc),'generator':model['id']
                        })
                model_result['status']='COMPLETE'
            except FileNotFoundError as exc:
                model_result['status']='FILE_MISSING'; model_result['error']=repr(exc)
            except Exception as exc:
                model_result['status']='MODEL_RUNTIME_FAIL'; model_result['error']=repr(exc)
            finally:
                if proc is not None and log is not None:
                    self._stop_server(proc,log)
            results.append(model_result)

        manifest={
            'benchmark_id':'ALINA_LITERARY_CATALOG_SWEEP_V1',
            'run_id':run_id,
            'created_at':datetime.now(timezone.utc).isoformat(),
            'agent':'AG-001',
            'profile':'ALINA_LITERARY',
            'suite':'ALINA_LITERARY_GENRE_SUITE_V1',
            'catalog_total_assets':self.catalog()['total_discovered_assets'],
            'eligible_model_count':len(models),
            'results':results,
        }
        (run_dir/'summary.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        self._write_review_bundle(run_dir,manifest)
        return run_dir,manifest

    @staticmethod
    def _write_review_bundle(run_dir, manifest):
        lines=[
            '# ALINA Literary Catalog Sweep — Expert Review Bundle','',
            f"Run: {manifest['run_id']}",
            f"Catalog assets: {manifest['catalog_total_assets']}",
            f"Eligible text models: {manifest['eligible_model_count']}",'',
            'Expert review status: PENDING_CHATGPT_REVIEW','',
        ]
        for model in manifest['results']:
            lines += [
                f"## {model['model_id']} — {model['status']}",
                f"File: {model.get('file')}",
                f"Class: {model.get('class')}",
                f"Template: {model.get('selected_template','NOT_READY')}",'',
            ]
            if model.get('error'):
                lines += [f"MODEL ERROR: {model['error']}",'']
            for case in model.get('cases',[]):
                lines += [
                    f"### {case.get('case_id')} / {case.get('genre')}",
                    f"Generator: {case.get('generator')}",
                    f"Agent: {case.get('agent','AG-001')}",
                    f"Prompt/RAG/KB: {case.get('prompt_version','0.2.0')} / {case.get('rag_version','ALINA_LITERARY_RAG_V02')} / {case.get('kb_version','0.2.0')}",
                    f"Expert review: {case.get('expert_review','PENDING')}",'',
                ]
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