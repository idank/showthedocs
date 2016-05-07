#!/bin/bash

set -e

function abspath() {
    python -c "import os; print os.path.abspath('"$1"')"
}

ROOT="$(abspath $(dirname "$0")/../..)"
EXTERNALTMP="$ROOT/externaltmp"

mkdir -p "$EXTERNALTMP"

REPO="~/dev/nginx.org"

if ! [[ -d "$EXTERNALTMP/nginx" ]]; then
    hg clone "$REPO" "$EXTERNALTMP/nginx"
fi

FILE="libxslt/en/docs/ngx_core_module.html"
OUTFILE="$ROOT/external/nginx/ngx_core_module.html"

pushd "$EXTERNALTMP/nginx"
make "$FILE"
popd

python <<EOF
from bs4 import BeautifulSoup
contents = open("$EXTERNALTMP/nginx/$FILE").read()
soup = BeautifulSoup(contents, 'lxml')
node = soup.find(id='content')
open("$OUTFILE", 'wb').write(str(node))
print 'wrote', "$OUTFILE"
EOF
