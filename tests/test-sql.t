  $ . $TESTDIR/setup.t.bash
  $ export TESTLANG=sql

  $ printf 'select * from a as b' | annotator
  Annotation(0, 8, select, ['showdocs-decorate-block'], 0) 'select *'
  Annotation(9, 13, from, ['showdocs-decorate-block'], 0) 'from'
  Annotation(16, 18, as, ['showdocs-decorate-back'], 0) 'as'
  Annotation(14, 20, table_name, ['showdocs-decorate-back'], 0) 'a as b'

  $ annotator <<EOF
  > select * from a where b = c
  > EOF
  Annotation(0, 8, select, ['showdocs-decorate-block'], 0) 'select *'
  Annotation(9, 13, from, ['showdocs-decorate-block'], 0) 'from'
  Annotation(16, 27, where, ['showdocs-decorate-block'], 0) 'where'..'b = c'
  Annotation(14, 15, table_name, ['showdocs-decorate-back'], 0) 'a'

  $ printf 'select * from (select * from a) as b' | annotator -d
  Annotation(0, 8, select, ['showdocs-decorate-block'], 0) 'select *'
  Annotation(9, 13, from, ['showdocs-decorate-block'], 0) 'from'

  $ printf 'select * from a join b where c=d' | annotator -d
  Annotation(0, 8, select, ['showdocs-decorate-block'], 0) 'select *'
  Annotation(9, 13, from, ['showdocs-decorate-block'], 0) 'from'

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
  Annotation(0, 243, createtable, ['showdocs-decorate-block'], 0) 'CREAT'..'te\n);'
  Annotation(13, 18, table_name, ['showdocs-decorate-back'], 0) 'films'
