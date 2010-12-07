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


-----

**Changing the Legend Layout**

For each new symbol and color used, sconcho places a legend entry
consisting of a symbol and its description on the canvas. Both the symbol 
and the text can be moved separately anywhere on the canvas and the 
default description for a symbol can be changed.

If no legend is desired at all it can be turned off via un-checking
**View -> Show Legend**.  


-----

**Inserting and Deleting Columns and Rows in the Chart**

Additional rows and columns can be inserted into and deleted from an 
already existing chart using the *Insert/Delete Rows and Columns* dialog 
(**Grid -> Insert/Delete Rows and Columns**). Here, it is important to keep 
in mind that while it is always possible to add and remove rows, columns can 
be added only if the new row does not appear within an already existing 
multi-cell symbol. Similarly, a column can be removed only if it is not 
part of a multi-cell symbol.


----

**Saving and Opening Sconcho Projects**

Sconcho projects can be saved in a platform independent binary 
format called *sconcho project format (SPF)*. SPF files typically end
with the extension .spf. SPF files can then be re-opened in sconcho.


----

**Exporting and Printing Charts**

You can either print your sconcho project on a printer (or print
to a PDF file on some platforms) or export it as a bitmapped image
file such as jped, tif, or png. The available image 
file formats depends on the operating system. Soncho project can 
also be saved in svg format.


----

**Changing the Label and Legend Properties**

The font and size of the labels or the legend can be changed independently in 
the preferences dialog (**File -> Preferences**). Furthermore the preferences
dialog allows one to select the *interval i* with which the labels are displayed.
By default, i is set to 1. Both the label and legend font, size as well as label 
interval are saved in sconcho project files and will be restored upon loading a
previously saved project.
