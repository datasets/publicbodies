var nunjucks = require('nunjucks');
var fs = require('fs');

if (!fs.existsSync('build')) {
  fs.mkdirSync('build');
}

var env = new nunjucks.Environment(new nunjucks.FileSystemLoader('templates'));
var html = env.getTemplate('view.html');
var out = html.render({ title: "james" });
fs.writeFileSync('build/index.html', out);
