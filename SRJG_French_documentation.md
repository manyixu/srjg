**En cours d'écriture**

![https://lh6.googleusercontent.com/-m1X7mJnIQHY/T2j6Td1w66I/AAAAAAAAA9s/d669u1vk_PA/s800/srjg_menu_principal.jpg](https://lh6.googleusercontent.com/-m1X7mJnIQHY/T2j6Td1w66I/AAAAAAAAA9s/d669u1vk_PA/s800/srjg_menu_principal.jpg)



# SRJG Video demonstration #

<a href='http://www.youtube.com/watch?feature=player_embedded&v=1qjapUIsEiE' target='_blank'><img src='http://img.youtube.com/vi/1qjapUIsEiE/0.jpg' width='425' height=344 /></a>

# Le paramétrage #

Deux paramètres ne peuvent pas être configurés depuis la TV en RSS :<br>
L’emplacement du Jukebox (Jukebox_Path), et le numéro du port utilisé (Port) pour exécuter les scripts cgi.<br>
Le fichier srjg.cfg doit être copié dans /usr/local/etc/<br>
<br>
Vous pouvez a présent modifier tous les autres paramètres depuis votre écran de télévision. Vous éviterez ainsi des éventuelles erreurs de saisie dans le fichier de configuration.<br>
<br>
<img src='https://lh6.googleusercontent.com/-fJn5femmgco/T2j6S6Uyl5I/AAAAAAAAA-s/C6MwHDxcpbs/s700/srjg_menu_config.jpg' />

<h2>Détail du Fichier de config</h2>

Les paramètres sont entre balise. Ne modifiez pas les noms des balises.<br>
Exemple:<br>
<code>&lt;Lang&gt;en&lt;/Lang&gt;</code><br>
Le nom  du paramètre c’est « Lang » et sa valeur c’est « en »<br>
<h3>Liste des paramètres</h3>

<ul><li>Lang (defaut en)<br>
Permet de mettre l’interface dans la langue choisie.</li></ul>

<ul><li>Jukebox_Path ( defaut /usr/local/etc/srjg/)<br>
C’est le chemin où se trouve le SRJG.<br>
Sur certains player, nottament HMB, le chemin sera /usr/local/etc/scripts/srjg/<br>
Nottez qu’il y a un « / » à la fin du chemin.</li></ul>

<ul><li>Jukebox_Size (defaut 2x6)<br>
C’est l’affichage par défaut des Jukebox.<br>
Liste des choix possibles<br>
2x6 2 rangées de 6 Pochettes<br>
3x8 3 rangées de 8 Pochettes<br>
Sheetwall C’est un mode avec l’image Sheet en pleine page et les Pochette en bas de l’écran.</li></ul>

<ul><li>Movies_Path (defaut /tmp/usbmounts/sdb1/)<br>
C’est le chemin vers l’emplacement de vos films.<br>
Ce chemin doit exister<br>
Nottez qu’il y a un « / » à la fin du chemin.</li></ul>

<ul><li>Nfo_Path (defaut MoviesPath)<br>
Indique l’emplacement des fichiers .nfo<br>
Valeurs possibles:<br>
MoviesPath les fichiers .nfo sont placés dans le dossier des Films définit dans le paramètre MoviesPath<br>
SRJG les fichiers .nfo sont placés dans un sous dossier des films : <chemin des films>/SRJG/ImgNfo/ qui se trouve dans le dossier des Films définit dans le paramètre MoviesPath<br>
«Un chemin vers un dossier qui existe/» Vous pouvez indiquer le chemin de votre choix. Ce dossier doit exister et être accessible en écriture.<br>
Nottez qu’il y a un « / » à la fin du chemin.</li></ul>

<ul><li>Poster_Path (defaut MoviesPath)<br>
Indique l’emplacement des Pochettes<br>
Valeurs possibles :<br>
MoviesPath les Pochettes  sont placées dans le dossier des Films définit dans le paramètre MoviesPath<br>
SRJG les Pochettes  sont placées dans un sous dossier des films : <chemin des films>/SRJG/ImgNfo/ qui se trouve dans le dossier des Films définit dans le paramètre MoviesPath<br>
«Un chemin vers un dossier qui existe/» Vous pouvez indiquer le chemin de votre choix. Ce dossier doit exister et être accessible en écriture.<br>
Nottez qu’il y a un « / » à la fin du chemin.</li></ul>

<ul><li>Sheet_Path (defatut MoviesPath)<br>
Indique l’emplacement des images Sheet.<br>
Valeurs possibles:<br>
MoviesPath les images Sheet sont placées dans le dossier des Films définit dans le paramètre MoviesPath<br>
SRJG les images Sheet sont placées dans un sous dossier des films : <chemin des films>/SRJG/ImgNfo/ qui se trouve dans le dossier des Films définit dans le paramètre MoviesPath<br>
«Un chemin vers un dossier qui existe/» Vous pouvez indiquer le chemin de votre choix. Ce dossier doit exister et être accessible en écriture.<br>
Nottez qu’il y a un « / » à la fin du chemin.</li></ul>

<ul><li>SingleDb (defaut no)<br>
Valeur « yes » il n’y a qu’une seule base de données dans /usr/local/etc/<br>
Valeur « no » la base de données se situe dans <chemin des films>/SRJG/. Cela permet d’utiliser plusieurs Jukebox en ne changeant que le chemin des films.</li></ul>

<ul><li>UnlockRM (defaut no)<br>
Si ce paramètre est à « yes » cela active un menu lorsque l’on appuie sur la touche « Edit ». Il sert à supprimer des Pochettes, des images Sheet, des fichiers .nfo et des films.</li></ul>

<ul><li>Movie_Filter (defaut sample,"2 ch",cd2)<br>
Ce filtre contient une liste qui va permettre d’écarter des films qui contiennent ces termes.<br>
Ces éléments doivent être séparés par une virgule. Si un élément comporte un blanc, il doit être entre guillemets.<br>
Si une vidéo est coupée en deux, cd2 sert à masquer le deuxième cd. Les films en deux parties sont gérés par SRJG, qui passe automatiquement à la deuxième partie. Il faut impérativement que la partie 1 comporte l’élément cd1 à la fin de son nom et la partie 2 contienne cd2 :<br>
Exemple<br>
<pre><code>&lt;nom du film&gt;_cd1.avi<br>
&lt;nom du film&gt;_cd2.avi<br>
</code></pre>
Ou bien<br>
<pre><code>&lt;nom du film&gt;cd1.avi<br>
&lt;nom du film&gt;cd2.avi<br>
</code></pre>
Les minuscules sont importantes pour reconnaître cd1 et cd2.</li></ul>

<ul><li>Port (defaut 80)<br>
Ce numéro de port permet d’exécuter les scripts cgi. Si vous ne connaissez pas votre numéro de port, vous avez un petit outil pour le trouver.<br>
Mettez-vous en Telnet et exécutez le script srjg/installer/port.sh</li></ul>

<ul><li>Recent_Max (defaut 24)<br>
Indique le nombre maximum de films affichés dans la rubrique « Pas Regardés »</li></ul>

<ul><li>Dspl_Genre_txt (defaut white)<br>
Valeurs possibles: white, black<br>
Indique la couleur d’affichage du texte sur les Pochettes des genres (blanc, noir).</li></ul>

<ul><li>Subt_OneAuto (defaut no)<br>
Valeurs possibles: yes, no<br>
Si à "yes", si la vidéo n'a qu'un seul sous-titre, la vidéo sera lancée automatiquement avec le sous-titre présent. Le menu de sélection des sous-titres n'apparaît que s'il y a plusieurs sous-titres pour la même vidéo.</li></ul>

<ul><li>Subt_FontPath (defaut JukeboxPath)<br>
Valeurs possibles: JukeboxPath, un chemin vers un dossier de polices.<br>
JukeboxPath: le menu des polices va chercher les polices dans le dossier "font" situé dans le dossier du programme srjg<br>
Vous pouvez définir le dossier de votre choix qui contient des Polices.<br>
Votre Firwmare contient déjà des polices:<br>
<pre><code>/usr/local/bin/Resource<br>
/usr/local/bin/Resource/CC_Font<br>
</code></pre></li></ul>

<ul><li>Subt_FontFile (defaut "")<br>
Si rien n'est précisé, la police système est utilisée.<br>
Attention, si le nom de la police précisée ici n'existe pas, votre Player va rebooter. Il est conseillé d'utiliser les menus de configuration depuis votre TV pour renseigner ce paramètre.</li></ul>

<ul><li>Subt_Color (defaut white)<br>
Valeurs possibles: white, yellow.<br>
C'est la couleur d'affichage de la police.</li></ul>

<ul><li>Subt_ColorBg (defaut transparent)<br>
Valeurs possibles: trasparent, white, black.<br>
C'est la couleur de fond pour la police.</li></ul>

<ul><li>Subt_Size (defaut 24)<br>
Taille de la police.</li></ul>

<ul><li>Subt_Pos (defaut 0)<br>
Position a partir du bas de l'écran, les valeurs doivent être négatives.</li></ul>

<ul><li>Imdb (defaut no)<br>
Permet d’utiliser Imdb pour récupérer automatiquement des Pochettes, Jaquettes et/ou fichiers .nfo, en fonction des paramètres choisis.</li></ul>

<ul><li>Imdb_Lang (defaut en)<br>
Permet de definer la langue de l’interface sur une image Sheet (acteur, directeur, genre, année, durée). Pour définir la langue utilisée dans le synopsis, il faut utiliser le paramètre Imdb_Source.</li></ul>

<ul><li>Imdb_Source (defaut imdb)<br>
Valeurs possibles: imdb, tmdb, allocine.<br>
Permet de défini sur quel site les images des Pochettes, les images Sheet et le fichier .nfo vont être récupéré. C’est le site qui définit la langue utilisé dans le Synopsis et les images. Pour le Français, il faut prendre allocine.</li></ul>

<ul><li>Imdb_Poster (defaut yes)<br>
yes active la récupération des Pochettes<br>
no les pochettes ne seront pas récupérées.</li></ul>

<ul><li>Imdb_PBox (defaut generic)<br>
Valeurs possibles : no, bdrip, bluray, dtheater, dvd, generic, hddvd, hdtv, itunes<br>
Affiche un cadre pour la pochette.</li></ul>

<ul><li>Imdb_PPost (defaut yes)<br>
Valeurs possibles: yes, no<br>
Si active, la pochette sera choisie aléatoirement parmi les images disponibles sur le site source.</li></ul>

<ul><li>Imdb_Sheet (defaut yes)<br>
yes active la récupération des images Sheet.<br>
no les images Sheet ne seront pas récupérées.</li></ul>

<ul><li>Imdb_SBox (defaut generic)<br>
Valeurs possibles : no, bdrip, bluray, dtheater, dvd, generic, hddvd, hdtv, itunes<br>
Affiche un cadre pour la pochette à l’intérieur de l’image Sheet.</li></ul>

<ul><li>Imdb_SPost (defaut yes)<br>
Valeurs possibles: yes, no<br>
Si active, la pochette sera choisie aléatoirement parmi les images disponibles sur le site source.</li></ul>

<ul><li>Imdb_Backdrop (defaut yes)<br>
Valeurs possibles: yes, no<br>
Si active, le fond de l’image Sheet sera choisi aléatoirement parmi les images disponibles sur le site source.</li></ul>

<ul><li>Imdb_Font (defaut tahoma)<br>
Valeurs possibles :  arial, bookman, comic, tahoma, times, verdana<br>
Permet de définir la police de caractère utilize dans l’image Sheet.</li></ul>

<ul><li>Imdb_Genres (defaut no)<br>
Valeurs possibles: yes, no<br>
Si activé, ce seront des images qui vont être affichées à la place du texte. Ce système marche bien avec des genres en Anglais, à cause de la traduction, il se peut que certains genres Images ne s’affichent pas.</li></ul>

<ul><li>Imdb_Tagline (defaut yes)<br>
Valeurs possibles : yes, no<br>
Permet d’afficher la ligne Tag dans une images Sheet.</li></ul>

<ul><li>Imdb_Time (defaut no)<br>
Valeurs possibles: no, real, hours<br>
Permet de définir le format pour l’affichage de la durée dans une image Sheet.</li></ul>

<ul><li>Imdb_Info (defaut yes)<br>
yes active la récupération des fichiers .nfo<br>
no les fichiers .nfo ne seront pas récupérés.</li></ul>

<ul><li>Imdb_MaxDl (defaut 3)<br>
Indique le nombre de téléchargements simultanés pour récupérer les images et fichiers .nfo<br>
Ce réglage dépend du débit de votre connexion Internet et des ressources de votre Player.<br>
Si vous avez un petit débit, mettez le téléchargement à 1 ou 2.<br>
Si vous mettez un trop gros chiffre, votre Player va être surchargé et sur la durée cela va être aussi long que de se contenter d’un petit nombre.<br>
Les meilleures performances sont généralement atteintes avec 3 ou 4 téléchargements simultanés.</li></ul>

<h1>Films en 2 cd</h1>

Fichiers doivent se terminer par cd1 cd2<br>
Par exemple:<br>
{{{Nom du film cd2.avi<br>
Nom_du_film_cd2.avi}}}<br>
Dans le filtre, il faut qu’il y ait écrit cd2 pour que les 2èmes parties des films ne soient pas intégrées dans le Jukebox.<br>
Un icone va apparaître sur la pochette ou la jaquette, en haut à droite pour indiquer qu’il y a une deuxième partie. Lors du visionnage, à la fin de la première partie, ou si vous appuyez sur la touche arrêt, la deuxième partie va s’enchaîner automatiquement.<br>
<h1>Organisation des fichiers</h1>
<h2>Les films</h2>
Vous avez une grande liberté sur l’organisation de vos fichiers : les films sont repérés automatiquement dans toutes les arborescences.<br>
<pre><code> Dossier principal<br>
  |-- Film 1<br>
  |-- Film 2<br>
  |-- …<br>
<br>
 Dossier principal<br>
  |-- Dossier Film 1<br>
        |-- Film 1<br>
  |-- Dossier Film 2<br>
        |-- Film 2<br>
<br>
 Dossier principal<br>
  |-- Dossier  ensemble 1<br>
        |-- Film 1<br>
        |-- Film 2<br>
        |-- …<br>
        |-- Dossier …<br>
            |-- Film 333<br>
            |-- Film 334<br>
            |-- …<br>
</code></pre>

L'emplacement du « Dossier principal », c'est le chemin des Films. Il est à indiquer dans le fichier de config, ou bien dans le menu configuration de l’interface RSS.<br>
Pour le chemin /tmp/usbmounts/sdb1/film on aura:<br>
<pre><code>&lt;Movies_Path&gt;"/tmp/public/zozo(usb)/film/"&lt;/Movies_Path&gt;<br>
</code></pre>
Notez qu’il y a un / à la fin du chemin.<br>
<br>
<h2>Exclusion de dossiers</h2>
En plaçant un fichier nommé exclu.txt, vous pouvez exclure un dossier pour que les films qui s'y trouvent n'apparaissent pas dans le jukebox.<br>
Dans l'exemple, ci-dessous, tous les films situés dans "Dossier 2" et "Dossier 3" sont exclus du Jukebox.<br>
<br>
<pre><code>Dossier Principal<br>
  |-- Dossier 1<br>
        |-- Film 1<br>
        |-- Film 2<br>
        |-- …<br>
        |-- Dossier 2<br>
            |-- exclu.txt<br>
            |-- Film 222<br>
            |-- Film 223<br>
            |-- …<br>
            |-- Dossier 3<br>
                |-- Film 333<br>
                |-- Film 334<br>
                |-- …<br>
        |-- Dossier 4<br>
            |-- Film 444<br>
            |-- Film 445<br>
            |-- …   <br>
</code></pre>
Vous pouvez mettre autant de fichier exclu.txt que vous voulez, mais n'oubliez pas que s'il n'y a plus rien dans votre Jukebox, c'est peut-être que vous avez mis un fichier exclu.txt au mauvais endroit...<br>
<br>
<h2>Les pochettes, les images Sheet et les fichiers Nfo</h2>

Les pochettes sont des petites images (souvent les affiches des films), en 150x220<br>
Les images Sheets ont une grande taille 1280x720. Elles comportent toute une série d’informations sur le film. Généralement il y aura le titre, des images du Film, un résumé  etc…<br>
Les fichiers Nfo, comportent toutes les informations du film au format texte.<br>
Pour notre Jukebox, il va servir à retrouver :<br>
Le titre original du film et l’afficher à la place du nom de fichier. Si vous avez le nom du fichier lorsque vous sélectionnez un film dans le Jukebox, c’est que le fichier Nfo n’a pas été trouvé.<br>
Le genre auquel appartient le film. Lorsque vous allez rechercher un genre, par exemple science-fiction, vous allez retrouver tous vos films qui comportent le genre science-fiction dans le fichier Nfo. Le même film peut avoir plusieurs genres.<br>
Tous ces fichiers doivent avoir le même nom que les Films (attention, les noms sont sensibles à la case, il faut donc respecter les majuscules/minuscules) :<br>
<pre><code>Mon super Film.avi<br>
Mon super Film.jpg<br>
Mon super Film_sheet.jpg<br>
Mon super Film.nfo<br>
</code></pre>
En fonction des paramètres dans le fichier de config, ces fichiers peuvent être situés à divers endroits:<br>
Nfo_Path, Poster_Path et Sheet_Path peuvent avoir les valeurs suivantes:<br>
MoviesPath :	Correspond au « chemin des films ». Ce sera mélangé avec les fichiers des Films.<br>
SRJG :	Correspond à un sous dossier dans le chemin des films <Chemin des films>/SRJG/ImgNfo<br>
Un chemin :	il faut que ce chemin pointe vers un dossier qui existe<br>
Nfo_Path, Poster_Path et Sheet_Path peuvent avoir des valeurs indépendamment les unes des autres.<br>
Par exemple:<br>
<pre><code>&lt;Movies_Path&gt;/tmp/usbmounts/sdb1/Films/&lt;/Movies_Path&gt;<br>
&lt;Nfo_Path&gt;MoviesPath&lt;/Nfo_Path&gt;<br>
&lt;Poster_Path&gt;/home/Images/Posters/&lt;/Poster_Path&gt;<br>
&lt;Sheet_Path&gt;SRJG&lt;/Sheet_Path&gt;<br>
</code></pre>
Cela peut être utile lorsque les films sont stockés sur une partition protégée en écriture (NAS), vous pouvez décider d’avoir les films sur votre NAS et les images sur un disque local dans votre Player.<br>
<br>
<h2>Comment récupérer des Pochettes, des images Sheet et des fichiers Nfo avec IMDB</h2>

SRJG est capable de récupérer ces fichiers pour vous (pas besoin de Thumbgen, Yamj ou autre).<br>
<br>
<img src='https://lh4.googleusercontent.com/-dEqggOwjwhk/T2j6TVb621I/AAAAAAAAA-w/YzTzeMob5q8/s700/srjg_menu_imdb.jpg' />

Par défaut l'option Imdb est désactivée : elle est très consommatrice de temps, puisqu'elle va permettre à SRJG d'aller chercher sur internet les images et informations. Tout va dépendre de la quantité de films pour lesquels vous voulez ces images, mais aussi de la vitesse de votre connexion Internet.<br>
Si Imdb est activé, les images et .nfo vont être récupérés lorsque vous lancez une Mise à jour du Jukebox. Que ce soit une mise à jour rapide, ou une reconstruction, SRJG commencera par récupérer les fichiers avant de mettre à jour les films.<br>
Imdb ne remplacera pas les Pochettes, images Sheet et fichiers Nfo que vous avez déjà, il va se contenter d'aller chercher ce qu’il manque.<br>
Ce procédé est totalement anonyme, il n'y a aucune collecte d'informations.<br>
Voilà comment ça marche :<br>
<ul><li>Recherche sur votre Player des vidéos pour lesquelles il manque une Pochette, une image Sheet ou un fichier Nfo<br>
</li><li>Épuration de certains caractères dans le nom des fichiers pour être le plus près possible d'un nom de Film<br>
</li><li>Envoi des titres générés à l'Api de playon.unixstorm.org<br>
</li><li>Playon.unixstorm.org interroge les serveurs officiels de vidé comme imdb, allocine.fr pour récupérer les images et in<br>
Si un site fait de la collecte d'informations, il ne verra que des demandes en provenance de Playon.unixstorm.org</li></ul>

<h1>Liste des paramètres</h1>

Si les images générées ne conviennent pas, ou bien les informations contenues correspondent à d'autres films, cela vient généralement du nom de vos fichiers qui ne correspondent pas tout à fait au nom du film. Commencez par vérifier le nom de vos fichiers.<br>
Le site Allocine n’est pas très fiable au niveau des recherches. Ce qui explique que si vous cherchez le film « Le Pari » de Didier Bourdon, vous allez le retrouver en 150ème position dans la liste. Par conséquent le Synopsis de ce film sera le premier de la liste, et pas celui que vous attendiez. Pareil pour « Iron Man »…<br>
<br>
<h1>Suppression des images et .nfo erronés</h1>

Vous pouvez supprimer les Pochettes, Sheet, Nfo erronés depuis SRJG en RSS : activez la fonction « Autoriser Suppression» (paramètre UnlockRM dans srjg.cfg).<br>
Ainsi, lorsque vous êtes sur une pochette de Film (ou un Sheet), appuyez sur « Edit » et supprimez le fichier de votre choix. Lors de la prochaine mise à jour, ces fichiers seront récupérés à nouveau.<br>
Une suppression du fichier .nfo oblige à reconstruire le Jukebox.<br>
Astuce pour éviter une reconstruction :<br>
<ul><li>Changez le nom de votre film<br>
</li><li>Lancez une mise à jour rapide<br>
Si vous tenez à lui remettre son nom d’origine, refaites une autre mise à jour rapide.</li></ul>

<h2>Manuellement</h2>

Sur votre explorateur Internet favori, vous pouvez récupérer les images en essayant des noms plus parlants que les noms vos fichiers.<br>
Le générateur de fichier est situé sur le site de Mikka  <a href='http://playon.unixstorm.org/imdb.php'>http://playon.unixstorm.org/imdb.php</a><br>
Pour récupérer une Pochette<br>
<pre><code>http://playon.unixstorm.org/IMDB/movie.php?name=fight%20club&amp;mode=poster<br>
</code></pre>
Faites un clic droit sur l’image et enregistrez-la sous le <nom de votre film>.jpg<br>
Pour récupérer une image Sheet<br>
<pre><code>http://playon.unixstorm.org/IMDB/movie.php?name=fight%20club&amp;mode=sheet&amp;backdrop=yes&amp;box=generic&amp;post=y&amp;genres=yes<br>
</code></pre>
Faites un clic droit sur l’image et enregistrez-la sous le <nom de votre film><i>sheet.jpg</i><br>
Pour récupérer un fichier Nfo<br>
<pre><code>http://playon.unixstorm.org/IMDB/movie.php?name=fight%20club&amp;mode=info<br>
</code></pre>
Affichez le code source de la page avant de copier ce code dans un fichier du <nom de votre film>.nfo<br>
<br>
<h2>Depuis un ordinateur</h2>

Vous pouvez aussi utiliser d'autres outils pour récupérer ces informations<br>
<ul><li>Thumbgen <a href='http://geekyhmb.niloo.fr/content/thumbgen-0'>http://geekyhmb.niloo.fr/content/thumbgen-0</a>
</li><li>YAMJ <a href='http://geekyhmb.niloo.fr/content/yamj'>http://geekyhmb.niloo.fr/content/yamj</a>
</li><li>SheetMaker <a href='http://geekyhmb.niloo.fr/content/sheetmaker'>http://geekyhmb.niloo.fr/content/sheetmaker</a>
</li><li>Tvixie2PlayOn!HD</li></ul>

<h1>Gestion des Genres</h1>

<blockquote><font color='red'>ATTENTION</font> si vous éditez les fichiers sous Windows, n'utilisez pas "notepad", il va ajouter des CRLF en fin de ligne qui vont faire planter les scripts, utilisez par exemple <a href='http://notepad-plus-plus.org/fr/'>notepad++</a> (gratuit).</blockquote>

Les Genres sont dépendants de la langue utilisée dans le fichier Nfo. Tout va dépendre de la source utilisée pour récupérer ces fichiers, vous aurez des genres en Anglais, et d’autres dans votre langue.<br>
Deux fichiers vont vous servir à paramétrer l’affichage des genres :<br>
<h3>fr_genre</h3>
Ce fichier va faire permettre de rediriger un nom de genre dans votre langue vers un nom de fichier d’images qui se trouve dans le dossier srjg/Images/genre. Le nom des fichiers d’images des genres est en anglais.<br>
<pre><code>|Comédie&gt;Comedy|<br>
</code></pre>
Le genre Comédie va avoir l’image srjg/Images/genre/Comedy.jpg<br>
Vous pouvez avoir plusieurs genres qui vont utiliser la même image.<br>
<pre><code>|Comédie musicale&gt;Music|<br>
|Musical&gt;Music|<br>
</code></pre>
<h3>fr_genreGrp</h3>
Ce fichier va permettre de regrouper des genres entre eux. Par défaut nous avons décidé que tous les films qui appartiennent au genre Sci-Fi soient regroupés avec le genre Science-fiction.<br>
Vous pouvez regrouper d’autres genres entre eux. Par exemple (c’est juste un exemple ). Pour mettre les films qui appartiennent au genre Crime, avec ceux qui sont dans le genre Thriller, vous allez ajouter la ligne suivante dans le fichier :<br>
<pre><code>s:&lt;name&gt;Crime&lt;/name&gt;:&lt;name&gt;Thriller&lt;/name&gt;:<br>
</code></pre>

Ce système peut être utilisé pour traduire les genres. Si vous avez des fichiers Nfo en Anglais, les films vont être attachés à des genres Anglais. En ajoutant des lignes dans ce fichier, vous pouvez les regrouper avec des genres en Français.<br>
Vous pouvez aussi modifier directement les noms de genre dans le fichier Nfo, puisque c’est un simple fichier texte. Il faut repérer les balises<br>
<pre><code>&lt;genre&gt;…&lt;/genre&gt;<br>
</code></pre>

<h1>Tag Vu</h1>

Vous pouvez marquer les films comme étant vu.<br>
Positionnez-vous sur la Pochette, ou bien sur la page Sheet, puis appuyez sur la touche 2. En appuyant une deuxième fois sur 2, vous pouvez enlever le Tag vu.<br>
Le fait de visionner un film va automatiquement le taguer comme vu. Le fait d'arrêter la lecture avec la touche arrêt, n'empêchera pas qu'il soit Tagué, il faudra le dé-taguer manuellement.<br>
Un film qui comporte un Tag vu, n'apparaît plus dans la liste des films « Pas regardés ».<br>
<br>
<h1>Mises à jour</h1>

La première fois que l'on va créer le Jukebox, il va falloir créer la base de données en faisant une mise à jour complète (Reconstruire)<br>
Les mises à jour complètes doivent être exceptionnelles, uniquement si la base est endommagée. Il se peut qu'une nouvelle version du Jukebox demande de reconstruire la base de données. Cela reste tout de même des cas rares. Tant mieux, parce que ça peut être très long, tout dépend du nombre de films que vous avez.<br>
<br>
<h2>Base de données unique ou base de données par Jukebox</h2>

SingleDb est à Non (no dans le fichier srjg.cfg)<br>
La base de données va se créer là <Chemin des films>/SRJG/<br>
Ainsi, vous pouvez avoir plusieurs Jukebox. C'est utile si vous avez plusieurs disques durs (interne ou Usb), ou plusieurs chemins sur un même disque.<br>
Le fait d'avoir une base de données par chemin, vous évite de reconstruire la base si vous changez l'emplacement du  Jukebox.<br>
SingleDb est à Oui (yes dans le fichier srjg.cfg)<br>
La base de données est unique, cela veut dire qu'il n'y a qu'un seul Jukebox. Ce sera plutôt utilisé pour un NAS, ou un chemin qui est protégé contre l'écriture.<br>
L'autre avantage, c'est que les accès à la base seront plus rapides que sur une clé Usb puisqu'elle sera créée dans la mémoire Flash du Player<br>
<pre><code>/usr/local/etc/<br>
</code></pre>
<h2>Dans quels cas faut-il faire une mise à jour ?</h2>
<table><thead><th> <b>Cas de figure</b> </th><th> <b>Type de mise à jour</b> </th></thead><tbody>
<tr><td>Ajout de films        </td><td>Mises à jour Rapide         </td></tr>
<tr><td>Suppression de films directement dans le disque</td><td>Mises à jour Rapide         </td></tr>
<tr><td>Suppression de films en RSS dans le Jukebox</td><td>Pas nécessaire              </td></tr>
<tr><td>Ajout d'une pochette  </td><td>Pas nécessaire              </td></tr>
<tr><td>Ajout d'une page Sheet</td><td>Pas nécessaire              </td></tr>
<tr><td>Suppression d'une pochette</td><td>Pas nécessaire              </td></tr>
<tr><td>Suppression d'une page Sheet</td><td>Pas nécessaire              </td></tr>
<tr><td>Ajout, suppression, modification d'un fichier nfo</td><td>reconstruction complète     </td></tr>
Astuce pour éviter la reconstruction à cause d'un fichier nfo :<br>
Déplacez les films et les nfo hors du chemin du Jukebox, faites une mise à jour rapide (cela va retirer ces films de la base de données) puis remettez-les et refaites une mise à jour rapide. Vos films seront ajoutés avec les données de leur nfo.</tbody></table>

<h1>Utilisation du Jukebox avec un NAS</h1>

<h2>NAS autorisé en lecture seule</h2>

La base de données ne pourra pas accéder au dossier des films, il faudra donc activer le paramètre SingleDb à Oui (yes dans le fichier srjg.cfg).<br>
Il n'y aura qu'une seule base de données, vous n'aurez qu'un seul Jukebox.<br>
Si vous voulez mettre à jour les images Pochettes, Sheets et les fichiers nfo, vous devrez préciser les chemins pour chacun vers des dossiers accessibles en écriture.<br>
Par exemple :<br>
<pre><code>&lt;Movies_Path&gt;/NAS/Films/&lt;/Movies_Path&gt;<br>
&lt;Nfo_Path&gt;/home/Images/Posters/&lt;/Nfo_Path&gt;<br>
&lt;Poster_Path&gt;/home/Images/Posters/&lt;/Poster_Path&gt;<br>
&lt;Sheet_Path&gt;/home/Images/Posters/&lt;/Sheet_Path&gt;<br>
</code></pre>

<h2>NAS autorisé en lecture/écriture</h2>

Vous avez le choix de l'utiliser comme un disque dur en local. Mais si vous trouvez que les accès à la base de données sont très lents, vous pouvez essayer de mettre votre base de données en local en activant SingleDb.<br>
<br>
<h1>A voir</h1>

Comment faire reconnaître un montage NAS sur votre Player<br>
<a href='http://geekyhmb.niloo.fr/content/nas-et-lecteur-r%C3%A9seau'>http://geekyhmb.niloo.fr/content/nas-et-lecteur-r%C3%A9seau</a>

<h1>Dépannage</h1>
<ul><li>Le déplacement dans les Pochettes du Jukebox est extrêmement lent :<br>
Vérifiez la taille des images : 150x220 pour les Pochettes et 1280x<br>
Vous pouvez aussi jouer sur le taux de compression du JPEG.<br>
Comme plus ces images sont petites, plus le déplacement dans le Jukebox est rapide.<br>
Voir comment réduire les images par lot :<br>
Photofiltre <a href='http://geekyhmb.niloo.fr/content/photofiltre'>http://geekyhmb.niloo.fr/content/photofiltre</a>
Phatch <a href='http://geekyhmb.niloo.fr/content/phatch'>http://geekyhmb.niloo.fr/content/phatch</a>