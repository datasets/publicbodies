var nunjucks = require('nunjucks');
var fs = require('fs');

if (!fs.existsSync('build')) {
  fs.mkdirSync('build');
}

var env = new nunjucks.Environment(new nunjucks.FileSystemLoader('templates'));
var tmpl = env.getTemplate('view.tmpl');
var out = tmpl.render({ title: "james" });
fs.writeFileSync('build/index.html', out);
