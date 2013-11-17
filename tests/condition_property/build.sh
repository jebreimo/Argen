#!/bin/sh
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
clapgen --test --hpp=hpp "$DIR/helptext.txt" && \
c++ -std=c++11 -stdlib=libc++ "$DIR/ParseArguments.cpp" -o ParseArguments
