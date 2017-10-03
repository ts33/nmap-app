let chai = require('chai');
let fs = require('fs');
let scanParser = require('../scan_parser.js');
let expectedParsedResult = require('./files/expected.js');
let assert = chai.assert;

let testFileDir = 'test/files'


suite('Scan Parser', function() {

  test('should parse scan results into table', function(done) {
    ackScan = fs.readFileSync(`${testFileDir}/ack.xml`, 'utf8');
    nullScan = fs.readFileSync(`${testFileDir}/null.xml`, 'utf8');
    synScan = fs.readFileSync(`${testFileDir}/syn.xml`, 'utf8');
    xmasScan = fs.readFileSync(`${testFileDir}/xmas.xml`, 'utf8');

    allScanData = [ackScan, nullScan, synScan, xmasScan]

    outputData = scanParser.parseAllScans(allScanData, function(err, res){
      assert.equal(res.length, 100);
      assert.deepEqual(res, expectedParsedResult.expectedScan);
      done();
    });
  });
  
});
