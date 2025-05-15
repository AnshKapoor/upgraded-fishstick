#!/usr/bin/env bash

sudo apt-get install build-essential cmake -y
WD=`pwd`
cd
wget https://github.com/libgit2/libgit2/archive/v0.25.1.tar.gz
tar xzf v0.25.1.tar.gz
rm v0.25.1.tar.gz
cd libgit2-0.25.1/
cmake .
make
sudo make install
cd ..
rm -rf libgit2-0.25.1
sudo ldconfig
cd "$WD"
