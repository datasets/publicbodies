var async = require('async'),
    Dirty = require('dirty'),
    db = new Dirty(),
    csv = require('csv'),
    fs = require('fs'),
    path = require('path');

module.exports = db;

function onError(err) {
    if (err) {
        console.log(err);
        process.exit(1);
    }
}

function initialise() {
    fs.readdir('data', function(err, files) {
        if (err) {
            onError(err);
        } else {
            async.each(files, processFile);
        }
    }, onError);
}

function processFile(file, callback) {
    var count = 0;

    if (/\.csv$/.test(file)) {
        console.log("Processing %s...", file);
        csv().from(path.resolve('data', file), {
            columns: true
        }).on('record', function(record) {
            var key = record.key;
                tokens = key.split('/');

            record.jurisdiction_code = tokens[0];
            record.slug = tokens[1];
            record.type = 'body';
            db.set(key, record);
            count++;
        }).on('end', function() {
            console.log("Added %d bodies from %s", count, file);

            callback();
        });
    } else {
        callback();
    }
}

initialise();
