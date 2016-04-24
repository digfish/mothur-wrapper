#!/usr/bin/env python

import os
import sys
import ConfigParser as cp
import re
import argparse
import multiprocessing
import pprint
import pexpect
from subprocess import *


fields = ['fasta','taxonomy','reference','reftaxonomy','name','count','dist','column','processors','fastq',\
            'output','contaxonomy','constaxonomy','start','end']

settings = ['processors', 'flow', 'file', 'biom', 'phylip', 'column', 'summary', 'fasta', 'name', 'group',\
            'list', 'taxonomy', 'qfile', 'accnos', 'rabund', 'sabund', 'design', 'order', 'tree', 'shared',\
            'ordergroup', 'count', 'relabund', 'sff', 'oligos', 'clear', 'seed', 'inputdir', 'outputdir' ]


interactive_mode = False
verbose_mode = False

def define_fields(argparser):
    global fields
    for field in fields:
        argparser.add_argument('--%s' % field)

def main():

    global fields, interactive_mode, verbose_mode, settings

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

    argparser.add_argument('batch_script',help='The mothur batch script with placeholders to fill in',nargs='?')
    argparser.add_argument('--verbose','-v',help='Enable verbose mode',action='store_true')
    argparser.add_argument('--output_dir',help='The output dir to be used',default=os.getcwd())

    define_fields(argparser)

    parsed_args = argparser.parse_args()

    if parsed_args.verbose:
        verbose_mode = True

    if not parsed_args.batch_script:
        interactive_mode = True
    else:
        batch_script = parsed_args.batch_script

    #print parsed_args

    #fills the params with values that come from the command line, overriding eventually
    #some that comes from the config file
    for (name,value) in parsed_args.__dict__.iteritems():
       if value is not None and name != 'verbose':
         params[name] = value

    if verbose_mode:
        print "%s will use the following parameters:" % (exec_name)
        pprint.pprint( params, indent=3)


    if not interactive_mode:
        # reads the mothur batch script
        batch_string = open(batch_script, "r").read()
        p = re.compile('\\$[a-z_]+')
        new_vars = p.findall(batch_string)
        parsed_script_contents = batch_string
        for (name,value) in params.iteritems():
            print name,'=>', value
            parsed_script_contents = parsed_script_contents.replace('$'+name, value)
        parsed_batch_script_name = "." + os.path.basename(batch_script) + ".parsed"
        parsed_batch = open(parsed_batch_script_name, "w")
        parsed_batch.write(parsed_script_contents)
        parsed_batch.close()
        os.system('mothur ' + parsed_batch_script_name)
        os.remove(parsed_batch_script_name)

    else: #interactive_mode
        print "Entering in interactive mode"
        mothur = pexpect.spawn('mothur')
        mothur.before
        filled_settings = set(params.keys()) & set(settings)
        if "output_dir" in params.keys():
            mothur.sendline("set.dir(output=%s)" % params['output_dir'] )
        for setting in filled_settings:
            mothur.sendline("set.current(%s=%s)" %(setting,params[setting]  ))
        mothur.interact()

    output_dir = params['output_dir']

    last_logfile = ""
    if os.path.isfile( output_dir + os.sep + 'current_files.summary'):
        last_logfile =  output_dir + os.sep + 'current_files.summary'
        if verbose_mode:
            print ("Found current_files.summary in " + output_dir  + " : it will used !")
    else:
        last_logfile = get_most_recent_logfile_on_dir( output_dir )

        last_logfile =  output_dir + os.sep + last_logfile

        if not os.path.is_file(os.getcwd()):
            last_logfile = get_most_recent_logfile_on_dir

        if verbose_mode:
            print "Last logfile found:", last_logfile

    log_content = open(last_logfile,'r').read()

    p = re.compile('[a-zA-Z0-9_]+?=[a-zA-Z0-9/_.]+')

    new_vars = p.findall(log_content)

    if verbose_mode:
        print "%s caught the following vars:" % (exec_name)
        pprint.pprint(new_vars, indent=3)

    if len(new_vars) > 0:
        for match in new_vars:
            name,value = match.split('=')
            # skips pairs with value as 'current', avoiding to include them in the config file
            if value == 'current': continue
            params[name] = value
        new_config_filename = os.getcwd() + os.sep + os.path.basename( config_filename )

        if os.environ['HOME'] == os.getcwd() and \
            os.path.isfile(os.environ['HOME'] + os.path.basename( config_filename) ):
            print ("WARNING: the " +  config_filename + " will not be written in order to not overwrite the one that is in " + \
                   "your home root dir, please next time run mothur from another dir besides your home root dir in order to avoid conflicts. ")
            return

        store_config(params,new_config_filename)

def get_most_recent_logfile_on_dir(output_dir):
    return check_output('ls -t *.logfile | head -n 1',shell=True,cwd=output_dir).rstrip()

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
