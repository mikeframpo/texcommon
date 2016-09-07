
import os
import json
import subprocess

class ImgArgs:

    def __init__(self, script, args, img):
        self.script = script
        self.args = args
        self.img = img
    
    def processed_key(self):
        key = self.script
        if self.args is not None:
            key += '_' + self.args
        return key

# a dictionary mapping of image filename to script (including
# script arguments)
fname_to_script = None

# a set of already processed scripts
processed_scripts = set()

def _get_dest_dir():
    scriptdir = _get_script_dir()
    imgdir = os.path.join(scriptdir, 'imgbuild')
    if not os.path.isdir(imgdir):
        raise Exception('Expected \'imgbuild\' directory in script dir.')
    return imgdir

def _get_script_dir():
    scriptdir = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'script')
    if not os.path.islink(scriptdir):
        raise Exception('Expected symlink \'script\' in texcommon/script'\
                + ' dir pointing to root of image script dir.')
    return scriptdir

def _load_image_deps():
    scriptdir = _get_script_dir()

    depfile = os.path.join(scriptdir, 'imgdep.json')
    if not os.path.isfile(depfile):
        raise Exception('No \'imgdep.json\' file found in script dir.')

    with open(depfile) as dephandle:
        parsed = json.load(dephandle)
    
    global fname_to_script
    fname_to_script = { }
    scripts = parsed['scripts']
    for script in scripts:
        args = None
        scriptpath = script.keys()[0]
        scriptdata = script[scriptpath]
        if scriptdata.has_key('args'):
            args = scriptdata['args']
        images = scriptdata['img']
        for img in images:
            imgargs = ImgArgs(scriptpath, args, img)
            fname_to_script[img] = imgargs

def _process_img(imgpath):
    if not fname_to_script.has_key(imgpath):
        raise Exception(
            'Image {} was not found in imgdeps file.'.format(imgpath))

    destpath = os.path.join(_get_dest_dir(), imgpath)
    if os.path.isfile(destpath):
        print('=== img already exists, skipping: {}'.format(imgpath))
        return

    imgargs = fname_to_script[imgpath]
    args = ''
    if imgargs.args is not None:
        args = imgargs.args

    scriptrel = imgargs.script
    scriptfull = os.path.join(_get_script_dir(), scriptrel)
    if not os.path.isfile(scriptfull):
        raise Exception(
            'Script does not exist {}'.format(scriptfull))

    global processed_scripts
    if not imgargs.processed_key() in processed_scripts:
        scriptloc, scriptname = os.path.split(scriptfull)
        cmd = 'SAVEFIGS=True python2 {} {}'.format(scriptname, args)
        print('=== running script {}'.format(cmd))
        ret = subprocess.call(cmd, shell=True, cwd=scriptloc)

        if ret is not 0:
            raise Exception(
                'Script returned non-zero errcode {}.'.format(ret))

        processed_scripts.add(imgargs.processed_key())
    else:
        print('=== script already run, skipping {}'.format(scriptrel))

    if not os.path.isfile(destpath):
        raise Exception(
            'Image {} was not built by script {}.'
            .format(imgpath, scriptfull))

def img(imgpath):
    if fname_to_script is None:
        _load_image_deps()

    _process_img(imgpath)

