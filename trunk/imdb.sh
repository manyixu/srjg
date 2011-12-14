#!/bin/sh
# Simple RSS Jukebox Generator -> IMDB plugin
# Author: mikka [mika.hellmann@gmail.com]
# Modified by Snappy46 [levesque.marcel@gmail.com]
# Documentation: http://playon.unixstorm.org/imdb.php

IMDB_LINK="http://playon.unixstorm.org/IMDB/movie.php?name="			# Link to IMDB API [DO NOT CHANGE, unless you are requested to do so]
IMDB_INFO="&mode=info"													# Parameters for generating info file
IMDB_MOVIE="&mode=sheet&backdrop=y&box=bluray&source=y&tagline=y"		# Parameters for generating moviesheet
IMDB_POSTER="&mode=poster"												# Parameters for generating poster

IMDB_TMP="/tmp/movies.list"				# Path to the list of movies [DO NOT CHANGE, unless you are requested to do so]
IMDB_MODE="all"							# all: Generate everything (moviesheet, nfo, poster)
										# images: Generate both moviesheet and poster
										# moviesheet: Generate only moviesheet
										# nfo: Generate .nfo file only
										# poster: Generate only poster
										
IMDB_TITLE="directory"					# directory: Use directory name for IMDB search
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
	
	
	# Replace special characters with plus sign
    MOVIENAME=`echo $MOVIENAMETEMP | sed "s/[ &']/+/g"`
	
	# Download poster
	if ( [ -n $POSTER ] && [ ! -e "$MOVIEPATH/folder.jpg" ] && [ ! -e "$MOVIEPATH/${MOVIEFILE}.jpg" ] )
	then
		echo "Processing $MOVIENAMETEMP poster.."
		wget -q "$IMDB_LINK$MOVIENAME$IMDB_POSTER" -O "$MOVIEPATH/${MOVIEFILE}.jpg" ;
		
		# TODO: Check generated poster
		#if ( [ -e "$MOVIEPATH/$IMDB_DEFPOSTER" ] && [ "`du "$MOVIEPATH/$IMDB_DEFPOSTER" | cut -f1`" -lt 2000 ] )
		#then
		#	cat "$MOVIEPATH/$IMDB_DEFPOSTER"
		#	rm -f "$MOVIEPATH/$IMDB_DEFPOSTER"
		#fi
	fi

	# Download moviesheet
	if ( [ -n $MOVIESHEET ] && [ ! -e "$MOVIEPATH/about.jpg" ] && [ ! -e "$MOVIEPATH/0001.jpg" ] && [ ! -e "$MOVIEPATH/${MOVIEFILE}_sheet.jpg" ] )
	then
		echo "Processing $MOVIENAMETEMP moviesheet.."
		wget -q "$IMDB_LINK$MOVIENAME$IMDB_MOVIE" -O "$MOVIEPATH/${MOVIEFILE}_sheet.jpg" ;
		
		# TODO: Check generated moviesheet
		#if ( [ -e "$MOVIEPATH/$IMDB_DEFMOVIE" ] && [ "`du "$MOVIEPATH/$IMDB_DEFMOVIE" | cut -f1`" -lt 2000 ] )
		#then
		#	cat "$MOVIEPATH/$IMDB_DEFMOVIE"
		#	rm -f "$MOVIEPATH/$IMDB_DEFMOVIE"
		#fi
	fi
	
	# Download NFO file
	if ( [ -n $INFO ] && [ ! -e "$MOVIEPATH/$MOVIEFILE.nfo" ] && [ ! -e "$MOVIEPATH/MovieInfo.nfo" ] )
	then
		echo "Processing $MOVIENAMETEMP nfo file.."
		wget -q "$IMDB_LINK$MOVIENAME$IMDB_INFO" -O "$MOVIEPATH/${MOVIEFILE}.nfo" ;
		
		# TODO: Check generated nfo file (at least if <title> section exists)
		#if ( [ -e "$MOVIEPATH/$IMDB_DEFMOVIE" ] && [ "`du "$MOVIEPATH/$IMDB_DEFMOVIE" | cut -f1`" -lt 2000 ] )
		#then
		#	cat "$MOVIEPATH/$IMDB_DEFMOVIE"
		#	rm -f "$MOVIEPATH/$IMDB_DEFMOVIE"
		#fi
	fi
	
done < "$IMDB_TMP"

echo "Finished IMDB API.."