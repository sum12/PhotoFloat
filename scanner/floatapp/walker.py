from TreeWalker import TreeWalker
from floatapp.process import thumber_works

from time import sleep
import os
def wait_and_scan(albumpath, cachepath):
    def check(jb):
        return not jb._jb.ready() and jb.type == 'thumber'
    while len(filter(check, thumber_works)) > 0:
        sleep(5)
    apath = os.path.abspath(albumpath)
    cpath = os.path.abspath(cachepath)
    TreeWalker(apath, cpath)
    del thumber_works[:]
