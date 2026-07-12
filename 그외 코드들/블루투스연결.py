import modi_plus
import time

bundle = modi_plus.MODIPlus(connection_type="ble",network_uuid="C275969")

print("ez")
print(bundle.modules)