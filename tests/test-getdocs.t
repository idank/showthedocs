  $ . $TESTDIR/setup.t.bash

  $ export CONFIG=$TMPDIR/config.py
  $ cat <<EOF > $CONFIG
  > from showdocs import config
  > config.update({
  >     'EXTERNAL_DIR': "$TMPDIR/external",
  >     'LOG': False,
  >     })
  > EOF
  $ getdocs list
  mysql
  nginx
  postgres
  $ getdocs build --lang foo
  unknown lang 'foo', known languages: nginx, postgres, mysql
  [1]
