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
    res.render('jurisdiction', {
        bodies: bodies
    });
};
