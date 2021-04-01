# installing dependencies, cloning repo (can be used to prepare a boot disk image)
sudo apt-get update
sudo apt-get install -y git
sudo apt-get install -y youtube-dl
sudo apt-get install -y python3-pip
pip3 install requests
pip3 install bs4
pip3 install pydrive
git clone https://github.com/justadreamer/pointfree-downloader

# after clone (this and below blocks can be rerun on a disk image after it has been prepared)
cd pointfree-downloader
git clean -fdx
git pull 
for f in `gsutil ls gs://secure-configs`; do gsutil cp $f .; done

#actual grabbing
python3 grab.py
python3 grab.py --swift-talk
