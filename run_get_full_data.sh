#!/bin/bash

POPS=( "ac" "al" "ap" "am" "ba" "ce" "es" "go" "ma" "mt"  "ms" "mg" "pa" "pb" "pr" "pe" "pi" "rj" "rn" "rs" "ro" "rr" "sc" "sp" "se" "to" "df" )
for test_type in "banda_bbr" "banda_cubic" "atraso_bi" "atraso_uni" "traceroute"
do
	for src in ${POPS[@]}
	do
		for dst in ${POPS[@]}
		do
			if [ $src != $dst ]
			then
				#echo "python3 get_full_data.py $src $dst $test_type"
				python3 get_full_data.py $src $dst $test_type
			fi
		done
	done
done
