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
                    key: code.toLowerCase(),
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
    });

    res.render('index', {
        juris: juris
    });
};

/*
 * GET list of bodies in jurisdiction
 */
exports.jurisdiction = function(req, res) {
    var bodies = [],
        name,
        jurisdiction = req.params.jurisdiction.toUpperCase();

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
        code: jurisdiction,
        name: name,
        pageTitle: name,
        bodies: bodies
    });
};

/*
 * GET single public body
 */
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

/*
 * GET single public body as JSON
 */
exports.bodyJSON = function(req, res) {
    var jurisdiction = req.params.jurisdiction,
        key = req.params.key;

    function toJSON(body, getParent) {
        var json = _.omit(body, 'type', 'jurisdiction', 'slug');

        _.each(json, function(value, key) {
            if (value == '') {
                delete json[key];
            }
        });

        if (json.url) {
            json.links = [{url: json.url}];
            delete json.url;
        }

        if (json.source_url) {
            json.sources = [{url: json.source_url}];
            delete json.source_url;
        }

        if (json.abbreviation) {
            json.other_names = [{name: json.abbreviation}];
            delete json.abbreviation;
        }

        if (json.email || json.address) {
            json.contact_details = [];
        }

        if (json.email) {
            json.contact_details.push({
                label: 'Email',
                type: 'email',
                value: json.email
            });
            delete json.email;
        }

        if (json.address) {
            json.contact_details.push({
                label: 'Address',
                type: 'address',
                value: json.address
            });
            delete json.address;
        }

        if (getParent && json.parent_id) {
            json.parent = toJSON(db.get(json.parent_id), false);
        }

        return json;
    }

    res.json(toJSON(db.get(jurisdiction + '/' + key), true));
};

/*
 * GET search page
 */
exports.search = function(req, res) {
    res.render('search');
};
