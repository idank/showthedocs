import logging
import markupsafe

from flask import render_template
from showdocs import app, html, annotate, structs, docs, views

from showdocs.structs import Annotation

logger = logging.getLogger(__name__)


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
                           docs=views._safedocs(d))
