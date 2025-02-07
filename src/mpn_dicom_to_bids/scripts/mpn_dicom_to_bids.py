#!/usr/bin/env python

import argparse
import os
from dataclasses import dataclass

from bic_util.fs import require_output_directory, require_readable_directory

from mpn_dicom_to_bids.pipeline import mpn_dicom_to_bids


def main():

    # Parse CLI arguments

    parser = argparse.ArgumentParser(
        prog='mpn_dicom_to_bids',
        description='Run the MPN DICOM to BIDS script on a DICOM directory',
    )

    parser.add_argument('input_dicom_dir_path',
        help='Path of the input DICOM directory.')

    parser.add_argument('output_bids_dir_path',
        help='Path of the output BIDS directory.')

    parser.add_argument('--subject',
        required=True,
        help='BIDS subject label.')

    parser.add_argument('--session',
        required=True,
        help='BIDS session label.')

    parser.add_argument('--overwrite',
        action='store_true',
        help='Overwrite the static dataset files in the BIDS directory if needed.')

    args = parser.parse_args()

    # Process CLI arguments

    @dataclass
    class Args:
        input_dicom_dir_path: str
        output_bids_dir_path: str
        subject: str
        session: str
        overwrite: bool

    args = Args(
        input_dicom_dir_path = os.path.normpath(args.input_dicom_dir_path),
        output_bids_dir_path = os.path.normpath(args.output_bids_dir_path),
        subject        = args.subject,
        session        = args.session,
        overwrite      = args.overwrite,
    )

    require_readable_directory(args.input_dicom_dir_path)
    require_output_directory(args.output_bids_dir_path)

    mpn_dicom_to_bids(args.input_dicom_dir_path, args.output_bids_dir_path, args.subject, args.session, args.overwrite)

    print('Success !')
