#!/bin/sh

astyle -A3 -s2 --keep-one-line-blocks --pad-paren-in --unpad-paren --pad-oper --suffix=none ../src/*.cxx ../src/*.h

etags ../src/*.h ../src/*.cxx
