#!/bin/sh
# toggle touchscreen with toggleinputd.py

if [ $(cat /tmp/touchscreen_grabbed) = "0" ]
then
	echo -n 'grab' > /tmp/touchscreen.fifo
elif [ $(cat /tmp/touchscreen_grabbed) = "1" ]
then 
	echo -n 'ungrab' > /tmp/touchscreen.fifo
fi
