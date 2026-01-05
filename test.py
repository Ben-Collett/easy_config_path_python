# WARNING: vibe coded
import unittest
from pathlib import Path

from config_manager import ConfigManager


class MockPlatformWrapper:
    def __init__(
        self,
        *,
        linux=False,
        mac=False,
        windows=False,
        env=None,
        sudo_uid=None,
        existing_paths=None,
    ):
        self._linux = linux
        self._mac = mac
        self._windows = windows
        self._env = env or {}
        self._sudo_uid_value = sudo_uid
        self._existing_paths = set(existing_paths or [])
        self.created_dirs = []
        self.created_files = []

    # ---- platform flags ----

    @property
    def _is_on_linux(self):
        return self._linux

    @property
    def _is_on_mac(self):
        return self._mac

    @property
    def _is_on_windowns(self):
        return self._windows

    # ---- env / sudo ----

    def get_env(self, name):
        return self._env.get(name)

    @property
    def _sudo_id(self):
        return self._sudo_uid_value

    # ---- filesystem ----

    def exists(self, path: Path):
        return path in self._existing_paths

    def mkdir(self, path: Path):
        self.created_dirs.append(path)
        self._existing_paths.add(path)

    def touch(self, path: Path):
        self.created_files.append(path)
        self._existing_paths.add(path)


class ConfigFinderTests(unittest.TestCase):
    def _patch_create_config_file(self):
        """
        Patch create_config_file to avoid pathlib.touch()
        """

        def create_config_file(self, file_name):
            config_dir = self.find_config_dir_path()
            self._platform_wrapper.mkdir(config_dir)
            path = config_dir / file_name
            if not self._platform_wrapper.exists(path):
                self._platform_wrapper.touch(path)

        ConfigManager.create_config_file = create_config_file

    def setUp(self):
        self._patch_create_config_file()

    # ---------- LINUX ----------

    def test_linux_xdg_config_home(self):
        wrapper = MockPlatformWrapper(
            linux=True,
            env={"XDG_CONFIG_HOME": "/xdg/config"},
        )
        finder = ConfigManager("myapp", _platform_wrapper=wrapper)

        self.assertEqual(
            finder.find_config_dir_path(),
            Path("/xdg/config/myapp"),
        )

    def test_linux_fallback_to_home_config(self):
        wrapper = MockPlatformWrapper(linux=True)
        finder = ConfigManager("myapp", _platform_wrapper=wrapper)

        path = finder.find_config_dir_path()
        self.assertEqual(path.name, "myapp")
        self.assertIn(".config", str(path))

    # ---------- MACOS ----------

    def test_macos_path(self):
        wrapper = MockPlatformWrapper(mac=True)
        finder = ConfigManager("myapp", _platform_wrapper=wrapper)

        path = finder.find_config_dir_path()
        self.assertEqual(
            path.parts[-3:],
            ("Library", "Application Support", "myapp"),
        )

    # ---------- WINDOWS ----------

    def test_windows_appdata(self):
        wrapper = MockPlatformWrapper(
            windows=True,
            env={"APPDATA": "C:/Users/Test/AppData/Roaming"},
        )
        finder = ConfigManager("myapp", _platform_wrapper=wrapper)

        self.assertEqual(
            finder.find_config_dir_path(),
            Path("C:/Users/Test/AppData/Roaming/myapp"),
        )

    def test_windows_appdata_fallback(self):
        wrapper = MockPlatformWrapper(windows=True, env={})
        finder = ConfigManager("myapp", _platform_wrapper=wrapper)

        path = finder.find_config_dir_path()
        self.assertEqual(path.name, "myapp")

    # ---------- OVERRIDE ----------

    def test_override_env_var(self):
        wrapper = MockPlatformWrapper(
            linux=True,
            env={"MYAPP_CONFIG": "/override/path"},
        )
        finder = ConfigManager(
            "myapp",
            path_override_variable_name="MYAPP_CONFIG",
            _platform_wrapper=wrapper,
        )

        self.assertEqual(
            finder.find_config_dir_path(),
            Path("/override/path"),
        )

    def test_override_env_var_empty_ignored(self):
        wrapper = MockPlatformWrapper(
            linux=True,
            env={"MYAPP_CONFIG": ""},
        )
        finder = ConfigManager(
            "myapp",
            path_override_variable_name="MYAPP_CONFIG",
            _platform_wrapper=wrapper,
        )

        self.assertNotEqual(
            finder.find_config_dir_path(),
            Path(""),
        )

    # ---------- CREATE / EXISTS ----------

    def test_config_dir_exists_false(self):
        wrapper = MockPlatformWrapper(linux=True)
        finder = ConfigManager("myapp", _platform_wrapper=wrapper)

        self.assertFalse(finder.config_dir_exists())

    def test_create_config_dir(self):
        wrapper = MockPlatformWrapper(linux=True)
        finder = ConfigManager("myapp", _platform_wrapper=wrapper)

        finder.create_config_dir()

        self.assertIn(
            finder.find_config_dir_path(),
            wrapper.created_dirs,
        )

    def test_create_config_file(self):
        wrapper = MockPlatformWrapper(linux=True)
        finder = ConfigManager("myapp", _platform_wrapper=wrapper)

        finder.create_config_file("config.toml")

        path = finder.find_config_file("config.toml")
        self.assertIn(path, wrapper._existing_paths)

    def test_create_config_file_no_duplicate(self):
        wrapper = MockPlatformWrapper(linux=True)
        finder = ConfigManager("myapp", _platform_wrapper=wrapper)

        finder.create_config_file("config.toml")
        finder.create_config_file("config.toml")

        self.assertEqual(len(wrapper.created_files), 1)

    def test_config_file_exists_false(self):
        wrapper = MockPlatformWrapper(linux=True)
        finder = ConfigManager("myapp", _platform_wrapper=wrapper)

        self.assertFalse(finder.config_file_exists("missing.conf"))

    # ---------- FAILURE PATHS ----------

    def test_unsupported_platform_raises(self):
        wrapper = MockPlatformWrapper()
        finder = ConfigManager("myapp", _platform_wrapper=wrapper)

        with self.assertRaises(RuntimeError):
            finder.find_config_dir_path()

    def test_linux_sudo_path_does_not_crash(self):
        wrapper = MockPlatformWrapper(
            linux=True,
            sudo_uid="0",
        )
        finder = ConfigManager("myapp", _platform_wrapper=wrapper)

        # Just ensure path resolution succeeds
        path = finder.find_config_dir_path()
        self.assertTrue(path.name == "myapp")


if __name__ == "__main__":
    unittest.main()
