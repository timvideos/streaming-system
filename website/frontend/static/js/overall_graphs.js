// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:

(function(){

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
            // Set the time range to be within the past 1 hour.
            min: min_time,
            max: max_time
        },
        grid: {
            markings: markings
        }
    };

    plots = [];
    var graph_wrapper = $('#stats-graph-wrapper');
    graph_wrapper.empty();
    for(var i = 0; i < source_graphs.length; i++){
        var graph = new Graph(source_graphs[i]);
        graph_wrapper.append(graph.render());
        var plot = $.plot(graph.getEl(), graph.raw_series, graph_options);
        var graph_el = plot.getPlaceholder();
        for(var j in annotations){
            var annotation = annotations[j];
            console.log(annotation);
            var o = plot.pointOffset({ x: annotation.x, y: 50});
            graph_el.append('<div style="position:absolute;left:' + (o.left + 4) + 'px;top:' + o.top + 'px;color:#666;">'+ annotation.label + '</div>')
        }
    }

    // drawAnnotations(annotations);
}


var startGraphRefresh = function() {
    // Get the data for the graph from the server.
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

$('select').live('change', function(){
    view_range = $(this).val();
    startGraphRefresh();
});

$('input[type="checkbox"]').live('click', function(e){
    var checkbox = $(this);
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
