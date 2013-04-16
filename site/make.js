var fs = require('fs');
var util = require('util');
var path = require('path');

var nunjucks = require('nunjucks');
var csv = require('csv');


var env = new nunjucks.Environment(new nunjucks.FileSystemLoader('templates'));

function prepare() {
  if (fs.existsSync('build')) {
    deleteFolderRecursive('build'); 
  }
  fs.mkdirSync('build');
}

var countries = [ 'eu', 'gb', 'de' ];
var countries = [ 'eu' ];


// url structure
// /{country}/{id}.html
// /{country}/{id}.json

function build() {
  prepare();
  var index = {};
  for (idx in countries) {
    country = countries[idx];
    index[country] = [];
    fs.mkdirSync(path.join('build', country));
    csvpath = path.join('..', 'data', country + '.csv');
    csv().from(csvpath, {columns: true})
      .on('record', function(record, idx) {
        // key = eu/abcefg, slug = ten_tea
        destpath = path.join('build', country, record['slug'] + '.html');
        index[country].push(country + '/' + record['slug'] + '.html');
        templateHtml(record, destpath);
      });
  }
}

function templateHtml(data, path) {
  var html = env.getTemplate('view.html');
  var out = html.render(data);
  fs.writeFileSync(path, out);
}

deleteFolderRecursive = function(path) {
  var files = [];
  if( fs.existsSync(path) ) {
    files = fs.readdirSync(path);
    files.forEach(function(file,index){
      var curPath = path + "/" + file;
      if(fs.statSync(curPath).isDirectory()) { // recurse
        deleteFolderRecursive(curPath);
      } else { // delete file
        fs.unlinkSync(curPath);
      }
    });
    fs.rmdirSync(path);
  }
};

build();
