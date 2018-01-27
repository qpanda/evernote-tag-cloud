EvernoteTagCloud
================
A small Python script that generates a [tag cloud](https://en.wikipedia.org/wiki/Tag_cloud) of all tags a user has created in [Evernote](https://evernote.com/).

**EvernoteTagCloud** uses the [Evernote API](http://dev.evernote.com/doc/) to retrieve all tags and the number of notes each tag is associated with and then uses the [word_cloud](http://amueller.github.io/word_cloud/) library to generate a tag cloud.

## Prerequisites
In order to use **EvernoteTagCloud** you have to request a [DeveloperToken](https://www.evernote.com/api/DeveloperToken.action) for your Evernote account.

## Installation
To use **EvernoteTagCloud** download the ``evernote-tag-cloud`` Git repository from GitHub and use ``pip`` to install all dependencies.
  
    $ wget https://github.com/qpanda/evernote-tag-cloud/archive/master.zip
    $ unzip evernote-tag-cloud-master.zip
	$ cd evernote-tag-cloud-master
    $ pip install -r REQUIREMENTS.pip

**Note:** Installing [word_cloud](http://amueller.github.io/word_cloud/) using ``pip`` requires a compiler. Precompiled wheel packages for ``word_cloud`` are available, for more information please refer to the [README](https://github.com/amueller/word_cloud/blob/master/README.md) of the [word_cloud](https://github.com/amueller/word_cloud) project on GitHub.

## Using EvernoteTagCloud
Run ```EvernoteTagCloud.py -h``` to get usage information. All parameters except for ``evernoteAuthToken`` (Evernote Developer Token / API Key) are optional.

    $ EvernoteTagCloud.py -h
    EvernoteTagCloud.py 0.1.0
    usage: EvernoteTagCloud.py [-h] [--verbose] [--sandbox]
                               [--imageFile IMAGEFILE] [--imageSize IMAGESIZE]
                               [--maskFile MASKFILE] [--fontFile FONTFILE]
                               [--maxTags MAXTAGS]
                               [--horizontalTags HORIZONTALTAGS]
                               [--tagScaling TAGSCALING]
                               [--tagColorScheme {viridis,plasma,inferno,magma,Greys,Purples,Blues,Greens,Oranges,Reds,YlOrBr,YlOrRd,OrRd,PuRd,RdPu,BuPu,GnBu,PuBu,YlGnBu,PuBuGn,BuGn,YlGn,binary,gist_yarg,gist_gray,gray,bone,pink,spring,summer,autumn,winter,cool,Wistia,hot,afmhot,gist_heat,copper,PiYG,PRGn,BrBG,PuOr,RdGy,RdBu,RdYlBu,RdYlGn,Spectral,coolwarm,bwr,seismic,Pastel1,Pastel2,Paired,Accent,Dark2,Set1,Set2,Set3,tab10,tab20,tab20b,tab20c,flag,prism,ocean,gist_earth,terrain,gist_stern,gnuplot,gnuplot2,CMRmap,cubehelix,brg,hsv,gist_rainbow,rainbow,jet,nipy_spectral,gist_ncar}]
                               evernoteAuthToken
     
    Create Word Cloud from Evernote Tags
     
    positional arguments:
      evernoteAuthToken     authentication token for Evernote API
     
    optional arguments:
      -h, --help            show this help message and exit
      --verbose             print tag names and frequency
      --sandbox             connect to Evernote sandbox environment
      --imageFile IMAGEFILE
                            tag cloud file (default: EvernoteTagCloud.png)
      --imageSize IMAGESIZE
                            tag cloud size (default: 2048x1152)
      --maskFile MASKFILE   image mask file to use
      --fontFile FONTFILE   tag font to use
      --maxTags MAXTAGS     maximum number of tags (default: 300)
      --horizontalTags HORIZONTALTAGS
                            ratio of horizontal tags (default: 0.90)
      --tagScaling TAGSCALING
                            impact of tag frequency on tag size (default: 0.50)
      --tagColorScheme {viridis,plasma,inferno,magma,Greys,Purples,Blues,Greens,Oranges,Reds,YlOrBr,YlOrRd,OrRd,PuRd,RdPu,BuPu,GnBu,PuBu,YlGnBu,PuBuGn,BuGn,YlGn,binary,gist_yarg,gist_gray,gray,bone,pink,spring,summer,autumn,winter,cool,Wistia,hot,afmhot,gist_heat,copper,PiYG,PRGn,BrBG,PuOr,RdGy,RdBu,RdYlBu,RdYlGn,Spectral,coolwarm,bwr,seismic,Pastel1,Pastel2,Paired,Accent,Dark2,Set1,Set2,Set3,tab10,tab20,tab20b,tab20c,flag,prism,ocean,gist_earth,terrain,gist_stern,gnuplot,gnuplot2,CMRmap,cubehelix,brg,hsv,gist_rainbow,rainbow,jet,nipy_spectral,gist_ncar}
                            tag color scheme (default: Blues)TODO

The [masks/](masks/) folder contains Evernote Logo masks that can be used to create a tag cloud in the shape of the iconic Evernote elephant logo.

## Examples
[examples/EvernoteTagCloud.png](examples/EvernoteTagCloud.png) is an example tag cloud created from an Evernote account with 900+ notes and 500+ tags.

![EvernoteTagCloudExample](examples/EvernoteTagCloud.png)

The tag cloud has been created by executing the following command.

    $ EvernoteTagCloud.py --imageFile examples/EvernoteTagCloud.png --maxTags 999 <evernoteAuthToken>

[examples/EvernoteTagCloud-LogoMask.png](examples/EvernoteTagCloud-LogoMask.png) is an example tag cloud created from an Evernote account with 900+ notes and 500+ tags using the iconic Evernote elephant
logo as the mask.

![EvernoteTagCloud-LogoMask](examples/EvernoteTagCloud-LogoMask.png) 

The tag cloud has been created by executing the following command.

    $ EvernoteTagCloud.py --imageFile examples/EvernoteTagCloud-LogoMask.png --maskFile masks/EvernoteLogoMask-2048x2391.png --maxTags 999  <evernoteAuthToken>

## License
EvernoteTagCloud is licensed under the MIT license.