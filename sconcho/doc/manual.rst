Sconcho Manual
--------------

*Author: Markus Dittrich (last change 09/10/2011)*

Sconcho is a tool for creating knitting charts. Charts can be created by placing
a variety of knitting symbols into a rectangular grids. Projects can be saved in
a platform independent format as sconcho project files (spf) and can be edited
at a later time. Charts can be exported in a variety of image formats and also
printed to a printer of saved in PDF or PostScript format.


**Contents of this manual**:

* `Starting a new Project`_
* `Interacting with Sconcho`_
* `Adding Symbols to Pattern Grid`_
* `Copy and Pasting a Selection`_
* `Un-doing/Re-doing Canvas Actions`_
* `Changing a Symbol's Background Color`_ 
* `Changing the Legend Layout`_
* `Adding Pattern Repeat Boxes`_
* `Inserting and Deleting Columns and Rows in the Chart`_
* `Saving and Opening Sconcho Projects`_
* `Exporting and Printing Charts`_
* `Changing the Label and Legend Properties`_
* `Creating your own Custom Symbols`_


Starting a new Project
~~~~~~~~~~~~~~~~~~~~~~

After start-up, sconcho by default presents a pattern grid with 10 rows and
10 columns. This initial grid size can be changed by either

  * starting a new project (**File -> New**) and specifying the proper size in the *New Pattern Grid* dialog.

  * adding the proper number of rows with the *Insert/Delete Rows and Columns* dialog (**Grid -> Insert/Delete Rows and Columns**).



Interacting with Sconcho
~~~~~~~~~~~~~~~~~~~~~~~~

Most interactions with sconcho only require a simple mouse click. This is
true for all selections, e.g. to choose the currently active knitting symbol 
or to place symbols into the existing pattern grid.

There are a number of additional ways to select cells on the pattern grid and
these all involve holding down the **Shift key** while using the mouse:

* Shift + mouse click and then dragging the mouse across the pattern grid will 
  activate the *Rubberband Tool*. Upon releasing the mouse button all grid cells 
  under the rubberband will either be selected or unselected based on their 
  previous state. If there is a knitting symbol active it will be placed 
  immediately if it fits into the selection area.

* Shift + right click on either a row or column label will again select or
  un-select the whole row or column based on its previous state. If there is an
  active knitting symbol it will be placed.

Finally, several items on the canvas can be moved around. Movable items are: 
legend items (both symbols and text) and repeat boxes on the canvas. In order
to move items, hold down the **Control key** then click on the item with the
mouse button and start dragging. Releasing the mouse button causes the item
to be placed at the location of the mouse cursor.


Adding Symbols to Pattern Grid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Symbols are added to the pattern grid via selecting grid cells. These
cells will then be filled with the currently active knitting symbol from
the list of available knitting symbols. 

The presently active symbol (including its background color) is indicated 
in the *Active Symbol Tool* in the lower right hand corner. If no symbol is 
selected the *Active Symbol Tool* displays **No Active Symbol**.

Grid cells can be selected in three ways:

  1) individual grid cells can be selected by using the right mouse button to click on them
  2) complete rows or columns can be selected by holding down the **Control** key and clicking on the row or column labels. If the label spacing is larger than one, Control-clicking in empty row/column label positions will also select whole rows/columns.
  3) a rectangular area can be selected with the *Rubberband Tool* by holding down the **Shift** key and the right mouse button and then dragging the mouse.

Without an active symbol (the *Active Symbol Tool*
shows **No Active Symbol**) selecting grid cells will highlight
them in a light gray color. As soon as a symbol is activated it
will be inserted into the highlighted grid cells. If a 
symbol is already active while selecting grid cells, the symbol will be 
inserted into the highlighted cells immediately. 

**Note:** If a symbol is active which spans more than a single
cell - a 3 stitch cable for example -- it will only
be inserted if the selected grid cells can fit the symbols 
exactly (there could be more than one if the *Rubberband Tool* is
used).


Copy and Pasting a Selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The currently selected cells can be copied via
**Right Mouse Click -> Copy Selection**. The cells copied in this fashion
can then then be pasted via **Right Mouse Click -> Paste Selection** as 
often as needed.
Pasting will insert the most recently copied rectangular selection such 
that the grid cell under the mouse pointer ends up at the upper left 
hand corner. When pasting, the target area has to fit the copied selection 
exactly, i.e., pasting can not leave cells half filled. If pasting is not
possible at the requested location, the *Paste Selection* option is grayed out.
This can only happen when attempting to paste into areas with symbols wider 
than a single cell (e.g. 2, 3, 4, 5, or 6 stitch cables).

**Note:** Presently, only rectangular selections can be copied and pasted. 
If the current selection is not rectangular or consists of multiple disconnected
pieces it can not be copied and the *Copy Selection* option is grayed out.



Un-doing/Re-doing Canvas Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sconcho allows unlimited undo and redo of all canvas actions,
including adding symbols, copy & paste, deleting/inserting rows and columns, 
changing colors, and moving and editing legend items.


Changing a Symbol's Background Color
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With the exception of the **no-stitch** symbol, the default background of
all symbols is *white*. The color of the active symbol can be changed
by choosing one of the predefined colors in the *Color Selector Tool*.
The currently selected color is indicated in the *Active Symbol Tool*.
The color in each of the predefined color selectors can be customized by 
clicking on the *Customize Color* button and changing the color.
In addition, one can also load a color from any grid cell into the 
currently active color selector by grabbing the color via 
**Right Mouse Click -> Grab Color**.



Changing the Legend Layout
~~~~~~~~~~~~~~~~~~~~~~~~~~

For each new symbol and color used, sconcho places a legend entry
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
be the outline of the selected cells) and then click on
**View -> Create Pattern Repeat** to create it. To change the color and
line thickness of an existing repeat box or to delete a box move the mouse
over the pattern repeat box, right click and select **Edit Pattern Repeat**
to make visible a dialog for changing the box's properties.

To move a pattern repeat box hold down the **Control Key**
(the **Command Key** on Mac OSX) and **Left Mouse Click** on the
desired item. The cursor should change to a cross shape and the
repeat box can now be moved.


Inserting and Deleting Columns and Rows in the Chart
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additional rows and columns can be inserted into and deleted from an 
already existing chart using the *Insert/Delete Rows and Columns* dialog 
(**Grid -> Insert/Delete Rows and Columns**). Here, it is important to keep 
in mind that while it is always possible to add and remove rows, columns can 
be added only if the new row does not appear within an already existing 
multi-cell symbol. Similarly, a column can be removed only if it is not 
part of a multi-cell symbol.



Saving and Opening Sconcho Projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sconcho projects can be saved in a platform independent binary 
format called *sconcho project format (SPF)*. SPF files typically end
with the extension .spf. SPF files can then be re-opened in sconcho.



Exporting and Printing Charts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can either print your sconcho project on a printer (or print
to a PDF file on some platforms), export it as a bitmapped image
file, or save it as an svg image. The available image file formats 
depend on the operating system. Click on the *Browse* button to
see all available formats. Exported images can also be scaled. 

To enable the generation of non-rectangular image files, sconcho can 
hide all *nostitch* symbols in the exported image of your pattern.
Check *Hide Nostitch Symbols* in the export dialog to select this.



Changing the Label and Legend Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The font and size of the labels or the legend can be changed independently in 
the preferences dialog (**File -> Preferences**). Furthermore the preferences
dialog allows one to select the *interval i* with which the labels are displayed.
By default, *i* is set to 1. Both the label and legend font, size as well as label 
interval are saved in sconcho project files and will be restored upon loading a
previously saved project.


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

1. You need to restart sconcho to make newly added symbols appear in the list of available symbols. 
2. If you choose a symbol name and category identical to one provided by default with sconcho, your custom symbol will take precedence.
3. Sconcho does not provide a facility for creating the SVG images needed for a new symbol. You can use the excellent program Inkscape <http://inkscape.org/> for this purpose. Inkscape was also used to create the symbols that come with sconcho.

By default, your new symbols are stored within your home directory 
(*C:/Documents and Settings/Username* on Windows). You can change the location 
in the *Symbol Location* tab of the *Preferences* Dialog.

By pressing the *Update Selected Symbol* button you can update the information
for the currently highlighted symbol in the list of *Available Symbols*.
Updates take effect immediately.

Finally, pressing *Delete Selected Symbol* will delete the currently highlighted
symbol. 

**Please Note:**:

If you delete a symbol any previously saved sconcho projects which include
this symbol will cease to load properly. Thus, please think twice before 
removing a symbol.




