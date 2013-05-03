var fs = require('fs');
var util = require('util');
var path = require('path');

var nunjucks = require('nunjucks');
var csv = require('csv');

var dataDirectory = path.join('..', 'data');

var env = new nunjucks.Environment(new nunjucks.FileSystemLoader('templates'));

function prepare() {
  if (fs.existsSync('build')) {
    deleteFolderRecursive('build');
  }
  fs.mkdirSync('build');
  fs.mkdirSync('build/css');
  fs.mkdirSync('build/js');
  fs.createReadStream(path.join('css', 'style.css'))
      .pipe(fs.createWriteStream(
          path.join('build', 'css', 'style.css')));
  fs.createReadStream(path.join('js', 'app.js'))
      .pipe(fs.createWriteStream(
          path.join('build', 'js', 'app.js')));
}

// read the contents of the data directory, include the name if it ends with ".csv"
var csvRegex = /\.csv/;
var dataFiles = fs.readdirSync(dataDirectory);
var countries = [];
for (var idx in dataFiles) {
  if (csvRegex.test(dataFiles[idx])) {
    countries.push(dataFiles[idx].replace(csvRegex, ''));
  }
}

function build() {
  var country;

  prepare();
  var index = [];
  for (var idx in countries) {
    country = countries[idx];
    index[country] = [];
    renderCountry(country, index, callback);
  }
  var count = 0;
  function callback() {
    count += 1;
    if (count === countries.length) { buildIndex({index: index, countries: countries}) }
  }
}

function buildIndex(data) {
  var html = env.getTemplate('index.html');
  var out = html.render(data);
  fs.writeFileSync(path.join('build', 'index.html'), out);
}

function renderCountry(country, index, cb) {
  fs.mkdirSync(path.join('build', country));
  var csvpath = path.join(dataDirectory, country + '.csv');
  csv().from(csvpath, {columns: true})
    .on('record', function(record, idx) {
      // key = eu/abcefg
      var slug = record['key'].split('/')[1]
      record['slug'] = slug;
      var destpath = path.join('build', country, slug);
      var destjson = destpath + '.json';
      destpath = destpath + '.html';
      var offset = country + '/' + slug + '.html';
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

function deleteFolderRecursive(path) {
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
}

build();
