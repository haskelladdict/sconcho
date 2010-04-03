INCLUDE(${QT_USE_FILE})

SET(SCONCHO_SRCS
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
  sconcho.cxx
  settings.cxx
  symbolSelectorItem.cxx
  symbolSelectorWidget.cxx
)

SET(SCONCHO_MOC_HDRS
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
  symbolSelectorItem.h
  symbolSelectorWidget.h
)

SET(SCONCHO_ICONS
  icons.qrc
)

QT4_WRAP_CPP(SCONCHO_MOCS ${SCONCHO_MOC_HDRS})
QT4_ADD_RESOURCES (SCONCHO_SRCS ${SCONCHO_ICONS})
ADD_EXECUTABLE(sconcho ${SCONCHO_SRCS} ${SCONCHO_MOCS} ) 
TARGET_LINK_LIBRARIES(sconcho ${CMAKE_LD_FLAGS} ${QT_LIBRARIES} ${BOOST_LIBS}) 

INSTALL(TARGETS sconcho RUNTIME DESTINATION bin/)

