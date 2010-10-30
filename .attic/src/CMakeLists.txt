INCLUDE( ${QT_USE_FILE} )

SET( SCONCHO_SRCS
     colorSelectorItem.cxx
     colorSelectorWidget.cxx
     graphicsScene.cxx
     gridDimensionDialog.cxx
     helperFunctions.cxx
     io.cxx
     knittingPatternItem.cxx
     knittingSymbol.cxx
     legendItem.cxx
     legendLabel.cxx
     mainWindow.cxx
     patternGridItem.cxx
     patternGridLabel.cxx
     patternGridRectangle.cxx
     patternGridRectangleDialog.cxx
     patternView.cxx
     preferencesDialog.cxx
     rowColDeleteInsertDialog.cxx
     sconcho.cxx
     settings.cxx
     symbolSelectorItem.cxx
     symbolSelectorWidget.cxx
   )

SET( SCONCHO_MOC_HDRS
     colorSelectorItem.h
     colorSelectorWidget.h
     graphicsScene.h
     gridDimensionDialog.h
     legendItem.h
     legendLabel.h
     mainWindow.h
     patternGridItem.h
     patternGridRectangle.h
     patternGridRectangleDialog.h
     patternView.h
     preferencesDialog.h
     rowColDeleteInsertDialog.h
     symbolSelectorItem.h
     symbolSelectorWidget.h
   )

SET ( SCONCHO_UI_FILES
      ui/rowColDeleteInsertDialog.ui
    )

SET( SCONCHO_ICONS
     icons.qrc
   )

QT4_WRAP_UI( SCONCHO_UIS ${SCONCHO_UI_FILES} )
QT4_WRAP_CPP( SCONCHO_MOCS ${SCONCHO_MOC_HDRS} )
QT4_ADD_RESOURCES( SCONCHO_SRCS ${SCONCHO_ICONS} )
ADD_EXECUTABLE( sconcho ${SCONCHO_SRCS} ${SCONCHO_MOCS} ${SCONCHO_UIS} )
TARGET_LINK_LIBRARIES( sconcho ${CMAKE_LD_FLAGS} ${QT_LIBRARIES} ${BOOST_LIBS} )

INSTALL( TARGETS sconcho RUNTIME DESTINATION bin/ )

