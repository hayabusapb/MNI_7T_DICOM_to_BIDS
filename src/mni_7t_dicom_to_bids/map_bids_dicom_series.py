from bic_util.print import print_error_exit
from bic_util.util import find

from mni_7t_dicom_to_bids.dataclass import BidsAcquisitionInfo, BidsAcquisitionMapping, DicomSeriesInfo
from mni_7t_dicom_to_bids.variables import bids_dicom_ignores, bids_dicom_mappings


def map_bids_dicom_series(
    dicom_series_entries: list[DicomSeriesInfo],
    ignore_unknown: bool,
) -> tuple[list[BidsAcquisitionMapping], list[DicomSeriesInfo]]:
    """
    Map the DICOM series of a DICOM study to BIDS acquisition mappings and unknown DICOM series
    according to the MNI 7T DICOM to BIDS converter.
    """

    bids_acquisition_mappings: list[BidsAcquisitionMapping] = []
    unknown_dicom_series: list[DicomSeriesInfo] = []

    for dicom_series in dicom_series_entries:
        if ignore_dicom_series(dicom_series):
            print(f"Ignore DICOM series '{dicom_series.description}'.")
            continue

        bids_acquisition = get_bids_acquisition_info(dicom_series)
        if bids_acquisition is None:
            if ignore_unknown:
                unknown_dicom_series.append(dicom_series)
                continue

            print_error_exit(f"No BIDS mapping found for DICOM series '{dicom_series.description}'.")

        add_bids_dicom_mapping(bids_acquisition_mappings, bids_acquisition, dicom_series)

    bids_acquisition_mappings.sort(key=lambda mapping: (mapping.acquisition.scan_type, mapping.acquisition.scan_type))

    return bids_acquisition_mappings, unknown_dicom_series


def add_bids_dicom_mapping(
    bids_acquisition_mappings: list[BidsAcquisitionMapping],
    bids_acquisition: BidsAcquisitionInfo,
    dicom_series: DicomSeriesInfo,
):
    """
    Add a mapping between a BIDS acquisition and a DICOM series in the BIDS acquisitions to DICOM
    series mappings.
    """

    bids_acquisition_mapping = find(lambda mapping: mapping.acquisition == bids_acquisition, bids_acquisition_mappings)

    if bids_acquisition_mapping is None:
        bids_acquisition_mapping = BidsAcquisitionMapping(
            acquisition  = bids_acquisition,
            dicom_series = [],
        )

        bids_acquisition_mappings.append(bids_acquisition_mapping)

    bids_acquisition_mapping.dicom_series.append(dicom_series)


def ignore_dicom_series(dicom_series: DicomSeriesInfo) -> bool:
    """
    Check if a DICOM series should be ignored as per the MNI 7T DICOM to BIDS converter parameters.
    """

    for bids_dicom_ignore in bids_dicom_ignores:
        if dicom_series.description == bids_dicom_ignore:
            return True

    return False


def get_bids_acquisition_info(dicom_series: DicomSeriesInfo) -> BidsAcquisitionInfo | None:
    """
    Return the BIDS parameters of a DICOM series as per the MNI 7T DICOM to BIDS converter
    conversion parameters.
    """

    for bids_scan_type, bids_dicom_mapping in bids_dicom_mappings.items():
        for bids_file_name, bids_dicom_series_descriptions in bids_dicom_mapping.items():
            if isinstance(bids_dicom_series_descriptions, str):
                bids_dicom_series_descriptions = [bids_dicom_series_descriptions]

            for bids_dicom_series_description in bids_dicom_series_descriptions:
                if dicom_series.description == bids_dicom_series_description:
                    return BidsAcquisitionInfo(
                        scan_type = bids_scan_type,
                        file_name = bids_file_name,
                    )

    return None
