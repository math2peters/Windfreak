from windfreak import SynthHD

# your com port here
port = 'COM5'
synth = SynthHD(port)
synth.init()

# Print SynthHD information
print(f"Initialized {synth.model_type} at port " + port +
      f", trigger mode {synth.trigger_mode}")

# Check current settings
print(f"Channel A: {synth[0].frequency / 1e6} MHz, {synth[0].power} dBm, "
      f"output on = {synth[0].rf_enable}")
print(f"Channel B: {synth[1].frequency / 1e6} MHz, {synth[1].power} dBm, "
      f"output on = {synth[1].rf_enable}")
print()

# Set static outputs on both channels
ChA_freq = 2874.75e6 # Hz
ChA_power = 10.0 # dBm
ChB_freq = 5401.825e6
ChB_power = 8.0
synth[0].frequency = ChA_freq
synth[0].power = ChA_power
synth[1].frequency = ChB_freq
synth[1].power = ChB_power
synth[0].enable = True
synth[1].enable = True
print("Setting static outputs")
print(f"Channel A: {synth[0].frequency / 1e6} MHz, {synth[0].power} dBm, "
      f"output on = {synth[0].rf_enable}")
print(f"Channel B: {synth[1].frequency / 1e6} MHz, {synth[1].power} dBm, "
      f"output on = {synth[1].rf_enable}")

# Set sweep on channel 1 (B)
print("On Channel " + str(synth.read('channel')))
probe_sweep_freq_low = 5401.625 # in MHz
probe_sweep_freq_high = 5402.026
probe_sweep_freq_step = 0.01
probe_sweep_time_step = 100 # in ms
probe_sweep_power_low = ChB_power
probe_sweep_power_high = ChB_power

synth.write('sweep_freq_low', probe_sweep_freq_low)
synth.write('sweep_freq_high', probe_sweep_freq_high)
synth.write('sweep_freq_step', probe_sweep_freq_step)
synth.write('sweep_time_step', probe_sweep_time_step)
synth.trigger_mode = 'single frequency step'
synth.sweep_enable = True
print(f"Sweeping from {synth.read('sweep_freq_low')} MHz to "
      f"{synth.read('sweep_freq_high')} MHz, "
      f"frequency step {synth.read('sweep_freq_step')} MHz, "
      f"time step {synth.read('sweep_time_step')} ms.")