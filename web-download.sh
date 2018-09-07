rm -r www.pointfree.co

wget -c --recursive -l 1 --load-cookies pointfree-cookies.txt https://www.pointfree.co/

rm pointfree.zip

zip -r pointfree.zip  www.pointfree.co

../google-drive-wrapper/upload.sh pointfree.zip PointFree
