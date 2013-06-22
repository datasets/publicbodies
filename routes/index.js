var db = require('../lib/db'),
    _ = require('underscore');

/*
 * GET home page.
 */

exports.index = function(req, res) {
    var juris = {};

    db.forEach(function(key, record) {
        if (record.type === 'body') {
            var code = record.jurisdiction_code;

            juris[code] = juris[code] || 0;

            juris[code]++;
        }
    });
    res.render('index', {
        juris: juris
    });
};

exports.jurisdiction = function(req, res) {
    var bodies = [],
        jurisdiction = req.params.jurisdiction;

    db.forEach(function(key, record) {
        if (record.jurisdiction_code === jurisdiction) {
            bodies.push(record);
        }
    });
    bodies.sort(function(a, b) {
        if (a.title === b.title) {
            return 0;
        } else {
            return a.title < b.title ? -1 : 1;
        }
    });
    res.render('jurisdiction', {
        code: jurisdiction.toUpperCase(),
        bodies: bodies
    });
};
