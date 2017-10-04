let fs = require('fs');
let path = require('path');
const express = require('express');
let dbHelper = require('./db_helper.js');
let scanParser = require('./scan_parser.js');


const pool = dbHelper.connectDb(
  process.env.POSTGRES_USERNAME,
  process.env.POSTGRES_PASSWORD,
  process.env.POSTGRES_HOST,
  process.env.POSTGRES_PORT,
  process.env.POSTGRES_DB
);
const port = process.env.PEACOCK_PORT;
const app = express();
app.set('view engine', 'pug')
app.use(express.static(path.join(__dirname, './views')));


app.get('/health', function(req, res) {
  res.statusCode = 200;
  res.send('Thank you, I am healthy');
});


app.get('/', function (req, res, next) {
  readAndSaveScanData(function(err){
    if (err != null){
      res.render('loading', { title: 'Home' })
    } else {
      res.render('homepage', { title: 'Home' })
    }
  });
})


app.listen(port, function() {
  console.log(`App listening on port ${port}!`);
});


// read the most recent scan records
function readAndSaveScanData(callback){

  dbHelper.read(pool, function(err, scans){
    if (err != null || scans == null) {
      callback(err);
    } else {
      scanParser.parseAllScans(scans, function(err, res){
        json = JSON.stringify(res);
        fs.writeFile('views/data/output.json', json, 'utf8', function(){
          callback();
        });
      });
    }
  });

}
