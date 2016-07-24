var mongoose = require('mongoose');

var Schema = mongoose.Schema;

mongoose.connect('mongodb://localhost/myTestDB');
var db = mongoose.connection;

db.on('error', function (err) {
console.log('connection error', err);
});

function httpGet(url) {
  var xmlHttp = new XMLHtppRequest();
  xmlHttp.open("GET", url, false);
  xmlHttp.send(null);
  return xmlHttp.responseText;
}

db.once('open', function () {
  console.log('connected.');

  var url = "http://www.unbiasedResume.com/json=true";

  var userSchema = new Schema({
  firstName : String,
  lastName : String,
  oldResumePath : String,
  newResumePath : String,
  linterScore : Number,
  githubUsername: String,
  school : String,
  email : String
  });

  var User = mongoose.model('User', userSchema);

  // var listOfUsers = httpGet(url); // list of json objects

 var listOfUsers = [{
      firstName : "Elmer",
      lastName : "Diaz",
      oldResumePath : "okay coo",
      newResumePath : "okay cooler",
     linterScore : 5,
    githubUsername : "elmerd",
    school : "UC Berkeley",
      email : "elmerd@berkeley.edu"
    }, {firstName : "Elm",
    lastName : "D",
    oldResumePath : "okay cool",
    newResumePath : "okay coolerer",
    linterScore : 7,
    githubUsername : "elmerd1",
    school : "UC Berkeleyy",
    email : "elmerd@berkeleyy.edu"}];

  var user1 = new User(listOfUsers[0]);
  var user2 = new User(listOfUsers[1]);

  user1.save(function(err) {
    if (err) return console.error(err);
    console.dir(user1);
  });
  user2.save(function(err) {
    if (err) return console.error(err);
    console.dir(user2);
  });

});
