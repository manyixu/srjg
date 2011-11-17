#!/bin/sh
# PlayOn!HD Simple RSS Jukebox Generator

# Initialize some Variables

MoviesList="/tmp/movies.list"
InsertList="/tmp/insert.list"
DeleteList="/tmp/delete.list"
PreviousMovieList="/usr/local/etc/srjg/prevmovies.list"
DiffList="/tmp/diff.list"


ReadConfigFile()
# Reading/parsing xml configuration file and assign variables.
{
CfgFile=./Jukebox.cfg
if [ ! -f "${CfgFile}" ]; then
  echo "Don't found config file : ${CfgFile}"
  exit 1
fi
sed '1d;$d;s:<\(.*\)>\(.*\)</.*>:\1=\2:' ${CfgFile} >/tmp/Jukebox.cfg
. /tmp/Jukebox.cfg
}


usage()
# Display help menu
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


GenerateMovieList()
# Find the movies based on movie extension and path provided.  Remove movies 
# that contains the string(s) specified in $Movie_Filter
{
# Replace the comma in Movie_Filter to pipes |
Movie_Filter=`echo $Movie_Filter | sed 's/,/|/ g'`
echo "Searching for movies.."
find "$Movies_Path" | egrep -i '\.(asf|avi|dat|divx|flv|img|iso|m1v|m2p|m2t|m2ts|m2v|m4v|mkv|mov|mp4|mpg|mts|qt|rm|rmp4|rmvb|tp|trp|ts|vob|wmv)$' | egrep -iv "$Movie_Filter" > $MoviesList
echo "Found `sed -n '$=' $MoviesList` movies"
}


Infoparsing()
# Parse nfo file to extract movie title, genre and year
{
# Look for lines matching <title>
while read LINE
   do
     # Strip out <title> to make it shorter.
     SHORT="${LINE#<title>}"
     # If it's not shorter, it didn't have <title>
     [ "${#SHORT}" = "${#LINE}" ] && continue
     MOVIETITLE=`echo "$SHORT" | sed "s/'/''/"`
     break   # Found <title>, quit looking
   done <"$MOVIEPATH/$INFONAME"
        
GENRE=`sed -e '/<genre/,/\/genre>/!d;/genre>/d' "$MOVIEPATH/$INFONAME"`
MovieYear=`sed '/<year/!d;s:.*>\(.*\)</.*:\1:' "$MOVIEPATH/$INFONAME"`            
}


GenerateInsDelFiles()
# Generate the working insertion and deletion files 
{
[ ! -f "$PreviousMovieList" ] && touch $PreviousMovieList;
diff $PreviousMovieList $MoviesList | sed '1,3d' > $DiffList
> $InsertList
> $DeleteList
while read LINE
do
 if [ ${LINE:0:1} = '+' ]; then echo ${LINE:1} >> $InsertList; fi
 if [ ${LINE:0:1} = '-' ]; then echo ${LINE:1} >> $DeleteList; fi
done < $DiffList
mv $MoviesList $PreviousMovieList
}

DBMovieInsert()
# Add movies to the Database and extract movies posters/folders
{
echo "Adding movies to the Database ...."
 
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
        
   if [ -e "$MOVIEPATH/$INFONAME" ]; then Infoparsing; fi

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

dbgenre=$GENRE
dbtitle="<title>$MOVIETITLE"
dbposter="<poster>$MOVIEPOSTER</poster>"
dbinfo="<info>$MOVIESHEET</info>"
dbfile="<file>$MOVIEPATH/$MOVIEFILE</file>"
dbYear=$MovieYear

/home/srjgsql/sqlite3 /home/srjgsql/movies.db "insert into t1 (head,genre,title,poster,info,file,footer) values ('<item>','$dbgenre','$dbtitle','$dbposter','$dbinfo','$dbfile','</item>');";

done < $InsertList
}


DBMovieDelete()
# Delete records from the movies.db database.
{
echo "Removing movies from the Database ...."
while read LINE
do
/home/srjgsql/sqlite3 /home/srjgsql/movies.db  "DELETE from t1 WHERE file='${LINE}'";
done < $DeleteList
/home/srjgsql/sqlite3 /home/srjgsql/movies.db  "VACUUM";
}


#*****************  Main Program  *****************************************

ReadConfigFile;
GenerateMovieList;
[ -n "$MODE" ] && /usr/local/etc/srjg/imdb.sh;
echo Indexing $Movies_Path;
# if full update required then just delete (rm) $PreviousMovieList
GenerateInsDelFiles;
if [[ -s $DeleteList ]] ; then DBMovieDelete; fi
if [[ -s $InsertList ]] ; then DBMovieInsert; fi
echo -e "\nDone!"


