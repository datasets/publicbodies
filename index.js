/**
 * Module dependencies.
 */

var express = require('express'),
    errorhandler = require('errorhandler'),
    favicon = require('serve-favicon'),
    morgan = require('morgan'),
    lessMiddleware = require('less-middleware'),
    routes = require('./routes'),
    http = require('http'),
    path = require('path'),
    app = express(),
    db = require('./lib/db');

// all environments
app.set('port', process.env.PORT || 3000);
app.set('views', __dirname + '/views');
app.set('view engine', 'pug');
app.use(favicon(path.join(__dirname, 'public', 'images', 'favicon.ico')));
app.use(morgan('dev'));
app.use(lessMiddleware(__dirname + '/public'));
app.use(express.static(path.join(__dirname, 'public')));

// development only
if ('development' === process.env.NODE_ENV) {
    app.use(errorhandler());
}
else { // production only
    // handle https redirect
    function ensureSecure(req, res, next){
        if(req.secure){
        // OK, continue
        return next();
        };
        res.redirect('https://' + req.hostname + req.url);
    }
    app.all('*', ensureSecure);
}

app.get('/', routes.index);
app.get('/search', routes.search);
app.get('/:jurisdiction', routes.jurisdiction);
app.get('/:jurisdiction/:key.json', routes.bodyJSON);
app.get('/:jurisdiction/:key', routes.body);

http.createServer(app).listen(app.get('port'), function(){
    console.log('Express server listening on port ' + app.get('port'));
});
