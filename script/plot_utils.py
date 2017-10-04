
import numpy as np
import math
import os
import matplotlib as mpl

def get_save_path():
    if os.environ.has_key('SAVEPATH'):
        return os.environ['SAVEPATH']
    elif os.environ.has_key('SAVEFIGS'):
        return '../imgbuild'
    return None

def save_enabled():
    return get_save_path() is not None

if save_enabled():

    mpl.use('pgf')

    pgf_with_latex = {                      # setup matplotlib to use latex for output
        "pgf.texsystem": "pdflatex",        # change this if using xetex or lautex
        "text.usetex": True,                # use LaTeX to write all text
        "font.family": "serif",
        "font.serif": [],                   # blank entries should cause plots to inherit fonts from the document
        "font.sans-serif": [],
        "font.monospace": [],
        "axes.labelsize": 10,               # LaTeX default is 10pt font.
        "font.size": 10,
        "legend.fontsize": 8,               # Make the legend/label fonts a little smaller
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "figure.figsize": (10.0, 10.0),     # default fig size of 0.9 textwidth
        "axes.linewidth": 1.5,
        "pgf.preamble": [
            r"\usepackage[utf8x]{inputenc}",    # use utf8 fonts becasue your computer can handle it :)
            r"\usepackage[T1]{fontenc}",        # plots will be generated using this preamble
            ]
        }
    mpl.rcParams.update(pgf_with_latex)

import matplotlib.pyplot as plt

#mpl.rcParams.update ({'font.size': 7})
mpl.rcParams['lines.linewidth'] = 1.0

def savefig(path, fig=None):
    dpi=200
    print('Saving figure to: ' + path)
    if fig is not None:
        fig.tight_layout()
        fig.savefig(path, dpi=dpi, bbox_inches='tight', pad_inches=0)
    else:
        plt.tight_layout()
        plt.savefig(path, dpi=dpi, bbox_inches='tight', pad_inches=0)

def _save_to_genpath(fname, fig=None):
    genpath = get_save_path()
    if genpath is not None:
        if os.path.isdir(genpath):
            destpath = genpath
        else:
            raise Exception('Savepath {} does not exist'.
                    format(genpath))
        path = os.path.join(destpath, fname)
        savefig(path, fig)
    else:
        assert not save_enabled()

def showsave(fnames, figs=None, block=True, path=None):
    if not hasattr(fnames, '__iter__'):
        fnames = [fnames]
    if figs is not None:
        if not hasattr(figs, '__iter__'):
            figs = [figs]
        assert len(fnames) == len(figs)
    for ii in range(len(fnames)):
        fig=figs[ii] if figs is not None else None
        _save_to_genpath(fnames[ii], fig)
    if not save_enabled():
        plt.show(block=block)

fig_keys = { }

def get_fig(key):
    if key in fig_keys:
        return fig_keys[key]()
    else:
        raise Exception('Unknown figure key %s' % key)

cm_per_inch=2.54

# dimensions in inches
a4pagesize_inch=(21.0/cm_per_inch, 29.7/cm_per_inch)

# these were the margins used in confirmation report, will probably be used
# later on also.
a4margins_inch=(2.0/cm_per_inch, 3.0/cm_per_inch)

# the available size in inches, two margin widths are subtracted from either
# side to get the available page space
a4size_inch=(a4pagesize_inch[0] - 2.0*a4margins_inch[0],
                a4pagesize_inch[1] - 2.0*a4margins_inch[1])

beamerpagesize_inch=(12.8/cm_per_inch, 9.6/cm_per_inch)

beamermargins_inch=(1.54/cm_per_inch, 0.064/cm_per_inch)

beamersize_inch=(beamerpagesize_inch[0] - 2.0*beamermargins_inch[0],
                beamerpagesize_inch[1] - 2.0*beamermargins_inch[1])

# this width was found using the following commands
#
# \usepackage{layouts}
# ...
# \printinunitsof{cm}\prntlen{\columnwidth}
ieee_col_width = 8.855 / cm_per_inch

def puFig(f):

    def create_fig():
        if not save_enabled():
            return plt.figure()
        else:
            xdim, ydim = f()
            return plt.figure(figsize=(xdim, ydim))

    fig_keys[f.__name__] = create_fig
    return create_fig

def fig_thirdpage():
    return plt.figure(figsize=(14, 6))

def fig_quarterpage():
    return plt.figure(figsize=(4.68, 3.122))

# naming standard for the figuresize is:
#   fig_<width-description>_<height-description>

#   if one of the dimensions are not specified then the aspect ratio may
#   be specified by one of the following keys

#   "43" 4 x 3

#   40p indicates that a dimension takes up 40% of the space

# four of these plots fit vertically, each spanning the width of the page
@puFig
def fig_whole_quarter():
    return a4size_inch[0], a4size_inch[1]/4

@puFig
def fig_whole_43():
    xdim = a4size_inch[0]
    ydim = xdim * 0.75
    return xdim, ydim

@puFig
def fig_ieeecol_42():
    xdim = ieee_col_width
    ydim = xdim * 0.5
    return xdim, ydim

@puFig
def fig_ieeecol_43():
    xdim = ieee_col_width
    ydim = xdim * 0.75
    return xdim, ydim

@puFig
def fig_ieeecol_square():
    xdim = ieee_col_width
    ydim = xdim
    return xdim, ydim

@puFig
def fig_half_43():
    xdim = a4size_inch[0]/2
    ydim = xdim * 0.75
    return xdim, ydim

@puFig
def fig_beamer_41():
    xdim = beamersize_inch[0]
    ydim = xdim / 4.0
    return xdim, ydim

@puFig
def fig_whole_40p():
    xdim = a4size_inch[0]
    ydim = a4size_inch[1]*0.4
    return xdim, ydim

def fig_6x6():
    return plt.figure(figsize=(6.0, 6.0))

def plt_sig(sig, title=None, label=None, fmt=None, xmin=None, xmax=None,
            kwargs=None, fname=None, t=None, tscale=1e6, legloc=None,
            xlim=None, ylim=None, xlabel='Time ($\mu \; s$',
            ylabel='Voltage ($V$)'):

    if title is not None:
        plt.title(title)
    if xlabel is not None:
        plt.xlabel(xlabel)
    if ylabel is not None:
        plt.ylabel(ylabel)
    plt.grid(True)
    if kwargs is None:
        kwargs = { }
    if label is not None:
        kwargs['label'] = label
    if t == None:
        t = sig.t
    t = t * tscale
    if fmt is not None:
        plt.plot(t, sig, fmt, **kwargs)
    else:
        plt.plot(t, sig, **kwargs)
    if xlim is not None:
        xmin = xlim[0]
        xmax = xlim[1]
    if xmin is None:
        xmin = t[0]
    if xmax is None:
        xmax = t[-1]
    if ylim is not None:
        plt.axis(ymin=ylim[0], ymax=ylim[1])
    plt.axis(xmin=xmin, xmax=xmax)
    plt.legend(loc=legloc, labelspacing=0)

def plt_sig_separate(sigs, **kwargs):
    fig = plt.gcf()
    sp1 = fig.add_subplot(211)
    plt_sig(sigs[0], *kwargs)
    sp2 = fig.add_subplot(212)
    plt_sig(sigs[1], *kwargs)

def plt_series_separate(sigs):
    for sig in sigs:
        plt_sig_separate(sig)

def get_fft(sig, zpfactor=None):
    if zpfactor is not None:
        sig = sig.zeropad(len(sig) * zpfactor)
    return sig.fft()

def plt_spec(sig, title=None, label=None, fname=None, zpfactor=None,
                fmin=None, fmax=None, ftick=None, norm=None, db=False,
                fmt=''):
    xlabel = 'Frequency (Hz)'
    ylabel = 'FFT Magnitude'
    if sig.fdomain:
        fft = sig
    else:
        fft = get_fft(sig, zpfactor=zpfactor)
    if norm is not None:
        if type(norm) is bool:
            scalefac = max(abs(fft))
        elif isinstance(norm, np.ndarray):
            normfft = get_fft(norm, zpfactor=zpfactor)
            scalefac = max(abs(normfft))
        else:
            raise Exception('unsupported norm type')
        fft = fft.scale(1.0/scalefac)
        ylabel += ' (normalised)'
    if db:
        fft = 20*np.log10(fft)
    if title is not None:
        plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if fmin is None:
        fmin = 0
    if fmax is None:
        fmax = 10000
    if ftick is None:
        plt.xticks(np.arange(0, fmax, float(fmax)/20), rotation=-30)
    else:
        plt.xticks(np.arange(0, fft.f[len(fft.f) / 2 - 1], ftick), rotation=-30)
    plt.axis(xmin=fmin, xmax=fmax)
    plt.grid(True)
    if label is not None:
        plt.plot(fft.f, np.abs(fft), fmt, label=label)
    else:
        plt.plot(fft.f, np.abs(fft))
    plt.legend()
    plt.gcf().subplots_adjust(bottom=0.15)

    return fft

def plot_spectrum_separate(sig, title=None, zp=16):
    p1 = plt.subplot(211)
    if title:
        plt.title(title)
    plt_spec(sig[0], zpfactor=zp)
    p2 = plt.subplot(212)
    plt_spec(sig[1], zpfactor=zp)

def get_logticks(decvals, startexp, endexp):
    t = np.array([])
    for exp in range(startexp, endexp+1):
        t = np.append(t, np.array(decvals) * 10**exp)
    return t

def plt_stft(sig, width, window='hamming', fmax=None, interp=None):
    overlap = 1

    XX, f, t = sig.stfft(width, overlap, window=window)
    assert len(XX[0]) == len(f)

    if len(f) % 2 == 0:
        ifmax = len(f) / 2 - 1
    else:
        ifmax = len(f) / 2
    if fmax is not None:
        for ifreq in range(len(f)):
            if f[ifreq] >= fmax:
                ifmax = ifreq
                break
    #cut out the negative freq_components
    XX2 = [X[:ifmax] for X in XX]

    plt.imshow(np.abs(XX2.T), aspect='auto', interpolation=interp, origin='lower',
            extent=(t[0]*1e6, t[-1]*1e6, f[0], f[ifmax]))

    ax = plt.gca()
    ax.set_xlabel('Time (microseconds)')
    ax.set_ylabel('Frequency (Hz)')

    return XX, f, t

def plt_stft_separate(sig, width, title=None, fmax=None):
    fig = plt.gcf()
    ax1 = fig.add_subplot(211)
    if title is not None:
        ax1.set_title(title)
    plt_stft(sig[0], width, fmax=fmax)
    ax2 = fig.add_subplot(212)
    plt_stft(sig[1], width, fmax=fmax)

def get_spectra_peaks(fft, numpeaks=1):
    fftabs = np.abs(fft)
    peaks_idx = fftabs.peakfind(num_peaks=numpeaks, interp=True)[0]

    #FIXME to use the adjusted values
    peaks = [fftabs[peak] for peak in peaks_idx]
    peak_f = [fftabs.f[peak] + (math.modf(peak)[0] * fftabs.df) for peak in peaks_idx]
    return peaks, peak_f

