# MNI 7T DICOM to BIDS converter

This project is the MNI 7T DICOM to BIDS converter, which is used at the Montreal Neurological Institute-Hospital to convert 7 Tesla DICOM scans to BIDS.

## Installation

### PIP

To install the converter with PIP, install the following packages in the relevant Python environment:

```sh
pip install git+https://github.com/BIC-MNI/BIC_MRI_pipeline_util
pip install git+https://github.com/BIC-MNI/MNI_7T_DICOM_to_BIDS
```

You must also have [dcm2niix](https://github.com/rordenlab/dcm2niix) (preferably a more recent version) installed on your machine.

### Docker

To install the converter with Docker, clone the GitHub repository and build the project using the `run.Dockerfile` file:

```sh
git clone https://github.com/BIC-MNI/MNI_7T_DICOM_to_BIDS mni_7t_dicom_to_bids
docker build -t mni_7t_dicom_to_bids -f mni_7t_dicom_to_bids/run.Dockerfile mni_7t_dicom_to_bids
```

## Compilation

This project can be compiled and distributed as an executable using PyInstaller, the compilation process is described in the [`COMPILATION.md`](./COMPILATION.md) file.

## Execution

You can run the MNI 7T DICOM to BIDS converter using the following command:

```sh
mni7t_dcm2bids <dicom_study_path> <bids_dataset_path> --subject <subject_label> --session <session_label>
```

The input DICOM directory must contain the DICOMs of a single session. The output BIDS directory can either be an empty directory (which can be created by the script) or be an existing BIDS directory (in which case the converted session is added to the existing BIDS).
