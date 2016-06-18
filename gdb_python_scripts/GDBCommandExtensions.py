import gdb
import pickle
import sys

# This is some retarded hack
gdbvalue = gdb.parse_and_eval("$PINCE_PATH")
PINCE_PATH = gdbvalue.string()
sys.path.append(PINCE_PATH)  # Adds the PINCE directory to PYTHONPATH to import libraries from PINCE
import gdb_python_scripts.ScriptUtils as ScriptUtils
import GuiUtils
import SysUtils
import type_defs

COMBOBOX_BYTE = type_defs.COMBOBOX_BYTE
COMBOBOX_2BYTES = type_defs.COMBOBOX_2BYTES
COMBOBOX_4BYTES = type_defs.COMBOBOX_4BYTES
COMBOBOX_8BYTES = type_defs.COMBOBOX_8BYTES
COMBOBOX_FLOAT = type_defs.COMBOBOX_FLOAT
COMBOBOX_DOUBLE = type_defs.COMBOBOX_DOUBLE
COMBOBOX_STRING = type_defs.COMBOBOX_STRING
COMBOBOX_AOB = type_defs.COMBOBOX_AOB


# returns values from memory according to address table contents sent from PINCE
class ReadAddressTableContents(gdb.Command):
    def __init__(self):
        super(ReadAddressTableContents, self).__init__("pince-update-address-table", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        table_contents_send = []
        inferior = gdb.selected_inferior()
        pid = inferior.pid
        directory_path = SysUtils.get_PINCE_IPC_directory(pid)
        recv_file = directory_path + "/address-table-from-PINCE.txt"
        send_file = directory_path + "/address-table-to-PINCE.txt"
        table_contents_recv = pickle.load(open(recv_file, "rb"))

        # table_contents_recv format: [[address1,string1],[address2,string2],..]
        for item in table_contents_recv:
            address = item[0]
            string = item[1]
            index, length, unicode, zero_terminate = GuiUtils.text_to_valuetype(string)
            readed = ScriptUtils.read_single_address(address, index, length, unicode, zero_terminate)
            table_contents_send.append(readed)
        pickle.dump(table_contents_send, open(send_file, "wb"))


class ReadSingleAddress(gdb.Command):
    def __init__(self):
        super(ReadSingleAddress, self).__init__("pince-read-single-address", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        try:
            parameters = eval(
                arg)  # more like EVIL mwahahahaha... HAHAHAHAHA... **muffled evil laughter from distance**

            # 5 is the number of parameters coming from PINCE
            address, value_type, length, unicode, zero_terminate = parameters + (None,) * (5 - len(parameters))
            address = hex(address)
        except:
            print("")
            return

        # python can't print a string that has null bytes in it, so we'll have to print the raw bytes instead and let PINCE do the parsing
        # Weird enough, even when python can't print those strings, pyqt can(in it's gui elements like labels)
        if value_type is COMBOBOX_STRING:
            value_type = COMBOBOX_AOB
        print(ScriptUtils.read_single_address(address, value_type, length, unicode, zero_terminate))


class IgnoreErrors(gdb.Command):
    def __init__(self):
        super(IgnoreErrors, self).__init__("ignore-errors", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        try:
            gdb.execute(arg, from_tty)
        except:
            pass


IgnoreErrors()
ReadAddressTableContents()
ReadSingleAddress()