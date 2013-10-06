var db = require('../lib/db'),
    _ = require('underscore');

/*
 * GET home page.
 */

exports.index = function(req, res) {
    var juris = [],
        indexes = {};

    db.forEach(function(key, record) {
        if (record.type === 'body') {
            var code = record.jurisdiction_code,
                jurisdiction;

            if (indexes[code] === undefined) {
                juris.push({
                    name: record.jurisdiction,
                    key: code,
                    count: 0
                });
                indexes[code] = juris.length - 1;
            }

            juris[indexes[code]].count++;
        }
    });

    juris.sort(function(a, b) {
        if (a.name === b.name) {
            return 0;
        } else {
            return a.name < b.name ? -1 : 1;
        }
    })
    res.render('index', {
        juris: juris
    });
};

exports.jurisdiction = function(req, res) {
    var bodies = [],
        name,
        jurisdiction = req.params.jurisdiction;

    db.forEach(function(key, record) {
        if (record.jurisdiction_code === jurisdiction) {
            name = name || record.jurisdiction;
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
        name: name,
        pageTitle: name,
        bodies: bodies
    });
};

exports.body = function(req, res) {
    var body,
        jurisdiction = req.params.jurisdiction,
        key = req.params.key;

    body = db.get(jurisdiction + '/' + key);

    if (body.parent_id) {
        body.parentBody = db.get(body.parent_id);
    }

    body.pageTitle = body.name + ' / ' + body.jurisdiction;

    res.render('body', body);
};

exports.bodyJSON = function(req, res) {
    var body,
        jurisdiction = req.params.jurisdiction,
        key = req.params.key;

    body = db.get(jurisdiction + '/' + key);
    res.send(200, body);
};
