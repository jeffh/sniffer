import os
import collections

__all__ = ['get_files', 'file_validator', 'runnable', 'select_runnable']


def get_files(exts=('py',), dirname=None):
    if dirname is None:
        dirname = os.getcwd()
    if type(exts) is str:
        exts = [exts]
    exts = set(exts)
    for root, dirs, files in os.walk(dirname):
        for f in files:
            if f.split('.')[-1].lower() not in exts:
                continue
            yield os.path.join(root, f)


class Wrapper(object):
    def __init__(self, func, api_type):
        self.scent_api_type = api_type
        self.func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

        if not isinstance(func, collections.Callable):
            raise TypeError("Given object is not callable.")

    def __repr__(self):
        return "<%s %s>" % (self.scent_api_type, self.func.__name__)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def select_runnable(runnable):
    def decorator(func):
        if (not isinstance(func, Wrapper) or
            func.scent_api_type != 'file_validator'):
            raise TypeError(
                'select_runnable must be the outermost decorator on a '
                'file_validator'
            )
        func.runnable = runnable
        return func
    return decorator


def file_validator(func):
    return Wrapper(func, api_type='file_validator')


def runnable(func):
    return Wrapper(func, api_type='runnable')
