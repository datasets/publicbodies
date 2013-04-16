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
  fs.mkdirSync('build/css');
  fs.createReadStream(path.join('css', 'style.css'))
      .pipe(fs.createWriteStream(
          path.join('build', 'css', 'style.css')));
}

var countries = [ 'eu', 'gb', 'de' ];
// var countries = [ 'eu' ];

// url structure
// /{country}/{id}.html
// /{country}/{id}.json

function build() {
  prepare();
  var index = [];
  for (idx in countries) {
    country = countries[idx];
    index[country] = [];
    renderCountry(country, index, callback);
  }
  var count = 0;
  function callback() {
    count += 1;
    if (count == countries.length) { buildIndex({index: index, countries: countries}) }
  }
}

function buildIndex(data) {
  var html = env.getTemplate('index.html');
  var out = html.render(data);
  fs.writeFileSync(path.join('build', 'index.html'), out);
}

function renderCountry(country, index, cb) {
  fs.mkdirSync(path.join('build', country));
  csvpath = path.join('..', 'data', country + '.csv');
  csv().from(csvpath, {columns: true})
    .on('record', function(record, idx) {
      // key = eu/abcefg, slug = ten_tea
      destpath = path.join('build', country, record['slug']);
      destjson = destpath + '.json';
      destpath = destpath + '.html';  
      var offset = country + '/' + record['slug'] + '.html';
      index[country].push({title: record['title'], url: offset});
      templateHtml(record, destpath);
      fs.writeFileSync(destjson, JSON.stringify(record, null, 2));
    })
    .on('end', function() {
      cb();
    })
    ;
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
