PROJECT(SCONCHO)

####################################################################
# check for cmake and establish linking policy
####################################################################
CMAKE_MINIMUM_REQUIRED(VERSION 2.6.0)

if(COMMAND cmake_policy)
  cmake_policy(SET CMP0003 NEW)
endif(COMMAND cmake_policy)


####################################################################
# check for QT4
####################################################################
FIND_PACKAGE(Qt4 COMPONENTS QtCore QtGui QtSvg REQUIRED)

####################################################################
# check for boost
####################################################################
INCLUDE(FindBoost)
IF(Boost_FOUND)
  MESSAGE(STATUS "boost found")
  SET(BOOST_LIBS boost_system)
ELSE(NOT BoostFound)
  MESSAGE(FATAL_ERROR "No boost install detected")
ENDIF(Boost_FOUND)


####################################################################
# add subdirs and enable testing 
####################################################################
SUBDIRS(src)

####################################################################
# set proper CFLAGS/LDFLAGS for release and regular builds 
# regular builds compile the unit test that can be run via
# make test
####################################################################

SET(CMAKE_LD_FLAGS "-Wl,-O1 -Wl,-z,now -Wl,-z,relro -Wl,--sort-common -Wl,--enable-new-dtags -Wl,--as-needed")

###################### Release build ###############################
IF(RELEASE)

SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -I./ -O2 -fomit-frame-pointer -march=native")

###################### regular build ###############################
ELSE(NOT RELEASE)
  SET(CMAKE_CXX_FLAGS "-I./ ${STLPORT_INCLUDES} -O0 -Wall -Wimplicit -Wreturn-type -Wswitch -Wcomment -Wparentheses -Wshadow -Wpointer-arith -Woverloaded-virtual -Wextra -Wfloat-equal -Winline -Wctor-dtor-privacy -Wnon-virtual-dtor -Wreorder -Wno-deprecated  -Wstrict-null-sentinel -Wno-non-template-friend  -Woverloaded-virtual -Wno-pmf-conversions -Wsign-promo -Wextra -pthread -g -ggdb -D_FILE_OFFSET_BITS=64 -D_STLP_DEBUG -DDEBUG")
ENDIF(RELEASE)


