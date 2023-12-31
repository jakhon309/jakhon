#! /usr/bin/python
import csv
from google.protobuf.descriptor import FieldDescriptor
from pathlib import Path
import json
import os
from common import log_normal, log_debug, log_warn, log_info, log_error
lang = os.getenv('MAJSOUL_LANG', 'jp')
verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

def main(original_assets_path, temp_path):
    log_normal('Export csv files from lqc.lqbin...', verbose)

    log_info('Load config_pb2.py...', verbose)
    import_config_path = Path(temp_path) / 'proto' / 'config_pb2.py'
    with open(import_config_path, 'r', encoding='utf-8') as config_pb2_file:
        config_pb2_code = config_pb2_file.read()
        exec(config_pb2_code, globals())

    log_info('Load sheets_pb2.py...', verbose)
    import_sheets_path = Path(temp_path) / 'proto' / 'sheets_pb2.py'
    with open(import_sheets_path, 'r', encoding='utf-8') as sheets_pb2_file:
        sheets_pb2_code = sheets_pb2_file.read()
        exec(sheets_pb2_code, globals())


    log_info('Load tables from lqc.lqbin...', verbose)
    config_table = ConfigTables()
    lqc_path = Path(original_assets_path) / 'res' / 'config' / 'lqc.lqbin'
    with open(lqc_path, "rb") as lqc:
        config_table.ParseFromString(lqc.read())

    csv_path = Path(temp_path) / 'csv'
    csv_path.mkdir(parents=True, exist_ok=True)

    for data in config_table.datas:
        class_words = f"{data.table}_{data.sheet}".split("_")
        class_name = "".join(name.capitalize() for name in class_words)
        klass = globals()[class_name]

        log_info(f'Write {class_name}.csv...', verbose)
        with open(csv_path / f'{class_name}.csv', 'w', encoding='utf-8-sig', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([x.name for x in klass().DESCRIPTOR.fields])
            
            if not hasattr(data, 'data'):
                continue

            for field_msg in data.data:
                field = klass()
                field.ParseFromString(field_msg)
                row = []
                for x in klass().DESCRIPTOR.fields:
                    if hasattr(field, x.name):
                        v = getattr(field, x.name)
                        if x.label == FieldDescriptor.LABEL_REPEATED:
                            v = json.dumps(list(v))
                        row.append(v)
                    else:
                        row.append(None)
                csv_writer.writerow(row)
    log_info('Export complete', verbose)

if __name__ == '__main__':
    main(
        str(Path('./assets-original')),
        str(Path('./temp'))
    )