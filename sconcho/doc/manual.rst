Sconcho version 0.1 Manual
--------------------------

*Author: Markus Dittrich (last updated 04/10/2012)*

**About Sconcho**:

Sconcho is a tool for designing knitting charts of any dimension. 
Sconcho comes with a large number of predefined knitting symbols and 
it is very easy to define and import your own. Knitting charts can be 
saved in a platform independent format as sconcho project files (spf) 
which can be opened and edited at a later time. Charts can be exported 
into a variety of image formats (jpg, png, pdf on Linux and Mac OSX) 
or printed to a printer.

**Contents of this manual**:

* `Starting a new Project`_
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
* `Changing Chart Properties`_
* `Creating your own Custom Symbols`_


Starting a new Project
~~~~~~~~~~~~~~~~~~~~~~

After start-up, sconcho by default presents a pattern grid with 10 rows and
10 columns. This initial grid size can be changed by 

  * starting a new project (**File -> New**) and specifying the intended size in the *New Pattern Grid* dialog.

  * adding the desired number of rows and columns.


Adding Symbols to Pattern Grid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can add symbols to the pattern grid by selecting grid cells via:

* Clicking on cells individually 

* Shift + right mouse clicking and then dragging the mouse across the 
  pattern grid will activate the *Rubberband Tool*. Upon releasing the 
  mouse button, all grid cells in the area covered by the rubberband will 
  either be selected or un-selected based on their previous state. If there 
  is a knitting symbol active it will be placed immediately into the
  selection assuming it (or multiples of it) fits.

* Shift + right mouse clicking adjacent to the left/right or top/bottom 
  edge of the pattern grid will select/unselect all cells in the adjacent 
  row or column based on each grid cell's previous state. If there 
  is an active knitting symbol it will be placed into the selection.

Selected cells will turn gray if there is no knitting symbol active
otherwise the active knitting symbol will be inserted if it fits into
the selection (e.g. a three stitch cable can not be added to a single
selected cell, a multiple of three adjacent cells would have to be
selected). Clicking on (or otherwise selecting) currently selected 
cells will un-select them again. If you first select a number
of cells without an active symbol and then select one, sconcho will try 
to immediately place the active knitting symbol.

Active symbols can be selected by choosing from the list
of available symbols on the right a category and associated symbol. 
The currently active symbol (including its background color) is shown
in the *Active Symbol Tool* above the canvas on the left. If no symbol is 
selected, the *Active Symbol Tool* displays **No Active Symbol**.

Finally, you can select all patter grid cells of a certain color or
type in one swoop by right mouse clicking on a cell with the desired
color/symbol and then choosing the proper option in the selector menu.


Copy and Pasting a Selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can copy and paste any selection on your chart. To copy, select a region
(make sure to disable the currently active symbol first) and then 
**Edit -> Copy** (or **Ctrl+C** hotkey). Next, you can
paste this selection into your chart. To do so either

  1) Select the region on the canvas you would like to paste into and then
  **Edit -> Paste** (or **Ctrl-V** hotkey). This
  region has to have the same size and shape (or a multiple) of the 
  originally copied selection. In the latter case, sconcho will paste the
  respective number of copies. E.g. if you paste a 3x4 block into a 6x12 
  selection you get 6 copies of your original. 

  2) Right click on the canvas and in the pop-up menu select 
  **Paste**. Sconcho will try to paste a single
  copy of your selection such that the cell you clicked on will become the 
  upper left hand corner. This may fail if there is not enough space or
  due to the layout (e.g. you can not paste partially over a stitch, such as 
  half of a 2 stitch cable).


Un-doing/Re-doing Canvas Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sconcho allows unlimited undo and redo of all canvas actions,
including adding symbols, copy & paste, deleting/inserting rows and 
columns, changing colors, and moving and editing legend items.


Changing a Symbol's Background Color
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With exception of the **no-stitch** symbol, the default background of
all symbols is *white*. The color of the active symbol can be changed
by choosing one of the predefined colors in the *Color Selector Tool*
or by customizing one (via **customize color**). The selected color 
will be reflected in the *Active Symbol Tool*. You can also load a color
from any grid cell in your chart into the currently active 
color selector by **Right Mouse Click -> Grab Color**.


Changing the Legend Layout
~~~~~~~~~~~~~~~~~~~~~~~~~~

For each new colored symbol used, sconcho places a legend entry
consisting of a symbol and its description on the canvas. Both the symbol 
and the text can be moved separately anywhere on the canvas. 
The default description text for a symbol can be changed
by clicking on and editing it.

To move a legend symbol or text item hold down the **Control Key**
(the **Command Key** on Mac OSX) and **Left Mouse Click** on the
desired item. The cursor should change to a cross shape and
the item can now be moved. 

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
if complete rows or columns have been selected. 

To add rows or columns mark a **single** complete row/column as
pivot. Next, open up the **Row And Column Management Menu** by 
right mouse clicking outside the chart area and then selecting 
the either add row or column.


Saving and Opening Sconcho Projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sconcho projects can be saved in a platform independent binary 
format called *sconcho project format (spf)*. spf files typically end
with the extension .spf. spf files can then be re-opened in sconcho.



Exporting and Printing Charts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can either print your sconcho project to a printer (or print
to a PDF file on some platforms), export it as a bitmapped image
file, or save it as an svg image. The available image file formats 
depend on the operating system and are listed at the bottom of
the *Export As Bitmap or Svg* dialog.

To enable the generation and export of non-rectangular knitting
charts, sconcho can hide all *nostitch* symbols in the exported image 
of your pattern. Check *Hide Nostitch Symbols* in the export dialog to 
enable this.


Changing Chart Properties
~~~~~~~~~~~~~~~~~~~~~~~~~

The preferences dialog (**File -> Preferences**) allows you to
change many properties of your chart such as font and size of 
labels or the legend, label intervals and location and much more.
Just take a look at what is available.


Creating your own Custom Symbols
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the *Manage Custom Knitting Symbols* dialog (**Edit -> Manage Custom
Knitting Symbols**) you can add your own knitting symbols and make them
available within sconcho. 

To *add* a new symbol click on the *Add New Symbol* button. Then enter the
required information in the respective fields of the dialog. You need to 
provide an SVG image file of your symbol, a symbol name, category, default
width and finally a symbol description. Then click on *Add Symbol*.
You can cancel adding the symbol by pressing *Cancel* at any time.

**Please Note:**: 

Sconcho does not provide a facility for creating the SVG images needed for 
a new symbol. You can use the excellent program Inkscape 
<http://inkscape.org/> for this purpose. Inkscape was also used to create 
the symbols that come with sconcho.

By default, your new symbols are stored within your home directory 
(*C:/Documents and Settings/Username* on Windows). You can change the 
location in the *Custom Symbols & Logging* tab of the *Preferences* Dialog.
If you change the location any existing custom symbols in the old location
will be lost until you copy them into the new location "by hand".

The currently selected custom symbol can be updated or deleted. Deletion is
only possible if the symbol does not appear in the currently worked on chart. 
Similarly, updating is only possible if the name, svg name, and width remain
the same. Otherwise, close your current session, open a blank document and
delete/update then which is always possible. 

Updating or deleting a symbol will cause your undo history to be lost. Thus,
in general it is advisable to *not* add/update/delete new symbols while
working on an important chart.

You can export all your custom symbols as a single zip file for sharing
with others. Conversely, you can import zipped up custom symbols from
others and use them for your projects. 

**Please Note:**:

If you delete (or update the name of) a symbol any previously saved sconcho 
projects which include this symbol will cease to load properly. Thus, please 
think twice before removing or updating a symbol.




