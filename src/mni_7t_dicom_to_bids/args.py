import os
from argparse import Namespace
from dataclasses import dataclass

from bic_util.print import print_error_exit


@dataclass
class AbortUnknownsArg:
    pass


@dataclass
class SkipUnknownsArg:
    pass


@dataclass
class ConvertUnknownsArg:
    dir_path: str


UnknownsArg = AbortUnknownsArg | SkipUnknownsArg | ConvertUnknownsArg


@dataclass
class SkipErrorsArg:
    pass


@dataclass
class IncludeErrorsArg:
    pass


ErrorsArg = SkipErrorsArg | IncludeErrorsArg


@dataclass
class Args:
    dicom_study_path: str
    bids_dataset_path: str
    subject: str
    session: str
    unknowns: UnknownsArg
    errors: ErrorsArg
    overwrite: bool
    dataset_files: bool


def process_args(args: Namespace) -> Args:
    """
    Get the structured arguments given to the MNI 7T DICOM to BIDS converter. Exit the program with
    an error if the arguments provided are incorrect.
    """

    match args.skip_unknowns, args.convert_unknowns:
        case False, None:
            unknowns_arg = AbortUnknownsArg()
        case True, None:
            unknowns_arg = SkipUnknownsArg()
        case False, _:
            unknowns_arg = ConvertUnknownsArg(args.convert_unknowns)
        case _:
            print_error_exit("Options --skip-unknowns and --convert-unknowns cannot be used at the same time.")

    if args.include_errors:
        errors_arg = IncludeErrorsArg()
    else:
        errors_arg = SkipErrorsArg()

    return Args(
        dicom_study_path  = os.path.normpath(args.dicom_study_path),
        bids_dataset_path = os.path.normpath(args.bids_dataset_path),
        subject           = args.subject,
        session           = args.session,
        unknowns          = unknowns_arg,
        errors            = errors_arg,
        overwrite         = args.overwrite,
        dataset_files     = args.dataset_files,
    )
