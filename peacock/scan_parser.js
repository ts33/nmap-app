let _ = require('underscore');
let async = require('async');
let parseString = require('xml2js').parseString;
let pr = require('./port_record.js');


// parses all records, accepts an array of scan results
function parseAllScans(scans, callback){

  functionList = scans.map(function(data){
    return function (callback){
      parseScanEntry(data, callback);
    }
  })

  async.series(functionList, function (err, results) {
    // console.log(results.length);
    output = transposeScanData(results);
    callback(null, output);
  });

}


// accepts an array of scan data
function transposeScanData(scanData){
  transposedData = {}

  for (var portGrouping of scanData){
    for (var portRecord of portGrouping){
      uniqueIdentifier = `${portRecord.hostName}_${portRecord.portId}`

      // portId already exists
      if (uniqueIdentifier in transposedData) {
        // add the four columns state, reason, timestr and name if not empty
        transposedElement = transposedData[uniqueIdentifier]
        transposedElement[[`${portRecord.scanType}_state`]] = portRecord.portState
        transposedElement[[`${portRecord.scanType}_reason`]] = portRecord.portReason
        transposedElement[[`${portRecord.scanType}_completed_time`]] = portRecord.completedTime

        if (portRecord.portName != null) {
          transposedElement['name'] = portRecord.portName
        }

        transposedData[uniqueIdentifier] = transposedElement

      // portId doesnt exist
      } else {
        transposedElement = {
          'hostname': portRecord.hostName,
          'protocol': portRecord.portProtocol,
          'port': portRecord.portId,
          'name': portRecord.portName,
          [`${portRecord.scanType}_state`]: portRecord.portState,
          [`${portRecord.scanType}_reason`]: portRecord.portReason,
          [`${portRecord.scanType}_completed_time`]: portRecord.completedTime
        }
        transposedData[uniqueIdentifier] = transposedElement
      }

    }
  }

  arrayData = []
  for (var key in transposedData) {
    if (transposedData.hasOwnProperty(key)) {
      arrayData.push(transposedData[key]);
    }
  }

  return arrayData;
}


function parseScanEntry(text, callback) {

  parseString(text, function (err, result) {
    allPortRecords = []
    data = result.nmaprun

    scaninfo = data.scaninfo[0].$
    scanType = scaninfo.type
    scanProtocol = scaninfo.protocol
    // console.log(`numservices: ${scaninfo.numservices}`)
    completedTime = data.runstats[0].finished[0].$.timestr

    hosts = data.host
    for (var host of hosts){
      allPortIds = generatePortIds(scaninfo.services)

      hostname = host.hostnames[0].hostname[0].$.name
      // console.log(`hostname: ${hostname}`)
      ports = host.ports[0]

      if (ports.port != undefined) {
        for (var port of ports.port){
          portId = parseInt(port.$.portid)
          portState = port.state[0].$.state
          portReason = port.state[0].$.reason
          portName = port.service[0].$.name

          // create a port record
          portRecord = new pr.PortRecord(hostname, scanType, scanProtocol, portId, portState, portReason, portName, completedTime);
          allPortRecords.push(portRecord);
          // delete all found port from the array
          allPortIds = _.without(allPortIds, portId);

        }
      }

      // for all other ports not found, populate supporting information from extra ports
      extraPortsState = ports.extraports[0].$.state
      extraPortsReason = ports.extraports[0].extrareasons[0].$.reason

      for (var portId of allPortIds){
        portRecord = new pr.PortRecord(hostname, scanType, scanProtocol, portId, extraPortsState, extraPortsReason, null, completedTime);
        allPortRecords.push(portRecord);
      }
      // console.log(`port records generated for ${hostname} : ${allPortRecords.length}`)
    }

    // console.log(`Total port records generated for ${scanType} : ${allPortRecords.length}`)
    callback(null, allPortRecords);
  });

}


function generatePortIds(services){
  allPortIds = []
  portRanges = services.split(',');

  for (var portRange of portRanges){
    if (portRange.includes('-')){
      portLimits = portRange.split('-');
      lowerLimit = parseInt(portLimits[0])
      upperLimit = parseInt(portLimits[1])
      fullRange = _.range(lowerLimit, upperLimit+1);
      allPortIds.push.apply(allPortIds, fullRange)
    }else {
      allPortIds.push(parseInt(portRange));
    }
  }

  // console.log(`number of port ids generated : ${allPortIds.length}`)
  return allPortIds
}


function printAttributes(obj){
  for (var k in obj) {
    if (obj.hasOwnProperty(k)) {
      console.log(`attribute ${k} has value ${obj[k]}`)
    }
  }
}


module.exports.parseAllScans = parseAllScans;
