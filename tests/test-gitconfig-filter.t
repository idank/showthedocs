  $ . $TESTDIR/setup.t.bash

  $ $TESTDIR/runfilters.py -l gitconfig <<EOF 2>&1 | tail -n 1
  > <div></div>
  > EOF
  ValueError: couldn't find 'configuration file' section

  $ $TESTDIR/runfilters.py -l gitconfig <<EOF
  > <div class="sect1"><h2>configuration file</h2>
  >   <div class="sect2"><div class="dlist">
  >     <dl>
  >       <dt class="hdlist1">section.name</dt>
  >       <dt class="hdlist1">section.&lt;subsection&gt;.name</dt>
  > 
  >       <dt class="hdlist1">advice.*</dt>
  >       <dd><dl><dt class="hdlist1">nestedoption</dt></dl></dd>
  >       <dt class="hdlist1">alias.*</dt>
  > 
  >       <dt class="hdlist1">blahblah</dt>
  >     </dl>
  >   </div></div>
  > </div>
  > EOF
  <div class="sect1"><h2>configuration file</h2>
    <div class="sect2"><div class="dlist">
      <dl>
        <dt class="hdlist1"><span class="hdlist1 showdocs-decorate-back" data-showdocs="section.name">section.name</span>
        </dt><dt class="hdlist1"><span class="hdlist1 showdocs-decorate-back" data-showdocs="section.name">section.&lt;subsection&gt;.name</span>
  
        </dt><dt class="hdlist1">advice.*</dt>
        <dd><dl><dt class="hdlist1"><span class="hdlist1 showdocs-decorate-back" data-showdocs="advice.nestedoption">nestedoption</span></dt></dl></dd>
        <dt class="hdlist1"><span class="hdlist1 showdocs-decorate-back" data-showdocs="section.alias">alias.*</span>
  
        </dt><dt class="hdlist1">blahblah</dt>
      </dl>
    </div></div>
  </div>
