// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:

(function(){

var Graph = (function() {

    function Graph(graph_dict) {
        this.id = 'graph-' + ((new Date()).getTime()).toString();
        this.title = graph_dict.title
        this.raw_series = graph_dict.series;
        this.raw_series.sort(sortLabel)

    }

    Graph.prototype.render = function() {
        return "<h2>" + this.title + "</h2>" + "<div id='" + this.id + "' class='graph'></div>";
    };

    Graph.prototype.getEl = function() {
        return $('#' + this.id);
    }

    // Graph.prototype.getSeries = function() {
    //     series
    //     for(var i in this.raw_series){

    //     }
    // };

    return Graph;
})();
 

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


// // Prepare the data as an Array of [X,Y] points for the bitrate and client graphs.
// var prepareData = function(track_data) {
//     var bitrate_data = [];
//     var client_data = [];
//     for(var i in track_data){
//         var point_data = track_data[i];
//         bitrate_data.push([
//             point_data.lastseen * 1000,                 // JS needs timestamps in ms
//             point_data.overall_bitrate / (1024 * 1024)  // convert to mbps
//         ])
//         client_data.push([
//             point_data.lastseen * 1000,                 // JS needs timestamps in ms
//             point_data.overall_clients
//         ])
//     }
//     return {
//         'bitrate_data': bitrate_data,
//         'client_data': client_data
//     };
// }

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
                from: annotation.date * 1000,
                to: annotation.date * 1000
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
    var graph_wrapper = $('#stats-graph-wrapper')
    for(var i = 0; i < source_graphs.length; i++){
        var graph = new Graph(source_graphs[i]);
        graph_wrapper.append(graph.render());
        var plot = $.plot(graph.getEl(), graph.raw_series, graph_options);
    }

    // // Ensure the groups are sorted alphabetically.
    // bitrate_graph_data;
    // client_graph_data.sort(sortLabel);

    // // Call jQuery.flot with the data and options.
    // var bitrate_plot = $.plot($("#bitrate-stats-graph"), bitrate_graph_data, graph_options);
    // var client_plot = $.plot($("#client-stats-graph"), client_graph_data, graph_options);
    // plots = [bitrate_plot, client_plot];
    // drawAnnotations(response.annotations);
}

var drawAnnotations = function(annotations){
    console.log(annotations[0].date)
    for(var i in plots){
        var plot = plots[i];
        var graph_el = plot.getPlaceholder();
        for(var j in annotations){
            var annotation = annotations[j];
            var o = plot.pointOffset({ x: annotation.date * 1000, y: 50});
            graph_el.append('<div style="position:absolute;left:' + (o.left + 4) + 'px;top:' + o.top + 'px;color:#666;">'+ annotation.label + '</div>')

        }
    }
}

var startGraphRefresh = function() {
    // Get the data for the graph from the server.
    doing_refresh = true;
    $.getJSON('/tracker/overall-stats.json', {}, function(response){
        drawPlots(response);
        doing_refresh = false;
    })
};

var startInterval = function() {
    refresh_interval = setInterval(function(){
        if(!doing_refresh){
            startGraphRefresh();
        }
    }, 10*1000)
}

window.plot_stats = function() {
    startGraphRefresh();
    startInterval();
}

$('select').live('change', function(){
    view_range = $(this).val();
    startGraphRefresh();
});

$('input[type="checkbox"]').live('click', function(e){
    var checkbox = $(this);
    setTimeout(function(){
        if(checkbox.is(':checked')){
            console.log('checked')
            startInterval();
        } else {
            console.log('unchecked')
            clearInterval(refresh_interval);
        }
    },1)
});

}).call(this)
