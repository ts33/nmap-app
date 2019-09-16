const {Pool} = require('pg');


let getLatestScanRecords = 'SELECT id, scan_name, content FROM scans ' +
  'WHERE id IN (SELECT max(id) FROM scans GROUP BY scan_name);'


function connectDb(username, password, host, port, db) {
 return new Pool({
   connectionString: constructDbUrl(username, password, host, port, db)
 });
}


function constructDbUrl(username, password, host, port, db){
  return `postgresql://${username}:${password}@${host}:${port}/${db}`
}


function read(pool, callback) {

  pool.query(getLatestScanRecords, (err, res) => {
    if (err) {
      console.log(err.stack);
      callback(err, null);
    } else {
      callback(null, extractScan(res.rows));
    }
  });

}


function extractScan(res){
  scans = []
  for (var obj of res){
    scans.push(obj.content)
  }

  return scans
}


module.exports.connectDb = connectDb;

module.exports.read = read;
