#!/bin/sh
# Simple RSS Jukebox Generator -> DB to HTML converter
# Author: mikka [mika.hellmann@gmail.com]
# Modified by Snappy46 [levesque.marcel@gmail.com]
# Demo: http://members.home.nl/hellmann/

# Paths
SRJGPATH="`sed '/<Jukebox_Path/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"
MOVPATH="`sed '/<Movies_Path/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"
DB2HTML="$SRJGPATH/db2html"		# Main path to db2html
DBFILE="$MOVPATH/SRJG/movies.db"	# Path to movies.db
SQLPATH="$SRJGPATH/sqlite3"		# Path to sqlite binary
DEFPOSTER="$SRJGPATH/nofolder.jpg"
DEFSHEET="$SRJGPATH/NoMovieinfo.jpg"
TMPTITLE="/tmp/srjg_title"
TMPPOSTER="/tmp/srjg_poster"
TMPSHEET="/tmp/srjg_sheet"
TMPFILE="/tmp/srjg_file"

COLUMNS=10						# Number of columns to be created
WIDTH=85						# Width of poster to be displayed
HEIGHT=128						# Height of poster to be displayed
IDX=1;							# Starting index
COUNT=1;						# Starting counter

USECATEG=0						# Create categories (default Off)
USEDATE=0						# Display creation date (default Off)
USESHEET=0						# Include moviesheets (default Off)
USETITLE=0						# Show title (default Off)

usage()
{
cat << EOF
Usage: $0 options
Example: $0 -o /home/JukeboxHTML/ -c -d -m -t -p tar

This script converts SRJG movies.db to HTML jukebox. 

OPTIONS:
   -h      Show this message
   -o      Output path to HTML jukebox (Optional) 
   -p      Type of archive: [tar] (Optional)
   -c	   Create alphabetical page categories (Optional, no argument needed)
   -d	   Generate creation date (Optional, no argument needed)
   -m	   Include moviesheets (Optional, no argument needed)
   -t	   Enable displaying movie title (Optional, no argument needed)
   
   
NOTES:  If any of the path arguments have spaces in them they must be surrounded by quotes: ""
        Output path has to be ending with slash: /
EOF
exit 1
}

while getopts o:p:cdmth OPTION 
do
  case $OPTION in  
	 o)	MAINPATH=$OPTARG	;;
     p)	PACK=$OPTARG		;;
     c)	USECATEG=1			;;  	   
     d)	USEDATE=1			;;  
     m)	USESHEET=1			;;
     t)	USETITLE=1			;;
     h)	usage				;;
   esac
done


# If output path to HTML jukebox has NOT been provided, use main path from movies.db
if [ -z "$MAINPATH" ]
then
  MAINPATH="$MOVPATH"
fi

# Initialize title and paths
HTMLPATH="$MAINPATH"SRJG
IMGPATH="$HTMLPATH"/images

# If image path doesn't exist, create folder for HTML jukebox
if [ ! -d "$IMGPATH" ];
then
  echo "Creating $IMGPATH.."
  mkdir -p "$IMGPATH"
fi

# Create symlink to HTML jukebox
mount -o remount,rw /
rm -f /tmp/www/srjg
rm -f /tmp_orig/www/srjg
ln -sf "$HTMLPATH" /tmp/www/srjg
ln -sf "$HTMLPATH" /tmp_orig/www/srjg
  
  
# Default template header
echo '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><head>
<title>SRJG Jukebox</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<link rel="StyleSheet" type="text/css" href="s.css">
</head>

<body onloadset="nextlink" focuscolor="#FDDB2B" focustext="#000000" bgproperties="fixed" style="background-position: center top; background-repeat: no-repeat;" background="images/b.jpg" bgcolor="#000000">
<table align="center" width="1100"><tbody><tr><td>
<div class="title" align="center"><font color="#colortitle">Jukebox</font></div>' > "$HTMLPATH/index.html"

# Creating /hdd symlink
if [ $USETITLE = 1 ];
then
  rm -f /tmp/www/hdd
  rm -f /tmp_orig/www/hdd
  ln -sf "$MOVPATH" /tmp/www/hdd
  ln -sf "$MOVPATH" /tmp_orig/www/hdd
fi

if [ $USEDATE = 1 ];
then
  echo "<br>Created on `date +"%Y-%m-%d %H:%M:%S"` with <b>db2html</b><br>" >> "$HTMLPATH/index.html"
fi

if [ $USECATEG = 1 ];
then
  echo '<br><div class="navigation" align="center">-' >> "$HTMLPATH/index.html"
		  
  for x in A B C D E F G H I J K L M N O P Q R S T U W X Y Z
  do
	echo '<a href="'"#$x"'">'"$x"'</a> -' >> "$HTMLPATH/index.html"
  done
  
  echo '</div><br>' >> "$HTMLPATH/index.html"
fi
  
  	    
echo '<br><br><table align="center" cellpadding="1"><tbody><tr>' >> "$HTMLPATH/index.html"

# Get all titles and links
"$SQLPATH" -separator '' "$DBFILE" "SELECT title FROM t1 ORDER BY title COLLATE NOCASE" | sed -n '/<title>/,/<\/title>/s/.*<title>\(.*\)<\/title>/\1/p' > "$TMPTITLE"

"$SQLPATH" -separator '' "$DBFILE" "SELECT poster FROM t1 ORDER BY title COLLATE NOCASE" | sed -n '/<poster>/,/<\/poster>/s/.*<poster>\(.*\)<\/poster>/\1/p' > "$TMPPOSTER"

"$SQLPATH" -separator '' "$DBFILE" "SELECT info FROM t1 ORDER BY title COLLATE NOCASE" | sed -n '/<info>/,/<\/info>/s/.*<info>\(.*\)<\/info>/\1/p' > "$TMPSHEET"

"$SQLPATH" -separator '' "$DBFILE" "SELECT file FROM t1 ORDER BY title COLLATE NOCASE" | sed -n '/<file>/,/<\/file>/s/.*<file>\(.*\)<\/file>/\1/p' | sed "s|$MOVPATH|/hdd/|" > "$TMPFILE"

echo "Movies found: `sed -n '$=' "$TMPTITLE"`"  

# Copy basic files
echo "Copying basic files.."
cp "$DB2HTML/b.jpg" "$DB2HTML/defposter.jpg" "$DB2HTML/defsheet.jpg" "$IMGPATH"
cp "$DB2HTML/s.css" "$HTMLPATH"

# Main loop
while read MOVIE
do
  echo "Processing $IDX: $MOVIE.."
  
  POSTER="`sed -n "$IDX"p "$TMPPOSTER"`"
  if [ "$POSTER" != "$DEFPOSTER" ];
  then
	cp "$POSTER" "$IMGPATH/p$IDX.jpg" 
	SHOWPOSTER="images/p$IDX.jpg"
  else
    SHOWPOSTER="images/defposter.jpg"
  fi 

  
  if [ $USESHEET = 1 ];
  then
	SHEET="`sed -n "$IDX"p "$TMPSHEET"`"
	
	if [ "$SHEET" != "$DEFSHEET" ];
	then
	  cp "$SHEET" "$IMGPATH/m$IDX.jpg"
	  SHOWSHEET="images/m$IDX.jpg"
	else
      SHOWSHEET="images/defsheet.jpg"
	fi
	
  else
    SHOWSHEET="#"
  fi
  
 
  if [ $USETITLE = 1 ];
  then
    TITLE="`sed -n "$IDX"p "$TMPFILE"`"
	SHOWTITLE='<br><strong><a href="'"$TITLE"'">'$MOVIE'</a></strong><br><br>'
  else
    SHOWTITLE=""
  fi
  
  
  if [ $USECATEG = 1 ];
  then
    L=`echo "$MOVIE" | cut -c1`
	SHOWCATEG='name="'$L'"'
  else
    SHOWCATEG=""
  fi
  
  echo '<td valign="top" width="'"$WIDTH"'" height="'"$HEIGHT"'"><center><a href="'"$SHOWSHEET"'" title="'"$MOVIE"'" '"$SHOWCATEG"' id="thumbimage"><img src="'"$SHOWPOSTER"'" width="'"$WIDTH"'" height="'"$HEIGHT"'"></a>'"$SHOWTITLE"'</center></td>' >> "$HTMLPATH/index.html"

  if [ $COUNT != $COLUMNS ];
  then
    let COUNT=$COUNT+1;
  else
    COUNT=1;
    echo '</tr><tr>' >> "$HTMLPATH/index.html"
  fi
  
  let IDX=$IDX+1 
done < "$TMPTITLE"


# Default template footer
echo '</tr></tbody></table></td></tr>'$SHOWDATE'</tbody></table></body></html>' >> "$HTMLPATH/index.html"

echo "Jukebox saved into $HTMLPATH/"

# Pack everything
if [ "$PACK" == "tar" ];
then
  echo "Packing into "$MAINPATH"html.tar.."
  tar -c -f "$MAINPATH"html.tar -C "$MAINPATH" HTML/
fi
