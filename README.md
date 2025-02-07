# MPN DICOM to BIDS converter

This project contains the Montreal Paris NeuroBank DICOM to BIDS converter.

# Installation

## PIP

To install the project with PIP, install the following packages in the relevant Python environment:

```
pip install git+https://github.com/BIC-MNI/BIC_MRI_pipeline_util.git
pip install git+https://github.com/BIC-MNI/MPN_DICOM_to_BIDS.git
```

You must also have (https://github.com/rordenlab/dcm2niix)[dcm2niix] (preferably a more recent version) installed on your machine.

## Docker

To install the projet with Docker, clone the GitHub repository and run the Docker builder:

```
git clone https://github.com/BIC-MNI/MPN_DICOM_to_BIDS.git mpn_dicom_to_bids
docker build mpn_dicom_to_bids -t mpn_dicom_to_bids
```

# Execution

You can run the MPN DICOM to BIDS converter using the following command:

```
mpn_dicom_to_bids <input_dicom_dir_path> <output_bids_dir_path> --subject <subject_label> --session <session_label>
```

The input DICOM directory must contain the DICOMs of a single session. The output BIDS directory can either be an empty directory (which can be created by the script) or be an existing MPN BIDS directory (in which case the converted session is added to the existing BIDS).
