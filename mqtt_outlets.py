#!/bin/env python

import paho.mqtt.client as mqtt
import outlets
import argparse
import os
import json

connection_status = {
1 : "Connection Refused: Incorrect Protocol Version",
2 : "Connection Refused: Invalid Client Identifier",
3 : "Connection Refused: Server Unavailable",
4 : "Connection Refused: Bad Usermane or Password",
5 : "Connection Refused: Not Authorized"
}


def to_bool(value):
    """
    Converts 'something' to boolean. Raises exception if it gets a string it doesn't handle.
    Case is ignored for strings. These string values are handled:
      True: 'True', "1", "TRue", "yes", "y", "t","On"
      False: "", "0", "faLse", "no", "n", "f", "OFf"
    Non-string values are passed to bool.
    """
    if type(value) == type(''):
        if value.lower() in ("yes", "y", "true",  "t", "1", "on"):
            return True
        if value.lower() in ("no",  "n", "false", "f", "0", "", "off"):
            return False
        raise Exception('Invalid value for boolean conversion: ' + value)
    return bool(value)

class OutletMQTTClient(mqtt.Client):
    def __init__(self,config_block,listen_mode=True):
        super(OutletMQTTClient,self).__init__()

        def on_connect(client,userdata,rc):
            if rc == 0:
                client.connected(userdata)
            elif rc in connection_status.keys():
                print(connection_status[rc])
            else:
                print("Unknown Server Error: ",rc)

        self.config_block = config_block
        self.listen_mode = listen_mode
        self.on_connect = on_connect

    def connect(self):
        print("Connecting...")
        return super(OutletMQTTClient,self).connect(
                self.config_block['broker'],
                port=self.config_block['port'], 
                keepalive=60
                )


class OutletMQTTClientListener(OutletMQTTClient):
    def __init__(self,config_block,outlet_suite):
        super(OutletMQTTClientListener,self).__init__(config_block)

        def on_message(client,userdata,msg):
            client.message(userdata,msg)

        self.on_message = on_message
        self.outlet_suite = outlet_suite

    def connected(self,userdata):
        topic = self.config_block['channel_prefix'] + "#"
        print("...connected")
        if isinstance(topic,unicode):
            topic = topic.encode('utf-8')
        self.subscribe(topic)

    def message(self,userdata,msg):
        print "Message Topic: ",msg.topic
        print "Message Payload: ",str(msg.payload)
        if to_bool(msg.payload):
            self.outlet_suite.on(os.path.basename(msg.topic))
        else:
            self.outlet_suite.off(os.path.basename(msg.topic))

    def loop_forever(self):
        print("Listening on channel %s..."%(self.config_block['channel_prefix'] + "#"))
        super(OutletMQTTClient,self).loop_forever()

class OutletMQTTClientSender(OutletMQTTClient):
    def __init__(self,config_block,name,state):
        super(OutletMQTTClientSender,self).__init__(config_block)
        self.outlet_name = name
        self.outlet_state = state

    def connected(self,userdata):
        payload = "On" if self.outlet_state else "Off"
        topic = self.config_block['channel_prefix'] + self.outlet_name
        print("....connected")
        print("Sending \"%s\" to %s"%(payload,topic))

        (result,mid) = self.publish(topic,payload)
    

def cli_parser():
    parser = argparse.ArgumentParser(description='Manage outet MQTT Channels')
    parser.add_argument('--listen', action='store_true', help='Listen on the specified channel and control the associted outlets')
    parser.add_argument('-c','--config',required=True,help="Configuration file to load")
    parser.add_argument('--on', action='store_true',help='Send an \'on\' message in --send mode')
    parser.add_argument('--off', action='store_true',help='Send an \'off\' message')
    parser.add_argument('outlet',nargs='?', help='The name of the outlet to send message to. Only valid when not --listen ing')

    return parser

def main():
    parser = cli_parser()
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print("You must specify an existing configuration file")
        exit(1)

    config = json.load(open(args.config))

    outlet_config = config['outlet_config']
    outlet_names = outlet_config['outlets'].keys()

    if args.listen:
        outlet_suite = outlets.OutletSuite(outlet_config)
        client = OutletMQTTClientListener(config['mqtt_config'],outlet_suite)
        client.connect()
        client.loop_forever()
    else:
        if args.outlet is None:
            print("You must specify an outlet if you don't specify --listen")
            exit(1)
        elif not args.outlet in outlet_names:
            print("Unrecognized outlet.  Choose from this list: %r"%(outlet_names))
        else:
            client = OutletMQTTClientSender(config['mqtt_config'],args.outlet,True if args.on else False)
            print(client.connect())
            client.loop()
                
if __name__ == "__main__":
    main()
