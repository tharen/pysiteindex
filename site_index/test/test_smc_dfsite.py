
import unittest

import pandas as pd

import site_index
import site_index.si

class Test_DF_SMC(unittest.TestCase):
    
    si = pd.Series([35,65,95])
    tta = pd.Series([5,15,30,50,70])
    # Published base heights
    ht = pd.DataFrame.from_records([
        [1.94,10.93,35.0,60.81,79.98],
        [2.76,23.26,65.0,109.28,138.84],
        [5.89,40.41,95.0,152.52,184.65],
        ])
    ht.index = si
    ht.index.name = 'si'
    ht.columns = tta
    
    def test_height(self):
        """
        Test the SMC height function.
        """
        df_smc = site_index.si.DF_SMC_SiteCurve(ht_plant=1.4)
        df_smc.set_density(2, 100, 300)
        
        for a in self.tta:
            for i in self.si:
                ht = self.ht.loc[i,a]
                hx = df_smc.height(a, i)
                assert round(float(hx),1)==round(float(ht),1)
    