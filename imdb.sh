#!/bin/sh
# Simple RSS Jukebox Generator -> IMDB plugin
# Author: mikka [mika.hellmann@gmail.com]
# Modified by Snappy46 [levesque.marcel@gmail.com]
# Documentation: http://playon.unixstorm.org/imdb.php

IMDB_LINK="http://playon.unixstorm.org/IMDB/movie.php?name="			# DO NOT CHANGE, unless you are requested to do so
IMDB_INFO="&mode=info"													# Parameters for generating info file
IMDB_MOVIE="&mode=sheet&backdrop=y&box=bluray&source=y&tagline=y"		# Parameters for generating moviesheet
IMDB_POSTER="&mode=poster&box=bluray"									# Parameters for generating poster

IMDB_DEFPOSTER="folder.jpg"				# Name of poster file
IMDB_DEFMOVIE="0001.jpg"				# Name of moviesheet file
# IMDB_DEFMOVIE="`date +"%Y-%m-%d_%H-%M-%S".jpg`"    # only for testing purposes

IMDB_TMP="/tmp/movie.list"				# Path to the list of movies
IMDB_MODE="moviesheet"					# all: Generate everything (moviesheet, nfo, poster)
										# images: Generate both moviesheet and poster
										# moviesheet: Generate only moviesheet
										# nfo: Generate .nfo file only
										# poster: Generate only poster
										
IMDB_TITLE="directory"					# directory: Use directory name for IMDB search
										# filename: Use filename for IMDB search


# Initialize variables
MOVIESHEET="n"
POSTER="n"									
INFO="n"
						
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
	
	# Get movie name
	if [ $IMDB_TITLE = "directory" ];
	then
		MOVIEFILE="${MOVIEPATH##*/}"		# Extract directory name
	else
		MOVIEEXT="${LINE##*/}"				# Extract filename 
        MOVIEFILE="${MOVIEEXT%.*}"     		# Remove extension
	fi
	
	# Replace special characters with plus sign
    MOVIENAME=`echo $MOVIEFILE | sed "s/[ &']/+/g"`
	
	# Download poster
	if ( [ $POSTER = "y" ] && [ ! -e "$MOVIEPATH/folder.jpg" ] && [ ! -e "$MOVIEPATH/${MOVIEFILE}.jpg" ] )
	then
		echo "Processing $MOVIEFILE poster.."
		wget -q "$IMDB_LINK$MOVIENAME$IMDB_POSTER" -O "$MOVIEPATH/$IMDB_DEFPOSTER" ;
		
		# Check generated poster
		if ( [ -e "$MOVIEPATH/$IMDB_DEFPOSTER" ] && [ "`du "$MOVIEPATH/$IMDB_DEFPOSTER" | cut -f1`" -lt 2000 ] )
		then
			cat "$MOVIEPATH/$IMDB_DEFPOSTER"
			rm -f "$MOVIEPATH/$IMDB_DEFPOSTER"
		fi
	fi

	# Download moviesheet
	if ( [ $MOVIESHEET = "y" ] && [ ! -e "$MOVIEPATH/about.jpg" ] && [ ! -e "$MOVIEPATH/${MOVIEFILE}_sheet.jpg" ] && [ ! -e "$MOVIEPATH/0001.jpg" ] )
	then
		echo "Processing $MOVIEFILE moviesheet.."
		wget -q "$IMDB_LINK$MOVIENAME$IMDB_MOVIE" -O "$MOVIEPATH/$IMDB_DEFMOVIE" ;
		
		# Check generated moviesheet
		if ( [ -e "$MOVIEPATH/$IMDB_DEFMOVIE" ] && [ "`du "$MOVIEPATH/$IMDB_DEFMOVIE" | cut -f1`" -lt 2000 ] )
		then
			cat "$MOVIEPATH/$IMDB_DEFMOVIE"
			rm -f "$MOVIEPATH/$IMDB_DEFMOVIE"
		fi
	fi
	
	
	# TODO:
	# Download NFO file
	if ( [ $INFO = "y" ] && [ ! -e "$MOVIEPATH/${MOVIEFILE}.nfo" ] )	
	then
		echo "Processing $MOVIEFILE nfo file.."
		wget -q "$IMDB_LINK$MOVIENAME$IMDB_INFO" -O "$MOVIEPATH/${MOVIEFILE}.nfo" ;
	fi
	
done < "$IMDB_TMP"

echo "Finished IMDB API.."