#!/usr/bin/env python
"""
File: BraTS_partitions
Date: 5/5/18 
Author: Jon Deaton (jdeaton@stanford.edu)
"""
import os
import BraTS

import os
import sys
import argparse
import logging

import BraTS
from segmentation.BraTS_partitions import *
from random import shuffle


def partition_brats(brats_root, output_dir, year, num_test=40, num_validation=40):
    BraTS.set_root(brats_root)
    brats = BraTS.DataSet(year=year)

    # Shuffle up the data
    ids = brats.train.ids
    shuffle(ids)

    # Split up the patient IDs into test, validation and train
    test_ids = ids[:num_test]
    validation_ids = ids[num_test:(num_test + num_validation)]

    test_ids_file = os.path.join(output_dir, test_ids_filename)
    validation_ids_file = os.path.join(output_dir, validation_ids_filename)

    # Write the test and validation IDs to file
    with open(test_ids_file, 'w') as f:
        f.write("\n".join(test_ids))

    with open (validation_ids_file, 'w') as f:
        f.write("\n".join(validation_ids))


def parse_args():
    """
    Parse command line arguments

    :return: An argparse object containing parsed arguments
    """

    parser = argparse.ArgumentParser(description="Train tumor segmentation model",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    io_options_group = parser.add_argument_group("I/O")
    io_options_group.add_argument('--brats', required=True,  help="BraTS data root directory")
    io_options_group.add_argument('--output', required=False, default=partition_store, help="Where the ids are stored")

    sets_options_group = parser.add_argument_group("Partition Set")
    sets_options_group.add_argument("--year", type=int, default=brats_year, help="BraTS data year")
    sets_options_group.add_argument("--test", type=int, default=40, help="Size of training set")
    sets_options_group.add_argument("--validation", type=int, default=40, help="Size of validation set")

    general_options_group = parser.add_argument_group("General")
    general_options_group.add_argument("--pool-size", type=int, default=8, help="Size of worker pool")

    logging_options_group = parser.add_argument_group("Logging")
    logging_options_group.add_argument('--log', dest="log_level", default="WARNING", help="Logging level")
    logging_options_group.add_argument('--log-file', default="model.log", help="Log file")

    args = parser.parse_args()

    # Setup the logger
    global logger
    logger = logging.getLogger('root')

    # Logging level configuration
    log_level = getattr(logging, args.log_level.upper())
    if not isinstance(log_level, int):
        raise ValueError('Invalid log level: %s' % args.log_level)

    log_formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(funcName)s] - %(message)s')

    # For the log file...
    file_handler = logging.FileHandler(args.log_file)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    # For the console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    logger.setLevel(log_level)

    return args


def main():
    args = parse_args()

    brats_root = os.path.expanduser(args.brats)
    output_dir = os.path.expanduser(args.output)

    if not os.path.isdir(brats_root):
        raise FileNotFoundError(brats_root)

    logger.debug("BraTS root: %s" % brats_root)

    if not os.path.exists(output_dir):
        logging.debug("Creating output directory: %s" % output_dir)
        try:
            os.mkdir(output_dir)
        except FileExistsError:
            logger.debug("Output directory exists.")
    else:
        logger.debug("Output directory: %s" % output_dir)

    logger.debug("Number of test examples: %d" % args.test)
    logger.info("Number of validation examples: %d" % args.validation)

    partition_brats(brats_root, output_dir, args.year,
                    num_test=args.test,
                    num_validation=args.validation)


if __name__ == "__main__":
    main()