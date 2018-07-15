# etekcity_mqtt 

This is a small, python based [MQTT](mqtt) listener and sender that controls [EtekCity remote outlets](http://a.co/fVCohfv)
using [RFOutlet](https://github.com/kfieldho/rfoutlet), a [wiringPi](wiringpi.com) utility that controls a 
[SMAKN 433Hz Transmitter](http://a.co/0scz2qP) to transmit the appropriate signals.

## Config File

The script is configured using a JSON file with the following structure

	{
		"mqtt_config": {
			"broker" : "192.168.168.165",
			"port": 1883,
			"channel_prefix": "21outlet/outlets/"
		},
		"outlet_config" : {
			"code_sender" : "/home/kfieldho/Projects/Personal/RFOutlet/rfoutlet/codesend",
			"pin": 0,
			"default_delay": 176,
			"outlets" : {
				"aquarium": {
					"on" : "284099",
					"off" : "284108"
				}
	}

The `mqtt_config` dictionary controls the MQTT server that is used, by specifying the `broker` host and `port`.  
The `channel_prefix` specifies the the MQTT channel each out is controled on.

The `outlet_config` dictionary provides information about the RFOutlet `codesend` command that is used to actually 
control the outlets.  The `code_sender` element specifies the location of the command, the `pin` element specifies
the GPIO pin # that is wired to the transmitter and the `default_delay` specifies the delay between pulses (different
outlet controllers sometimes use different delays for better operation.  Use a `delay` element in the outlet config if you 
need to specify a delay different than the default).

There can be any number of `outlets`, keyed by the (must be unique) name of the outlet (which is appended to the MQTT
`channel_prefix`).  The EtekCity outlets work py providing a `on` and `off` code for each outlet.


## mqtt_outlet

`mqtt_outlet` is the MQTT sender and listener.  Typically the listerner is started with a [supervisor](supervisord.org) start script.

	usage: mqtt_outlets.py [-h] [--listen] -c CONFIG [--on] [--off] [outlet]

	Manage outet MQTT Channels

	positional arguments:
	  outlet                The name of the outlet to send message to. Only valid
							when not --listen ing

	optional arguments:
	  -h, --help            show this help message and exit
	  --listen              Listen on the specified channel and control the
							associted outlets
	  -c CONFIG, --config CONFIG
							Configuration file to load
	  --on                  Send an 'on' message in --send mode
	  --off                 Send an 'off' message

## outlet

`outlets` is a script that reads the same config file syntax as `mqtt_outlet` but directly controls the transmitter.  In fact
it is the module that the `mqtt_outlet` listener uses to control the outlets
