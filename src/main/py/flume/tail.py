#!/usr/bin/python

import sys, os, glob, time
from stat import *

class WatchedFile:
  def __init__(self, path, inode, length):
    self.path = path
    self.inode = inode
    self.length = length
    self.fd = open(path, "r")
    self.newdata = True
    self.offset = 0
    self.data = bytearray("")
  def close(self):
    self.fd.close()

  def reset(self):
    self.close()
    self.fd = open(self.path, "r")
    self.offset = 0
    self.length = 0
    self.data = bytearray("")

  def __repr__(self):
    return "WatchedFile(path = %s, inode = %d, offset = %d, length = %d, newdata = '%s')"  \
        % (self.path, self.inode, self.offset, self.length, str(self.newdata))


def tail(pattern, processor):
  watchedFiles = {}
  while True:
    # file all items matching the pattern
    for path in glob.iglob(pattern):
      try:
        stat = os.stat(path)
        # only watch regular files
        if S_ISREG(stat.st_mode):
          if stat.st_ino in watchedFiles:
            # update length for files already being watched
            watchedFile = watchedFiles[stat.st_ino]
            if stat.st_size > watchedFile.length:
              watchedFile.newdata = True
            elif stat.st_size < watchedFile.length:
              watchedFile.reset()
              if stat.st_size > 0:
                watchedFile.newdata = True
            watchedFile.length = stat.st_size
            print watchedFile
          else:
            watchedFiles[stat.st_ino] = WatchedFile(path, stat.st_ino, stat.st_size)
      except OSError:
        # thrown by either os.stat or open
        pass
    for watchedFile in watchedFiles.values():
      if not watchedFile.newdata:



    for watchedFile in watchedFiles.values():
      if watchedFile.newdata:
        length = watchedFile.length - watchedFile.offset
        if length > 0:
          data = watchedFile.fd.read(length)
          if data:
            watchedFile.data += bytearray(data)
            watchedFile.offset += processor(watchedFile.path, watchedFile.data)
            watchedFile.newdata = False
    # remove files which no longer exist
    inodes = watchedFiles.keys()
    for inode in inodes:
      watchedFile = watchedFiles[inode]
      if not os.path.isfile(watchedFile.path):
        watchedFile.close()
        del watchedFiles[inode]
    try:
      time.sleep(1)
    except KeyboardInterrupt:
      sys.exit(0)
    #break

def line_processor(path, buff):
  offset = 1
  bytesRead = 0
  while offset > 0:
    offset = buff.find("\n")
    if offset > 0:
      offset += 1 # include \n
      line = buff[:offset]
      del buff[:offset]
      print "%s = '%s'" % (path, line.strip())
      bytesRead += offset
  return bytesRead
  
tail(sys.argv[1], line_processor)
