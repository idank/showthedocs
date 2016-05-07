  $ . $TESTDIR/setup.t.bash

  $ for f in $(cd $TESTDIR/../external && find . -name '*.html' | cut -c 3-); do
  >     validatedoc "$f"
  > done
  validating 'nginx/ngx_core_module.html'
  validating 'sql/mysql/select.html'
  tag '<em class="replaceab', group 'select-expr' has no showdocs-decorate-* class, found [u'replaceable']
  tag '<code class="literal', group 'foo' has no showdocs-decorate-* class, found [u'literal']
  tag '<code class="literal', group 'foo2' has no showdocs-decorate-* class, found [u'literal']
  validating 'sql/pg/select.html'
  validating 'test/select.html'
  tag '<em class="replaceab', group 'select-expr' has no showdocs-decorate-* class, found [u'replaceable']
  tag '<code class="literal', group 'foo' has no showdocs-decorate-* class, found [u'literal']
  tag '<code class="literal', group 'foo2' has no showdocs-decorate-* class, found [u'literal']
