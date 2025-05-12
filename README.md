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

### Setup

To more easily distribute the MNI 7T DICOM to BIDS converter, this project can be compiled into an executable by using PyInstaller.

Compiling a package with PyInstaller requires the Python header files, which can be installed using the following command:

```sh
sudo apt install python3.11-dev
```

PyInstaller is a development dependency of the project, and can be installed as such using the following command in the project directory:

```sh
pip install .[dev]
```

### Configuration

The PyInstaller configuration of the MNI 7T DICOM to BIDS converter is saved in the `mni_7t_dicom_to_bids.spec` file. To regenerate this configuration, use the following command in the project root directory:

```sh
pyi-makespec --onefile --name mni_7t_dicom_to_bids --add-data src/mni_7t_dicom_to_bids/assets:mni_7t_dicom_to_bids/assets src/mni_7t_dicom_to_bids/scripts/run_mni_7t_dicom_to_bids.py
```

### Compilation (local compatibility)

To compile the MNI 7T DICOM to BIDS converter, use the following command in the project root directory:

```sh
pyinstaller mni_7t_dicom_to_bids.spec
```

This will create a `dist/mni_7t_dicom_to_bids` executable for the MNI 7T DICOM to BIDS converter.

### Compilation (maximum compatibility)

The executable of a project compiled with PyInstaller may be depend on the `glibc` version of the system on which it was compiled. As such, the MNI 7T DICOM to BIDS includes a `compile.Dockerfile` file designed to build the project using an old `glibc` version such that the executable created is compatible with Debian 10 or more recent Debian-based systems.

To build the Docker image for the compiler, use the following command in the project root directory:

```sh
docker build -t compile_mni_7t_dicom_to_bids -f compile.Dockerfile .
```

To compile the using the previously built Docker image, use the following command while replacing `TARGET_DIRECTORY_PATH` by the directory in which to create the executable:

```sh
docker run --mount type=bind,src=TARGET_DIRECTORY_PATH,dst=/mni_7t_dicom_to_bids/dist compile_mni_7t_dicom_to_bids
```

## Execution

You can run the MNI 7T DICOM to BIDS converter using the following command:

```sh
mni_7t_dicom_to_bids <input_dicom_dir_path> <output_bids_dir_path> --subject <subject_label> --session <session_label>
```

The input DICOM directory must contain the DICOMs of a single session. The output BIDS directory can either be an empty directory (which can be created by the script) or be an existing BIDS directory (in which case the converted session is added to the existing BIDS).
