import dbus
import dbus.mainloop.glib

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

from bluez_components import *

mainloop = None


class RowChrc(Characteristic):
    ROW_UUID = '12345678-1234-5678-1234-56789abc000'

    def __init__(self, index, service, row, printer):
        Characteristic.__init__(
            self, index,
            self.ROW_UUID + hex(row)[2:],  # use the row number to build the UUID
            ['read', 'write'],
            service)
        self.value = [0x00, 0x00]
        self.row = row
        self.printer = printer

    def ReadValue(self, options):
        print('RowCharacteristic Read: Row: ' + str(self.row) + ' ' + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print('RowCharacteristic Write: Row: ' + str(self.row) + ' ' + repr(value))
        #set_printer_row(self.printer, self.row, value[:2])
        self.value = value[:2]


class PrinterService(Service):
    PRN_SVC_UUID = '12345678-1234-5678-1234-56789abc0010'

    def __init__(self, index, printer):
        Service.__init__(self, index, self.PRN_SVC_UUID, True)
        self.add_characteristic(RowChrc(0, self, 0, printer))


class PrinterApplication(Application):
    def __init__(self, printer):
        Application.__init__(self)
        self.add_service(PrinterService(0, printer))


class PrinterAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, 'peripheral')
        self.add_service_uuid(PrinterService.PRN_SVC_UUID)
        self.include_tx_power = True



def register_ad_cb():
    """
    Callback if registering advertisement was successful
    """
    print('Advertisement registered')


def register_ad_error_cb(error):
    """
    Callback if registering advertisement failed
    """
    print('Failed to register advertisement: ' + str(error))
    mainloop.quit()


def register_app_cb():
    """
    Callback if registering GATT application was successful
    """
    print('GATT application registered')


def register_app_error_cb(error):
    """
    Callback if registering GATT application failed.
    """
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    names = find_adapter_names()
    if not names:
        print("Can not find Gatt and Advertisement accessiable adapter.")
        exit()

    # Get ServiceManager and AdvertisingManager
    managers = get_managers_of_adapter(names[0])


    # Create gatt services
    app = PrinterApplication(0)

    # Create advertisement
    test_advertisement = PrinterAdvertisement(0)

    mainloop = GObject.MainLoop()

    # Register gatt services
    managers["gatt"].RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)

    # Register advertisement
    managers["advertisement"].RegisterAdvertisement(test_advertisement.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)

    try:
        mainloop.run()
    except KeyboardInterrupt:
        exit()


if __name__ == '__main__':
    main()

