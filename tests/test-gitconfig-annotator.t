  $ . $TESTDIR/setup.t.bash
  $ export TESTLANG=gitconfig

  $ annotator <<EOF
  > #
  > # This is the config file, and
  > # a '#' or ';' character indicates
  > # a comment
  > #
  > ; core variables
  > [core]
  >     ; Don't trust file modes
  >     filemode = false
  > ; Our diff algorithm
  > [diff]
  >     external = /usr/local/bin/diff-wrapper
  >     renames = true
  > ; Proxy settings
  > [core]
  >     gitproxy=proxy-command for kernel.org
  >     gitproxy=default-proxy ; for all the rest
  > ; HTTP
  > [http]
  >     sslVerify
  > [http "https://weak.example.com"]
  >     sslVerify = false
  >     cookieFile = /tmp/cookie.txt
  > EOF
  Annotation(99, 155, 'section.core', ['showdocs-decorate-block'], 0) '[core'..'false'
  Annotation(139, 147, 'core.filemode', ['showdocs-decorate-back'], 0) 'filemode'
  Annotation(177, 245, 'section.diff', ['showdocs-decorate-block'], 0) '[diff'..' true'
  Annotation(188, 196, 'diff.external', ['showdocs-decorate-back'], 0) 'external'
  Annotation(231, 238, 'diff.renames', ['showdocs-decorate-back'], 0) 'renames'
  Annotation(263, 338, 'section.core', ['showdocs-decorate-block'], 0) '[core'..'proxy'
  Annotation(274, 282, 'core.gitproxy', ['showdocs-decorate-back'], 0) 'gitproxy'
  Annotation(316, 324, 'core.gitproxy', ['showdocs-decorate-back'], 0) 'gitproxy'
  Annotation(365, 385, 'section.http', ['showdocs-decorate-block'], 0) '[http'..'erify'
  Annotation(376, 385, 'http.sslverify', ['showdocs-decorate-back'], 0) 'sslVerify'
  Annotation(386, 474, 'section.http', ['showdocs-decorate-block'], 0) '[http'..'e.txt'
  Annotation(424, 433, 'http.sslverify', ['showdocs-decorate-back'], 0) 'sslVerify'
  Annotation(446, 456, 'http.cookiefile', ['showdocs-decorate-back'], 0) 'cookieFile'

  $ annotator <<EOF
  > [alias]
  > foo = echo
  > EOF
  Annotation(0, 18, 'section.alias', ['showdocs-decorate-block'], 0) '[alia'..' echo'

  $ annotator <<EOF
  > [mergetool "kdiff3"]
  > path = kdiff3
  > EOF
  Annotation(0, 34, 'section.mergetool', ['showdocs-decorate-block'], 0) '[merg'..'diff3'
  Annotation(21, 25, 'mergetool.path', ['showdocs-decorate-back'], 0) 'path'

parsing error:

  $ annotator <<EOF
  > [mergetool
  > path = kdiff3
  > EOF
  Traceback (most recent call last):
  ParsingError: parser gave no additional information (position 11)
