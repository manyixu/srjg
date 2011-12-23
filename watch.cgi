#!/bin/sh

# Parsing query string provided by the server/client
QUERY=$QUERY_STRING

# Setting up variable according to srjg.cfg file
. /tmp/srjg.cfg

Database=${Jukebox_Path}"/movies.db"
Sqlite=${Jukebox_Path}"/sqlite3"

echo -e '
<?xml version="1.0" ?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
<onEnter>
redrawDisplay();
postMessage("return");
</onEnter>'

watch="`${Sqlite} -separator ''  ${Database}  "SELECT Watched FROM t1 WHERE Movie_ID like '$QUERY'";`"

if [ $watch == "1" ]; then
      watch="0";
else
     watch="1";
fi

${Sqlite} ${Database} "UPDATE t1 set Watched=$watch WHERE Movie_ID like '$QUERY'";

echo -e '
<channel>
<item>
</item>
</channel>
</rss>'

exit 0
                              
          
