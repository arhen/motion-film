import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/motion-film-qa/scripts/media-check.py"
spec = importlib.util.spec_from_file_location("media_check", SCRIPT)
media_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(media_check)


class MediaCheckTests(unittest.TestCase):
    def setUp(self):
        self.clock = {"fps": 30, "seconds": 6, "width": 640, "height": 360}
        self.probe = {"size_bytes": 1024, "duration": 6,
                      "video": {"width": 640, "height": 360, "fps": 30,
                                "avg_frame_rate": "30/1", "duration": 6,
                                "nb_frames": 180, "start_time": 0, "rotation": 0}}

    def test_master_matches(self):
        result = media_check.verify(self.clock, self.probe)
        self.assertTrue(result["ok"])
        self.assertTrue(result["frame_count_verified"])

    def test_planned_derivative_dimensions(self):
        self.probe["video"].update(width=320, height=180)
        self.assertFalse(media_check.verify(self.clock, self.probe)["ok"])
        self.assertTrue(media_check.verify(self.clock, self.probe, 320, 180)["ok"])

    def test_retimed_or_reframed_output_fails(self):
        for patch in ({"duration": 5.9}, {"duration": 6.1}, {"nb_frames": 179},
                      {"avg_frame_rate": "25/1"}, {"width": 360, "height": 640},
                      {"variable_frame_rate_suspected": True}, {"start_time": 0.1},
                      {"rotation": 90}):
            with self.subTest(patch=patch):
                probe = copy.deepcopy(self.probe)
                probe["video"].update(patch)
                self.assertFalse(media_check.verify(self.clock, probe)["ok"])

    def test_missing_frame_count_is_reported(self):
        self.probe["video"].update(nb_frames=None, duration=None)
        self.probe["duration"] = 6.008
        result = media_check.verify(self.clock, self.probe)
        self.assertTrue(result["ok"])
        self.assertFalse(result["frame_count_verified"])
        self.assertTrue(result["notes"])

    def test_rounds_frames_like_remotion(self):
        self.clock["seconds"] = 0.15
        self.probe["video"].update(nb_frames=5, duration=5 / 30)
        self.assertTrue(media_check.verify(self.clock, self.probe)["ok"])

    def test_invalid_clock_or_probe_fails_closed(self):
        for field, value in (("fps", 0), ("fps", float("nan")), ("seconds", -1),
                             ("width", 641), ("fps", True)):
            with self.subTest(field=field, value=value):
                clock = {**self.clock, field: value}
                with self.assertRaises(ValueError):
                    media_check.verify(clock, self.probe)
        for patch in ({"dry_run": True}, {"status": "failed"}, {"video": None},
                      {"size_bytes": 0}):
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):
                    media_check.verify(self.clock, {**self.probe, **patch})
        with self.assertRaises(ValueError):
            media_check.verify(self.clock, self.probe, width=320)

    def test_cli_errors_are_nonzero_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            clock, probe = Path(tmp) / "clock.json", Path(tmp) / "probe.json"
            clock.write_text(json.dumps(self.clock))
            probe.write_text(json.dumps(self.probe))
            run = subprocess.run([sys.executable, str(SCRIPT), str(clock), str(probe)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(json.loads(run.stdout)["ok"])
            probe.write_text("{}")
            run = subprocess.run([sys.executable, str(SCRIPT), str(clock), str(probe)],
                                 capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse(json.loads(run.stdout)["ok"])


@unittest.skipUnless(os.environ.get("FFMPEG_SKILL_DIR") and shutil.which("ffmpeg"),
                     "set FFMPEG_SKILL_DIR to the complete pinned upstream package")
class PipelineIntegrationTests(unittest.TestCase):
    def run_command(self, *args):
        run = subprocess.run([str(arg) for arg in args], capture_output=True, text=True, timeout=60)
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        return run.stdout

    def upstream(self, name, *args):
        return self.run_command(sys.executable, self.upstream_dir / "scripts" / f"{name}.py", *args)

    def test_remux_and_web_encodes_preserve_clock(self):
        self.upstream_dir = Path(os.environ["FFMPEG_SKILL_DIR"])
        self.assertEqual(json.loads((self.upstream_dir / "package.json").read_text())["version"], "2.14.0")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source, delivered, poster = tmp / "master.mp4", tmp / "film.mp4", tmp / "poster.jpg"
            self.run_command("ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                             "testsrc2=size=640x360:rate=30", "-f", "lavfi", "-i",
                             "sine=frequency=440:sample_rate=48000", "-t", "2",
                             "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:v", "libx264",
                             "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", "-c:a", "aac", source)
            original = source.read_bytes()
            clock = {"fps": 30, "seconds": 2, "width": 640, "height": 360}
            self.upstream("probe", source, "--json")
            plan = json.loads(self.upstream("export", source, "--preset", "copy", "--no-scale",
                                           "--allow-long", "-o", delivered, "--dry-run", "--json"))
            self.assertTrue(plan["dry_run"])
            self.assertFalse(delivered.exists())
            self.upstream("export", source, "--preset", "copy", "--no-scale", "--allow-long",
                          "-o", delivered, "--json")
            probe = json.loads(self.upstream("probe", delivered, "--json"))
            self.assertTrue(media_check.verify(clock, probe)["ok"])
            check = json.loads(self.upstream("check", delivered, "--platform", "custom",
                                             "--lufs", "-16", "--tp", "-1.5", "--json"))
            self.assertTrue(check["ok"])
            self.upstream("look", delivered, "--tiles", "3x2", "--no-timecode", "-o", tmp / "sheet.png", "--json")
            self.assertTrue((tmp / "sheet.png").is_file())
            self.run_command("ffmpeg", "-v", "error", "-i", source, "-frames:v", "1", poster)
            self.run_command("bash", ROOT / "skills/motion-film-deliver/scripts/encode-web.sh",
                             delivered, poster, tmp / "web", "film", "320", "320")
            for extension in ("mp4", "webm"):
                output = tmp / "web" / f"film.{extension}"
                metadata = json.loads(self.upstream("probe", output, "--json"))
                self.assertTrue(media_check.verify(clock, metadata, 320, 180)["ok"])
                self.upstream("check", output, "--platform", "custom",
                              "--lufs", "-16", "--tp", "-1.5", "--json")
            self.assertEqual(source.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
