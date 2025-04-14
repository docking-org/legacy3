#!/bin/sh

SOURCE_PKG="$1"
INSTALL_ROOT="$2"
PYTHON_TOOLS=$( dirname $( readlink -f $0 ) )
LD_RUN_PATH='$ORIGIN/../lib:$ORIGIN/../local/lib'
export LD_RUN_PATH

VERSION=`basename "$SOURCE_PKG" | tr [:upper:] [:lower:]`
INSTALL_DIR="$INSTALL_ROOT/$VESRION"
ENV_DIR="$INSTALL_ROOT/environments/$VERSION"

echo "Building and Installing Python (Shared)"
tar -xzf $SOURCE_PKG
cd `basename $SOURCE_PKG .tgz`
./configure --prefix=$INSTALL_DIR --enable-shared
make
make install

echo "Building and Installing Python (Static)"
./configure --prefix=$INSTALL_DIR
make
make install

echo "Creating Local Install Resources Directory"
mkdir -pv $INSTALL_DIR/local/lib
( cd $INSTALL_DIR/local/lib ; ln -sv ../../lib/lib* . )

echo "Writing Bare-Bones Environmnet Script"
echo "#!/bin/sh
export PATH=$INSTALL_DIR/bin:$PATH"
" >> "$INSTALL_DIR"/env.sh
echo "#!/bin/csh
set path = ( $INSTALL_DIR/bin $path )
" >> "$INSTALL_DIR"/env.csh

echo "Building Packaging Tools (Masking PATH to hide System version)"
PATH="" $INSTALL_DIR/bin/python $PYTHON_TOOLS/ez_setup.py
PATH="" $INSTALL_DIR/bin/easy_install pip

echo "Installing Core packages Packages"
$INSTALL_DIR/bin/pip install -r ${PYTHON_TOOLS}/requirements.txt


