"""Bridge functionality for the MIDI-Interface"""

import rtmidi
from time import sleep


def bundle_after_channels_ip(midi_input, channel_dict):
    """Changes channel_dict"""
    chnl_stat, pitch, velocity = midi_input[0]
    duration = midi_input[1]
    try:
        channel_dict[chnl_stat]["pitch"].append(pitch)
        channel_dict[chnl_stat]["velocity"].append(velocity)
        channel_dict[chnl_stat]["duration"].append(duration)
    except KeyError:
        channel_dict.update({chnl_stat: {"pitch": [],
                                    "velocity": [],
                                    "duration": []}})


INPUT = rtmidi.MidiIn(rtmidi.API_UNIX_JACK, "Kodou")



def record(msg, msg_dict):
    chnl_stat, pitch, vel = msg[0]
    dur = msg[1]
    try:
        if chnl_stat == 144:    # onset
            onset = msg_dict[1]["onset"][-1] + dur
            msg_dict[1]["onset"].append(onset)
            msg_dict[1]["pitch"].append(pitch)
            msg_dict[1]["vel"].append(vel)
        elif chnl_stat == 128:
            msg_dict[1]["dur"].append(dur)
    except KeyError:
        msg_dict[1] = {"pitch": [pitch],
                       "onset": [0],
                       "vel": [vel],
                       "dur": []}
    return msg_dict

def connect_dev_to_rtmidi(midiin, port_name):
    port_names = [name.upper() for name in midiin.get_ports()]
    port_name = port_name.upper()
    for port_num, name in enumerate(port_names):
        if port_name in name:
            midiin.open_port(port_num)
            return
    raise NameError("Unknown device {}!".format(port_name))


def run(midiin, msg_dict):
    onset = 0
    while True:
        msg = midiin.get_message()
        if msg:
            msg_dict = record(msg, msg_dict)
            print(msg)
        sleep(.01)
    return msg_dict



