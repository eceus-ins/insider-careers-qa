"""Stub implementations of Insider framework decorators."""


def _make_class_namespace():
    class _Namespace:
        def __getattr__(self, _):
            def decorator(cls):
                return cls
            return decorator
    return _Namespace()


Owner = _make_class_namespace()
Priority = _make_class_namespace()
ProductTeam = _make_class_namespace()


def decorator_loader(*_args):
    def decorator(cls):
        return cls
    return decorator


def error_logger(func):
    return func


def CaseId(_ids):
    def decorator(cls):
        return cls
    return decorator
