install:
	install -pm755 toggle_input.sh /usr/local/bin/toggle_input.sh
	install -pm755 toggleinputd.py /usr/local/bin/toggleinputd.py
	install -pm644 touchscreen.desktop /usr/share/applications/touchscreen.desktop 
	install -pm644 toggleinputd.service /etc/systemd/system/toggleinputd.service
	systemctl enable --now toggleinputd.service
