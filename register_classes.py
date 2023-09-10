from labscript_devices import register_classes

register_classes(
    'Windfreak',
    BLACS_tab='user_devices.Cesium.Windfreak.blacs_tabs.WindfreakTab',
    runviewer_parser=None,
)
