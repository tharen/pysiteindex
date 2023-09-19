"""
Site curve classes
"""

# TODO: Implement a click based command line too for site index, height, and conversions.

from __future__ import print_function, division

import os
import sys
import abc
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from builtins import iter
import logging

try:
    import smc_dfsite
except:
    pass

try:
    import pyfvs.fvs

except:
    logging.warn('PyFVS is not available')
    pass

def find_si(
        ht_func, bha, ht, min_si=5.0, max_si=300.0
        , max_iters=20, ht_err=0.1):
    """
    Estimate the site index value that best matches the ht, age pair.

    Args
    ----
    ht_func: Function to estimate height given an age and site index.
    bha: Breast height age
    ht: Total height
    min_si: Minimum valid site index.
    max_si: Maximum valid site index.
    max_iters: Maximum number of search iterations to perform.
    ht_err: Allowable height tolerance.

    Return
    ------
    si: Estimated site index
    """

    if (ht is None) or (not np.isfinite(ht)) or (ht<=0.0):
        return -1 * np.Inf

    # First check the bounds of the search
    min_ht = ht_func(bha, min_si)
    if min_ht > ht:
        return -1 * np.Inf

    max_ht = ht_func(bha, max_si)
    if max_ht < ht:
        return np.Inf

    i = 0
    while i < max_iters:

        mid_si = (min_si + max_si) * 0.5
        mid_ht = ht_func(bha, mid_si)

        if mid_ht == np.NaN:
            return np.NaN

        if abs(ht - mid_ht) <= ht_err:
            break

        if mid_ht > ht:
            max_si = mid_si

        elif mid_ht < ht:
            min_si = mid_si

        i += 1

    return mid_si

def find_bha(
        ht_func, si, ht, ht_err=0.05, max_steps=50
        , min_bha=0, max_bha=500
        , min_ht=0, max_ht=500):
    """
    Estimate breast height age for a site index.

    Args
    ----
    ht_func: Function to estimate height given an age and site index.
    si: Site index
    ht: Total tree height
    max_bha: Maximum possible tree breast height age.
    ht_err: Height error tolerance.
    max_steps: Maximum number of search steps to attempt

    Return
    ------
    bha: Estimated breast height age

    Ref
    ---
    Adapted from:
    http://interactivepython.org/runestone/static/pythonds/SortSearch/TheBinarySearch.html
    """
    first = min_bha
    last = max_bha

    # Make sure the search will terminate
    if ht_err <= 0.0:
        ht_err = 0.001

    if ht <= min_ht:
        logging.warn('*** Height is less than the curve minimum: {}<={}'.format(ht, min_ht))
        return first

    # Make sure the maximum height is not exceeded
    if ht >= max_ht:
        logging.warn('*** Height is greater than curve maximum: {}>={}'.format(ht, max_ht))
        return last

    # Start the search with a check_ht well above the maximum allowable
    #   so the search does not get stuck
    check_ht = ht + ht_err + 999
    i = 0
    # Stop searching when the tolerance met
    # Stopping at max steps help guard against erroneous height functions
    while (abs(check_ht - ht) > ht_err) and (i < max_steps):
        # mid = round((first + last) / 2.0)
        mid = (first + last) * 0.5
        check_ht = ht_func(mid, si)
        if ht < check_ht:
            last = mid
        else:
            first = mid

        i += 1

#         logging.debug('** Search steps:', i)
    return mid

# TODO: Make adjustments for total age when index_bha=False

class SiteCurve(object):
    """
    Parent class with utility methods for site index (height growth) curves.

    All subclasses must override the `height` method, which is assumed to
    predict height as a function of age and site index.
    """
    __metaclass__ = abc.ABCMeta
    __curve_name__ = 'none'
    def __init__(self, name='', abbreviation=''
            , index_age=0, index_bha=True, min_bha=0, max_bha=250
            , min_si=10, max_si=250, si_incr=20, units='ft', *args, **kwargs):
        self.name = name
        self.abbreviation = abbreviation
        self.index_age = index_age
        self.index_bha = index_bha
        self.min_bha = min_bha
        self.max_bha = max_bha
        self.min_si = min_si
        self.max_si = max_si
        self.si_incr = si_incr
        self.units = units

        self.max_ht = self.height(self.max_bha, self.max_si)
        self.min_ht = self.height(self.min_bha, self.min_si)

    @abc.abstractmethod
    def height(self, bha, si):
        """
        Return total height given an age, site index pair.
        """
        msg = 'Height is not implemented for {}'.format(self.name)
        raise NotImplementedError(msg)

    # @abc.abstractmethod
    # def site_index(self, bha, ht):
        # """
        # Return site index calculated from breast height age and total height.
        # """
        # msg = 'Site index is not implemted for {}'.format(self.name)
        # raise NotImplemented(msg)

    @abc.abstractmethod
    def site_index(self, bha, ht):
        """
        Return an estimate of site index given age, height pair(s).

        NOTE: If not implemented the `find_si` search function is used.
        """
        if hasattr(bha, '__iter__') or hasattr(ht, '__iter__'):
            si = self.v_site_index(bha, ht)
        else:
            si = self.find_si(bha, ht)

        return si

    def v_height(self, bha, si):
        """
        Return an array of heights.  Vectorized form of `self.height`.
        """
        func = np.vectorize(self.height)
        ht = func(bha, si)
        return ht

    def v_site_index(self, bha, ht):
        """
        Return an array of site indexes. Vectorized form of `self.site_index`.
        """
        func = np.vectorize(self.site_index)
        si = func(bha, ht)
        return si

    def height_table(self
                , min_bha=None, max_bha=None, si_incr=20
                , min_si=None, max_si=None):
        """
        Return a dataframe of age height pairs for a range of site index values.
        """

        if min_bha is None: min_bha = self.min_bha
        if max_bha is None: max_bha = self.max_bha
        if min_si is None: min_si = self.min_si
        if max_si is None: max_si = self.max_si

        bha = np.arange(min_bha, max_bha + 1, 2)

        if not hasattr(si_incr, '__iter__'):
            si = np.round(np.arange(min_si, max_si + 1, si_incr))

        else:
            si = si_incr

        dfs = []
        for s in si:
            ht = self.v_height(bha, s)
            d = pd.DataFrame({'bha':bha, 'si':s, 'ht':ht})
            dfs.append(d)

        df = pd.concat(dfs)

        return df

    def site_index_table(self
                , min_bha=None, max_bha=None, bha_incr=5
                , min_ht=None, max_ht=None
                , min_si=None, max_si=None):
        """
        Return a dataframe of site index height pairs for a range of ages.
        """
        if min_bha is None: min_bha = self.min_bha
        if max_bha is None: max_bha = self.max_bha
        if min_ht is None: min_ht = self.min_ht
        if max_ht is None: max_ht = self.max_ht
        if min_si is None: min_si = self.min_si
        if max_si is None: max_si = self.max_si

        ht = np.arange(min_ht, max_ht + 1, 1)

        if not hasattr(bha_incr, '__iter__'):
            bha = np.round(np.arange(min_bha, max_bha + 1, bha_incr)).astype(int)
        else:
            bha = bha_incr

        dfs = []
        for a in bha:
            si = self.v_site_index(a, ht)
            si[si < min_si] = np.nan
            si[si > max_si] = np.nan
            d = pd.DataFrame({'bha':a, 'ht':ht, 'si':si})
            dfs.append(d)

        df = pd.concat(dfs)

        return df

    def age(self, si, ht):
        """
        Return an estimated breast-height age

        Args
        ----
        si: Site index
        ht: Total height
        """
        return self.find_bha(si, ht)

    def find_bha(self, si, ht, ht_err=0.1, max_steps=50):
        """
        Return an estimate of breast height age for a site_index, height pair.

        NOTE: BHA is found using a binary search method.
        """
        bha = find_bha(self.height, si, ht, ht_err=ht_err, max_steps=max_steps
                , min_bha=self.min_bha, max_bha=self.max_bha
                , min_ht=self.min_ht, max_ht=self.max_ht)
        return bha

    def find_si(self, bha, ht, **kwargs):
        si = find_si(self.height, bha, ht
                , min_si=self.min_si, max_si=self.max_si)

        return si

    def plot_height_growth(
            self, ax=None
            , min_bha=None, max_bha=None
            , si_incr=None, min_si=None, max_si=None
            , **kwargs):
        """
        Return a height growth chart as a matplotlib axis object.

        Args
        ----
        min_bha: Minimum breast height age to plot
        max_bha: Maximum breast height age to plot
        si_incr: Site index increment between each line
        min_si: Minimum site index to plot
        max_si: Maximum site index to plot
        """

        keys = ['min_bha', 'max_bha', 'si_incr', 'min_si', 'max_si']
        args = {}
        for k in keys:
            if locals()[k] is None:
                args[k] = getattr(self, k)
            else:
                args[k] = locals()[k]

        tbl = self.height_table(**args)

        if ax == None:
            fig, ax = plt.subplots()

        for key, grp in tbl.groupby(['si']):
            rate = grp - grp.shift()
            ht = (rate['ht'].values / rate['bha'].values)[1:]
            age = grp['bha'].values[1:]

            xloc = age[np.where(ht == ht.max())[0]][-1]

            p = ax.plot(age, ht, label=key, **kwargs)
            ax.text(xloc, np.nanmax(ht) + .02
                    , s=key, horizontalalignment='center')

#         l = ax.legend(loc='best', title='Site Index')
        p = ax.set_title('Height Growth Rate\n{}'.format(self.name))
        p = ax.set_xlabel('Breast Height Age')
        p = ax.set_ylabel('Annual Height Growth (ft/yr)')

        ax.axvline(self.index_age, color='grey', linestyle='dashed', linewidth=1.0)

        return ax

    def plot_height_curves(
            self, ax=None
            , min_bha=None, max_bha=None
            , si_incr=None, min_si=None, max_si=None
            , **kwargs):
        """
        Return site index height curves as a matplotlib axis object

        Args
        ----
        min_bha: Minimum breast height age to plot
        max_bha: Maximum breast height age to plot
        si_incr: Site index increment between each line
        min_si: Minimum site index to plot
        max_si: Maximum site index to plot
        """

        if max_bha is None:
            max_bha = self.index_age * 3

        keys = ['min_bha', 'max_bha', 'si_incr', 'min_si', 'max_si']
        args = {}
        for k in keys:
            if locals()[k] is None:
                args[k] = getattr(self, k)
            else:
                args[k] = locals()[k]

        tbl = self.height_table(**args)

        if ax == None:
            fig, ax = plt.subplots()

        for key, grp in tbl.groupby(['si']):
            ht = grp['ht'].values
            age = grp['bha'].values
            xloc = args['max_bha'] - 3

            p = ax.plot(age, ht, label=key, **kwargs)
            ax.text(xloc, np.nanmax(ht) + 1
                    , s=key, horizontalalignment='right')

#         l = ax.legend(loc='best', title='Site Index')
        p = ax.set_title('Height Curves\n{}'.format(self.name))
        p = ax.set_xlabel('Breast Height Age')
        p = ax.set_ylabel('Total Height (ft)')

        ax.axvline(self.index_age, color='grey', linestyle='dashed', linewidth=1.0)

        # ax.set_xlim(0,self.index_age*3)

        return ax

    def plot_site_index_curves(
            self, ax=None
            , min_bha=None, max_bha=None, bha_incr=None
            , min_ht=10, max_ht=250
            , min_si=50, max_si=150
            , **kwargs):

        if max_bha is None:
            max_bha = int(round(self.index_age*3.0/10.0)*10)

        if min_bha is None:
            min_bha = int(round(self.index_age/3.0/10.0)*10)

        bha_incr = int((max_bha - min_bha) / 9.0)
        bha_incr = min([10,15,20], key=lambda x:abs(x-bha_incr))

        tbl = self.site_index_table(
                min_bha, max_bha, bha_incr, min_ht, max_ht, min_si, max_si
                )
#         print(tbl)

        if ax == None:
            fig, ax = plt.subplots()

        pfx = 'Age='
        ha = 'right'
        for key, grp in tbl.groupby(['bha']):
            p = ax.plot(grp['ht'], grp['si'], label=key, **kwargs)
            i = np.nanargmax(grp['si'].values)
            y = round(np.nanmax(tbl['si'].values)) + 1
            s = ax.text(grp['ht'][i], y, s='{}{}'.format(pfx, key)
                    , horizontalalignment=ha)
            pfx = ''
            ha = 'center'

#         l = ax.legend(loc='best', title='BHA')
        p = ax.set_title('Site Index Estimation Curves\n{}'.format(self.name))
        p = ax.set_ylabel('Site Index (ft@{})'.format(self.index_age,))
        p = ax.set_xlabel('Total Height (ft)')

        ax.set_ylim(min_si - 5, max_si + 5)

        return ax

class DF_King_SiteCurve(SiteCurve):
    """
    Douglas-fir, King (1966)
    """
    __curve_name__ = 'king_1966'
    def __init__(self, *args, **kwargs):
        SiteCurve.__init__(self
                , name='Douglas-fir, King (1966)'
                , abbreviation='King (1966)'
                , index_age=50, index_bha=True
                , min_bha=10, max_bha=130
                , min_si=40, max_si=160
                , units='ft')

    @staticmethod
    def height(bha, si):
        """
        Return total height using King (1966).

        Args
        ----
        bha - Breast Height Age
        si - Site Index (total height at bha==50)

        Refs
        ----
        King (1966)
        """

        a0 = -0.954038
        a1 = 0.109757
        b0 = 0.0558178
        b1 = 0.00792236
        c0 = -0.000733819
        c1 = 0.000197693

        z50 = 2500 / (si - 4.5)
        a = a0 + a1 * z50
        b = b0 + b1 * z50
        c = c0 + c1 * z50

        ht = (bha * bha) / (a + b * bha + c * (bha * bha)) + 4.5

        return ht

    @staticmethod
    def site_index(bha, ht):
        """
        Return King's site index given total height and breast height age.

        This solves King's total height formula for site index by substituting
            the coefficient predictor equations and factoring out Z for bha 50.

        Args
        ----
        bha - Breast Height Age
        ht - Total Height
        """
        a0 = -0.954038
        a1 = 0.109757
        b0 = 0.0558178
        b1 = 0.00792236
        c0 = -0.000733819
        c1 = 0.000197693

        i = bha ** 2 / (ht - 4.5)
        j = i - a0 - b0 * bha - c0 * bha ** 2
        k = a1 + b1 * bha + c1 * bha ** 2
        si = 4.5 + 2500 * (k / j)

        return si

    def plot_site_index_curves(self, ax=None
            , min_bha=20, max_bha=120, bha_incr=10
            , min_ht=20, max_ht=250
            , min_si=50, max_si=150):

        super(DF_King_SiteCurve, self).plot_site_index_curves(
            ax, min_bha, max_bha, bha_incr, min_ht, max_ht, min_si, max_si)


class WH_Wiley_SiteCurve(SiteCurve):
    """
    Western Hemlock, FIA PNW eq. 5a, Wiley (1978)
    """
    __curve_name__ = 'wiley_1978'
    def __init__(self, *args, **kwargs):
        SiteCurve.__init__(self
                , name='Western Hemlock, Wiley (1978)'
                , abbreviation='Wiley (1978)'
                , index_age=50, index_bha=True
                , min_bha=0, max_bha=150
                , min_si=40, max_si=160
                , units='ft')

    @staticmethod
    def height(bha, si):
        """
        FIA PNW eq. 5a, Wiley (1978), solved for height
        """
        a0 = 0.1394
        a1 = 0.0137
        a2 = 0.00007
        b0 = -1.7307
        b1 = -0.0616
        b2 = 0.00192

        z = 2500 / (si - 4.5)
        i = a0 + a1 * bha + a2 * bha ** 2
        j = b0 + b1 * bha + b2 * bha ** 2
        h = bha ** 2 / (z * i + j) + 4.5

        return h

    @staticmethod
    def site_index(bha, ht):
        """
        FIA PNW eq. 5a, Wiley (1978)
        """
        a0 = 0.1394
        b0 = 0.0137
        c0 = 0.00007
        a1 = -1.7307
        b1 = -0.0616
        c1 = 0.00192

        x = a0 + b0 * bha + c0 * bha ** 2.0
        y = a1 + b1 * bha + c1 * bha ** 2.0

        try:
            si = 2500 * (
                    ((ht - 4.5) * x) / (bha ** 2.0 - (ht - 4.5) * y)
                    ) + 4.5
        except:
            logging.error('Error computing site index: bha:{}, ht:{}'.format(bha, ht))
            si = np.NaN

        return si

class DF_Bruce_SiteCurve(SiteCurve):
    """
    Douglas-fir, Bruce (1981)
    """
    __curve_name__ = 'bruce_1981'
    def __init__(self, *args, **kwargs):
        SiteCurve.__init__(self
                , name='Douglas-fir, Bruce (1981)'
                , abbreviation='Bruce (1981)'
                , index_age=50, index_bha=True
                , min_bha=3, max_bha=200
                , min_si=10, max_si=250
                , units='ft')

    @staticmethod
    def height(bha, si):
        """
        Bruce (1981)
        """
        ytb = 13.25 - si / 20
        b3 = (-0.447762 - 0.894427 * (si / 100)
                + 0.793548 * (si / 100) ** 2.0
                - 0.171666 * (si / 100) ** 3.0
                )

        z = ((13.25 - si / 20) ** b3 - (63.25 - si / 20) ** b3)
        b2 = np.log(4.5 / si) / z

        ht = si * np.exp(b2 * ((bha + ytb) ** b3 - (50 + ytb) ** b3))

        return ht

    def plot_site_index_curves(self, ax=None
            , min_bha=20, max_bha=120, bha_incr=10
            , min_ht=20, max_ht=250
            , min_si=50, max_si=150):

        super(DF_Bruce_SiteCurve, self).plot_site_index_curves(
            ax, min_bha, max_bha, bha_incr, min_ht, max_ht, min_si, max_si)

class RA_Harrington_SiteCurve(SiteCurve):
    """
    Red alder, Harrington (1986)
    """
    __curve_name__ = 'harrington_1986'
    def __init__(self, *args, **kwargs):
        SiteCurve.__init__(self
                , name='Red alder, Harrington (1986)'
                , abbreviation='Harrington (1986)'
                , index_age=20, index_bha=True
                , min_bha=0, max_bha=150
                , units='ft')
        # FIXME: Harrington RA age range

    def plot_height_growth(self, ax=None
            , min_bha=1, max_bha=50, si_incr=10, min_si=35, max_si=75):

        super(RA_Harrington_SiteCurve, self).plot_height_growth(
                ax, min_bha, max_bha, si_incr, min_si, max_si)

    def plot_height_curves(self, ax=None
            , min_bha=1, max_bha=50, si_incr=10, min_si=35, max_si=75):

        super(RA_Harrington_SiteCurve, self).plot_height_curves(
                ax, min_bha, max_bha, si_incr, min_si, max_si)

    def plot_site_index_curves(self, ax=None
            , min_bha=5, max_bha=50, bha_incr=5, min_ht=0, max_ht=120
            , min_si=35, max_si=75):

        super(RA_Harrington_SiteCurve, self).plot_site_index_curves(
            ax, min_bha, max_bha, bha_incr, min_ht, max_ht, min_si, max_si)

    @staticmethod
    def site_index_direct(bha, ht):
        """
        Harrington (1986)

        NOTE: This is the independently fit SI function. Harrington argues
                that solving for SI as the dependent variable is more
                correct for predicting SI than simply solving the height
                growth function for SI.
        """
        if bha <= 0:
            return 0.0

        a = 54.1857 - 4.6170 * bha + 0.11065 * bha ** 2 - 0.00076335 * bha ** 3
        b = 1.25934 - 0.012989 * bha + 3.5220 * (1.0 / bha) ** 3

        si = a + b * ht

        return si

    @staticmethod
    def height(bha, si):
        """
        Harrington (1986)
        """

        # Implement equation 4 with english units
        a = 59.5864
        b = 0.7953
        c = 0.001940
        d = -0.0007403
        f = 0.9198

        # NOTE: There is a typo and poor formatting in the publication
        #       This was cross checked with the FVS PN source code (htcalc.f)
        #       b -> d in second term, and f exponent on first eq chunk
        x = (a + b * si) * (1.0 - np.exp((c + d * si) * bha)) ** f
        y = (a + b * si) * (1.0 - np.exp((c + d * si) * 20.0)) ** f

        ht = si + x - y

        return ht

class SS_Farr_SiteCurve(SiteCurve):
    """
    Sitka spruce, Farr (1984), Res. Paper PNW-326
    """
    __curve_name__ = 'farr_1984'
    def __init__(self, *args, **kwargs):
        SiteCurve.__init__(self
                , name='Sitka Spruce, Farr (1984)'
                , abbreviation='Farr (1984)'
                , index_age=50, index_bha=True
                , min_si=40, max_si=160
                , min_bha=5, max_bha=150
                , units='ft'
                )

    @staticmethod
    def height(bha, si):
        """
        Sitka spruce, Farr, Res. Paper PNW-326

        Also used for Western red cedar.

        NOTE: Adapted from FVS PN variant `htcalc.f`
        """
        B0 = -0.2050542
        B1 = 1.449615
        B2 = -0.01780992
        B3 = 6.519748e-5
        B4 = -1.095593e-23
        B5 = -5.611879
        B6 = 2.418604
        B7 = -0.2593110
        B8 = 1.351445e-4
        B9 = -1.701139e-12
        B10 = 7.964197e-27
        B11 = -86.43

        AZ = (B0 + B1 * np.log(bha)
                + B2 * np.log(bha) ** 3.0
                + B3 * np.log(bha) ** 5.0
                + B4 * np.log(bha) ** 30.0)
        BZ = (B5 + B6 * np.log(bha) + B7 * np.log(bha) ** 2.0 + B8 * np.log(bha) ** 5.0
                + B9 * np.log(bha) ** 16.0 + B10 * np.log(bha) ** 36.0)
        ht = 4.5 + np.exp(AZ) + B11 * np.exp(BZ) + (si - 4.5) * np.exp(BZ)

        return ht

class DF_Curtis_SiteCurve(SiteCurve):
    """
    Douglas-fir, Curtis, 1972
    """
    __curve_name__ = 'curtis_1974'
    def __init__(self, *args, **kwargs):
        SiteCurve.__init__(self
                , name='Douglas-fir, Curtis (1974)'
                , abbreviation='Curtis (1974)'
                , index_age=100, index_bha=True
                , min_bha=5, max_bha=250
                , min_si=50, max_si=250
                , units='ft')

    @staticmethod
    def height(bha, si):
        """
        Douglas-fir, Curtis, 1972

        Used for "other" species in FVS

        NOTE: Adapted from FVS (PN, WC) source code `htcalc.f`.
        """

        b0 = 0.6192
        b1 = -5.3394
        b2 = 240.29
        b3 = 3368.9

        ht = (
                (si - 4.5) / (b0 + b1 / (si - 4.5)
                + b2 * bha ** (-1.4) + (b3 / (si - 4.5)) * bha ** (-1.4))
                ) + 4.5

        return ht

class DF_SMC_SiteCurve(SiteCurve):
    """
    Douglas-fir site curves produced for the Stand Management Cooperative.

    Args
    ----
    max_age: Maximum age to project site index and height
    units: Height units 'ft' or 'm'
    convergence: Convergence criterion (see DFSITE documents)
    ht_plant: Tree height at planting, fixed at two years of age.

    Reference
    ---------
    Height-age curves for planted stands of Douglas fir, with
        adjustments for density. A report prepared for the Stand Management
        Coop, March 30, 2000 (revised December, 2000). By James Flewelling,
        Randy Collier, Bob Gonyea, David Marshall and Eric Turnblom.
    """

    __curve_name__ = 'smc_2001'
    def __init__(self, *args, **kwargs):
        #max_age=100, units='ft', convergence=0.5 / 12.0, ht_plant=1.4
        self.max_age = kwargs.get('max_age', 100)
        self.units = kwargs.get('units', 'ft').lower()
        self.convergence = kwargs.get('convergence', 0.5/12.0)
        self.ht_plant = kwargs.get('ht_plant', 1.4)

        if self.units=='ft':
            self._units = 1
        else:
            self._units = 2

        SiteCurve.__init__(self
                , name='Douglas-fir, SMC (2001)'
                , abbreviation='SMC (2001)'
                , index_age=30, index_bha=False
                , min_bha=1, max_bha=70
                , min_si=10, max_si=100
                )

        self.setup()

    def setup(self):
        """
        Initialize the dfsite library
        """

        if not 'smc_dfsite' in sys.modules:
            raise SystemError('smc_dfsite is not available')

        err = smc_dfsite.dfsite1(self.max_age, self._units, self.convergence)
        smc_dfsite.dfsite2(self.ht_plant)

        # Base curves assume a density of 300 TPA
        self.set_density(2, 100, 300)

    def set_density(self, age1, age2, density):
        """
        Set the density (TPA) regime for a specific age range
        """
        # Base curves assume a density of 300 TPA
        dense = np.zeros((100), dtype=np.float32)
        dense[age1:age2] = density
        err = smc_dfsite.dfsite3d(age1, age2, dense)
        if err != 0:
            raise ValueError('Error setting density regime.')

    def height(self, tta, si):
        """
        Return an estimate of total height for a given site index and age.

        Args
        ----
        tta - Tree age (from seed).
        si - Site index.
        """
        self.setup()
        psi, si, err = smc_dfsite.dfsite3h(si, 1, self.index_age)
        ht_base, ht_adj = smc_dfsite.dfsite4(tta)
        return ht_base

    def site_index(self, tta, ht):
        """
        Return and estimate of site index given a total age, height pair.

        Args
        ----
        tta: Tree age (from seed)
        """
        self.setup()
        psi, si, err = smc_dfsite.dfsite3h(ht, 1, tta)
        return si

class FVS_SiteCurve(SiteCurve):
    """
    Species site curves embedded in FVS variant libraries.
    """
    __curve_name__ = 'fvs'

    def __init__(self, fvs_variant, spp, forest_code=0, *args, **kwargs):
        self.fvs_variant = fvs_variant.upper()
        self.spp = spp.upper()
        ## TODO: Get default forest code from FVS
        self.forest_code = forest_code

        self.fvs = None
        self.spp_idx = 39
        self.spp_valid = False

        self._setup()

        # Specify the index age
        # TODO: Can this be discovered from the FVS library?
        idx_age = 100
        max_si = 200
        min_si = 50
        if self.fvs_variant in ('PN',):
            if self.spp in ('DF', 'WH', 'SS', 'GF', 'WF', 'LP'):
                idx_age = 50
                max_si = 200

            elif spp in ('RA',):
                idx_age = 20
                max_si = 200

        elif self.fvs_variant in ('WC',):
            if self.spp in ('WH', 'SS', 'GF', 'WF', 'LP'):
                idx_age = 50
                max_si = 200

            elif self.spp in ('DF',):
                idx_age = 100
                max_si = 300

            elif self.spp in ('RA',):
                idx_age = 20
                max_si = 200

        elif self.fvs_variant in ('CA'):
                idx_age = 50
                max_si = 200

        elif self.fvs_variant in ('SO'):
                idx_age = 50
                max_si = 200

                if self.spp in ('SP','PP','MH','ES','WJ','WB','AF','NF','WC'):
                    idx_age = 100
                    max_si = 200

                elif self.spp in ('RA',):
                    idx_age = 20
                    max_si = 200

                elif self.spp in ('AS',):
                    idx_age = 80
                    max_si = 200

        # FIXME: index_bha is not always True
        # FIXME: units for some variants are metric
        SiteCurve.__init__(self
                , name='FVS Variant Site Curve'
                , abbreviation=self.abbreviation
                , index_age=idx_age, index_bha=True
                , min_si=min_si
                , max_si=max_si
                , units='ft'
                , **kwargs)

    def _setup(self):
        self.fvs = pyfvs.fvs.FVS(self.fvs_variant)
        self.fvs.fvs_step.init_blkdata()

        if not self.spp in list(self.fvs.spp_codes):
            msg = (f'Species code {self.spp} is not recognized.  '
                f'Expected one of {list(self.fvs.spp_codes)}'
                )
            raise ValueError(msg)

        self.spp_idx = list(self.fvs.spp_codes).index(self.spp) + 1

        # try:
            # if not self.spp in list(self.fvs.spp_codes):
                # if self.fvs_variant in ('SO', 'CA'):
                    # ds = 'OS'
                    # self.spp_idx = list(self.fvs.spp_codes).index(ds) + 1
                # else:
                    # ds = 'OT'
                    # self.spp_idx = list(self.fvs.spp_codes).index(ds) + 1

                # logging.info(('Site species code not found for {}, variant {}'
                        # ', defaulting to {}'
                        # ).format(self.spp, self.fvs_variant, ds))

            # else:
                # self.spp_idx = list(self.fvs.spp_codes).index(self.spp) + 1

            # self.spp_valid = True

        # except ValueError:
            # logging.info('Site species code not found for {}, defaulting to "OT"'.format(self.spp))
            # self.spp_idx = list(self.fvs.spp_codes).index('OT') + 1
            # spp_valid = False

        ## TODO: re-enable if FVS default kodfor is fixed
        # if self.forest_idx == 0:
        #     logging.warn('Forest code {} is not recognized.'.format(self.forest_code))

#         idx_ages = {'PN':{
#                 100:('SF','NF','WP','SP','PP','IC','JP','OT','RF','MH',)
#                 , 50:('DF','WH','SS','RC','GF')
#                 , 20:('RA',)
#                 }}

    @property
    def forest_idx(self):
        """Index of the FVS forest location code."""
        self.fvs.globals.kodfor = [self.forest_code, ]
        self.fvs.forkod()
        return self.fvs.globals.ifor

    @property
    def name(self):
        # TODO: Interogate the FVS library for references???
        s = 'FVS-{} Height Curve (sp={})'.format(
                self.fvs_variant, self.spp)
        return s

    @name.setter
    def name(self, value):
        pass

    @property
    def abbreviation(self):
        s = 'FVS {} ({})'.format(self.fvs_variant, self.spp)
        return s

    @abbreviation.setter
    def abbreviation(self, value):
        pass

    def height(self, bha, si):
        """

        """

        if self.fvs_variant in ('PN', 'WC', 'OP'):
            ht = self.fvs.htcalc(si, self.spp_idx, bha)

        elif self.fvs_variant in ('SO', 'CA', 'OC'):
            ht = self.fvs.htcalc(self.forest_idx, si, self.spp_idx, bha)

        else:
            logging.warn('Height not fully implemented for variant: {}'.format(
                    self.fvs_variant))
            ht = self.fvs.htcalc(si, self.spp_idx, bha)

        return ht

# def test():
#     si = WH_SiteCurve()
#     site_idx = 120
#     print('si:', site_idx)
#
#     print()
#     print('Direct Ht Calc:')
#     print('BHA: 50', 'Site Idx:', site_idx, 'height:', si.height(50, site_idx))
#
#     print()
#     print('Find effective bha and height:')
#     bha = si.find_bha(site_idx, 100, ht_err=0.5)
#     print('Approx. BHA:', bha)
#     ht = si.height(bha, site_idx)
#     print('BHA: 50', 'Site Idx:', site_idx, 'height:', ht)
#
#     bha = range(10, 150, 10)
#     hts = si.v_height(bha, site_idx)
#     sx = si.v_site_index(bha, hts)
# #     sx = si.v_site_index(50, hts)
#
#     print()
#     print('Vectorized height and site_index functions:')
#     print('bha', bha)
#     print('ht:', [round(h, 1) for h in hts])
#     print('si:', [round(s, 1) for s in sx])
#
#     tbl = si.site_index_table()
#     si.plot_site_curves()
#
#     dfsi = DF_King_SiteCurve()
# #     fig = plt.gcf()
#     fig = dfsi.plot_site_curves()
#     n = 'site_curves_{}.png'.format(dfsi.abbreviation)
#     fn = os.path.join('c:/temp', n)
#     fig.savefig(fn)
#
#     whsi = WH_SiteCurve()
#     fig = whsi.plot_site_curves()
#     n = 'site_curves_{}.png'.format(whsi.abbreviation)
#     fn = os.path.join('c:/temp', n)
#     fig.savefig(fn)
#
# if __name__ == '__main__':
#     test()
