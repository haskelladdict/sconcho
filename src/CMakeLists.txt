INCLUDE(${QT_USE_FILE})

SET(SCONCHO_SRCS
  aboutSconcho.cxx
  graphicsScene.cxx
  gridDimensionDialog.cxx
  io.cxx
  knittingSymbol.cxx
  mainWindow.cxx
  patternGridItem.cxx
  patternGridLabel.cxx
  patternGridRectangle.cxx
  patternView.cxx
  preferencesDialog.cxx
  sconcho.cxx
  symbolSelectorItem.cxx
  symbolSelectorWidget.cxx
)

SET(SCONCHO_MOC_HDRS
  graphicsScene.h
  gridDimensionDialog.h
  mainWindow.h
  patternGridItem.h
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
TARGET_LINK_LIBRARIES(sconcho ${CMAKE_LD_FLAGS} ${STLPORT_LIBS} 
  ${QT_LIBRARIES} ${BOOST_LIBS}) 

