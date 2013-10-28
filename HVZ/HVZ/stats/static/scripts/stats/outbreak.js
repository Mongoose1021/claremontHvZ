$(function () {
    "use strict";

    $.getJSON(
        '/status/json/poptimeseries.json',
        function(data, status, jqXHR) {
            console.log("successful stat GET");
            console.log(data);

            var $population = $("#population_time_series");
            var population_options = {
                xaxis: {
                    mode: "time",
                    timezone: "browser",
                },
            };

            $.plot($population, data, population_options);
        }
    );

    $.getJSON(
        '/status/json/taghistogram.json',
        function(data, status, jqXHR) {
            console.log("successful stat GET");
            console.log(data);

            var $tag_histogram = $("#tag_histogram");
            var tag_histogram_options = {
                bars: {show: true},
                 xaxis: {
                     mode: "time",
                     timezone: "browser",
                 },
            };

            $.plot($tag_histogram, data, tag_histogram_options);
        }
    );

    $('.noscript').remove();
    $('.scriptonly').show();
});
