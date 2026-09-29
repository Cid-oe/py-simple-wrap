import git
import pytest

from py_simple_package.src.py_simple.easy_config import (
    EasyConfigError,
    pre_commit_config,
)


def test_pre_commit_config_creates_file_at_current_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    pre_commit_config()

    config_file = tmp_path / ".pre-commit-config.yaml"
    assert config_file.exists()
    content = config_file.read_text(encoding="utf-8")
    assert "repos:" in content
    assert "pre-commit-hooks" in content
    assert "ruff" in content


def test_pre_commit_config_does_not_overwrite_existing_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config_file = tmp_path / ".pre-commit-config.yaml"
    config_file.write_text("custom pre-commit\n", encoding="utf-8")

    pre_commit_config()

    assert config_file.read_text(encoding="utf-8") == "custom pre-commit\n"


def test_pre_commit_config_can_target_repository_root(tmp_path, monkeypatch):
    git.Repo.init(tmp_path)
    nested = tmp_path / "nested"
    nested.mkdir()
    monkeypatch.chdir(nested)

    pre_commit_config(at_root=False)

    config_file = tmp_path / ".pre-commit-config.yaml"
    assert config_file.exists()
    content = config_file.read_text(encoding="utf-8")
    assert "repos:" in content
    assert not (nested / ".pre-commit-config.yaml").exists()


def test_pre_commit_config_wraps_template_errors(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def missing_template(_package):
        raise FileNotFoundError("template missing")

    monkeypatch.setattr(
        "py_simple_package.src.py_simple.easy_config.files", missing_template
    )

    with pytest.raises(EasyConfigError, match="template missing"):
        pre_commit_config()


def test_pre_commit_config_wraps_git_errors(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(EasyConfigError):
        pre_commit_config(at_root=False)


def test_pre_commit_config_wraps_permission_errors(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def mock_open(*args, **kwargs):
        raise PermissionError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    with pytest.raises(EasyConfigError, match="Permission denied"):
        pre_commit_config()
