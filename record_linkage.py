"""
Link records using settings learned from train_from_csv.py
"""
import logging
from timeit import default_timer as timer
from datetime import timedelta

import common

logger = logging.getLogger()


data_1_fn = 'data1.csv'
data_2_fn = 'data2.csv'
link_min_threshold = 0.50

def cluster(linker, data_1, data_2):
    logger.info('clustering...')
    timer_start = timer()
    linked_records = linker.join(data_1, data_2, threshold=link_min_threshold)
    logger.info(f'duration in linker.join(): {timedelta(seconds=timer()-timer_start)}')
    logger.info(f'# duplicate sets {len(linked_records)}')
    return linked_records


def go():
    import dedupe
    logger.info(f'reading from {common.settings_fn}')
    with open(common.settings_fn, 'rb') as sf :
        linker = dedupe.StaticRecordLink(sf)

    data_1 = common.read_data(data_1_fn)
    data_2 = common.read_data(data_1_fn)
    linked_records = cluster(linker, data_1, data_2)
    #write_linked(linked_records, output_file, in_file_1, in_file_2)


if __name__ == "__main__":
    go()
    