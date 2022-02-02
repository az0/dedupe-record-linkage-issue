settings_fn = 'settings.dedupe'

def preProcess(column):
    """
    Do a little bit of data cleaning with the help of Unidecode and Regex.
    Things like casing, extra spaces, quotes and new lines can be ignored.
    """

    from unidecode import unidecode
    import re

    try : # python 2/3 string differences
        column = column.decode('utf8')
    except AttributeError:
        pass
    column = unidecode(column)
    column = re.sub('\n', ' ', column)
    column = re.sub('-', '', column)
    column = re.sub('/', ' ', column)
    column = re.sub("'", '', column)
    column = re.sub(",", '', column)
    column = re.sub(":", ' ', column)
    column = re.sub('  +', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    if not column :
        column = None
    return column


def read_data(filename, max_rows = False):
    """
    Read in our data from a CSV file and create a dictionary of records,
    where the key is a unique record ID.
    """

    print(f'reading CSV file: {filename}')
    data_d = {}


    import csv
    with open(filename, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        row_count = 0
        for i, row in enumerate(reader):
            if max_rows and i > max_rows:
                break
            clean_row = dict([(k, preProcess(v)) for (k, v) in row.items()])
            # FIXME: dedupe API requests that the row key be the record key,
            # but we make a fake key.
            row_key = filename + str(i) 
            data_d[row_key] = dict(clean_row)

    return data_d

