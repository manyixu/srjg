#!/bin/sh
# PlayOn!HD Simple RSS Jukebox Generator
# Author: mikka [mika.hellmann@gmail.com]
# Modified by Snappy46 [levesque.marcel@gmail.com]


TMP="/tmp/movie.list"
#TMP2="/tmp/genrerss.list"
#SORTEDTMP="/tmp/sortedrss.list"
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

    The Following options are only required if you decide to use the script built-iname
    capability to create automatically Moviesheet/Thumbnails. I suggest you consult this
    Web site: http://playon.unixstorm.org/imdb.php if you want to know more about 
    the various options.

   -m      Generate moviesheets and thumbnails. (Optional)
           Possible values are: moviesheet, poster, both
   -n      name of the moviesheeet ?????????????????????????????
   -b	   if set to "yes" random backdrop will be used (Optional)
   -c      Possible values are: bdrip, bluray, dtheater, dvd, generic, hddvd, 
           hdtv, itunes (works only with mode set to moviesheet) (Default generic)
   -s      If set to "tmdb" random poster from themoviedb.org will be used
           Otherwise default poster from IMDB will be used (works only with mode 
           set to poster or moviesheet) (Optional)
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
  echo -e "A directory must be specified using -p must be specified."
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


#echo "Sorting movies.."

#sed 's:\(.*/\)\([^/]*\):\2 \1\2:' $TMP | sort | sed 's:[^/]* ::' > $SORTEDTMP
echo "Found `sed -n '$=' $TMP` movies"
}


# Creates moviesheets by calling IMDB API
genmoviesheet()
{
echo "Generating Moviesheet.."
API="http://playon.unixstorm.org/IMDB/imdb.php?"

grep "$MOVIESPATH" "$TMP" | while read LINE
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
echo "Done generating Moviesheet/Thumbnails"
}


# creates the jukebox.xml file.
# Remember to change title to mainheading
genjukexml()
{	
echo "Indexing movies.."

#grep "$MOVIESPATH" "$TMP" | 
while read LINE
do
        MOVIEPATH="${LINE%/*}"  # Shell builtins instead of dirname
        MOVIEFILE="${LINE##*/}" # Shell builtins instead of basename
        MOVIENAME="${MOVIEFILE%.*}"  # Strip off .ext       

        # Initialize defaults, replace later


        MOVIETITLE="$MOVIENAME</title>"
        MOVIESHEET=/usr/local/etc/srjg/NoMovieinfo.bmp
        MOVIEPOSTER=/usr/local/etc/srjg/nofolder.bmp
        GENRE=Unknown

        
        [ -e "$MOVIEPATH/$MOVIENAME.nfo" ] && INFONAME=$MOVIENAME.nfo;
	[ -e "$MOVIEPATH/MovieInfo.nfo" ] && INFONAME=MovieInfo.nfo;
        
	if [ -e "$MOVIEPATH/$INFONAME" ]
        then
                # Look for lines matching <title>
                while read LINE
                do
                        # Strip out <title> to make it shorter.
                        SHORT="${LINE#<title>}"
                        # If it's not shorter, it didn't have <title>
                        [ "${#SHORT}" = "${#LINE}" ] && continue
                        MOVIETITLE=`echo "$SHORT" | sed "s/'/''/"`
#			MOVIETITLE="$SHORT"
                        break   # Found <title>, quit looking
               done <"$MOVIEPATH/$INFONAME"
        
#       MOVIETITLE=`grep "<title>.*<.title>" "$MOVIEPATH/MovieInfo.nfo" | sed -e "s/^.*<title/<title/" | cut -f2 -d">"| cut -f1 -d"<"`
#       MOVIETITLE=`sed -n '/<title>/,/<\/title>/p' "$MOVIEPATH/MovieInfo.nfo" | grep -v "<*title>"`
#       GENRE=`sed -n '/<genre>/,/<\/genre>/p' "$MOVIEPATH/MovieInfo.nfo" | grep -v "<*genre>"`
        GENRE=`sed -e '/<genre/,/\/genre>/!d;/genre>/d' "$MOVIEPATH/$INFONAME"`
        Movie_Year=`sed '/<year/!d;s:.*>\(.*\)</.*:\1:' "$MOVIEPATH/$INFONAME"`            
    #     MOVIETITLE=`sed 's/'/''/' $MOVIETITLE`
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

#        cat <<EOF
#<item>
dbgenre=$GENRE
dbtitle="<title>$MOVIETITLE"
dbposter="<poster>$MOVIEPOSTER</poster>"
dbinfo="<info>$MOVIESHEET</info>"
dbfile="<file>$MOVIEPATH/$MOVIEFILE</file>"
#</item>


#result=`sqlite3 /home/srjgsql/movies.db "SELECT title FROM t1 WHERE file='$dbfile'";`

#echo $result

#if [ ! -n "$result" ]; then

/home/srjgsql/sqlite3 /home/srjgsql/movies.db "insert into t1 (head,genre,title,poster,info,file,footer) values ('<item>','$dbgenre','$dbtitle','$dbposter','$dbinfo','$dbfile','</item>');";
#fi

#EOF
        # Note:  OVERWRITES $RSS
done < $TMP  #> $RSS	# needs to overwrite previous file

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
sqlite3 /home/srjgsql/movies.db  "delete from t1";
sqlite3 /home/srjgsql/movies.db  "VACUUM";
movies_processing;
[ -n "$MODE" ] && genmoviesheet;
#find "$MOVIESPATH" -name genre.jpg > $TMP2
if [ $INSTALL = "1" ]
then
   genmainjukexmlheader;
fi
#while read plik
#do
#  MOVIESPATH="`dirname "$plik"`/"
  echo Indexing $MOVIESPATH
#  FOLDER=$plik
#  TITLE=`basename "$MOVIESPATH"` 
#  RSS=$MOVIESPATH"jukebox.xml" 
#x=1
#while [ $x -le 10 ]
#do
  genjukexml;
#x=$(( $x + 1 ))
#done
if [ $INSTALL = "1" ]
then
  genmainjukexml;
fi
#done < $TMP2
if [ $INSTALL = "1" ]
then
echo -e "</Jukebox>" >> $MAINMOVIESPATH
fi
echo -e "\nDone!"
