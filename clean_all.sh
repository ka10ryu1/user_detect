#!/bin/bash
#clean_all.sh
rm -rf ./*.npz ./result ./__pycache__/ ./*~ ./log.txt
rm -rf ./Lib/__pycache__/ ./Lib/*~ ./Lib/result
cd ./Tools;./clean_all.sh;cd ../
