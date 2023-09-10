import h5py
from blacs.tab_base_classes import Worker
from windfreak import SynthHD



class WindfreakWorker(Worker):

    def init (self):
        # Once off device initialisation code called when the
        # worker process is first started .
        # Usually this is used to create the connection to the
        # device and/or instantiate the API from the device
        # manufacturer
        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows

        port = self.com_port
        self.synthesizer = SynthHD(port)
        self.synthesizer.init()

        # Print self.synthesizerHD information
        print(f"Initialized {self.synthesizer.model_type} at port " + port +
            f", trigger mode {self.synthesizer.trigger_mode}")

        # Check current settings
        print(f"Channel A: {self.synthesizer[0].frequency / 1e6} MHz, {self.synthesizer[0].power} dBm, "
            f"output on = {self.synthesizer[0].rf_enable}")
        print(f"Channel B: {self.synthesizer[1].frequency / 1e6} MHz, {self.synthesizer[1].power} dBm, "
            f"output on = {self.synthesizer[1].rf_enable}\n")

        if self.reference_mode not in self.synthesizer.reference_modes:
            raise Exception(ValueError("Reference mode not supported. Choose one from {}".format(str(self.synthesizer.reference_modes))))
        self.synthesizer.reference_mode = self.reference_mode
        

    def set_frequency(self, channel, frequency):
        """Sets the frequency for the synthesizer

        Args:
            channel (int): name of the channel (0 or 1)
            frequency (float): frequency to set for the channel
        """

        if not 10e6 <= frequency <= 15e9:
            raise Exception(ValueError("Frequency in invalid range"))

        self.synthesizer[channel].frequency = float(frequency)
        set_frequency = self.synthesizer[channel].frequency
        print("Setting Frequency: {}".format(set_frequency))
        return set_frequency

    def set_power(self, channel, power):
        """Sets the power for the synthesizer

        Args:
            channel (int): name of the channel (0 or 1)
            power (float): power to set for the channel
        """

        if not -70 <= power <= 20:
            raise Exception(ValueError("Power in invalid range"))

        self.synthesizer[channel].power = float(power)
        set_power = self.synthesizer[channel].power
        print("Setting Power: {}".format(set_power))
        return set_power

    def set_phase(self, channel, phase):
        """Sets the phase for the synthesizer

        Args:
            channel (int): name of the channel (0 or 1)
            phase (float): phase to set for the channel
        """

        if not 0 <= phase <= 360:
            raise Exception(ValueError("Phase in invalid range"))
        self.synthesizer[channel].phase = float(phase)
        set_phase = self.synthesizer[channel].phase
        print("Setting Phase: {}".format(set_phase))
        return set_phase

    def set_enable(self, channel, enable):
        """Sets the enable for the synthesizer

        Args:
            channel (int): name of the channel (0 or 1)
            frequency (float): frequency to set for the channel
        """


        self.synthesizer[channel].enable = enable
        return self.synthesizer[channel].rf_enable

    def set_sweep(self, channel, sweeps_list):
        """Sets the sweep for the synthesizer

        Args:
            channel (int): name of the channel (0 or 1)
            sweeps_list (list): list of tuples of the form (channel, start, stop, step, enable)
        """
        print("Setting Ch{} Sweep: {}".format(channel, sweeps_list[:3]))
        start_frequency, stop_frequency, step_frequency, enable = sweeps_list
        self.synthesizer[channel].sweep_enable = True
        self.synthesizer[channel].trigger_mode = 'single frequency step'
        self.synthesizer[channel].sweep_freq_low = start_frequency/1e6 # Convert to MHz
        self.synthesizer[channel].sweep_freq_high = stop_frequency/1e6
        self.synthesizer[channel].sweep_freq_step = step_frequency/1e6


    def shutdown (self):
        # Once off device shutdown code called when the
        # BLACS exits
        pass

    def program_manual ( self , front_panel_values ):
        # Update the output state of each channel using the values
        # in front_panel_values ( which takes the form of a
        # dictionary keyed by the channel names specified in the
        # BLACS GUI configuration
        # return a dictionary of coerced / quantised values for each
        # channel , keyed by the channel name (or an empty dictionary )
        return {}
        
    def transition_to_buffered ( self , device_name , h5_file_path,
    initial_values , fresh ):
        # Access the HDF5 file specified and program the table of
        # hardware instructions for this device .
        # Place the device in a state ready to receive a hardware
        # trigger (or software trigger for the master pseudoclock )
        #
        # The current front panel state is also passed in as
        # initial_values so that the device can ensure output
        # continuity up to the trigger .
        #
        # The fresh keyword indicates whether the entire table of
        # instructions should be reprogrammed (if the device supports
        # smart programming )
        # Return a dictionary , keyed by the channel names , of the
        # final output state of the shot file . This ensures BLACS can
        # maintain output continuity when we return to manual mode
        # after the shot completes .

        self.h5_filepath = h5_file_path
        self.device_name = device_name

        # From the H5 sequence file, get the sequence we want programmed into the arduino
        with h5py.File(h5_file_path, 'r') as hdf5_file:
            
            device = hdf5_file['devices'][device_name]
            frequencies = device['frequency'][:]
            phases = device['phase'][:]
            powers = device['power'][:]
            sweeps = device['sweep'][:]
            sweep_enable_0 = sweeps[0][-1]
            sweep_enable_1 = sweeps[1][-1]


            self.set_frequency(0, frequencies[0])
            self.set_frequency(1, frequencies[1])

            self.set_phase(0, phases[0])
            self.set_phase(1, phases[1])

            self.set_power(0, powers[0])
            self.set_power(1, powers[1])

            if sweep_enable_0:
                self.set_sweep(0, sweeps[0])
            if sweep_enable_1:
                self.set_sweep(1, sweeps[1])

        final_values = {}
        return final_values


    def transition_to_manual ( self ):
        # Called when the shot has finished , the device should
        # be placed back into manual mode
        # return True on success
        # self.synthesizer.sweep_enable = False
        # self.synthesizer.trigger_mode = 'disabled'
        # self.set_frequency(0, self.current_frequencies[0])
        # self.set_frequency(1, self.current_frequencies[1])
        return True

    def abort_transition_to_buffered ( self ):
        # Called only if transition_to_buffered succeeded and the
        # shot if aborted prior to the initial trigger
        # return True on success
        return True

    def abort_buffered ( self ):
        # Called if the shot is to be abort in the middle of
        # the execution of the shot ( after the initial trigger )
        # return True on success
        return True

