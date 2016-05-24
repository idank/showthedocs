export PYTHONPATH=$PYTHONPATH:$TESTDIR/..
export PATH=$PATH:$TESTDIR/..

function annotator() {
    python $TESTDIR/annotator.py -l $TESTLANG $@
    return $?
}
