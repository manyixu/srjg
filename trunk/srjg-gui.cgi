#!/bin/sh
# Simple RSS Jukebox Generator -> web interface
# Author: mikka [mika.hellmann@gmail.com]

cat << EOF
Content-type: text/html

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head><title>SRJG: web-interface</title><body><table align="center" width="70%"><tbody><tr><td><h3>Start-up check</h3></td><td></td><td width="30%">&nbsp;</td><td><h3>Settings</h3></td><td></td></tr>
EOF

echo '<tr><td>Checking srjg.cfg:</td>'
if [ -f "/usr/local/etc/srjg.cfg" ];
then
	echo '<td><font color="green">Found</font></td>'
else
	echo '<td><font color="red">Not found</font></td>'
	exit
fi

LANG="`sed '/<Lang/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"
JPATH="`sed '/<Jukebox_Path/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"
SIZE="`sed '/<Jukebox_Size/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"
MPATH="`sed '/<Movies_Path/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"
FILT="`sed '/<Movie_Filter/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"
PORT="`sed '/<Port/!d;s:.*>\(.*\)</.*:\1:' /usr/local/etc/srjg.cfg | grep "[!-~]"`"

echo "<td width="30%">&nbsp;</td><td><b>WWW port:</b></td><td>$PORT</td></tr>"


echo '<tr><td>Checking language file:</td>'
if [ -f "$JPATH/lang/$LANG" ];
then
	echo '<td><font color="green">Found</font><br></td>'
else
	echo '<td><font color="red">Not found</font><br></td>'
fi

echo "<td width="30%">&nbsp;</td><td><b>Language:</b></td><td>$LANG</td></tr>"


echo '<tr><td>Checking jukebox path:</td>'
if [ -d "$JPATH" ];
then
	echo '<td><font color="green">Found</font><br></td>'
else
	echo '<td><font color="red">Not found</font><br></td>'
fi

echo "<td width="30%">&nbsp;</td><td><b>Jukebox path:</b></td><td>$JPATH</td></tr>"


echo '<tr><td>Checking movies database:</td>'
if [ -f "$JPATH/movies.db" ];
then
	echo '<td><font color="green">Found</font><br></td>'
else
	echo '<td><font color="red">Not found</font><br></td>'
fi

echo "<td width="30%">&nbsp;</td><td><b>Jukebox size:</b></td><td>$SIZE</td></tr>"


echo '<tr><td>Checking movies path:</td>'
if [ -d "$MPATH" ];
then
	echo '<td><font color="green">Found</font><br></td>'
else
	echo '<td><font color="red">Not found</font><br></td>'
fi

echo "<td width="30%">&nbsp;</td><td><b>Movies path:</b></td><td>$MPATH</td></tr>"


echo '<tr><td>Checking sqlite:</td>'
if [ -f "$JPATH/sqlite3" ];
then
	echo '<td><font color="green">'`"$JPATH/sqlite3" --version | cut -d' ' -f1`'</font><br></td>'
else
	echo '<td><font color="red">Not found</font><br></td>'
fi

echo "<td width="30%">&nbsp;</td><td><b>Movies filter:</b></td><td>$FILT</td></tr>"

echo '</tbody></table><br><br><br>'

echo '<table align="center" width="70%"><tbody><tr><td><h3>Generate jukebox</h3></td><td></td></tr>'


echo '</tbody></table></body></html>'