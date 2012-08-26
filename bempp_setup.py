#Copyright (C) 2011 by the BEM++ Authors
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

# BEM++ setup script


import sys,os
from py_modules.tools import writeOptions, setDefaultConfigOption, pythonInfo, checkCreateDir, testBlas, testLapack, cleanUp, checkDeleteFile
from ConfigParser import ConfigParser
from optparse import OptionParser




import py_modules.boost as boost
import py_modules.armadillo as armadillo
import py_modules.tbb as tbb
import py_modules.dune as dune
import py_modules.trilinos as trilinos
import py_modules.bempp as bempp
import py_modules.ahmed as ahmed
import py_modules.mkl as mkl
import py_modules.tools as tools

libraries = {'tbb':tbb,
             'mkl':mkl,
             'armadillo':armadillo,
             'boost':boost,
             'dune':dune,
             'trilinos':trilinos,
             'ahmed':ahmed
            }
library_names = sorted(libraries.keys())


###########################

# The following functions determine the directory in which the file resides.
# Trick taken from http://stackoverflow.com/questions/2632199/how-do-i-get-the-path-of-the-current-executed-file-in-python

def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")

def module_path():
    if we_are_frozen():
        return os.path.split(os.path.abspath(sys.executable))[0]
    return os.path.split(os.path.abspath(__file__))[0]

def downloadDependencies(root,config):

    checkCreateDir(root+"/contrib/files")

    for dep in library_names:
        libraries[dep].download(root,config)
    
def prepareDependencies(root,config):

    prefix=config.get('Main','prefix')
    checkCreateDir(prefix+"/bempp")
    checkCreateDir(prefix+"/bempp/lib")
    checkCreateDir(prefix+"/bempp/include")

    for dep in library_names:
        libraries[dep].prepare(root,config)
    
def configureDependencies(root,config):
    
    for dep in library_names:
        libraries[dep].configure(root,config)

def buildDependencies(root,config):

    for dep in library_names:
        libraries[dep].build(root,config)

def installDependencies(root,config):

    for dep in library_names:
        libraries[dep].install(root,config)
    

def prepare(root,config):
    # Test whether the main options are present
    if not config.has_option('Main','prefix'): raise Exception('prefix not defined')
    setDefaultConfigOption(config,'Main','cc','gcc')
    setDefaultConfigOption(config,'Main','cxx','g++')
    setDefaultConfigOption(config,'Main','architecture','intel64')
    setDefaultConfigOption(config,'Main','cflags',"")
    setDefaultConfigOption(config,'Main','cxxflags',"")
    setDefaultConfigOption(config,'Main','root_dir',root)
    setDefaultConfigOption(config,'Main','build_jobs',1)

    # Set empty BLAS/Lapack options if none exists

    setDefaultConfigOption(config,'BLAS','lib',"")
    setDefaultConfigOption(config,'LAPACK','lib',"")

    # Add the correct architecture parameters
    cflags = config.get('Main','cflags')
    cxxflags = config.get('Main','cxxflags')

    arch = config.get('Main','architecture')
    if not arch in ['ia32','ia64','intel64']:
        raise Exception("Architecture '"+arch+"' is not supported. "
                        "Supported architectures: ia32, ia64, intel64.")
    
    if sys.platform.startswith('darwin'):
        if arch=='intel64':
            param = '-arch x86_64'
        else:
            param = '-arch i386'
        config.set('Main','cflags',cflags+" "+param)
        config.set('Main','cxxflags',cxxflags+" "+param)
    elif sys.platform.startswith('linux'):
        if arch=='intel64' or arch=='ia64':
            param = '-m64'
        else:
            param = '-m32'
        config.set('Main','cflags',cflags+" "+param)       
        config.set('Main','cxxflags',cxxflags+" "+param)
    else:
        raise Exception("Platform '"+sys.platform+"' is not supported")

    # Add the correct Python options

    import numpy

    (py_exe,py_lib,py_include) = pythonInfo()
    setDefaultConfigOption(config,'Python','exe',py_exe)
    setDefaultConfigOption(config,'Python','lib',py_lib)
    setDefaultConfigOption(config,'Python','include_dir',py_include)
    setDefaultConfigOption(config,'Python','numpy_include_dir',numpy.get_include())
     
###########################

if __name__ == "__main__":

    usage = "usage: %prog [options] configuration_file"
    parser = OptionParser()
    parser.add_option("-c", "--configure", action="store_true",
                      help="Configure the setup program")
    parser.add_option("-i", "--install", type="string", metavar="WHAT",
                      help="Build and install WHAT. Possible values for WHAT: "
                      "all (BEM++ and its dependencies), bempp (BEM++ only), " +
                      ", ".join(library_names) + " (particular BEM++ dependencies)")
    (options,args) = parser.parse_args()
    root=module_path()
    config=ConfigParser()
    if len(args) != 1:
        parser.error("Configuration file not specified")
    optfile = args[0]
    optfile_generated = optfile+".generated"
    config.read(optfile)
    prepare(root,config)
    if options.configure:
        checkDeleteFile(optfile_generated)
        try:
            cleanUp(root,config)
            downloadDependencies(root,config)
            prepareDependencies(root,config)
            bempp.prepare(root,config)
            testBlas(root,config)
            testLapack(root,config)
        except Exception as e:
            print "Configuration failed with error message: \n"+ e.message
            #sys.exit(1)
            raise
        opt_fp = open(optfile_generated,'w')
        config.write(opt_fp)
        opt_fp.close()
        print "Updated configuration written to "+root+"/"+optfile_generated
        enable_mkl = tools.to_bool(config.get('MKL','enable_mkl'))
        if not enable_mkl:
            print ("----------------------------------------------------------\n"
                   "You configured BEM++ to use another BLAS and LAPACK\n"
                   "libraries than Intel MKL. For optimum performance, ensure\n"
                   "that your BLAS and LAPACK libraries are configured to work\n"
                   "in single-threaded mode, as otherwise threads spawned by\n"
                   "BLAS and LAPACK will compete for resources with those\n"
                   "spawned by BEM++. For instance, if you are using\n"
                   "GotoBLAS, set the environmental variable GOTO_NUM_THREADS\n"
                   "to '1' before running any programs using BEM++.\n")
        
    if options.install:
        config = ConfigParser()
        if not os.path.exists(root+"/"+optfile_generated):
            print "You must first successfully run bempp_setup.py with the configure option."
            sys.exit(1)
        config.read(root+"/"+optfile_generated)
        writeOptions(root,config)
        if options.install in library_names:
            libraries[options.install].configure(root,config)
            libraries[options.install].build(root,config)
            libraries[options.install].install(root,config)
        elif options.install == "all":
            configureDependencies(root,config)
            buildDependencies(root,config)
            installDependencies(root,config)
            bempp.configure(root,config)
            bempp.build(root,config)
            bempp.install(root,config)
        elif options.install == "bempp":
            bempp.configure(root,config)
            bempp.build(root,config)
            bempp.install(root,config)
        else:
            raise Exception("Library name not recognized.")
        
        


    