import logging, itertools, urllib, codecs
import markupsafe

from flask import render_template, request, redirect
from showdocs import app, html, annotate, structs, docs

from showdocs.structs import Annotation

logger = logging.getLogger(__name__)

def _safedocs(docs):
    for path, externaldoc in docs.withcontents():
        yield path, markupsafe.Markup(externaldoc.contents)

def _csspaths(docs):
    css = set()
    for _, externaldoc in docs.withcontents():
        for path in externaldoc.css:
            css.add('/static/external/' + path)
    return css

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query')
def query():
    q = request.args.get('q', '')
    if not q:
        return redirect('/')

    lang = request.args.get('lang', 'guess')
    formatquery = bool(request.args.get('format', True))

    annotated, docs = annotate.annotate(q, lang, formatquery)

    return render_template('query.html',
                           lang=lang,
                           query=markupsafe.Markup(annotated),
                           docs=_safedocs(docs),
                           additionalcss=_csspaths(docs))

@app.route('/testpage')
def testpage():
    query = '''\
SELECT p.Name AS ProductName
       NonDiscountSales = (OrderQty * UnitPrice),
       Discounts = ((OrderQty * UnitPrice) * UnitPriceDiscount)
FROM Production.Product AS p
INNER JOIN Sales.SalesOrderDetail AS sod ON p.ProductID = sod.ProductID
ORDER BY ProductName DESC;

this is a very very very very very very very very very very very very very very very very very very very very very long line'''

    a = []
    a.append(Annotation(0, query.index('FROM'), 'select', [structs.decorate.BLOCK]))
    a.append(Annotation(query.index('FROM'), query.index('INNER'), 'from', [structs.decorate.BLOCK]))
    a.append(Annotation(query.index('INNER'), query.index('ORDER'), 'inner', [structs.decorate.BLOCK]))
    a.append(Annotation(
        query.index('ORDER'), len(query), 'order', [structs.decorate.BLOCK]))
    a.append(Annotation(query.index('tName'), query.index('= (Ord') + 5, 'foo', [structs.decorate.UNDER]))

    x = 'n.Prod'
    a.append(Annotation(
        query.index(x), query.index(x) + 9, 'foo', [structs.decorate.UNDER]))
    a.append(Annotation(0, 4, 'bar', [structs.decorate.UNDER]))
    a.append(Annotation(2, 6, 'baz', [structs.decorate.UNDER]))
    a.append(Annotation(
        query.index('.Name'), query.index(
            'AS') + 2, 'foobar', [structs.decorate.BACK]))
    a.append(Annotation(
        query.index('Product'), query.index(
            'tName') + 4, 'foobar', [structs.decorate.BACK]))
    a.append(Annotation(
        query.index('((Or'), query.index(
            '((Or') + 9, 'foobar', [structs.decorate.BACK]))
    a.append(Annotation(
        query.index('ct AS p'), query.index(
            'AS sod') + 5, 'convex', [structs.decorate.UNDER]))

    query = html.wrap(query, a)

    d = docs.Collection()
    d.add('test/select.html')

    return render_template('query.html',
                           query=markupsafe.Markup(query),
                           docs=_safedocs(d))
