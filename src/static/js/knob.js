/**
* Authored By: Andrew Hassan
* KNOB CLASS
*
* This class is used to emulate some of the jQuery knob control functionality.
*
* Params:
*		selector: The id of the html element you want the svg to be in.
*		value: The value (out of 100) you want the knob to represent.
*       delta: The amount of time in seconds to display
*		width: The width of the control.
*		height: The height of the control.
*		colors: The colors to use for the control. [Good color as hex, neutral color as hex, bad color as hex]
*
* Requires:
*       d3.js
*/
function Knob(selector, value, delta, width, height, label, colors,max,min) {
    
    this.value = ((value - min) /(max-min)) * 100
    this.selector = selector;
    this.width = width;
    this.height = height;
    this.label = label;
    this.delta = delta;

    if (typeof (colors) === "undefined") {
        this.colors = ["#e74c3c", "#f1c40f", "#2ecc71"];
    }
    else {
        this.colors = colors;
    }

    this.radius = Math.min(this.width, this.height) / 2;

    this.svg = d3.select(this.selector)
		.append("svg")
		.attr("class", "knob")
		.attr("width", this.width)
		.attr("height", this.height);

    this.pieSlice = function(d) {
        return [{ data: d, startAngle: -2 * Math.PI / 3, endAngle: (d / 100) * (4 * Math.PI / 3) - (2 * Math.PI / 3)}];
    };

    this.dataArc = d3.svg.arc()
		.innerRadius(0.5 * this.radius)
		.outerRadius(0.99 * this.radius);

    d3.select(this.selector).select(".knob")
		.data(this.pieSlice(100))
		.append("g")
		.attr("class", "backdrop")
		.append("path")
		.attr("d", this.dataArc)
		.attr("transform", "translate(" + this.width / 2 + ", " + this.height / 2 + ")")
		.attr("style", "fill:none;stroke:#888888;");

    this.dataSvg = d3.select(this.selector).select(".knob")
		.append("g")
		.attr("class", "data-knob")
		.attr("transform", "translate(" + (this.width / 2) + ", " + (this.height / 2) + ")");

    d3.select(this.selector).select(".knob")
        .append("g")
        .attr("class", "text");

    var tempC = this.colors;

    this.dataPath = this.dataSvg
		.selectAll("path")
		.data(this.pieSlice(this.value))
		.enter()
		.append("path")
		.attr("fill", function(d) {
		    if (d.data < 50) {
		        var i = d3.interpolateRgb(tempC[2], tempC[1]);
		        return i(2 * d.data / 100);
		    }
		    else {
		        var i = d3.interpolateRgb(tempC[1], tempC[0]);
		        return i(2 * (d.data - 50) / 100);
		    }
		})
		.attr("d", this.dataArc);

    this.textSvg = d3.select(this.selector).select(".text")
		.append("text")
		.attr("class", "backdrop-text")
		.attr("x", this.width / 2)
		.attr("y", 11 * this.height / 16)
		.attr("text-anchor", "middle")
		.attr("dy", "0.35em")
		.attr("dx", "0.1em")
        .attr("fill", "#555")
		.attr("style", "font-size:" + this.radius * 2 / 7 + "pt;")
		.text(this.delta.toFixed(2));

    this.textSvg = d3.select(this.selector).select(".text")
        .append("text")
        .attr("class", "backdrop-label")
        .attr("x", this.width / 2)
        .attr("y", this.height / 2 + this.radius / 2)
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .attr("style", "font-size:" + this.radius / 7 + "pt;")
        .text(this.label);

}

Knob.prototype.updateValue = function(newValue, delta,max,min) {
    /*if (newValue < 0) {
        return;
    }*/
    var old = this.pieSlice(this.value);
    var oldDelta = this.pieSlice(this.delta);
    this.value = ((newValue - min) /(max-min)) * 100
    
    this.delta = delta;
	var tempC = this.colors;
    var dataArc = this.dataArc;

    this.dataPath.data(this.pieSlice(this.value));
    this.dataPath
        .transition()
        .duration(1000)
        .attr("fill", function(d) {
            if (d.data < 50) {
                var i = d3.interpolateRgb(tempC[2], tempC[1]);
                return i(2 * d.data / 100);
            } else {
                var i = d3.interpolateRgb(tempC[1], tempC[0]);
                return i(2 * (d.data - 50) / 100);
            }
        })
        .attrTween("d", function(d, i, a) {
            var i = function(t) {
                return { data: d.data, startAngle: -2 * Math.PI / 3, endAngle: t * (d.endAngle - old[0].endAngle) + old[0].endAngle };
            };
            return function(t) { return dataArc(i(t)); };
        });

	var oldData = ((old[0].data)*(max-min))/100 + min;
    var temp = newValue - oldData;
    d3.select(this.selector).selectAll(".backdrop-text")
        .data([this.delta])
        .text(oldDelta.data)
        .transition()
        .duration(1000)
        .tween("text", function(d) {
        	console.log(d);
            var i = function(t) {
                return (oldData + temp*t).toFixed(2);
            };

            return function(t) {
                this.textContent = i(t);
            };
        });
};


function zeroPad(num, places) {
    var zero = places - num.toString().length + 1;
    return Array(+(zero > 0 && zero)).join("0") + num;
}