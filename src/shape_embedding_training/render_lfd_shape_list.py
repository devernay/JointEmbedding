#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
import sys
import datetime
from functools import partial
from multiprocessing.dummy import Pool
from subprocess import call

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(BASE_DIR))
from global_variables import *

report_step = 100

if __name__ == '__main__':
    if not os.path.exists(g_lfd_images_folder):
        os.mkdir(g_lfd_images_folder) 

    shape_list = [line.strip().split(' ') for line in open(g_shape_list_file, 'r')]
    print(len(shape_list), 'shapes are going to be rendered!')

    print('Generating rendering commands...', end = '')
    commands = []
    first_shape_idx = 0 # modify to set a different starting point
    for shape_property in shape_list[first_shape_idx:]:
        shape_synset = shape_property[0]
        shape_md5 = shape_property[1]
        shape_file = os.path.join(g_shapenet_root_folder, shape_synset, shape_md5, g_shapenet_model)

        command = '%s ../blank.blend --background --python render_lfd_single_shape.py -- %s %s %s ' % (g_blender_executable_path, shape_file, shape_synset, shape_md5)
        if len(shape_list) > 32:
            command = command + ' > /dev/null 2>&1'
        commands.append(command)
    print('done(%d commands)'%(len(commands)))

    print('Rendering, it takes long time...')
    pool = Pool(g_lfd_rendering_thread_num)
    for idx, return_code in enumerate(pool.imap(partial(call, shell=True), commands)):
        if idx % report_step == 0:
            print('[%s] Rendering command %d of %d, shape %s %s' % (datetime.datetime.now().time(), idx+first_shape_idx , len(shape_list), shape_list[idx+first_shape_idx].shape_synset, shape_list[idx+first_shape_idx].shape_md5))
        if return_code != 0:
            print('Rendering command %d of %d (shape %s %s) failed' % (idx+first_shape_idx, len(shape_list), shape_list[idx+first_shape_idx].shape_synset, shape_list[idx+first_shape_idx].shape_md5))
