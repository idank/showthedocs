  $ . $TESTDIR/setup.t.bash

  $ for f in $(cd $TESTDIR/../external && find . -name '*.html' | cut -c 3-); do
  >     validatedoc "$f"
  > done
  validating 'sql/mysql/select.html'
  tag '<div class="showdocs', group 'select' missing attribute id
  tag '<em class="replaceab', group 'select-expr' has no showdocs-decorate-* class, found [u'replaceable']
  tag '<em class="replaceab', group 'select-expr' missing attribute id
  tag '<code class="literal', group 'foo' has no showdocs-decorate-* class, found [u'literal']
  tag '<code class="literal', group 'foo' missing attribute id
  tag '<code class="literal', group 'foo2' has no showdocs-decorate-* class, found [u'literal']
  tag '<code class="literal', group 'foo2' missing attribute id
  validating 'sql/pg/select.html'
  tag '<span class="showdoc', group 'select' missing attribute id
  tag '<tt class="REPLACEAB', group 'table_name' missing attribute id
  tag '<tt class="COMMAND s', group 'select' missing attribute id
  tag '<tt class="COMMAND s', group 'select' missing attribute id
  tag '<tt class="REPLACEAB', group 'table_name' missing attribute id
  tag '<tt class="LITERAL s', group 'as' missing attribute id
  tag '<tt class="REPLACEAB', group 'table_name' missing attribute id
  validating 'test/select.html'
  tag '<div class="showdocs', group 'select' missing attribute id
  tag '<span class="showdoc', group 'inner' missing attribute id
  tag '<span class="showdoc', group 'from' missing attribute id
  tag '<em class="replaceab', group 'select-expr' has no showdocs-decorate-* class, found [u'replaceable']
  tag '<em class="replaceab', group 'select-expr' missing attribute id
  tag '<code class="literal', group 'foo' has no showdocs-decorate-* class, found [u'literal']
  tag '<code class="literal', group 'foo' missing attribute id
  tag '<code class="literal', group 'foo2' has no showdocs-decorate-* class, found [u'literal']
  tag '<code class="literal', group 'foo2' missing attribute id
