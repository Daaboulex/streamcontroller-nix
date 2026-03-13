# StreamController CLI — Test Plan and Results

## Test Plan

### Unit Tests (`test_core.py`)

Tests core modules with synthetic data, no external dependencies.

| Module | Test | Description |
|--------|------|-------------|
| `settings` | `TestLoadSaveJson` | JSON load/save, missing files, corrupt files, auto-create dirs |
| `config` | `TestConfig` | Data path resolution, dir creation, deck model constants |
| `settings` | `TestSettingsManager` | App settings CRUD, deck brightness (incl. clamping), screensaver, default pages, serial listing |
| `pages` | `TestPageManager` | Create, list, delete, rename, duplicate, export/import, inspect, backup/restore, case-insensitive lookup |
| `buttons` | `TestButtonManager` | Labels (set/clear/positions/fonts), images (set/clear/missing), actions (set/add/clear), coord normalization, multi-state, missing page errors |
| `plugins` | `TestPluginManager` | List plugins, get info, search, missing plugin handling |
| `devices` | `TestDeviceManager` | List known devices, device info, missing device, model listing |
| `output` | `TestOutputFormatter` | Human mode output, JSON mode output verification |

### E2E Tests (`test_full_e2e.py`)

Tests the Click CLI interface end-to-end using `CliRunner`.

| Group | Test | Description |
|-------|------|-------------|
| `TestPageCLI` | 10 tests | Create, list, delete, rename, duplicate, export/import, inspect — both human and JSON output |
| `TestButtonCLI` | 11 tests | Set/clear labels (all positions), set/clear images, set/add/clear actions, list buttons — both modes |
| `TestPluginCLI` | 5 tests | List, info, search plugins — both modes, error on missing |
| `TestDeviceCLI` | 3 tests | List devices (empty), models listing — both modes |
| `TestSettingsCLI` | 3 tests | Show empty, set/get roundtrip, brightness |
| `TestBackupCLI` | 2 tests | Create+list, restore cycle |
| `TestWorkflow` | 3 tests | Multi-step realistic workflows: full page setup + export/import, device settings, backup/restore |
| `TestCLISubprocess` | 4 tests | Subprocess execution with `_resolve_cli()`: help, page CRUD, models, settings roundtrip |

### Workflow Tests (within `TestWorkflow`)

1. **Full Page Setup**: Create page, configure multiple buttons (labels, images, actions), export, import to fresh data dir, verify all data survives
2. **Device Settings**: Create page, set brightness + default page for a device, verify via device list
3. **Backup/Restore**: Create pages with buttons, backup, delete all, restore, verify data integrity

## Test Results

```
============================= test session starts ==============================
platform linux -- Python 3.13.12, pytest-9.0.2, pluggy-1.6.0
collected 92 items

cli_anything/streamcontroller/tests/test_core.py::TestLoadSaveJson::test_load_corrupt_json PASSED
cli_anything/streamcontroller/tests/test_core.py::TestLoadSaveJson::test_load_missing_file PASSED
cli_anything/streamcontroller/tests/test_core.py::TestLoadSaveJson::test_save_and_load PASSED
cli_anything/streamcontroller/tests/test_core.py::TestLoadSaveJson::test_save_creates_dirs PASSED
cli_anything/streamcontroller/tests/test_core.py::TestConfig::test_deck_models PASSED
cli_anything/streamcontroller/tests/test_core.py::TestConfig::test_ensure_data_dirs PASSED
cli_anything/streamcontroller/tests/test_core.py::TestConfig::test_resolve_data_path_override PASSED
cli_anything/streamcontroller/tests/test_core.py::TestConfig::test_resolve_data_path_tilde PASSED
cli_anything/streamcontroller/tests/test_core.py::TestSettingsManager::test_app_settings_empty PASSED
cli_anything/streamcontroller/tests/test_core.py::TestSettingsManager::test_app_settings_roundtrip PASSED
cli_anything/streamcontroller/tests/test_core.py::TestSettingsManager::test_deck_brightness PASSED
cli_anything/streamcontroller/tests/test_core.py::TestSettingsManager::test_deck_brightness_clamped PASSED
cli_anything/streamcontroller/tests/test_core.py::TestSettingsManager::test_default_page PASSED
cli_anything/streamcontroller/tests/test_core.py::TestSettingsManager::test_get_set_app_setting PASSED
cli_anything/streamcontroller/tests/test_core.py::TestSettingsManager::test_list_known_serials PASSED
cli_anything/streamcontroller/tests/test_core.py::TestSettingsManager::test_screensaver PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPageManager::test_backup_and_restore PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPageManager::test_case_insensitive_lookup PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPageManager::test_create_and_list PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPageManager::test_create_duplicate_raises PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPageManager::test_delete PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPageManager::test_delete_missing_raises PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPageManager::test_duplicate PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPageManager::test_export_import PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPageManager::test_inspect PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPageManager::test_list_empty PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPageManager::test_rename PASSED
cli_anything/streamcontroller/tests/test_core.py::TestButtonManager::test_add_action PASSED
cli_anything/streamcontroller/tests/test_core.py::TestButtonManager::test_clear_actions PASSED
cli_anything/streamcontroller/tests/test_core.py::TestButtonManager::test_clear_image PASSED
cli_anything/streamcontroller/tests/test_core.py::TestButtonManager::test_clear_label PASSED
cli_anything/streamcontroller/tests/test_core.py::TestButtonManager::test_coord_formats PASSED
cli_anything/streamcontroller/tests/test_core.py::TestButtonManager::test_list_keys PASSED
cli_anything/streamcontroller/tests/test_core.py::TestButtonManager::test_missing_page_raises PASSED
cli_anything/streamcontroller/tests/test_core.py::TestButtonManager::test_multiple_states PASSED
cli_anything/streamcontroller/tests/test_core.py::TestButtonManager::test_set_action PASSED
cli_anything/streamcontroller/tests/test_core.py::TestButtonManager::test_set_image PASSED
cli_anything/streamcontroller/tests/test_core.py::TestButtonManager::test_set_image_missing_file PASSED
cli_anything/streamcontroller/tests/test_core.py::TestButtonManager::test_set_label PASSED
cli_anything/streamcontroller/tests/test_core.py::TestButtonManager::test_set_label_with_font PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPluginManager::test_get_missing_plugin PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPluginManager::test_get_plugin_info PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPluginManager::test_list_plugins PASSED
cli_anything/streamcontroller/tests/test_core.py::TestPluginManager::test_search PASSED
cli_anything/streamcontroller/tests/test_core.py::TestDeviceManager::test_get_device_info PASSED
cli_anything/streamcontroller/tests/test_core.py::TestDeviceManager::test_get_missing_device PASSED
cli_anything/streamcontroller/tests/test_core.py::TestDeviceManager::test_list_models PASSED
cli_anything/streamcontroller/tests/test_core.py::TestDeviceManager::test_list_no_devices PASSED
cli_anything/streamcontroller/tests/test_core.py::TestDeviceManager::test_list_with_settings PASSED
cli_anything/streamcontroller/tests/test_core.py::TestOutputFormatter::test_human_mode PASSED
cli_anything/streamcontroller/tests/test_core.py::TestOutputFormatter::test_json_mode PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPageCLI::test_page_create_and_list PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPageCLI::test_page_create_json PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPageCLI::test_page_delete PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPageCLI::test_page_delete_nonexistent PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPageCLI::test_page_duplicate PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPageCLI::test_page_export_import PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPageCLI::test_page_inspect PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPageCLI::test_page_list_empty PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPageCLI::test_page_list_json PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPageCLI::test_page_rename PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestButtonCLI::test_button_add_action PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestButtonCLI::test_button_clear_actions PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestButtonCLI::test_button_clear_image PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestButtonCLI::test_button_clear_label PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestButtonCLI::test_button_list_after_config PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestButtonCLI::test_button_list_empty PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestButtonCLI::test_button_set_action PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestButtonCLI::test_button_set_image PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestButtonCLI::test_button_set_label PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestButtonCLI::test_button_set_label_json PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestButtonCLI::test_button_set_label_positions PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPluginCLI::test_plugin_info PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPluginCLI::test_plugin_info_missing PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPluginCLI::test_plugin_list PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPluginCLI::test_plugin_list_json PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestPluginCLI::test_plugin_search PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestDeviceCLI::test_device_list_empty PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestDeviceCLI::test_device_models PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestDeviceCLI::test_device_models_json PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestSettingsCLI::test_settings_brightness PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestSettingsCLI::test_settings_set_and_get PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestSettingsCLI::test_settings_show_empty PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestBackupCLI::test_backup_create_and_list PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestBackupCLI::test_backup_restore PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestWorkflow::test_backup_restore_workflow PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestWorkflow::test_device_settings_workflow PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestWorkflow::test_full_page_setup_workflow PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestCLISubprocess::test_device_models PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestCLISubprocess::test_help PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestCLISubprocess::test_page_create_and_list PASSED
cli_anything/streamcontroller/tests/test_full_e2e.py::TestCLISubprocess::test_settings_roundtrip PASSED

============================== 92 passed in 0.25s ==============================
```

## Summary

- **92 tests total**: 51 unit tests + 41 E2E tests
- **100% pass rate**
- **Execution time**: 0.25 seconds
- **Coverage areas**: config, settings, pages, buttons, plugins, devices, output formatting, CLI interface, subprocess execution, multi-step workflows
