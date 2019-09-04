# Implement Site index functions
def df_king_ht(bha,si50):
    """
    Return total height given breast height age and 50 year site index using King (1966).
    
    Ref. King (1966)
    """

    a0 = -0.954038
    a1 = 0.109757
    b0 = 0.0558178
    b1 = 0.00792236
    c0 = -0.000733819
    c1 = 0.000197693

    z50 = 2500/(si50-4.5)
    a = a0 + a1*z50
    b = b0 + b1*z50
    c = c0 + c1*z50
    
    ht = (bha*bha) / (a + b*bha + c*(bha*bha)) + 4.5
    
    return ht

def df_king_si(bha, ht):
    """
    Return King's site index given total height and breast height age.
    
    This solves King's total height formula for site index by substituting 
        the coeffient predictor equations and factoring out Z for age 50
    """
    a0 = -0.954038
    a1 = 0.109757
    b0 = 0.0558178
    b1 = 0.00792236
    c0 = -0.000733819
    c1 = 0.000197693

    i = bha**2/(ht-4.5)
    j = i - a0 - b0*bha - c0*bha**2
    k = a1 + b1*bha + c1*bha**2
    si = 4.5 + 2500 * (k/j)
    return si

def df_curtis_ht(bha, si):
    """Curtis, et al, 1974"""
    a = 0.6192
    b = -5.3394
    c = 240.29
    d = 3368.9
    n = -1.4
    
    bha[bha<=0] = 1
    
    ht = 4.5 + (si-4.5)/(a + b/(si-4.5) + c*bha**n + d/(si-4.5)*bha**n)
    
    ht[bha<=0] = 4.5
    
    return ht

def ra_harringtion_si(bha, ht):
    """
    Return 20 year site index for red alder
    
    Ref: Harrington and Curtis (1985).
    """
    a0 = 54.1850
    a1 = -4.61694
    a2 = 0.11065
    a3 = -0.0007633
    b0 = 1.25934
    b1 = -0.012989
    b2 = 3.5220
    
    a = a0 + a1*bha + a2*bha**2 + a3*bha**3
    b = b0 + b1*bha + b2*(1/bha)**3
    si = a + b*ht
    
    return si

def ra_harringtion_ht(bha, si):
    """
    Return total height for red alder.  *20 year site index.
    
    Ref: Harrington and Curtis (1985).
    """
    a0 = 54.1850
    a1 = -4.61694
    a2 = 0.11065
    a3 = -0.0007633
    b0 = 1.25934
    b1 = -0.012989
    b2 = 3.5220
    
    a = a0 + a1*bha + a2*bha**2 + a3*bha**3
    b = b0 + b1*bha + b2*(1/bha)**3
    ht = (si-a)/b
    
    return ht
    
def nf_fia_si(bha, ht):
    """
    FIA Eq. 4, Noble fir
    """
    if bha<=100:
        si = (4.5 + 0.2145*(100-bha) + 0.0089*(100-bha)**2)
        si += ((1.0 + 0.00386*(100-bha) + 1.2518*(100-bha)**5)/10**10)*(ht-4.5)
    else:
        si = -62.755 + 672.55*(1/bha)**0.5
        si += (0.9484 + 516.49*(1/bha)**2) * (ht-4.5)
        si += (-0.00144 + 0.1442*(1/bha)) * (ht-4.5)
    
    return si
    
def ra_fia_si(bha, ht):
    """
    FIA Eq. 13, Red alder and other hardwoods.
    """
    si = (0.60924 + 19.538/bha) * ht
    return si

def wh_fvs_ht(bha, si):
    """
    FVS PN implementation of Wiley, 1978
    """
    b0 = -1.7307
    b1 = 0.1394
    b2 = -0.0616
    b3 = 0.0137
    b4 = 0.00192
    b5 = 0.00007
    
    z = 2500.0/(si-4.5)
    ht = (bha**2.0/(b0 + b1*z + (b2 + b3*z)*bha + (b4 + b5*z)*(bha**2.0))) + 4.5
    return ht

def wh_fvs_si(bha, ht):
    """
    FVS PN implementation of Wiley, 1978
    """
    
    b0 = -1.7307
    b1 = 0.1394
    b2 = -0.0616
    b3 = 0.0137
    b4 = 0.00192
    b5 = 0.00007
    
    i = b1 + b3*bha + b5*bha**2.0
    j = b0 + b2*bha + b4*bha**2.0
    k = bha**2.0 / (ht-4.5)
    si = 2500.0 * (i/(k-j)) + 4.5
    return si

def wh_fia_si(bha, ht):
    """
    FIA Eq. 5, BHA<=120 Wiley (1978); BHA>120 Barnes (1962)
    """
    
    if bha<=120:
        # Wiley (1978)
        a0=0.1394
        b0=0.0137
        c0=0.00007
        a1=-1.7307
        b1=-0.0616
        c1=0.00192

        i = (ht-4.5) * (a0 + b0*bha + c0*bha**2)
        j = bha**2 - (ht-4.5)*(a1 + b1*bha + c1*bha**2)
        si = 2500 * (i/j) + 4.5
    
    else:
        # Barnes (1962)
        si = 4.5 + 22.6 * math.exp((0.014482 - 0.001162*math.log(bha**2)) * (ht-4.5))
    
    return si

def wh_fia_ht(bha,si):
    ##TODO: include the Barnes eq for trees >120 years
    """
    Wiley (1978) Solved for height
    """
    a0=0.1394
    b0=0.0137
    c0=0.00007
    a1=-1.7307
    b1=-0.0616
    c1=0.00192

    z = 2500/(si-4.5)
    i = a0 + b0*bha + c0*bha**2
    j = a1 + b1*bha + c1*bha**2
    h = bha**2 / (z*i + j) + 4.5
    return h

def find_age(ht_func, si, ht, max_age=300.0, steps=10, ht_err=0.5):
    """
    Return approximate breast height age given a height function, site index, and total height.
    """
    
    # Locate the approximate age using a binary search
    # If ht_func is not monotonic this will fail
    age_high = max_age
    age_low = 0.0
    age_mid = max_age * 0.5
    
    # Pre-define the half steps
    steps = (0.5**np.arange(1,steps+1,1)) * age_mid
    
    for step in steps:
        # Calculate the mid-point to test
        ht_mid = ht_func(age_mid, si)
        
        # If the absolute error is within the defined tolerance, we're done
        if abs(ht_mid-ht)<ht_err:
            break
            
        if ht<ht_mid:
            # If the mid-point overshot the height
            #   reduce the age by a half step
            age_high = age_mid
            age_mid = age_mid - step
        else:
            # Otherwise increase the age by a half step
            age_low = age_mid
            age_mid = age_mid + step
        
    return age_mid

# age = 60
# si = 120
# ht = 133.892

# find_age(king_ht, si, ht)
