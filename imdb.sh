#!/bin/sh
# Simple RSS Jukebox Generator -> IMDB plugin
# Author: mikka [mika.hellmann@gmail.com]
# Modified by Snappy46 [levesque.marcel@gmail.com]
# Documentation: http://playon.unixstorm.org/imdb.php

# Reading/parsing xml configuration file and assign variables.

CfgFile=/usr/local/etc/srjg.cfg
if [ ! -f "${CfgFile}" ]; then
  echo "Configuration file not found: ${CfgFile}"
  exit 1
fi
sed '1d;$d;s:<\(.*\)>\(.*\)</.*>:\1=\2:' ${CfgFile} >/tmp/srjg.cfg
. /tmp/srjg.cfg

PAR_LINK="http://playon.unixstorm.org/IMDB/movie.php?name="			# Link to IMDB API [DO NOT CHANGE, unless you are requested to do so]
PAR_INFO="&mode=info"													# Parameters for generating info file

PAR_SHEET="&mode=sheet&box=$Imdb_SBox&lang=$Imdb_Lang&font=$Imdb_Font"		# Parameters for generating moviesheet
if [ $Imdb_Backdrop != "no" ]; then PAR_SHEET="$PAR_SHEET&backdrop=y"; fi
if [ $Imdb_SBox != "no" ]; then PAR_SHEET="$PAR_SHEET&box=$Imdb_SBox"; fi
if [ $Imdb_SPost != "no" ]; then PAR_SHEET="$PAR_SHEET&post=y"; fi
if [ $Imdb_Tagline != "no" ]; then PAR_SHEET="$PAR_SHEET&tagline=y"; fi
if [ $Imdb_Time != "no" ]; then PAR_SHEET="$PAR_SHEET&time=$Imdb_Time"; fi
if [ $Imdb_Genres != "no" ]; then PAR_SHEET="$PAR_SHEET&genres=$Imdb_Genres"; fi

PAR_POSTER="&mode=poster"												# Parameters for generating poster
if [ $Imdb_PBox != "no" ]; then PAR_POSTER="$PAR_POSTER&box=$Imdb_PBox"; fi
if [ $Imdb_PPost != "no" ]; then PAR_POSTER="$PAR_POSTER&post=y"; fi

IMDB_TMP="/tmp/srjg_movies.list"				# Path to the list of movies [DO NOT CHANGE, unless you are requested to do so]
										
IMDB_TITLE="filename"					# directory: Use directory name for IMDB search
										# filename: Use filename for IMDB search
						
# Create moviesheets by calling IMDB API
echo "Starting IMDB API.."

# Loop through all movies
while read LINE
do
	MOVIEPATH="${LINE%/*}"					# Extract whole path
	MOVIEEXT="${LINE##*/}"					# Extract filename 
	MOVIEFILE="${MOVIEEXT%.*}"     			# Remove extension from filename
	
	# Get movie name
	if [ $IMDB_TITLE = "directory" ];
	then
		MOVIENAMETEMP="${MOVIEPATH##*/}"		# Use directory as moviename
	else
        MOVIENAMETEMP="$MOVIEFILE"				# Use file as moviename
	fi
	
	
	# Remove CD parts and replace special characters with plus sign
    MOVIENAME=`echo $MOVIENAMETEMP | sed "s/[cC][dD]*[1-9]//g" | sed "s/[ &']/+/g"`
	
	# Download poster
	if ( [ $Imdb_Poster = "yes" ] && [ ! -e "$MOVIEPATH/folder.jpg" ] && [ ! -e "$MOVIEPATH/${MOVIEFILE}.jpg" ] )
	then
		echo "Processing $MOVIENAMETEMP poster.."
		NAME="$MOVIEPATH/${MOVIEFILE}.jpg"
		wget -q "$PAR_LINK$MOVIENAME$PAR_POSTER" -O "$NAME";

		# Check generated poster
		PATT=`grep Movie "$NAME"`
		if ( [ -e "$NAME" ] && [ -n "$PATT" ] )
		then
			echo `cat "$NAME"`
			rm -f "$NAME"
		fi
	fi

	# Download moviesheet
	if ( [ $Imdb_Sheet = "yes" ] && [ ! -e "$MOVIEPATH/about.jpg" ] && [ ! -e "$MOVIEPATH/0001.jpg" ] && [ ! -e "$MOVIEPATH/${MOVIEFILE}_sheet.jpg" ] )
	then
		echo "Processing $MOVIENAMETEMP moviesheet.."
		NAME="$MOVIEPATH/${MOVIEFILE}_sheet.jpg"
		wget -q "$PAR_LINK$MOVIENAME$PAR_SHEET" -O "$NAME" ;
		
		# Check generated moviesheet
		PATT=`grep Movie "$NAME"`
		if ( [ -e "$NAME" ] && [ -n "$PATT" ] )
		then
			echo `cat "$NAME"`
			rm -f "$NAME"
		fi
	fi
	
	# Download NFO file
	if ( [ $Imdb_Info = "yes" ] && [ ! -e "$MOVIEPATH/$MOVIEFILE.nfo" ] && [ ! -e "$MOVIEPATH/MovieInfo.nfo" ] )
	then
		echo "Processing $MOVIENAMETEMP nfo file.."
		NAME="$MOVIEPATH/${MOVIEFILE}.nfo"
		wget -q "$PAR_LINK$MOVIENAME$PAR_INFO" -O "$NAME" ;
		
		# Check generated nfo file
		PATT=`grep title "$NAME"`
		if ( [ -e "$NAME" ] && [ -z "$PATT" ] )
		then
			echo `cat "$NAME"`
			rm -f "$NAME"
		fi
	fi
	
done < "$IMDB_TMP"

echo "Finished IMDB API.."
