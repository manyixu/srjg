#!/bin/sh
# srjg Version 5.0
# http://code.google.com/p/srjg/
# based on the srjg PlayOn!HD Original work by Mikka.
# Programmed by Snappy46 and addapted by Zozodesbois

CfgFile=./Jukebox.cfg
if [ ! -f "${CfgFile}" ]; then
  echo "Don't found config file : ${CfgFile}"
  exit 1
fi
sed '1d;$d;s:<\(.*\)>\(.*\)</.*>:\1=\2:' ${CfgFile} >/tmp/Jukebox.cfg
. /tmp/Jukebox.cfg
#-----------------------------------------------------------------------------
# Chargement du fichier config et affectation des variables du nom des balises
#  lang=fr
#  Jukebox_Path=/usr/local/bin/scripts/Jukebox
#  Jukebox_Size=2x6 | 3x8
#  AllMovies_Path=/usr/local/bin/scripts/Films
#  AllMovies_Name=filename | infoname
#  Type_Info=MovieInfo | MovieName | <Info_Path>
#  Type_Poster=folder | MovieName | <Poster_Path>
#  Type_Sheet= about | 0001 | MovieName | <Sheet_Path>
#  Poster_Ext=jpg | bmp
#  Sheet_Ext=jpg | bmp
#  Movie_Movie=xxooxxooip
#  Skin=HardManBlue | Snappy46
#-----------------------------------------------------------------------------

Ch_Jbx="${Jukebox_Path}/Jbx"			# Chemin des Jukebox .xml
Ch_Modules="${Jukebox_Path}/Modules"		# Chemin des modules
AllMovies_Bd="${Jukebox_Path}/Jukebox.bd"	# Liste des films
AllMovies_Bd_Sort="/tmp/sortedrss.list"		# Liste triée des films
Genre_List="/tmp/genre.list"			# Liste des chemins des thèmes
Main_Movies_Path="${Jukebox_Path}/mainjukebox.xml"	# Nom du jukebox des thèmes
Genre_Img="genre.jpg"				# Nom de l'image du thème (sert aussi à détecter un thème)
Letter_exclu="exclu.txt"			# Nom du fichier d'exclusion des Jukebox par lettre
LOG_IMG="${Jukebox_Path}/images.log"		# Nom du log pour recueillir les images manquantes
Letter_exclu_path_list="/tmp/excluletter.list"	# Liste des chemins exclus pour le Jukebox par lettre
AllMovies_Bd_Letter="/tmp/rss-exclu.list"	# Liste qui sert à retirer les films exclus

Poster_Path=""					# Chemin Poster
Sheet_Path=""					# Chemin Sheets
Info_Path=""					# Chemin .nfo

usage()
{
cat << EOF
usage: $0 options

This script creates a Movie / TV Episode on a specify directory. 
All the movies/TV Episode must be in their own directory.

OPTIONS:
   -h      Show this message
   -p      This indicate the jukebox directory ex: -p /HDD/movies/
   -f      This is the filter option, movies filename containing this/those
           string(s) will be skipped.  Strings must be separated by a ","
           (Optional) ex: -f sample,trailer

NOTES:  If any of the arguments have spaces in them they must be surrounded by quotes: ""
           
EOF
exit 1
}

#------------------------
# Ctrl des paramètres
#------------------------
while getopts p:f:h OPTION 
do
  case $OPTION in
     p)
       AllMovies_Path=$OPTARG
       if [ ! -d "${AllMovies_Path}" ]			# ctrl directory param
       then
         echo -e "The specified directory doesn't exist: ${AllMovies_Path}"
         exit 1
       fi
       sed -i "s:\(AllMovies_Path>\)\(.*\)\(</.*\):\1${AllMovies_Path}\3:" ${CfgFile}	# write param in cfg file
       ;;
     f)
       Movie_Filter=$OPTARG
       sed -i "s:\(Movie_Filter>\)\(.*\)\(</.*\):\1${Movie_Filter}\3:" ${CfgFile}	# write param in cfg file
       ;;
     h)
       usage
       ;;
   esac
done

if [ ! -d "${AllMovies_Path}" ]; then			# ctrl directory cfg file
  echo -e "The AllMovies_Path specified directory in ${CfgFile} doesn't exist: ${AllMovies_Path}"
  exit 1
fi

if [ "${Type_Poster}" == "MovieName" ] || [ "${Type_Poster}" == "folder" ]; then
  Poster_Path="${AllMovies_Path}"
elif [ -d "${Type_Poster}" ]; then			# ctrl directory cfg file
  Poster_Path="${Type_Poster}"
else
  echo "The Type_Poster specified in ${CfgFile} doesn't exist : ${Type_Poster}"
  echo "It must be MovieName or folder or an existing Poster directory"
  exit 1
fi

if [ "${Type_Sheet}" == "MovieName" ] || [ "${Type_Sheet}" == "about" ] || [ "${Type_Sheet}" == "0001" ]; then
  Sheet_Path="${AllMovies_Path}"
elif [ -d "${Sheet_Path}" ]; then			# ctrl directory cfg file
  Sheet_Path="${Type_Sheet}"
else
  echo "The Type_Sheet specified in ${CfgFile} doesn't exist: ${Type_Sheet}"
  echo "It must be MovieName or about or 0001 or an existing Sheet directory"
  exit 1
fi

if [ "${Type_Info}" == "MovieName" ] || [ "${Type_Info}" == "MovieInfo" ]; then
  Info_Path="${AllMovies_Path}"
elif [ -d "${Type_Info}" ]; then			# ctrl directory cfg file
  Info_Path="${Type_Info}"
else
  echo "The Type_Info specified in ${CfgFile} doesn't exist: ${Type_Info}"
  echo "It must be MovieName or MovieInfo or an existing Info directory"
  exit 1
fi

if [ ${AllMovies_Name} != "filename" ] && [ ${AllMovies_Name} != "infoname" ]; then
  echo "The AllMovies_Name scpecified in ${CfgFile} must be filename or infoname : ${AllMovies_Name}"
  exit 1
fi

if [ ! -d "${Jukebox_Path}/Skin/${Skin}" ]; then
  echo "The specified Skin in ${CfgFile} doesn't exist : ${Jukebox_Path}/Skin/${Skin}"
  exit 1
fi

#------------------------------
# fonctions
#------------------------------
movies_processing()
{
# Replace the comma in Movie_Filter to pipes |
Movie_Filter=`echo ${Movie_Filter} | sed 's/,/|/ g'`

# Find and sort the movies based on selection
echo "Searching for movies.."
find "${AllMovies_Path}" | egrep -i '\.(asf|avi|dat|divx|flv|img|iso|m1v|m2p|m2t|m2ts|m2v|m4v|mkv|mov|mp4|mpg|mts|qt|rm|rmp4|rmvb|tp|trp|ts|vob|wmv)$' | egrep -iv "${Movie_Filter}" > ${AllMovies_Bd}

# Tri sur le nom de fichier
echo "Sorting movies.."
sed 's:\(.*/\)\([^/]*\):\2 \1\2:' ${AllMovies_Bd} | sort | sed 's:[^/]* ::' > ${AllMovies_Bd_Sort}
echo "Found `sed -n '$=' ${AllMovies_Bd_Sort}` movies"

# Recherche les thèmes
echo "Searching for genre.."
find "${AllMovies_Path}" -name ${Genre_Img} | sed 's:\(.*/\)\([^/]*\):\2 \1:' | sort | sed 's:[^/]* ::' > ${Genre_List}  # recherche des thèmes

# Recherche les 1ères lettres pour le découpage du Jukebox
echo "Searching for first letters.."

find "${AllMovies_Path}" -name ${Letter_exclu} | sed 's:\(.*/\)\([^/]*\):\1:' > ${Letter_exclu_path_list} # recherche des exclusions

cp ${AllMovies_Bd_Sort} ${AllMovies_Bd_Letter}
while read plik						# retire tous les thèmes qui ont le fichier d'exclusion
do
  plik2=`basename $plik`
  sed -i "/\/$plik2\//d" ${AllMovies_Bd_Letter}
done < ${Letter_exclu_path_list}

# Recherche les 1ères lettres des noms des Films, en majuscule, 0 pour les autres caractères, trie en enlèvant les doublons, enlève les retours chariots
L_RSS="ALL "`sed 's:\(.*/\)\([^/]*\):\2:' ${AllMovies_Bd_Letter} | cut -c1 | tr a-z A-Z | tr -c A-Z'\n' 0 | sort -u |tr '\n' ' ' `
}

# ouverture des jukebox
genjukexmlheader()
{
echo -e '<Jukebox><title>'$Jukebox_Title'</title>' > $RSS
}

# fermeture des jukebox
genjukexmlfooter()
{
Nb_Ligne=`cat $RSS | wc -l`
Nb_Ligne=`expr $Nb_Ligne - 1`
echo "<Count>$Nb_Ligne</Count></Jukebox>">>$RSS
}

# Création des jukebox
genjukexml()
{

MoviePath_length=`expr length ${AllMovies_Path} + 2`		# longueur du chemin film
PosterPath_length=`expr length ${Poster_Path} + 2`		# longueur du chemin Poster
SheetPath_length=`expr length ${Sheet_Path} + 2`		# longueur du chemin Sheet

cat ${AllMovies_Bd_Sort} | while read plik
do
  printf '.'

  Date_File=`date -r "${plik}" '+%Y%m%d%H%M%S'` # récupération de la date de modif du film

  plik=`echo "$plik" | sed -e 's/\&/\&amp;/g'`	# conversion des & pour la compatibilité html
											
  Movie_Name=`basename "$plik" | sed 's/\(.*\)\..*/\1/'`	# nom du film sans l'extention
  Movie_Path=`dirname "$plik"`					# nom du chemin
  Movie_File=`echo $plik | cut -c${MoviePath_length}-`		# tronque le chemin du film + nom du film (sans le chemin général)
  Movie_Title="${Movie_Name}"

  if [ "${Type_Info}" == "MovieInfo" ]; then
    Info_Name="MovieInfo.nfo"
  else
    Info_Name="${Movie_Name}.nfo"
  fi

  if [ -e "${Info_Path}/${Info_Name}" ]; then # Si Info existe
    if [ ${AllMovies_Name} = "infoname" ]; then
      Movie_Title=`sed '/<title/!d;s:.*>\(.*\)</.*:\1:' "${Info_Path}/${Info_Name}"`
    fi
    Movie_Year=`sed '/<year/!d;s:.*>\(.*\)</.*:\1:' "${Info_Path}/${Info_Name}"`
    Movie_Rating=`sed '/<rating/!d;s:.*>\(.*\)</.*:\1:' "${Info_Path}/${Info_Name}"`
    Movie_Genre=`sed -e '/<genre/,/\/genre>/!d;/genre>/d' "${Info_Path}/${Info_Name}" | tr -d '\n\r'`

#  <year>1997</year>
#  <rating>7.8</rating>
#  <actor>
#    <name>Bruce Willis</name>
#    <name>Gary Oldman</name>
#    <name>Ian Holm</name>
#    <name>Milla Jovovich</name>
#    <name>Chris Tucker</name>
#  </actor>
#  <genre>
#    <name>Science fiction</name>
#  </genre>
#  <director>
#    <name>Luc Besson</name>
#  </director>

#awk '{
#    for (i=1; i<=NF; i++)
#       if ($i ~ /actor>/)
#          print $i;
# }
# ' "${Info_Path}/${Movie_Name}.nfo"

  fi

  if [ "${Type_Poster}" == "folder" ]; then
    Poster_Name="folder.${Poster_Ext}"
  else
    Poster_Name="${Movie_Name}.${Poster_Ext}"
  fi

  if [ "${Type_Sheet}" == "about" ]; then
    Sheet_Name="about.${Sheet_Ext}"
  elif [ "${Type_Sheet}" == "0001" ]; then
    Sheet_Name="0001.${Sheet_Ext}"
  else
    Sheet_Name="${Movie_Name}_sheet.${Sheet_Ext}"
  fi

  if [ ! -e "${Poster_Path}/${Poster_Name}" ]; then		# Si Jaquette n'existe pas
    echo "Jaquette: ${Poster_Path}/${Poster_Name}" >> "${LOG_IMG}"
  fi

  if [ ! -e "${Sheet_Path}/${Sheet_Name}" ]; then		# Si pages de résumé existe
    echo "Sheet: ${Sheet_Path}/${Sheet_Name}" >> "${LOG_IMG}"
  fi

  Poster_File=`echo "${Poster_Path}/${Poster_Name}" | cut -c${PosterPath_length}-`	# chemin du Poster avec le nom du Poster, sans le chemin général
  Sheet_File=`echo "${Sheet_Path}/${Sheet_Name}" | cut -c${SheetPath_length}-`		# chemin du Sheet avec le nom du Sheet, sans le chemin général

  # Constitution du nom des Jukebox dans lesquels le film doit être présent
  C_RSS=`expr substr "${Movie_Title}" 1 1`			# Extrait la 1ere lettre nom du film
  case ${C_RSS} in
    [a-zA-Z] ) C_RSS=`echo ${C_RSS} | tr a-z A-Z`; RSS="${Ch_Jbx}/jbx_${C_RSS}.xml" ;; # si une lettre -> jukebox de la lettre
    * )        RSS="${Ch_Jbx}/jbx_0.xml" ;;			# Si autre chose met dans liste 0
  esac

  if [ ! -e "${Movie_Path}/${Letter_exclu}" ]; then
    # Jukebox par lettre Alpha
    echo -e '<Movie><title>'${Movie_Title}'</title><poster>'${Poster_File}'</poster><sheet>'${Sheet_File}'</sheet><file>'${Movie_File}'</file><Genre>'${Movie_Genre}'</Genre><Rating>'${Movie_Rating}'</Rating><Year>'${Movie_Year}'</Year><AddTime>'${Date_File}'</AddTime></Movie>' >> $RSS

    # Jukebox Total
    echo -e '<Movie><title>'${Movie_Title}'</title><poster>'${Poster_File}'</poster><sheet>'${Sheet_File}'</sheet><file>'${Movie_File}'</file><Genre>'${Movie_Genre}'</Genre><Rating>'${Movie_Rating}'</Rating><Year>'${Movie_Year}'</Year><AddTime>'${Date_File}'</AddTime></Movie>' >> "${Ch_Jbx}/jbx_ALL.xml"
  fi

  # Jukebox par thèmes
  if [ -e "${Movie_Path}/${Genre_Img}" ]; then
    Jukebox_Title=`basename "${Movie_Path}"`
    RSS="${Ch_Jbx}/jbx_${Jukebox_Title}.xml"

    echo -e '<Movie><title>'${Movie_Title}'</title><poster>'${Poster_File}'</poster><sheet>'${Sheet_File}'</sheet><file>'${Movie_File}'</file><Genre>'${Movie_Genre}'</Genre><Rating>'${Movie_Rating}'</Rating><Year>'${Movie_Year}'</Year><AddTime>'${Date_File}'</AddTime></Movie>' >> $RSS
  fi
done
printf "\n"
}

# Génère les entêtes des jukebox
genmainjukexmlheader()
{
echo -e '<?xml version="1.0" encoding="UTF-8"?>
<Jukebox>
  <Category>
    <title>Jukebox Main Menu</title>
    <link>MainJukebox.rss</link>
  </Category>' > ${Main_Movies_Path}
}

# Génère le menu des thèmes
genmainjukexml()	
{
echo -e "<genre>
<title>$Jukebox_Title</title>
<poster>$FOLDER</poster>
<link>$RSS</link>
</genre>" >> ${Main_Movies_Path}
}

#----------------------------
# Main Program
#----------------------------

rm "${Ch_Jbx}/"jbx_*.xml 2>/dev/null		# Supprime les jukebox
rm "${LOG_IMG}" 2>/dev/null	# Supprime le log des images manquantes

movies_processing;				# liste des films, tri

####### Génération des Jukebox
echo "Generating RSS header by genre.."
while read plik					# ouvre tous les entêtes pour chaque thème
do
  Jukebox_Title=`basename "${plik}"`
  RSS="${Ch_Jbx}/jbx_${Jukebox_Title}.xml"
  genjukexmlheader;
done < ${Genre_List}

echo "Generating RSS header by letter.."
for i in ${L_RSS}				# ouvre tous les entêtes lettre et total
do
  Jukebox_Title="${i}"
  RSS="${Ch_Jbx}/jbx_${i}.xml"
  genjukexmlheader;
done

echo "Indexing movies.."
genjukexml;					# génération de tous les jukebox 

echo "closing RSS by letter.."
for i in ${L_RSS}				# ferme tous les jukebox lettre et total
do
  RSS="${Ch_Jbx}/jbx_${i}.xml"
  genjukexmlfooter;
done

echo "closing RSS by genre.."
while read plik					# ferme tous les jukkebox pour chaque thème
do
  Jukebox_Title=`basename "${plik}"`
  RSS="${Ch_Jbx}/jbx_${Jukebox_Title}.xml"
  genjukexmlfooter;
done < ${Genre_List}

####### Génération du Jukebox des thèmes
echo "Generating main jukebox.."
genmainjukexmlheader;				# Crée l'entête du menu des thèmes

while read plik					# ajoute les jukebox par thèmes au menu des thèmes
do
  FOLDER="${plik}/${Genre_Img}"
  Jukebox_Title=`basename "${plik}"`
  RSS="${Ch_Jbx}/jbx_${Jukebox_Title}.xml"
  genmainjukexml;
done < ${Genre_List}

for i in ${L_RSS}				# ajoute les jukebox lettre et total au menu des thèmes
do
  FOLDER="${Ch_Modules}/JukeMenu_${i}.jpg"
  Jukebox_Title="${i}"
  RSS="${Ch_Jbx}/jbx_${i}.xml"
  genmainjukexml;
done

echo -e '</Jukebox>' >> ${Main_Movies_Path}	# Fermeture du menu des thèmes
echo -e '\nDone!'

