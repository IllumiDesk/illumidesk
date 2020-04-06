import inspect

from jupyterhub import crypto

from pytest import fixture


_db = None


@fixture
def db():
    """Get a db session"""
    global _db
    if _db is None:
        _db = orm.new_session_factory('sqlite:///:memory:')()
        user = orm.User(name=getuser())
        _db.add(user)
        _db.commit()
    return _db