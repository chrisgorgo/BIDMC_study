import os
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.interfaces.io as nio           # Data i/o

from confidential_variables import subjects
from nipype.interfaces.dcm2nii import Dcm2nii

data_dir = os.path.abspath('/media/data/rojas/')

info = dict(FSPGR = [['subject_id','FSPGR_3D_[0-9]']],
            Foot_Movement = [['subject_id', 'fMRI_Foot_Movement_[0-9]']],
            Hand_Movement = [['subject_id', 'fMRI_Hand_Movement_[0-9]']],
            Language = [['subject_id', 'fMRI_Language_[0-9]']])

subjects_infosource = pe.Node(interface=util.IdentityInterface(fields=['subject_id']),
                     name="subjects_infosource")
subjects_infosource.iterables = ('subject_id', subjects)

datasource = pe.Node(interface=nio.DataGrabber(infields=['subject_id'],
                                               outfields=info.keys()),
                     name = 'datasource')

datasource.inputs.base_directory = data_dir
datasource.inputs.template = '%s/*/%s*/*0001.dcm'
datasource.inputs.template_args = info

dcm2nii_struct = pe.Node(interface=Dcm2nii(anonymize= True), name="dcm2nii_struct")
dcm2nii_hand = pe.Node(interface=Dcm2nii(anonymize= True), name="dcm2nii_hand")
dcm2nii_foot = pe.Node(interface=Dcm2nii(anonymize= True), name="dcm2nii_foot")
dcm2nii_language = pe.Node(interface=Dcm2nii(anonymize= True), name="dcm2nii_language")

def getReportFilename(subject_id):
    return "subject_%s_report.pdf"%subject_id

main_pipeline = pe.Workflow(name="pipeline")
main_pipeline.base_dir = os.path.join(data_dir,"workdir")
main_pipeline.connect([
                       (subjects_infosource, datasource, [('subject_id', 'subject_id')]),
                       (datasource, dcm2nii_struct, [('FSPGR', 'source_names')]),
                       (datasource, dcm2nii_hand, [('Hand_Movement', 'source_names')]), 
                       (datasource, dcm2nii_foot, [('Foot_Movement', 'source_names')]), 
                       (datasource, dcm2nii_language, [('Language', 'source_names')])          
                       ])

main_pipeline.run()
