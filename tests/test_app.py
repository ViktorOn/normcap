import logging
import sys
from pathlib import Path

import pytest
import toml
from PySide6 import QtWidgets

import normcap
from normcap import app, utils

logger = logging.getLogger(__name__)


def test_version():
    with Path("pyproject.toml").open(encoding="utf8") as toml_file:
        pyproject_toml = toml.load(toml_file)

    briefcase_version = pyproject_toml["tool"]["briefcase"]["version"]
    poetry_version = pyproject_toml["tool"]["poetry"]["version"]
    normcap_version = normcap.__version__
    assert briefcase_version == poetry_version == normcap_version


def test_get_args(monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(
            sys,
            "argv",
            [sys.argv[0], "--language", "eng", "deu", "--mode=raw", "--tray=True"],
        )
        args = app._get_args()

    assert args.mode == "raw"
    assert args.language == ["eng", "deu"]
    assert args.tray is True


def test_get_args_version(monkeypatch, capsys):
    with monkeypatch.context() as m:
        m.setattr(sys, "argv", [sys.argv[0], "--version"])
        with pytest.raises(SystemExit) as exc:
            _ = app._get_args()

    output = capsys.readouterr()
    assert normcap.__version__ in output.out
    assert not output.err
    assert exc.value.code == 0


@pytest.mark.parametrize(
    ("level", "result"),
    [
        ("info", {"level": logging.INFO, "has_hook": True}),
        ("debug", {"level": logging.DEBUG, "has_hook": False}),
    ],
)
def test_prepare_logging(monkeypatch, level, result, caplog):
    with monkeypatch.context() as m:
        m.setattr(sys, "argv", [sys.argv[0], "--verbosity", level])
        args = app._get_args()

    app._prepare_logging(getattr(args, "verbosity", "ERROR"))
    logger = logging.getLogger("normcap")

    assert logger.level == result["level"]
    assert (sys.excepthook == utils.hook_exceptions) is result["has_hook"]


def test_get_application():
    qt_app = app._get_application()
    assert isinstance(qt_app, QtWidgets.QApplication)
    assert not qt_app.quitOnLastWindowClosed()


def test_prepare_env():
    app._prepare_envs()
