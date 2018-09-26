/**
 * Select2 Chinese translation
 */
(function ($) {
    "use strict";
    $.extend($.fn.select2.defaults, {
        formatNoMatches: function () { return "\u6ca1\u6709\u627e\u5230\u5339\u914d\u9879"; },
        formatInputTooShort: function (input, min) { var n = min - input.length; return "\u8bf7\u518d\u8f93\u5165" + n + "\u4e2a\u5b57\u7b26";},
        formatInputTooLong: function (input, max) { var n = input.length - max; return "\u8bf7\u5220\u6389" + n + "\u4e2a\u5b57\u7b26";},
        formatSelectionTooBig: function (limit) { return "\u4f60\u53ea\u80fd\u9009\u62e9\u6700\u591a" + limit + "\u9879"; },
        formatLoadMore: function (pageNumber) { return "\u52a0\u8f7d\u7ed3\u679c\u4e2d..."; },
        formatSearching: function () { return "\u641c\u7d22\u4e2d..."; }
    });
})(jQuery);
