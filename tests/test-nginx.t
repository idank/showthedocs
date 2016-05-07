  $ . $TESTDIR/setup.t.bash
  $ export TESTLANG=nginx

  $ annotator -f <<EOF
  > user  www www; # comments are omitted from the output
  > worker_processes           5;
  >         
  > http {
  >   include    conf/mime.types;
  > 
  >   if (\$request_method = POST ) {
  >   set            \$foo       N;
  >     return 405;
  > }
  > 
  >   server {
  >     listen       80;
  > 
  >     location ~ \.php$ {
  >       fastcgi_pass   127.0.0.1:1025;
  >     }
  >   }
  > }
  > EOF
  user www www;
  worker_processes 5;
  
  http {
      include conf/mime.types;
  
      if ($request_method = POST ) {
          set $foo N;
          return 405;
      }
  
      server {
          listen 80;
  
          location ~ \.php$ {
              fastcgi_pass 127.0.0.1:1025;
          }
      }
  }

  $ annotator <<EOF
  > user  www www; # comments are omitted from the output
  > worker_processes           5;
  > 
  > http {
  >   include    conf/mime.types;
  > 
  >   if (\$request_method = POST ) {
  >   set            \$foo       N;
  >     return 405;
  > }
  > 
  >   server {
  >     listen       80;
  > 
  >     location ~ \.php$ {
  >       fastcgi_pass   127.0.0.1:1025;
  >     }
  >   }
  > }
  > EOF
  Annotation(0, 4, 'user', ['showdocs-decorate-back'], 0) 'user'
  Annotation(14, 30, 'worker_processes', ['showdocs-decorate-back'], 0) 'worke'..'esses'
  Annotation(35, 273, 'http', ['showdocs-decorate-block'], 0) 'http '..'  }\n}'
  Annotation(46, 53, 'include', ['showdocs-decorate-back'], 0) 'include'
  Annotation(158, 271, 'server', ['showdocs-decorate-block'], 0) 'serve'..'    }'
  Annotation(175, 181, 'listen', ['showdocs-decorate-back'], 0) 'listen'
  Annotation(195, 265, 'location', ['showdocs-decorate-block'], 0) 'locat'..'    }'
  Annotation(227, 239, 'fastcgi_pass', ['showdocs-decorate-back'], 0) 'fastc'..'_pass'
