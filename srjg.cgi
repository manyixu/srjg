#!/bin/sh

# Parsing query string provided by the server/client
QUERY=$QUERY_STRING
SAVEIFS=$IFS
IFS="@"
set -- $QUERY
mode=`echo $1`
CategoryTitle=`echo $2 | sed "s/%2d/-/g" | sed "s/%20/ /g"`
Jukebox_Size=`echo $3`
IFS=$SAVEIFS
if [ $mode = "genre" ]; then
Search=`echo ${CategoryTitle} | cut -c1-3`
else
Search=${CategoryTitle}
fi

# Setting up variable according to srjg.cfg file
. /tmp/srjg.cfg

# Setting up other variable

Database=${Jukebox_Path}"/movies.db"
Sqlite=${Jukebox_Path}"/sqlite3"

SetVar()
# Settting up a few variables needed
{
[ $mode = "genreSelection" ] && nextmode="genre";
[ $mode = "yearSelection" ] && nextmode="year";
[ $mode = "alphaSelection" ] && nextmode="alpha";

if [ $mode = "genre" ] || [ $mode = "year" ] || [ $mode = "alpha" ] || [ $mode = "recent" ] || [ $mode = "notwatched" ]; then
  nextmode="moviesheet";
fi
}

CreateMovieDB()
# Create the Movie Database
# DB as an automatic datestamp but unfortunately it relies on the player having the
# correct date which can be trivial with some players.
{
${Sqlite} ${Database} "create table t1 (Movie_ID INTEGER PRIMARY KEY AUTOINCREMENT,genre TEXT,title TEXT,year TEXT,poster TEXT,info TEXT,file TEXT,watched INTEGER,dateStamp DATE DEFAULT CURRENT_DATE)";
${Sqlite} ${Database} "create table t2 (header TEXT, footer TEXT, IdMovhead TEXT, IdMovFoot TEXT,WatchedHead TEXT, WatchedFoot TEXT)";
${Sqlite} ${Database} "insert into t2 values ('<item>','</item>','<IdMovie>','</IdMovie>','<Watched>','</Watched>')";
}

Force_DB_Creation()
# Force creation of the Database using the "u" parameter option
# This option can be use to start up with a fresh database in case of
# Database corruption
{
rm $PreviousMovieList
rm ${Database}
CreateMovieDB;
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
  if [ "${#SHORT}" = "${#LINE}" ]; then continue ; fi
  MOVIETITLE="$SHORT"
  break   # Found <title>, quit looking
done <"$MOVIEPATH/$INFONAME"
        
GENRE=`sed -e '/<genre/,/\/genre>/!d;/genre>/d' "$MOVIEPATH/$INFONAME"`
MovieYear=`sed '/<year/!d;s:.*>\(.*\)</.*:\1:' "$MOVIEPATH/$INFONAME"`            
}


GenerateMovieList()
# Find the movies based on movie extension and path provided.  Remove movies 
# that contains the string(s) specified in $Movie_Filter
{
# Replace the comma in Movie_Filter to pipes |
Movie_Filter=`echo $Movie_Filter | sed 's/,/|/ g'`
echo "Searching for movies.."
find "$Movies_Path" \
  | egrep -i '\.(asf|avi|dat|divx|flv|img|iso|m1v|m2p|m2t|m2ts|m2v|m4v|mkv|mov|mp4|mpg|mts|qt|rm|rmp4|rmvb|tp|trp|ts|vob|wmv)$' \
  | egrep -iv "$Movie_Filter" > $MoviesList
echo "Found `sed -n '$=' $MoviesList` movies"
}

GenerateInsDelFiles()
# Generate insertion and deletion files
{
sed -i -e 's/\[/\&lsqb;/g' -e 's/\]/\&rsqb;/g' $MoviesList # Conversion of [] for grep
if [ -s "$PreviousMovieList" ] ; then # because the grep -f don't work with empty file
  grep -vf $MoviesList $PreviousMovieList | sed -e 's/\&lsqb;/\[/g' -e 's/\&rsqb;/\]/g' > $DeleteList
  grep -vf $PreviousMovieList $MoviesList | sed -e 's/\&lsqb;/\[/g' -e 's/\&rsqb;/\]/g' > $InsertList
else
  cat $MoviesList | sed -e 's/\&lsqb;/\[/g' -e 's/\&rsqb;/\]/g' > $InsertList
fi
mv $MoviesList $PreviousMovieList
}

DBMovieDelete()
# Delete records from the movies.db database.
{
echo "Removing movies from the Database ...."
while read LINE
do
  ${Sqlite} ${Database}  "DELETE from t1 WHERE file='<file>${LINE}</file>'";
done < $DeleteList
${Sqlite} ${Database}  "VACUUM";
}

DBMovieInsert()
# Add movies to the Database and extract movies posters/folders
{
while read LINE
do
   MOVIEPATH="${LINE%/*}"  # Shell builtins instead of dirname
   MOVIEFILE="${LINE##*/}" # Shell builtins instead of basename
   MOVIENAME="${MOVIEFILE%.*}"  # Strip off .ext       

   # Initialize defaults, replace later
   MOVIETITLE="$MOVIENAME</title>"
   MOVIESHEET=${Jukebox_Path}/images/NoMovieinfo.jpg
   MOVIEPOSTER=${Jukebox_Path}/images/nofolder.jpg
   GENRE="<name>Unknown</name>"
   MovieYear=""
		
   [ -e "$MOVIEPATH/$MOVIENAME.nfo" ] && INFONAME=$MOVIENAME.nfo
   [ -e "$MOVIEPATH/MovieInfo.nfo" ] && INFONAME=MovieInfo.nfo
        
   [ -e "$MOVIEPATH/$INFONAME" ] && Infoparsing

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

${Sqlite} ${Database} "insert into t1 (genre,title,year,poster,info,file) values('$dbgenre','$dbtitle','$dbYear','$dbposter','$dbinfo','$dbfile');";

done < $InsertList
}

Update()
# Will update the Database based on the parameters in srjg.cfg
{
# Initialize some Variables

MoviesList="/tmp/movies.list"
InsertList="/tmp/insert.list"
DeleteList="/tmp/delete.list"
PreviousMovieList="${Jukebox_Path}/prevmovies.list"
IMDB=""
Force_DB_Update=""

GenerateMovieList;
[ -n "$IMDB" ] &&  ${Jukebox_Path}/imdb.sh
[ -n "$Force_DB_Update" ] && Force_DB_Creation
[ ! -f "${Database}" ] && CreateMovieDB
GenerateInsDelFiles;
[[ -s $DeleteList ]] && DBMovieDelete
[[ -s $InsertList ]] && DBMovieInsert
}

WatchedToggle()
# Toggle the state of the watched field in the Database.
{
echo -e '
<?xml version="1.0" ?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
<onEnter>
showIdle();
postMessage("return");
</onEnter>'

watch="`${Sqlite} -separator ''  ${Database}  "SELECT Watched FROM t1 WHERE Movie_ID like '$CategoryTitle'";`"

if [ $watch == "1" ]; then
      watch="0";
else
     watch="1";
fi

${Sqlite} ${Database} "UPDATE t1 set Watched=$watch WHERE Movie_ID like '$CategoryTitle'";

echo -e '
<channel>
<item>
</item>
</channel>
</rss>'

exit 0
}

Header()
#Insert RSS Header
{
echo -e '
<?xml version="1.0" ?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">'
}


Footer()
#Insert RSS Footer
{
echo -e '
</channel>
</rss>'
}


MoviesheetView()
#Display moviesheet
{
ImgLink="`${Sqlite} -separator ''  ${Database}  "SELECT info FROM t1 WHERE Movie_ID like '$Search'" | sed '/<info/!d;s:.*>\(.*\)</.*:\1:'| grep "[!-~]";`"
FileLink="`${Sqlite} -separator ''  ${Database}  "SELECT file FROM t1 WHERE Movie_ID like '$Search'" | sed '/<file/!d;s:.*>\(.*\)</.*:\1:'| grep "[!-~]";`"

cat <<EOF
<onEnter>showIdle();</onEnter>
<mediaDisplay name="onePartView" backgroundColor="0:0:0" sideColorBottom="0:0:0" sideColorTop="0:0:0" sideTopHeightPC="0" sideBottomHeightPC="0" imageBorderPC="0" centerHeightPC="100" showHeader="no" showDefaultInfo="no" idleImageWidthPC="9" idleImageHeightPC="16">
<idleImage> image/POPUP_LOADING_01.png </idleImage>
<idleImage> image/POPUP_LOADING_02.png </idleImage>
<idleImage> image/POPUP_LOADING_03.png </idleImage>
<idleImage> image/POPUP_LOADING_04.png </idleImage>
<idleImage> image/POPUP_LOADING_05.png </idleImage>
<idleImage> image/POPUP_LOADING_06.png </idleImage>
<idleImage> image/POPUP_LOADING_07.png </idleImage>
<idleImage> image/POPUP_LOADING_08.png </idleImage>
<backgroundDisplay>
<image redraw="no" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">$ImgLink</image>
</backgroundDisplay>
<onUserInput>
<script>
userInput = currentUserInput();
if (userInput == "enter") {
    playItemURL("$FileLink", 10);
    "true";
}
else if (userInput == "left" || userInput == "right") {"true"; }

</script>
</onUserInput>
</mediaDisplay>
<channel>
EOF
}


DisplayRss()
#Display many of the RSS required based on various parameters/variables
{
if [ $Jukebox_Size = "2x6" ]; then
   row="2"; col="6"; itemWidth="14.06"; itemHeight="35.42"; itemXPC="5.5"; itemYPC="12.75";
   NewView="sheetwall";
   
elif [ $Jukebox_Size = "sheetwall" ]; then
   row="1"; col="8"; itemWidth="10.3"; itemHeight="20"; itemXPC="5.5"; itemYPC="80";
   NewView="sheetmovie";
   
 elif [ $Jukebox_Size = "sheetmovie" ]; then
   row="1"; col="8"; itemWidth="10.3"; itemHeight="20"; itemXPC="5.5"; itemYPC="20";
   NewView="3x8";
   
else
   row="3"; col="8"; itemWidth="10.3"; itemHeight="23.42"; itemXPC="5.5"; itemYPC="12.75";
   NewView="2x6";
fi
   
echo -e '
	<onEnter>redrawDisplay();</onEnter>

	<script>
	    Config = "/usr/local/etc/srjg.cfg";
		Config_ok = loadXMLFile(Config);
		if (Config_ok == null) {
			Jukebox_Path = ""/usr/local/etc/srjg";
			Language = "en";
        }
		else {
			Jukebox_Path = getXMLText("Config", "Jukebox_Path");
			Language = getXMLText("Config", "Lang");
		}
		
		Jukebox_Temp = "/tmp/";
            Category_Title = "'$CategoryTitle'";
	    Category_Background = "'${Jukebox_Path}'/images/background.jpg";						           
            setFocusItemIndex(0);
            Current_Item_index=0;
            NewView = "'$NewView'";
            Genre_Title = Category_Title;
	    Jukebox_Size ="'$Jukebox_Size'";
	    mode = "'$mode'";
	    nextmode = "'$nextmode'";
		
		langpath = Jukebox_Path + "/lang/" + Language;
		langfile = loadXMLFile(langpath);
		if (langfile != null)
		{
			jukebox_top = getXMLText("jukebox", "top");
		}
		
	</script>

<mediaDisplay name="photoView" rowCount="'$row'" columnCount="'$col'" imageFocus="null" showHeader="no" showDefaultInfo="no" drawItemBorder="no" viewAreaXPC="0" viewAreaYPC="0" viewAreaWidthPC="100" viewAreaHeightPC="100" itemGapXPC="0.7" itemGapYPC="1" itemWidthPC="'$itemWidth'" itemHeightPC="'$itemHeight'" itemOffsetXPC="'$itemXPC'" itemOffsetYPC="'$itemYPC'" itemBorderPC="0" itemBorderColor="7:99:176" itemBackgroundColor="-1:-1:-1" sideTopHeightPC="0" sideBottomHeightPC="0" bottomYPC="100" idleImageXPC="67.81" idleImageYPC="89.17" idleImageWidthPC="4.69" idleImageHeightPC="4.17" backgroundColor="0:0:0">

		<idleImage> image/POPUP_LOADING_01.png </idleImage>
		<idleImage> image/POPUP_LOADING_02.png </idleImage>
		<idleImage> image/POPUP_LOADING_03.png </idleImage>
		<idleImage> image/POPUP_LOADING_04.png </idleImage>
		<idleImage> image/POPUP_LOADING_05.png </idleImage>
		<idleImage> image/POPUP_LOADING_06.png </idleImage>
		<idleImage> image/POPUP_LOADING_07.png </idleImage>
		<idleImage> image/POPUP_LOADING_08.png </idleImage>'


if ([ $Jukebox_Size = "2x6" ] ||  [ $Jukebox_Size = ""3x8"" ]); then		
cat <<EOF
		<backgroundDisplay>
            <script>
                 Jukebox_itemSize = getPageInfo("itemCount"); 
			</script>
			<image redraw="no" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
				<script>
					print(Category_Background);
				</script>
		  	</image>      
		</backgroundDisplay>   

        <text redraw="no" align="center" offsetXPC="2" offsetYPC="1" widthPC="96" heightPC="3" fontSize="12" backgroundColor="-1:-1:-1" foregroundColor="130:130:130">
			<script>
				print(jukebox_top);
			</script>
		</text>
   
		<text redraw="no" align="center" offsetXPC="2.5" offsetYPC="3" widthPC="90" heightPC="10" fontSize="20" backgroundColor="-1:-1:-1" foregroundColor="192:192:192">
			<script>
			    print(Category_Title);
			</script>
		</text>
EOF

elif [ $Jukebox_Size = "sheetwall" ]; then
cat <<EOF
		<backgroundDisplay>
                        <script>
                                Jukebox_itemSize = getPageInfo("itemCount"); 
			</script>    
		</backgroundDisplay>
		
		<image redraw="yes" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="80">
				<script>
					getItemInfo(-1, "info");
				</script>
</image>
EOF

else
cat <<EOF
		<backgroundDisplay>
                        <script>
                                Jukebox_itemSize = getPageInfo("itemCount"); 
			</script>    
		</backgroundDisplay>
		
		<image redraw="yes" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
				<script>
					getItemInfo(-1, "info");
				</script>
</image>
EOF

fi
	
cat <<EOF	
	<onUserInput>
			<script>
				userInput = currentUserInput();
				Current_Item_index=getFocusItemIndex();
				Max_index = (-1 + Jukebox_itemSize);
				Prev_index = (-1 + Current_Item_index);
				Next_index = (1 + Current_Item_index);
				Prev10_index = (-10 + Current_Item_index);
				Next10_index = (10 + Current_Item_index);

				if (userInput == "pageup" &amp;&amp; Current_Item_index &gt; 9) {
					setFocusItemIndex(Prev10_index); 
					"true";
					redrawDisplay();
				} else if (userInput == "pagedown"  &amp;&amp; Current_Item_index &lt; (Max_index - 9)) {
					setFocusItemIndex(Next10_index); 
					"true";
					redrawDisplay();
				} else if (userInput == "left") {
					"false";
				} else if (userInput == "right") {
					"false";                                 
                                } else if (userInput == "enter") {
					if (nextmode == "moviesheet") {
					   Genre_Title=getItemInfo(-1, "IdMovie");}
					else {
					   Genre_Title=urlencode(getItemInfo(-1, "title"));}
					   jumpToLink("NextView");
					   "false";
				} else if (userInput == "one") {
                                        Genre_Title=urlEncode(Genre_Title); 
					jumpToLink("SwitchView");
					"false";
					redrawDisplay();
				} 
EOF

	if [ $mode = "genre" ] || [ $mode = "year" ] || [ $mode = "alpha" ] || [ $mode = "recent" ] || [ $mode = "notwatched" ]; then
	  cat <<EOF     
				  else if (userInput == "video_play") {
                                        Current_Movie_File=getItemInfo(-1, "file");
                                        playItemURL(Current_Movie_File, 10);
					"false";
				} else if (userInput == "two") {
                                        MovieID=getItemInfo(-1, "IdMovie"); 
					jumpToLink("Watchcgi");
					"false";
				}
EOF
	fi

cat << EOF 
			</script>
		</onUserInput>
EOF


if ([ $Jukebox_Size = "2x6" ] ||  [ $Jukebox_Size = ""3x8"" ]); then
cat << EOF 
<!-- Show Folder Name -->
<text offsetXPC="7" offsetYPC="88.8" widthPC="60" heightPC="5" fontSize="14" useBackgroundSurface="yes" foregroundColor="195:196:195" redraw="yes" lines="1">
 <script>
    displayTitle = getItemInfo(-1, "title"); 
    displayTitle;
 </script>
</text>


<!-- Show Page Info -->
<text offsetXPC="85" offsetYPC="88.8" widthPC="8" heightPC="5" fontSize="14" foregroundColor="195:196:195" useBackgroundSurface="yes" redraw="yes" lines="1">
 <script>
  pageInfo = Add(getFocusItemIndex(),1) + "/" + Jukebox_itemSize;
  pageInfo;
 </script>
</text>

<itemDisplay>
EOF

else
cat << EOF 
<itemDisplay>
EOF

fi

cat << EOF 
<!-- Bottom Layer focus/unfocus -->
<image offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
EOF
echo -e'
 <script>
  if (getDrawingItemState() == "focus")
  { if (getItemInfo(-1, "Watched") == "1") {
      "'${Jukebox_Path}'/images/focus_watched.jpg";
      }
    else {
      "'${Jukebox_Path}'/images/focus.jpg";
      }
  }
  else
  { if (getItemInfo(-1, "Watched") == "1") {
      "'${Jukebox_Path}'/images/unfocus_watched.jpg";
      }
    else {
      "'${Jukebox_Path}'/images/unfocus.jpg";
      }
  }
 </script>
</image>'


if [ "$mode" = "yearSelection" ]; then
echo -e '
<!-- Top Layer folder.jpg -->
<image offsetXPC="8.2" offsetYPC="5.5" widthPC="84.25" heightPC="89.25">
 <script>
  thumbnailPath = "'${Jukebox_Path}'/images/yearfolder.jpg";
  thumbnailPath;
 </script>
</image>
<text offsetXPC="4" offsetYPC="16" widthPC="105" heightPC="20" fontSize="12" align="center" foregroundColor="0:0:0">
<script>
	getItemInfo(-1, "title");
</script>
</text>'


else
echo -e '

<!-- Top Layer folder.jpg -->
<image offsetXPC="8.2" offsetYPC="5.5" widthPC="84.25" heightPC="89.25">
 <script>
  thumbnailPath = getItemInfo(-1, "poster");
  thumbnailPath;
 </script>
</image>

<!-- Display watched icon -->
<image offsetXPC="3.2" offsetYPC="3.0" widthPC="20" heightPC="15">
<script>
   if (getItemInfo(-1, "Watched") == "1") {
      "'${Jukebox_Path}'/images/watched.png";
      }
   else {
      "'${Jukebox_Path}'/images/notwatched.png"; }
</script>
</image>'
     
fi

cat << EOF
</itemDisplay>
</mediaDisplay>

<NextView>
    <link>
       <script>
	print("http://127.0.0.1:$Port/cgi-bin/srjg.cgi?"+nextmode+"@"+Genre_Title+"@"+Jukebox_Size);
       </script>
    </link>
</NextView>


<SwitchView>
    <link>
       <script>
           print("http://127.0.0.1:$Port/cgi-bin/srjg.cgi?"+mode+"@"+Genre_Title+"@"+NewView);
       </script>
    </link>
</SwitchView>

<Watchcgi>
    <link>
       <script>
           print("http://127.0.0.1:$Port/cgi-bin/srjg.cgi?togglewatch@"+MovieID+"@"+Jukebox_Size);
       </script>
    </link>
</Watchcgi>

<channel>
	<title><script>Category_Title;</script></title>
	<link><script>Category_RSS;</script></link>
	<itemSize><script>Jukebox_itemSize;</script></itemSize>
EOF

if [ "$mode" = "genre" ]; then
   if [ "$Search" = "All" ]; then
     ${Sqlite} -separator ''  ${Database}  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,poster,info,file,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 ORDER BY title COLLATE NOCASE"; # All Movies
   else
      ${Sqlite} -separator ''  ${Database}  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,poster,info,file,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 WHERE genre LIKE '%$Search%' ORDER BY title COLLATE NOCASE";
   fi   
fi

if [ "$mode" = "alpha" ]; then
${Sqlite} -separator ''  ${Database}  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,poster,info,file,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 WHERE title LIKE '<title>$Search%' ORDER BY title COLLATE NOCASE";
fi

if [ "$mode" = "year" ]; then
${Sqlite} -separator ''  ${Database}  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,poster,info,file,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 WHERE year ='$Search' ORDER BY title COLLATE NOCASE";
fi

if [ "$mode" = "recent" ]; then
${Sqlite} -separator ''  ${Database}  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,poster,info,file,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 ORDER BY datestamp DESC LIMIT "$Recent_Max;
fi

if [ "$mode" = "notwatched" ]; then
${Sqlite} -separator ''  ${Database}  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,poster,info,file,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 WHERE watched <>'1' OR watched IS NULL ORDER BY title COLLATE NOCASE";
fi

if [ "$mode" = "yearSelection" ]; then
# pulls out the years of the movies
${Sqlite} -separator ''  ${Database}  "SELECT DISTINCT year FROM t1 ORDER BY year COLLATE NOCASE" > /tmp/year.list
while read LINE
do
echo "<item>"
echo "<title>"$LINE"</title>"
echo "</item>"
done < /tmp/year.list
fi


if [ "$mode" = "genreSelection" ]; then
# pulls out the genre of the movies
# The first line does the following: Pull data from database; remove all leading/trailing white spaces; sort and remove duplicate
# remove possible empty line that may exist; remove <name>Sci-fi</name> keeps Science fiction instead; remove any blank line
# that may be still present.
${Sqlite} -separator ''  ${Database}  "SELECT genre FROM t1" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' | sort -u | sed '/<name/!d;s:.*>\(.*\)</.*:\1:' | grep "[!-~]" | egrep -v "Sci-Fi" > /tmp/genre.list
sed -i 1i"All Movies" /tmp/genre.list
while read LINE
do
echo -e '<item>
     <title>'$LINE'</title>
     <poster>'${Jukebox_Path}'/images/genre/'$LINE'.jpg</poster>
     </item>'
done < /tmp/genre.list
fi


if [ "$mode" = "alphaSelection" ]; then
# pulls out the first letter of alphabet of the movie title
# The first line does the following: Pull data from database; remove the leading and trailing <title></title>; cut the title first 
# Character; remove anything that is not A-Z ex: a number; sort and remove duplicate.
${Sqlite} -separator ''  ${Database}  "SELECT title FROM t1" | sed '/<title/!d;s:.*>\(.*\)</.*:\1:' | cut -c 1 | grep '[A-Z]' | sort -u > /tmp/alpha.list
while read LINE
do
echo "<item>"
echo "<title>"$LINE"</title>"
echo "<poster>"${Jukebox_Path}"/images/alpha/JukeMenu_"$LINE".jpg</poster>"
echo "</item>"
done < /tmp/alpha.list
fi
}


#***********************Main Program*********************************

if [ "$mode" = "togglewatch" ]; then
   WatchedToggle;
fi
if [ "$mode" = "Update" ]; then
  Update;
else
  if [ "$mode" = "moviesheet" ]; then
    Header;
    MoviesheetView;
    Footer;
  else
    SetVar;
    Header;
    DisplayRss;
    Footer;
  fi
fi
exit 0

