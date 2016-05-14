function autoannotate(selector) {
    var i = 0;
    var j = 0;
    var s = $(selector)
        // Don't touch pre-annotated elements.
        .filter(function() { return !this.hasAttribute('data-showdocs'); });

    s.each(function() {
        $(this).attr('data-showdocs', $(this).text().toLowerCase());
        i++;
    });

    s.filter(groupsinquery).each(function() {
        $(this).addClass('showdocs-decorate-back');
        j++;
    });

    console.log('added', i, 'groups to existing elements and decorated', j);
}
