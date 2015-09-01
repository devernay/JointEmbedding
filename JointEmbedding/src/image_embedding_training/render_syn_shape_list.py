#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
import sys
import shutil
import random
import tempfile
import datetime
from functools import partial
from multiprocessing.dummy import Pool
from subprocess import call

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(BASE_DIR))
from global_variables import *

report_step = 100

if __name__ == '__main__':
    if not os.path.exists(g_syn_images_folder):
        os.mkdir(g_syn_images_folder) 

    shape_list = [line.strip().split(' ') for line in open(g_shape_list_file, 'r')]
    print(len(shape_list), 'shapes are going to be rendered!')
    
    # compute required image num per model for each synset    
    shape_synset_count = dict()
    for e in shape_list:
        if e[0] not in shape_synset_count:
            shape_synset_count[e[0]] = 0
        shape_synset_count[e[0]] += 1
    shape_synset_images_per_shape = dict()
    for synset in shape_synset_count:
        shape_synset_images_per_shape[synset] = int(g_images_per_synset / shape_synset_count[synset])
    print('shape_synset_images_per_shape: ', shape_synset_images_per_shape)

    # reading view distribution file
    shape_synset_view_params = dict()
    for synset in shape_synset_count:
        if not os.path.exists(g_view_distribution_files[synset]):
            print 'Failed to read view distribution files from %s for synset %s'%(g_view_distribution_files[synset], synset)
            exit()
        view_params = open(g_view_distribution_files[synset]).readlines()
        view_params = [[float(x) for x in line.strip().split(' ')] for line in view_params] 
        shape_synset_view_params[synset] = view_params

    print('Generating rendering commands...', end = '')
    commands = []
    tmp_dirname = os.path.join(g_data_folder, 'tmp_views/')
    for shape_property in shape_list:
        shape_synset = shape_property[0]
        shape_md5 = shape_property[1]
        shape_file = os.path.join(g_shapenet_root_folder, shape_synset, shape_md5, 'model.obj')
        images_per_shape = shape_synset_images_per_shape[shape_synset]
        # generate view distribution file
        view_params = shape_synset_view_params[shape_synset]

        if not os.path.exists(tmp_dirname):
            os.mkdir(tmp_dirname)
        tmp = tempfile.NamedTemporaryFile(dir=tmp_dirname, delete=False)
        for i in range(images_per_shape): 
            paramId = random.randint(0, len(view_params)-1)
            tmp_string = '%f %f %f %f\n' % (view_params[paramId][0], view_params[paramId][1], view_params[paramId][2], max(0.01,view_params[paramId][3]))
            tmp.write(bytes(tmp_string, 'UTF-8'))
        tmp.close()

        command = '%s %s --background --python %s -- %s %s %s %s > /dev/null 2>&1' % (g_blender_executable_path, g_blank_blend_file_path, os.paht.join(BASE_DIR, render_syn_single_shape.py), shape_file, shape_synset, shape_md5, tmp.name)
        #command = '%s ../blank.blend --background --python render_syn_single_shape.py -- %s %s %s %s ' % (g_blender_executable_path, shape_file, shape_synset, shape_md5, tmp.name)
        commands.append(command)
    print('done (%d commands)!'%(len(commands)))

    print('Rendering, it takes long time...')
    pool = Pool(g_syn_rendering_thread_num)
    for idx, return_code in enumerate(pool.imap(partial(call, shell=True), commands)):
        if idx % report_step == 0:
            print('[%s] Rendering command %d of %d' % (datetime.datetime.now().time(), idx, len(shape_list)))
        if return_code != 0:
            print('Rendering command %d of %d (\"%s\") failed' % (idx, len(shape_list), commands[idx]))
            
    shutil.rmtree(tmp_dirname)
