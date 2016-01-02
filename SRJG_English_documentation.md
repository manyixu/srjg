**Currently in progress**<br>
<br>
<img src='https://lh6.googleusercontent.com/-m1X7mJnIQHY/T2j6Td1w66I/AAAAAAAAA9s/d669u1vk_PA/s800/srjg_menu_principal.jpg' /><br>
<br>
<br>
<br>
<h1>SRJG Video demonstration</h1>
<br>
<a href='http://www.youtube.com/watch?feature=player_embedded&v=1qjapUIsEiE' target='_blank'><img src='http://img.youtube.com/vi/1qjapUIsEiE/0.jpg' width='425' height=344 /></a><br>
<br>
<br>
<h1>Parameters</h1>
<br>
Two parameters can not be configured from the TV feed: <br>
The location of the Jukebox (Jukebox_Path), and the port number used<br>
(Port) to run cgi scripts. <br>
Srjg.cfg the file must be copied to /usr/local/etc/<br>
<br>
You can change any other settings from your television screen. This<br>
will avoid any data entry errors in the configuration file.<br>
<br>
<img src='https://lh6.googleusercontent.com/-fJn5femmgco/T2j6S6Uyl5I/AAAAAAAAA-s/C6MwHDxcpbs/s700/srjg_menu_config.jpg' /><br>
<br>
<br>
<h2>Configuration file (srjg.cfg) details</h2>
<br>
The parameters are between tags. Do not change the tags names.<br>
Exemple:<br>
<br>
<code>&lt;Lang&gt;en&lt;/Lang&gt;</code><br>
The parameter name is "Lang" and its value is "en"<br>
<br>
<br>
<h3>List of configuration parameters</h3>
<br>
Lang (default "en")<br>
<br>
Puts the interface in the chosen language.<br>
<br>
<br>
Jukebox_Path (default "/usr/local/etc/srjg/")<br>
<br>
This is the path where you have installed SRJG. Note that there is a "/" at the end of the path and it must be included.<br>
<br>
<br>
Jukebox_Size (default "2x6")<br>
<br>
This option determine how the movies thumbnails will be shown.<br>
<br>
Possible values are:<br>
<br>
2x6 : Two(2) rows of six(6) thumbnails<br>
3x8 : Three(3) rows of eight(8) thumbnails<br>
Sheetwall: Mode with full moviesheet view with thumbnails at the bottom of the screen.<br>
<br>
<br>
Movies_Path (default "/tmp/usbmounts/sdb1/")<br>
<br>
This is the path to the locations of your movies.&nbsp; This path must already exist.<br>
Note that there is a "/" at the end of the path and it must be included.<br>
<br>
Nfo_Path (default "MoviesPath")<br>
<br>
This is the path to the locations of your NFO movie files.<br>
<br>
Possible values are:<br>
<br>
MoviesPath : NFO files are located/created in the Movies folders<br>
defined in the parameter "MoviesPath"<br>
SRJG: NFO files are located/created in a subfolder of the movies<br>
<movie path>/SRJG/ImgNfo/ which is defined in the parameter<br>
"MoviesPath"<br>
You can also specify the any path of your choice by entering it between<br>
the tags. This path must already exist and be writable.<br>
Note that there is a "/" at the end of the path and it must be included.<br>
<br>
<br>
Poster_Path (default "MoviesPath")<br>
<br>
This is the path to the locations of your movie thumbnail files.<br>
<br>
Possible values are:<br>
<br>
MoviesPath : Thumbnail files are located/created in the Movies folders<br>
defined in the parameter "MoviesPath"<br>
SRJG: Thumbnail files are located/created in a subfolder of the movies<br>
<movie path>/SRJG/ImgNfo/ which is defined in the parameter<br>
"MoviesPath"<br>
You can also specify the any path of your choice by entering it between<br>
the tags. This path must already exist and be writable.<br>
Note that there is a "/" at the end of the path and it must be included.<br>
<br>
<br>
Sheet_Path (default "MoviesPath")<br>
<br>
This is the path to the locations of your movie sheets files.<br>
<br>
Possible values are:<br>
<br>
MoviesPath : Moviesheet files are located/created in the Movies folders<br>
defined in the parameter "MoviesPath"<br>
SRJG: Moviesheet files are located/created in a subfolder of the movies<br>
<movie path>/SRJG/ImgNfo/ which is defined in the parameter<br>
"MoviesPath"<br>
You can also specify the any path of your choice by entering it between<br>
the tags. This path must already exist and be writable.<br>
Note that there is a "/" at the end of the path and it must be included.<br>
<br>
<br>
SingleDb (default "no")<br>
<br>
"Yes" there is only one database in /usr/local/etc/ <br>
"No" the database is in <code>&lt;MoviesPath&gt;</code>/SRJG/. This allows multiple<br>
Jukebox by changing the location of the main movies path.<br>
<br>
<br>
UnlockRM (defaut "no")<br>
<br>
If this parameter is "yes" it activates a menu when you press the<br>
button "Edit". It is used to remove pockets, Sheet images, files. Nfo<br>
and movies. <br>
<br>
<br>
<br>
Movie_Filter (default "sample, "2 ch", cd2")<br>
<br>
<br>
This filter contains a list that will allow to exclude films that<br>
contain these words. <br>
These elements must be separated by a comma. If an item has a space, it<br>
must be quoted. <br>
If a video is in two parts, cd2 serves to mask the second cd. The films<br>
in two parts are managed by SRJG, which automatically switches to the<br>
second part. <br>
It is essential that Part 1 includes the element cd1 at the end of its<br>
name and part 2 contains cd2: <br>
Example: <br>
<Movie name> cd1.avi <movie name> cd2.avi <br>
The lowercase is important to recognize cd1 and cd2.<br>
<br>
<br>
Port (default 80) <br>
<br>
This port number is used to execute cgi scripts. If you do not know<br>
your port number, you have a small tool to find it. <br>
Start Telnet and run the script "srjg/installer/port.sh". <br>
<br>
<br>
Recent_Max? (defaut 24) <br>
<br>
Specifies the maximum number of movies shown in the "Recently Added"<br>
Thumbnail screen.<br>
<br>
<br>
Dspl_Genre_txt (default white)<br>
<br>
Possible values: white, black <br>
<br>
Indicates the color of the text used on the movies genre thumbnails<br>
(white, black). <br>
<br>
<br>
Dspl_HelpBar (default top)<br>
<br>
Possible values: up, down, no <br>
<br>
Determine the location or presence of the bar help (up, down or not at<br>
all).<br>
<br>
<br>
The remainders of the settings only deals with the automatic creation<br>
of thumbnails, moviesheets and NFO files.&nbsp; If you choose to<br>
manually create those<br>
then you do not have to worry about those settings.<br>
<br>
<br>
Imdb (default no) <br>
<br>
Allows automatic retrieval of Imdb thumbnails, moviesheets or NFO files<br>
depending on the settings chosen. (yes/no)<br>
<br>
<br>
Imdb_Lang (en default) <br>
<br>
Defines the interface language the Movie Sheet (actor, director, genre,<br>
year, duration). To set the language used in the synopsis, <br>
you should use the parameter Imdb_Source. <br>
<br>
<br>
<br>
Imdb_Source (default imdb) <br>
<br>
Possible values are: imdb, tmdb, allocine.<br>
<br>
Set which site to use as source for the thumbnails, Movie Sheets and<br>
Nfo files. This site also defines the language used for Synopsis and<br>
pictures.<br>
<br>
<br>
Imdb_Poster (default yes) <br>
<br>
Allows the automatic retrieval of the thumbnails. (yes/no)<br>
<br>
<br>
Imdb_PBox (default generic)<br>
<br>
Possible values: No, bdrip, bluray, dtheater, dvd, generic, hddvd,<br>
hdtv, itunes <br>
<br>
Defines the display frame used for the thumbnails.<br>
<br>
<br>
Imdb_PPost (default yes)<br>
<br>
if active, the thumbnail will be chosen at random from the available<br>
images on the source site.(yes/no)<br>
<br>
<br>
Imdb_Sheet (default yes)<br>
<br>
Allows the automatic retrieval of the movie sheets. (yes/no)<br>
<br>
<br>
Imdb_SBox (default generic)<br>
<br>
Possible values: No, bdrip, bluray, dtheater, dvd, generic, hddvd,<br>
hdtv, itunes<br>
<br>
Defines the display frame used for the thumbnail inside the movie<br>
sheets.<br>
<br>
<br>
Imdb_SPost (default yes)<br>
<br>
if active, the thumbnail inside the movie sheets will be chosen at<br>
random from the available images on the source site.(yes/no)<br>
<br>
<br>
Imdb_Backdrop (default yes)<br>
<br>
If active, the background of the movie Sheets will be randomly selected<br>
from the images available on the source site. (yes/no)<br>
<br>
<br>
Imdb_Font (default tahoma)<br>
<br>
Possible values: Arial, Bookman, comic, tahoma, times, verdana <br>
<br>
Sets the font used for the movie Sheets. <br>
<br>
<br>
<br>
Imdb_Genres (default no) <br>
<br>
If enabled, images that will be displayed instead of text for genre<br>
types. This system works well with genres in English, but because of<br>
the translation, <br>
it is possible that certain types Images do not displayed get displayed<br>
when other languages are selected. (yes/no)<br>
<br>
<br>
<br>
Imdb_Tagline (default yes)<br>
<br>
if active, displays the tag line in the movie Sheets. (yes/no)<br>
<br>
<br>
<br>
Imdb_Time (default no)<br>
<br>
Possible values: no, real, hours<br>
<br>
Sets the format for time display in the movie Sheets.<br>
<br>
<br>
<br>
Imdb_Info (default yes) <br>
<br>
if active, enable the creation of movies NFO files.<br>
<br>
<br>
<br>
Imdb_MaxDl (default 3) <br>
<br>
Indicates the number of simultaneous downloads to retrieve the images<br>
and NFO files.&nbsp; This setting depends on the speed of your Internet<br>
connection<br>
and capability of your Player. If you have a small bandwitdh, put a<br>
download of one or two. If you put a number that is too big, your<br>
player will <br>
be overloaded and over time it will be as long if not longer than using<br>
a small number. The best performance is generally achieved with 3 or 4<br>
simultaneous downloads. <br>
<br>
<br>
<br>
<br>
Movies made up of 2 cd files<br>
<br>
Files must end with cd1 cd2 <br>
<br>
For example: <br>
<br>
<code>movie name cd2.avi movie name_cd2.avi</code>. In the filter parameter<br>
(Movie_Filter) , cd2 must be written so that the 2nd part of the movie<br>
(cd2)<br>
does not get included in the Jukebox. An icon will appear on the movie<br>
thumbnail, top right to indicate that there is a second part. While<br>
viewing, <br>
at the end of the first part, or if you press stop, the second part<br>
will automatically start.<br>
<br>
<br>
<br>
<h1>Organizing Files and folders</h1>
<br>
<h2>Movies</h2>
<br>
You have a lot of freedom in the organization of your files: movies are<br>
automatically detected in many types of directory trees.<br>
<br>
<pre><code>Main Folder<br>
   | - Movie 1<br>
   | - Movie 2   <br>
Main Folder<br>
   | - Feature Film 1         <br>
           | - Movie 1<br>
   | - Feature Film 2 <br>
           | - Movie 2<br>
Main Folder <br>
   | - other folder with all the movies <br>
           | - Movie 1<br>
           | - Movie 2 <br>
           | - ...<br>
           |-- other folder<br>
                   | - Movie 333    <br>
                   | - Movie 334 <br>
                   | - ... <br>
</code></pre>
<br>
The location of the "Main Folder" is the path of movies. It should be<br>
entered in the config file, or the menu interface configuration RSS. <br>
For the path /tmp/usbmounts/sdb1/Movies we have: <br>
<br>
<code>&lt;Movies_Path&gt;/tmp/usbmounts/sdb1&lt;/Movies_Path&gt;</code><br>
<br>
Note that there is a / at the end of the path.<br>
<br>
<h2>The poster (Thumbnail), images (moviesheet) and Nfo files.</h2>
<br>
The poster/thumbnail are small images (often the posters of movies) in 150x220.<br>

The images (moviesheets) are 1280x720. They contain a wide array of information about the movie, images of the movie, a summary etc ...<br>

Nfo files, include all information in text format about the movie. it will be used by the jukebox to find:<br>

-The original title of the film and the display instead of the filename. If you see the file name when you select a movie in the Jukebox it usually means that the Nfo file was not found, does not exist or nfo file does not follow the naming convention.<br>
- The movie genre. When you search for a genre, eg science fiction, you will find all movies that include the science fiction genre in the Nfo file. A movie can have several genre.<br>
- The year of the movie. When you search for a year, eg "2011", you will find all the movies that specify that release year in the Nfo file.<br>

All these files must have the same name as the film (note that names are case sensitive, it means respecting upper / lower case):<br>

Example:<br>

My_Movie.avi<br>
My_Movie.jpg<br>
My_Movie_sheet.jpg<br>
My_Movie.nfo<br>

Depending on the settings in the config file, these files can be located at various locations:<br>

Nfo_Path, Poster_Path and Sheet_Path may have the following values:<br>

MoviesPath: Corresponds to the "movies path". Files will be in the same directory as the movie files.<br>
SRJG: Corresponds to a sub folder in the movie path <movie path>/SRJG/ImgNfo<br>
Path: This path must point to a folder that already exists <br>

Nfo_Path, Poster_Path and Sheet_Path can have paths different from each other.<br>
For example:<br>

<pre><code>&lt;Movies_Path&gt;/tmp/usbmounts/sdb1/Movies/&lt;/Movies_Path&gt;<br>
&lt;Nfo_Path&gt;MoviesPath&lt;/Nfo_Path&gt;<br>
&lt;Poster_Path&gt;/home/Images/Posters/&lt;/Poster_Path&gt;<br>
&lt;Sheet_Path&gt;SRJG&lt;/Sheet_Path&gt;<br>
</code></pre>

<br>
This can be useful when the films are stored on a write-protected partition (NAS), you may decide to have movies on your NAS and supporting files on a local disk in your player.  This could also speed up navigation since all the images for the thumbnail/moviesheet will be access on the local drive versus the NAS.<br>

<h2>How to automatically thumbnails, movieSheet images and Nfo files using IMDB</h2>

SRJG is able to create these files for you (no need for Thumbgen, Sheetmaker, YAMJ or other utility).<br>
<br>
<img src='https://lh4.googleusercontent.com/-dEqggOwjwhk/T2j6TVb621I/AAAAAAAAA-w/YzTzeMob5q8/s700/srjg_menu_imdb.jpg' />

By default Imdb option is disabled: it is very time consuming, since it will allow SRJG to fetch the images on the internet and information. How long depends on the number of movies for which you want to collect images, but also the speed of your Internet connection.<br>

If Imdb is activated, the images and Nfo files will be retrieved and created when you run an update Jukebox. Whether it's a fast update, or rebuild, SRJG will begin by retrieving those files before updating the movies. Imdb will not replace thumbnails, MovieSheets and Nfo files that you already have, it will simply create the one that are absent.<br>

This process is completely anonymous, there is no collection of information.<br>
Here's how it works:<br>

-Search on your player for missing thumbnails, Moviesheets or Nfo files.<br>

-Removal of certain characters in file names to be as close to the actual movie name to help with the api search.<br>

-Send titles generated by the Api playon.unixstorm.org<br>

-Playon.unixstorm.org interrogate official servers like imdb, allocine.fr etc.. to retrieve the images and movie information.<br>


Collecting sites (imdb, allocine.fr etc...) only sees the api from Playon.unixstorm.org.<br>


<h1>List of parameters</h1>

If the images generated are not suitable, or the information corresponding to other movies, this is typically because the name of your files are not quite the movie name. Start by checking the name of your files.<br>

.......<br>
