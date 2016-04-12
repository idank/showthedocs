export PYTHONPATH=$PYTHONPATH:$TESTDIR/..

function annotator() {
    python $TESTDIR/annotator.py -l $TESTLANG $@
    return $?
}

alias validatedoc="python $TESTDIR/validatedoc.py"
