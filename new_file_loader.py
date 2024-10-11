from io import StringIO
import new_filehandler as fh
import pandas as pd


def load_files(upload_files, cutoff):
    big_data = {}
    if upload_files is not None:
        temps, dict = fh.files_to_dict(upload_files)
        for t in temps:
            if dict[t][0] != None and dict[t][1] != None:
                bytes_data = dict[t][0].read().decode('latin1')
                bytes_data_ref = dict[t][1].read().decode('latin1')
                mod = fh.modify_text_file(bytes_data, cutoff)
                mod_ref = fh.modify_text_file(bytes_data_ref, cutoff)

                big_data[t] = (pd.read_csv(StringIO(mod), sep = ',', encoding = 'latin1', skipinitialspace = True),
                                pd.read_csv(StringIO(mod_ref), sep = ',', encoding = 'latin1', skipinitialspace = True))
            elif dict[t][0] == None:
                bytes_data_ref = dict[t][1].read().decode('latin1')
                mod_ref = fh.modify_text_file(bytes_data_ref, cutoff)

                big_data[t] = (None, pd.read_csv(StringIO(mod_ref), sep = ',', encoding = 'latin1', skipinitialspace = True))
            elif dict[t][1] == None:
                bytes_data_ref = dict[t][0].read().decode('latin1')
                mod_ref = fh.modify_text_file(bytes_data_ref, cutoff)

                big_data[t] = (pd.read_csv(StringIO(mod_ref), sep = ',', encoding = 'latin1', skipinitialspace = True), None)

    return temps, big_data