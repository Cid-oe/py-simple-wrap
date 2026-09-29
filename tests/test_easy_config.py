import git
import pytest

from py_simple_package.src.py_simple.easy_config import (
    EasyConfigError,
    editorconfig_config,
)


def test_editorconfig_config_creates_file_at_current_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    editorconfig_config()

    config_file = tmp_path / ".editorconfig"
    assert config_file.exists()
    content = config_file.read_text(encoding="utf-8")
    assert "root = true" in content
    assert "indent_style = space" in content
    assert "indent_size = 4" in content


def test_editorconfig_config_does_not_overwrite_existing_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config_file = tmp_path / ".editorconfig"
    config_file.write_text("custom editorconfig\n", encoding="utf-8")

    editorconfig_config()

    assert config_file.read_text(encoding="utf-8") == "custom editorconfig\n"


def test_editorconfig_config_can_target_repository_root(tmp_path, monkeypatch):
    git.Repo.init(tmp_path)
    nested = tmp_path / "nested"
    nested.mkdir()
    monkeypatch.chdir(nested)

    editorconfig_config(at_root=False)

    config_file = tmp_path / ".editorconfig"
    assert config_file.exists()
    content = config_file.read_text(encoding="utf-8")
    assert "root = true" in content
    assert not (nested / ".editorconfig").exists()


def test_editorconfig_config_wraps_template_errors(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def missing_template(_package):
        raise FileNotFoundError("template missing")

    monkeypatch.setattr(
        "py_simple_package.src.py_simple.easy_config.files", missing_template
    )

    with pytest.raises(EasyConfigError, match="template missing"):
        editorconfig_config()


def test_editorconfig_config_wraps_git_errors(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(EasyConfigError):
        editorconfig_config(at_root=False)


def test_editorconfig_config_wraps_permission_errors(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def mock_open(*args, **kwargs):
        raise PermissionError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    with pytest.raises(EasyConfigError, match="Permission denied"):
        editorconfig_config()
