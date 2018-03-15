
import os
import json
import subprocess

SCRIPT_PDFTEX = 'pdf_tex'
SCRIPT_ISCAPEPDF = 'inkscape_pdf'

class ImgArgs:

    def __init__(self, script, args, img):
        self.script = script
        self.args = args
        self.img = img
    
    def processed_key(self):
        if self.is_py_script():
            key = self.script
            if self.args is not None:
                key += '_' + self.args
            return key
        elif self.is_pdftex_script():
            return SCRIPT_PDFTEX + '_' + self.img
        elif self.is_inkscape_pdf():
            return SCRIPT_ISCAPEPDF + '_' + self.img
        else:
            raise Exception('Unknown script type')

    def is_py_script(self):
        return os.path.splitext(self.script)[1] == '.py'

    def is_pdftex_script(self):
        return self.script == SCRIPT_PDFTEX

    def is_inkscape_pdf(self):
        return self.script == SCRIPT_ISCAPEPDF

    def get_script_path(self):
        if self.is_pdftex_script() or self.is_inkscape_pdf():
            raise Exception('pdf_tex does not call a script')
        return os.path.join(_get_script_dir(), self.script)

    def get_targets(self):
        targets = []
        if self.is_py_script():
            targets.append(os.path.join(_get_dest_dir(), self.img))
        elif self.is_pdftex_script() or self.is_inkscape_pdf():
            imgbase = os.path.splitext(self.img)[0]
            targets.append(os.path.join(_get_dest_dir(), imgbase + '.pdf'))
            if self.is_pdftex_script():
                targets.append(os.path.join(_get_dest_dir(), imgbase + '.pdf_tex'))
        return targets

    def get_sources(self):
        '''returns a list of all known files which the resulting image
        depends on.'''
        deps = []
        if self.is_py_script():
            # this is commented because it's kindof annoying to rebuild every
            # plot whenever the script is modified
            #deps.append(self.get_script_path())
            pass
        elif self.is_pdftex_script() or self.is_inkscape_pdf():
            imgbase = os.path.splitext(self.img)[0]
            deps.append(os.path.join(_get_dest_dir(), '../', imgbase + '.svg'))
        return deps

# a dictionary mapping of image filename to script (including
# script arguments) for all dependencies known in the imgdep.json file
fname_to_script = None

# a set of already processed scripts
processed_scripts = set()

savepath = None

def _get_dest_dir():
    if savepath is None:
        raise Exception('Savepath has not been set, call '\
            + 'imgdep.set_save_path() before calling imgdep.img()')
    if not os.path.isdir(savepath):
        raise Exception(
            'Savepath {} is not a valid directory.'.format(savepath))
    return os.path.realpath(savepath)

tikzdir = None

def _get_tikz_dir():
    if tikzdir is None:
        raise Exception('Tikz dir has not been set, call '\
            + 'imgdep.set_tikz_path() before running build')
    if not os.path.isdir(tikzdir):
        raise Exception(
            'tikzdir {} is not a valid directory.'.format(tikzdir))
    return os.path.realpath(tikzdir)

def _get_script_dir():
    scriptdir = os.path.join(
                    os.path.dirname(imgdir_path),
                    'script')
    if not os.path.islink(scriptdir):
        raise Exception('Expected symlink \'script\' in texcommon/script'\
                + ' dir pointing to root of image script dir.')
    return os.path.realpath(scriptdir)

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
        images = []
        if scriptdata.has_key('img'):
            images.extend(scriptdata['img'])
        if scriptdata.has_key('tex'):
            images.extend(scriptdata['tex'])
        for img in images:
            imgargs = ImgArgs(scriptpath, args, img)
            fname_to_script[img] = imgargs

def _get_img_args(imgpath):
    if not fname_to_script.has_key(imgpath):
        raise Exception(
            'Image {} was not found in imgdeps file.'.format(imgpath))

    imgargs = fname_to_script[imgpath]
    if imgargs.is_py_script():
        scriptfull = imgargs.get_script_path()
        if not os.path.isfile(scriptfull):
            raise Exception(
                'Script does not exist {}'.format(scriptfull))
    return imgargs

def _process_img(imgpath):

    imgargs = _get_img_args(imgpath)
    args = ''
    if imgargs.args is not None:
        args = imgargs.args

    global processed_scripts
    if not imgargs.processed_key() in processed_scripts:

        if imgargs.is_py_script():
            scriptfull = imgargs.get_script_path()
            scriptloc, scriptname = os.path.split(scriptfull)
            cmd = 'SAVEPATH={} python2 {} {}'.format(savepath, scriptname, args)
            print('=== running script {}'.format(cmd))
            ret = subprocess.call(cmd, shell=True, cwd=scriptloc)

        if imgargs.is_pdftex_script() or imgargs.is_inkscape_pdf():

            extraargs = ''
            if imgargs.is_pdftex_script():
                extraargs = '--export-latex'

            imgbase = os.path.splitext(imgargs.img)[0]
            cmd = 'inkscape -C -z --file=../%s.svg --export-pdf=%s.pdf %s'\
                    % (imgbase, imgbase, extraargs)
            print('=== running script %s' % cmd)
            ret = subprocess.call(cmd, shell=True, cwd=_get_dest_dir())

        if ret is not 0:
            raise Exception(
                'Script returned non-zero errcode {}.'.format(ret))
        processed_scripts.add(imgargs.processed_key())
    else:
        print('=== script already run, skipping {}'.format(imgargs.script))

    targets = imgargs.get_targets()
    for target in targets:
        if not os.path.isfile(target):
            raise Exception(
                'Image {} was not built by script {}.'
                .format(target, imgargs.script))

def get_img_source_targets(imgpath):
    if fname_to_script is None:
        _load_image_deps()

    imgargs = _get_img_args(imgpath)
    return imgargs.get_sources(), imgargs.get_targets(), imgargs.processed_key()

def set_save_path(path):
    global savepath
    savepath = os.path.abspath(path)

    # the __file__ variable is a rel path to this script, relative to the 
    # place this was imported from. This means that __file__ can no longer
    # be used when the working directly later changes, as occurs when
    # working in an SConscript file.
    global imgdir_path
    imgdir_path = os.path.abspath(__file__)

def set_tikz_path(path):
    global tikzdir
    tikzdir = os.path.abspath(path)

def img(imgpath):
    if fname_to_script is None:
        _load_image_deps()

    _process_img(imgpath)

