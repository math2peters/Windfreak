#####################################################################
#                                                                   #
# Copyright 2019, Monash University and contributors                #
#                                                                   #
# This file is part of labscript_devices, in the labscript suite    #
# (see http://labscriptsuite.org), and is licensed under the        #
# Simplified BSD License. See the license.txt file in the root of   #
# the project for the full license.                                 #
#                                                                   #
#####################################################################

from labscript import IntermediateDevice, TriggerableDevice, AnalogOut, DigitalOut, Trigger
from labscript.labscript import Device, set_passed_properties
import numpy as np

class Windfreak(IntermediateDevice, TriggerableDevice):

    # A human readable name for device model used in error messages
    description = "Windfreak frequency synthesizer"
    # The labscript Output classes this device supports
    allowed_children = [ ]
    # The maximum update rate of this device (in Hz)
    clock_limit = 1e4

    @set_passed_properties(
        property_names={
            'connection_table_properties':
                [
                    'name',
                    'com_port',
                    'reference_mode',
                ]
        }
    )
    def __init__ (self, name, com_port, reference_mode='internal 27mhz', parent_device=None, connection=None, **kwargs):
        """init the windfreak device

        Args:
            name (str): name of windfreak
            com_port (str): com port for the windfreak
            reference_mode (str): whether or not the reference is internal or external. Options are: ('external', 'internal 27mhz', 'internal 10mhz')
        """
        if connection is None:
            IntermediateDevice.__init__ ( self , name, parent_device, **kwargs)
        else:
            TriggerableDevice.__init__ ( self , name, parent_device, connection=connection, **kwargs)
        self.BLACS_connection = "Windfreak Synthesizer {}".format(com_port)
        self.name = name
        self.reference_mode = reference_mode

        # Dictionaries for values we want to set in the device
        self.frequency_dict = {0:10e6, 1:10e6} # Hz
        self.phase_dict = {0:0, 1:0} # degrees
        self.power_dict = {0:0, 1:0} # dBm
        self.enable_dict = {0:False, 1:False}
        self.sweep_dict = {0:(0., 0., 0., 0.), 1:(0., 0., 0., 0.)} # (start, stop, step, enable) (frequency)

        self.minimum_frequency = 10e6 # Hz
        self.maximum_frequency = 15000e6 # Hz

        self.minimum_power = -70 # dBm
        self.maximum_power = +20 # dBm

        self.minimum_phase = 0 # dBm
        self.maximum_phase = 360 # dBm


    def generate_code(self,hdf5_file):
        """Write the frequency sequence for each channel to the HDF file

        Args:
            hdf5_file (hdf): labscript hdf file
        """

        Device.generate_code(self, hdf5_file)

        grp = hdf5_file.require_group(f'/devices/{self.name}/')

        frequencies = grp.require_dataset('frequency', (2,), dtype='f')
        frequencies[:] = [self.frequency_dict[0], self.frequency_dict[1]]

        enables = grp.require_dataset('enable', (2,), dtype='?')
        enables[:] = [self.enable_dict[0], self.enable_dict[1]]

        phases = grp.require_dataset('phase', (2,), dtype='f')
        phases[:] = [self.phase_dict[0], self.phase_dict[1]]

        powers = grp.require_dataset('power', (2,), dtype='f')
        powers[:] = [self.power_dict[0], self.power_dict[1]]

        sweeps = grp.require_dataset('sweep', (2,4), dtype='f')
        sweeps[:] = [self.sweep_dict[0], self.sweep_dict[1]]

    


    def set_frequency(self, channel, frequency):
        """Set the frequency for the windfreak channel  0 or 1

        Args:
            channel (int): channel to set the frequency for (0 or 1)
            frequency (float): frequency to set the channel to (in Hz)
        """

        if not self.minimum_frequency <= frequency <= self.maximum_frequency:
            raise(ValueError("The maximum frequency value is {}, but {} was entered".format(self.maximum_frequency, frequency)))

        if channel not in [0, 1]:
            raise(ValueError("The channel must be either 0 or 1, but {} was entered".format(channel)))


        self.frequency_dict[channel] = frequency
        self.enable_dict[channel] = True

    def set_power(self, channel, power):
        """Set the power for the windfreak channel  

        Args:
            channel (int): channel to set the power for (0 or 1)
            power (float): power to set the channel to (in dBm)
        """

        if not self.minimum_power <= power <= self.maximum_power:
            raise(ValueError("The maximum power value is {}, but {} was entered".format(self.maximum_power, power)))

        if channel not in [0, 1]:
            raise(ValueError("The channel must be either 0 or 1, but {} was entered".format(channel)))


        self.power_dict[channel] = power

    def set_phase(self, channel, phase):
        """Set the phase for the windfreak channel  0 or 1

        Args:
            channel (int): channel to set the phase for (0 or 1)
            phase (float): phase to set the channel to (deg)
        """

        if not self.minimum_phase <= phase <= self.maximum_phase:
            raise(ValueError("The maximum phase value is {}, but {} was entered".format(self.maximum_phase, phase)))

        if channel not in [0, 1]:
            raise(ValueError("The channel must be either 0 or 1, but {} was entered".format(channel)))


        self.phase_dict[channel] = phase

    def enable_channel(self, channel, enable):
        """Enable or disable the windfreak channel enable = True or False"""
        if channel not in [0, 1]:
            raise(ValueError("The channel must be either 0 or 1, but {} was entered".format(channel)))

        self.enable_dict[channel] = enable

    def setup_sweep(self, channel, start_frequency, stop_frequency, step_frequency):
        """Set up a triggerable sweep for the windfreak channel

        Args:
            channel (int): channel to sweep (0 or 1)
            start_frequency (float): starting frequency to sweep in Hz
            stop_frequency (float): stop freq to sweep in Hz
            step_frequency (float): how much to jump in Hz each step
        """
        self.sweep_dict[channel] = (start_frequency, stop_frequency, step_frequency, 1)