  $ . $TESTDIR/setup.t.bash
  $ export TESTLANG=sql

  $ printf 'select * from a as b group by c' | annotator
  Annotation(0, 6, u'select', ['showdocs-decorate-back'], 0) u'select'
  Annotation(9, 13, u'from', ['showdocs-decorate-back'], 0) u'from'
  Annotation(16, 18, u'as', ['showdocs-decorate-back'], 0) u'as'
  Annotation(21, 29, 'group by', ['showdocs-decorate-back'], 0) u'group by'
  Annotation(0, 8, 'select', ['showdocs-decorate-block'], 0) u'select *'
  Annotation(9, 13, 'from', ['showdocs-decorate-block'], 0) u'from'
  Annotation(14, 20, 'table_name', ['showdocs-decorate-back'], 0) u'a as b'

  $ annotator <<EOF
  > select * from a where b = c
  > EOF
  Annotation(0, 6, u'select', ['showdocs-decorate-back'], 0) u'select'
  Annotation(9, 13, u'from', ['showdocs-decorate-back'], 0) u'from'
  Annotation(16, 21, u'where', ['showdocs-decorate-back'], 0) u'where'
  Annotation(0, 8, 'select', ['showdocs-decorate-block'], 0) u'select *'
  Annotation(9, 13, 'from', ['showdocs-decorate-block'], 0) u'from'
  Annotation(16, 27, 'where', ['showdocs-decorate-block'], 0) u'where'..u'b = c'
  Annotation(14, 15, 'table_name', ['showdocs-decorate-back'], 0) u'a'

  $ annotator <<EOF
  > CREATE TABLE films (
  >     code        char(5) CONSTRAINT firstkey PRIMARY KEY,
  >     title       varchar(40) NOT NULL,
  >     did         integer NOT NULL,
  >     date_prod   date,
  >     kind        varchar(10),
  >     len         interval hour to minute
  > );
  > EOF
  Annotation(0, 6, u'create', ['showdocs-decorate-back'], 0) u'CREATE'
  Annotation(7, 12, u'table', ['showdocs-decorate-back'], 0) u'TABLE'
  Annotation(45, 55, u'constraint', ['showdocs-decorate-back'], 0) u'CONSTRAINT'
  Annotation(65, 72, u'primary', ['showdocs-decorate-back'], 0) u'PRIMARY'
  Annotation(73, 76, u'key', ['showdocs-decorate-back'], 0) u'KEY'
  Annotation(106, 114, u'not null', ['showdocs-decorate-back'], 0) u'NOT NULL'
  Annotation(140, 148, u'not null', ['showdocs-decorate-back'], 0) u'NOT NULL'
  Annotation(231, 233, u'to', ['showdocs-decorate-back'], 0) u'to'
  Annotation(234, 240, u'minute', ['showdocs-decorate-back'], 0) u'minute'
  Annotation(0, 243, 'createtable', ['showdocs-decorate-block'], 0) u'CREAT'..u'te\n);'
  Annotation(13, 18, 'table_name', ['showdocs-decorate-back'], 0) u'films'

sqlparse is pretty lenient:

  $ annotator <<EOF
  > this is clearly not a query!
  > EOF
  Annotation(5, 7, u'is', ['showdocs-decorate-back'], 0) u'is'
  Annotation(16, 19, u'not', ['showdocs-decorate-back'], 0) u'not'
