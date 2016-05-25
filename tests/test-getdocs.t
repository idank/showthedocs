  $ . $TESTDIR/setup.t.bash

  $ export CONFIG=$TMPDIR/config.py
  $ cat <<EOF > $CONFIG
  > from showdocs import config
  > config.update({
  >     'EXTERNAL_DIR': "$TMPDIR/external",
  >     'LOG': False,
  >     })
  > EOF
  $ getdocs.py list
  nginx
  $ getdocs.py build --lang foo
  unknown lang 'foo', known languages: nginx
  [1]

  $ getdocs.py build --config $CONFIG --lang nginx
  $ cd $TMPDIR/external && find .
  .
  ./nginx
  ./nginx/ngx_core_module.html
  ./nginx/http
  ./nginx/http/ngx_http_core_module.html
