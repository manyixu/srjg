#!/bin/sh
# Simple RSS Jukebox Generator -> web interface
# Author: mikka [mika.hellmann@gmail.com]

cat << EOF
Content-type: text/html

<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<title>SRJG: web-interface</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

<script type="text/javascript">
var one='Directory which will be scanned by SRJG'
var two='Generate moviesheets, thumbnails and NFO files'
var three='Force rebuild of the movies database'
function writetext(what){
document.getElementById('textarea').innerHTML=''+what+'';
}
function notext(){
document.getElementById('textarea').innerHTML='';
}
</script>

<style type="text/css">
* { margin:0; padding:0;}
body { background:#000; font-family:Arial; font-size:100%; line-height:.9375em; color:#7d7d7d; text-align:center;}
p, h1 { margin:10px 10px 10px 10px;}
input, select { vertical-align:middle; font-weight:normal;}
a {color:#fff;}
a:hover{text-decoration:none;}
b.rtop, b.rbottom{display:block;background: #000}
b.rtop b, b.rbottom b{display:block;height: 1px; overflow: hidden; background: #1a1a19}
b.r1{margin: 0 5px}
b.r2{margin: 0 3px}
b.r3{margin: 0 2px}
b.rtop b.r4, b.rbottom b.r4{margin: 0 1px;height: 2px}
.rs1{margin: 0 2px}
.rs2{margin: 0 1px}
div.container1{ margin: 0 2%;background: #1a1a19; width:42%; float: left; margin-bottom:17px;}
div.container2{ margin: 0 2%;background: #1a1a19; width:47%; float: right; margin-bottom:17px;}
div.container3{ margin: 0 2%;background: #1a1a19; width:96%; float: left; margin-bottom:17px;}
.form1 { height:24px; float:left; }
.form1 input {width:81px; height:16px; background:#1d1d1a; border:1px solid #333331; font-size:1em; color:#fff; padding-left:3px;}
.form1 label { width:62px; float:left; text-align:right; margin-right:3px; margin-left:10px;}
.form1 .input_1 { width:131px;}
.form1 select {width:86px; height:18px; background:#1d1d1a; border:1px solid #333331; font-size:1em; color:#fff; line-height:16px;}
.form1 .select_1 { width:136px;}
.input_2 { margin-left:4px;}
.separator { width:50px; float:left;}
#main {width:766px; margin:0 auto; text-align:left;}
#border { border:1px solid #111;}
#header {height:475px;}
#header, #content, #footer { font-size:0.69em;}
#textarea {width:300px; float:left;}
</style>
</head>

<body><div id="main"><br><div id="content">
EOF

echo '
<div class="container1">
<b class="rtop"><b class="r1"></b><b class="r2"></b><b class="r3"></b><b class="r4"></b></b>
	<table align="center" width="70%"><tbody>
		<tr><td><p><h1>Start-up check</h1></p></td></tr>'
	
echo '<tr><td><p>Checking srjg.cfg:</p></td>'
if [ -f "/usr/local/etc/srjg.cfg" ];
then
	echo '<td><font color="green">Found</font></td></tr>'
else
	echo '<td><font color="red">Not found</font></td></tr>'
	exit
fi
	
LANG="`sed '/<Lang/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"
JPATH="`sed '/<Jukebox_Path/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"
SIZE="`sed '/<Jukebox_Size/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"
MPATH="`sed '/<Movies_Path/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"
FILT="`sed '/<Movie_Filter/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"
PORT="`sed '/<Port/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"

echo '<tr><td><p>Checking jukebox path:</p></td>'
if [ -d "$JPATH" ];
then
	echo '<td><font color="green">Found</font></td></tr>'
else
	echo '<td><font color="red">Not found</font></td></tr>'
fi

echo '<tr><td><p>Checking language file:</p></td>'
if [ -f "$JPATH/lang/$LANG" ];
then
	echo '<td><font color="green">Found</font></td></tr>'
else
	echo '<td><font color="red">Not found</font></td></tr>'
fi

echo '<tr><td><p>Checking movies database:</p></td>'
if [ -f "$JPATH/movies.db" ];
then
	echo '<td><font color="green">Found</font></td></tr>'
else
	echo '<td><font color="red">Not found</font></td></tr>'
fi

echo '<tr><td><p>Checking movies path:</p></td>'
if [ -d "$MPATH" ];
then
	echo '<td><font color="green">Found</font></td></tr>'
else
	echo '<td><font color="red">Not found</font></td></tr>'
fi

echo '<tr><td><p>Checking sqlite:</p></td>'
if [ -f "$JPATH/sqlite3" ];
then
	echo '<td><font color="green">'`"$JPATH/sqlite3" --version | cut -d' ' -f1`'</font></td></tr>'
else
	echo '<td><font color="red">Not found</font></td></tr>'
fi


echo '</tbody></table>
<b class="rbottom"><b class="r4"></b><b class="r3"></b><b class="r2"></b><b class="r1"></b></b>
</div>

<div class="container2">
<b class="rtop"><b class="r1"></b><b class="r2"></b><b class="r3"></b><b class="r4"></b></b>
	<table align="center" width="70%"><tbody>
		<tr><td><p><h1>Settings</h1></p></td></tr>'

echo "
<tr><td><p><b>WWW port:</b></p></td><td>$PORT</td></tr>
<tr><td><p><b>Jukebox path:</b></p></td><td>$JPATH</td></tr>
<tr><td><p><b>Language:</b></p></td><td>$LANG</td></tr>
<tr><td><p><b>Jukebox size:</b></p></td><td>$SIZE</td></tr>
<tr><td><p><b>Movies path:</b></p></td><td>$MPATH</td></tr>
<tr><td><p><b>Movies filter:</b></p></td><td>$FILT</td></tr>"

echo '</tbody></table>
<b class="rbottom"><b class="r4"></b><b class="r3"></b><b class="r2"></b><b class="r1"></b></b>
</div>'



echo '
<div class="container3">
<b class="rtop"><b class="r1"></b><b class="r2"></b><b class="r3"></b><b class="r4"></b></b>
	<h1>Generate</h1>
	<form id="form2" action="" enctype="multipart/form-data"><br>
		<div class="form1" onmouseover="writetext(one)" onmouseout="notext()"><label>Path:</label><input type="text" value="'$MPATH'" class="input_1" /></div>	
		<div class="separator">&nbsp;</div>
		<div><input class="input_2" type="image" src="/generate-icon.png" label="Generate jukebox" /></div>
		<div class="form1" onmouseover="writetext(two)" onmouseout="notext()"><label>IMDB plugin:</label><select class="select_1"><option>Yes</option><option>No</option></select></div><br><br>				
		<div class="form1" onmouseover="writetext(three)" onmouseout="notext()"><label>Force:</label><select class="select_1"><option>No</option><option>Yes</option></select></div>
		<div class="separator">&nbsp;</div>						
		<div id="textarea"></div><br><br><br><br>
	</form>						
	
	<p><center><a href="http://code.google.com/p/srjg/">SRJG web panel</a> &copy; 2012</center></p>					
<b class="rbottom"><b class="r4"></b><b class="r3"></b><b class="r2"></b><b class="r1"></b></b>						
</div>
				
</div></div></body></html>'