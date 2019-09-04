import unittest
import pytest

import pandas as pd
import numpy as np

import site_index
import site_index.si

ht_func = site_index.si.FVS_SiteCurve('PN','OT')
ht_func = None

variants = [('pn',),('wc',),('ca',),('so',)]
spp = {
        'ca':['PP','DF','LP'],
        'so':['DF','SF','PP'],
        'pn':['DF','WH','RA'],
        'wc':['DF','RF','RA']
        }

@pytest.mark.parametrize(('variant',), variants)
def test_height(variant):
    for sp in spp[variant]:
        si = site_index.si.FVS_SiteCurve(variant, sp)
        ht = si.height(50,50)

if __name__=='__main__':
    test_height('so')
    
# class Test_FVS_SiteCurve(unittest.TestCase):
    # """    
    # """
    
    # # test data
    # si = pd.Series([70,100,130])
    # bha = pd.Series([15,50,75,120])
    # ht = pd.DataFrame.from_records([
        # [26.7,70.0,86.7,104.3],
        # [37.3,100.0,125.1,152.2],
        # [48.1,130.0,163.9,201.7]
        # ])
    # ht.index = si
    # ht.index.name = 'si'
    # ht.columns = bha
    
    # def test_height(self):
        # """
        # Test the King (1966) DF height function.
        # """
        # df_king = site_index.si.DF_King_SiteCurve()
        
        # for a in self.bha:
            # for i in self.si:
                # ht = self.ht.loc[i,a]
                # hx = df_king.height(a, i)
                # assert abs(hx-ht)<0.1

    # def test_site_index(self):
        # """
        # Test the King (1966) DF site index function.
        # """
        # df_king = site_index.si.DF_King_SiteCurve()
        
        # for a in self.bha:
            # for i in self.si:
                # ht = self.ht.loc[i,a]
                # sx = df_king.site_index(a, ht)
                # assert abs(i-sx)<0.1
                
    # def test_find_si(self):
        # """
        # Test the King (1966) DF site index search function.
        # """
        # df_king = site_index.si.DF_King_SiteCurve()
        
        # errs = []
        # for a in self.bha:
            # for i in self.si:
                # ht = self.ht.loc[i,a]
                # sx = df_king.find_si(a, ht)
                # if not abs(sx-i)==0:
                    # errs.append([a,ht,i,sx]) 

        # if not errs==[]:
            # print('Misses finding equivalent SI:')
            # df = pd.DataFrame.from_records(errs)
            # df.columns = ['BHA','Ht','SI','SI_est']
            # print(df)
            # raise AssertionError('SI search errors')
         
    # def test_find_bha(self):
        # """
        # Test the King (1966) DF age search function.
        # """
        # df_king = site_index.si.DF_King_SiteCurve()
        
        # errs = []
        # for a in self.bha:
            # for i in self.si:
                # ht = self.ht.loc[i,a]
                # ax = df_king.find_bha(i, ht)
                
                # # Verify BHA rounds the same
                # if not abs(a-ax)==0:
                    # errs.append([i,ht,a,ax])
                    
        # if not errs==[]:
            # print('Misses finding equivalent BHA:')
            # df = pd.DataFrame.from_records(errs)
            # df.columns = ['SI','Ht','BHA','BHA_est']
            # print(df)
            # raise AssertionError('BHA search errors') 

    # def test_validate(self):
        # """
        # Validate King (1966) site index against the original publication.
        # """
        # from site_index.test import king_data
        # df_king = site_index.si.DF_King_SiteCurve()
        # ht_func = df_king.v_height
        
        # # Tables of data reported in the original publication by King, 1966.
        # king_si = king_data.si
        
        # si_dfs = []
        # for s in king_si:
            # l = len(s[0])
            # cols = s[0]
            # # Load the data records to a dataframe
            # data = np.array([s[i] for i in range(1,len(s))])
            # df = pd.DataFrame.from_records(data)
            # df.columns = cols
            # df.set_index('bha',inplace=True)
            # df = df.stack().reset_index()
            # df.columns = ('bha','si','ht')
            # si_dfs.append(df)
        
        # si_df = pd.concat(si_dfs)
        # si_df['ht_y'] = df_king.v_height(si_df['bha'],si_df['si'])
        # si_df['ht_diff'] = si_df['ht_y'] - si_df['ht']
        
        # # TODO: find out why BHA <10 does validate
        # m = (si_df['bha']>=10) & (si_df['ht_diff'].abs()>0.2)
        
        # v = si_df.loc[m]
        # if v.shape[0]>0:
            # print('King Validation Errors')
            # print(v)
            # raise AssertionError()
