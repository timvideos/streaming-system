// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:

(function(){

var sortLabel = function(a,b){
    if(a.label < b.label) {
        return -1;
    } else if (a.label > b.label) {
        return 1;
    } else {
        return 0;
    }
}


// Prepare the data as an Array of [X,Y] points for the bitrate and client graphs.
var prepareData = function(track_data) {
    var bitrate_data = [];
    var client_data = [];
    for(var i in track_data){
        var point_data = track_data[i];
        bitrate_data.push([
            point_data.lastseen * 1000,                 // JS needs timestamps in ms
            point_data.overall_bitrate / (1024 * 1024)  // convert to mbps
        ])
        client_data.push([
            point_data.lastseen * 1000,                 // JS needs timestamps in ms
            point_data.overall_clients
        ])
    }
    return {
        'bitrate_data': bitrate_data,
        'client_data': client_data
    };
}

var drawPlot = function(raw_data) {

    var bitrate_graph_data = [];
    var client_graph_data = [];

    // Graph options for filled line time series graphs.
    var graph_options = {
        series: {
            stack: true,
            lines: {
                show: true,
                fill: true
            }
        },
        legend: {
            position: 'nw'
        },
        xaxis: {
            mode: "time",
            timeformat: "%y/%m/%d %h:%M",
            // Set the time range to be within the past 1 hour.
            min: (new Date()).getTime() - (1 * 60 * 60 * 1000),
            max: (new Date()).getTime()
        }
    };

    for(var track_name in raw_data){
        var data_to_graph = prepareData(raw_data[track_name]);
        bitrate_graph_data.push({
            data: data_to_graph['bitrate_data'],
            label: track_name,
        })
        client_graph_data.push({
            data: data_to_graph['client_data'],
            label: track_name,
        })
    }

    // Ensure the groups are sorted alphabetically.
    bitrate_graph_data.sort(sortLabel);
    client_graph_data.sort(sortLabel);

    // Call jQuery.flot with the data and options.
    $.plot($("#bitrate-stats-graph"), bitrate_graph_data, graph_options);
    $.plot($("#client-stats-graph"), client_graph_data, graph_options);
}

var doing_refresh = false;

var startGraphRefresh = function() {
    // Get the data for the graph from the server.
    doing_refresh = true;
    $.getJSON('/tracker/overall-stats.json', {}, function(response){
        drawPlot(response);
        doing_refresh = false;
    })
};

window.plot_stats = function() {
    startGraphRefresh();
    setInterval(function(){
        if(!doing_refresh){
            startGraphRefresh();
        }
    }, 10*1000)
    
}

}).call(this)
