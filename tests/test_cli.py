from pathlib import Path
import tempfile
import unittest

from codex_task_workspace_manager.cli import main


class CliTests(unittest.TestCase):
    def test_bootstrap_and_create_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(main(["bootstrap", "--root", str(root)]), 0)
            self.assertTrue((root / "skills" / "common").is_dir())
            self.assertEqual(main(["create-task", "--root", str(root), "--domain", "research", "--type", "presentations", "--name", "DetWAN_GroupMeetingPPT", "--date", "20260607"]), 0)
            task = root / "research" / "presentations" / "20260607_DetWAN_GroupMeetingPPT"
            for sub in ("input", "output", "logs", "assets", "temp", "archive"):
                self.assertTrue((task / sub).is_dir())

    def test_route_file_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            main(["create-task", "--root", str(root), "--domain", "research", "--type", "presentations", "--name", "DetWAN_GroupMeetingPPT", "--date", "20260607"])
            source = root / "DetWAN.pdf"
            source.write_text("pdf", encoding="utf-8")
            self.assertEqual(main(["route-file", "--root", str(root), "--file", str(source), "--task", "20260607_DetWAN_GroupMeetingPPT", "--kind", "input", "--copy"]), 0)
            routed = root / "research" / "presentations" / "20260607_DetWAN_GroupMeetingPPT" / "input" / "20260607_DetWAN_GroupMeetingPPT_input.pdf"
            self.assertTrue(routed.exists())
            self.assertTrue(source.exists())


if __name__ == "__main__":
    unittest.main()
