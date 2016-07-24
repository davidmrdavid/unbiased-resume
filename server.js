// modules =================================================
var exec = require('child_process').exec;
var express        = require('express');
var app            = express();
var mongoose       = require('mongoose');
var bodyParser     = require('body-parser');
var methodOverride = require('method-override');
var multer         = require('multer');
var fs = require("fs");

app.engine('.html', require('ejs').__express);
app.set('views', __dirname + '/public');
app.set('view engine', 'html');


var storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, './uploads')
  },
  filename: function (req, file, cb) {
    cb(null, file.fieldname)
  }
})


var upload = multer({ storage: storage })


var port = process.env.PORT || 8080; // set our port
// mongoose.connect(db.url); // connect to our mongoDB database (commented out after you enter in your own credentials)

// get all data/stuff of the body (POST) parameters
app.use(bodyParser.json()); // parse application/json
app.use(bodyParser.json({ type: 'application/vnd.api+json' })); // parse application/vnd.api+json as json
app.use(bodyParser.urlencoded({ extended: true })); // parse application/x-www-form-urlencoded

app.use(methodOverride('X-HTTP-Method-Override')); // override with the X-HTTP-Method-Override header in the request. simulate DELETE/PUT
app.use(express.static(__dirname + '/public')); // set the static files location /public/img will be /img for users

app.get('/', function (req, res) {
  res.sendFile(__dirname + '/public/home.html');
});

app.get('/home', function (req, res) {
  res.sendFile(__dirname + '/public/home.html');
});

app.get('/recipients', function (req, res) {
  res.sendFile(__dirname + '/public/recipients.html');
});


app.post('/', upload.single("resume.pdf"), function(req,res){

  var cmd = 'python code.py '+ './'+req.file.path;
  exec(cmd, function(error, stdout, stderr) {
    console.log(stdout);

    fs.readFile('json_response', function (err, data) {
      if (err) {
          return console.error(err);
      }
      var contents = data.toString();
      var response = JSON.parse(contents);

      // Elmer, take it from here...
      console.log(response);


      // DAVID...

      res.sendFile(__dirname + "/public/view.html");
    });
  });


});

// start app ===============================================
app.listen(port);
exports = module.exports = app; 						// expose app
