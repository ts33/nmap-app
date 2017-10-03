'use strict';

class PortRecord{

 constructor(hostName, scanType, portProtocol, portId, portState, portReason, portName, completedTime){
    this.hostName = hostName;
    this.scanType = scanType;
    this.portProtocol = portProtocol;
    this.portId = portId;
    this.portState = portState;
    this.portReason = portReason;
    this.portName = portName;
    this.completedTime = completedTime;
 }

}

module.exports.PortRecord = PortRecord;
