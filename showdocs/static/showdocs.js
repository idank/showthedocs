var urlhashprefix = "#sd-";
var sizes = {
    block: {
        width: 8,
        margin: 25,
        linegap: 3,
        linewidth: 8*10,
        circler: 3,
        circlespacing: 10,
        padoverlap: -8 - 5,
        lettersize: 20,
    },
    linkmargin: 5,
};


function yforscroll(element) {
    var y = offset(element).top;
    y -= $("#affixed").height();
    // go back a bit so the element is behind the bottom border blur of
    // #affixed.
    y -= 30;
    return y;
}

function elementfromhash() {
    // #sd-.*-\d+
    var r = new RegExp(urlhashprefix + "(.*)-(\\d+)");
    var m = r.exec(window.location.hash);
    if (m != null) {
        var g = m[1];
        var index = parseInt(m[2]);
        var samegroup = d3.selectAll("#docs [data-showdocs=" + g + "]")[0];
        if (index < samegroup.length) {
            return samegroup[index];
        }

        if (samegroup.length == 0) {
            console.log('unknown group', g);
        }
        else if (samegroup.length <= index) {
            console.log('out of bound index', index, 'for group', g);
        }
    }
    return null;
}

function scrolltohash() {
    if (window.location.hash.startsWith(urlhashprefix)) {
        var realid = window.location.hash.slice(urlhashprefix.length);
        if ($("#" + realid).length) {
            setTimeout(function() {
                window.scrollTo(0, yforscroll($("#" + realid)));
            }, 1);
        }
    }
}

function windowheight() {
    return window.innerHeight || document.documentElement.clientHeight;
}

function inView(e) {
    var rect = e.getBoundingClientRect();
    var viewport = {
        top: 0, left: 0,
        bottom: window.innerHeight || document.documentElement.clientHeight,
        right: window.innerWidth || document.documentElement.clientWidth};

    // If this is inside #docs, set the top of the viewport to the height of
    // #affixed, since items between 0-height are behind it.
    if ($("#docs").find(e).length) {
        viewport.top += $("#affixed").height();
    }
    // If we're inside #query, the top-bottom are between the bottom of .topnav
    // and height of #affixed.
    else if ($("#query").find(e).length) {
        viewport.top = $(".topnav").height();
        viewport.bottom = $("#affixed").height();
    }

    var h = $(e).height();
    var w = $(e).width();

    // Consider it in view if any interior point of rect is inside the
    // viewport.
    return (
        (rect.top >= viewport.top || rect.top+h >= viewport.top) &&
        (rect.left >= viewport.left || rect.left+w >= viewport.left) &&
        (rect.bottom <= viewport.bottom || rect.bottom-h <= viewport.bottom) &&
        (rect.right <= viewport.right || rect.right-w <= viewport.right)
    );
}

function offset(e) {
    var $e = $(e);
    var o = $e.offset();
    // Use outerWidth/Height to account for border/padding. Otherwise the
    // source/dest position in addhoverlinks doesn't end up in the middle of
    // the element (.showdocs-decorate-back).
    o.width = $e.outerWidth();
    o.height = $e.outerHeight();
    o.bottom = o.top + o.height;
    o.right = o.left + o.width;
    return o;
}

function pos(e) {
    var $e = $(e);
    var p = $e.position();
    p.bottom = p.top + $e.height();
    p.right = p.left + $e.width();
    return p;
}

function rnd(x) {
    return Math.round(x);
}

function findPixelsBetweenLines() {
    $("#query").prepend('<span id="l1">a\n</span><span id="l2">b</span>');
    var px = Math.abs($('#l1').position().top + $('#l1').height() - $('#l2').position().top);
    $('#l1').remove();
    $('#l2').remove();
    return px;
}

function addhoverlinks(e) {
    d3.select(e)
        .on('click.links', function() {
            clickgroup(this);
        })
        .on('mouseenter.links', function() {
            var g = findparentgroup(this);
            // Group elements by their top offset. Round to the nearest
            // multiple of 5 so those that are roughly on the same end up in
            // the same group.
            var keyfromoffset = function(e) {
                return (Math.floor(offset(e).top / 5) * 5).toString();
            };
            var bins = d3.nest()
                .key(keyfromoffset)
                .sortKeys(function(a, b) { return d3.ascending(parseInt(a), parseInt(b)); })
                // Connect everything with data-showdocs that isn't a <g> and
                // is on the screen.
                .entries(d3.selectAll("[data-showdocs=" + g + "].showdocs-decorate-back:not(g)")
                    .filter(function() {
                        return inView(this) ? this : null;
                    })[0]);

            var thiskey = keyfromoffset(this);
            var thisindex = bins.findIndex(function(d) {
                return d.key == thiskey;
            });
            var osource = offset(this);

            var computelinks = function(osource, range) {
                var stages = [];
                range.forEach(function(i) {
                    var links = [];
                    bins[i].values.forEach(function(current) {
                        var otarget = offset(current);
                        var link = {
                            source: {x: osource.left + osource.width/2},
                            target: {x: otarget.left+otarget.width/2},
                        };

                        // source is below target
                        if (osource.top > otarget.top) {
                            link.source.y = osource.top - sizes.linkmargin;
                            link.target.y = otarget.bottom + sizes.linkmargin;
                        }
                        else {
                            link.source.y = osource.bottom + sizes.linkmargin;
                            link.target.y = otarget.top - sizes.linkmargin;
                        }

                        links.push(link);
                    });
                    stages.push(links);
                    osource = offset(bins[i].values[0]);
                });
                return stages;
            };
            var stagesup = computelinks(osource, d3.range(thisindex-1, -1, -1));
            var stagesdown = computelinks(osource, d3.range(thisindex+1, bins.length));
            var diagonal = d3.svg.diagonal();
            function drawlinks(duration, links, i) {
                function transitionpath(which) {
                    d3.select("#main-canvas")
                        .append("g")
                        .selectAll(which)
                        .data(links)
                        .enter()
                        .append("path")
                        .classed(which, true)
                        .attr("d", diagonal)
                        .each(function() {
                            var totalLength = d3.select(this).node().getTotalLength();

                            d3.select(this)
                              .attr("stroke-dasharray", totalLength + " " + totalLength)
                              .attr("stroke-dashoffset", totalLength)
                              .transition()
                                .duration(duration)
                                .delay(duration*i)
                                .ease("linear")
                                .attr("stroke-dashoffset", 0);
                        });
                }
                transitionpath('showdocs-link-back');
                transitionpath('showdocs-link');
            };
            const totalduration = 750;
            stagesup.forEach(drawlinks.bind(undefined, totalduration / stagesup.length));
            stagesdown.forEach(drawlinks.bind(undefined, totalduration / stagesdown.length));

            highlightgroup(d3.select(this));
            // Check if we have anything for 'this' in the scrollbar. If so,
            // highlight it too. Otherwise, highlight everything with the same
            // group.
            if ('__scrollbarg__' in this) {
                highlightgroup(d3.select(this.__scrollbarg__));
            }
            else {
                highlightgroup(d3.selectAll("#docs-scrollbar-canvas [data-showdocs=" + g + "]"));
            }
        })
        .on('mouseleave.links', function() {
            // Clear the links.
            d3.selectAll("#main-canvas *")
                .transition()
                .style('opacity', 0)
                .remove();

            unhighlightgroup(d3.select(this));
            if ('__scrollbarg__' in this) {
                unhighlightgroup(d3.select(this.__scrollbarg__));
            }
            else {
                var g = findparentgroup(this);
                unhighlightgroup(d3.selectAll("#docs-scrollbar-canvas [data-showdocs=" + g + "]"));
            }
        });
}

function initlegend() {
    var ordered = [];
    var seen = d3.set();
    d3.selectAll("#query [data-showdocs]")
        .each(function() {
            var g = this.getAttribute("data-showdocs");
            if (seen.has(g))
                return;
            ordered.push(g);
            seen.add(g);
        });

    var m = {
        margin: {left: 40, right: 2, top: 20},
        // Padding on the y axis between items.
        itempadding: 15,
        // Width and height of the rect per item.
        width: 20,
        height: 12,
        symbolradius: 12,
        lettersize: 25,
        // Number of items per column.
        itemspercolumn: 3,
        // Padding between item rect and symbol/text.
        itempad: 15,
    };
    // Where to start the legend.
    m.starty = m.margin.top;
    m.columnwidth = m.width + m.itempad + m.symbolradius * 2;

    var g = d3.select("#legend-canvas")
        .append("g")
        .classed("showdocs-legend clickable", true);

    ordered.forEach(function(group, i) {
        var shapes = ShapesContainer();

        var x = Math.floor(i / m.itemspercolumn) * m.columnwidth;
        var y = m.starty + (m.height + m.itempadding) * (i % m.itemspercolumn);
        shapes.rects.push({
            x: x, y: y,
            rx: 5, ry: 5,
            width: m.width, height: m.height
        });
        // Update x to be after the rect.
        x += m.width;
        if (groupstate[group].hasOwnProperty('symbol')) {
            shapes.symbols.push({
                fill: groupstate[group].symbol.fill,
                stroke: groupstate[group].symbol.stroke,
                type: groupstate[group].symbol.type,
                x: x+m.itempad, y: y + m.height/2,
                radius: m.symbolradius,
            });
        }
        else {
            y += 2;
            shapes.text.push({
                text: groupstate[group].letter,
                x: x+m.itempad, y: y + m.height/2,
                size: m.lettersize,
                font: 'monospace',
                anchor: 'middle',
                alignment: 'middle',
            });
        }

        var gg = g.append("g");
        gg.attr('data-showdocs', group);
        gg.on('click', function() {
            clickgroup(this);
        });
        gg.on('mouseenter', function() {
            var g = findparentgroup(this);
            highlightgroup(d3.selectAll("[data-showdocs="+g+"]"));
        });
        gg.on('mouseleave', function() {
            var g = findparentgroup(this);
            unhighlightgroup(d3.selectAll("[data-showdocs="+g+"]"));
        });
        appendshapes(gg, group, shapes);
    });

    // Align everything to the right edge of #legend-canvas.
    var gwidth = g.node().getBBox().width;
    var gwidthpadded = gwidth + m.margin.right;
    var rightedge = $("#legend-canvas").width();
    g.attr('transform', 'translate(' + (rightedge - gwidthpadded) + ')')
}

function ShapesContainer() {
    var d = {
        rects: [],
        circles: [],
        symbols: [],
        lines: [],
        path: [],
        links: [],
        text: [],
        empty: function() {
          for (var k in this) {
            if (Array.isArray(this[k]) && this[k].length > 0)
              return false;
          }
          return true;
        },
        g: [],
    };
    return d;
}

function initialize() {
    var queryData = $("#query [data-showdocs]");

    var groups = _.groupBy(queryData, function(e) {
        return e.getAttribute("data-showdocs");
    });

    pxBetweenLines = findPixelsBetweenLines();

    groupstate = {}; // global
    var color = d3.scale.category20();

    var i = 0;
    for (var k in groups) {
        groupstate[k] = {color: color(i)};
        i++;
    }

    var i = 0;
    var seen = d3.set();
    d3.selectAll("#query .showdocs-decorate-block")
        .each(function() {
            var g = this.getAttribute("data-showdocs");
            if (seen.has(g))
                return;
            groupstate[g].letter = String.fromCharCode("A".charCodeAt(0) + seen.size());
            seen.add(g);
        });
    seen = d3.set();
    d3.selectAll("#query [data-showdocs]:not(.showdocs-decorate-block)")
        .each(function() {
            var g = this.getAttribute("data-showdocs");
            if (seen.has(g))
                return;
            var fill = seen.size() < d3.svg.symbolTypes.length;
            console.log(fill);
            groupstate[g].symbol = {
                fill: fill,
                stroke: !fill,
                type: d3.svg.symbolTypes[seen.size() % d3.svg.symbolTypes.length],
            };

            seen.add(g);
        });

    initlegend();

    // Key shapes by the group that created them so we can nest them all in the
    // same <g>.
    var queryshapes = {};
    // Shapes from -block decorations go into a different svg that isn't
    // inside #query-scroller because they're outside its bounds (to the left).
    // Add them to a different svg that is translated when #query-scroller is
    // scrolled.
    d3.select("#query-scroller").on('scroll', function() {
        var translate = [0, -this.scrollTop];
        d3.select("#query-container #translate-on-scroll").attr('transform', 'translate(' + translate + ')');
        d3.select(".translate-on-scroll").attr('transform', 'translate(' + translate + ')');
    });
    var queryblockshapes = {};

    for (var g in groups) {
        queryshapes[g] = ShapesContainer();
        queryblockshapes[g] = ShapesContainer();
    }

    var queryblockindices = arrangeintervals(
        d3.selectAll("#query .showdocs-decorate-block[data-showdocs]")[0]
            .map(function(v) { return {e: v, interval: {s: rnd(pos(v).top), e: rnd(pos(v).bottom)}}; }),
        function(d) { return d.interval; },
        true);

    queryData.each(function() {
        var $this = $(this);
        var g = this.getAttribute("data-showdocs");
        var p = pos(this);
        var h = $this.height();
        var w = $this.width();

        var shapes = queryshapes[g];
        var blockshapes = queryblockshapes[g];

        if ($this.hasClass("showdocs-decorate-block")) {
            let startx = offset($("#query")).left - sizes.block.margin;
            let starty = p.top;

            var blockindex = queryblockindices.find(function(d) { return d.e === this; }, this).index;
            let x = startx - sizes.block.width + (blockindex * sizes.block.padoverlap);
            blockshapes.rects.push({
                x: x,
                y: starty - pxBetweenLines / 4,
                rx: 5,
                ry: 5,
                width: sizes.block.width,
                height: h + (pxBetweenLines / 4) * 2
            });
            let fontsize = Math.max(rnd(pxBetweenLines*1.8), rnd(h / 2));
            let linewidth = sizes.block.linewidth + fontsize / 1.3;
            blockshapes.lines.push({
                x1: x - sizes.block.linegap,
                y1: starty + h/2,
                x2: x - linewidth,
                y2: starty + h/2,
                strokewidth: 8,
                color: 'white',
            });
            blockshapes.lines.push({
                x1: x - sizes.block.linegap,
                y1: starty + h/2,
                x2: x - linewidth,
                y2: starty + h/2,
                strokewidth: 1,
            });
            x = x - linewidth - sizes.block.circler;
            blockshapes.circles.push({
                cx: x,
                cy: starty + h/2,
                r: sizes.block.circler
            });
            x -= sizes.block.circlespacing;
            blockshapes.text.push({
                x: x,
                y: starty + rnd(h/2)+3,
                text: groupstate[g].letter,
                font: 'monospace',
                size: fontsize,
                anchor: "end",
                alignment: "middle",
            });
        }
        else if ($this.hasClass("showdocs-decorate-back")) {
            $this.css('background-color', groupstate[g].color);
            addhoverlinks(this);
        }
        else if ($this.hasClass("showdocs-decorate-under")) {
            var height = 5;
            var padY = 3 + height;
            var walker = document.createTreeWalker(
                    d3.select('#query').node(),
                    NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
            var sawcurrent = false;
            var connect = false;
            while (walker.nextNode()) {
                if (!sawcurrent && walker.currentNode === this) {
                    sawcurrent = true;
                }

                if (sawcurrent && walker.currentNode.nodeType == Node.TEXT_NODE) {
                    var currtext = walker.currentNode.textContent;
                    if (currtext == $this.text())
                        continue;

                    var parentelement = walker.currentNode.parentElement;
                    var attempt = 0;
                    while (attempt++ < 5 && $(parentelement).text() == currtext) {
                        if (parentelement.getAttribute('data-showdocs') == g) {
                            connect = true;
                            w += (pos(parentelement).right - p.right);
                            break;
                        }
                        parentelement = parentelement.parentElement;
                    }

                    break;
                }
            }
            shapes.rects.push({
                x: p.left,
                y: p.bottom + 5,
                width: w,
                height: height,
                rx: 2,
                ry: 2});
        }
        else {
            console.log('unknown decoration for ', this);
        }
    });

    console.log(queryblockshapes);
    [[queryshapes, "#query-canvas-inner"], [queryblockshapes, "#translate-on-scroll"]].forEach(function(pair) {
        var shapes = pair[0];
        var selection = d3.select(pair[1]);

        for (let g in groups) {
            if (shapes[g].empty())
                continue;

            var gg = selection
                .append('g')
                .attr('data-showdocs', g)
                .classed('clickable', true)
                .on('mouseenter', function() {
                    highlightgroup(d3.selectAll("#docs-scrollbar-canvas [data-showdocs=" + g + "]"));
                })
                .on('mouseleave', function() {
                    unhighlightgroup(d3.selectAll("#docs-scrollbar-canvas [data-showdocs=" + g + "]"));
                })
                .on('click', function() { clickgroup(this); });
            appendshapes(gg, g, shapes[g]);
        }
    });

    var docswindowheight = windowheight() - $("#affixed").height();
    var docsshapes = {};
    var docsblockindices = arrangeintervals(
        d3.selectAll("#docs .showdocs-decorate-block[data-showdocs]")
            .filter(groupsinquery)[0]
            .map(function(v) { return {e: v, interval: {s: rnd(pos(v).top), e: rnd(pos(v).bottom)}}; }),
        function(d) { return d.interval; },
        false);

    d3.selectAll("#docs [data-showdocs]")
    .filter(groupsinquery)
    .call(function() {
        if (this.empty()) {
            console.log("#docs contains no tags with data-showdocs attribute!");
        }
    })
    .each(function() {
        var $this = $(this);
        var g = this.getAttribute("data-showdocs");
        var p = pos(this);
        var h = $this.outerHeight();
        var w = $this.width();

        if (!(g in docsshapes))
            docsshapes[g] = ShapesContainer();

        var shapes = docsshapes[g];

        if ($this.hasClass("showdocs-decorate-block")) {
            var rectstartx = 5;
            var padx = sizes.block.width + 8;
            var letterstartx = 10;
            var symbolstartx = 5 + sizes.block.width/2;
            var blockindex = docsblockindices.find(function(d) { return d.e === this; }, this).index;

            // Put the letter at every multiple of the window height of #docs.
            for (var i = 0; i <= Math.floor(h / docswindowheight); i++) {
                var strokedshapes = ShapesContainer();
                shapes.g.push({
                    class: 'showdocs-decorate-block-lettersymbol-outline',
                    shapes: strokedshapes,
                });

                var firstdelta = 0;

                if ('letter' in groupstate[g]) {
                    if (i == 0)
                        firstdelta = -10;
                    let d = {
                        x: letterstartx+(padx*blockindex),
                        y: p.top+(i*docswindowheight)+firstdelta,
                        text: groupstate[g].letter,
                        font: 'monospace',
                    };

                    strokedshapes.text.push(d);
                    strokedshapes.text.push(d);
                }
                else {
                    if (i == 0)
                        firstdelta = -15;
                    let d = {
                        x: symbolstartx+(padx*blockindex),
                        y: p.top+(i*docswindowheight)+firstdelta,
                        fill: groupstate[g].symbol.fill,
                        stroke: groupstate[g].symbol.stroke,
                        type: groupstate[g].symbol.type,
                        radius: 10,
                    };

                    strokedshapes.symbols.push(d);
                    strokedshapes.symbols.push(d);
                }
            }
            shapes.rects.push({
                x: rectstartx+(padx*blockindex),
                y: p.top,
                rx: 5,
                ry: 5,
                width: sizes.block.width,
                height: h,
            });
        }
        else if ($this.hasClass("showdocs-decorate-back")) {
            $this.css('background-color', groupstate[g].color);
            addhoverlinks(this);
        }
    });

    var dcanvas = d3.select("#docs-canvas")
        .append('g')
        .attr('transform', 'translate(' + [0, -$("#affixed").height()] + ')');
    for (var g in docsshapes) {
        if (docsshapes[g].empty())
            continue;

        var gg = dcanvas.append('g')
            .attr('data-showdocs', g)
            .classed('clickable', true)
        appendshapes(gg, g, docsshapes[g]);
    }

    initscrollbar();
    // circleunder();
}

function findparentgroup(e) {
    while (e != document) {
        var g = e.getAttribute('data-showdocs');
        if (g != null)
            return g;
        e = e.parentNode;
    }

    console.log('findparentgroup for', e, 'is null!');
    return null;
}

function clickgroup(e) {
    var g = findparentgroup(e);
    console.log('clickgroup', g);
    // Clicking on an item in #docs scrolls to the next tag and updates
    // the url hash.
    var samegroup = d3.selectAll("#docs [data-showdocs=" + g + "]")[0];
    if (samegroup.length == 0)
        return;

    // If the clicked element is inside #docs, go to the one after it.
    // Otherwise, look at location.url and go to the next one.
    var index = 0;
    if ($("#docs").find(e).length != 0) {
        var thisindex = samegroup.indexOf(e);
        if (thisindex !=- 1) {
            index = thisindex + 1;
        }
    }
    else {
        var hashelement = elementfromhash(g);
        if (hashelement != null) {
            var hashindex = samegroup.indexOf(hashelement);
            if (hashindex !=- 1) {
                index = hashindex + 1;
            }
        }
    }
    // Wrap around to the start.
    index = index % samegroup.length;
    var scrollto = samegroup[index];
    window.location.hash = urlhashprefix + g + "-" + index;

    window.scrollTo(0, yforscroll(scrollto));
}

function highlightgroup(selection) {
    if (selection.empty()) {
        console.log('highlightgroup empty selection!');
        return;
    }

    var g = findparentgroup(selection.node());
    console.log('highlightgroup', selection, g);
    var c = d3.rgb(groupstate[g].color);

    selection
        .filter(function() { return d3.select(this).classed('showdocs-decorate-back') && inView(this); })
        .transition()
        .duration(750)
        .styleTween('box-shadow', function() {
            var i = d3.interpolate('0px', '3px');
            return function(t) {
                var s = '0px 0px 0px ' + i(t) + ' black';
                return s;
            };
        });

    selection
        .filter(function() { return d3.select(this).classed('showdocs-decorate-under'); })
        .each(function() { d3.select(this.__highlightg__).style('display', null); });

    // Start css animation for symbols in the scrollbar.
    selection.selectAll(".showdocs-decorate-symbol-pulse path")
        .classed('showdocs-decorate-symbol-pulse-animate', true);

    selection
        .filter(function() { return d3.select(this).classed('showdocs-decorate-letter-zoom'); })
        .selectAll("text")
        .transition()
        .duration(750)
        .attr('font-size', '60px');
}

function unhighlightgroup(selection) {
    if (selection.empty()) {
        console.log('unhighlightgroup empty selection!');
        return;
    }

    var g = findparentgroup(selection.node());
    console.log('unhighlightgroup', selection, g);
    var c = d3.rgb(groupstate[g].color);

    selection
        .filter(function() { return d3.select(this).classed('showdocs-decorate-back') && inView(this); })
        .transition()
        .styleTween('box-shadow', function() {
            var i = d3.interpolate('3px', '0px');
            return function(t) {
                return '0px 0px 0px ' + i(t) + ' black';
            };
        })
        .each('end', function() { d3.select(this).style('box-shadow', null); });

    selection
        .filter(function() { return d3.select(this).classed('showdocs-decorate-under'); })
        .each(function() { d3.select(this.__highlightg__).style('display', 'none'); });

    // Stop css animation for symbols in the scrollbar.
    selection.selectAll(".showdocs-decorate-symbol-pulse path")
        .classed('showdocs-decorate-symbol-pulse-animate', false);

    selection
        .filter(function() { return d3.select(this).classed('showdocs-decorate-letter-zoom'); })
        .selectAll("text")
        .transition()
        .attr('font-size', '40px');
}

function appendshapes(selection, group, shapes) {
    var color = null;
    if (group != null)
        color = groupstate[group].color;

    selection.selectAll("rect")
        .data(shapes.rects)
        .enter()
        .append("rect")
        .attr("fill", function(d) { return ('color' in d) ? d.color : color;})
        .attr("x", function(d) { return rnd(d.x); })
        .attr("y", function(d) { return rnd(d.y); })
        .attr("rx", function(d) { return rnd(d.rx); })
        .attr("ry", function(d) { return rnd(d.ry); })
        .attr("width", function(d) { return rnd(d.width); })
        .attr("height", function(d) { return rnd(d.height); });

    selection.selectAll("line")
        .data(shapes.lines)
        .enter()
        .append("line")
        .attr("stroke-width", function(d) { return d.strokewidth; })
        .attr("stroke", function(d) { return ('color' in d) ? d.color : color;})
        .attr("x1", function(d) { return rnd(d.x1); })
        .attr("y1", function(d) { return rnd(d.y1); })
        .attr("x2", function(d) { return rnd(d.x2); })
        .attr("y2", function(d) { return rnd(d.y2); });

    selection.selectAll("path")
        .data(shapes.path)
        .enter()
        .append("path")
        .attr({
            fill: 'none',
            'stroke': color,
            'stroke-width': '2px'
        })
        .attr('d', function(d) {
            return d3.svg.line()
                .x(function(d) { return rnd(d.x); })
                .y(function(d) { return rnd(d.y); })
                .interpolate('basis')(d.data); });

    selection.selectAll("text")
        .data(shapes.text)
        .enter()
        .append("text")
        .attr("x", function(d) { return rnd(d.x); })
        .attr("y", function(d) { return rnd(d.y); })
        .attr("font-family", function(d) { return d.font; })
        .attr("font-size", function(d) { return d.size; })
        .attr("fill", function(d) { return ('color' in d) ? d.color : color;})
        .attr("text-anchor", function(d) { return d.anchor; })
        .attr("alignment-baseline", function(d) { return d.alignment; })
        .text(function(d) { return d.text; });

    selection.selectAll("circle")
        .data(shapes.circles)
        .enter()
        .append("circle")
        .attr("stroke-width", 1)
        .attr("stroke", color)
        .attr("fill", "none")
        .attr("cx", function(d) { return rnd(d.cx); })
        .attr("cy", function(d) { return rnd(d.cy); })
        .attr("r", function(d) { return rnd(d.r); });

    selection.selectAll(".showdocs-decorate-symbol")
        .data(shapes.symbols)
        .enter()
        .append("path")
        .classed("showdocs-decorate-symbol", true)
        .style("fill", function(d) { return (d.fill ? color : null); })
        .style("stroke", function(d) { return (d.stroke ? color : null); })
        .attr("transform", function(d) { return "translate(" + [rnd(d.x), rnd(d.y)] + ")"; })
        .attr("d", d3.svg.symbol()
          .size(function(d) { return d3.scale.pow().exponent(2)(d.radius); })
          .type(function(d) { return d.type; }));

    shapes.g.forEach(function(g) {
        var gg = selection
            .append('g');

        for (var k in g) {
            if (k != 'shapes')
                gg.attr(k, g[k]);
        }

        appendshapes(gg, group, g.shapes);
    });
}

function initscrollbar() {
    var selection = d3.selectAll("#docs [data-showdocs]")
        .filter(groupsinquery);

    const m = d3.max(selection[0].map(function(x) { return pos(x).top; }));
    const affixtop = rnd($("#affixed").height());
    var scrollyscale = d3.scale.linear()
        .domain([
            0,
            $('body').height()
        ])
        .range([0, $("#docs-scrollbar").height()]);

    var scrollxscale = d3.scale.linear()
        .domain([0, rnd($("#docs").width())])
        .range([10, $("#docs-scrollbar").width()-10]);

    selection.each(function() {
        var $this = $(this);
        var g = this.getAttribute("data-showdocs");
        var p = pos(this);
        // We want items at the top of #docs to be at the top of the
        // scrollbar. But the position here is relative to the document,
        // so we need to subtract the space occupied by stuff preceding #docs.
        p.top -= affixtop;
        p.bottom -= affixtop;

        const r = 10;
        var x = 10+scrollxscale(p.left);
        // This is the center of the shape, account for the radius.
        var y = scrollyscale(p.top) + r/2;

        var that = this;
        var group = d3.select("#docs-scrollbar-canvas")
            .append('g')
            .attr('data-showdocs', g)
            .classed('clickable', true)
            .on('click', function() {
                var index = d3.selectAll("#docs [data-showdocs=" + g + "]")[0].indexOf(that);
                window.location.hash = urlhashprefix + g + "-" + index;
                window.scrollTo(0, yforscroll(that));
            })
            .on('mouseenter', function() {
                highlightgroup(d3.select(that));
                highlightgroup(d3.select(this));
            })
            .on('mouseleave', function() {
                unhighlightgroup(d3.select(that));
                unhighlightgroup(d3.select(this));
            });

        // Associate the item we're handing with the g we've created in the
        // scrollbar. It will be used when the item is hovered.
        this.__scrollbarg__ = group.node();

        var shapes = ShapesContainer();

        if (groupstate[g].hasOwnProperty('symbol')) {
            shapes.symbols.push({
              fill: groupstate[g].symbol.fill,
              stroke: groupstate[g].symbol.stroke,
              type: groupstate[g].symbol.type,
              radius: r,
              x: 0, y: 0,
            });

            var scaledsymbols = ShapesContainer();
            shapes.g.push({class: 'showdocs-decorate-symbol-pulse', shapes: scaledsymbols});
            scaledsymbols.symbols.push({
              fill: false,
              stroke: true,
              type: groupstate[g].symbol.type,
              radius: r,
              x: 0, y: 0,
            });


            var that = this;
            group.attr('transform', 'translate(' + [x, y] + ')');
        }
        else {
            shapes.text.push({
                text: groupstate[g].letter,
                x: x, y: y,
                size: '40px',
                font: 'monospace',
                anchor: 'middle',
                alignment: 'middle',
            });
            group.classed('showdocs-decorate-letter-zoom', true);
            appendshapes(group, g, shapes);
        }

        appendshapes(group, g, shapes);
    });

    var scrollery = d3.scale.linear()
        .domain([0, $('body').height()])
        .range([0, $("#docs-scrollbar").height()]);

    var scrollerheight = Math.max(5, rnd(scrollery(window.innerHeight - affixtop)));
    var scrollbareyes = d3.select("#docs-scrollbar-canvas")
        .append('rect')
        .attr('class', 'scrollbar-eyes')
        .attr('width', $("#docs-scrollbar").width())
        .attr('height', scrollerheight)
        .attr('x', 0)
        .attr('y', 0)
        .attr('rx', 5)
        .attr('ry', 5);

    $(window).scroll(function() {
          scrollbareyes.attr('transform', 'translate(0, ' + scrollery(window.scrollY) + ')');
    });
}

function clean() {
    d3.selectAll("[data-showdocs]")
        .on('mouseenter', null)
        .on('mouseleave', null);
}

function circleunder() {
    function mid(a, b) {
      return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    }

    function distance(a, b) {
      var xd = a[0] - b[0];
      var yd = a[1] - b[1];
      return Math.sqrt(xd * xd + yd * yd);
    }

    function key(e) {
        return (Math.floor(offset(e).top / 5) * 5).toString();
    };

    var nest = d3.nest()
        .key(key)
        .sortKeys(function(a, b) { return d3.ascending(parseInt(a), parseInt(b)); })
        .entries(d3.selectAll("#query .showdocs-decorate-under")[0]);

    if (!nest.length)
        return;

    var lineheight = pxBetweenLines;

    var clusters = [];
    var currcluster = [nest[0]];
    for (var i = 1; i < nest.length; i++) {
        var prevtop = parseInt(nest[i-1].key);
        var currtop = parseInt(nest[i].key);
        if (currtop-prevtop > lineheight*1.8) {
            clusters.push(currcluster);
            currcluster = [nest[i]];
        }
        else {
            currcluster.push(nest[i]);
        }
    }
    clusters.push(currcluster);
    console.log('clusters', clusters);

    function circlecluster(nest) {
        const pad = 11;
        var path = [];

        nest.forEach(function(d, i) {
          var p = pos(d.values[d.values.length - 1]);
          path.push([p.right + pad, p.top - pad]);
          path.push([p.right + pad, p.bottom + pad]);
        });
        nest.reverse().forEach(function(d, i) {
          var p = pos(d.values[0]);
          path.push([p.left - pad, p.bottom + pad]);
          path.push([p.left - pad, p.top - pad]);
        });

        var midbottom = nest[0].values[Math.floor(nest[0].values.length / 2)];

        var closenessthreshold = 30;
        for (var i = 0; i < path.length; i++) {
          for (var j = i + 1; j < path.length; j++) {
            var pi = path[i];
            var pj = path[j];
            if (distance(pi, pj) < closenessthreshold) {
              path.splice(j, 1);
              j--;
            }
          }
        }
        // Close the path.
        path.push(path[0]);
        path.push(path[1]);

        function noise() {
          return 0;//Math.floor(Math.random() * 10) - 5;
        }
        path.forEach(function(p) {
          p[0] += noise();
          p[1] += noise();
        });


        var mprev = mid(path[0], path[path.length - 1]);
        var prev = mprev;
        var spath = 'M' + mprev;
        var alpha = 0.6;
        for (var i = 1; i < path.length; i++) {
          var curr = path[i];
          var m = mid(prev, curr);
          var c1 = [mprev[0] + (prev[0] - mprev[0]) * alpha, mprev[1] + (prev[1] - mprev[1]) * alpha];
          var c2 = [m[0] + (prev[0] - m[0]) * alpha, m[1] + (prev[1] - m[1]) * alpha];
          spath += ' C' + c1 + ' ' + c2 + ' ' + m;
          prev = curr;
          mprev = m;
        }

        var g = d3.select("#query-canvas")
            .append('g')
            .style('display', 'none');
        g.append("path")
            .classed('showdocs-link-back', true)
            .attr('d', spath);
        g.append("path")
            .classed('showdocs-link', true)
            .attr('d', spath);

        nest.forEach(function(d) {
            d.values.forEach(function(node) {
                node.__highlightg__ = g.node();
            });
        });
    }

    clusters.forEach(function(cluster) {
        circlecluster(cluster);
    });
}

function arrangeintervals(arr, intervalfn, reverse) {
    function overlap(i1, i2) {
        if (i1.s >= i2.s && i1.s <= i2.e)
            return true;
        if (i1.e >= i2.s && i1.e <= i2.e)
            return true;
        return false;
    }

    function allocateindex(arr) {
        var index = 0;
        for (var i = 0; i <= arr.length; i++) {
            while (true) {
                if (arr.some(function(v) { return v.index == index; })) {
                    index += 1;
                }
                else {
                    return index;
                }
            }
        }
    }

    var disjoint = [];
    arr.forEach(function(v1) {
        var i1 = intervalfn(v1);
        for (var i = 0; i < disjoint.length; i++) {
            if (disjoint[i].some(function(v2) { return overlap(i1, intervalfn(v2)); })) {
                disjoint[i].push(v1);
                return;
            }
        }
        disjoint.push([v1]);
    });

    disjoint.forEach(function(overlapping) {
        overlapping = _.sortBy(overlapping, function(v) {
            var i = intervalfn(v);
            return i.s;
        });

        overlapping.forEach(function(v1, i) {
            var i1 = intervalfn(v1);
            var handledoverlaps = [];
            for (var j = 0; j < i; j++) {
                if (overlap(i1, intervalfn(overlapping[j]))) {
                    handledoverlaps.push(overlapping[j]);
                }
            }
            var index = allocateindex(handledoverlaps);
            v1.index = index;
        });

        if (reverse) {
            for (let i = 0; i < Math.floor(overlapping.length / 2); i++) {
                let j = overlapping.length - 1 - i;
                let a = overlapping[i].index;
                overlapping[i].index = overlapping[j].index;
                overlapping[j].index = a;
            }
        }
    });

    return arr;
}

function groupsinquery() {
    return this.getAttribute('data-showdocs') in groupstate;
}
