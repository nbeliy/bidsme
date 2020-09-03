# Supported formats

- [Supported formats](#supported-formats)
	- [<a name="mri"></a> MRI](#-mri)
		- [<a name="dicom"></a> DICOM](#-dicom)
		- [<a name="hmriNIFTI"></a> hmriNIFTI](#-hmrinifti)
		- [<a name="bidsmeNIFTI"></a> bidsmeNIFTI](#-bidsmenifti)
		- [<a name=jsonNIFTI></a> jsonNIFTI](#-jsonnifti)
		- [<a name=NIFTI> </a> NIFTI](#-nifti)
	- [<a name="eeg"></a>EEG](#eeg)
		- [<a name="BV"></a>BrainVision](#brainvision)

BIDSme was designed for supporting different types of data (MRI, PET, EEG...)
and various data-files format. This is achieved using object-oriented approach.

Each data-type is viewed as sub-module of `Modules` and inherits from base class
`baseModule`, which defines the majority of logic needed for bidsification.

The sub-modules main classes (e.g. `Modules/MRI/MRI.py`) defines the bids-related 
information defines for this particular data-type, like the list of needed metadata for
JSON sidecar file or list of modalities and entities.

Finally for each data-type, several file-formats are treated by a separate class, that 
inherits from corresponding data-type class (e.g. `Modules/MRI/Nifti_SPM12.py`).
This class defines how extract needed meta-data from a particular file, how identify
a file, and similar file-related operations.	

## <a name="mri"></a> MRI

`MRI` data-type integrated all MRI images. The corresponding BIDS formatting can be
found [there](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html).

It defines the following modalities:
- **anat** for [anatomical images](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#anatomy-imaging-data)
- **func** for [functional images](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#task-including-resting-state-imaging-data)
- **dwi** for [diffusion images](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#diffusion-imaging-data)
- **fmap** for [fieldmaps](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#fieldmap-data)

### <a name="dicom"></a> DICOM

BIDSme support generic raw [DICOM](https://www.dicomstandard.org/) file format. 
Attributes extraction rely on [`pydicom`](https://pydicom.github.io/pydicom/stable/index.html) library.

DICOM files are identified by an extension `.dcm` and `.DCM`, and by word `DICM` placed in file at  `0x80`.

Attributes can be retrieved using both the DICOM tag and keyword (if defined).
For example `getField("InstanceCreationDate")` and `getField("(008, 0012)")` will both retrieve the same 
`Instance Creation Date`.
Tags must be **exatctly** in form of string formatted as follows: `"(%04d, %04d)"`, and the tag numbers
must be put in hexadecimal form without `0x` prefix -- the same way as DICOM tags are usually depicted.
Retrieved values are parsed if possible into python base values: `int`, `float`, `str`, `datetime.date`, 
`datetime.time` and `datetime.datetime`.

Nested values are retrieved using `/` separator, for example `getField("(2005, 140f)/0/PixelPresentation")` 
will retrieve Pixel Presentation value from private tag.
The navigation follows the same structure as pydicom: `ds[0x2005, 0x140f][0]["PixelPresentation"]`.
To retrieve values with multiplicity an index addressing each value must be used.
For example if `(0008, 0008) Image Type` is `['ORIGINAL', 'PRIMARY', 'M_FFE', 'M', 'FFE']`,
it can be accessed by `getField("ImageType/0") -> 'ORIGINAL'`. 

For convenience, during the preparation step, the full dump of DICOM header is created in form of JSON file
`dcm_dump_<dicom file name>.json`. 
In this dump, dataset structure is represented as dictionary, multi-values and sequences as lists.

### <a name="hmriNIFTI"></a> hmriNIFTI

`hmriNIFTI` data-format is a DICOM files converted to Nifti format by 
[hMRI toolbox](https://www.sciencedirect.com/science/article/pii/S1053811919300291) for 
[SPM12](https://www.fil.ion.ucl.ac.uk/spm/software/spm12/). 
Essentially it consists by a nifti image data and a JSON file with DICOM header dumped into it.

All recording attributes are retrieved from `acqpar[0]` dictionary within json file,
requesting directly the name of corresponding field: `getField("SeriesNumber") -> 4`
In case of nested dictionaries, for ex. `"[CSAImageHeaderInfo"]["RealDwellTime"]`,
a field separator `/` should be used: 
```
getField("CSAImageHeaderInfo/RealDwellTime") -> 2700
```
In case of lists, individual elements are retrieved by passing the index:
```
getField("AcquisitionMatrix[3]") -> 72
```

The additional fields, that are not stored directly in JSON file, are calculated:
- **DwellTime** is retrieved from private field with tags `(0019,1018)` and converted from 
micro-seconds to seconds. 
- **NumberOfMeasurements** are retrieved from `lRepetitions` field and incremented by one.
- **PhaseEncodingDirection** are retrieved from `PhaseEncodingDirectionPositive`, and transformed 
to `1`(positive) or `-1`(negative)
- **B1mapNominalFAValues** are reconstructed from `adFree` and `alFree`. The exact reconstruction 
alghorytm is sequence dependent. 
- **B1mapMixingTime** are reconstructed from `adFree` and `alFree`. The exact reconstruction 
alghorytm is sequence dependent. 
- **RFSpoilingPhaseIncrement** are reconstructed from `adFree` and `alFree`. The exact reconstruction 
alghorytm is sequence dependent.
- **MTState** is retrieved from `[CSASeriesHeaderInfo"]["MrPhoenixProtocol"]["sPrepPulses"]` and set either 
to `On` of `Off`

> **Warning** These fields are guaranteed to be in the Siemens DICOM files, in case different origin, their
implementation must be either patched up or performed in plugins.

> **Warning** `B1mapNominalFAValues`, `B1mapMixingTime` and `RFSpoilingPhaseIncrement` are sequence
dependent. It is unclear to me if sequences names are standard or not. If outcome of these values produces
incorrect output, the correction must be either patched or corrected in plugin.

### <a name="bidsmeNIFTI"></a> bidsmeNIFTI

`bidsmeNIFTI` dataformat is a generic NIFTI data file with a accompaigned DICOM header created
by BIDSme from original DICOM file, as described in [MRI/DICOM](#dicom) section.
It was introduced in order to use user-preferred DICOM converting tools without loosing any meta-data
from the initial file.

The JSON file conserves the same structure as original DICOM, with conservation of DICOM key words
if defined and tags (in form `"(%04d, %04d)"`) if not.

Te expected procedure to use this format is following:

	1. DICOM dataset is prepared as described [there](#wf_prep).
	2. DICOM files are converted to NIFTI format using tool of preference, but conserving the file
name (modulo the extention).
	3. DICOM files must be removed from prepared folder together with any JSON files created by 
converter to avoid data format mis-identifications and file double-counting.
	4 [process](#wf_process) and [bidsify](#wf_bidsify) steps will now use 
`dcm_dump_<dicom file name>.json`to identify recordings.

### <a name=jsonNIFTI></a> jsonNIFTI

A lot of DICOM converters create a JSON file containing extracted meta-data. 
What metadata and how it is stored may vary unpredictably from one converter to another.

`jsonNIFTI` is an attempt to incorporate such converted files. 
The metadata is extracted from JSON file using same procedure as for [hmriNIFTI](#hmriNIFTI):
```
getField("CSAImageHeaderInfo/RealDwellTime") -> 2700
```

### <a name=NIFTI> </a> NIFTI

A generic Nifti format implements [NIfti file format](os.path.join(directory, bidsname).
It's supports `ni1` (`.hdr + .img` files), `n+1` and `n+2` (`.nii`) formats.

Nifti files are identified by extension, either `.hdr` or `.nii`, and 
the first 4 bytes of file: it must encode either `348` or `540`. 
As Nifti do not impose the endianess of file, both little and big 
endiannes is checked.

Base attributes are extracted directly from header, and conserve 
the name as defined
[here](https://brainder.org/2012/09/23/the-nifti-file-format/)
and [here](https://brainder.org/2015/04/03/the-nifti-2-file-format/),
or alternatively in `C` header file for 
[`ni1/n+1`](https://nifti.nimh.nih.gov/pub/dist/src/niftilib/nifti1.h)
and [`n+2`](https://nifti.nimh.nih.gov/pub/dist/doc/nifti2.h).
For example, the image x-dimension can be accessed by
`getAttribute("dim/1")`.

The Nifti header do not contain information used to identify given
recording, like protocol name, subject Id, Sequence etc.
To identify recordings these values must be set in plugins using
`setAttribute(name, value)` function.
If they are not set manually, a default value will be used.
If filename is formatted in bids-like way, the default subject Id 
and session Id are extracted from file name, if not a null value `None`
will be used.

|Attribute name| Default value|
|--------------------|------------------|
|`PatientId`			| `sub-<subId>` or `None` |
|`SessionId`			| `ses-<sesId>` or `None` |
|`RecordingId`		| filename without extension |
|`RecordingNumber`	| index of current file |
|`AcquisitionTime`		| `None`|


## <a name="eeg"></a>EEG

`EEG` data-type integrated all EEG recordings. 
The corresponding BIDS formatting can be
found [there](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/03-electroencephalography.html).

It defines the modality **eeg**.
Outside the data files, BIDS requires also export of channels and events
(if present) data in `.tsv` files accompanied by sidecar JSON file.

### <a name="BV"></a>BrainVision