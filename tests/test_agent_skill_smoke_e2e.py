import os
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tests.e2e.agent_harness import REPO_ROOT, run_agent_prompt
from tests.e2e.harness import build_temp_instance, fixture_path


class AgentSkillSmokeE2ETest(unittest.TestCase):
    def test_run_agent_prompt_requires_runner_env(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(
                RuntimeError,
                "SKILL_AGENT_RUNNER must point to an executable runner path",
            ):
                run_agent_prompt("Use skill wiki-init.")

    def test_run_agent_prompt_reports_timeout(self) -> None:
        with TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            runner_path = temp_dir / "sleep-runner.sh"
            runner_path.write_text("#!/bin/sh\nsleep 1\n", encoding="utf-8")
            runner_path.chmod(0o755)

            with patch.dict(
                os.environ,
                {"SKILL_AGENT_RUNNER": str(runner_path)},
                clear=False,
            ):
                with patch(
                    "tests.e2e.agent_harness.AGENT_RUN_TIMEOUT_SECONDS",
                    0.01,
                ):
                    with self.assertRaisesRegex(
                        RuntimeError,
                        "Agent runner timed out",
                    ):
                        run_agent_prompt("Use skill wiki-query.")

    def test_run_agent_prompt_resolves_relative_runner_from_repo_root(self) -> None:
        with TemporaryDirectory(dir=REPO_ROOT) as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            runner_path = temp_dir / "echo-runner.sh"
            runner_path.write_text("#!/bin/sh\ncat\n", encoding="utf-8")
            runner_path.chmod(0o755)
            relative_runner = runner_path.relative_to(REPO_ROOT)
            original_cwd = Path.cwd()
            os.chdir("/tmp")
            self.addCleanup(os.chdir, original_cwd)

            with patch.dict(
                os.environ,
                {"SKILL_AGENT_RUNNER": str(relative_runner)},
                clear=False,
            ):
                result = run_agent_prompt("Use skill wiki-query.")

        self.assertEqual(0, result.returncode)
        self.assertEqual("Use skill wiki-query.", result.stdout.strip())

    def test_run_agent_prompt_uses_requested_working_directory(self) -> None:
        with TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            runner_path = temp_dir / "pwd-runner.sh"
            runner_path.write_text("#!/bin/sh\npwd\n", encoding="utf-8")
            runner_path.chmod(0o755)

            with patch.dict(
                os.environ,
                {"SKILL_AGENT_RUNNER": str(runner_path)},
                clear=False,
            ):
                result = run_agent_prompt("Use skill wiki-init.", cwd=temp_dir)

        self.assertEqual(0, result.returncode)
        self.assertEqual(str(temp_dir.resolve()), str(Path(result.stdout.strip()).resolve()))

    def test_real_agent_runs_minimal_skill_workflow(self) -> None:
        if os.environ.get("SKILL_AGENT_E2E") != "1":
            self.skipTest("set SKILL_AGENT_E2E=1 to enable slow real-agent smoke test")

        instance = build_temp_instance()
        self.addCleanup(instance.temp_dir.cleanup)
        fixture_root = fixture_path()

        init_prompt = (
            "Use skill wiki-init. "
            f"Create config-dir {instance.config_dir} and wiki-root {instance.wiki_root}. "
            "Domain: E2E testing knowledge base. "
            "Source types: notes, articles. "
            "Categories: Wiki Pages, Concepts Pages, Topic Relations, Quick Navigation."
        )
        init_result = run_agent_prompt(init_prompt)
        self.assertEqual(0, init_result.returncode, init_result.stderr)
        self.assertTrue((instance.config_dir / "openwiki.toml").exists())

        source_path = fixture_root / "source.md"
        ingest_prompt = (
            "Use skill wiki-ingest. "
            f"Use config-dir {instance.config_dir}. "
            f"Ingest local file {source_path}. "
            "For this smoke test, the user wants the default emphasis and confirms you may proceed. "
            "Do not use network or agent-browser; use only local fixtures and local wiki state."
        )
        ingest_result = run_agent_prompt(ingest_prompt)
        self.assertEqual(0, ingest_result.returncode, ingest_result.stderr)
        page_path = instance.wiki_root / "wiki" / "pages" / "local-first-wiki-testing.md"
        raw_source_path = instance.wiki_root / "raw" / "local-first-wiki-testing-source.md"
        self.assertTrue(page_path.exists())
        self.assertTrue(raw_source_path.exists())

        query_text = (fixture_root / "query.txt").read_text(encoding="utf-8").strip()
        query_prompt = (
            "Use skill wiki-query. "
            f"Use config-dir {instance.config_dir}. "
            f"Question: {query_text} "
            "Answer only from the local wiki instance and do not use network or agent-browser. "
            "Do not save the answer to concepts for this smoke test."
        )
        query_result = run_agent_prompt(query_prompt)
        self.assertEqual(0, query_result.returncode, query_result.stderr)
        self.assertTrue(query_result.stdout.strip())
        self.assertIn("local-first-wiki-testing", query_result.stdout.lower())
        self.assertIn("worth saving", query_result.stdout.lower())
        log_path = instance.wiki_root / "wiki" / "log.md"
        self.assertTrue(log_path.exists())
        self.assertIn("query |", log_path.read_text(encoding="utf-8"))

        update_path = fixture_root / "update.md"
        update_prompt = (
            "Use skill wiki-update. "
            f"Use config-dir {instance.config_dir}. "
            f"Apply the update described in {update_path}. "
            "Do not use network or agent-browser; use only local wiki files and the provided update file. "
            "For this smoke test, the user pre-approves the proposed diff once you show it."
        )
        update_result = run_agent_prompt(update_prompt)
        self.assertEqual(0, update_result.returncode, update_result.stderr)
        self.assertIn("current:", update_result.stdout.lower())
        self.assertIn("proposed:", update_result.stdout.lower())
        self.assertIn("reason:", update_result.stdout.lower())
        self.assertIn("source:", update_result.stdout.lower())

        self.assertTrue(page_path.exists())
        page_md = page_path.read_text(encoding="utf-8")
        self.assertIn("The update now covers wiki-lint in a later phase.", page_md)
        log_md = log_path.read_text(encoding="utf-8")
        self.assertIn("update |", log_md)
        self.assertIn("reason", log_md.lower())
        self.assertIn("source", log_md.lower())

    def test_real_agent_discovers_config_dir_from_current_working_directory(self) -> None:
        if os.environ.get("SKILL_AGENT_E2E") != "1":
            self.skipTest("set SKILL_AGENT_E2E=1 to enable slow real-agent smoke test")

        instance = build_temp_instance()
        self.addCleanup(instance.temp_dir.cleanup)
        fixture_root = fixture_path()

        init_prompt = (
            "Use skill wiki-init. "
            f"Create config-dir {instance.config_dir} and wiki-root {instance.wiki_root}. "
            "Domain: E2E testing knowledge base. "
            "Source types: notes, articles. "
            "Categories: Wiki Pages, Concepts Pages, Topic Relations, Quick Navigation."
        )
        init_result = run_agent_prompt(init_prompt)
        self.assertEqual(0, init_result.returncode, init_result.stderr)

        nested_work_dir = instance.config_dir / "nested" / "workspace"
        nested_work_dir.mkdir(parents=True, exist_ok=True)
        source_path = fixture_root / "source.md"
        ingest_prompt = (
            "Use skill wiki-ingest. "
            f"Ingest local file {source_path}. "
            "Do not use network or agent-browser; use only local fixtures and local wiki state."
        )
        ingest_result = run_agent_prompt(ingest_prompt, cwd=nested_work_dir)
        self.assertEqual(0, ingest_result.returncode, ingest_result.stderr)

        page_path = instance.wiki_root / "wiki" / "pages" / "local-first-wiki-testing.md"
        self.assertTrue(page_path.exists())

    def test_real_agent_uses_default_config_dir_when_no_explicit_config_dir(self) -> None:
        if os.environ.get("SKILL_AGENT_E2E") != "1":
            self.skipTest("set SKILL_AGENT_E2E=1 to enable slow real-agent smoke test")

        instance = build_temp_instance()
        self.addCleanup(instance.temp_dir.cleanup)

        init_prompt = (
            "Use skill wiki-init. "
            f"Create config-dir {instance.config_dir} and wiki-root {instance.wiki_root}. "
            "Domain: E2E testing knowledge base. "
            "Source types: notes, articles. "
            "Categories: Wiki Pages, Concepts Pages, Topic Relations, Quick Navigation."
        )
        init_result = run_agent_prompt(init_prompt)
        self.assertEqual(0, init_result.returncode, init_result.stderr)

        simulated_home = instance.temp_root / "simulated-home"
        simulated_home.mkdir(parents=True, exist_ok=True)
        default_config_dir = simulated_home / ".openwiki"
        shutil.copytree(str(instance.config_dir), str(default_config_dir))
        self.assertTrue((default_config_dir / "openwiki.toml").exists())

        work_dir = instance.temp_root / "some-random-workdir"
        work_dir.mkdir(parents=True, exist_ok=True)

        with patch.dict(os.environ, {"HOME": str(simulated_home)}, clear=False):
            query_result = run_agent_prompt(
                "Use skill wiki-query. "
                "Question: What testing layers exist? "
                "Answer only from the local wiki and do not use network or agent-browser.",
                cwd=work_dir,
            )

        self.assertEqual(0, query_result.returncode, query_result.stderr)
        output_lower = query_result.stdout.lower()
        self.assertTrue(
            "default wiki config" in output_lower
            or ".openwiki" in output_lower,
            f"agent output should mention default config usage: {query_result.stdout[:500]}",
        )


if __name__ == "__main__":
    unittest.main()
