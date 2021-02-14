from TreeWalker import TreeWalker
from floatapp.process import thumber_works
from PhotoAlbum import Photo

from time import sleep
import os
def wait_and_scan(albumpath, cachepath):
    def check(jb):
        return not jb._jb.ready() and jb.type == 'thumber'
    while len(list(filter(check, thumber_works))) > 0:
        sleep(5)
    apath = os.path.abspath(albumpath)
    cpath = os.path.abspath(cachepath)
    TreeWalker(apath, cpath)
    del thumber_works[:]

def wait_and_compress(*args, **kwds):
    def check(jb):
        return jb.type == 'scanner'
    while len(list(filter(check, thumber_works))) > 0:
        sleep(5)
    Photo(*args, **kwds)
