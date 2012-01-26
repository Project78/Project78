#ReportLab install/check script
#Copyright ReportLab Europe Ltd. 2000-2008
import os
import sys
import re
import urllib

pyMajor, pyMinor = sys.version_info[0:2]

def normalizeRlVersionString(ver):
    """
    >>> normalizeRlVersionString("2.0.20060901072110")
    '2.0.20060901'
    >>> normalizeRlVersionString("2.0.20060901072516")
    '2.0.20060901'
    >>> normalizeRlVersionString("2.0.2")
    '2.0.2'
    >>> normalizeRlVersionString("2.0")
    '2.0'

    If the format isn't known, leave it alone:

    >>> normalizeRlVersionString("2.0.200609010725161")
    '2.0.200609010725161'

    """
    if re.match('\d{1,2}\.\d{1,3}\.\d{14}$', ver):
        # strip time from ISO date+time timestamp
        return ver[:-6]
    return ver

def check():
    print 'ReportLab Health Check script'
    print '_____________________________'
    print

    print '''
This will inspect your reportlab installations and help you
ensure they are correct, complete and up to date.  If you don't
have reportlab's software installed, it will help you.  It will
NOT modify anything at all, so you can run it safely at any time.
'''

    print 'Python %s' % sys.version
    print 'Executable:',sys.executable
    print
    
    

    found_reportlab = 0
    found_rl_accel = 0
    found_renderpm = 0
    found_pyrxp = 0
    found_rlextra = 0
    found_pil = 0    

    #reportlab package
    print '\n1. ReportLab Toolkit - open source PDF library...',
    try:
        import reportlab
        print 'version %s' % reportlab.Version
        print '\t(in %s)' % reportlab.__file__
        found_reportlab = 1
    except ImportError:
        print 'not found'
        print '''
The basic ReportLab Toolkit is not found.  If you have installed it, check
it's on your Python path when this script is run.  If not, you can download
it from http://www.reportlab.org/download.html'''
        


    print '\n2. _rl_accel extension module...',
    try:
        import _rl_accel
        print 'found version %s' % _rl_accel.version
        print '\t(in %s)' % _rl_accel.__file__
        found_rl_accel = 1
    except ImportError:
        print 'not found'
        print '''
_rl_accel is an extension module written in C (or Java, for Jython users)
which makes PDF generation much faster.  Any serious reportlab user should
install it.  On Windows you can get precompiled binary versions for your
Python version from here:
  ftp://ftp.reportlab.com/win32-dlls/
On any other platform with a C compiler (or Windows if you wish) you can
compile this with python's distutils.  For version 1.19 and lower, cd
into reportlab/lib and execute the command "python setup.py install".
For version 1.20 and higher, get the rl_addons package and execute
the same command, which will build several extensions.
'''        


    if found_reportlab and found_rl_accel:
        if reportlab.Version >= '2.0':
            if _rl_accel.version < 0.54:
                print '''
You have an old version of _rl_accel!  It lacks new functions to
do fast Unicode character metrics which were added in _rl_accel 0.54,
release concurrently with reportlab 2.0.
On Windows you can get precompiled binary versions for your
Python version from here:
  ftp://ftp.reportlab.com/win32-dlls/
On any other platform with a C compiler (or Windows if you wish) you can
compile this with python's distutils.  For version 1.20 and higher,
get the rl_addons package and execute the command "python setup.py install"
in the rl_accel directory.  Then re-run this script.
'''

    print '\n3. Python Imaging Library...',
    try:
        import PIL.Image
        #need to do a full test to prove it really
        # has the _imaging.pyd
        
        try:
            try:
                import _imaging
            except ImportError:
                import PIL._imaging
            found_pil = 1
            print 'found' 
            print '\t(in %s)' % os.path.dirname(PIL.Image.__file__)
            
           
        except ImportError:
            print "partial/broken!"
            print 'PIL python package present but _imaging extension not importable'
            print '\t(in %s)' % os.path.dirname(PIL.Image.__file__)

    except ImportError:
        print 'not found'
        print '''
The Python Imaging Library is a well known Python package for manipulating
bitmap images.  If you want to import bitmap art into PDF files or use
our graphics module to create bitmaps, you need this.  Get it from
    http://www.pythonware.com/products/pil/index.htm
'''        

    print '\n4. _renderPM extension module...',
    try:
        import _renderPM
        print 'found version %s' % _renderPM._version
        found_renderpm = 1
        print '\t(in %s)' % _renderPM.__file__
    except ImportError:
        print 'not found'
        print '''
_renderPM is an extension module written in C which allows the
reportlab/graphics subpackage to make bitmap output - i.e. to save charts and
diagrams in GIF, PNG and JPG as well as PDF.
On Windows you can get precompiled binary versions for your Python version from
here:
  ftp://ftp.reportlab.com/win32-dlls/
On any other platform with a C compiler (or Windows if you wish) you can
compile this with python's distutils.  Get the rl_addons package from
www.reportlab.org and execute 'python setup.py install', which will build
several extensions.'''        

    print '\n5. pyRXP xml parser...',
    try:
        import pyRXP
        print 'found version %s' % pyRXP.version
        found_pyrxp = 1
        print '\t(in %s)' % pyRXP.__file__
    except ImportError:
        print 'not found'
        print '''
pyRXP is a very fast validating XML parser.  It is NOT required for the
ReportLab toolkit, although future versions may use it.  It is used
by ReportLab's commercial libraries including RML2PDF.
On Windows you can get precompiled binary versions for your Python version
from here:
  ftp://ftp.reportlab.com/win32-dlls/
On any other platform with a C compiler (or Windows if you wish) you can
compile this with python's distutils.  Get the rl_addons package from
www.reportlab.org and execute 'python setup.py install', which will build
several extensions.'''        


    print '\n5. ReportLab commercial package (rlextra)...',
    try:
        import rlextra
        print 'found version %s' % rlextra.Version
        found_rlextra = 1
        print '\t(in %s)' % rlextra.__file__
        
    except ImportError:
        print 'not found'
        print '''
The commercial package is only available to customers and partners.
Various versions can be found (if you have a site password) at
    http://developer.reportlab.com/devnet'''        

    if found_reportlab and found_rlextra:
        if (normalizeRlVersionString(reportlab.Version) !=
            normalizeRlVersionString(rlextra.Version)):
            print "Warning: reportlab and rlextra versions differ!"

    ##################################################################
    #
    # under development - will download all the bits for you
    #
    #################################################################


def reportFunc(blocksSoFar, blockSize, fileSize):
    sys.stdout.write('.')

def getPilWin(pyMajor,pyMinor, pilVersion='1.1.4', into=os.getcwd()):
    filename = 'PIL-%s.win32-py%d.%d.exe' % (pilVersion, pyMajor, pyMinor)
    remoteFile = 'http://effbot.org/downloads/' + filename
    print 'downloading', filename, 
    urllib.urlretrieve(remoteFile,
                       os.path.join(into, filename),
                       reportFunc)
    print 'done.'

def getPilSrc(pilVersion='1.1.4', into=os.getcwd()):
    filename = 'Imaging-%s.tar.gz' % pilVersion
    remoteFile = 'http://effbot.org/downloads/' + filename
    print 'downloading', filename, 
    urllib.urlretrieve(remoteFile,
                       os.path.join(into, filename),
                       reportFunc)
    print 'done.'


if __name__=='__main__':
    check()

##    getPilWin(pyMajor, pyMinor)
##    getPilSrc()
