import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from father_runtime.project_init import ProjectInitializer


class ProjectInitPreflightTest(unittest.TestCase):
    def test_local_existing_path_blocks_create_new(self):
        with TemporaryDirectory() as d:
            proposal={
                "github_owner":"example",
                "github_repository":"repo",
                "local_directory":d,
            }
            plan={"github_mode":"CREATE_NEW","local_mode":"CREATE_NEW","git_mode":"INIT_AND_BIND"}
            init=ProjectInitializer()
            init.github_status=lambda _: (False,None)
            init._gh_available=lambda: True
            result=init.preflight(proposal,plan)
            self.assertIn("LOCAL_DIRECTORY_ALREADY_EXISTS",result.conflicts)

    def test_existing_github_blocks_create_new(self):
        with TemporaryDirectory() as d:
            proposal={
                "github_owner":"example",
                "github_repository":"repo",
                "local_directory":str(Path(d)/"new"),
            }
            plan={"github_mode":"CREATE_NEW","local_mode":"CREATE_NEW","git_mode":"INIT_AND_BIND"}
            init=ProjectInitializer()
            init.github_status=lambda _: (True,"https://github.com/example/repo")
            init._gh_available=lambda: True
            result=init.preflight(proposal,plan)
            self.assertIn("GITHUB_REPOSITORY_ALREADY_EXISTS",result.conflicts)
            self.assertIn("BIND_EXISTING",result.allowed_actions)

    def test_execution_requires_approval(self):
        init=ProjectInitializer()
        with self.assertRaises(PermissionError):
            init.execute({}, {}, approved=False)

    def test_ui_calls_preflight_before_execute(self):
        text=Path("factory/ui/father_site/stage001.js").read_text(encoding="utf-8")
        self.assertIn('await api("/stage001/preflight"',text)
        self.assertIn('await api("/stage001/execute"',text)
        self.assertIn('Создание заблокировано',text)
        self.assertIn('openGithub',text)
        self.assertIn('openLocal',text)


if __name__=="__main__":
    unittest.main()
