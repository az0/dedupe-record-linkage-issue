"""
Train the dedupe system on human-labeled pairs
"""


import logging
import re
from datetime import datetime

import dedupe

import common

logger = logging.getLogger()

train_csv_fn = 'label.csv'
in_file_1_fn = 'data1.csv'
in_file_2_fn = 'data2.csv' 
training_json_fn = 'training.json'


def get_naive_linker():
    # Define the fields the linker will pay attention to
        #
        # Notice how we are telling the linker to use a custom field comparator
        # for the 'price' field.
    fields = [
            {'field' : 'name', 'type': 'String'},
            {'field' : 'street', 'type': 'Address', 'has missing': True},
            {'field' : 'city', 'type': 'ShortString'},
            {'field' : 'state', 'type': 'Exact'},
            {'field' : 'zip', 'type': 'ShortString'}]

    import dedupe
    linker = dedupe.RecordLink(fields)
    return linker

def train(data_1, data_2):
    import dedupe
    if not os.path.exists(common.settings_fn):
        logger.error(f'run train_from_csv.py to create the settings file: {settings_fn}')

    logger.warning(f'reading from {settings_fn}')
    with open(settings_fn, 'rb') as sf :
        linker = dedupe.StaticRecordLink(sf)
    return linker



def get_labeled():
    """Return a dictionary of labeled examples for use in mark_pairs()"""
    train_csv = common.read_data(train_csv_fn)

    # see https://dedupe.io/developers/library/en/latest/API-documentation.html#Dedupe.markPairs
    match = []
    distinct = []
    for row_key in train_csv:
        row = train_csv[row_key]
        o_dict = {'name': row['o_name'], 'street': row['o_street'],
                  'city': row['o_city'], 'state': row['o_state'], 'zip': row['o_zip']}
        s_dict = {'name': row['s_name'], 'street': row['s_street'],
                  'city': row['s_city'], 'state': row['s_state'], 'zip': row['s_zip']}
        pair = (o_dict, s_dict)
        if row['type'] == 'distinct':
            distinct.append(pair)
        elif row['type'] == 'match':
            match.append(pair)
        else:
            raise RuntimeError('unknown type : %s ' % row['type'])

    logger.info('Record counts: {:,} match vs. {:,} distinct'.format(len(match), len(distinct)))

    labeled_examples = {'match': match,
                        'distinct': distinct}
    return labeled_examples

def label_dict_to_json(d):
    """Convert training dictionary to JSON training file"""
    import io
    import json
    f = io.StringIO(json.dumps(d, indent=4))
    return f

def go():
    linker = get_naive_linker()

    logger.info('reading data 1 and 2')
    data_1 = common.read_data(in_file_1_fn)
    data_2 = common.read_data(in_file_2_fn)

    logger.info('prepare_training()')
    labeled_examples = get_labeled()
    linker.prepare_training(data_1, data_2, training_file=label_dict_to_json(labeled_examples))

    if False:
        logger.info('Skip console_label() for automation')
    else:
        logger.info('console_label()')
        dedupe.convenience.console_label(linker)

    logger.info('train()')
    linker.train()

    logger.info('write_training()')
    with open(training_json_fn, 'w') as tf:
        linker.write_training(tf)

    logger.info('write_settings()')
    with open(settings_fn, 'wb') as sf:
        linker.write_settings(sf)

    logger.info('All done') 

if __name__ == "__main__":
    try:
        go()
    except:
        logger.exception('unhandled exception in go()')
