#!/bin/sh

RDKIT_PKG="$1"
PYTHON_PREFIX=$( dirname $( dirname $( which python ) ) )
DESTINATION=$PYTHON_PREFIX/local/rdkit
PYTHON_LIB=`ls $PYTHON_PREFIX/lib/lib*.so | xargs basename`

RDKIT_DIR=`basename $RDKIT_PKG .tar.gz`

tar -xzvf $RDKIT_PACKAGE
cd $RDKIT_DIR
RDKIT_SRC=`pwd`

RDBASE=$PYTHON_PREFIX/local/rdkit
mkdir -pv $RDBASE
cd $RDBASE
cmake -DPYTHON_EXECUTABLE=$PYTHON_PREFIX/bin/python \
      -DPYTHON_INCLUDE_PATH=$PYTHON_PREFIX/include/python2.7 \
      -DPYTHON_LIBRARY=`ls $PYTHON_PREFIX/lib/libpython*.so` \
      -DPYTHON_NUMPY_INCLUDE_PATH=$PYTHON_PREFIX/lib/python2.7/site-packages/numpy/core/include \
      -DRDK_BUILD_INCHI_SUPPORT=ON \
      -DINCHI_LIBRARY=$RDKIT_SRC/External/INCHI-API \
      -DINCHI_INCLUDE_DIR=$RDKIT_SRC/External/INCHI-API/src \
      $RDKIT_SRC
make
make install
( cd $PYTHON_PREFIX/local/lib ; ln -sv ../rdkit/lib/lib* . )

