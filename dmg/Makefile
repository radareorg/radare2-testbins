all:
	hdiutil create ./src.dmg -srcfolder ./src/ -ov
	hdiutil create -encryption AES-128 ./src-aes-128.dmg -srcfolder ./src/ -ov
	hdiutil create -encryption AES-256 ./src-aes-256.dmg -srcfolder ./src/ -ov
	hdiutil create -format UDZO ./src-compressed.dmg -srcfolder ./src/ -ov
	hdiutil create -format UDRO ./src-ro.dmg -srcfolder ./src/ -ov
