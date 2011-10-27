#!/bin/sh
# Simple RSS Jukebox Generator: XML to HTML converter
# Author: Snappy46 [levesque.marcel@gmail.com]

# Default SRJG poster and moviesheet
DEFPOSTER="/usr/local/etc/srjg/nofolder.bmp"
DEFSHEET="/usr/local/etc/srjg/NoMovieinfo.bmp"
TMPPOSTER="/tmp/poster"
TMPSHEET="/tmp/sheet"

APPDIR="${0%/*}"				# Main path to xml2html
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
Example: xml2html.sh -j "/home/AKCJA, PRZYGODOWE, SENSACYJNE/jukebox.xml" -o /home/JukeboxHTML/ -p tar

This script converts SRJG jukebox.xml to HTML jukebox. 

OPTIONS:
   -h      Show this message
   -j      Input path to jukebox.xml (Required) 
   -o      Output path to HTML jukebox (Optional) 
   -p      Type of archive: [tar] (Optional)
   -c	   Create alphabetical page categories (Optional, no argument needed)
   -d	   Generate creation date (Optional, no argument needed)
   -m	   Include moviesheets (Optional, no argument needed)
   -t	   Enable displaying movie title (Optional, no argument needed)
   
   
NOTES:  If any of the path arguments have spaces in them they must be surrounded by quotes: ""
           
EOF
exit 1
}

while getopts j:o:p:cdmth OPTION 
do
  case $OPTION in
     j)	XMLPATH=$OPTARG		;;     
	 o)	MAINPATH=$OPTARG	;;
     p)	PACK=$OPTARG		;;
     c)	USECATEG=1			;;  	   
     d)	USEDATE=1			;;  
     m)	USESHEET=1			;;
     t)	USETITLE=1			;;
     h)	usage				;;
   esac
done

# Check if required path to XML jukebox has been provided
if [ -z "$XMLPATH" ]
then
  echo "A filename must be specified using -o argument."
  usage
  exit 1
fi

# If output path to HTML jukebox has NOT been provided, use main path from jukebox.xml
if [ -z "$MAINPATH" ]
then
  MAINPATH=`sed -n '/<Path>/,/<\/Path>/s/.*<Path>\(.*\)<\/Path>/\1/p' "$XMLPATH" | head -1`
fi

# Initialize title and paths
MAINTITLE=`sed -n '/<jukeboxheading>/,/<\/jukeboxheading>/s/.*<jukeboxheading>\(.*\)<\/jukeboxheading>/\1/p' "$XMLPATH" | head -1`
HTMLPATH="$MAINPATH"HTML
IMGPATH="$HTMLPATH"/images

# If image path doesn't exist, create folder for HTML jukebox
if [ ! -d "$IMGPATH" ];
then
  echo "Creating $IMGPATH.."
  mkdir -p "$IMGPATH"
fi

# Default template header
echo '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><head>
<title>'$MAINTITLE'</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<link rel="StyleSheet" type="text/css" href="s.css">
</head>

<body onloadset="nextlink" focuscolor="#FDDB2B" focustext="#000000" bgproperties="fixed" style="background-position: center top; background-repeat: no-repeat;" background="images/b.jpg" bgcolor="#000000">
<table align="center" width="1100"><tbody><tr><td>
<div class="title" align="center"><font color="#colortitle">Jukebox '$MAINTITLE'</font></div>' > "$HTMLPATH/index.html"

if [ $USEDATE = 1 ];
then
  echo "<br>Created on `date +"%Y-%m-%d %H:%M:%S"` with <b>xml2html</b><br>" >> "$HTMLPATH/index.html"
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

# Get all links
sed -n '/<poster>/,/<\/poster>/s/.*<poster>\(.*\)<\/poster>/\1/p' "$XMLPATH" > "$TMPPOSTER"
sed -n '/<info>/,/<\/info>/s/.*<info>\(.*\)<\/info>/\1/p' "$XMLPATH" > "$TMPSHEET"

echo "Movies found: `sed -n '/<title>/,/<\/title>/s/.*<title>\(.*\)<\/title>/\1/p' "$XMLPATH" | sed -n '$='`"  

# Copy basic files
echo "Copying basic files.."
cp "$APPDIR/b.jpg" "$APPDIR/defposter.jpg" "$APPDIR/defsheet.jpg" "$IMGPATH"
cp "$APPDIR/s.css" "$HTMLPATH"


# Main loop
sed -n '/<title>/,/<\/title>/s/.*<title>\(.*\)<\/title>/\1/p' "$XMLPATH"  | while read MOVIE
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
    SHOWTITLE="<br><strong>$MOVIE</strong><br><br>"
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
done


# Default template footer
echo '</tr></tbody></table></td></tr>'$SHOWDATE'</tbody></table></body></html>' >> "$HTMLPATH/index.html"

echo "Jukebox saved into $HTMLPATH/"

# Pack everything
if [ "$PACK" == "tar" ];
then
  echo "Packing into "$MAINPATH"html.tar.."
  tar -c -f "$MAINPATH"html.tar -C "$MAINPATH" HTML/
fi
