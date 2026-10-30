import ast
import unittest
from pathlib import Path


class CliLazyImportsTest(unittest.TestCase):
    def test_cli_has_no_top_level_factory_test_import(self):
        path=Path("father_runtime/cli.py")
        tree=ast.parse(path.read_text(encoding="utf-8"))
        imports=[]
        for node in tree.body:
            if isinstance(node,ast.ImportFrom):
                imports.append(node.module or "")
            elif isinstance(node,ast.Import):
                imports.extend(alias.name for alias in node.names)
        self.assertFalse(
            any(name.startswith("factory.tests") for name in imports),
            imports,
        )

    def test_story_swap_import_is_lazy(self):
        text=Path("father_runtime/cli.py").read_text(encoding="utf-8")
        marker="if args.command == 'test-01-story-model-swap':"
        block=text[text.index(marker):]
        self.assertIn(
            "from factory.tests.test_01_story_model_swap.runtime import StoryModelSwapTest",
            block,
        )


if __name__=="__main__":
    unittest.main()
