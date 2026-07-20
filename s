#!/usr/bin/env sh
uz ../../output/AP_"$1".zip asd
codium --wait asd/AP_"$1"_Spoiler.txt
# read -r _
rm -rf asd
