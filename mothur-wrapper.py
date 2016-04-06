#!/usr/bin/env python

import os
import sys
import ConfigParser as cp
import re
import argparse
import multiprocessing
import subprocess
import pprint

fields = ['fasta','taxonomy','reference','reftaxonomy','name','count','dist','column','processors','fastq',\
            'output','contaxonomy']

def define_fields(argparser):
    global fields
    for field in fields:
        argparser.add_argument('--%s' % field)

def main():

    global fields

    #holds the params that either can come from the config
    # file or the command line args

    params = dict()

    #the only param that comes by default
    params['num_cpus'] =  str(multiprocessing.cpu_count()-1)

    #searches for the config file (with the same basename in the dir)
    exec_name = os.path.basename(sys.argv[0]).split('.')[0]

    config_filename = '.' + exec_name + '.ini'

    if (not os.path.exists(os.getcwd() + os.sep + config_filename)):
        if (not os.path.exists(os.environ['HOME'] + os.sep + config_filename)):
            print config_filename, "does not exist!"
            return
        else:
            config_filename = os.environ['HOME'] + os.sep + config_filename
    else:
        config_filename = os.getcwd() + os.sep + config_filename

    print "Found config file at ", config_filename

    config_parser = cp.ConfigParser()

    config_parser.read(config_filename)

    for (name,value) in config_parser.items('config'):
        params[name] = value

    #print params


    argparser = argparse.ArgumentParser()

    argparser.add_argument('batch_script',help='The mothur batch script with placeholders to fill in')
    argparser.add_argument('--output_dir',help='The output dir to be used')

    define_fields(argparser)

    parsed_args = argparser.parse_args()

    batch_script = parsed_args.batch_script

    #print parsed_args

    #fills the params with values that come from the command line, overriding evertually
    #some that comes from the config file
    for (name,value) in parsed_args.__dict__.iteritems():
       if value is not None:
         params[name] = value

    print "%s will use the following parameters:" % (exec_name)
    pprint.pprint( params, indent=3)



    # reads the mothur batch script
    batch_string = open(batch_script, "r").read()

    p = re.compile('\\$[a-z_]+')

    new_vars = p.findall(batch_string)

#    print new_vars

    parsed_script_contents = batch_string

    for (name,value) in params.iteritems():
        parsed_script_contents = parsed_script_contents.replace('$'+name, value)

    #print parsed_script_contents



    parsed_batch_script_name = "." + os.path.basename(batch_script) + ".parsed"

    parsed_batch = open(parsed_batch_script_name, "w")

    parsed_batch.write(parsed_script_contents)

    parsed_batch.close()

    os.system('mothur ' + parsed_batch_script_name)

    #mothur_out = subprocess.check_output( 'mothur ' + parsed_batch_script_name, shell=True)

    #print mothur_out

    os.remove(parsed_batch_script_name)

    output_dir = params['output_dir']

    last_logfile = subprocess.check_output('ls -t *.logfile | head -n 1',\
                                           shell=True,cwd=output_dir).rstrip()

    print "Last logfile:", output_dir + os.sep + last_logfile

    log_content = open(output_dir + os.sep + last_logfile,'r').read()

    p = re.compile('[a-zA-Z0-9_]+?=[a-zA-Z0-9/_.]+')

    new_vars = p.findall(log_content)

    print "%s caught the following vars:" % (exec_name)

    pprint.pprint(new_vars, indent=3)

    if len(new_vars) > 0:

        for match in new_vars:

            name,value = match.split('=')
            # skips pairs with value as 'current', avoiding to include them in the config file
            if value == 'current': continue
            params[name] = value

        new_config_filename = os.getcwd() + os.sep + os.path.basename( config_filename )
        store_config(params,new_config_filename)

def store_config(params,new_config_filename):
    config = cp.ConfigParser()
    config.add_section('config')
    for (name,value) in params.iteritems():
        config.set('config',name,value)
    ini = open(new_config_filename,'w')
    config.write(ini)
    print "Wrote configuration file to", os.path.abspath(ini.name)

if __name__ == '__main__':
    main()
