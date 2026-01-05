# config_manager

A small, vendor-friendly utility module for locating and managing
configuration directories and files in a cross-platform way.

This repository is primarily intended for **personal use** to speed up
development across multiple projects, but it is published so others are
free to copy, modify, and reuse it as they see fit.

---

## Project scope and expectations

- This project is **not actively maintained as a general-purpose library**
- Issues and pull requests are welcome, but may not be accepted unless they
  align with my own use cases
- If you need additional features or different behavior, you are encouraged
  to **fork this repository** and adapt it to your needs rather than rely on
  upstream changes

Vendoring this code directly into your project is the intended usage.

---

## Licensing

This project is licensed under the **BSD Zero-Clause (BSD-0) License**.

This means you are free to:
- Copy the code
- Modify it
- Vendor it into your project
- Re-license it under any license you choose
- Use it commercially
- Do all of the above **without attribution**

If you submit a pull request, all contributed code must be licensed under
BSD-0 as well.

---

## Installation / Usage

It is recommended that you **copy the `config_manager/` directory directly**
into your project rather than treating this as an external dependency.

---

## API Reference

### Construction

You typically only need a single `ConfigManager` instance, which can be
stored in a global or application-level variable.

```python
from config_manager import ConfigManager

PROJECT_NAME = "project"
ENV_VARIABLE_OVERRIDE = "MYAPP_CONFIG"

manager = ConfigManager(
    PROJECT_NAME,
    path_override_variable_name=ENV_VARIABLE_OVERRIDE,
)

```

The path_override_variable_name is optional but if set it allows the user to set an environment variable with that path to search there instead of the normal config directory location on the platform.

## Methods

Returns the config directory path based on platform/environment settings, returns a pathlib Path

```python
manager.find_config_dir_path()
```
Returns the config file path based on platform/environment settings, returns a pathlib Path
```python
manager.find_config_file_path("project.yaml")
```

Returns True if a config directory/folder exist on the current platform/enviorment variable settings
```python 
manager.config_dir_exists()
```

Returns True if a config file exist on the current platform/enviorment variable settings
```python
manager.config_file_exists("config.toml") 
```

Creates a config directory/folder using the current platform/enviorment variable settings, will create parent directories as needed.
```python
manager.create_config_dir()
```
Creates a config file using the current platform/enviorment variable settings, will create parent directories as needed.
```python
manager.create_config_file("config.json")
```

# LICENSE
[BSD Zero](LICENSE)


