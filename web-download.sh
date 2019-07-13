# delete old stuff
rm -r www.pointfree.co
rm pointfree.zip

# download new stuff
wget -c --recursive -l 1 --load-cookies pointfree-cookies.txt https://www.pointfree.co/

# update the links
cd www.pointfree.co
for f in `ls episodes/*`; do mv $f $f.html; done
cat index.html | sed 's!/episodes/\([^"]*\)!episodes/\1.html!g' > index1.html
mv index1.html index.html
cd -

# zip 
zip -r pointfree.zip  www.pointfree.co

# upload
../google-drive-wrapper/upload.sh pointfree.zip Screencasts/PointFree

