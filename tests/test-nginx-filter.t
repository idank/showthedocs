  $ . $TESTDIR/setup.t.bash

  $ $TESTDIR/runfilters.py -l nginx <<EOF
  > <a>no directives</a>
  > EOF
  <a>no directives</a>

  $ $TESTDIR/runfilters.py -l nginx <<EOF
  > <a>before</a>
  > <div class="directive">no id, gets ignored</div>
  > <div class="directive" id="d1">d1</div>
  > <a>after</a>
  > <p>d1 paragraph</p>
  > <div class="directive" id="d2">d2</div>
  > <p>d2 paragraph</p>
  > EOF
  <a>before</a>
  <div class="directive">no id, gets ignored</div>
  <div data-showdocs="d1" class="showdocs-decorate-block"><div class="directive" id="d1">d1</div><a>after</a>
  <p>d1 paragraph</p>
  </div><div data-showdocs="d2" class="showdocs-decorate-block"><div class="directive" id="d2">d2</div><p>d2 paragraph</p>
  </div>
