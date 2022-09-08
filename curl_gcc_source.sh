#!/bin/sh
# download and decompress the GCC source code from
# https://people.csail.mit.edu/smcc/projects/single-file-programs/ using curl
# and save in the current directory
#
# note: requires curl and bzip2

curl -o gcc.c.bz2 https://people.csail.mit.edu/smcc/projects/single-file-programs/gcc.c.bz2
bzip2 -d gcc.c.bz2


