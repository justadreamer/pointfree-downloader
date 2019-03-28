## Work environment on Ubuntu:
```
sudo apt-get update
sudo apt-get install python3-pip
sudo pip3 install --upgrade pip
sudo pip3 install bs4
sudo pip3 install pydrive #for google drive
```

## Cookie format:
`cookies.txt` should be present in the working dir and have the first line:
```
# Netscape HTTP Cookie File
```

## Google Drive setup
- download `client_secrets.json` from Google Developer Console
- on the first attempt to upload you would be requested to authenticate
and the `credentials.json` file will be stored for subsequent use