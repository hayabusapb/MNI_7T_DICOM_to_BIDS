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
### Apptainer / Singularity (HPC deployment)

To install the converter with Apptainer, clone the Github repository (APB forked main branch) and build the project using Apptainer recipe file (.def):

```sh
git clone https://github.com/hayabusapb/MNI_7T_DICOM_to_BIDS
apptainer build <IMAGE.sig> ./MNI_7T_DICOM_to_BIDS/MPN7T.def
```
The apptainer container is by default rootless and contain all stand alone dependencies to run in HPC. 
Its size is 448.5MB, tested as per dist. Apptainer 1.4.1 
To execute from container do module load apptainer in HPC of choice, then execute as:

```sh
IN="<PATH_TO_DICOM>"
OUT="<PATH_TO_BIDS>"
IMG="<PATH_TO_IMAGE.sif>"
SUB="<SUBJECT_ID>"
SESSION="<SESSION>"
apptainer exec --bind ${IN}:/mnt_IN,${OUT}:/mnt_OUT $IMG mni7t_dcm2bids /mnt_IN /mnt_OUT --subject $SUB --session $SESSION
```
Alternatively a frozen image can be obtained here:
https://zenodo.org/records/17072935

## Execution

You can run the MNI 7T DICOM to BIDS converter using the following command:

```sh
mni7t_dcm2bids <dicom_study_path> <bids_dataset_path> --subject <subject_label> --session <session_label>
```
* To run from container (e.g apptainer), make sure to bind directories before executing such as described in the example below

Inputs must be provided as strings matching exactly participants provided input data. The input DICOM directory must contain the DICOMs of a single session (No Metafile in this directory). The output BIDS directory can either be an empty directory (which can be created by the script) or be an existing BIDS directory (in which case the converted session is added to the existing BIDS). 

## BIDS naming dictionary

### Anatomical

| **N** | **7T Terra Siemens acquisition**                   | **BIDS**                            | **Directory** |
|:-----:|:--------------------------------------------------:|:-----------------------------------:|:-------------:|
|   1   |  anat-T1w_acq_mprage_0.8mm_CSptx                   | T1w                                 | anat          |
|   2   |  anat-T1w_acq-mp2rage_0.7mm_CSptx_INV1             | inv-1_MP2RAGE                       | anat          |
|   3   |  anat-T1w_acq-mp2rage_0.7mm_CSptx_INV2             | inv-2_MP2RAGE                       | anat          |
|   4   |  anat-T1w_acq-mp2rage_0.7mm_CSptx_T1_Images        | T1map                               | anat          |
|   5   |  anat-T1w_acq-mp2rage_0.7mm_CSptx_UNI_Images       | UNIT1                               | anat          |
|   6   |  anat-T1w_acq-mp2rage_0.7mm_CSptx_UNI-DEN          | desc-denoised_UNIT1                 | anat          |
|   7   |  anat-flair_acq-0p7iso_UPAdia                      | FLAIR                               | anat          |
|   8   |  CLEAR-SWI_anat-T2star_acq-me_gre_0\*7iso_ASPIRE   | acq-SWI_T2starw                     | anat          |
|   9   |  Romeo_P_anat-T2star_acq-me_gre_0\*7iso_ASPIRE     | acq-romeo_T2starw                   | anat          |
|  10   |  Romeo_Mask_anat-T2star_acq-me_gre_0\*7iso_ASPIRE  | acq-romeo_desc-mask_T2starw         | anat          |
|  11   |  Romeo_B0_anat-T2star_acq-me_gre_0\*7iso_ASPIRE    | acq-romeo_desc-unwrapped_T2starw    | anat          |
|  12   |  Aspire_M_anat-T2star_acq-me_gre_0\*7iso_ASPIRE    | acq-aspire_part-mag_T2starw         | anat          |
|  13   |  Aspire_P_anat-T2star_acq-me_gre_0\*7iso_ASPIRE    | acq-aspire_part-phase_T2starw       | anat          |
|  14   |  EchoCombined_anat-T2star_acq-me_gre_0\*7iso_ASPIRE | acq-aspire_desc-echoCombined_T2starw | anat          |
|  15   |  sensitivity_corrected_mag_anat-T2star_acq-me_gre_0\*7iso_ASPIRE | acq-aspire_desc-echoCombinedSensitivityCorrected_T2starw | anat |
|  16   |  T2star_anat-T2star_acq-me_gre_0\*7iso_ASPIRE      | acq-aspire_[T2starw,T2starmap]      | anat          |
|  17   |  anat-mtw_acq-MTON_07mm                            | acq-mtw_mt-on_MTR                   | anat          |
|  18   |  anat-mtw_acq-MTOFF_07mm                           | acq-mtw_mt-off_MTR                  | anat          |
|  19   |  anat-mtw_acq-T1w_07mm                             | acq-mtw_T1w                         | anat          |
|  20   |  anat-nm_acq-MTboost_sag_0.55mm                    | acq-neuromelaninMTw_T1w             | anat          |
|  21   |  anat-angio_acq-tof_03mm_inplane                   | angio                               | anat          |
|  22   |  anat-angio_acq-tof_03mm_inplane_MIP_SAG           | acq-sag_angio                       | anat          |
|  23   |  anat-angio_acq-tof_03mm_inplane_MIP_COR           | acq-cor_angio                       | anat          |
|  24   |  anat-angio_acq-tof_03mm_inplane_MIP_TRA           | acq-tra_angio                       | anat          |

> The acquisitions `acq-romeo_part-phase_T2starw`, `acq-aspire_part-mag_T2starw`, and `acq-aspire_part-phase_T2starw` each have five echoes. The final string will include the identifier `echo-` followed by the echo number. For example: `acq-aspire_echo-1_part-mag_T2starw`.

### Field maps

| **N** | **7T Terra Siemens acquisition**    | **BIDS**               | **Directory** |
|:-----:|:-----------------------------------:|:----------------------:|:-------------:|
|  1    | fmap-b1_tra_p2                      | acq-[anat,sfam]_TB1TFL | fmap          |
|  2    | fmap-b1_acq-sag_p2                  | acq-[anat,sfam]_TB1TFL | fmap          |
|  3    | fmap-fmri_acq-mbep2d_SE_19mm_dir-AP | acq-fmri_dir-AP_epi    | fmap          |
|  4    | fmap-fmri_acq-mbep2d_SE_19mm_dir-PA | acq-fmri_dir-PA_epi    | fmap          |

### Functional

| **N** | **7T Terra Siemens acquisition** | **BIDS**           | **Directory** |
|:-----:|:--------------------------------:|:------------------:|:-------------:|
|  1    | func-cross_acq-ep2d_MJC_19mm     | task-rest_bold     | func          |
|  2    | func-cloudy_acq-ep2d_MJC_19mm    | task-cloudy_bold   | func          |
|  3    | func-present_acq-mbep2d_ME_19mm  | task-present_bold  | func          |

> Each functional MRI acquisition includes three echoes and a phase. The final string will contain the identifier `echo-` followed by the echo number (e.g., `task-rest_echo-1_bold`). Additionally, the string `part-phase` will be included to identify the phase (e.g., `task-rest_echo-1_part-phase_bold`).

### Diffusion weighted images

| **N** | **7T Terra Siemens acquisition**    | **BIDS**                  | **Directory** |
|:-----:|:-----------------------------------:|:-------------------------:|:-------------:|
|  1    | *dwi_acq_b0_PA                      | acq-b0_dir-PA_dwi         | dwi           |
|  2    | *dwi_acq_b0_PA_SBRef                | acq-b0_dir-PA_sbref       | dwi           |
|  3    | *dwi_acq_multib_38dir_AP_acc9       | acq-multib38_dir-AP_dwi   | dwi           |
|  4    | *dwi_acq_multib_38dir_AP_acc9_SBRef | acq-multib38_dir-AP_sbref | dwi           |
|  5    | *dwi_acq_multib_70dir_AP_acc9       | acq-multib70_dir-AP_dwi   | dwi           |
|  6    | *dwi_acq_multib_70dir_AP_acc9_SBRef | acq-multib70_dir-AP_sbref | dwi           |

> The string `part-phase` will be included to identify the phase acquisitions (e.g., `acq-multib38_dir-AP_part-phase_dwi`).

### Abbreviation Glossary

| **Abbreviation** | **Description**                                               |
|------------------|---------------------------------------------------------------|
| **AP**           | Anterio-Posterior                                             |
| **PA**           | Postero-anterior                                              |
| **mtw**          | Magnetic transfer weighted                                    |
| **sfmap**        | Scaled flip angle map                                         |
| **tof**          | Time of flight                                                |
| **multib**       | Multi shell N directions                                      |
| **semphon**      | Semantic-phonetic                                             |
| **romeo**        | Rapid opensource minimum spanning tree algorithm              |
| **aspire**       | Combination of multi-channel phase data from multi-echo acquisitions |

### References

1. Eckstein K, Dymerska B, Bachrata B, Bogner W, Poljanc K, Trattnig S, Robinson SD. Computationally efficient combination of multi‐channel phase data from multi‐echo acquisitions (ASPIRE). Magnetic resonance in medicine. 2018 Jun;79(6):2996-3006. https://doi.org/10.1002/mrm.26963

2. Dymerska B, Eckstein K, Bachrata B, Siow B, Trattnig S, Shmueli K, Robinson SD. Phase unwrapping with a rapid opensource minimum spanning tree algorithm (ROMEO). Magnetic resonance in medicine. 2021 Apr;85(4):2294-308. https://doi.org/10.1002/mrm.28563

3. Sasaki M, Shibata E, Tohyama K, Takahashi J, Otsuka K, Tsuchiya K, Takahashi S, Ehara S, Terayama Y, Sakai A. Neuromelanin magnetic resonance imaging of locus ceruleus and substantia nigra in Parkinson's disease. Neuroreport. 2006 Jul 31;17(11):1215-8. https://doi.org/10.1097/01.wnr.0000227984.84927.a7

## Compilation

This project can be compiled and distributed as an executable using PyInstaller, the compilation process is described in the [`COMPILATION.md`](./COMPILATION.md) file.

## Related repositories

This DICOM to BIDS converter is a rewrite of Raul Cruces' [MPN 7T pipeline DICOM to BIDS converter](https://github.com/rcruces/MPN_7T_pipeline). The present converter aims to provide a similar behavior (up to versions) with enhanced safety checks, portability, performance, and maintainability.
