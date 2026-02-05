import os
import tempfile

from aion_engine.session import Session


def test_create_session():
    with tempfile.TemporaryDirectory() as tmpdir:
        session = Session.create(tmpdir, "实验室测试")
        assert session.title == "实验室测试"
        assert os.path.exists(session.session_dir)


def test_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        session = Session.create(tmpdir, "测试")
        session.advance("点燃", {"fire": True})
        session.save()

        loaded = Session.load(session.session_dir)
        assert loaded.title == "测试"
