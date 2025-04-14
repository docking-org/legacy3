HOWTO get started with DOCK
===========================

    python-pip  
    pip install -r install/environ/python/requirements.txt

    # compile libfgz, a small Fortran library to read gzipped files
    pushd docking/DOCK/src/libfgz
    make COMPILER=gnu
    popd

    # complile DOCK and install into the docking/DOCK/bin directory
    pushd docking/DOCK/src/i386
    make COMPILER=gnu
    make install
    popd

    # run all tests
    pushd test
    sh all-test.py
    popd
    
