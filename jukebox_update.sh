#!/bin/sh
# Simple RSS Jukebox Generator
# Author: mikka [mika.hellmann@gmail.com]
# Modified by Snappy46 [levesque.marcel@gmail.com]


TMP="/tmp/rss.list"
TMP2="/tmp/genrerss.list"
SORTEDTMP="/tmp/sortedrss.list"
INSTALL="0"

if [ -f /usr/local/etc/srjg/filter.conf ];
then
  FILTER=`cat /usr/local/etc/srjg/filter.conf`
else
  FILTER="xxooxxooip"
fi

usage()
{
cat << EOF
usage: $0 options

This script creates a Movie / TV Episode on a specify directory. 
All the movies/TV Episode must be in their own directory.

OPTIONS:
   -h      Show this message
   -i      This indicate the mode install and should only be used the first time 
           you run this command on a given directory. (Optional)
   -p      This indicate the jukebox directory ex: -p /HDD/movies/
   -f      This is the filter option, movies filename containing this/those
           string(s) will be skipped.  Strings must be separated by a ","
           (Optional) ex: -f sample,trailer 
NOTES:  If any of the arguments have spaces in them they must be surrounded by quotes: ""

    The following options are only required if you decide to use the script built-in
    capability to create automatically Moviesheets/Thumbnails. I suggest you consult this
    website: http://playon.unixstorm.org/imdb.php if you want to know more about 
    the various options.

   -m      Generate moviesheets and/or thumbnails (Required)
           Possible values are: "moviesheet", "poster", "both"
   -b	   If set to "yes" random backdrop will be used (Optional)
   -c      Generate box cases (Optional)
           Possible values are: "bdrip", "bluray", "dtheater", "dvd", "generic", 
           "hddvd", "hdtv", "itunes" (Default: generic)
   -s      If set to "tmdb" random poster from themoviedb.org will be used
           Otherwise default poster from IMDB will be used (Optional)
   -t      If set to "real" time will represented in HH:MM format
           If set to "hours" time will be represented in HHh MMm format
           Otherwise time will be represented in minutes (works only with mode 
           set to moviesheet)(Optional)                
EOF
exit 1
}

while getopts p:f:m:b:c:s:t:hi OPTION 
do
  case $OPTION in
     p)
       MOVIESPATH=$OPTARG
       ;;
     f)
       FILTER=$OPTARG
       ;;
     m)
       MODE=$OPTARG
       ;;
     b)
       BACKDROP=$OPTARG
       ;;
     c)
       COVER=$OPTARG
       ;;
     s)
       SOURCE=$OPTARG
       ;;
     t)
       TIMESTYLE=$OPTARG
       ;;
     i)
       INSTALL="1"
       ;;
     h)
       usage
       ;;
   esac
done

if [ -z "$MOVIESPATH" ]
then
  echo -e "A directory must be specified using -p option."
  usage
  exit 1
fi  


movies_processing()
{
# Replace the comma in FILTER to pipes |
FILTER=`echo $FILTER | sed 's/,/|/ g'`

# Find and sort the movies based on selection
echo "Searching for movies.."
find "$MOVIESPATH" | egrep -i '\.(asf|avi|dat|divx|flv|img|iso|m1v|m2p|m2t|m2ts|m2v|m4v|mkv|mov|mp4|mpg|mts|qt|rm|rmp4|rmvb|tp|trp|ts|vob|wmv)$' | egrep -iv "$FILTER" > $TMP


echo "Sorting movies.."

sed 's:\(.*/\)\([^/]*\):\2 \1\2:' $TMP | sort | sed 's:[^/]* ::' > $SORTEDTMP
echo "Found `sed -n '$=' $SORTEDTMP` movies"
}


# Creates moviesheets by calling IMDB API
genmoviesheet()
{
echo "Generating moviesheets/thumbnails.."
API="http://playon.unixstorm.org/IMDB/imdb.php?"

grep "$MOVIESPATH" "$SORTEDTMP" | while read LINE
do
        MOVIEPATH="${LINE%/*}"  # Shell builtins instead of dirname
        MOVIEFILE="${LINE##*/}" # Shell builtins instead of basename
        MOVIENAME="${MOVIEFILE%.*}"  # Strip off .ext       

        # Initialize defaults, replace later
        MOVIETITLE="$MOVIENAME"

        if [ -e "$MOVIEPATH/MovieInfo.nfo" ];
          then
            MOVIEINFO="$MOVIEPATH/MovieInfo.nfo"
            MOVIETITLE=`grep "<title>.*<.title>" "$MOVIEINFO" | sed -e "s/^.*<title/<title/" | cut -f2 -d">"| cut -f1 -d"<"`
        fi

        if [ -e "$MOVIEPATH/$MOVIENAME.nfo" ];
          then
            MOVIEINFO="$MOVIEPATH/$MOVIENAME.nfo"
            MOVIETITLE=`grep "<title>.*<.title>" "$MOVIEINFO" | sed -e "s/^.*<title/<title/" | cut -f2 -d">"| cut -f1 -d"<"`
        fi

        MOVIETITLE=`echo $MOVIETITLE | sed 's/ /+/ g'`

        if ( [ $MODE = "poster" ] || [ $MODE = "both" ] ) &&  [ ! -e "$MOVIEPATH/folder.jpg" ] && [ ! -e "$MOVIEPATH/${MOVIENAME}.jpg" ] 
        then
          wget "${API}name=$MOVIETITLE&mode=poster" -O "$MOVIEPATH/${MOVIENAME}.jpg" ;
        fi


        if ( [ $MODE = "moviesheet" ] || [ $MODE = "both" ] ) &&  [ ! -e "$MOVIEPATH/about.jpg" ] && [ ! -e "$MOVIEPATH/${MOVIENAME}_sheet.jpg" ] && [ ! -e "$MOVIEPATH/0001.jpg" ] 
        then
           wget "${API}name=$MOVIETITLE&mode=moviesheet&backdrop=$BACKDROP&box=$COVER&source=$SOURCE&time=$TIMESTYLE" -O "$MOVIEPATH/${MOVIENAME}_sheet.jpg";
        fi
done
echo "Done generating moviesheets/thumbnails"
}


# creates the jukebox.xml file.
# Remember to change title to mainheading
genjukexml()
{
echo "Generating RSS header.."
echo -e '﻿<?xml version="1.0" encoding="UTF-8"?>
<Jukebox>
  <Path>'$MOVIESPATH'</Path>
  <Temp>/tmp/</Temp>
  <Version>5.0</Version>
  <Category>
    <background>/usr/local/etc/srjg/background.bmp</background>
    <title>'$TITLE'</title>
    <link>Jukebox.rss</link>
    <MovieInfo_Template>MovieInfo_Template.rss</MovieInfo_Template>
    <MovieInfo_RSS>MovieInfo.rss</MovieInfo_RSS>
    </Category>' > $RSS
	
echo "Indexing movies.."

grep "$MOVIESPATH" "$SORTEDTMP" | while read LINE
do
        MOVIEPATH="${LINE%/*}"  # Shell builtins instead of dirname
        MOVIEFILE="${LINE##*/}" # Shell builtins instead of basename
        MOVIENAME="${MOVIEFILE%.*}"  # Strip off .ext       

        # Initialize defaults, replace later


        MOVIETITLE="$MOVIENAME</title>"
        MOVIESHEET=/usr/local/etc/srjg/NoMovieinfo.bmp
        MOVIEPOSTER=/usr/local/etc/srjg/nofolder.bmp

        if [ -e "$MOVIEPATH/MovieInfo.nfo" ]
        then
                # Look for lines matching <title>
                while read LINE
                do
                        # Strip out <title> to make it shorter.
                        SHORT="${LINE#<title>}"
                        # If it's not shorter, it didn't have <title>
                        [ "${#SHORT}" = "${#LINE}" ] && continue
                        MOVIETITLE="$SHORT"
                        break   # Found <title>, quit looking
                done <"$MOVIEPATH/MovieInfo.nfo"
        fi

        # Check for any files of known purpose inside the movie's folder.
       for FILE in "folder.jpg" "${MOVIENAME}.jpg"
        do
        [ ! -e "$MOVIEPATH/$FILE" ] && continue
        MOVIEPOSTER="$MOVIEPATH/$FILE"
        break
        done

       for FILE in "about.jpg" "0001.jpg" "${MOVIENAME}_sheet.jpg"
        do
        [ ! -e "$MOVIEPATH/$FILE" ] && continue
        MOVIESHEET="$MOVIEPATH/$FILE"
        break
        done

        # Print it all in one whack with a here-document.
        cat <<EOF
<Movie>
<title>$MOVIETITLE
<poster>$MOVIEPOSTER</poster>
<info>$MOVIESHEET</info>
<file>$MOVIEPATH/$MOVIEFILE</file>
</Movie>

EOF
        # Note:  OVERWRITES $RSS
done >> $RSS
	
echo "Generating RSS footer.."
echo -e "</Jukebox>" >> $RSS
}

genmainjukexmlheader()
{
echo "Generating RSS header.."
echo -e '<?xml version="1.0" encoding="UTF-8"?>
<Jukebox>
  <Category>
    <title>Jukebox Main Menu</title>
    <link>MainJukebox.rss</link>
  </Category>' > $MAINMOVIESPATH
}

genmainjukexml()	
{
echo "Indexing movies.."
echo -e "<genre>
<title>$TITLE</title>
<poster>$FOLDER</poster>
<link>$RSS</link>
</genre>" >> $MAINMOVIESPATH
}

#*****************  Main Program  *****************************************

MAINMOVIESPATH="/usr/local/etc/srjg/mainjukebox.xml"
movies_processing;
[ -n "$MODE" ] && genmoviesheet;
find "$MOVIESPATH" -name genre.jpg > $TMP2
if [ $INSTALL = "1" ]
then
   genmainjukexmlheader;
fi
while read plik
do
  MOVIESPATH="`dirname "$plik"`/"
  echo Indexing $MOVIESPATH
  FOLDER=$plik
  TITLE=`basename "$MOVIESPATH"` 
  RSS=$MOVIESPATH"jukebox.xml"  
  genjukexml;
if [ $INSTALL = "1" ]
then
  genmainjukexml;
fi
done < $TMP2
if [ $INSTALL = "1" ]
then
echo -e "</Jukebox>" >> $MAINMOVIESPATH
fi
echo -e "\nDone!"
