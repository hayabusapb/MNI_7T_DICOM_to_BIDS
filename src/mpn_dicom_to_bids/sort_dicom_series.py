import os

import pydicom
from bic_util.fs import count_dir_files
from bic_util.print import get_progress_printer
from bic_util.util import find

from mpn_dicom_to_bids.dataclass import DicomSeriesInfo


def sort_dicom_series(dicom_dir_path: str) -> list[DicomSeriesInfo]:
    """
    Read a DICOM directory and sort all the DICOM files according to their series description and
    series number.
    """

    files_count = count_dir_files(dicom_dir_path)

    progress = get_progress_printer(files_count)

    dicom_series_entries: list[DicomSeriesInfo] = []

    for dicom_file in os.scandir(dicom_dir_path):
        progress()

        dicom = pydicom.dcmread(dicom_file.path)  # type: ignore

        dicom_series = find(
            lambda dicom_series: (
                dicom_series.description == dicom.SeriesDescription
                and dicom_series.number == dicom.SeriesNumber
            ),
            dicom_series_entries,
        )

        if dicom_series is None:
            dicom_series = DicomSeriesInfo(
                description = dicom.SeriesDescription,
                number      = dicom.SeriesNumber,
                file_paths         = [],
            )

            dicom_series_entries.append(dicom_series)

        dicom_series.file_paths.append(dicom_file.path)

        # TODO: Handle session numbers.

    dicom_series_entries.sort(key=lambda dicom_series: dicom_series.number)

    return dicom_series_entries
