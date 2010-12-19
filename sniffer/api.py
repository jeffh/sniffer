import os,sys

__all__ = ['get_files', 'file_validator', 'runnable']

def get_files(exts=('py',), dirname=None):
    if dirname is None:
        dirname = os.getcwd()
    if type(exts) is str:
        exts = [exts]
    exts = set(exts)
    for root,dirs,files in os.walk(dirname):
        for f in files:
            if f.split('.')[-1].lower() not in exts:
                continue
            yield os.path.join(root, f)

def file_validator(func):
    func.scent_api_type = 'file_validator'
    return func
    
def runnable(func):
    func.scent_api_type = 'runnable'
    return func