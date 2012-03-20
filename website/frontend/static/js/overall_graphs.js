// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:

(function(){

// Class that holds the actual graph data. Assigns itself an ID based on the
// current timestamp and can generate the necessary markup for the plot.
var Graph = (function() {

    function Graph(graph_dict) {
        this.id = 'graph-' + ((new Date()).getTime()).toString();
        this.title = graph_dict.title
        this.raw_series = graph_dict.series;
        this.raw_series.sort(sortLabel)
    };

    Graph.prototype.render = function() {
        return "<h2>" + this.title + "</h2>" + "<div id='" + this.id + "' class='graph'></div>";
    };

    Graph.prototype.getEl = function() {
        return $('#' + this.id);
    };

    return Graph;
})();


// Simple "class" for managing the loading spinner.
var Spinner = (function() {

    var spin_interval, el, container, rotation;

    function Spinner(graph_dict) {
        el = $('#spinner');
        container = $('#graph-loader');
        rotation = 0;
    };

    function rotate() { 
        var prefixes = ['-webkit-','-moz-','-ms-',''];
        rotation += 180;
        for(var i in prefixes) {
            var prefix = prefixes[i];
            el.css(prefix + 'transform','rotate('+ rotation.toString() + 'deg)')
        }
    };

    Spinner.prototype.start = function() {
        this.show();
        clearInterval(spin_interval);
        spin_interval = setInterval(rotate,500)
    };

    Spinner.prototype.stop = function() {
        this.hide();
        clearInterval(spin_interval);
        rotation = -180;
        rotate();
    };

    Spinner.prototype.hide = function() {
        container.css('visibility','hidden');
    }

    Spinner.prototype.show = function() {
        container.css('visibility','visible');
    }

    return Spinner;
})();


var spinner;
var plots = [];
var doing_refresh = false;
var view_range = 10 // minutes;
var refresh_interval;

var sortLabel = function(a,b){
    if(a.label < b.label) {
        return -1;
    } else if (a.label > b.label) {
        return 1;
    } else {
        return 0;
    }
}

var drawPlots = function(response) {
    var source_graphs = response.graphs;
    var annotations = response.annotations;

    var now = (new Date()).getTime();
    var markings = [{
        color: '#F00',
        lineWidth: 2,
        xaxis: {
            from: now,
            to: now
        }
    }]

    for(var i in annotations){
        var annotation = annotations[i];
        markings.push({
            color: '#000',
            lineWidth: 1,
            xaxis: {
                from: annotation.x,
                to: annotation.x
            }
        })
    }

    // Graph options for filled line time series graphs.
    // The graph shows now plus one minute.
    var max_time = (new Date()).getTime() + 60000;
    var min_time = max_time - (view_range * 60 * 1000);
    var graph_options = {
        series: {
            stack: true,
            lines: {
                show: true,
                fill: true,
                lineWidth: 0
            }
        },
        legend: {
            position: 'nw'
        },
        xaxis: {
            mode: "time",
            timeformat: "%y/%m/%d %h:%M",
            // Set the time range to be within the specified limits.
            min: min_time,
            max: max_time
        },
        grid: {
            markings: markings
        }
    };

    plots = [];

    // Grab the graph wrapper from the document and empty it.
    var $graph_wrapper_el = $('#stats-graph-wrapper');
    $graph_wrapper_el.empty();

    // Iterate over the incoming graphs, adding the elements created by the Graph
    // class to the graph wrapper, plotting the graph, and adding any annotations.
    for(var i in source_graphs){
        var graph = new Graph(source_graphs[i]);
        $graph_wrapper_el.append(graph.render());
        var plot = $.plot(graph.getEl(), graph.raw_series, graph_options);
        var $graph_el = plot.getPlaceholder();

        for(var j in annotations){
            var annotation = annotations[j];
            var o = plot.pointOffset({ x: annotation.x, y: 50});
            $graph_el.append(
                '<div style="'
                + 'position:absolute;'
                + 'left:' + (o.left + 4) + 'px;'
                + 'top:' + o.top + 'px;'
                + 'color:#666;'
                + '">'
                + annotation.label + '</div>'
            )
        }
    }

}


var startGraphRefresh = function() {
    spinner.start();
    doing_refresh = true;
    $.getJSON('/tracker/overall-stats.json', {
        range: view_range
    }, function(response){
        drawPlots(response);
        doing_refresh = false;
        spinner.stop();
    })
};

var startInterval = function() {
    startGraphRefresh();
    clearInterval(refresh_interval);
    refresh_interval = setInterval(function(){
        if(!doing_refresh){
            startGraphRefresh();
        }
    }, 10*1000)
}

// Whenever the view-range dropdown is changed, set the new view-range and
// refresh the graphs.
$('select').live('change', function(){
    view_range = $(this).val();
    startGraphRefresh();
});

// Whenever the auto-refresh checkbox is clicked, toggle the interval that
// triggers the graph refreshing.
$('input[type="checkbox"]').live('click', function(e){
    var checkbox = $(this);

    // Use a timeout so the click event completes first and the checked state
    // can be read correctly.
    setTimeout(function(){
        if(checkbox.is(':checked')){
            startInterval();
        } else {
            clearInterval(refresh_interval);
        }
    },1)
});


$(document).ready(function(){
    spinner = new Spinner();
    startInterval();
});

}).call(this)
