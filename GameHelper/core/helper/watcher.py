# -*- encoding=utf8 -*-

from typing import Callable


class WatcherRegistry:

    actions = {}

    def add_watcher(self, key: str, func: Callable[[], None]) -> None:
        if key in self.actions or not callable(func):
            raise Exception("duplicate key:" + key+".")
        self.actions[key] = func
        return

    def remove_watcher(self, key: str) -> None:
        del self.actions[key]
        return

    def trigger(self, key: str, supplier: Callable[[], None]=None) -> None:
        _event_name = key
        if supplier and callable(supplier):
            _event_name = supplier()
            pass
        _func_ = self.actions.get(_event_name)
        if _func_:
            _func_()
            pass
        return

    pass


# class WatcherTask:


if __name__ == '__main__':
    _wr = WatcherRegistry()
    _wr.add_watcher("x", lambda: print("key:x"))
    _wr.trigger("x")
