===============
Sconcho Manual
===============

Sconcho is a tool for creating knitting charts. Charts can be created by placing
a variety of knitting symbols into a rectangular grids. Projects can be saved in
a platform independent format as sconcho project files (spf) and can be edited
at a later time. Charts can be exported in a variety of image formats and also
printed to a printer of saved in PDF or PostScript format.


------

**Starting a new Project**

After startup sconcho by default presents a pattern grid with 10 rows and
10 columns. The grid size can be changed by either

  * starting a new project (**File -> New**) and specifying the proper 
     size in the *New Pattern Grid* dialog.

  * adding the proper number of rows with the 
     *insert/delete rows and columns* dialog (**Grid -> insert/delete row 
     and columns**).


------

**Adding Symbols to Pattern Grid**

Symbols are added to the pattern grid via selecting grid cells and 
then adding the activated symbol from the list of available knitting 
symbols. The presently active symbol (including its background
color) is indicated in the *Active Symbol Tool* in the lower
right hand corner. If no symbol is selected the *Active Symbol Tool* 
displays **No Active Symbol**.

Individual grid cells can be selected in 3 ways:

  1) by using the right mouse button to click on them
  2) by clicking on the row or column labels selecting the respecive 
     row or column. 
  3) a rectangular area can be selected with the *Rubberband Tool* 
     by holding down the **Shift** key and the right mouse button and 
     then dragging the mouse.

Without an active symbol (the *Active Symbol Tool*
shows **No Active Symbol**) selecting grid cells will highlight
them in a light grey color. As soon as a symbol is activated it
will be inserted into the the highlighted grid cells. If a 
symbol is active while selecting grid cells, the symbol will be 
inserted immediately into the highlighted cells. 

**Note:** If a symbol is active which spans more than a single
cell - a 3 stitch cable for example -- the proper number of cells
has to be selected first before the symbol will be inserted.
If cells are highlighted initially without an active symbol and 
followed by choosing an active symbol, sconcho will only add the 
symbol if the whole selection can be completely filled any number
of symbols; sconcho will not just fill some part of the selection.


-----

**Changing a Symbol's Background Color**

With the exception of the **no-stitch** symbol, the background of
all symbols is *white*. The color of the active symbol can be changed
by choosing one of the predefined colors in the *Color Selector Tool*.
The currently selected color is indicated in the *Active Symbol Tool*.
Each of the predefined color selectors can be customized by 
clicking on the *customize color* button and selecting a color.
In addition, one can also load a color from any grid cell into the 
currently selected color selector by **Left Mouse Click -> Grab Color**.





