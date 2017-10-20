#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
build: compile and pack kagami package

author(s): Albert
origin: 05-19-2017

"""


import os, compileall, shutil


def compl(sdir, ddir):
    if not os.path.isdir(sdir):
        raise IOError('Source dir [%s] not exists' % sdir)

    if os.path.isdir(ddir):
        # should manual remove, just for safety...
        raise IOError('Destination dir [%s] already exists' % sdir)

    print 'Compiling files ...'
    compileall.compile_dir(sdir, force = True)
    print ''

    print 'Moving files to destination ...'
    sfiles = [(root, name) for root, dirs, files in os.walk(sdir) for name in files + dirs if name.endswith('.pyc')]
    for sd, fn in sfiles:
        dd = os.path.join(ddir, sd[len(sdir.rstrip(os.sep))+1:])
        if not os.path.isdir(dd):
            print 'Destination dir [%s] not exists, created' % dd
            os.makedirs(dd)
        print 'Moving ' + os.path.join(sd, fn) + ' -> ' + dd + ' ...'
        shutil.move(*map(lambda x: os.path.join(x, fn), (sd, dd)))
    print ''

def pack(sdir, folder, vers):
    if not os.path.isdir(sdir):
        raise IOError('Source dir [%s] not exists' % sdir)

    print 'Packing files ...'
    os.chdir(sdir)
    pkgf = 'libkagami_' + vers + '.zlib'
    os.system('zip -vrm0 %s %s' % (pkgf, folder))
    if not os.path.isfile(pkgf):
        raise RuntimeError('Compression failed')
    print ''


# main
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('src', help = 'source path')
    parser.add_argument('-d', '--dst', help = 'destination path', default = 'dist')
    parser.add_argument('-v', '--ver', help = 'version string', default = None)
    parser.add_argument('-p', '--pkg', help = 'package name', default = 'kagami')
    args = parser.parse_args()

    compl(args.src, os.path.join(args.dst, args.pkg))
    pack(args.dst, args.pkg,
         args.ver if args.ver is not None else __import__(args.src.rstrip(os.sep)).__version__)
    print 'Done'

