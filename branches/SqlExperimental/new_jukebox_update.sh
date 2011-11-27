#!/bin/sh
# Simple RSS Jukebox Generator


# Reading/parsing xml configuration file and assign variables.

CfgFile=./Jukebox.cfg
if [ ! -f "${CfgFile}" ]; then
  echo "Configuration file not found: ${CfgFile}"
  exit 1
fi
sed '1d;$d;s:<\(.*\)>\(.*\)</.*>:\1=\2:' ${CfgFile} >/tmp/Jukebox.cfg
. /tmp/Jukebox.cfg

# Initialize some Variables

MoviesList="/tmp/movies.list"
InsertList="/tmp/insert.list"
DeleteList="/tmp/delete.list"
PreviousMovieList="$Jukebox_Path/prevmovies.list"
DiffList="/tmp/diff.list"
IMDB=""
Force_DB_Update=""

usage()
# Display help menu
{
cat << EOF
usage: $0 options

This script creates a Movie / TV Episode on a specified directory.

OPTIONS:
   -h      Show this message
   -p      This indicate the jukebox directory ex: -p /HDD/movies/
   -f      This is the filter option, movies filename containing this/those
           string(s) will be skipped.  Strings must be separated by a ","
           (Optional) ex: -f sample,trailer
   -g      Generate moviesheets, thumbnails and NFO files. (Optional)
           Please refer to $Jukebox_Path/imdb.sh for additional settings.
NOTES:  If any of the arguments have spaces in them they must be surrounded by quotes: ""
    
EOF
exit 1
}

#------------------------
# Parsing parameters 
#------------------------
while getopts p:f:ghu OPTION 
do
  case $OPTION in
     p)
       Movies_Path=$OPTARG
       if [ ! -d "${Movies_Path}" ]			# ctrl directory param
       then
         echo -e "The specified directory doesn't exist: ${Movies_Path}"
         exit 1
       fi
       sed -i "s:\(Movies_Path>\)\(.*\)\(</.*\):\1${Movies_Path}\3:" ${CfgFile}	# write param in cfg file
       ;;
     f)
       Movie_Filter=$OPTARG
       sed -i "s:\(Movie_Filter>\)\(.*\)\(</.*\):\1${Movie_Filter}\3:" ${CfgFile}	# write param in cfg file
       ;;
     g)
       IMDB=y
       ;;
     h)
       usage
       ;;
     u)
       Force_DB_Update=y
   esac
done

if [ ! -d "${Movies_Path}" ]; then			# ctrl directory cfg file
  echo -e "The Movies_Path specified directory in ${CfgFile} doesn't exist: ${Movies_Path}"
  exit 1
fi



CreateMovieDB()
# Create the Movie Database
# DB as an automatic datestamp but unfortunately it relies on the player having the
# correct date which can be trivial with some players.
{
echo "Creating Database..."
$Jukebox_Path/sqlite3 ${Movies_Path}movies.db "create table t1 (Movie_ID INTEGER PRIMARY KEY AUTOINCREMENT,head TEXT,genre TEXT,title TEXT,year TEXT,poster TEXT,info TEXT,file TEXT,footer TEXT,dateStamp DATE DEFAULT CURRENT_DATE);"
}

Force_DB_Creation()
# Force creation of the Database using the "u" parameter option
# This option can be use to start up with a fresh database in case of
# Database corruption
{
rm $PreviousMovieList
rm ${Movies_Path}movies.db
CreateMovieDB;
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
     MOVIETITLE="$SHORT"
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
   MovieYear=Unknown
		
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
dbtitle=`echo "<title>$MOVIETITLE" | sed "s/'/''/g"`
dbposter=`echo "<poster>$MOVIEPOSTER</poster>" | sed "s/'/''/g"`
dbinfo=`echo "<info>$MOVIESHEET</info>" | sed "s/'/''/g"`
dbfile=`echo "<file>$MOVIEPATH/$MOVIEFILE</file>" | sed "s/'/''/g"`
dbYear=$MovieYear

$Jukebox_Path/sqlite3 ${Movies_Path}movies.db "insert into t1 (head,genre,title,year,poster,info,file,footer) values ('<item>','$dbgenre','$dbtitle','$dbYear','$dbposter','$dbinfo','$dbfile','</item>');";

done < $InsertList
}


DBMovieDelete()
# Delete records from the movies.db database.
{
echo "Removing movies from the Database ...."
while read LINE
do
$Jukebox_Path/sqlite3 ${Movies_Path}movies.db  "DELETE from t1 WHERE file='<file>${LINE}</file>'";
done < $DeleteList
$Jukebox_Path/sqlite3 ${Movies_Path}movies.db  "VACUUM";
}


#*****************  Main Program  *****************************************

GenerateMovieList;
[ -n "$IMDB" ] && $Jukebox_Path/imdb.sh;
[ -n "$Force_DB_Update" ] && Force_DB_Creation;
[ ! -f "${Movies_Path}movies.db" ] && CreateMovieDB;
echo Indexing $Movies_Path;
# if full update required then just delete (rm) $PreviousMovieList
GenerateInsDelFiles;
if [[ -s $DeleteList ]] ; then DBMovieDelete; fi
if [[ -s $InsertList ]] ; then DBMovieInsert; fi
echo -e "\nDone!"


