"""
Site index command line utilities.
"""

import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import click

import site_index
import site_index.si
from site_index import curves

# Declare the package name if needed
if __name__ == '__main__' and __package__ is None:
    import os, sys, importlib
    parent_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.dirname(parent_dir))
    __package__ = os.path.basename(parent_dir)
    importlib.import_module(__package__)

def curve_docs():
    keys = sorted(site_index.curves.keys())
    msg = 'Available Site Index Curves:\n'
    for key in keys:
        sf = site_index.curves[key]
        try:
            if key=='fvs':
                sc = sf('PN','DF',708)
            else:
                sc = sf()
            
            ds = sc.__doc__.strip().split('\n')[0]
            
        except:
            ds = ''
        
        msg += '{}: {}\n'.format(key, ds)
        
    return msg
    
@click.command()
@click.option('--curve', '-c', required=True, help='Site curve name.')
@click.option('--age', '-a', required=True, type=float, help='Tree age - BHA, TTA, etc. see curve description.')
@click.option('--height', '-t', required=True, type=float, help='Tree height - See curve description.')
@click.option('--variant', '-v', required=False, type=str, help='FVS variant abbreviation when curve="fvs".')
@click.option('--forest', '-f', required=False, type=int, default=0, help='FVS forest code when curve="fvs".')
@click.option('--species', '-s', required=False, type=str, help='FVS species code when curve="fvs".')
def si(curve, age, height, variant=None, forest=0, species=None):
    """
    Return the site index estimate for a single tree.
    """
    if curve.lower()=='fvs' and species is None:
        raise AttributeError('A valid species is required for curve=="fvs"')
        
    sc = curves[curve](variant, species, forest_code=forest)
    si = sc.site_index(age, height)
    if sc.index_bha:
        ref = 'bha'
    else:
        ref = 'tta'
        
    print('{:.2f}{} @{}={}'.format(si, sc.units, ref, sc.index_age))

@click.command()
@click.option('--curve', '-c', required=True, help='Site curve name.')
@click.option('--age', '-a', required=True, type=float, help='Tree age - BHA, TTA, etc. see curve description.')
@click.option('--site-index', '-i', required=True, type=float, help='Site index - See curve description.')
@click.option('--variant', '-v', required=False, type=str, help='FVS variant abbreviation when curve="fvs".')
@click.option('--forest', '-f', required=False, type=int, default=0, help='FVS forest code when curve="fvs".')
@click.option('--species', '-s', required=False, type=str, help='FVS species code when curve="fvs".')
def ht(curve, age, site_index, variant=None, forest=0, species=None):
    """
    Return the estimated height of a single tree for a given age and site index.
    """
    if curve.lower()=='fvs' and species is None:
        raise AttributeError('A valid species is required for curve=="fvs"')
    
    if curve.lower()=='fvs' and not variant:
        raise AttributeError('A FVS variant (e.g. -v=pn) is required for curve=="fvs"')

    sc = curves[curve](variant, species, forest_code=forest)
    ht = sc.height(age, site_index)
    if sc.index_bha:
        ref = 'bha'
    else:
        ref = 'tta'
        
    print('{:.2f}{} @{}={}'.format(ht, sc.units, ref, age))
    
@click.group(invoke_without_command=True)
@click.option('--help-curves', is_flag=True, default=False, help='Return a list of supported site curve funtions.')
@click.pass_context
def cli(ctx, help_curves=False, *args, **kwargs):

    if ctx.invoked_subcommand is None:
        if help_curves:
            msg = curve_docs()
            print(msg)
            sys.exit(0)

cli.add_command(si)
cli.add_command(ht)

if __name__ == '__main__':
    cli(obj={})