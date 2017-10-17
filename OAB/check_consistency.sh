#!/bin/bash

filename_nok="30001-40000_nok.csv"
filename_ok="30001-40000.csv"

# for line in `cat $filename_ok`;do
while read -r line
do
    # echo $line
    oab_code=`echo $line | awk 'BEGIN { FS="," } { print $1}'`
    # echo $oab_code
    found=$(echo `grep -o "$oab_code" $filename_ok | wc -l`)
    # echo $found
    if [[ $found == 2 ]]; then
        echo $oab_code
    fi
done < "$filename_ok"
