from blacs.device_base_class import DeviceTab, define_state
from qtutils.qt.QtCore import*
from qtutils.qt.QtGui import *
from qtutils.qt.QtWidgets import *
from qtutils import UiLoader
from pathlib import Path

class WindfreakTab(DeviceTab):
    def initialise_GUI ( self ):
        
        root_path = Path(__file__).parent.resolve()
        ui_path = str(root_path.joinpath('windfreak.ui'))

        # pull the layout of the tab so that we can place widgets in it
        layout = self.get_tab_layout()
        self.ui = UiLoader().load(ui_path)
        layout.addWidget(self.ui)

        self.set_button_group = QButtonGroup()
        self.set_button_group.setExclusive(True)

        self.set_button_group.addButton(self.ui.ch0_set_button)
        self.set_button_group.addButton(self.ui.ch1_set_button)

        self.set_button_group.buttonClicked.connect(self.set_on_click)

        self.line_edit_dict = {0:[self.ui.ch0_frequency_edit, self.ui.ch0_phase_edit, self.ui.ch0_power_edit],
                               1:[self.ui.ch1_frequency_edit, self.ui.ch1_phase_edit, self.ui.ch1_power_edit]}

        self.ui.ch0_enable_check.stateChanged.connect(lambda: self.checkbox_clicked(self.ui.ch0_enable_check, 0))
        self.ui.ch1_enable_check.stateChanged.connect(lambda: self.checkbox_clicked(self.ui.ch0_enable_check, 1))

    MODE_MANUAL = 1
    @define_state(MODE_MANUAL,True)  
    def set_on_click(self, btn):
        """On a button press, send the corresponding textbox contents to the windfreak

        Args:
            btn ([type]): which of the buttons were pressed
        """
        self.logger.debug('entering set')

        # the last part of the name of the button is the channel that is being changed
        channel = btn.text()[-1]

        # get the number of the channel from the name of the channel
        channel = int(channel)
        
        # try to get the float value from the textbox, check to see if the contents are a float, then set the DDS channel
        try:
            # format string: valid inputs are a single number
            line_edit_list = self.line_edit_dict[channel]
            frequency_value = float(line_edit_list[0].text().replace(" ", ""))
            phase_value = float(line_edit_list[1].text().replace(" ", ""))
            power_value = float(line_edit_list[2].text().replace(" ", ""))
            

            results = yield(self.queue_work('main_worker','set_frequency', channel, frequency_value))
            results = yield(self.queue_work('main_worker','set_phase', channel, phase_value))
            results = yield(self.queue_work('main_worker','set_power', channel, power_value))
        except Exception as e:
            self.logger.debug(str(e))
            self.ui.error_message.setText(str(e))

        return

        
    MODE_MANUAL = 1
    @define_state(MODE_MANUAL,True)  
    def checkbox_clicked(self, btn, channel):
        """Checkbox changed; update outputs

        Args:
            btn (QCheckBox): which of the buttons were pressed
            channel (int): which of the buttons were pressed
        """

        # try to get the float value from the textbox, check to see if the contents are a float, then set the DDS channel
        try:
            # format string: valid inputs are a single number

            
            pass
            results = yield(self.queue_work('main_worker','set_enable', channel, btn.isChecked()))

        except Exception as e:
            self.logger.debug(str(e))
            self.ui.error_message.setText(str(e))

        return
        

    def initialise_workers(self):
        connection_table = self.settings['connection_table']
        device = connection_table.find_by_name(self.device_name)

        # Create and set the primary worker
        self.create_worker(
            'main_worker',
            'user_devices.Cesium.Windfreak.blacs_workers.WindfreakWorker',
            {
                'name': device.properties['name'],
                'com_port': device.properties['com_port'],
                'reference_mode': device.properties['reference_mode']
            },
        )
        self.primary_worker = 'main_worker'