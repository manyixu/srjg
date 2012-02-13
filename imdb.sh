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

IMDB_LINK="http://playon.unixstorm.org/IMDB/movie.php?name="			# Link to IMDB API [DO NOT CHANGE, unless you are requested to do so]
IMDB_INFO="&mode=info"													# Parameters for generating info file
IMDB_MOVIE="&mode=sheet&backdrop=y&box=bluray&post=y&tagline=y&lang=${Lang}"		# Parameters for generating moviesheet
IMDB_POSTER="&mode=poster"												# Parameters for generating poster

IMDB_TMP="/tmp/srjg_movies.list"				# Path to the list of movies [DO NOT CHANGE, unless you are requested to do so]
IMDB_MODE="all"							# all: Generate everything (moviesheet, nfo, poster)
										# images: Generate both moviesheet and poster
										# moviesheet: Generate only moviesheet
										# nfo: Generate .nfo file only
										# poster: Generate only poster
										
IMDB_TITLE="filename"					# directory: Use directory name for IMDB search
										# filename: Use filename for IMDB search


# Initialize variables
MOVIESHEET=""
POSTER=""									
INFO=""
						
# Create moviesheets by calling IMDB API
echo "Starting IMDB API.."

# Check running mode
if ( [ $IMDB_MODE = "moviesheet" ] || [ $IMDB_MODE = "images" ] || [ $IMDB_MODE = "all" ] )
then
  MOVIESHEET="y"
fi

if ( [ $IMDB_MODE = "poster" ] || [ $IMDB_MODE = "images" ] || [ $IMDB_MODE = "all" ] )
then
  POSTER="y"
fi

if ( [ $IMDB_MODE = "nfo" ] || [ $IMDB_MODE = "all" ] )
then
  INFO="y"
fi


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
	if ( [ -n $POSTER ] && [ ! -e "$MOVIEPATH/folder.jpg" ] && [ ! -e "$MOVIEPATH/${MOVIEFILE}.jpg" ] )
	then
		echo "Processing $MOVIENAMETEMP poster.."
		NAME="$MOVIEPATH/${MOVIEFILE}.jpg"
		wget -q "$IMDB_LINK$MOVIENAME$IMDB_POSTER" -O "$NAME";

		# Check generated poster
		PATT=`grep Movie "$NAME"`
		if ( [ -e "$NAME" ] && [ -n "$PATT" ] )
		then
			echo `cat "$NAME"`
			rm -f "$NAME"
		fi
	fi

	# Download moviesheet
	if ( [ -n $MOVIESHEET ] && [ ! -e "$MOVIEPATH/about.jpg" ] && [ ! -e "$MOVIEPATH/0001.jpg" ] && [ ! -e "$MOVIEPATH/${MOVIEFILE}_sheet.jpg" ] )
	then
		echo "Processing $MOVIENAMETEMP moviesheet.."
		NAME="$MOVIEPATH/${MOVIEFILE}_sheet.jpg"
		wget -q "$IMDB_LINK$MOVIENAME$IMDB_MOVIE" -O "$NAME" ;
		
		# Check generated moviesheet
		PATT=`grep Movie "$NAME"`
		if ( [ -e "$NAME" ] && [ -n "$PATT" ] )
		then
			echo `cat "$NAME"`
			rm -f "$NAME"
		fi
	fi
	
	# Download NFO file
	if ( [ -n $INFO ] && [ ! -e "$MOVIEPATH/$MOVIEFILE.nfo" ] && [ ! -e "$MOVIEPATH/MovieInfo.nfo" ] )
	then
		echo "Processing $MOVIENAMETEMP nfo file.."
		NAME="$MOVIEPATH/${MOVIEFILE}.nfo"
		wget -q "$IMDB_LINK$MOVIENAME$IMDB_INFO" -O "$NAME" ;
		
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
