#!/usr/bin/env python

import argparse
import os
from dataclasses import dataclass

from bic_util.fs import require_empty_directory, require_output_directory, require_readable_directory
from bic_util.print import print_error_exit

from mni_7t_dicom_to_bids.pipeline import mni_7t_dicom_to_bids


@dataclass
class Args:
    dicom_study_path: str
    bids_dataset_path: str
    subject: str
    session: str
    ignore_unknown: bool
    convert_unknown: str | None
    overwrite: bool
    dataset_files: bool


def main():

    # Parse CLI arguments

    parser = argparse.ArgumentParser(
        prog='mni_7t_dicom_to_bids',
        description="Run the MNI 7T DICOM to BIDS converter on a DICOM study",
    )

    parser.add_argument('dicom_study_path',
        help="Path of the input DICOM study directory.")

    parser.add_argument('bids_dataset_path',
        help="Path of the output BIDS dataset directory.")

    parser.add_argument('--subject',
        required=True,
        help="BIDS subject label.")

    parser.add_argument('--session',
        required=True,
        help="BIDS session label.")

    parser.add_argument('--ignore_unknown',
        action='store_true',
        help="Ignore the unknown DICOM series if there are some. Cannot be used with --ignore_unknown.")

    parser.add_argument('--convert_unknown',
        help=(
            "Path of the output directory to which to convert the unrecognized DICOM series if there are some. Cannot"
            " be used with --ignore_unknown."
        ))

    parser.add_argument('--dataset_files',
        action='store_true',
        help="Generate some static dataset files for the BIDS dataset.")

    parser.add_argument('--overwrite',
        action='store_true',
        help="Overwrite files in the BIDS dataset if they already exist.")

    args = parser.parse_args()

    # Process CLI arguments

    args = Args(
        dicom_study_path  = os.path.normpath(args.dicom_study_path),
        bids_dataset_path = os.path.normpath(args.bids_dataset_path),
        subject           = args.subject,
        session           = args.session,
        ignore_unknown    = args.ignore_unknown,
        convert_unknown   = args.convert_unknown,
        overwrite         = args.overwrite,
        dataset_files     = args.dataset_files,
    )

    if args.ignore_unknown and args.convert_unknown is not None:
        print_error_exit("Options --ignore_unknown and --convert_unknown cannot be used at the same time.")

    require_readable_directory(args.dicom_study_path)
    require_output_directory(args.bids_dataset_path)

    if args.convert_unknown is not None:
        require_output_directory(args.convert_unknown)
        require_empty_directory(args.convert_unknown)

    # Run the script.

    mni_7t_dicom_to_bids(
        args.dicom_study_path,
        args.bids_dataset_path,
        args.subject,
        args.session,
        args.ignore_unknown,
        args.convert_unknown,
        args.dataset_files,
        args.overwrite,
    )

    print('Success !')


if __name__ == '__main__':
    main()
