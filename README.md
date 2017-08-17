# ble-tester
A simple PC BLE test tool which reads data from the trackle sensor and sends it to the backend.

This is based on [BluePy](https://github.com/IanHarvey/bluepy) python BLE library.

This works on Linux only. Please follow [this](https://github.com/IanHarvey/bluepy) to install the BluePy on he linux machine.

Run `sudo python trackle_ble_client.py` and type in the index number of the ble device from the list of devices that appear

Once the device is connected, the python script receives the data from the trackle sensor and pushes the values to the backend

Press `Ctrl + C` to exit
