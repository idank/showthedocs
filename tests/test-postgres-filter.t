  $ . $TESTDIR/setup.t.bash

  $ $TESTDIR/runfilters.py -l postgres <<EOF
  > <a>nothing here</a>
  > EOF
  <a>nothing here</a>

test annotation of code tags:

  $ $TESTDIR/runfilters.py -l postgres <<EOF
  > <a>nothing here</a>
  > <code>no class</code>
  > <code class="foo">bar</code>
  > <code class="foo">bar <a>baz</a></code>
  > <code class="foo">this exceeds the limit and should be ignored</code>
  > EOF
  <a>nothing here</a>
  <code>no class</code>
  <code class="foo showdocs-decorate-back" data-showdocs="bar">bar</code>
  <code class="foo showdocs-decorate-back" data-showdocs="bar baz">bar <a>baz</a></code>
  <code class="foo">this exceeds the limit and should be ignored</code>

test annotation of div tags:

  $ $TESTDIR/runfilters.py -l postgres <<EOF
  > <a>nothing here</a>
  > <div>no class, no id</div>
  > <div class="foo">no id</div>
  > <div class="foo" id="bar"></div>
  > <div class="REFSECT2"></div>
  > <div class="REFSECT2" id="foo"></div>
  > <div class="REFSECT2" id="SQL-"></div>
  > <div class="REFSECT2" id="SQL-X"></div>
  > EOF
  <a>nothing here</a>
  <div>no class, no id</div>
  <div class="foo">no id</div>
  <div class="foo" id="bar"></div>
  <div class="REFSECT2"></div>
  <div class="REFSECT2" id="foo"></div>
  <div class="REFSECT2" id="SQL-"></div>
  <div class="REFSECT2 showdocs-decorate-block" id="SQL-X" data-showdocs="x"></div>
