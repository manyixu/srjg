#!/bin/sh

# Parsing query string provided by the server/client
QUERY=$QUERY_STRING
SAVEIFS=$IFS
IFS="@"
set -- $QUERY
mode=`echo $1`
# full urldecode the CategoryTitle
CategoryTitle=$(echo $2 | sed 's/+/ /g;s/%\(..\)/\\x\1/g;')
CategoryTitle=`echo -n -e $CategoryTitle`
Jukebox_Size=`echo $3`
IFS=$SAVEIFS
Search=${CategoryTitle}

# Setting up variable according to srjg.cfg file
. /tmp/srjg.cfg

# Setting up other variable
if [ "${SingleDb}" = "yes" ]; then 
  Database="${Jukebox_Path}movies.db"
  UpdateLog="${Jukebox_Path}update.log"
  PreviousMovieList="${Jukebox_Path}prevmovies.list"
else
  Database="${Movies_Path}SRJG/movies.db"
  UpdateLog="${Movies_Path}SRJG/update.log"
  [ -d "${Movies_Path}" ] && mkdir -p "${Movies_Path}SRJG/"
  PreviousMovieList="${Movies_Path}SRJG/prevmovies.list"
fi

Sqlite=${Jukebox_Path}"sqlite3"
MoviesList="/tmp/srjg_movies.list"
InsertList="/tmp/srjg_insert.list"
DeleteList="/tmp/srjg_delete.list"

# Genre "All Movies" depending of the language
AllMovies=`sed "/>All Movies|/!d;s:|\(.*\)>.*:\1:" "${Jukebox_Path}lang/${Language}_genre"`

SetVar()
# Settting up a few variables needed
{
[ $mode = "genreSelection" ] && nextmode="genre";
[ $mode = "yearSelection" ] && nextmode="year";
[ $mode = "alphaSelection" ] && nextmode="alpha";

if [ $mode = "genre" ] || [ $mode = "year" ] || [ $mode = "alpha" ] || [ $mode = "recent" ] || [ $mode = "notwatched" ] || [ $mode = "moviesearch" ]; then
  nextmode="moviesheet";
fi
}

CreateMovieDB()
# Create the Movie Database
# DB as an automatic datestamp but unfortunately it relies on the player having the
# correct date which can be trivial with some players.
{
${Sqlite} "${Database}" "create table t1 (Movie_ID INTEGER PRIMARY KEY AUTOINCREMENT,genre TEXT,title TEXT,year TEXT,path TEXT,file TEXT,ext TEXT,watched INTEGER,dateStamp DATE DEFAULT CURRENT_DATE)";
${Sqlite} "${Database}" "create table t2 (header TEXT, footer TEXT, IdMovhead TEXT, IdMovFoot TEXT,WatchedHead TEXT, WatchedFoot TEXT)";
${Sqlite} "${Database}" "insert into t2 values ('<item>','</item>','<IdMovie>','</IdMovie>','<Watched>','</Watched>')";
}

Force_DB_Creation()
# Force creation of the Database using the "u" parameter option
# This option can be use to start up with a fresh database in case of
# Database corruption
{
rm "${PreviousMovieList}" 2>/dev/null # The /dev/null if list not exist due to rss update
rm "${Database}" 2>/dev/null
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

# if genre not exist <genre />
GENRE=`sed -e '/<genre>/,/\/genre>/!d;/genre>/d' -f "${Jukebox_Path}lang/${Language}_genreGrp" "$MOVIEPATH/$INFONAME"`
MovieYear=`sed '/<year>/!d;s:.*>\(.*\)</.*:\1:' "$MOVIEPATH/$INFONAME"`            
}

GenerateMovieList()
# Find the movies based on movie extension and path provided.  Remove movies 
# that contains the string(s) specified in $Movie_Filter
{
# Replace the comma in Movie_Filter to pipes |
Movie_Filter=`echo $Movie_Filter | sed 's/,/|/ g'`

find "$Movies_Path" \
  | egrep -i '\.(asf|avi|dat|divx|flv|img|iso|m1v|m2p|m2t|m2ts|m2v|m4v|mkv|mov|mp4|mpg|mts|qt|rm|rmp4|rmvb|tp|trp|ts|vob|wmv)$' \
  | egrep -iv "$Movie_Filter" > $MoviesList
}

GenerateInsDelFiles()
# Generate insertion and deletion files
{
sed -i -e 's/\[/\&lsqb;/g' -e 's/\]/\&rsqb;/g' $MoviesList # Conversion of [] for grep
if [ -s "${PreviousMovieList}" ] ; then # because the grep -f don't work with empty file
  grep -vf $MoviesList "${PreviousMovieList}" | sed -e 's/\&lsqb;/\[/g' -e 's/\&rsqb;/\]/g' > $DeleteList
  grep -vf "${PreviousMovieList}" $MoviesList | sed -e 's/\&lsqb;/\[/g' -e 's/\&rsqb;/\]/g' > $InsertList
else
  cat $MoviesList | sed -e 's/\&lsqb;/\[/g' -e 's/\&rsqb;/\]/g' > $InsertList
fi
mv $MoviesList "${PreviousMovieList}"
}

DBMovieDelete()
# Delete records from the movies.db database.
{
echo "Removing movies from the Database ...."
while read LINE
do
  ${Sqlite} "${Database}"  "DELETE from t1 WHERE file='<file>${LINE}</file>'";
done < $DeleteList
${Sqlite} "${Database}"  "VACUUM";
}

DBMovieInsert()
# Add movies to the Database and extract movies posters/folders
{
rm "${UpdateLog}" 2>/dev/null
while read LINE
do
   MOVIEPATH="${LINE%/*}"  # Shell builtins instead of dirname
   MOVIEFILE="${LINE##*/}" # Shell builtins instead of basename
   MOVIENAME="${MOVIEFILE%.*}"  # Strip off .ext
   MOVIEEXT="${MOVIEFILE##*.}"  # only ext

   # Initialize defaults, replace later
   MOVIETITLE="$MOVIENAME</title>"
   MOVIESHEET=NoMovieinfo.jpg
   GENRE="<name>Unknown</name>"
   MovieYear=""
		
   [ -e "$MOVIEPATH/$MOVIENAME.nfo" ] && INFONAME=$MOVIENAME.nfo
   [ -e "$MOVIEPATH/MovieInfo.nfo" ] && INFONAME=MovieInfo.nfo
        
   [ -e "$MOVIEPATH/$INFONAME" ] && Infoparsing

if [ -z "$GENRE" ]; then dbgenre="<name>Unknown</name>"; else dbgenre="$GENRE"; fi
dbtitle=`echo "<title>$MOVIETITLE" | sed "s/'/''/g"`
dbpath=`echo "<path>$MOVIEPATH</path>" | sed "s/'/''/g"`
dbfile=`echo "<file>$MOVIENAME</file>" | sed "s/'/''/g"`
dbext=`echo "<ext>$MOVIEEXT</ext>" | sed "s/'/''/g"`
dbYear=$MovieYear

${Sqlite} "${Database}" "insert into t1 (genre,title,year,path,file,ext) values('$dbgenre','$dbtitle','$dbYear','$dbpath','$dbfile','$dbext');"; 2>> "${UpdateLog}"
echo '<channel> </channel>' # to maintain the signal
done < $InsertList
}

Update()
# Will update the Database based on the parameters in srjg.cfg
{

Header;
echo -e '<onEnter>
showIdle();
postMessage("return");
</onEnter>'

GenerateMovieList;

[ "$Imdb" = "yes" ] &&  ${Jukebox_Path}imdb.sh >/dev/null 2>&1
[ -n "$Force_DB_Update" ] && Force_DB_Creation
[ ! -f "${Database}" ] && CreateMovieDB
GenerateInsDelFiles;
[[ -s $DeleteList ]] && DBMovieDelete
[[ -s $InsertList ]] && DBMovieInsert

echo '<channel>'
Footer;
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
</onEnter>
<mediaDisplay name="nullView"/>
'

watch="`${Sqlite} -separator ''  "${Database}"  "SELECT Watched FROM t1 WHERE Movie_ID like '$CategoryTitle'";`"

if [ $watch == "1" ]; then
      watch="0";
else
     watch="1";
fi

${Sqlite} "${Database}" "UPDATE t1 set Watched=$watch WHERE Movie_ID like '$CategoryTitle'";

echo -e '<channel></channel></rss>'

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

UpdateMenu()
#Display UpdateMenu
{
cat <<EOF
<?xml version="1.0"   encoding="utf-8" ?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">

<onEnter>
		langpath = "${Jukebox_Path}lang/${Language}";
		langfile = loadXMLFile(langpath);
		if (langfile != null)
		{
			update_fast = getXMLText("update", "fast");
      update_rebuild = getXMLText("update", "rebuild");
		}
</onEnter>

<mediaDisplay name="photoView" rowCount="2" columnCount="1" drawItemText="no" showHeader="no" showDefaultInfo="no" menuBorderColor="255:255:255" sideColorBottom="-1:-1:-1" sideColorTop="-1:-1:-1" itemAlignt="left" itemOffsetXPC="41" itemOffsetYPC="75" itemWidthPC="20" itemHeightPC="7.2" backgroundColor="-1:-1:-1" itemBackgroundColor="-1:-1:-1" sliding="no" itemGap="0" idleImageXPC="90" idleImageYPC="5" idleImageWidthPC="5" idleImageHeightPC="8" imageUnFocus="null" imageParentFocus="null" imageBorderPC="0" forceFocusOnItem="no" cornerRounding="yes" itemBorderColor="-1:-1:-1" focusBorderColor="-1:-1:-1" unFocusBorderColor="-1:-1:-1">
<idleImage> image/POPUP_LOADING_01.png </idleImage>
<idleImage> image/POPUP_LOADING_02.png </idleImage>
<idleImage> image/POPUP_LOADING_03.png </idleImage>
<idleImage> image/POPUP_LOADING_04.png </idleImage>
<idleImage> image/POPUP_LOADING_05.png </idleImage>
<idleImage> image/POPUP_LOADING_06.png </idleImage>
<idleImage> image/POPUP_LOADING_07.png </idleImage>
<idleImage> image/POPUP_LOADING_08.png </idleImage>
<itemDisplay>

<image type="image/png" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
 <script>
  if (getDrawingItemState() == "focus")
  {
      print("${Jukebox_Path}images/focus_on.png");
  }
 else
  {
      print("${Jukebox_Path}images/focus_off.png");
  }
 </script>
</image>

<text redraw="no" offsetXPC="0" offsetYPC="0" widthPC="94" heightPC="100" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" fontSize="16" align="center">
 <script>
    getItemInfo(-1, "title");
 </script>
</text>
</itemDisplay>  

<onUserInput>

  userInput = currentUserInput();

  if (userInput == "right") {
    "true";
  } else if (userInput == "enter") {
    postMessage("return");
    "false";
  }

</onUserInput>
</mediaDisplay>

<channel>
<title>Updating</title>

<item>
<title><script>update_fast;</script></title>
<link>http://127.0.0.1:$Port/cgi-bin/srjg.cgi?Update@Fast@$Jukebox_Size</link>
</item>

<item>
<title><script>update_rebuild;</script></title>
<link>http://127.0.0.1:$Port/cgi-bin/srjg.cgi?Update@Rebuild@$Jukebox_Size</link>
</item>

</channel>
</rss>
EOF
}

MoviesheetView()
#Display moviesheet
{
InfoMediabd="`${Sqlite} -separator ''  "${Database}"  "SELECT path,file,ext FROM t1 WHERE Movie_ID like '$Search'`"
PathLink="`echo $InfoMediabd | sed 's:.*path>\(.*\)</path.*:\1:' | grep "[!-~]";`"
SheetFile="`echo $InfoMediabd | sed 's:.*file>\(.*\)</file.*:\1:'`"
FileLink="${PathLink}/${SheetFile}.`echo $InfoMediabd | sed 's:.*ext>\(.*\)</ext.*:\1:'`"

ImgLink="${PathLink}/${SheetFile}_sheet.jpg"
if [ ! -f "${ImgLink}" ]; then
  ImgLink="${PathLink}/about.jpg"
  if [ ! -f "${ImgLink}" ]; then
    ImgLink="${PathLink}/0001.jpg"
    if [ ! -f "${ImgLink}" ]; then
      ImgLink="${Jukebox_Path}images/NoMovieinfo.jpg"
    fi
  fi
fi

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
<image type="image/jpeg" redraw="no" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">$ImgLink</image>
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
			Jukebox_Path = "/usr/local/etc/srjg/";
			Language = "en";
        }
		else {
			Jukebox_Path = getXMLText("Config", "Jukebox_Path");
			Language = getXMLText("Config", "Lang");
		}
		
		DefaultView = getXMLText("Config", "Jukebox_Size");
            Category_Title = "'$CategoryTitle'";
	    Category_Background = "'${Jukebox_Path}'images/background.jpg";						           
            setFocusItemIndex(0);
            Current_Item_index=0;
            NewView = "'$NewView'";
            Genre_Title = Category_Title;
	    Jukebox_Size ="'$Jukebox_Size'";
	    mode = "'$mode'";
	    nextmode = "'$nextmode'";
		
		langpath = Jukebox_Path + "lang/" + Language;
		langfile = loadXMLFile(langpath);
		if (langfile != null)
		{
			jukebox_top = getXMLText("jukebox", "top");
		}

    /* array to keep update Watchcgi during views */
    AWatched="";
    AWatched_size=0;
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


if ([ $Jukebox_Size = "2x6" ] || [ $Jukebox_Size = "3x8" ]); then		
cat <<EOF
		<backgroundDisplay>
            <script>
                 Jukebox_itemSize = getPageInfo("itemCount"); 
			</script>
			<image type="image/jpeg" redraw="no" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
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
echo -e '
		<backgroundDisplay>
    <script>
      Jukebox_itemSize = getPageInfo("itemCount"); 
    </script>    
		</backgroundDisplay>
		
		<image type="image/jpeg" redraw="yes" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="80">
  <script>
    ItemPath  = getItemInfo(-1, "path");
    ItemFile = getItemInfo(-1, "file");
    SheetPath = ItemPath +"/"+ ItemFile +"_sheet.jpg";
    Etat = readStringFromFile(SheetPath);
    if (Etat==null){
      SheetPath = ItemPath +"/about.jpg";
      Etat = readStringFromFile(SheetPath);
      if (Etat==null){
        SheetPath = ItemPath +"/0001.jpg";
        Etat = readStringFromFile(SheetPath);
        if (Etat==null){
          SheetPath = "'${Jukebox_Path}'images/NoMovieinfo.jpg";
        }
      }
    }
    SheetPath;
  </script>
</image>
'

else
echo -e '
<backgroundDisplay>
  <script>
    Jukebox_itemSize = getPageInfo("itemCount"); 
  </script>    
</backgroundDisplay>
		
<image type="image/jpeg" redraw="yes" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
  <script>
    ItemPath  = getItemInfo(-1, "path");
    ItemFile = getItemInfo(-1, "file");
    SheetPath = ItemPath +"/"+ ItemFile +"_sheet.jpg";
    Etat = readStringFromFile(SheetPath);
    if (Etat==null){
      SheetPath = ItemPath +"/about.jpg";
      Etat = readStringFromFile(SheetPath);
      if (Etat==null){
        SheetPath = ItemPath +"/0001.jpg";
        Etat = readStringFromFile(SheetPath);
        if (Etat==null){
          SheetPath = "'${Jukebox_Path}'images/NoMovieinfo.jpg";
        }
      }
    }
    SheetPath;
  </script>
</image>
'

fi

if ([ $mode = "genreSelection" ] || [ $mode = "alphaSelection" ] || [ $mode = "yearSelection" ]); then
cat <<EOF	
		<image type="image/jpeg" redraw="yes" offsetXPC="80" offsetYPC="5.5" widthPC="8" heightPC="6">
				<script>
					print("${Jukebox_Path}images/"+Jukebox_Size+".jpg");
				</script>
    </image>
EOF
fi
	
cat <<EOF	
	<onUserInput>
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
					   Genre_Title=urlEncode(getItemInfo(-1, "title"));}
					   jumpToLink("NextView");
					   "false";
				}
EOF
	if ([ $mode = "genreSelection" ] || [ $mode = "alphaSelection" ] || [ $mode = "yearSelection" ]); then
cat <<EOF	
				else if (userInput == "one") {
                    Genre_Title=urlEncode(Genre_Title); 
					executeScript("SwitchView");
					"false";
					redrawDisplay();
				} 

EOF
fi

if ([ $mode = "genre" ] || [ $mode = "year" ] || [ $mode = "alpha" ] || [ $mode = "recent" ] || [ $mode = "notwatched" ]); then
cat <<EOF     

          else if (userInput == "two") {
                                        MovieID=getItemInfo(-1, "IdMovie"); 
          Item_Watched=getItemInfo(-1, "Watched"); /* get item info before exiting rss */
					jumpToLink("Watchcgi"); /* update database */
          executeScript("WatchUpdate"); /* update array AWatched */
					"false";
				}
EOF
	fi

cat << EOF
				  else if (userInput == "video_play") {
  Current_Movie_File=getItemInfo(-1, "path") +"/"+ getItemInfo(-1, "file") +"."+ getItemInfo(-1, "ext");
                                        playItemURL(Current_Movie_File, 10);
					"false";
					}
		</onUserInput>
EOF


if ([ $Jukebox_Size = "2x6" ] ||  [ $Jukebox_Size = "3x8" ]); then
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
<image type="image/jpeg" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
EOF
echo -e '
 <script>
  if (getDrawingItemState() == "focus")
  { if (getItemInfo(-1, "Watched") == "1") {
      "'${Jukebox_Path}'images/focus_watched.jpg";
      }
    else {
      "'${Jukebox_Path}'images/focus.jpg";
      }
  }
  else
  { if (getItemInfo(-1, "Watched") == "1") {
      "'${Jukebox_Path}'images/unfocus_watched.jpg";
      }
    else {
      "'${Jukebox_Path}'images/unfocus.jpg";
      }
  }
 </script>
</image>'


if [ "$mode" = "yearSelection" ]; then
echo -e '
<!-- Top Layer folder.jpg -->
<image type="image/jpeg" offsetXPC="8.2" offsetYPC="5.5" widthPC="84.25" heightPC="89.25">
 <script>
  thumbnailPath = "'${Jukebox_Path}'images/yearfolder.jpg";
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
<image type="image/jpeg" offsetXPC="8.2" offsetYPC="5.5" widthPC="84.25" heightPC="89.25">
 <script>
  ItemPath  = getItemInfo(-1, "path");
  ItemFile = getItemInfo(-1, "file");
  thumbnailPath = ItemPath +"/"+ ItemFile +".jpg";
  Etat = readStringFromFile(thumbnailPath);
  if (Etat==null){
    thumbnailPath = ItemPath +"/folder.jpg";
    Etat = readStringFromFile(thumbnailPath);
    if (Etat==null){
      thumbnailPath = "'${Jukebox_Path}'images/nofolder.jpg";
    }
  }
  thumbnailPath;
 </script>
</image>

<!-- Display watched icon -->
<image type="image/png" offsetXPC="3.2" offsetYPC="3.0" widthPC="20" heightPC="15">
<script>
  MovieID=getItemInfo(-1, "IdMovie");
  AWatched_found="false";
  AWatched_state="";
	i=0;
	while(i &lt; AWatched_size ){
    if (MovieID == getStringArrayAt(AWatched,i)) {
      AWatched_found="true";
      AWatched_state=getStringArrayAt(AWatched,add(i,1));
      break;
    }
		i += 2;
	}
  if ( AWatched_found == "true") {
    if ( AWatched_state == "1" ) "'${Jukebox_Path}'images/watched.png";
  } else {
    if (getItemInfo(-1, "Watched") == "1") "'${Jukebox_Path}'images/watched.png";
  }
</script>
</image>'

if [ "$mode" = "genreSelection" ]; then
echo -e '
<text offsetXPC="1" offsetYPC="75" widthPC="98" heightPC="13" fontSize="13" align="center" foregroundColor="255:255:255">
<script>
	getItemInfo(-1, "title");
</script>
</text>'

  fi # if "$mode" = "genreSelection"
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

<SRJGView>
    <link>
       <script>
			print(Jukebox_Path + "SrjgMainMenu.rss");
       </script>
    </link>
</SRJGView>
EOF

if ([ $mode = "genreSelection" ] || [ $mode = "alphaSelection" ] || [ $mode = "yearSelection" ]); then
cat <<EOF	

<SwitchView>
  if( Jukebox_Size == "2x6" ) Jukebox_Size="3x8";
	else if( Jukebox_Size == "3x8") Jukebox_Size="sheetwall";
	else Jukebox_Size="2x6";
</SwitchView>
EOF
fi

cat << EOF
<Watchcgi>
    <link>
       <script>
           print("http://127.0.0.1:$Port/cgi-bin/srjg.cgi?togglewatch@"+MovieID+"@"+Jukebox_Size);
       </script>
    </link>
</Watchcgi>

<WatchUpdate>
  /* find if also watched, remove it and do nothing */
  AWatched_found="false";

  i=0;
  while(i &lt; AWatched_size ){
    if (MovieID == getStringArrayAt(AWatched,i)) {
      AWatched_found="true";
      AWatched=deleteStringArrayAt(AWatched, i);
      AWatched=deleteStringArrayAt(AWatched, i);
      AWatched_size -=2;
      break;
    }
  	i += 2;
  }
  if ( AWatched_found != "true") {
    if (Item_Watched == "1" ) {
      Watched = 0;
    } else {
      Watched = 1;
    }
    AWatched=pushBackStringArray(AWatched, MovieID);
    AWatched=pushBackStringArray(AWatched, Watched);
    AWatched_size +=2;
  }
</WatchUpdate>

<channel>
	<title><script>Category_Title;</script></title>
	<link><script>Category_RSS;</script></link>
	<itemSize><script>Jukebox_itemSize;</script></itemSize>
EOF

if [ "$mode" = "genre" ]; then
   if [ "$Search" = "$AllMovies" ]; then
     ${Sqlite} -separator ''  "${Database}"  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,path,file,ext,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 ORDER BY title COLLATE NOCASE"; # All Movies
   else
      ${Sqlite} -separator ''  "${Database}"  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,path,file,ext,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 WHERE genre LIKE '%$Search%' ORDER BY title COLLATE NOCASE";
   fi   
fi

if [ "$mode" = "alpha" ]; then
if [ "$Search" = "0-9" ]; then
${Sqlite} -separator ''  "${Database}"  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,path,file,ext,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 WHERE title LIKE '<title>9%' OR title LIKE '<title>8%' OR title LIKE '<title>7%' OR title LIKE '<title>6%' OR title LIKE '<title>5%' OR title LIKE '<title>4%' OR title LIKE '<title>3%' OR title LIKE '<title>2%' OR title LIKE '<title>1%' OR title LIKE '<title>0%'";
else
${Sqlite} -separator ''  "${Database}"  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,path,file,ext,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 WHERE title LIKE '<title>$Search%' ORDER BY title COLLATE NOCASE";
fi
fi

if [ "$mode" = "year" ]; then
${Sqlite} -separator ''  "${Database}"  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,path,file,ext,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 WHERE year ='$Search' ORDER BY title COLLATE NOCASE";
fi

if [ "$mode" = "recent" ]; then
${Sqlite} -separator ''  "${Database}"  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,path,file,ext,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 ORDER BY datestamp DESC LIMIT "$Recent_Max;
fi

if [ "$mode" = "notwatched" ]; then
${Sqlite} -separator ''  "${Database}"  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,path,file,ext,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 WHERE watched <>'1' OR watched IS NULL ORDER BY title COLLATE NOCASE";
fi

if [ "$mode" = "moviesearch" ]; then
${Sqlite} -separator ''  "${Database}"  "SELECT header,IdMovhead,Movie_ID,IdMovFoot,title,path,file,ext,WatchedHead,watched,WatchedFoot,footer FROM t1,t2 WHERE title LIKE '<title>%$Search%' ORDER BY title COLLATE NOCASE";
fi

if [ "$mode" = "yearSelection" ]; then
# pulls out the years of the movies
${Sqlite} -separator ''  "${Database}"  "SELECT DISTINCT year FROM t1 ORDER BY year COLLATE NOCASE" > /tmp/srjg_year.list
while read LINE
do
echo "<item>"
echo "<title>"$LINE"</title>"
echo "</item>"
done < /tmp/srjg_year.list
fi


if [ "$mode" = "genreSelection" ]; then
  # pulls out the genre of the movies
  # The first line does the following: Pull data from database; remove all leading/trailing white spaces; sort and remove duplicate
  # remove possible empty line that may exist; remove any blank line
  # that may be still present.
  ${Sqlite} -separator ''  "${Database}"  "SELECT genre FROM t1" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' | sort -u | sed '/<name/!d;s:.*>\(.*\)</.*:\1:' | grep "[!-~]" > /tmp/srjg_genre.list

  # Add "All Movies" depending of the language, into the genre list
  sed -i 1i"$AllMovies" /tmp/srjg_genre.list
  while read LINE
  do
    # translate to find genre thumbnails 
    Img_genre=`sed "/|$LINE>/!d;s:.*>\(.*\)|:\1:" "${Jukebox_Path}lang/${Language}_genre"`
    if [ -z "$Img_genre" ] ; then Img_genre="Unknown"; fi
    echo -e '
    <item>
    <title>'$LINE'</title>
    <path>'${Jukebox_Path}'images/genre</path>
    <file>'$Img_genre'</file>
    </item>'
  done < /tmp/srjg_genre.list
fi

if [ "$mode" = "alphaSelection" ]; then
# pulls out the first letter of alphabet of the movie title
# The first line does the following: Pull data from database; remove the leading and trailing <title></title>; cut the title first 
# Character; remove anything that is not A-Z ex: a number; sort and remove duplicate.
${Sqlite} -separator ''  "${Database}"  "SELECT title FROM t1" | sed '/<title/!d;s:.*>\(.*\)</.*:\1:' | cut -c 1 | grep '[0-9A-Z]' | sort -u > /tmp/srjg_alpha.list
iteration="0";
while read LINE
do
if [ $LINE -eq $LINE 2> /dev/null ]; then   
if [ $iteration = "0" ]; then
iteration="1";
echo "<item>"
echo "<title>"0-9"</title>"
echo "<path>"${Jukebox_Path}"images/alpha</path>"
echo "<file>JukeMenu_Number</file>"
echo "</item>"
fi
else
echo "<item>"
echo "<title>"$LINE"</title>"
echo "<path>"${Jukebox_Path}"images/alpha</path>"
echo "<file>JukeMenu_"$LINE"</file>"
echo "</item>"
fi
done < /tmp/srjg_alpha.list
fi
}

MenuCfg()
# RSS to edit srjg.cfg
{
cat <<EOF
<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:media="http://purl.org/dc/elements/1.1/">

<onEnter>
  showIdle();
	Config = "/usr/local/etc/srjg.cfg";
  Config_ok = loadXMLFile(Config);
    
	if (Config_ok == null) {
		print("Load Config fail ", Config);
	}
    else {
        Config_itemSize = getXMLElementCount("Config");
	}

  if (Config_itemSize > 0) {
    Language = getXMLText("Config", "Lang");
		Jukebox_Path = getXMLText("Config", "Jukebox_Path");
		Jukebox_Size = getXMLText("Config", "Jukebox_Size");
		Movies_Path = getXMLText("Config", "Movies_Path");
    SingleDb = getXMLText("Config", "SingleDb");
		Movie_Filter = getXMLText("Config", "Movie_Filter");
		Port = getXMLText("Config", "Port");
		Recent_Max = getXMLText("Config", "Recent_Max");
    Imdb = getXMLText("Config", "Imdb");
		Imdb_Lang = getXMLText("Config", "Imdb_Lang");
		Imdb_Poster = getXMLText("Config", "Imdb_Poster");
		Imdb_PBox = getXMLText("Config", "Imdb_PBox");
		Imdb_PPost = getXMLText("Config", "Imdb_PPost");
		Imdb_Sheet = getXMLText("Config", "Imdb_Sheet");
		Imdb_SBox = getXMLText("Config", "Imdb_SBox");
		Imdb_SPost = getXMLText("Config", "Imdb_SPost");
		Imdb_Backdrop = getXMLText("Config", "Imdb_Backdrop");
		Imdb_Font = getXMLText("Config", "Imdb_Font");
		Imdb_Genres = getXMLText("Config", "Imdb_Genres");
    Imdb_Tagline = getXMLText("Config", "Imdb_Tagline");
    Imdb_Time = getXMLText("Config", "Imdb_Time");
    Imdb_Info = getXMLText("Config", "Imdb_Info");
  }
	 
  srjgconf="/tmp/srjg.cfg";
  tmpconfigArray=null;
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Language="+Language);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Jukebox_Path="+Jukebox_Path);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Movies_Path="+Movies_Path);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Movie_Filter="+Movie_Filter);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "SingleDb="+SingleDb);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Port="+Port);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Recent_Max="+Recent_Max);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb="+Imdb);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Lang="+Imdb_Lang);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Poster="+Imdb_Poster);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_PBox="+Imdb_PBox);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_PPost="+Imdb_PPost);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Sheet="+Imdb_Sheet);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_SBox="+Imdb_SBox);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_SPost="+Imdb_SPost);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Backdrop="+Imdb_Backdrop);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Font="+Imdb_Font);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Genres="+Imdb_Genres);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Tagline="+Imdb_Tagline);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Time="+Imdb_Time);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Info="+Imdb_Info);
  writeStringToFile(srjgconf, tmpconfigArray);
	 
  langpath = Jukebox_Path + "lang/" + Language;
  langfile = loadXMLFile(langpath);
  if (langfile != null) {
    cfg_lang = getXMLText("cfg", "Lang");
    cfg_Jukebox_Path = getXMLText("cfg", "Jukebox_Path");
    cfg_Jukebox_Size = getXMLText("cfg", "Jukebox_Size");
    cfg_Movies_Path = getXMLText("cfg", "Movies_Path");
    cfg_SingleDb = getXMLText("cfg", "SingleDb");
    cfg_Movie_Filter = getXMLText("cfg", "Movie_Filter");
    cfg_Imdb = getXMLText("cfg", "Imdb");
    cfg_Port = getXMLText("cfg", "Port");
    cfg_Version = getXMLText("cfg", "Version");
    cfg_Recent_Max = getXMLText("cfg", "Recent_Max");
    cfg_Yes = getXMLText("cfg", "yes");
    cfg_No = getXMLText("cfg", "no");
  }

  Version = readStringFromFile(Jukebox_Path + "Version");
  if ( Version == null ) print ("Version File not found");
</onEnter>

<mediaDisplay name="photoView" rowCount="7" columnCount="1" drawItemText="no" showHeader="no" showDefaultInfo="no" menuBorderColor="255:255:255" sideColorBottom="-1:-1:-1" sideColorTop="-1:-1:-1" itemAlignt="left" itemOffsetXPC="4" itemOffsetYPC="32" itemWidthPC="32" itemHeightPC="7.2" backgroundColor="-1:-1:-1" itemBackgroundColor="-1:-1:-1" sliding="no" itemGap="0" idleImageXPC="90" idleImageYPC="5" idleImageWidthPC="5" idleImageHeightPC="8" imageUnFocus="null" imageParentFocus="null" imageBorderPC="0" forceFocusOnItem="no" cornerRounding="yes" itemBorderColor="-1:-1:-1" focusBorderColor="-1:-1:-1" unFocusBorderColor="-1:-1:-1">
<idleImage> image/POPUP_LOADING_01.png </idleImage> 
<idleImage> image/POPUP_LOADING_02.png </idleImage> 
<idleImage> image/POPUP_LOADING_03.png </idleImage> 
<idleImage> image/POPUP_LOADING_04.png </idleImage> 
<idleImage> image/POPUP_LOADING_05.png </idleImage> 
<idleImage> image/POPUP_LOADING_06.png </idleImage> 
<idleImage> image/POPUP_LOADING_07.png </idleImage> 
<idleImage> image/POPUP_LOADING_08.png </idleImage> 

<!-- comment menu display -->
<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="36" offsetYPC="35" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		print(Language);
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="36" offsetYPC="43" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		print(Movies_Path);
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="36" offsetYPC="51" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( SingleDb == "yes" ) print( cfg_Yes );
    else print( cfg_No );
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="36" offsetYPC="59" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		print(Movie_Filter);
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="36" offsetYPC="67" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		print(Jukebox_Size);
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="36" offsetYPC="75" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		print(Recent_Max);
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="36" offsetYPC="83" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( Imdb == "yes" ) print( cfg_Yes );
    else print( cfg_No );
	</script>
</text>

<!-- info display -->
<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="59" offsetYPC="10" widthPC="37" heightPC="4" fontSize="16" lines="1" align="center">
	<script>
		print(cfg_Jukebox_Path);
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="59" offsetYPC="14" widthPC="37" heightPC="4" fontSize="13" lines="1" align="center">
	<script>
		print(Jukebox_Path);
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="65" offsetYPC="18" widthPC="23" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		print(cfg_Port);
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="75" offsetYPC="18" widthPC="10" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		print(Port);
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="65" offsetYPC="22" widthPC="10" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		print(cfg_Version);
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="75" offsetYPC="22" widthPC="10" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		print(Version);
	</script>
</text>

<onUserInput>
  <script>
    userInput = currentUserInput();
	
    if (userInput == "enter" ) {
      indx=getFocusItemIndex();
      mode=getItemInfo(indx, "selection");
      if ( mode == "Movie_Filter") {
        inputFilter=getInput("userName","doModal");
        if (inputFilter != NULL) {
          mode="UpdateCfg";
          YPos="Movie_Filter";
          SelParam=inputFilter;
					jumpToLink("SelectionEntered");
        }
      } else
        SelParam=getItemInfo(indx, "param");
        YPos=getItemInfo(indx, "pos");
        jumpToLink("SelectionEntered");
			}
      "false";
    }
  </script>
</onUserInput>

 
<itemDisplay>

<image type="image/png" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
 <script>
  if (getDrawingItemState() == "focus")
  {
      print(Jukebox_Path + "images/focus_on.png");
  }
 else
  {
      print(Jukebox_Path + "images/focus_off.png");
  }
 </script>
</image>

<text redraw="no" offsetXPC="0" offsetYPC="0" widthPC="94" heightPC="100" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" fontSize="16" align="center">
 <script>
    getItemInfo(-1, "title");
 </script>
</text>
</itemDisplay>  

   <backgroundDisplay>
        <image type="image/jpeg" redraw="no" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
	     <script>
                 print(Jukebox_Path + "images/srjgMainMenu.jpg");
             </script>
        </image>
    </backgroundDisplay> 

</mediaDisplay>

<SelectionEntered>
    <link>
       <script>
           print("http://127.0.0.1:"+Port+"/cgi-bin/srjg.cgi?"+mode+"@"+SelParam+"@"+YPos);
       </script>
    </link>
</SelectionEntered>

<channel>
<title>Config menu</title>

<item>
<title>
	<script>
		print(cfg_lang);
	</script>
</title>
<selection>Lang</selection>
<param>en%20fr%20pl</param>
<pos>25</pos>
</item>

<item>
<title>
	<script>
		print(cfg_Movies_Path);
	</script>
</title>
<selection>FBrowser</selection>
<param></param>
<pos></pos>
</item>

<item>
<title>
	<script>
		print(cfg_SingleDb);
	</script>
</title>
<selection>SingleDb</selection>
<param>yes%20no</param>
<pos>43</pos>
</item>

<item>
<title>
	<script>
		print(cfg_Movie_Filter);
	</script>
</title>
<selection>Movie_Filter</selection>
<param></param>
<pos></pos>
</item>

<item>
<title>
	<script>
		print(cfg_Jukebox_Size);
	</script>
</title>
<selection>Jukebox_Size</selection>
<param>2x6%203x8%20sheetwall</param>
<pos>43</pos>
</item>

<item>
<title>
	<script>
		print(cfg_Recent_Max);
	</script>
</title>
<selection>Recent_Max</selection>
<param>10%2025%2050%2075%20100</param>
<pos>50</pos>
</item>

<item>
<title>
	<script>
		print(cfg_Imdb);
	</script>
</title>
<selection>ImdbCfgEdit</selection>
<param></param>
<pos></pos>
</item>

</channel>
</rss>
EOF
}

FBrowser()
# File browser
# Original code from DMD RM Jukebox by Martini(CZ) from DMD team
#    Contact: w0m@seznam.cz, http://www.hddplayer.cz
# Modified and adapted to the srjg project
{
cat <<EOF
<?xml version='1.0' ?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">

<onEnter> 
  Jukebox_Path="$Jukebox_Path";
  langpath = Jukebox_Path + "lang/$Language";
  langfile = loadXMLFile(langpath);
  if (langfile != null) {
		FBrowser_Title = getXMLText("FBrowser", "FBrowser_Title");
		FBrowser_Valid = getXMLText("FBrowser", "FBrowser_Valid");
  }
  dirCount=0;
  dir2File = "/tmp/srjg_Browser_dir.list";
  dirArray = null;
  Ch_Base = "/tmp/public/";
  Ch_Sel = Ch_Base;
  executeScript("listDir");
  setFocusItemIndex(0);
  RedrawDisplay();
</onEnter>

<mediaDisplay name="onePartView" sideLeftWidthPC="0" sideColorLeft="0:0:0" sideRightWidthPC="0" fontSize="14" focusFontColor="210:16:16" itemAlignt="center" viewAreaXPC=29.7 viewAreaYPC=26 viewAreaWidthPC=40 viewAreaHeightPC=50 headerImageWidthPC="0" itemImageHeightPC="0" itemImageWidthPC="0" itemXPC="10" itemYPC="15" itemWidthPC="80" itemHeightPC="10" itemBackgroundColor="0:0:0" itemPerPage="6" itemGap="0" infoYPC="90" infoXPC="90" backgroundColor="0:0:0" showHeader="no" showDefaultInfo="no">
<idleImage> image/POPUP_LOADING_01.png </idleImage>
<idleImage> image/POPUP_LOADING_02.png </idleImage>
<idleImage> image/POPUP_LOADING_03.png </idleImage>
<idleImage> image/POPUP_LOADING_04.png </idleImage>
<idleImage> image/POPUP_LOADING_05.png </idleImage>
<idleImage> image/POPUP_LOADING_06.png </idleImage>
<idleImage> image/POPUP_LOADING_07.png </idleImage>
<idleImage> image/POPUP_LOADING_08.png </idleImage>

<backgroundDisplay>
  <image type="image/png" offsetXPC=0 offsetYPC=0 widthPC=100 heightPC=100>
    <script>print(Jukebox_Path + "images/FBrowser_Bg.jpg");</script>
  </image>
</backgroundDisplay>

<text align="center" offsetXPC=0 offsetYPC=0 widthPC=100 heightPC=10 fontSize=14 backgroundColor=-1:-1:-1    foregroundColor=70:140:210>
  <script>print(FBrowser_Title);</script>
</text>

<image redraw="no" offsetXPC="10" offsetYPC="90.5" widthPC="9" heightPC="7.2">
  <script>print(Jukebox_Path + "images/play.png");</script>
</image>

<text align="left" offsetXPC=20.5 offsetYPC=89 widthPC=33 heightPC=10 fontSize=12 backgroundColor=-1:-1:-1    foregroundColor=200:200:200>
<script>print(FBrowser_Valid);</script>
</text>

<text redraw="yes" align="center" offsetXPC=2 offsetYPC=75 widthPC=96 heightPC=10 fontSize=10 backgroundColor=0:0:0 foregroundColor=200:150:0>
   <script>
		    curidx = getFocusItemIndex();
		    if (curidx != 0) {
		      New = getStringArrayAt(pathArray, curidx);
		    } else {
		      New = Ch_Sel;
		    }
        print(New);
    </script>
</text>

<itemDisplay>
  <image type="image/png" redraw="yes" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
    <script>
  if (getDrawingItemState() == "focus")
  {
      print(Jukebox_Path + "images/focus_on.png");
  }
 else
  {
      print(Jukebox_Path + "images/FBrowser_unfocus.png");
  }
    </script>
  </image>
  <image type="image/png" redraw="yes" offsetXPC="0" offsetYPC="25" widthPC="8" heightPC="50">
    <script>
					  Jukebox_Path +"images/folder.png";
    </script>
  </image>
  <text redraw="yes" offsetXPC="6" offsetYPC="0" widthPC="94" heightPC="100" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" fontSize="15">
   <script>
      getStringArrayAt(titleArray , -1);
   </script>
  </text>
</itemDisplay>

<onUserInput>
	userInput = currentUserInput();

	if ( userInput == "enter" || userInput == "right"){
		    curidx = getFocusItemIndex();
		    Ch_Sel = getStringArrayAt(pathArray, curidx);
		    executeScript("listDir");
  
        setFocusItemIndex(0);
        RedrawDisplay();
        "true";

  } else if ( userInput == "video_play" ) {
		    curidx = getFocusItemIndex();
		    if (curidx != 0) {
		      New_Ch_Base = getStringArrayAt(pathArray, curidx);
		    } else {
		      New_Ch_Base = Ch_Sel;
		    }
        New_Ch_Base=urlEncode(New_Ch_Base);
        dlok = loadXMLFile("http://127.0.0.1:80/cgi-bin/srjg.cgi?UpdateCfg@"+New_Ch_Base+"@Movies_Path");
        postMessage("return");
        "true";

  } else if ( userInput == "left") {
        setFocusItemIndex(0);
        postMessage("enter");
        "true";
  }
</onUserInput>
</mediaDisplay>

<listDir>
    writeStringToFile(dir2File, Ch_Sel);
    dlok = loadXMLFile("http://127.0.0.1:80/cgi-bin/srjg.cgi?DirList");
    test="";
    dirArray=null;
    titleArray=null;
    pathArray=null;
    idx=0;
    dirArray = readStringFromFile(dir2File);
    while (test != " ") {
      if (idx==0) {
          title = "..";
          path = getStringArrayAt(dirArray, idx);
      } else {
        test = getStringArrayAt(dirArray, idx);
        if (test == "*") test = " ";
        if (test != " ") {  
          title = test;
          path = Ch_Sel + test + "/";
        }
      }

      titleArray = pushBackStringArray(titleArray,title);
      pathArray = pushBackStringArray(pathArray,path);
      
      idx=Add(idx,1);
    }
    dirCount=idx - 1;
</listDir>

<item_template>
       <displayTitle>
            <script>
				getStringArrayAt(titleArray , -1);
			</script>
        </displayTitle>
        <media:thumbnail>
            <script>
			url = Jukebox_Path + "folder.png";
     	print("thumbnail:");
     	print(url);
     	url;
			</script>
        </media:thumbnail>
      		<media:content type="image/jpeg" />  
		<onClick>
			print("onClick");
		</onClick>
</item_template>
<channel>
        <title></title>
  <itemSize>
     <script>
        dirCount;
     </script>
  </itemSize>
</channel>
</rss>
EOF
}

UpdateCfg()
# Update the srjg.cfg
{
cat <<EOF
<?xml version="1.0" ?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
<onEnter>
showIdle();
postMessage("return");
</onEnter>
<mediaDisplay name="nullView"/>
EOF

Cfg_Tag=$Jukebox_Size
Cfg_Par=$CategoryTitle

if [ $Cfg_Tag = "Movies_Path" ]; then
  sed -i "s:<$Cfg_Tag>.*</$Cfg_Tag>:<$Cfg_Tag>\"$Cfg_Par\"</$Cfg_Tag>:" /usr/local/etc/srjg.cfg
else
  sed -i "s:<$Cfg_Tag>.*</$Cfg_Tag>:<$Cfg_Tag>$Cfg_Par</$Cfg_Tag>:" /usr/local/etc/srjg.cfg
fi

cat <<EOF
<channel></channel></rss>
EOF

exit 0
}

DirList()
# List HDD or Usb devices
{
cat <<EOF
<?xml version="1.0" ?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
<onEnter>
showIdle();
postMessage("return");
</onEnter>
<mediaDisplay name="nullView"/>
EOF

folder=`sed -n '1p' /tmp/srjg_Browser_dir.list`

dirname=${folder%/*}
prevdir=${dirname%/*}

echo $prevdir"/" > /tmp/srjg_Browser_dir.list

cd "$folder"
echo */ " " | sed "s/\/ /\n/g"  >> /tmp/srjg_Browser_dir.list

cat <<EOF
<channel></channel></rss>
EOF

exit 0
}

SubMenucfg()
# auto choice menu to edit cfg
{

Item_nb=0
for Item_lst in $CategoryTitle
do
  let Item_nb+=1
done

YPos=$Jukebox_Size

cat <<EOF
<?xml version="1.0"   encoding="utf-8" ?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">

<onEnter>
</onEnter>

<mediaDisplay name="photoView" rowCount="$Item_nb" columnCount="1" drawItemText="no" showHeader="no" showDefaultInfo="no" menuBorderColor="255:255:255" sideColorBottom="-1:-1:-1" sideColorTop="-1:-1:-1" itemAlignt="left" itemOffsetXPC="10" itemOffsetYPC="$YPos" itemWidthPC="20" itemHeightPC="7.2" backgroundColor="-1:-1:-1" itemBackgroundColor="-1:-1:-1" sliding="no" itemGap="0" idleImageXPC="90" idleImageYPC="5" idleImageWidthPC="5" idleImageHeightPC="8" imageUnFocus="null" imageParentFocus="null" imageBorderPC="0" forceFocusOnItem="no" cornerRounding="yes" itemBorderColor="-1:-1:-1" focusBorderColor="-1:-1:-1" unFocusBorderColor="-1:-1:-1">
<idleImage> image/POPUP_LOADING_01.png </idleImage>
<idleImage> image/POPUP_LOADING_02.png </idleImage>
<idleImage> image/POPUP_LOADING_03.png </idleImage>
<idleImage> image/POPUP_LOADING_04.png </idleImage>
<idleImage> image/POPUP_LOADING_05.png </idleImage>
<idleImage> image/POPUP_LOADING_06.png </idleImage>
<idleImage> image/POPUP_LOADING_07.png </idleImage>
<idleImage> image/POPUP_LOADING_08.png </idleImage>
<itemDisplay>

<image offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
 <script>
  if (getDrawingItemState() == "focus")
  {
      print("${Jukebox_Path}images/focus_on.png");
  }
 else
  {
      print("${Jukebox_Path}images/focus_off.png");
  }
 </script>
</image>

<text redraw="no" offsetXPC="0" offsetYPC="0" widthPC="94" heightPC="100" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" fontSize="16" align="center">
 <script>
    getItemInfo(-1, "title");
 </script>
</text>
</itemDisplay>  

<onUserInput>

  userInput = currentUserInput();

  if (userInput == "right") {
    "true";
  } else if (userInput == "enter") {
    postMessage("return");
    "false";
  }

</onUserInput>
</mediaDisplay>

<channel>
<title>Updating Cfg</title>
EOF

Item_nb=0
for Item_lst in $CategoryTitle
do
  case ${Item_lst} in
    "yes") Item_dspl=`sed "/<yes>/!d;s:.*>\(.*\)<.*:\1:" "${Jukebox_Path}lang/${Language}"`;;
    "no")  Item_dspl=`sed "/<no>/!d;s:.*>\(.*\)<.*:\1:" "${Jukebox_Path}lang/${Language}"`;;
    *)     Item_dspl=$Item_lst;;
  esac
cat <<EOF
<item>
<title>$Item_dspl</title>
<link>http://127.0.0.1:$Port/cgi-bin/srjg.cgi?UpdateCfg@$Item_lst@$mode</link>
</item>
EOF
done

cat <<EOF
</channel>
</rss>
EOF
}

ImdbSheetDspl()
# fullscreen display demo Imdb sheet
{
cat <<EOF
<?xml version="1.0"?>
<rss version="2.0" xmlns:media="http://purl.org/dc/elements/1.1/" xmlns:dc="http://purl.org/dc/elements/1.1/">

<onEnter>
  showIdle();
  redrawDisplay();
</onEnter>

<mediaDisplay name=photoView showHeader=no showDefaultInfo=no drawItemBorder=no viewAreaXPC=0 viewAreaYPC=0 viewAreaWidthPC=100 viewAreaHeightPC=100 itemOffsetXPC=0 itemOffsetYPC=0 sideTopHeightPC=0 sideBottomHeightPC=0 bottomYPC=100 backgroundColor=0:0:0 >
<idleImage> image/POPUP_LOADING_01.png </idleImage> 
<idleImage> image/POPUP_LOADING_02.png </idleImage> 
<idleImage> image/POPUP_LOADING_03.png </idleImage> 
<idleImage> image/POPUP_LOADING_04.png </idleImage> 
<idleImage> image/POPUP_LOADING_05.png </idleImage> 
<idleImage> image/POPUP_LOADING_06.png </idleImage> 
<idleImage> image/POPUP_LOADING_07.png </idleImage> 
<idleImage> image/POPUP_LOADING_08.png </idleImage> 

<backgroundDisplay>

<text redraw="no" align="left" offsetXPC="25" offsetYPC="50" widthPC="100" heightPC="6" fontSize="20" backgroundColor="-1:-1:-1" foregroundColor="255:255:255">
  <script>print("Press 1 to refresh...");</script>
</text>

<script>
	LnParam="name=avatar&amp;box=$Imdb_SBox&amp;mode=sheet&amp;font=$Imdb_Font&amp;lang=$Imdb_Lang";
  if ( "$Imdb_Backdrop" != "no" ) LnParam=LnParam+"&amp;backdrop=y";
  if ( "$Imdb_SPost" != "no" ) LnParam=LnParam+"&amp;post=y";
  if ( "$Imdb_SBox" != "no" ) LnParam=LnParam+"&amp;box=$Imdb_SBox";
	if ( "$Imdb_Tagline" != "no" ) LnParam=LnParam+"&amp;tagline=y";
	if ( "$Imdb_Time" != "no" ) LnParam=LnParam+"&amp;time=$Imdb_Time";
  if ( "$Imdb_Genres" != "no" ) LnParam=LnParam+"&amp;genres=$Imdb_Genres";
  ImdbLink = "http://playon.unixstorm.org/IMDB/movie.php?" + LnParam;
</script>
	
<image offsetXPC=5 offsetYPC=5 widthPC=90 heightPC=90><script> print(ImdbLink); </script></image>

</backgroundDisplay>

<onUserInput>
	userInput = currentUserInput();
  redrawDisplay();
</onUserInput>
</mediaDisplay>

<channel>
<title>SheetView Imdb</title>

</channel>
</rss>
EOF
}

ImdbCfgEdit()
# Imdb Config editor
{

cat <<EOF
<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:media="http://purl.org/dc/elements/1.1/">

<onEnter>
  showIdle();
	Config = "/usr/local/etc/srjg.cfg";
  Config_ok = loadXMLFile(Config);
    
	if (Config_ok == null) {
		print("Load Config fail ", Config);
	}
    else {
        Config_itemSize = getXMLElementCount("Config");
	}
    
  if (Config_itemSize > 0) {
    Language = getXMLText("Config", "Lang");
		Jukebox_Path = getXMLText("Config", "Jukebox_Path");
		Jukebox_Size = getXMLText("Config", "Jukebox_Size");
		Movies_Path = getXMLText("Config", "Movies_Path");
    SingleDb = getXMLText("Config", "SingleDb");
		Movie_Filter = getXMLText("Config", "Movie_Filter");
		Port = getXMLText("Config", "Port");
		Recent_Max = getXMLText("Config", "Recent_Max");
    Imdb = getXMLText("Config", "Imdb");
		Imdb_Lang = getXMLText("Config", "Imdb_Lang");
		Imdb_Poster = getXMLText("Config", "Imdb_Poster");
		Imdb_PBox = getXMLText("Config", "Imdb_PBox");
		Imdb_PPost = getXMLText("Config", "Imdb_PPost");
		Imdb_Sheet = getXMLText("Config", "Imdb_Sheet");
		Imdb_SBox = getXMLText("Config", "Imdb_SBox");
		Imdb_SPost = getXMLText("Config", "Imdb_SPost");
		Imdb_Backdrop = getXMLText("Config", "Imdb_Backdrop");
		Imdb_Font = getXMLText("Config", "Imdb_Font");
		Imdb_Genres = getXMLText("Config", "Imdb_Genres");
    Imdb_Tagline = getXMLText("Config", "Imdb_Tagline");
    Imdb_Time = getXMLText("Config", "Imdb_Time");
    Imdb_Info = getXMLText("Config", "Imdb_Info");
  }
	 
  srjgconf="/tmp/srjg.cfg";
  tmpconfigArray=null;
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Language="+Language);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Jukebox_Path="+Jukebox_Path);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Movies_Path="+Movies_Path);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Movie_Filter="+Movie_Filter);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "SingleDb="+SingleDb);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Port="+Port);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Recent_Max="+Recent_Max);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb="+Imdb);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Lang="+Imdb_Lang);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Poster="+Imdb_Poster);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_PBox="+Imdb_PBox);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_PPost="+Imdb_PPost);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Sheet="+Imdb_Sheet);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_SBox="+Imdb_SBox);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_SPost="+Imdb_SPost);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Backdrop="+Imdb_Backdrop);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Font="+Imdb_Font);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Genres="+Imdb_Genres);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Tagline="+Imdb_Tagline);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Time="+Imdb_Time);
  tmpconfigArray=pushBackStringArray(tmpconfigArray, "Imdb_Info="+Imdb_Info);
  writeStringToFile(srjgconf, tmpconfigArray);
	
  /* Translated values */ 
  langpath = Jukebox_Path + "lang/" + Language;
  langfile = loadXMLFile(langpath);
  if (langfile != null) {
    cfg_Imdb = getXMLText("cfg", "Imdb");
    cfg_Yes = getXMLText("cfg", "yes");
    cfg_No = getXMLText("cfg", "no");
    cfgI_Use=getXMLText("Imdb", "Imdb_Use");
    cfgI_Lang=getXMLText("Imdb", "Imdb_Lang");
    cfgI_Poster=getXMLText("Imdb", "Imdb_Poster");
    cfgI_PBox=getXMLText("Imdb", "Imdb_PBox");
    cfgI_PPost=getXMLText("Imdb", "Imdb_PPost");
    cfgI_Sheet=getXMLText("Imdb", "Imdb_Sheet");
    cfgI_SBox=getXMLText("Imdb", "Imdb_SBox");
    cfgI_SPost=getXMLText("Imdb", "Imdb_SPost");
    cfgI_Backdrop=getXMLText("Imdb", "Imdb_Backdrop");
    cfgI_Font=getXMLText("Imdb", "Imdb_Font");
    cfgI_Genres=getXMLText("Imdb", "Imdb_Genres");
    cfgI_Tagline=getXMLText("Imdb", "Imdb_Tagline");
    cfgI_Time=getXMLText("Imdb", "Imdb_Time");
    cfgI_Info=getXMLText("Imdb", "Imdb_Info");
  }
</onEnter>

<mediaDisplay name="photoView" rowCount="14" columnCount="1" drawItemText="no" showHeader="no" showDefaultInfo="no" menuBorderColor="255:255:255" sideColorBottom="-1:-1:-1" sideColorTop="-1:-1:-1" itemAlignt="left" itemOffsetXPC="4" itemOffsetYPC="10" itemWidthPC="30" itemHeightPC="5" backgroundColor="-1:-1:-1" itemBackgroundColor="-1:-1:-1" sliding="no" itemGap="0" idleImageXPC="90" idleImageYPC="5" idleImageWidthPC="5" idleImageHeightPC="8" imageUnFocus="null" imageParentFocus="null" imageBorderPC="0" forceFocusOnItem="no" cornerRounding="yes" itemBorderColor="-1:-1:-1" focusBorderColor="-1:-1:-1" unFocusBorderColor="-1:-1:-1">
<idleImage> image/POPUP_LOADING_01.png </idleImage> 
<idleImage> image/POPUP_LOADING_02.png </idleImage> 
<idleImage> image/POPUP_LOADING_03.png </idleImage> 
<idleImage> image/POPUP_LOADING_04.png </idleImage> 
<idleImage> image/POPUP_LOADING_05.png </idleImage> 
<idleImage> image/POPUP_LOADING_06.png </idleImage> 
<idleImage> image/POPUP_LOADING_07.png </idleImage> 
<idleImage> image/POPUP_LOADING_08.png </idleImage> 

<!-- covert display -->
<image type="image/jpeg" offsetXPC="68" offsetYPC="4" widthPC="14" heightPC="40">
  <script>
    if ( Imdb == "no" || Imdb_Poster == "no" ) "${Jukebox_Path}images/nofolder.jpg";
    else {
	    LnParam="name=avatar&amp;mode=poster";
      if ( Imdb_PBox != "no" ) LnParam=LnParam+"&amp;box="+Imdb_PBox;
	    if ( Imdb_PPost != "no" ) LnParam=LnParam+"&amp;post=y";
      "http://playon.unixstorm.org/IMDB/movie.php?" + LnParam;
    }
  </script>
</image>

<script>

</script>
	
<image offsetXPC="47" offsetYPC="46" widthPC="65" heightPC="50">
  <script>
    if ( Imdb == "no" || Imdb_Sheet == "no" ) "${Jukebox_Path}images/NoMovieinfo.jpg";
    else {
	    LnParam="name=avatar&amp;box="+Imdb_SBox+"&amp;mode=sheet&amp;font="+Imdb_Font+"&amp;lang="+Imdb_Lang;
      if ( Imdb_Backdrop != "no" ) LnParam=LnParam+"&amp;backdrop=y";
      if ( Imdb_SPost != "no" ) LnParam=LnParam+"&amp;post=y";
      if ( Imdb_SBox != "no" ) LnParam=LnParam+"&amp;box="+Imdb_SBox;
	    if ( Imdb_Tagline != "no" ) LnParam=LnParam+"&amp;tagline=y";
	    if ( Imdb_Time != "no" ) LnParam=LnParam+"&amp;time="+Imdb_Time;
      if ( Imdb_Genres != "no" ) LnParam=LnParam+"&amp;genres="+Imdb_Genres;
      "http://playon.unixstorm.org/IMDB/movie.php?" + LnParam;
    }
  </script>
</image>


<!-- comment menu display -->
<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="12" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( Imdb == "yes" ) print( cfg_Yes );
    else print( cfg_No );
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="18" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		print(Imdb_Lang);
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="24" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( Imdb_Poster == "yes" ) print( cfg_Yes );
    else print( cfg_No );
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="30" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( Imdb_PBox == "no" ) print( cfg_No );
    else print( Imdb_PBox );
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="36" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( Imdb_PPost == "yes" ) print( cfg_Yes );
    else print( cfg_No );
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="42" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( Imdb_Sheet == "yes" ) print( cfg_Yes );
    else print( cfg_No );
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="48" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( Imdb_SBox == "no" ) print( cfg_No );
    else print( Imdb_SBox );
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="54" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( Imdb_SPost == "yes" ) print( cfg_Yes );
    else print( cfg_No );
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="60" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( Imdb_Backdrop == "yes" ) print( cfg_Yes );
    else print( cfg_No );
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="66" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		print(Imdb_Font);
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="72" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( Imdb_Genres == "yes" ) print( cfg_Yes );
    else print( cfg_No );
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="78" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( Imdb_Tagline == "yes" ) print( cfg_Yes );
    else print( cfg_No );
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="84" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( Imdb_Time == "no" ) print( cfg_No );
    else print( Imdb_Time );
	</script>
</text>

<text redraw="no" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" offsetXPC="34" offsetYPC="90" widthPC="57" heightPC="4" fontSize="16" lines="1" align="left">
	<script>
		if ( Imdb_Info == "yes" ) print( cfg_Yes );
    else print( cfg_No );
	</script>
</text>

<onUserInput>
  <script>
    userInput = currentUserInput();
	
    if (userInput == "enter" ) {
      indx=getFocusItemIndex();
      mode=getItemInfo(indx, "selection");
      SelParam=getItemInfo(indx, "param");
      YPos=getItemInfo(indx, "pos");
      jumpToLink("SelectionEntered");
      "false";
    }	else if (userInput == "one") {
		  mode="ImdbSheetDspl";
			jumpToLink("SelectionEntered");
			"false";
    }	else if (userInput == "two") {
      redrawDisplay();
			"false";
    }
  </script>
</onUserInput>

 
<itemDisplay>

<image type="image/png" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
 <script>
  if (getDrawingItemState() == "focus")
  {
      print(Jukebox_Path + "images/focus_on.png");
  }
 else
  {
      print(Jukebox_Path + "images/focus_off.png");
  }
 </script>
</image>

<text redraw="no" offsetXPC="0" offsetYPC="0" widthPC="94" heightPC="100" backgroundColor="-1:-1:-1" foregroundColor="200:200:200" fontSize="13" align="center">
 <script>
    getItemInfo(-1, "title");
 </script>
</text>
</itemDisplay>  

  <backgroundDisplay>
    <image type="image/jpeg" redraw="no" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
      <script>
        print(Jukebox_Path + "images/srjgMainMenu.jpg");
      </script>
    </image>
  </backgroundDisplay> 
</mediaDisplay>

<SelectionEntered>
    <link>
       <script>
           print("http://127.0.0.1:"+Port+"/cgi-bin/srjg.cgi?"+mode+"@"+SelParam+"@"+YPos);
       </script>
    </link>
</SelectionEntered>

<channel>
<title>Imdb Config menu</title>

<item>
<title>
	<script>
		print(cfgI_Use);
	</script>
</title>
<selection>Imdb</selection>
<param>yes%20no</param>
<pos>10</pos>
</item>

<item>
<title>
	<script>
		print(cfgI_Lang);
	</script>
</title>
<selection>Imdb_Lang</selection>
<param>en%20fr</param>
<pos>17</pos>
</item>

<item>
<title>
	<script>
		print(cfgI_Poster);
	</script>
</title>
<selection>Imdb_Poster</selection>
<param>yes%20no</param>
<pos>10</pos>
</item>

<item>
<title>
	<script>
		print(cfgI_PBox);
	</script>
</title>
<selection>Imdb_PBox</selection>
<param>no%20bdrip%20bluray%20dtheater%20dvd%20generic%20hddvd%20hdtv%20itunes</param>
<pos>21</pos>
</item>

<item>
<title>
	<script>
		print(cfgI_PPost);
	</script>
</title>
<selection>Imdb_PPost</selection>
<param>yes%20no</param>
<pos>60</pos>
</item>

<item>
<title>
	<script>
		print(cfgI_Sheet);
	</script>
</title>
<selection>Imdb_Sheet</selection>
<param>yes%20no</param>
<pos>10</pos>
</item>

<item>
<title>
	<script>
		print(cfgI_SBox);
	</script>
</title>
<selection>Imdb_SBox</selection>
<param>no%20bdrip%20bluray%20dtheater%20dvd%20generic%20hddvd%20hdtv%20itunes</param>
<pos>21</pos>
</item>

<item>
<title>
	<script>
		print(cfgI_SPost);
	</script>
</title>
<selection>Imdb_SPost</selection>
<param>yes%20no</param>
<pos>60</pos>
</item>

<item>
<title>
	<script>
		print(cfgI_Backdrop);
	</script>
</title>
<selection>Imdb_Backdrop</selection>
<param>yes%20no</param>
<pos>25</pos>
</item>

<item>
<title>
	<script>
		print(cfgI_Font);
	</script>
</title>
<selection>Imdb_Font</selection>
<param>arial%20bookman%20comic%20tahoma%20times%20verdana</param>
<pos>43</pos>
</item>

<item>
<title>
	<script>
		print(cfgI_Genres);
	</script>
</title>
<selection>Imdb_Genres</selection>
<param>yes%20no</param>
<pos>50</pos>
</item>

<item>
<title>
	<script>
		print(cfgI_Tagline);
	</script>
</title>
<selection>Imdb_Tagline</selection>
<param>yes%20no</param>
<pos>70</pos>
</item>

<item>
<title>
	<script>
		print(cfgI_Time);
	</script>
</title>
<selection>Imdb_Time</selection>
<param>no%20real%20hours</param>
<pos>70</pos>
</item>

<item>
<title>
	<script>
		print(cfgI_Info);
	</script>
</title>
<selection>Imdb_Info</selection>
<param>yes%20no</param>
<pos>70</pos>
</item>

</channel>
</rss>
EOF
}

#***********************Main Program*********************************

case $mode in
  "togglewatch") WatchedToggle;;
  "Update")
    if [ "$CategoryTitle" = "Rebuild" ]; then
      Force_DB_Update="y"
      Update
    elif [ "$CategoryTitle" = "Fast" ]; then
      Force_DB_Update=""
      Update
    else
      UpdateMenu;
    fi;;
  "moviesheet")
    Header
    MoviesheetView
    Footer;;
  Lang|Jukebox_Size|SingleDb|Port|Recent_Max|Imdb|Imdb_Lang|\
  Imdb_Poster|Imdb_PBox|Imdb_PPost|Imdb_Sheet|\
  Imdb_SBox|Imdb_SPost|Imdb_Backdrop|Imdb_Font|\
  Imdb_Genres|Imdb_Tagline|Imdb_Time|Imdb_Info) SubMenucfg;;
  "UpdateCfg") UpdateCfg;;
  "DirList") DirList;;
  "FBrowser") FBrowser;;
  "MenuCfg") MenuCfg;;
	"ImdbSheetDspl") ImdbSheetDspl;;
  "ImdbCfgEdit") ImdbCfgEdit;;
  *)
    SetVar
    Header
    DisplayRss
    Footer;;
esac

exit 0

