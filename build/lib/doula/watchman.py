from gevent.event import AsyncResult
from gevent.pool import Pool
from path import path
import gevent



class FSWatchman(object):
    """
    Watches a directory and signals when any file changes
    """
    def __init__(self, directory, pattern=None, exts=None, interval=0.5, poolsize=2):
        self.dir = path(directory)
        self.interval = interval
        self.mtimes = {}
        self.pattern = pattern
        self.exts = set()
        if exts:
            self.exts = set(exts)
        self.pool = Pool(poolsize)

    def files(self):
        for f in self.dir.walkfiles(self.pattern):
            if f.ext in self.exts:
                yield f

    def spawn_check(self):
        changed = AsyncResult()
        self.pool.spawn(self.check).link(changed)
        gevent.sleep(self.interval)
        return changed

    def check_mtimes(self):
        changed = self.spawn_check()
        while True:
            if changed.ready:
                res = changed.get()
                if res:
                    yield res
                changed = self.spawn_check()

    def scan_mtimes(self):
        f_mtimes = ((fp, fp.mtime) for fp in self.files())
        out = dict(f_mtimes)
        return out

    @staticmethod
    def what_changed(new, old):
        for fp, mtime in new.items():
            if fp not in old:
                yield fp, mtime,
                continue
            if mtime != old[fp]:
                yield fp, mtime,
    
    def check(self):
        """
        """
        if not self.mtimes:
            self.mtimes = self.scan_mtimes()
            return []

        while True:
            new_mtimes = self.scan_mtimes()
            if new_mtimes != self.mtimes:
                changed = self.what_changed(new_mtimes, self.mtimes.copy())
                self.mtimes = new_mtimes
                return changed
            gevent.sleep(self.interval)
        

        

