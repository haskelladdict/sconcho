Sconcho version 0.1 Manual
--------------------------

*Author: Markus Dittrich (last updated 04/10/2012)*

**About Sconcho**:

Sconcho is a tool for designing publication quality knitting charts. 
Sconcho comes with a large number of included knitting symbols and 
it is very easy to create your own. Knitting charts can be 
saved in a platform independent format as sconcho project files (spf) 
which can be opened and edited at a later time. Charts can be exported 
into a variety of image (jpg, png, tif, etc.) and document formats
(pdf, post-script on Linux and Mac OSX) or printed to a printer.

**Contents of this manual**:

* `Starting a new Project`_
* `Adding Symbols to Pattern Grid`_
* `Copy and Pasting a Selection`_
* `Un-doing/Re-doing Canvas Actions`_
* `Changing a Symbol's Background Color`_ 
* `Changing the Legend Layout`_
* `Adding Pattern Repeat Boxes`_
* `Adding Row Repeats`_
* `Inserting and Deleting Columns and Rows`_
* `Saving and Opening Sconcho Projects`_
* `Exporting and Printing Charts`_
* `Changing Chart Properties`_
* `Creating your own Custom Symbols`_


Starting a new Project
~~~~~~~~~~~~~~~~~~~~~~

At start-up, sconcho by default presents a pattern grid with 10 rows and
10 columns. This initial grid size can be easily changed by 

  * starting a new project (**File -> New**) and specifying the intended size in the *New Pattern Grid* dialog.

  * adding/removing the desired number of rows and columns (see `Inserting and Deleting Columns and Rows`_).


Adding Symbols to Pattern Grid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can create your chart by adding symbols to the pattern grid.
This is done via selecting grid cells by:

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
  is an active knitting symbol it will be placed into the selection if
  it fits.

What happens after you select grid cells depends on if you
currently have an active knitting symbol selected or not. Without an
active knitting symbol cells will turn gray and a knitting
symbol will be inserted into all currently selected cells once you pick one 
(assuming the symbol or multiples of it fit properly into the selection). 
If you already have an active knitting symbol selected it will be inserted 
immediately into your selection if it fits (e.g. a three stitch cable 
can not be added to a single selected cell; a multiple of three adjacent 
cells would have to be selected). Clicking on (or otherwise picking) 
already selected cells will un-select them again. You can deselect all
currently selected cells by going to **Tools -> Deselect All**.

The currently active knitting symbol can be selected from the list
of available categories and symbols on the right. 
The currently active symbol (including its background color) is shown
in the *Active Symbol Tool* above the canvas on the left. If no symbol is 
selected, the *Active Symbol Tool* displays **No Active Symbol**.

To simplify replacing or changing existing symbols on your chart you 
can select all pattern grid cells of a certain color or containing a
certain symbol in one swoop by right mouse clicking on a cell with 
the desired color/symbol and then choosing the proper option in the 
selector menu.


Copy and Pasting a Selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can copy and paste any selection on your chart. To copy, select a region
(make sure to disable the currently active symbol first) and then 
**Edit -> Copy**. Next, you can paste this selection into your chart. 
To do so either

  1) Select the region on the canvas you would like to paste into and then
  **Edit -> Paste**. This
  region has to have the same size and shape then (or a multiple of) the 
  originally copied selection. In the latter case, sconcho will paste the
  respective number of copies. E.g. if you paste a 3x4 block into a 6x12 
  selection you get 6 copies of your original. 

  2) Right click on the canvas and in the pop-up menu select 
  **Paste**. Sconcho will try to paste a single
  copy of your selection such that the cell you clicked on will become the 
  upper left hand corner. This may fail if there is not enough space 
  available to place the selection or
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

**Note:** The color of the no-stitch symbol can not be changed
from gray.


Changing the Legend Layout
~~~~~~~~~~~~~~~~~~~~~~~~~~

For each new (colored) symbol used, sconcho places a legend entry
consisting of a symbol and its description on the canvas. Both the symbol 
and the text can be moved separately anywhere on the canvas. 
The default description text for a symbol can be changed by clicking on 
the text box and editing it.

To move a legend symbol or text item hold down the **Control Key**
(the **Command Key** on Mac OSX) and **Left Mouse Click** on the
desired item. The cursor should change to a cross shape and
the item can now be moved via the mouse. 

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

**NOTE:** Pattern repeat boxes are not tied to the underlying 
pattern (after all, they can be moved). Thus, if you remove or
add columns/rows underneath a pattern repeat it will not re-size
automatically. Rather, you will have to delete the previous
pattern repeat and create a new one with the correct dimensions.


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


Inserting and Deleting Columns and Rows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deleting rows and columns is straightforward. First, select the rows 
or columns you would like to delete. Next, open up the 
**Row And Column Management Menu** by right mouse clicking anywhere
outside the actual chart area and then select "delete selected rows" 
or "delete selected columns". 

**NOTE:** Deletion of rows and columns is only possible
if complete rows or columns have been selected and these form 
rectangular regions (i.e. no multi-cell symbols are partially
sticking out).. 

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
location in the *Custom Symbols & Logging* tab of the *Preferences Dialog*.
If you change the location any existing custom symbols in the old location
will be lost until you copy them into the new location "by hand".

The currently selected custom symbol can be updated or deleted. Deletion is
only possible if the symbol does not appear in the currently worked on chart. 
Similarly, updating of a symbol currently in use is only possible if the 
name, svg name, and width remain the same. Otherwise, close your current 
session, open a blank document and delete/update then which is always 
possible. 

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




