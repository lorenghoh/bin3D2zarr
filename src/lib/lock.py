import os
import time
import tempfile
import fcntl
import errno

from contextlib import contextmanager


@contextmanager
def create_temp_file(file_name, dir=None):
    tmp_file = tempfile.NamedTemporaryFile(
        mode="w+",
        delete=False,
        prefix=f"{file_name}.",
        suffix=None, dir=dir
    )
    tmp_file.file.close()
    try:
        yield tmp_file.name
    finally:
        try:
            os.remove(tmp_file.name)
        except OSError as error:
            if error.errno == 2:
                pass
            else:
                raise


@contextmanager
def f_lock(file, flag=True, timeout=30):
    with open(file, "r+") as fd:
        try:
            st_time = time.time()

            while flag:
                if time.time() > (st_time + timeout):
                    err = "Read operation timed out; resource blocked"
                    raise IOError(err)

                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    flag = False
                except (OSError, IOError, BlockingIOError) as e:
                    if e.errno == errno.EWOULDBLOCK:
                        print("Resource blocked. Waiting...")
                        time.sleep(5)  # Wait and try again
                    else:
                        raise
            yield fd
        finally:  # Unlock on exit
            fcntl.flock(fd, fcntl.LOCK_UN)


@contextmanager
def AtomicFile(file, *args, **kwargs):
    fsync = kwargs.get("fsync", True)

    tmp_dir = os.path.dirname(os.path.abspath(file))
    with create_temp_file(file, dir=tmp_dir) as tmp:
        with open(tmp, *args, **kwargs) as f:
            try:
                yield f
            finally:
                if fsync:
                    f.flush()
                    os.fsync(f.fileno())
        os.rename(tmp, file)


@contextmanager
def LockedAtomicFile(file, *args, **kwargs):
    fsync = kwargs.get("fsync", True)

    with f_lock(file) as _:
        tmp_dir = os.path.dirname(os.path.abspath(file))
        with create_temp_file(file, dir=tmp_dir) as tmp:
            with open(tmp, *args, **kwargs) as f:
                try:
                    yield f
                finally:
                    if fsync:
                        f.flush()
                        os.fsync(f.fileno())
            os.rename(tmp, file)
