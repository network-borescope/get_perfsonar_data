#!/bin/bash

MYSELF="run_get_full_data.sh"

if [ $# == 0 ]
then
	START_DATE=`date -d '-1 day' '+%Y%m%d'`
	END_DATE=${START_DATE}

else
	if [ $# == 2 ]
	then
		START_DATE=$1
		END_DATE=$2

	else
		echo "Erro $MYSELF: Must have 2 or 0 parameters"
		echo "To get data between start-date and end-date(inclusive): bash $MYSELF <start-date> <end-date>"
		echo "To get yesterday data: bash $MYSELF"
		exit 1
	fi
fi

#echo ${START_DATE}
#echo ${END_DATE}

echo "Getting Banda BBR data"
python3 get_full_data.py --time-start ${START_DATE} --time-end ${END_DATE} --test-type banda_bbr --event-type throughput &


echo "Getting Banda CUBIC data"
python3 get_full_data.py --time-start ${START_DATE} --time-end ${END_DATE} --test-type banda_cubic --event-type throughput &


echo "Getting Atraso e Perda de pacotes data"
python3 get_full_data.py --time-start ${START_DATE} --time-end ${END_DATE} --test-type atraso_bidir --event-type histogram-rtt &
python3 get_full_data.py --time-start ${START_DATE} --time-end ${END_DATE} --test-type atraso_bidir --event-type histogram-ttl-reverse &
python3 get_full_data.py --time-start ${START_DATE} --time-end ${END_DATE} --test-type atraso_bidir --event-type packet-loss-rate-bidir &


echo "Getting Atraso unidirecional data"
python3 get_full_data.py --time-start ${START_DATE} --time-end ${END_DATE} --test-type atraso_unidir --event-type histogram-owdelay &
python3 get_full_data.py --time-start ${START_DATE} --time-end ${END_DATE} --test-type atraso_unidir --event-type histogram-ttl &
python3 get_full_data.py --time-start ${START_DATE} --time-end ${END_DATE} --test-type atraso_unidir --event-type packet-loss-rate &


echo "Getting Traceroute data"
python3 get_full_data.py --time-start ${START_DATE} --time-end ${END_DATE} --test-type traceroute --event-type packet-trace &


echo "Getting Http data"
python3 get_full_data.py --time-start ${START_DATE} --time-end ${END_DATE} --test-type http &


echo "Getting Dns data"
python3 get_full_data.py --time-start ${START_DATE} --time-end ${END_DATE} --test-type dns &
