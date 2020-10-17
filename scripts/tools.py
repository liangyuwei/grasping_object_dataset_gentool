#!/usr/bin/env python
import h5py
import pdb
import os
import time
import trimesh

class process_3d_models(object):

    def __init__(self, mesh_path=None, sdf_path=None, object_scale=1, h5_path=None, h5_name=None, mass=1.0):

        # Specify paths before using the related functionality
        self.sdf_path = sdf_path
        self.object_scale = object_scale
        self.h5_path = h5_path
        self.h5_name = h5_name
        self.mass = mass

        
    def generate_model_folders(self, mesh_suffix, start_index=1, mesh_in_path=None):

        time_start = time.time()

        # path to store the generated SDF files
        if self.sdf_path == None:
            print("Please specify the path to store the sdf files.")
            return
        #model_description_root = self.sdf_path #'/home/liangyuwei/Downloads/2_Models-chosen-from-KIT-3DNet-SDF/'

        # obtain model name and other information
        if self.h5_path == None or self.h5_name == None:
            print("Please specify the path to the .h5 file or its name.")
            return
        model_h5_file_path = self.h5_path + '/' + self.h5_name + '.h5' #'/home/liangyuwei/Downloads/models_chosen_from_dexnet_KIT_3DNet_SDFobtained_mesh_info.h5'
        f = h5py.File(model_h5_file_path, 'r')

        # path to the meshes
        if mesh_in_path == None:
            print("Please specify the path to copy the meshes.")
            return

        # iterate to generate the folders
        index = start_index
        for model_name in f.keys():
      
            # create a new folder
            if not os.path.exists(self.sdf_path + '/' + str(index) + '_' + model_name + '_' + str(self.object_scale)):
                os.makedirs(self.sdf_path + '/' + str(index) + '_' + model_name + '_' + str(self.object_scale))
                os.makedirs(self.sdf_path + '/' + str(index) + '_' + model_name + '_' + str(self.object_scale) + '/meshes')

            # copy the mesh files, after the folders are created
            os.system('cp ' + mesh_in_path + '/' + model_name + '.' + mesh_suffix + ' ' + self.sdf_path + '/' + str(index) + '_' + model_name + '_' + str(self.object_scale) + '/meshes/')
      

            volume = f[model_name]['volume'].value

            bounding_box_size = f[model_name]['bounding_box_size'].value        
        
            max_length = max(bounding_box_size)
            
            
            
            unit_scale = 0.1 # a specified, fixed unit for all
            sdf_scale = unit_scale * object_scale / max_length # 0.1 / max_length # change the size(max length) here
            
            com = f[model_name]['com'].value
            com_offset = [c * sdf_scale for c in com] # to cope with models that have non-centered CoM..
        
            mass = volume * sdf_scale ** 3
        
            # call the function to generate model description files
            self.generate_config_sdf(self.sdf_path, index, model_name, self.object_scale, sdf_scale, bounding_box_size*sdf_scale, mesh_suffix, com_offset, self.mass)
            
            # iterate the index
            index = index + 1    

        time_end = time.time()
        print("Total time spent: {} s".format(time_end-time_start))


    def generate_config_sdf(self, storage_path, object_index, object_name, object_scale, scale, size, mesh_suffix, com_offset, mass=1.0):

        # here `scale` is the scale tag specified in the sdf file

        # Obtain the size
        w = size[0]
        d = size[1]
        h = size[2]  
        
        # Offset to shift CoM to object's center
        c_x = com_offset[0]
        c_y = com_offset[1]
        c_z = com_offset[2]

        ## Generate file contents
        model_config_content = "\
<?xml version=\"1.0\"?>\n\
<model>\n\
  <name>" + str(object_index) + '_' + object_name + '_' + str(object_scale) + "</name>\n\
  <version>1.0</version>\n\
  <sdf version='1.6'>model.sdf</sdf>\n\
  \n\
  <author>\n\
    <name>Yuwei Liang</name>\n\
    <email>lyw.liangyuwei@gmail.com</email>\n\
  </author>\n\
  \n\
  <description>\n\
    This is an auto-generated config file.\n\
  </description>\n\
  \n\
</model>"
  
        # print(model_config_content) # check the contents

        model_sdf_content = "\
<?xml version=\"1.0\"?>\n\
\n\
<sdf version='1.6'>\n\
  <model name='" + str(object_index) + '_' + object_name + '_' + str(object_scale) + "'>\n\
    <link name='" + object_name + "'>\n\
      <pose>0 0 " + str(h / 2.0) + " 0 0 0</pose>\n\
      <inertial>\n\
        <pose>" + str(c_x) + " " + str(c_y) + " " + str(c_z) + " 0 0 0</pose>\n\
        <mass>" + str(mass) + "</mass>\n\
        <inertia>\n\
          <izz>" + str(mass * (w **2 + d **2) / 12.0) + "</izz>\n\
          <ixy>0.0</ixy>\n\
          <ixx>" + str(mass * (d **2 + h **2) / 12.0) + "</ixx>\n\
          <ixz>0.0</ixz>\n\
          <iyz>0.0</iyz>\n\
          <iyy>" + str(mass * (w **2 + h **2) / 12.0) + "</iyy>\n\
        </inertia>\n\
      </inertial>\n\
      <visual name='" + object_name + "_visual'>\n\
        <geometry>\n\
          <mesh>\n\
            <uri>model://" + str(object_index) + '_' + object_name + '_' + str(object_scale) + "/meshes/" + object_name + "." + mesh_suffix + "</uri>\n\
            <scale>" + str(scale) + " " + str(scale) + " " + str(scale) + "</scale>\n\
          </mesh>\n\
        </geometry>\n\
      </visual>\n\
      \n\
      <collision name='" + object_name + "_collision'>\n\
        <geometry>\n\
          <mesh>\n\
            <uri>model://" + str(object_index) + '_' + object_name + '_' + str(object_scale) + "/meshes/" + object_name + "." + mesh_suffix + "</uri>\n\
            <scale>" + str(scale) + " " + str(scale) + " " + str(scale) + "</scale>\n\
          </mesh>\n\
        </geometry>\n\
        <surface>\n\
          <friction>\n\
            <ode>\n\
              <mu>20.0</mu>\n\
              <mu2>20.0</mu2>\n\
              <fdir1>0.0 0.0 1.0</fdir1>\n\
            </ode>\n\
          </friction>\n\
          <contact>\n\
            <ode>\n\
              <kp>10.0</kp>\n\
              <kd>0.0</kd>\n\
              <min_depth>0.0</min_depth>\n\
            </ode>\n\
          </contact>\n\
          <soft_contact>\n\
            <dart>\n\
              <stiffness>100</stiffness>\n\
              <damping>10</damping>\n\
            </dart>\n\
          </soft_contact>\n\
        </surface>\n\
      </collision>\n\
      \n\
    </link>\n\
    \n\
  </model>\n\
</sdf>"

        # print(model_sdf_content)

        ## Write files
        with open(storage_path + '/' + str(object_index) + '_' + object_name + '_' + str(object_scale) + '/model.config', 'w') as f_conf:
            f_conf.write(model_config_content)
            f_conf.close()

        with open(storage_path + '/' + str(object_index) + '_' + object_name + '_' + str(object_scale) + '/model.sdf', 'w') as f_sdf:
            f_sdf.write(model_sdf_content)
            f_sdf.close()


    def convert_obj_dae(self, mesh_in_dir, mesh_out_dir):
    
        # make a directory first
        if not os.path.exists(mesh_out_dir):
            os.makedirs(mesh_out_dir)

        # Obtain the list of mesh names
        for mesh_in_file in os.listdir(mesh_in_dir):
            if not mesh_in_file[-3:] == "obj": # not .obj file
                print(mesh_in_file + " is not .obj, skip.")
                continue
            mesh_file_name = mesh_in_file[:-4]
            os.system('meshlabserver -i ' + mesh_in_dir + '/' + mesh_file_name + '.obj -o ' + mesh_out_dir + '/' + mesh_file_name + '.dae')


    def convert_dae_obj(self, mesh_in_dir, mesh_out_dir):
    
        # make a directory first
        if not os.path.exists(mesh_out_dir):
            os.makedirs(mesh_out_dir)

        # Obtain the list of mesh names
        for mesh_in_file in os.listdir(mesh_in_dir):
            mesh_file_name = mesh_in_file[:-4]
            os.system('meshlabserver -i ' + mesh_in_dir + '/' + mesh_file_name + '.dae -o ' + mesh_out_dir + '/' + mesh_file_name + '.obj')


    def obtain_models_info(self, mesh_in_path, h5_path, h5_name):

        time_start = time.time()

        ## obtain the directories' names
        model_categories_list = []
        dataset_path = mesh_in_path #'/home/liangyuwei/Downloads/3d_model_database/my_choice/KIT_and_3DNet_from_dexnet/chosen_from_the_other_2_folders'


        ## iterate to process the model files
        mesh_info_storage_root = h5_path #'/home/liangyuwei/Downloads/models_chosen_from_dexnet_KIT_3DNet_SDF'
        # trimesh.util.attach_to_log() # print results to the screen

        # open a .h5 file for storage
        f = h5py.File(mesh_info_storage_root + '/' + h5_name + '.h5', 'a') # append mode!!!

        for obj_file_name in os.listdir(dataset_path):               
            # for every off model files
            # exclude .mtl files
            if not obj_file_name[-3:] == "obj": # not .obj file
                print(obj_file_name + " is not obj")
                continue
      
            # print the processing information
            print("Processing " + obj_file_name + " ...")
      
            # load the mesh
            obj_file_path = dataset_path + '/' + obj_file_name
            scene_or_mesh = trimesh.load(obj_file_path)
            # convert possible Scene object to Trimesh object
            if isinstance(scene_or_mesh, trimesh.Scene):
                if len(scene_or_mesh.geometry) == 0:
                    mesh = None  # empty scene
                else:
                    # we lose texture information here
                    mesh = trimesh.util.concatenate(
                        tuple(trimesh.Trimesh(vertices=g.vertices, faces=g.faces)
                        for g in scene_or_mesh.geometry.values()))
            else:
                assert(isinstance(mesh, trimesh.Trimesh))
                mesh = scene_or_mesh


            # compute needed information
            import pdb
            pdb.set_trace()
            volume = mesh.volume
            bounding_box_size = mesh.bounding_box.extents
            moment_inertia_matrix = mesh.moment_inertia
            com = mesh.center_mass

            if volume < 0:
                os.remove(obj_file_path)
                continue 

            # store the data
            obj_filename_group = f.create_group(obj_file_name[0:-4])
            obj_filename_group.create_dataset('volume', data=volume)
            obj_filename_group.create_dataset('bounding_box_size', data=bounding_box_size)
            obj_filename_group.create_dataset('moment_inertia_matrix', data=moment_inertia_matrix)
            obj_filename_group.create_dataset('com', data=com)
      
        # Close the file after exporting everything needed
        f.close()

        # show the time used on processing the whole dataset
        time_end = time.time()
        print("Total time spent: {} s".format(time_end - time_start))




if __name__ == '__main__':

    ### Initialize parameters
    mesh_path = '/home/liangyuwei/grasping-object-dataset-texture/meshes/tmp_texture' #test' #home_stuff' #chosen_from_the_other_2_folders'
    sdf_path = '/home/liangyuwei/grasping-object-dataset-texture/tmp_texture-sdf-object_size-1' #sdf-object_size-2' # sdf-object_size-1'
    object_scale = 1#1.5 #3#2#1
    h5_path = '/home/liangyuwei/grasping-object-dataset-texture/models_info'
    h5_name = 'tmp_texture'#'models_info_test_test'
    mass = 1.0


    ### Initialize the class
    proc_tools = process_3d_models(mesh_path=mesh_path, sdf_path=sdf_path, object_scale=object_scale, h5_path=h5_path, h5_name=h5_name, mass=mass)

    ### Convert the mesh type(from .obj to .dar)
    proc_tools.convert_obj_dae(mesh_in_dir=mesh_path, mesh_out_dir=mesh_path+'-dae')
#    proc_tools.convert_dae_obj(mesh_in_dir=mesh_path, mesh_out_dir=mesh_path+'-obj')

    ### Generate h5 for storing models info
    proc_tools.obtain_models_info(mesh_path, h5_path, h5_name)

    ### Generate the SDF folders in the target path
    proc_tools.generate_model_folders(start_index=1, mesh_suffix='dae', mesh_in_path=mesh_path+'-dae')#'/home/liangyuwei/grasping-object-dataset/meshes/chosen_from_the_other_2_folders-dae') #

    



        
    
        

  





