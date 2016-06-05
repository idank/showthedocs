  $ . $TESTDIR/setup.t.bash

  $ $TESTDIR/runfilters.py -l mysql <<EOF
  > <span><div id='docs-body'><div>hi</div></div></span>
  > EOF
  <div id="docs-body"><div>hi</div></div>

  $ $TESTDIR/runfilters.py -l mysql <<EOF
  > <span>
  >     <div id='docs-body'>
  >         <a href="foo.html">local link</a>
  >         <img src="bar.png"></img>
  >         <a href="c/d/foo.html">subdirectory link</a>
  >         <a href="http://otherhost/foo.html">absolute link</a>
  >     </div>
  > </span>
  > EOF
  <div id="docs-body">
          <a href="http://localhost/a/b/foo.html">local link</a>
          <img src="http://localhost/a/b/bar.png">
          <a href="http://localhost/a/b/c/d/foo.html">subdirectory link</a>
          <a href="http://otherhost/foo.html">absolute link</a>
      </div>

  $ $TESTDIR/runfilters.py -l mysql <<EOF
  > <span>
  >     <div id='docs-body'>
  >         <code class="a">hi</code>
  >         <code>table_references</code>
  >         <code class="foo">order
  >         by</code>
  >     </div>
  > </span>
  > EOF
  <div id="docs-body">
          <code class="a showdocs-decorate-back" data-showdocs="hi">hi</code>
          <code data-showdocs="table_name" class="showdocs-decorate-back">table_references</code>
          <code class="foo showdocs-decorate-back" data-showdocs="order by">order
          by</code>
      </div>
