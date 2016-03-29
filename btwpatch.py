#!/usr/bin/env python
##
## Copyright 2016 John J Foerch. All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##
##    1. Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##
##    2. Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in
##       the documentation and/or other materials provided with the
##       distribution.
##
## THIS SOFTWARE IS PROVIDED BY JOHN J FOERCH ''AS IS'' AND ANY EXPRESS OR
## IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL JOHN J FOERCH OR CONTRIBUTORS BE LIABLE
## FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
## CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
## SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
## BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##

import os, sys
import argparse
import json
import shutil
import subprocess
import tempfile

def copytree (src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def mkdir_p (path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def create_destination_directory (dest):
    if os.path.exists(dest):
        print "[status] {} already exists".format(dest)
    else:
        mkdir_p(dest)
        print "[status] created {}".format(dest)

def do_json (dst, dstbasename, orig, origbasename):
    origjsonpath = os.path.join(orig, origbasename + ".json")
    if not os.path.exists(origjsonpath):
        print "[error] {} not found".format(origjsonpath)
        exit()
    origjsonfile = open(origjsonpath)
    origjson = json.load(origjsonfile)
    origjson['id'] = dstbasename
    origjson.pop('assets', None)
    origjson.pop('assetIndex', None)
    origjson.pop('downloads', None)
    dstjsonpath = os.path.join(dst, dstbasename + ".json")
    dstjsonfile = open(dstjsonpath, 'w')
    json.dump(origjson, dstjsonfile, indent=2)
    print "[status] wrote {}".format(dstjsonfile)

def build_btw (dst, dstbasename, orig, origbasename):
    scratch = tempfile.mkdtemp(prefix="btwpatch-")
    print "[status] created {}".format(scratch)
    buildpath = os.path.join(scratch, "MINECRAFT-JAR")
    os.makedirs(buildpath)
    print "[status] created {}".format(buildpath)
    origjar = os.path.join(orig, origbasename + ".jar")
    subprocess.call(["unzip", origjar, "-d", buildpath])
    metainfpath = os.path.join(buildpath, "META-INF")
    shutil.rmtree(metainfpath)
    subprocess.call(["unzip", "-uo", btwzip, "-d", scratch, "MINECRAFT-JAR/*"])
    jarpath = os.path.join(scratch, dstbasename + ".jar")
    dstjarpath = os.path.abspath(os.path.join(dst, dstbasename + ".jar"))
    subprocess.call(["zip", "-R", jarpath, "*"], cwd=buildpath)
    shutil.move(jarpath, dstjarpath)
    print "[status] installed {}".format(dstjarpath)
    shutil.rmtree(scratch)
    print "[status] deleted {}".format(scratch)

##
## Main
##

cmdline_parser = argparse.ArgumentParser()
cmdline_parser.add_argument('source', help="A Minecraft version directory to clone for BTW")
cmdline_parser.add_argument('btwzip', help="Better Than Wolves zip file")
cmdline_parser.add_argument('dest', help="Directory in which to install Better Than Wolves")
args = cmdline_parser.parse_args()

orig = os.path.normpath(args.source)
btwzip = args.btwzip
dest = os.path.normpath(args.dest)

destbasename = os.path.basename(dest)
origbasename = os.path.basename(orig)

create_destination_directory(dest)
do_json(dest, destbasename, orig, origbasename)
build_btw(dest, destbasename, orig, origbasename)
