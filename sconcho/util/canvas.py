# -*- coding: utf-8 -*-
########################################################################
#
# (c) 2009-2012 Markus Dittrich
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License Version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License Version 3 for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free
# Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#
#######################################################################

import logging
import math

from sys import (maxsize, 
                 float_info)

from copy import copy

from PyQt4.QtCore import (QPointF, 
                          QRectF)

from PyQt4.QtGui import (QColor,
                         QMessageBox)

import sconcho.util.messages as msg


# module lever logger:
logger = logging.getLogger(__name__)


# constants determining the interacion mode with
# the canvas
SELECTION_MODE = 0
HIDE_MODE = 1
UNHIDE_MODE = 2

# opacity used for hiding cells
HIDE_OPACITY = 0.05


def convert_pos_to_col_row(mousePos, cellWidth, cellHeight):
    """ Converts a mouse position on the canvas into a tuple
    of (column, row).
    Note: This may be outside the actual pattern grid.

    """

    column = int( math.floor( mousePos.x()/cellWidth ) )
    row    = int( math.floor( mousePos.y()/cellHeight ) )

    return (column, row)



def convert_col_row_to_pos(column, row, cellWidth, cellHeight):
    """ Converts a (row, column) tuple to a position on
    the canvas in the center of the corresponding grid element.

    """

    return QPointF((column + 0.5) * cellWidth,
                   (row + 0.5) * cellHeight)



def is_click_in_grid(col, row, numCols, numRows):
    """ Returns true if col and row is within the limits
    set by numCol and numRow.

    """

    if ( col >= 0 and col < numCols ) and ( row >= 0 and row < numRows ):
        return True
    else:
        return False



def is_click_on_labels(col, row, numCols, numRows):
    """ Returns true if col and row is within the grid labels.

    NOTE: We accept both clicks on the right/left or top/bottom
    of the grid.
    """

    #if (((col == numCols or col == -1) and (row >= 0 and row < numRows)) or
    #    ((row == -1 or row == numRows) and (col >= 0 and col < numCols))):
    if ((col == numCols and (row >= 0 and row < numRows)) or
        (row == numRows and (col >= 0 and col < numCols))):

        return True
    else:
        return False



def shift_item_row_wise(item, num, unitCellHeight):
    """ Shifts the given item by num rows given unitCellHeight. """

    yShift = num * unitCellHeight
    item.prepareGeometryChange()
    item.row += num
    item.setPos(item.pos() + QPointF(0.0, yShift))



def shift_item_column_wise(item, num, unitCellWidth):
    """ Shifts the given item by num columns given unitCellWidth. """

    xShift = num * unitCellWidth
    item.prepareGeometryChange()
    item.column += num
    item.setPos(item.pos() + QPointF(xShift, 0.0))



def shift_legend_vertically(legendList, rowShift, unitCellHeight,
                            numColumns, unitWidth):
    """ Shift all legend items below the grid down by rowShift. """

    yShift = rowShift * unitCellHeight

    for item in legendList:
        symbol = legendItem_symbol(item)
        text   = legendItem_text(item)

        # we ignore all items above or right of the pattern grid
        if (symbol.scenePos().y() >= 0) and \
           (symbol.scenePos().x() <= numColumns * unitWidth):

            symbol.prepareGeometryChange()
            symbol.setPos(symbol.pos() + QPointF(0.0, yShift))


        if (text.scenePos().y() >= 0) and \
           (text.scenePos().x() <= numColumns * unitWidth):

            text.prepareGeometryChange()
            text.setPos(text.pos() + QPointF(0.0, yShift))



def shift_selection_vertically(selection, pivot, rowShift):
        """ Shifts all items in the current selection that are below the
        pivot down.

        """

        newSelection = {}
        for (key, entry) in selection.items():

            if entry.row >= pivot:
                entry.row += rowShift

            newID = get_item_id(entry.column, entry.row)
            newSelection[newID] = entry

        return newSelection



def shift_legend_horizontally(legendList, columnShift, unitCellWidth,
                              numRows, unitHeight):
    """ Shift all legend items to the right of the grid right by
    columnShift.

    """

    xShift = columnShift * unitCellWidth

    for item in legendList:
        symbol = legendItem_symbol(item)
        text = legendItem_text(item)

        # we ignore all items above or right of the
        # pattern grid
        if (symbol.scenePos().x() >= 0) and \
           (symbol.scenePos().y() >= 0) and \
           (symbol.scenePos().y() <= numRows * unitHeight):

            symbol.prepareGeometryChange()
            symbol.setPos(symbol.pos() + QPointF(xShift, 0.0))


        if (text.scenePos().x() >= 0) and \
           (text.scenePos().y() >= 0) and \
           (text.scenePos().y() <= numRows * unitHeight):

            text.prepareGeometryChange()
            text.setPos(text.pos() + QPointF(xShift, 0.0))



def shift_row_labels(rowLabels, pivot, rowShift):
    """ Shifts the row labels in the rowLabels dictionary
    according to the pivot point and shift given by rowShift.

    """

    newLabels = {}
    for (key, item) in rowLabels.items():
        if key >= pivot:
            newLabels[key+rowShift] = item
        else:
            newLabels[key] = item

    return newLabels



def shift_column_labels(columnLabels, pivot, columnShift):
    """ Shifts the column labels in the columnLabels dictionary
    according to the pivot point and shift given by columnShift.

    """

    newLabels = {}
    for (key, item) in columnLabels.items():
        if key > pivot-1:
            newLabels[key+columnShift] = item
        else:
            newLabels[key] = item

    #for (key, item) in newLabels.items():
    #    print(key, item.toPlainText())
    
    return newLabels



def shift_selection_horizontally(selection, pivot, columnShift):
        """ Shifts all items in the current selection that are right
        of the pivot to the right.

        """

        newSelection = {}
        for (key, entry) in selection.items():

            if entry.column >= pivot:
                entry.column += columnShift

            newID = get_item_id(entry.column, entry.row)
            newSelection[newID] = entry

        return newSelection



def compute_max_legend_y_coordinate(gridLegend, repeatLegend):
    """ Given the current list of existing legend items
    figure out the largest y coordinate among them all.

    """

    yList = [0]
    for item in gridLegend.values():
        yList.append(legendItem_symbol(item).scenePos().y())
        yList.append(legendItem_text(item).scenePos().y())

    for item in repeatLegend.values():
        yList.append(legendItem_symbol(item).scenePos().y())
        yList.append(legendItem_text(item).scenePos().y())

    return max(yList)



def change_count(item, count):
    """ Convenience wrapper changing the count for a particular
    legend entry.

    """

    item[0] += count
    return item



def legendItem_count(item):
    """ Convenience wrapper returning the reference count for the
    particular legend item.

    """

    return item[0]



def legendItem_symbol(item):
    """ Convenience wrapper returning the current symbol for a
    particular legend item.

    """

    return item[1]



def legendItem_text(item):
    """ Convenience wrapper returning the current description text
    for a particular legend item.

    """

    return item[2]



def generate_legend_id(symbol, color):
    """ Based on a symbol/legend info, generate an id tag. Currently
    this is just based on name and category.

    """

    name = symbol["name"]
    category = symbol["category"]

    return (name, color.name())



def arrange_label_item(legendItems, legendID, itemXPos, itemYPos, labelXPos,
                       labelYPos, description):
    """ Position all label items (pairs of PatternGridItem
    and PatternLegendItem) as requested in dict legendItems
    which comes from a parsed spf file.

    """

    if legendID in legendItems:

        legendItem = legendItems[legendID]
        legendPatternItem = legendItem_symbol(legendItem)
        legendTextItem = legendItem_text(legendItem)
        legendPatternItem.setPos(itemXPos, itemYPos)
        legendTextItem.setPos(labelXPos, labelYPos)
        legendTextItem.setPlainText(description)

    else:
        QMessageBox.critical(None, msg.errorMatchingLegendItemTitle,
                             msg.errorMatchingLegendItemText,
                             QMessageBox.Close)
        logger.error(msg.errorMatchingLegendItemText)


def get_upper_left_hand_corner(selectedCells):
    """ Returns the column and row of the upper left hand corner
    of selection.

    """

    if not selectedCells:
        return (None, None, None)

    cellsByRow = order_selection_by_rows(selectedCells)
    minRow = min(cellsByRow.keys())

    minCol = maxsize
    for item in cellsByRow[minRow]:
        if item.column < minCol:
            minCol = item.column

    return (minRow, minCol, cellsByRow)



def get_leftmost_column(selectedCells):
    """ Returns the leftmost columns in the provided list of cells """

    if not selectedCells:
        return None

    cells = list(selectedCells)
    cells.sort(key=(lambda x: x.column))

    return cells[0].column



def match_selections(copySelection, pasteSelection):
    """ This function checks if two selection match, i.e.,
    overlay exactly.

    """

    invalid = (None, None, None, None, None)

    (minCopyRow, minCopyCol, copyCellsByRow) = \
            get_upper_left_hand_corner(copySelection.values())
    (minPasteRow, minPasteCol, pasteCellsByRow) = \
            get_upper_left_hand_corner(pasteSelection.values())
    leftmostCopyCol = get_leftmost_column(copySelection.values())
    leftmostPasteCol = get_leftmost_column(pasteSelection.values())

    copyRows = copyCellsByRow.keys()
    copyRows.sort()
    pasteRows = pasteCellsByRow.keys()
    pasteRows.sort()

    if len(copyRows) != len(pasteRows):
            return invalid

    deadItems = set()
    while len(copyRows) > 0:
        copyRow = copyRows.pop(0)
        copyRowItems = copyCellsByRow[copyRow]
        copyRowItems.sort(key=(lambda x: x.column))
        copyLength = copyRowItems[-1].column + copyRowItems[-1].width \
                - leftmostCopyCol

        pasteRow = pasteRows.pop(0)
        pasteRowItems = pasteCellsByRow[pasteRow]
        pasteRowItems.sort(key=(lambda x: x.column))
        pasteLength = pasteRowItems[-1].column + pasteRowItems[-1].width \
                - leftmostPasteCol

        if (copyLength != pasteLength):
            return invalid

        # create bitmap and compare
        offset = leftmostPasteCol - leftmostCopyCol
        bitmap = [0]*copyLength
        for item in copyRowItems:
            for i in range(item.column, item.column + item.width):
                bitmap[i-leftmostCopyCol] = 1

        for item in pasteRowItems:
            for i in range(item.column, item.column + item.width):
                if bitmap[i-leftmostPasteCol] == 0:
                    return invalid
            deadItems.add(item)

    # all good - assemble dead items now
    deadSelection = {}
    for item in deadItems:
        itemID = get_item_id(item.column, item.row)
        deadSelection[itemID] = PatternCanvasEntry(item.column,
                                                    item.row,
                                                    item.width,
                                                    item.color,
                                                    item.symbol,
                                                    item.isHidden)
    return (minCopyCol, minCopyRow, minPasteCol, minPasteRow,
            deadSelection)



def is_selection_rectangular(selectedCells):
    """ This function checks if the provided selection
    is rectangular (i.e., not jagged or disconnected).
    The function returns (True, (col, row)) if yes and (False, (0,0))
    otherwise. Here, col and row and the number of columns and rows
    of the selected rectangle.

    """

    if not selectedCells:
        return (False, (0,0))

    cellsByRow = order_selection_by_rows(selectedCells)

    # make sure the rows are consecutive
    rowIDs = list(cellsByRow.keys())
    rowIDs.sort()
    for item in range(1, len(rowIDs)):
        if (rowIDs[item] - rowIDs[item-1]) != 1:
            return(False, (0,0))

    # check that each row has the same number of unit cells
    values = set(num_unitcells(row) for row in cellsByRow.values())
    if len(values) != 1:
        return (False, (0,0))

    # look for "holes"
    for row in cellsByRow.values():
        row.sort(key=(lambda x: x.column))
        if not are_consecutive([row]):
            return (False, (0,0))

    numCols = values.pop()
    numRows = len(cellsByRow)

    # should never happen
    assert(numCols != 0)
    assert(numRows != 0)

    return (True, (numCols, numRows))



def get_marked_rows(selectedCells, numColumns):
    """ Returns a list of selected rows. 

    Each row that has at least a single cell selected
    will be selected.

    Returns a list of selected rows if nothing else
    is selected and otherwise an empty list.

    """

    if selectedCells:
        cellsByRow = order_selection_by_rows(selectedCells)
        values = set(num_unitcells(row) for row in cellsByRow.values())
        return list(cellsByRow.keys())

    return []



def get_marked_columns(selectedCells, numRows):
    """ Returns a list of selected columns.

    Each column that has at least a single cell selected
    will be selected.

    Returns a list of selected columns if nothing else
    is selected and otherwise an empty list.

    """

    if selectedCells:
        cellsByColumn = {}
        for cell in selectedCells:
            for col in range(cell.column, cell.column + cell.width):
                if not col in cellsByColumn:
                    cellsByColumn[col] = [cell]
                else:
                    cellsByColumn[col].append(cell)

        entries = dict([(colID, len(cols)) for (colID, cols) 
                        in cellsByColumn.items()])

        # all columns are of lenght numRows - good to go
        return list(cellsByColumn.keys())

    return []



def can_outline_selection(selection):
    """ This function determines if the currently action selection
    can be outlined. This requires the selection to be connected
    without any holes.

    """

    if len(selection) == 0:
        return False

    # check that rows are consecutive
    cellsByRow = order_selection_by_rows(selection)
    keys = list(cellsByRow.keys())
    keys.sort()
    differences = set([(j-i) for (i,j) in zip(keys, keys[1:])])
    if len(differences) > 1:
        return False
    elif len(differences) == 1 and (1 not in differences):
        return False

    # check that each row has no holes
    for row in cellsByRow.values():
        row.sort(key=(lambda x: x.column))
        if not are_consecutive([row]):
            return False

    return True



def order_selection_by_rows(selection):
    """ Given a list of selected grid cells order them by row. """

    cellsByRow = {}
    if selection:
        for cell in selection:
            if not cell.row in cellsByRow:
                cellsByRow[cell.row] = [cell]
            else:
                cellsByRow[cell.row].append(cell)

    return cellsByRow



def order_selection_by_columns(selection):
    """ Given a list of selected grid cells order them by column. """

    cellsByColumn = {}
    if selection:
        for cell in selection:
            if not cell.column in cellsByColumn:
                cellsByColumn[cell.column] = [cell]
            else:
                cellsByColumn[cell.column].append(cell)

    return cellsByColumn



def chunkify_cell_arrangement(width, allCellsDict):
    """ Given a collection of selected cells verifies that we
    can place a symbol of given width. If so, return a
    list of consecutive chunks of cells all of a multiple of width
    that can be filled with the new symbol.

    """

    allCells = allCellsDict.values()

    # check 1: number of active cells has to be a multiple
    # of width
    if num_unitcells(allCells) % width != 0:
        return []

    cellsByRow = order_selection_by_rows(allCells)

    # check 2: each row has to be a multiple of width
    for row in cellsByRow.values():
        if num_unitcells(row) % width != 0:
            return []

    chunkList = chunk_all_rows(width, cellsByRow)

    return chunkList



def chunk_all_rows(width, cellsByRow):
    """ Separate each row into chunks at least as long as
    the items we want to place. Then we check if each
    chunk is consecutive.

    """

    chunkList = []
    for row in cellsByRow.values():
        row.sort(key=(lambda x: x.column))

        chunks = []
        chunk = []
        length = 0
        for entry in row:
            chunk.append(entry)
            length += entry.width
            if length % width == 0:
               chunks.append(chunk)
               chunk = []
               length = 0

        if not are_consecutive(chunks):
            return []

        chunkList.extend(chunks)

    return chunkList



def are_consecutive(chunks):
    """ Checks if each chunk in a list of chunks consists
    of consecutive items.

    """

    if not chunks:
        return True

    for chunk in chunks:
        if not chunk:
            return False

        consecutiveCol = chunk[0].column + chunk[0].width
        for cell in chunk[1:]:
            if cell.column != consecutiveCol:
                return False

            consecutiveCol = cell.column + cell.width

    return True



def num_unitcells(cells):
    """ Compute the total number of unit cells in the
    selection.

    """

    totalWidth = 0
    for item in cells:
        totalWidth += item.width

    return totalWidth



def get_item_id(column, row):
    """ Returns an items id based on its row and column location. """

    return str(column) + ":" + str(row)



def get_edge_id(gridPoint1, gridPoint2):
    """ Given the column and row values of two grid points
    return a string ID.

    NOTE: Each cell has 4 grid points. The upper left hand
    corner corresponds to the row/column id of the cell.
    The other corners each add +1 for row and/or column id.
    E.g. lower right hand corner has an id of (row + 1, column + 1).

    """

    return ":".join(map(str, gridPoint1 + gridPoint2))



def get_row_repeat_id(entry):
    """ Returns the pattern repeat id of a patter row repeat. """

    return entry[2]




def load_pattern_grid_items(patternGridItemInfo, knittingSymbols,
                            unitCellWidth, unitCellHeight):
    """ extract all patternGridItems from a loaded sconcho project. """

    allPatternGridItems = []
    try:
        for newItem in patternGridItemInfo:
            colID    = newItem["column"]
            rowID    = newItem["row"]
            width    = newItem["width"]
            height   = newItem["height"]
            name     = newItem["name"]
            color    = QColor(newItem["color"])
            isHidden = newItem["isHidden"]
            category = newItem["category"]
            location = QPointF(colID * unitCellWidth, rowID * unitCellHeight)
            symbol   = knittingSymbols[name]

            #if name == "nostitch":
            #    color = QColor("#6a6a6a")
            allPatternGridItems.append((location, colID, rowID, width, height,
                                        symbol, color, isHidden))

    except KeyError as e:
        logger.error(msg.errorLoadingGridText % e)
        QMessageBox.critical(None, msg.errorLoadingGridTitle,
                             msg.errorLoadingGridText % e,
                             QMessageBox.Close)
        return None

    return allPatternGridItems



def  extract_num_rows_columns(allPatternGridItems):
    """ From a list of new PatternGridItems extract the number of rows and
    columns.
    """

    numColumns = max([x[1] for x in allPatternGridItems]) + 1
    numRows = max([x[2] for x in allPatternGridItems]) + 1

    return (numRows, numColumns)



def load_legend_items(legendItemInfo):
    """ extract all legend items from a loaded sconcho project. """

    allLegendItems = []
    try:
        for item in legendItemInfo:
            legendID  = generate_legend_id(item, item["color"])
            itemXPos  = item["itemXPos"]
            itemYPos  = item["itemYPos"]
            labelXPos = item["labelXPos"]
            labelYPos = item["labelYPos"]
            description = item["description"]
            allLegendItems.append((legendID, itemXPos, itemYPos,
                                   labelXPos, labelYPos, description))
    except KeyError as e:
        logger.error(msg.errorLoadingLegendText % e)
        QMessageBox.critical(None, msg.errorLoadingLegendTitle,
                             msg.errorLoadingLegendText % e,
                             QMessageBox.Close)
        return None

    return allLegendItems



def load_patternRepeat_items(repeatItemInfo):
    """ extract all pattern repeat items from a loaded sconcho project. """

    allPatternRepeatItems = {}
    try:
        for item in repeatItemInfo:
            itemID = item["legendID"]
            itemPolygonInfo = item["polygon"]
            itemLineWidth = item["width"]
            itemPosition = item["position"]
            itemColor = item["color"]
            allPatternRepeatItems[itemID] = ((itemPolygonInfo, itemLineWidth,
                                              itemPosition, itemColor))
    except KeyError as e:
        logger.error(msg.errorLoadingRepeatBoxText % e)
        QMessageBox.critical(None, msg.errorLoadingRepeatBoxTitle,
                             msg.errorLoadingRepeatBoxText % e,
                             QMessageBox.Close)
        return None

    return allPatternRepeatItems



def load_patternRepeatLegend_items(repeatLegendInfo):
    """ extract all pattern repeat item legends from a loaded sconcho
    project. """

    allPatternRepeatLegendItems = {}
    try:
        for (key, item) in repeatLegendInfo.items():
            itemIsVisible = item["isVisible"]
            itemPosition = item["itemPos"]
            textItemPosition = item["textItemPos"]
            itemText = item["itemText"]
            allPatternRepeatLegendItems[key] = ((itemIsVisible,
                                                 itemPosition,
                                                 textItemPosition,
                                                 itemText))
    except KeyError as e:
        logger.error(msg.errorLoadingRepeatBoxLegendText % e)
        QMessageBox.critical(None, msg.errorLoadingRepeatBoxLegendTitle,
                             msg.errorLoadingRepeatBoxLegendText % e,
                             QMessageBox.Close)
        return None

    return allPatternRepeatLegendItems




def load_text_items(textItemInfo):
    """ extract all canvas text items from a loaded sconcho project. """

    allTextItems = []
    try:
        for item in textItemInfo:
            itemPosition = item["itemPos"]
            itemText = item["itemText"]
            allTextItems.append((itemPosition, itemText))

    except KeyError as e:
        logger.error(msg.errorLoadingTextItemsText % e)
        QMessageBox.critical(None, msg.errorLoadingTextItemsTitle,
                             msg.errorLoadingTextItemsText % e,
                             QMessageBox.Close)
        return None

    return allTextItems



def visible_bounding_rect(items):
    """ Returns the bounding rectangle of all visible items. """

    # initialize with
    min_x = float_info.max
    min_y = float_info.max
    max_x = -float_info.max
    max_y = -float_info.max

    for item in items:
        if item.isVisible():
            itemBounds = item.boundingRect()
            itemTopLeft = item.mapToScene(itemBounds.topLeft())
            itemBottomRight = item.mapToScene(itemBounds.bottomRight())

            if (itemTopLeft.x() < min_x):
                min_x = itemTopLeft.x()

            if (itemTopLeft.y() < min_y):
                min_y = itemTopLeft.y()

            if (itemBottomRight.x() > max_x):
                max_x = itemBottomRight.x()

            if (itemBottomRight.y() > max_y):
                max_y = itemBottomRight.y()

    margin = 10
    rect = QRectF(QPointF(min_x, min_y), QPointF(max_x, max_y))
    rect.adjust(-margin, -margin, margin, margin)
    return rect



def repeats_to_be_shifted_after_insert_row(repeats, cellHeight,
                                           pivot, numRows):
    """ Determine all pattern repeats that need to be
    shifted after insertion of rows.

    We don't do anything if rows are inserted within the
    pattern repeat.

    """

    patternItems = []
    for item in repeats:
        if (item.canvas_pos().y()/cellHeight < pivot):
            continue

        oldPos = item.pos()
        newPos = item.pos() + QPointF(0.0, numRows*cellHeight)
        patternItems.append((item, oldPos, newPos))

    return patternItems



def repeats_to_be_shifted_after_delete_rows(repeats, cellHeight,
                                            deadRows):
    """ Determine all pattern repeats that need to be
    shifted after deletion of rows.

    We don't do anything if rows are deleted within the
    pattern repeat.

    """

    patternItems = []
    for item in repeats:
        shift = 0
        for row in deadRows:
            if (item.canvas_pos().y()/cellHeight > row):
                shift += 1

        # a row within the patter repeat was remove - do nothing
        if shift == 0:
            continue

        oldPos = item.pos()
        newPos = item.pos() - QPointF(0.0, shift * cellHeight)
        patternItems.append((item, oldPos, newPos))

    return patternItems



def repeats_to_be_shifted_after_insert_col(repeats, cellWidth,
                                           pivot, numCols):
    """ Determine all pattern repeats that need to be
    shifted after insertion of columns.

    We don't do anything if columns are inserted within the
    pattern repeat.

    """

    patternItems = []
    for item in repeats:
        if (item.canvas_pos().x()/cellWidth < pivot):
            continue

        oldPos = item.pos()
        newPos = item.pos() + QPointF(numCols * cellWidth, 0.0)
        patternItems.append((item, oldPos, newPos))

    return patternItems



def repeats_to_be_shifted_after_delete_cols(repeats, cellWidth,
                                            deadCols):
    """ Determine all pattern repeats that need to be
    shifted after deletion of columns.

    We don't do anything if column sare deleted within the
    pattern repeat.

    """

    patternItems = []
    for item in repeats:
        shift = 0
        for col in deadCols:
            if (item.canvas_pos().x()/cellWidth > col):
                shift += 1

        # a row within the patter repeat was remove - do nothing
        if shift == 0:
            continue

        oldPos = item.pos()
        newPos = item.pos() - QPointF(shift * cellWidth, 0.0)
        patternItems.append((item, oldPos, newPos))

    return patternItems



def sort_vertices(segments):
    """ Sorts the line segments corresponding to a pattern
    repeat into a consecutive set of points describing
    the outline of the repeat.

    The list of segments is in the form
    [(point1, point2), (point3, point4), ....]
    where is point is an (x,y) tuple.

    NOTE 0: line vertices assumes that the are described
    by line vertices has not hole and is singly 
    connected.

    NOTE 1: If there is a problem sorting, e.g., if we're
    past a bunch of segments corresponding to an area with
    a whole we abort and return None

    """

    # find the beginning of outline
    minKey = get_min(segments)
    vertices = [minKey] 

    current = minKey
    while len(segments) > 0:

        # if get_segment returns None the most likely
        # was a hole in the are of the repeat and
        # we abort
        seg = get_segment(segments, current)
        if not seg:
            return None
        
        if seg[0] == current:
            vertices.append(seg[1])
            current = seg[1]
        else:
            vertices.append(seg[0])
            current = seg[0]
           
        segments.remove(seg)

    return vertices



def get_segment(segments, targetPoint):
    """ Given a list of segments and a target point
    picks the segment that contains the point.

    NOTE: this function will pick the first point
    it finds and None if nothing is returned.

    """

    for seg in segments:
        if (seg[0] == targetPoint):
            return seg
        elif (seg[1] == targetPoint):
            return seg

    return None



def get_min(segments):
    """ Given a list of segments return the smallest point
    in all segments.

    """

    if len(segments) == 0:
        return None

    currentMin = segments[0][0];
    for seg in segments:
        if seg[0] < currentMin:
            currentMin = seg[0]

        if seg[1] < currentMin:
            currentMin = seg[1]

    return currentMin



def extract_patternItems(allItems, patternType):
    """ From a list of QGraphicsItems extracts and returns
    all PatternGridItems.

    """

    patternItems = []
    for item in allItems:
        if isinstance(item, patternType):
            patternItems.append(item)

    return patternItems



def add_to_hidden_cells_tracker(tracker, item):
    """ Add the hidden item to the canvas' hidden cell tracker. """ 

    if item.row in tracker:
        tracker[item.row].update(\
                set(range(item.column, item.column+item.width)))
    else:
        newSet = set()
        newSet.update(set(range(item.column, item.column+item.width)))
        tracker[item.row] = newSet



def delete_from_hidden_cells_tracker(tracker, item):
    """ Add the hidden item to the canvas' hidden cell tracker. """ 

    if item.row in tracker:
        tracker[item.row].difference_update(\
            set(range(item.column, item.column+item.width)))



def column_delete_shift_hidden_cell_tracker(tracker, pivot, shift):
    """ Shift the tracked columns by shift around pivot and remove
    deleted columns if required.

    This function is used when deleting columns to
    make sure the tracker is properly synced with the current layout.
    
    """

    for (row, values) in tracker.items():
        newSet = set()
        for item in values:
            if item in range(pivot, pivot+shift):
                continue
            elif item >= pivot+shift:
                newSet.add(item - shift)
            else:
                newSet.add(item)
        tracker[row] = newSet



def column_insert_shift_hidden_cell_tracker(tracker, pivot, shift):
    """ Shift the tracked columns by shift around pivot and insert 
    columns if required.

    This function is used when inserting columns to ensure
    the tracker is properly synced with the current layout.
    
    """

    for (row, values) in tracker.items():
        newSet = set()
        for item in values:
            if item >= pivot:
                newSet.add(item + shift)
            else:
                newSet.add(item)
        tracker[row] = newSet



def row_delete_shift_hidden_cell_tracker(tracker, pivot, shift):
    """ Shift the tracked rows by shift around pivot and remove
    deleted rows if required.

    This function is used when deleting rows to ensure
    the tracker is properly synced with the current layout.

    NOTE: We don't want to mutate the hidden cell tracker
    so we create a new one and return it.
    
    """

    newTracker = {}
    for (row, value) in tracker.items():
        if row in range(pivot, pivot+shift):
            continue
        elif row >= pivot+shift:
            newTracker[row-shift] = value
        else:
            newTracker[row] = value
    
    return newTracker



def row_insert_shift_hidden_cell_tracker(tracker, pivot, shift):
    """ Shift the tracked rows by shift around pivot.

    This function is used when inserting rows to ensure
    the tracker is properly synced with the current layout.

    NOTE: We don't want to mutate the hidden cell tracker
    so we create a new one and return it.
    
    """

    newTracker = {}
    for (row, value) in tracker.items():
        if row >= pivot:
            newTracker[row+shift] = value
        else:
            newTracker[row] = value
    
    return newTracker




############################################################################
#
# Helper Classes
#
############################################################################
class PatternCanvasEntry(object):
    """ This is a small helper class for storing all relevant information
    to track a PatternGridItem.

    """

    def __init__(self,  column, row, width, color, symbol, hidden=False):

        self.column = column
        self.row    = row
        self.width  = width
        self.color  = color
        self.symbol = symbol
        self.isHidden = hidden
