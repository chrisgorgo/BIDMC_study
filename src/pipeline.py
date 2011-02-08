import os
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.interfaces.io as nio           # Data i/o
from neuroutils.helper_functions import create_pipeline_functional_run

from confidential_variables import subjects
from nipype.interfaces.dcm2nii import Dcm2nii
from nipype.utils.filemanip import split_filename
import neuroutils
from nipype.interfaces.utility import Merge

data_dir = os.path.abspath('/home/filo/data/rojas/')

info = dict(FSPGR = [['subject_id','co_FSPGR_3D']],
            Foot_Movement = [['subject_id', 'fMRI_Foot_Movement_[0-9]']],
            Hand_Movement = [['subject_id', 'fMRI_Hand_Movement_[0-9]']],
            Language = [['subject_id', 'fMRI_Language_[0-9]']])

subjects_infosource = pe.Node(interface=util.IdentityInterface(fields=['subject_id']),
                     name="subjects_infosource")
subjects_infosource.iterables = ('subject_id', subjects)

datasource = pe.Node(interface=nio.DataGrabber(infields=['subject_id'],
                                               outfields=info.keys()),
                     name = 'datasource', overwrite=True)

datasource.inputs.base_directory = data_dir
#datasource.inputs.template = '%s/*/%s*/*0001.dcm'
datasource.inputs.template = '%s/*/*%s*.nii'
datasource.inputs.template_args = info

#dcm2nii_struct = pe.Node(interface=Dcm2nii(anonymize= True), name="dcm2nii_struct")
#dcm2nii_hand = pe.Node(interface=Dcm2nii(anonymize= True), name="dcm2nii_hand")
#dcm2nii_foot = pe.Node(interface=Dcm2nii(anonymize= True), name="dcm2nii_foot")
#dcm2nii_language = pe.Node(interface=Dcm2nii(anonymize= True), name="dcm2nii_language")

language = create_pipeline_functional_run(name="language", 
                                                  conditions=['Task'], 
                                                  onsets=[range(0,100,20)],
                                                  durations=[[10]],
                                                  tr=3.0, 
                                                  contrasts=[('Task','T', ['Task'],[1])],
                                                  units='scans',
                                                  n_slices=30,
                                                  n_skip=0)

hand = create_pipeline_functional_run(name="hand", 
                                                  conditions=['Right', 'Left'], 
                                                  onsets=[range(0,150,40), range(20,150,40)],
                                                  durations=[[10], [10]],
                                                  tr=2.0, 
                                                  contrasts=[('Both','T', ['Right', 'Left'],[1, 1]),
                                                             ('Right', 'T', ['Right'], [1]),
                                                             ('Left', 'T', ['Left'], [1])],
                                                  units='scans',
                                                  n_slices=30,
                                                  n_skip=0)

foot = create_pipeline_functional_run(name="foot", 
                                                  conditions=['Right', 'Left'], 
                                                  onsets=[range(0,150,40), range(20,150,40)],
                                                  durations=[[10], [10]],
                                                  tr=2.0, 
                                                  contrasts=[('Both','T', ['Right', 'Left'],[1, 1]),
                                                             ('Right', 'T', ['Right'], [1]),
                                                             ('Left', 'T', ['Left'], [1])],
                                                  units='scans',
                                                  n_slices=30,
                                                  n_skip=0)

def getReportFilename(subject_id):
    return "subject_%s_report.pdf"%subject_id

def pickCo(list):
    for item in list:
        _,base,_ = split_filename(item)
        if base.startswith("co"):
            return item
        
mergeinputs = pe.Node(interface=Merge(3), name="mergeinputs")

subject_report = pe.Node(interface = neuroutils.PsMerge(), name = "subject_report")

main_pipeline = pe.Workflow(name="pipeline")
main_pipeline.base_dir = os.path.join(data_dir,"workdir")
main_pipeline.connect([
                       (subjects_infosource, datasource, [('subject_id', 'subject_id')]),
#                       (datasource, dcm2nii_struct, [('FSPGR', 'source_names')]),
#                       (datasource, dcm2nii_hand, [('Hand_Movement', 'source_names')]), 
#                       (dcm2nii_hand, hand, [("converted_files", "inputnode.func")]),
#                       (dcm2nii_struct, hand, [(("converted_files",pickCo),"inputnode.struct")]),
                       (datasource, hand, [("Hand_Movement", "inputnode.func"),
                                           ("FSPGR","inputnode.struct")]),
                       (hand, mergeinputs, [("report.psmerge_all.merged_file", "in1")]),  
                       
#                       (datasource, dcm2nii_foot, [('Foot_Movement', 'source_names')]),
#                       (dcm2nii_foot, foot, [("converted_files", "inputnode.func")]),
#                       (dcm2nii_struct, foot, [(("converted_files",pickCo),"inputnode.struct")]),
                       (datasource, foot, [("Foot_Movement", "inputnode.func"),
                                           ("FSPGR","inputnode.struct")]),
                       (foot, mergeinputs, [("report.psmerge_all.merged_file", "in2")]),  
                        
#                       (datasource, dcm2nii_language, [('Language', 'source_names')]),                      
#                       (dcm2nii_language, language, [("converted_files", "inputnode.func")]),
#                       (dcm2nii_struct, language, [(("converted_files",pickCo),"inputnode.struct")]),
                       (datasource, language, [("Language", "inputnode.func"),
                                               ("FSPGR","inputnode.struct")]),
                       (language, mergeinputs, [("report.psmerge_all.merged_file", "in3")]),
                       
                       (mergeinputs, subject_report, [("out", "in_files")]),
                       (subjects_infosource, subject_report, [(("subject_id", getReportFilename), "out_file")])          
                       ])

main_pipeline.run()
