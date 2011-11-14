#!/bin/sh

QUERY=$QUERY_STRING
SAVEIFS=$IFS
IFS="@"
set -- $QUERY
CategoryTitle=`echo $1 | sed "s/%20/ /g`
Jukebox_Size=`echo $2`
IFS=$SAVEIFS
GenreSearch=`echo ${CategoryTitle:0:3}`

if [ $Jukebox_Size = "2x6" ]; then
   row="2"; col="6"; itemWidth="14.06"; itemHeight="35.42";
   NewView="3x8";
else
   row="3"; col="8"; itemWidth="10.3"; itemHeight="23.42";
   NewView="2x6";
fi
   
echo -e '
﻿<?xml version="1.0" ?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
	<onEnter>redrawDisplay();</onEnter>

	<script>
	    Jukebox_Temp = "/tmp/";
            Category_Title = "'$CategoryTitle'";
	    Category_Background = "/usr/local/etc/srjg/background.bmp";
	    MovieInfo_RSS = "/tmp/MovieInfo.rss";						           
            setFocusItemIndex(0);
            Current_Item_index=0;
            NewView = "'$NewView'";
            Genre_Title = Category_Title;
	</script>

<mediaDisplay
    	name=photoView

	rowCount='$row'
	columnCount='$col'
	imageFocus=null
	showHeader=no
	showDefaultInfo=no
	drawItemBorder=no

	viewAreaXPC=0
	viewAreaYPC=0
	viewAreaWidthPC=100
	viewAreaHeightPC=100

	itemGapXPC=0.7
	itemGapYPC=1
	itemWidthPC='$itemWidth'
	itemHeightPC='$itemHeight'
	itemOffsetXPC=5.5
	itemOffsetYPC=12.75
	itemBorderPC=0
	itemBorderColor=7:99:176
	itemBackgroundColor=-1:-1:-1

	sideTopHeightPC=0
	sideBottomHeightPC=0
	bottomYPC=100

	idleImageXPC=67.81
	idleImageYPC=89.17
	idleImageWidthPC=4.69
	idleImageHeightPC=4.17
	backgroundColor=0:0:0

     >

		<idleImage> image/POPUP_LOADING_01.png </idleImage>
		<idleImage> image/POPUP_LOADING_02.png </idleImage>
		<idleImage> image/POPUP_LOADING_03.png </idleImage>
		<idleImage> image/POPUP_LOADING_04.png </idleImage>
		<idleImage> image/POPUP_LOADING_05.png </idleImage>
		<idleImage> image/POPUP_LOADING_06.png </idleImage>
		<idleImage> image/POPUP_LOADING_07.png </idleImage>
		<idleImage> image/POPUP_LOADING_08.png </idleImage>'

cat <<EOF
		<backgroundDisplay>
                        <script>
                                Jukebox_itemSize = getPageInfo("itemCount"); 
			</script>
			<image redraw="no" offsetXPC="0" offsetYPC="0" widthPC="100" heightPC="100">
				<script>
					print(Category_Background);
				</script>
		  	</image>      
		</backgroundDisplay>   

                <text redraw="no" align="left" offsetXPC="3" offsetYPC="1" widthPC="100" heightPC="3" fontSize="12" backgroundColor="-1:-1:-1" foregroundColor="130:130:130">1 = Switch View |		
		</text>

                <text redraw="no" align="left" offsetXPC="17" offsetYPC="1" widthPC="90" heightPC="3" fontSize="12" backgroundColor="-1:-1:-1" foregroundColor="130:130:130">Enter = Moviesheet |			
		</text>                

                <text redraw="no" align="left" offsetXPC="34" offsetYPC="1" widthPC="90" heightPC="3" fontSize="12" backgroundColor="-1:-1:-1" foregroundColor="130:130:130">Rtn = Previous Menu/View |			
		</text>     

                <text redraw="no" align="left" offsetXPC="56" offsetYPC="1" widthPC="90" heightPC="3" fontSize="12" backgroundColor="-1:-1:-1" foregroundColor="130:130:130">Play = Play Video/Movie |			
		</text> 

                <text redraw="no" align="left" offsetXPC="76" offsetYPC="1" widthPC="90" heightPC="3" fontSize="12" backgroundColor="-1:-1:-1" foregroundColor="130:130:130">2 = Jukebox Update			
		</text>  
   
		<text redraw="no" align="center" offsetXPC="2.5" offsetYPC="3" widthPC="90" heightPC="10" fontSize="20" backgroundColor="-1:-1:-1" foregroundColor="192:192:192">
			<script>
			    print(Category_Title);
			</script>
		</text>

	<onUserInput>
			<script>
				userInput = currentUserInput();
				Current_Item_index=getFocusItemIndex();
				Max_index = (-1 + Jukebox_itemSize);
				Prev_index = (-1 + Current_Item_index);
				Next_index = (1 + Current_Item_index);
				Prev10_index = (-10 + Current_Item_index);
				Next10_index = (10 + Current_Item_index);

				if (userInput == "pageup" &amp;&amp; Current_Item_index &gt; 9) {
					setFocusItemIndex(Prev10_index); 
					"true";
					redrawDisplay();
				} else if (userInput == "pagedown"  &amp;&amp; Current_Item_index &lt; (Max_index - 9)) {
					setFocusItemIndex(Next10_index); 
					"true";
					redrawDisplay();
				} else if (userInput == "left") {
					"false";
				} else if (userInput == "right") {
					"false";
                                } else if (userInput == "one") {
                                         Genre_Title=urlEncode(Genre_Title); 
					 jumpToLink("SwitchView");
					 "false";
                                         redrawDisplay();
                                } else if (userInput == "two") {                                        
                                        rss = "rss_file:///usr/local/etc/srjg/UpdatingDialog.rss";
                                        ret = doModalRss(rss);
                                        if (ret == "Confirm")    {
                                            writeStringToFile(Jukebox_Temp+"title.tmp", Category_Title);
					    writeStringToFile(Jukebox_Temp+"path.tmp", Jukebox_Path);
                                            jumpToLink("cgiscript");
                                            postMessage("return");
                                         }
					"false";
				} else if (userInput == "video_play") {
                                        Current_Movie_File=getItemInfo(-1, "file");
                                        playItemURL(Current_Movie_File, 10);
					"false";                                   
                                } else if (userInput == "enter") {
                                        
					Current_Movie_Title=getItemInfo(-1, "title");
					writeStringToFile(Jukebox_Temp+"Current_Movie_Title", Current_Movie_Title);

					Current_Movie_File=getItemInfo(-1, "file");
					writeStringToFile(Jukebox_Temp+"Current_Movie_File", Current_Movie_File);

					Current_Movie_Info=getItemInfo(-1, "info");
					writeStringToFile(Jukebox_Temp+"Current_Movie_Info", Current_Movie_Info);

					MovieInfo="";
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;?xml version='1.0' encoding='UTF-8' ?&gt;");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;rss version='2.0' xmlns:dc='http://purl.org/dc/elements/1.1/'&gt;");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;onEnter&gt;showIdle();&lt;/onEnter&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;mediaDisplay name='onePartView' ");
					MovieInfo=pushBackStringArray(MovieInfo, "itemBackgroundColor='0:0:0' ");
					MovieInfo=pushBackStringArray(MovieInfo, "backgroundColor='0:0:0' ");
					MovieInfo=pushBackStringArray(MovieInfo, "sideColorBottom='0:0:0' ");
					MovieInfo=pushBackStringArray(MovieInfo, "sideColorTop='0:0:0' ");
					MovieInfo=pushBackStringArray(MovieInfo, "sideTopHeightPC='0' ");
					MovieInfo=pushBackStringArray(MovieInfo, "sideBottomHeightPC='0' ");
					MovieInfo=pushBackStringArray(MovieInfo, "itemGap='0' ");
					MovieInfo=pushBackStringArray(MovieInfo, "itemGapXPC='0' ");
					MovieInfo=pushBackStringArray(MovieInfo, "itemGapYPC='0' ");
					MovieInfo=pushBackStringArray(MovieInfo, "itemWidthPC='9' ");
					MovieInfo=pushBackStringArray(MovieInfo, "itemHeightPC='5.7' ");
					MovieInfo=pushBackStringArray(MovieInfo, "itemBorderPC='0' ");
					MovieInfo=pushBackStringArray(MovieInfo, "rowCount='1' ");
					MovieInfo=pushBackStringArray(MovieInfo, "columnCount='1' ");
					MovieInfo=pushBackStringArray(MovieInfo, "itemPerPage='1' ");
					MovieInfo=pushBackStringArray(MovieInfo, "imageBorderPC='0' ");
					MovieInfo=pushBackStringArray(MovieInfo, "itemBorderColor='-1:-1:-1' ");
					MovieInfo=pushBackStringArray(MovieInfo, "itemImageWidthPC='0' ");
					MovieInfo=pushBackStringArray(MovieInfo, "itemImageHeightPC='0' ");
					MovieInfo=pushBackStringArray(MovieInfo, "itemXPC='100' ");
					MovieInfo=pushBackStringArray(MovieInfo, "itemYPC='100' ");
					MovieInfo=pushBackStringArray(MovieInfo, "centerHeightPC='100' ");

					MovieInfo=pushBackStringArray(MovieInfo, "showHeader='no' ");
					MovieInfo=pushBackStringArray(MovieInfo, "showDefaultInfo='no' ");
					MovieInfo=pushBackStringArray(MovieInfo, "idleImageWidthPC='9' ");
					MovieInfo=pushBackStringArray(MovieInfo, "idleImageHeightPC='16' ");

					MovieInfo=pushBackStringArray(MovieInfo, "&gt; ");

					MovieInfo=pushBackStringArray(MovieInfo, "&lt;idleImage&gt; image/POPUP_LOADING_01.png &lt;/idleImage&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;idleImage&gt; image/POPUP_LOADING_02.png &lt;/idleImage&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;idleImage&gt; image/POPUP_LOADING_03.png &lt;/idleImage&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;idleImage&gt; image/POPUP_LOADING_04.png &lt;/idleImage&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;idleImage&gt; image/POPUP_LOADING_05.png &lt;/idleImage&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;idleImage&gt; image/POPUP_LOADING_06.png &lt;/idleImage&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;idleImage&gt; image/POPUP_LOADING_07.png &lt;/idleImage&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;idleImage&gt; image/POPUP_LOADING_08.png &lt;/idleImage&gt; ");

					MovieInfo=pushBackStringArray(MovieInfo, "&lt;backgroundDisplay&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;image offsetXPC='0' offsetYPC='0' widthPC='100' heightPC='100' &gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, Current_Movie_Info);
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/image&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/backgroundDisplay&gt; ");

					MovieInfo=pushBackStringArray(MovieInfo, "&lt;onUserInput&gt;");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;script&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "userInput = currentUserInput();");
					MovieInfo=pushBackStringArray(MovieInfo, "if (userInput == &amp;quot;left&amp;quot;) {&amp;quot;true&amp;quot;;	} else if (userInput == &amp;quot;right&amp;quot;) {&amp;quot;true&amp;quot;;	}");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/script&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/onUserInput&gt;");

					MovieInfo=pushBackStringArray(MovieInfo, "&lt;itemDisplay&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;image offsetXPC='0' offsetYPC='0' widthPC='100' heightPC='100' &gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;script&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "if(getItemInfo(&amp;quot;Info&amp;quot;) == &amp;quot;PLAY&amp;quot;) ");
					MovieInfo=pushBackStringArray(MovieInfo, "if(getDrawingItemState() == &amp;quot;focus&amp;quot;) { ");
					MovieInfo=pushBackStringArray(MovieInfo, "&amp;quot;"Yamj_play_selected.png" + "&amp;quot;; ");
					MovieInfo=pushBackStringArray(MovieInfo, "} else { ");
					MovieInfo=pushBackStringArray(MovieInfo, "&amp;quot;"Yamj_play_selected.png" + "&amp;quot;; ");
					MovieInfo=pushBackStringArray(MovieInfo, "} ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/script&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/image&gt; ");

					MovieInfo=pushBackStringArray(MovieInfo, "&lt;text offsetXPC='20' offsetYPC='0' widthPC='100' heightPC='100' backgroundColor='-1:-1:-1' fontSize='15'&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;script&gt;getItemInfo(&amp;quot;Info&amp;quot;);&lt;/script&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;foregroundColor&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;script&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "if(getDrawingItemState() == &amp;quot;focus&amp;quot;) &amp;quot;192:192:0&amp;quot;; else &amp;quot;101:101:101&amp;quot;; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/script&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/foregroundColor&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/text&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/itemDisplay&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/mediaDisplay&gt; ");

					MovieInfo=pushBackStringArray(MovieInfo, "&lt;channel&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;title&gt;Movies&lt;/title&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;link&gt;rss_file://" + MovieInfo_RSS+"&lt;/link&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;menu&gt;main menu&lt;/menu&gt; ");

					MovieInfo=pushBackStringArray(MovieInfo, "&lt;item&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;title&gt;"+ Current_Movie_Title+ "&lt;/title&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;Info&gt;PLAY&lt;/Info&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;media:thumbnail url='Yamj_play_selected.png' width='0' height='0' /&gt; ");

					MovieInfo=pushBackStringArray(MovieInfo, "&lt;enclosure url='"+Current_Movie_File + "' /&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/item&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/channel&gt; ");
					MovieInfo=pushBackStringArray(MovieInfo, "&lt;/rss&gt; ");
					writeStringToFile(MovieInfo_RSS, MovieInfo);
					jumpToLink("moviesheet");
					"false";
				}
			</script>
		</onUserInput>

<!-- Show Folder Name -->
<text offsetXPC=7 offsetYPC=88.8 widthPC=60 heightPC=5 fontSize=14 useBackgroundSurface=yes foregroundColor=195:196:195 redraw=yes lines=1>
 <script>
    displayTitle = getItemInfo(-1, "title"); 
    displayTitle;
 </script>
</text>


<!-- Show Page Info -->
<text offsetXPC=85 offsetYPC=88.8 widthPC=8 heightPC=5 fontSize=14 foregroundColor=195:196:195 useBackgroundSurface=yes redraw=yes lines=1>
 <script>
  pageInfo = Add(getFocusItemIndex(),1) + "/" + Jukebox_itemSize;
  pageInfo;
 </script>
</text>

<itemDisplay>

<!-- Bottom Layer focus/unfocus -->
<image offsetXPC=0 offsetYPC=0 widthPC=100 heightPC=100>

 <script>
  if (getDrawingItemState() == "focus")
  {
      "/usr/local/etc/srjg/focus.bmp";
  }
  else
  {
      "/usr/local/etc/srjg/unfocus.bmp";
  }
 </script>
</image>

<!-- Top Layer folder.jpg -->
<image offsetXPC=8.2 offsetYPC=5.5 widthPC=84.25 heightPC=89.25>
 <script>
  
  thumbnailPath = getItemInfo(-1, "poster");
  thumbnailPath;
 </script>
</image>

</itemDisplay>
</mediaDisplay>

<moviesheet>
    <link>
       <script>
           print("rss_file://"+MovieInfo_RSS);
       </script>
    </link>
</moviesheet>

<cgiscript>
  <link>http://127.0.0.1/cgi-bin/jukebox_update.cgi</link>  
</cgiscript>

<SwitchView>
    <link>
       <script>
           print("http://127.0.0.1/cgi-bin/jukebox.cgi?"+Genre_Title+"@"+NewView);
       </script>
    </link>
</SwitchView>

<channel>
	<title><script>Category_Title;</script></title>
	<link><script>Category_RSS;</script></link>
	<itemSize><script>Jukebox_itemSize;</script></itemSize>
EOF


if [ "$GenreSearch" = "All" ]; then
   /home/srjgsql/sqlite3 -separator ''  /home/srjgsql/movies.db  "SELECT * FROM t1 ORDER BY title COLLATE NOCASE"; # All Movies
else
   /home/srjgsql/sqlite3 -separator ''  /home/srjgsql/movies.db  "SELECT head,title,poster,info,file,footer FROM t1 WHERE genre LIKE '%$GenreSearch%' ORDER BY title COLLATE NOCASE";
fi   

echo -e '
</channel>
</rss>'

exit 0




