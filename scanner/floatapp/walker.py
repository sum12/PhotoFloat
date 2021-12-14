from TreeWalker import TreeWalker
from PhotoAlbum import Photo

import os
def wait_and_scan(albumpath, cachepath):
    apath = os.path.abspath(albumpath)
    cpath = os.path.abspath(cachepath)
    TreeWalker(apath, cpath)

def wait_and_compress(*args, **kwds):
    Photo(*args, **kwds)
