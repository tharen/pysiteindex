# Function to compute site index from age and height as well as height
# from site and age.

#Hanson, Erica J.; Azuma, David L.; Hiserote, Bruce A.  2003.  Site index
#   equations and mean annual increment equations for Pacific Northwest
#   Research Station forest inventory and analysis inventories, 1985-2001.
#   Res. Note PNW-RN-533. Portland, OR: U.S. Department of Agriculture,
#   Forest Service, Pacific Northwest Research Station. 24 p.


king.siteindex = function(age,height){
  a = (height-4.5) + 0.954038 - 0.0558178*age + 0.000733819 * age**2
  b = 0.109757 + 0.00792236*age + 0.000197693*age*age

  si = 2500 / (age*age / a / b) + 4.5

  return(si)
}

king.height.fia = function(age, siteindex){
  ##---Transform the King equation to return height given age and site index.
  a =  0.954038 - 0.0558178*age + 0.000733819*age**2
  b = 0.109757 + 0.00792236*age + 0.000197693*age**2

  ht = age**2 / (b / ((siteindex-4.5)/2500.0)) - a + 4.5

  return(ht)
}

king.height.fvs = function(age,siteindex){
  # FVS PN HTCALC Equation
  # Adapted from FVS PN Variant, pn/htcalc.f & pn/blkdat.f
  AG = age
  SINDX = siteindex
  B0 = -0.954038
  B1 = 0.109757
  B2 = 5.58178E-2
  B3 = 7.92236E-3
  B4 = -7.33819E-4
  B5 = 1.97693E-4

  Z = 2500./(SINDX-4.5)
  HGUESS = (AG*AG/(B0 + B1*Z + (B2 + B3*Z)*AG + (B4 + B5*Z)*(AG*AG))) + 4.5

  return(HGUESS)
}

# # Adapted from King 1966
# #FIXME: This is not implemented correctly
# king.height = function(A,Z50){
#   a0 = -0.954038
#   a1 = 0.109757
#   b0 = 0.0558178
#   b1 = 0.00792236
#   c0 = -0.000733819
#   c1 = 0.000197693
#
#   Z = A^2/(Z50-4.5)
#   a = a0 + a1*Z50
#   b = b0 + b1*Z50
#   c = c0 + c1*Z50
#
#   H = A^2/(a + b*A + c*A^2) + 4.5
#   return(H)
# }

#Curtis DF, Equation 14 from Hanson 2003
curtis.siteindex = function(age, height){
  if (age<=100){
    a = 0.010006 * (100 - age)^2
    b = 1 + 0.00549779 * (100 - age) + 1.46842*10^-14 * (100 - age)^7
  } else {
    a = 7.66772 * exp(-0.95*(100.0/(age-100.0))**2)
    b = 1.0 - (0.730948 * (log10(age)-2.0)**0.8)
  }
  si = 4.5 + a + (b * (height - 4.5))
  return(si)
}

curtis.height = function(age, siteindex){
  if (age<=100){
    a = 0.010006 * (100 - age)^2
    b = 1 + 0.00549779 * (100 - age) + 1.46842*10^-14 * (100 - age)^7
  } else {
    a = 7.66772 * exp(-0.95*(100.0/(age-100.0))**2)
    b = 1.0 - (0.730948 * (log10(age)-2.0)**0.8)
  }
  ht = ((siteindex - 4.5) - a) / b + 4.5
  return(ht)
}

# WH, Wiley 1978
wiley.siteindex = function(age, height){
    if (age<=120){
        a = (height-4.5) * (0.1394 + 0.0137*age + 0.00007*age**2)
        b = age**2 - ((height-4.5) * (-1.7307-0.0616*age + 0.00192*age**2))
        si = 4.5 + 2500*(a/b)
        return(si)
    } else {
        print('Wiley site curve is not appropriate for trees >120 years of age.')
        return(NaN)
    }
}

wiley.height = function(age, siteindex){
    # Solve for height, subsituting subproblems with constants
    # http://www.quickmath.com/webMathematica3/quickmath/equations/solve/basic.jsp#c=solve_stepssolveequation&v1=s%3Dz%2Bq+*+(((h-z)*c)%2F(d-(h-z)*b))&v2=h
    q = 2500
    z = 4.5
    d = age**2.0
    b = -1.7307-0.0616*age+0.00192*d
    c = 0.1394 + 0.0137*age + 0.00007*d
    s = siteindex
    
    h = (z*d + b*z**2 - q*c*z - s*d - s*b*z)/(-s*b + z*b - q*c)
    
    return(h)
}