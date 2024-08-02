# AllImagesCatDownloader
All images downloaded from a Wikimedia Commons category, including sub-categories.

## Introduction
This is a script/tool to download all the images from a Wikimedia Commons category including sub-categories. The input is a Wikimedia Commons category, alternatively a Wikidata item can be used as an input and the Wikidata item will be search for Wikimedia Commons site link. Also downloaded is Author and Licence information which is stored as a json file with the same name as the file it applies to.

## Prerequisite

install the SPARQLWrapper library
```
pip install SPARQLWrapper
```

## Running
The begining of the script contains a `cookie` variable which should be set from a http request header, for a brower which is logged into https://commons-query.wikimedia.org/sparql , it will look something like
```
GeoIP=GB:ENG:location:32.31:-3.53:v3; wcqsSession=eyJ0eXdddiJKV1QiLCdddGciOiJIUzI1NiJ9.eyJleHAiOjEdddI2MzQzMzUsInVzZddddYW1lIoiU2ltb25jMTExIn0.DMN78XNNdddaOX3M_GQU2vxp5f_QddEE-rdaaBQa9DA; wcqsOauth=1c9f37de63599596a7a83a7e3916117.33ec0dd78230bb0b12311636c6323222de950
```
There are [guides](https://support.pentest-tools.com/en/scans-tools/how-to-get-the-session-cookie#:~:text=Go%20to%20the%20'Headers'%20Tab,and%20see%20the%20Cookie%20header) if you are unsure.

The `basefldr` variable should be set to your project folder e.g Linux `/home/yourname/yourprojectname/`, Windows `c:\projects\yourname\yourprojectname\` and is where everything will download to.

The `cat` variable should be set to the category you want to download e.g 'Bucephala clangula' will download the Commons category for this species of bird.

The optional `WDitem` variable can be left empty, if you provide a WikiData item id e.g Q190342 , the Wikidata items's site-link for commons will be used as a starting category.

The `limit` variable is defaulted to 20 images downloaded, and should be changed as needed, e.g the Bucephala clangula (Common Goldeneye) has around 350 images, so you would increase the limit if you needed all of them.

Now run the script.
```
python3 py.py
```

## Feedback 

[User_talk:Simonc8](https://www.wikidata.org/wiki/User_talk:Simonc8)
