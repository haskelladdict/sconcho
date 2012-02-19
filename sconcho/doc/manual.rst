Sconcho Manual
--------------

*Author: Markus Dittrich (last change 02/19/2012)*

Sconcho is a tool for creating knitting charts. Charts can be created by 
placing stitch patterns into a rectangular grid. Sconcho has a large
number of predefined knitting symbols and you can also define and import
your own. Knitting charts can be saved in a platform independent format 
as sconcho project files (spf) and can be edited at a later time. Charts 
can be exported in a variety of image formats (jpg, png, etc.) and also 
printed to a printer of saved in PDF or PostScript format (on Linux and
Mac OSX).


**Contents of this manual**:

* `Starting a new Project`_
* `Interacting with Sconcho`_
* `Adding Symbols to Pattern Grid`_
* `Copy and Pasting a Selection`_
* `Un-doing/Re-doing Canvas Actions`_
* `Changing a Symbol's Background Color`_ 
* `Changing the Legend Layout`_
* `Adding Pattern Repeat Boxes`_
* `Adding Row Repeats`_
* `Inserting and Deleting Columns and Rows in the Chart`_
* `Saving and Opening Sconcho Projects`_
* `Exporting and Printing Charts`_
* `Changing the Label and Legend Properties`_
* `Creating your own Custom Symbols`_


Starting a new Project
~~~~~~~~~~~~~~~~~~~~~~

After start-up, sconcho by default presents a pattern grid with 10 rows and
10 columns. This initial grid size can be changed by 

  * starting a new project (**File -> New**) and specifying the intended size in the *New Pattern Grid* dialog.

  * adding the proper number of rows with the *Insert/Delete Rows and Columns* dialog (**Grid -> Insert/Delete Rows and Columns**).


Interacting with Sconcho
~~~~~~~~~~~~~~~~~~~~~~~~

Most interactions with sconcho only require a simple mouse click. One of
the most fundamental interaction is the selection of any number of grid
cells. Selected grid cells can then be filled with knitting symbols, 
a color, or both (see `Adding Symbols To Pattern Grid`_).

There are a number of additional ways to select cells on the pattern grid 
all of which involve holding down the **Shift key** while clicking:

* Shift + right mouse clicking and then dragging the mouse across the 
  pattern grid will activate the *Rubberband Tool*. 
  Upon releasing the mouse button all 
  grid cells under the rubberband will either be selected or un-selected 
  based on their previous state. If there is a knitting symbol active it 
  will be placed immediately if it fits into the selection area.

* Shift + right mouse clicking adjacent to the left/right or top/bottom 
  edge of the pattern grid will select/unselect the neighboring complete 
  row or column based on its previous state. If there 
  is an active knitting symbol it will be placed into the selection.

Finally, several items on the knitting chart can be moved around. Movable 
items are: legend items (both symbols and text) and repeat boxes on the 
canvas. In order to move items, hold down the **Control key** then click 
on the item with the right mouse button and start dragging. Releasing the 
mouse button will cause the item to be placed at the current 
mouse pointer location.


Adding Symbols to Pattern Grid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can add symbols to the pattern grid via selecting grid cells. Selected
cells will turn gray if there is no knitting symbol active. Clicking on
selected cells once more will un-select them again. If a knitting symbol 
is currently active, sconcho will try to immediately place it into the 
selected cell if possible (e.g., sconcho can not place a three stitch 
cable into a single selected cell. In order to place it at a multiple of 
three adjacent cells has to be selected). If you first select a number
of cells without an active symbol, sconcho will try to place the active
knitting symbol as soon as you select one.

The presently active symbol (including its background color) is indicated 
in the *Active Symbol Tool* in the lower right hand corner. If no symbol is 
selected the *Active Symbol Tool* displays **No Active Symbol**.

As previously mentioned in `Interacting with Sconcho`_ Grid cells can be 
selected in three ways:

  1) individual grid cells can be selected by using the right mouse button 
  to click on them
  2) complete rows or columns can be selected by holding down the 
  **Shift** key and clicking on the row or column labels. If the label 
  spacing is larger than 1, Control-clicking in empty row/column label 
  positions will also select whole rows/columns.
  3) a rectangular area can be selected with the *Rubberband Tool* by 
  holding down the **Shift** key and the right mouse button and then 
  dragging the mouse.

**Note:** If a symbol is active which spans more than a single
cell - a 3 stitch cable for example -- it will only
be inserted if the selected grid cells can fit the symbols 
exactly.


Copy and Pasting a Selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can copy and paste any rectangular collection of cells by selecting 
them first and then copying them via
**Right Mouse Click -> Copy Selection**. The cells copied in this fashion
can then be pasted via **Right Mouse Click -> Paste Selection** as 
often as needed. 

**Note:** Before selecting cells for copying make sure no knitting
symbol is currently active. Otherwise, sconcho will insert it into 
the selection. In any case, if this happens to you, you can always undo 
this action.

Pasting will insert the most recently copied rectangular selection such 
that the grid cell under the mouse pointer will be at the upper left 
hand corner. When pasting, the target area has to fit the copied selection 
exactly, i.e., pasting can not leave cells half filled. If pasting is not
possible at the requested location, the *Paste Selection* option is grayed 
out.

**Note:** Presently, only rectangular selections can be copied and pasted. 
If the current selection is not rectangular or consists of multiple 
disconnected pieces it can not be copied and the *Copy Selection* option 
is grayed out.



Un-doing/Re-doing Canvas Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sconcho allows unlimited undo and redo of all canvas actions,
including adding symbols, copy & paste, deleting/inserting rows and 
columns, changing colors, and moving and editing legend items.


Changing a Symbol's Background Color
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With the exception of the **no-stitch** symbol, the default background of
all symbols is *white*. The color of the active symbol can be changed
by choosing one of the predefined colors in the *Color Selector Tool*.
The currently selected color is indicated in the *Active Symbol Tool*.
You can customize the color in each of the predefined color selectors by 
clicking on the *Customize Color* button and selecting a color.
In addition, one can also load a color from any grid cell into the 
currently active color selector by grabbing the color via 
**Right Mouse Click -> Grab Color**.



Changing the Legend Layout
~~~~~~~~~~~~~~~~~~~~~~~~~~

For each new colored symbol used, sconcho places a legend entry
consisting of a symbol and its description on the canvas. Both the symbol 
and the text can be moved separately anywhere on the canvas and the 
default description for a symbol can be changed.

To move a legend symbol or text item hold down the **Control Key**
(the **Command Key** on Mac OSX) and **Left Mouse Click** on the
desired item. The cursor should change to a cross shape and
the item can now be moved. 

**Note**: To move a text item click on the perimeter not the center
of the item.

To change the text of a legend item **Left Mouse Click** on its 
center and start editing.

If no legend is desired at all it can be turned off via un-checking
**View -> Show Legend**.  


Adding Pattern Repeat Boxes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pattern repeat boxes can be added to the pattern grid. Simply highlight
all cells that should be inside the repeat box (i.e., the repeat box will
be the outline of the selected cells) and click on
**View -> Create Pattern Repeat** to create it. To change the color and
line thickness of an existing repeat box or to delete a repeat box, 
right mouse click anywhere within the pattern repeat box and 
select *Edit Pattern Repeat* in the menu that will appear.
This will open a dialog window for changing the repeat box's properties. 

Pattern repeat boxes by default have a legend entry associated with them
consisting of a symbol showing a rectangular box of the same 
color as the pattern repeat and a text box whose content can be modified. 
The visibility of the legend entry for a repeat box can be toggled
on or off in its *Edit Pattern Repeat* dialog.  

To move a pattern repeat box hold down the **Control Key**
(the **Command Key** on Mac OSX) and **Left Mouse Click** on the
desired item. The cursor should change to a cross shape and the
repeat box can now be dragged while holding down the left mouse
button.


Adding Row Repeats
~~~~~~~~~~~~~~~~~~

You can add any number of non-overlapping row repeats to your chart. 
Sconcho will automatically adjust the row labels for you in this case.
To add a row repeat select any number of **consecutive** rows.
Then right mouse click anywhere outside the chart area to bring up the 
**Row And Column Management Menu**. Select *add row repeat*
and then the number of repeats in the appearing
repeat dialog.

A row repeat can be deleted by selecting at least one
complete row within the repeat. Selecting *delete row repeat* in the 
**Row And Column Management Menu** will then delete 
the repeat. 


Inserting and Deleting Columns and Rows in the Chart
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deleting rows and columns is straightforward. First, select the rows 
or columns you would like to delete. Next, open up the 
**Row And Column Management Menu** by right mouse clicking anywhere
outside the actual chart area and then selecting "delete selected rows" 
or "delete selected columns". 

**NOTE:** Deleting of rows and columns is only possible
if complete rows or columns have been selected. If the current
selection is anything but either complete rows or columns,
deleting is disabled and these options are grayed out.

To add rows or columns mark a **single** complete row/column.
Next, open up the **Row And Column Management Menu** by 
right mouse clicking outside the chart area and then selecting 
the desired add row or column selection.


Saving and Opening Sconcho Projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sconcho projects can be saved in a platform independent binary 
format called *sconcho project format (spf)*. spf files typically end
with the extension .spf. spf files can then be re-opened in sconcho.



Exporting and Printing Charts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can either print your sconcho project on a printer (or print
to a PDF file on some platforms), export it as a bitmapped image
file, or save it as an svg image. The available image file formats 
depend on the operating system and are listed at the bottom of
the *Export As Bitmap or Svg* dialog.

To enable the generation of non-rectangular image files, sconcho can 
hide all *nostitch* symbols in the exported image of your pattern.
Check *Hide Nostitch Symbols* in the export dialog to enable this.



Changing the Label and Legend Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The font and size of the labels or the legend can be changed independently 
in the preferences dialog (**File -> Preferences**). Furthermore the 
preferences dialog allows one to select the *interval i* with which the 
labels are displayed. By default, *i* is set to 1. Both the label and 
legend font, size as well as label interval are saved in sconcho project 
files and will be restored upon loading a previously saved project.


Creating your own Custom Symbols
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the *Manage Custom Knitting Symbols* dialog (**Edit -> Manage Custom
Knitting Symbols**) you can add your own knitting symbols and make them
available within sconcho. 

To *add* a new symbol click on the *Add New Symbol* button. Then enter the
required information in the respective fields of the dialog. You need to provide
an SVG image file of your symbol, a symbol name, category, default
width and finally a symbol description. Then click on *Add Symbol*.
You can cancel adding the symbol by pressing *Cancel* at any time.

**Please Note:**: 

Sconcho does not provide a facility for creating the SVG images needed for a new symbol. You can use the excellent program Inkscape <http://inkscape.org/> for this purpose. Inkscape was also used to create the symbols that come with sconcho.

By default, your new symbols are stored within your home directory 
(*C:/Documents and Settings/Username* on Windows). You can change the location 
in the *Custom Symbols & Logging* tab of the *Preferences* Dialog.

The currently selected custom symbol can be updated or deleted. Deletion is
only possible if the symbol does not appear in the currently worked on chart. 
Similarly, updating is only possible if the name, svg name, and width remain
the same. Otherwise, close your current session, open a blank document and
delete/update then which is always possible. 

Updating or deleting a symbol will cause your undo history to be lost. Thus,
in general it is advisable to *not* add/update/delete new symbols while
working on an important chart.

**Please Note:**:

If you delete (or update the name of) a symbol any previously saved sconcho 
projects which include this symbol will cease to load properly. Thus, please 
think twice before removing or updating a symbol.




