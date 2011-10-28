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
AllMovies_newBd="${Jukebox_Path}/Jukebox_new.bd"		# Nouvelle liste des films
move_sup="${Jukebox_Path}/Mv_sup.tmp"		# Liste des films à retirer
move_add="${Jukebox_Path}/Mv_add.tmp"		# Liste des films à ajouter

Poster_Path=""					# Chemin Poster
Sheet_Path=""					# Chemin Sheets
Info_Path=""					# Chemin .nfo

if [ "${Type_Poster}" == "MovieName" ] || [ "${Type_Poster}" == "folder" ]; then
  Poster_Path="${AllMovies_Path}"
elif [ -d "${Type_Poster}" ]; then			# ctrl directory cfg file
  Poster_Path="${Type_Poster}"
fi

if [ "${Type_Sheet}" == "MovieName" ] || [ "${Type_Sheet}" == "about" ] || [ "${Type_Sheet}" == "0001" ]; then
  Sheet_Path="${AllMovies_Path}"
elif [ -d "${Sheet_Path}" ]; then			# ctrl directory cfg file
  Sheet_Path="${Type_Sheet}"
fi

if [ "${Type_Info}" == "MovieName" ] || [ "${Type_Info}" == "MovieInfo" ]; then
  Info_Path="${AllMovies_Path}"
elif [ -d "${Type_Info}" ]; then			# ctrl directory cfg file
  Info_Path="${Type_Info}"
fi

# Suppression des entetes et derniere ligne des jukebox
supprheader()
{
  ls -C1 "${Ch_Jbx}"/jbx_*.xml |while read ligne
  do
    sed -i -e '1d' -e '$d' ${ligne}
  done
}

# Création des jukebox
genjukexml()
{

MoviePath_length=`expr length ${AllMovies_Path} + 2`		# longueur du chemin film
PosterPath_length=`expr length ${Poster_Path} + 2`		# longueur du chemin Poster
SheetPath_length=`expr length ${Sheet_Path} + 2`		# longueur du chemin Sheet

cat ${move_add} | while read plik
do
  printf '.'

  Date_File=`date -r "${plik}" '+%Y%m%d%H%M%S'` # récupération de la date de modif du film

  plik=`echo "$plik" | sed -e 's/\&/\&amp;/g'`	# conversion des & pour la compatibilité html
											
  Movie_Name=`basename "$plik" | sed 's/\(.*\)\..*/\1/'`	# nom du film sans l'extention
  Movie_Path=`dirname "$plik"`					# nom du chemin
  Movie_File=`echo $plik | cut -c${MoviePath_length}-`		# chemin du film avec le nom du film, sans le chemin général
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

# ajout des entetes et derniere ligne des jukebox
addheader()
{

# pour faire des tri sur les autres balises
Nb_Ligne=`cat "${Ch_Jbx}"/jbx_ALL.xml | wc -l`
cat "${Ch_Jbx}"/jbx_ALL.xml | sed 's:<Movie>\(.*\)\(<Rating>.*</Rating>\)\(.*\)</Movie>:<Movie>\2\1\3</Movie>:' >"${Ch_Jbx}"/jbx_Rating.xml
echo "<Jukebox><title>Rating</title>">"${Ch_Jbx}"/jbx_Rating.xml.tmp
sort -r "${Ch_Jbx}"/jbx_Rating.xml>>"${Ch_Jbx}"/jbx_Rating.xml.tmp
echo "<Count>${Nb_Ligne}</Count></Jukebox>">>"${Ch_Jbx}"/jbx_Rating.xml.tmp
mv "${Ch_Jbx}"/jbx_Rating.xml.tmp "${Ch_Jbx}"/jbx_Rating.xml
mv "${Ch_Jbx}"/jbx_Rating.xml "${Ch_Jbx}"/jbx_Rating.xml.sv

cat "${Ch_Jbx}"/jbx_ALL.xml | sed 's:<Movie>\(.*\)\(<Year>.*</Year>\)\(.*\)</Movie>:<Movie>\2\1\3</Movie>:' >"${Ch_Jbx}"/jbx_Year.xml
echo "<Jukebox><title>Year</title>">"${Ch_Jbx}"/jbx_Year.xml.tmp
sort -r "${Ch_Jbx}"/jbx_Year.xml>>"${Ch_Jbx}"/jbx_Year.xml.tmp
echo "<Count>${Nb_Ligne}</Count></Jukebox>">>"${Ch_Jbx}"/jbx_Year.xml.tmp
mv "${Ch_Jbx}"/jbx_Year.xml.tmp "${Ch_Jbx}"/jbx_Year.xml
mv "${Ch_Jbx}"/jbx_Year.xml "${Ch_Jbx}"/jbx_Year.xml.sv

cat "${Ch_Jbx}"/jbx_ALL.xml | sed 's:<Movie>\(.*\)\(<AddTime>.*</AddTime>\)\(.*\)</Movie>:<Movie>\2\1\3</Movie>:' >"${Ch_Jbx}"/jbx_AddTime.xml
echo "<Jukebox><title>AddTime</title>">"${Ch_Jbx}"/jbx_AddTime.xml.tmp
sort -r "${Ch_Jbx}"/jbx_AddTime.xml>>"${Ch_Jbx}"/jbx_AddTime.xml.tmp
echo "<Count>${Nb_Ligne}</Count></Jukebox>">>"${Ch_Jbx}"/jbx_AddTime.xml.tmp
mv "${Ch_Jbx}"/jbx_AddTime.xml.tmp "${Ch_Jbx}"/jbx_AddTime.xml
mv "${Ch_Jbx}"/jbx_AddTime.xml "${Ch_Jbx}"/jbx_AddTime.xml.sv


  ls -C1 "${Ch_Jbx}"/jbx_*.xml |while read ligne
  do
    Title=`echo "${ligne}" | sed 's:jbx_\(.*\).xml:\1:'`
    Nb_Ligne=`cat "${ligne}" | wc -l`
    echo "<Jukebox><title>${Title}</title>">"${ligne}.tmp"
    sort "${ligne}">>"${ligne}.tmp"
    echo "<Count>${Nb_Ligne}</Count></Jukebox>">>"${ligne}.tmp"
    mv "${ligne}.tmp" "${ligne}"
  done
mv "${Ch_Jbx}"/jbx_Rating.xml.sv "${Ch_Jbx}"/jbx_Rating.xml
mv "${Ch_Jbx}"/jbx_Year.xml.sv "${Ch_Jbx}"/jbx_Year.xml
mv "${Ch_Jbx}"/jbx_AddTime.xml.sv "${Ch_Jbx}"/jbx_AddTime.xml
}

#-------------------------
# main program
#-------------------------

MoviePath_length=`expr length ${AllMovies_Path} + 2`		# longueur du chemin film

# Find and sort the movies based on selection
echo "Searching for movies.."
find "${AllMovies_Path}" | egrep -i '\.(asf|avi|dat|divx|flv|img|iso|m1v|m2p|m2t|m2ts|m2v|m4v|mkv|mov|mp4|mpg|mts|qt|rm|rmp4|rmvb|tp|trp|ts|vob|wmv)$' | egrep -iv "${Movie_Filter}" > ${AllMovies_newBd}

sed -i -e 's/\[/\&lsqb;/g' -e 's/\]/\&rsqb;/g' "${AllMovies_Bd}" # conversion des [] pour grep
sed -i -e 's/\[/\&lsqb;/g' -e 's/\]/\&rsqb;/g' "${AllMovies_newBd}" # conversion des [] pour grep

# Find suppressed Movies, enlever le chemin des films, echapper les "/", construire ligne de suppression
grep -vf "${AllMovies_newBd}" "${AllMovies_Bd}" | cut -c${MoviePath_length}- | sed -e 's/\//\\\//g' | sed 's:\(.*\):\/\1\/d:'>"${move_sup}"

# Find New Movies
grep -vf "${AllMovies_Bd}" "${AllMovies_newBd}">"${move_add}"

# Suppress Movies in all jbx
NB=`cat "${move_sup}" | wc -l`
if [ ${NB} -gt 0 ]
then
  ls -C1 "${Ch_Jbx}"/jbx_*.xml |while read ligne
  do
    sed -i -f "${move_sup}" "${ligne}"
  done
fi

# Add new Movies
NB=`cat "${move_add}" | wc -l`
if [ ${NB} -gt 0 ]
then
  supprheader;
  genjukexml;
  addheader;
fi

mv "${AllMovies_newBd}" "${AllMovies_Bd}"
rm "${move_sup}" "${move_add}"



