from Modules.MRI.MRI import MRI
from Modules.MRI.DICOM import DICOM
from Modules.MRI.Nifti_dump import Nifti_dump

types_list = (DICOM, Nifti_dump)

def select(folder: str):
    for cls in types_list:
        if cls.isValidRecording(folder):
            return cls
    return None

def select_by_name(name: str):
    for cls in types_list:
        if cls.__name__ == name:
            return cls
    return None
