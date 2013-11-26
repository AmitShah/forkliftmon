(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['sensor_template'] = template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression;


  buffer += "<div class=\"featurette\" id=\"featurette_";
  if (stack1 = helpers.id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\">\n	<img class=\"featurette-image img-circle\" alt=\"512x512\" src=\"";
  if (stack1 = helpers.imgSrc) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.imgSrc; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" style=\"width: 175px; height: 175px;\">		\n	<h2 class=\"featurette-heading\">";
  if (stack1 = helpers.name) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.name; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + ", <span class=\"text-muted\">";
  if (stack1 = helpers.area) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.area; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</span></h2>\n	<div class=\"featurette-data\">\n		<span style=\"font-size: 31.5pt;\">";
  if (stack1 = helpers.lastReportedTime) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.lastReportedTime; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</span>\n	</div>\n	<div class=\"featurette-data\">\n		<span style=\"font-size: 31.5pt;\">";
  if (stack1 = helpers.lastReportedSpeed) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.lastReportedSpeed; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</span>\n	</div>\n</div>";
  return buffer;
  });
})();