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

After startup, sconcho by default presents a pattern grid with 10 rows and
10 columns. This initial grid size can be changed by either

  * starting a new project (**File -> New**) and specifying the proper size in the *New Pattern Grid* dialog.

  * adding the proper number of rows with the *Insert/Delete Rows and Columns* dialog (**Grid -> Insert/Delete Rows and Columns**).


------

**Adding Symbols to Pattern Grid**

Symbols are added to the pattern grid via selecting grid cells. These
cells will then be filled with the currently active knitting symbol from
the list of available knitting symbols. 

The presently active symbol (including its background color) is indicated 
in the *Active Symbol Tool* in the lower right hand corner. If no symbol is 
selected the *Active Symbol Tool* displays **No Active Symbol**.

Grid cells can be selected in 3 ways:

  1) individual grid cells can be selected by using the right mouse button to click on them
  2) complete rows or columns can be selected by clicking on the row or column labels
  3) a rectangular area can be selected with the *Rubberband Tool* by holding down the **Shift** key and the right mouse button and then dragging the mouse.

Without an active symbol (the *Active Symbol Tool*
shows **No Active Symbol**) selecting grid cells will highlight
them in a light grey color. As soon as a symbol is activated it
will be inserted into the the highlighted grid cells. If a 
symbol is already active while selecting grid cells, the symbol will be 
inserted into the highlighted cells immediately. 

**Note:** If a symbol is active which spans more than a single
cell - a 3 stitch cable for example -- it will only
be inserted if the selected grid cells can fit the symbols 
exactly (there could be more than one if the *Rubberband Tool* is
used).


-----

**Changing a Symbol's Background Color**

With the exception of the **no-stitch** symbol, the default background of
all symbols is *white*. The color of the active symbol can be changed
by choosing one of the predefined colors in the *Color Selector Tool*.
The currently selected color is indicated in the *Active Symbol Tool*.
The color in each of the predefined color selectors can be customized by 
clicking on the *Customize Color* button and changing the color.
In addition, one can also load a color from any grid cell into the 
currently active color selector by grabbing the color via 
**Left Mouse Click -> Grab Color**.



