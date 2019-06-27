$('.show_area_info').hover(function () {
    $(this).css({
        'background-color': '#AAAAAA'
    });
}, function () {
    $(this).css({
        'background-color': '#CCCCCC'
    });
});

$('.show_area_a').tooltip({
    position: {
        my: "right top",
        at: "left bottom"
    },
    show: {
        effect: "slideDown",
        delay: 250
    },
    hide: {
        effect: "explode",
        delay: 250
    }
})