import json
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

from capsule_maker.core import CapsuleError, import_capsule, inspect_capsule
from capsule_maker.release import create_release, import_release

FIXTURES = Path(__file__).resolve().parents[1] / "docs/capsules/psolver-periodic-v1"


def git(directory, *args):
    return subprocess.check_output(["git", "-C", str(directory), *args], text=True).strip()


@pytest.mark.skipif(shutil.which("git") is None, reason="Git needed to produce the release")
def test_poisson_psolver_release(tmp_path, monkeypatch):
    repo = tmp_path / "research"
    c1 = import_capsule(FIXTURES / "C1.zip", repo)
    c2 = import_capsule(FIXTURES / "C2.zip", tmp_path / "child")
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Example Researcher")
    git(repo, "config", "user.email", "researcher@example.invalid")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "Validate the 1D Poisson solver")
    shutil.copytree(tmp_path / "child", repo, dirs_exist_ok=True)
    git(repo, "add", ".")
    git(repo, "commit", "-m", "Extend the investigation with periodic PSolver")
    release = tmp_path / "release.zip"
    meta = create_release(repo, "main", release)
    with zipfile.ZipFile(release) as stream:
        bundle = tmp_path / "capsule.bundle"
        bundle.write_bytes(stream.read("capsule.bundle"))
        assert json.loads(stream.read("release.json")) == meta
        bad = tmp_path / "tampered.zip"
        with zipfile.ZipFile(bad, "w") as target:
            for name in stream.namelist():
                target.writestr(name, b"modified" if name == "README.md" else stream.read(name))

    clone = tmp_path / "cloned"
    git(tmp_path, "clone", "--branch", "main", str(bundle), str(clone))
    assert git(clone, "rev-parse", "HEAD") == meta["git_commit"]
    assert git(clone, "rev-list", "--count", "HEAD") == "2"
    assert json.loads(git(clone, "show", "HEAD^:manifest.json")) == c1
    monkeypatch.setenv("PATH", str(tmp_path / "no-git"))
    restored = tmp_path / "restored"
    assert import_release(release, restored) == meta
    assert inspect_capsule(restored) == c2
    for file in restored.rglob("*"):
        if file.is_file():
            assert file.read_bytes() == (clone / file.relative_to(restored)).read_bytes()
    with pytest.raises(CapsuleError, match="checksum"):
        import_release(bad, tmp_path / "rejected")
    assert not (tmp_path / "rejected").exists()


def test_release_rejects_unexpected_paths(tmp_path):
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("../outside", "unexpected")
    with pytest.raises(CapsuleError, match="Unexpected"):
        import_release(archive, tmp_path / "restored")
    assert not (tmp_path / "outside").exists()


@pytest.mark.parametrize("name", ["C1", "C2"])
def test_gallery_release_matches_original(tmp_path, name):
    original = import_capsule(FIXTURES / f"{name}.zip", tmp_path / "original")
    restored = tmp_path / "restored"
    import_release(FIXTURES / f"{name}-release.zip", restored)
    assert inspect_capsule(restored) == original
