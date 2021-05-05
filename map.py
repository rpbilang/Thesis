#!/usr/bin/env python
from netCDF4 import Dataset as nc
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import cartopy.crs as crs
from cartopy.io.shapereader import Reader
from cartopy.feature import NaturalEarthFeature
from cartopy.feature import ShapelyFeature
from glob import glob
from wrf import (getvar, interplevel, to_np, latlon_coords, get_cartopy,
                 cartopy_xlim, cartopy_ylim,ALL_TIMES)

#Listing the directory and sorting of files
wrfdir= sorted(glob("wrfout*"))
ncfiles = [nc(x) for x in wrfdir]

# Extract the pressure, geopotential height, and wind variables
ht = getvar(ncfiles, "height_agl", timeidx=ALL_TIMES,units="m")[:,0:10,:]
ua = getvar(ncfiles, "uvmet",timeidx=ALL_TIMES,method="cat",units="m s-1")[0,:,0:10]
va = getvar(ncfiles, "uvmet",timeidx=ALL_TIMES,method="cat", units="m s-1")[1,:,0:10]
wspd = getvar(ncfiles, "uvmet_wspd_wdir",timeidx=ALL_TIMES,method="cat", units="m s-1",meta=True)[0,:,0:10]

# Interpolate geopotential height, u, and v winds to 60 hPa
levels = np.asarray([100])
u_60 = interplevel(ua, ht, levels)
v_60 = interplevel(va, ht, levels)
wspd_60 = interplevel(wspd, ht, levels)

#get the mean 
uam = u_60.groupby('Time.month').mean('Time')
vam = v_60.groupby('Time.month').mean('Time')
wspdm = wspd_60.groupby('Time.month').mean('Time')
wspdmf = wspdm.squeeze('month')
uamf = uam.squeeze('month')
vamf = vam.squeeze('month')

#get the latlon coordinates
lats,lons = latlon_coords(wspdmf) 
cart_proj = get_cartopy(wspd)

# Create the figure
fig = plt.figure(figsize=(12,9))
ax = plt.axes(projection=cart_proj)

# Download and add the states and coastlines
fname = 'Rizal.shp'
fname1 = 'gadm36_PHL_2.shp'

shape_feature = ShapelyFeature(Reader(fname).geometries(), crs.PlateCarree(),
			       facecolor='none')
shape_feature1 = ShapelyFeature(Reader(fname1).geometries(), crs.PlateCarree(),
			       facecolor='none')
ax.add_feature(shape_feature1, linewidth=1, edgecolor="black")

# Add the wind speed contours
levels = np.linspace(1,15,15,dtype=float)
cmap = LinearSegmentedColormap.from_list('name',['blue',
		       "aqua","lime","lawngreen","yellow","gold","orange","tomato","red"])
wspd_contours = plt.contourf(to_np(lons), to_np(lats), to_np(wspdmf),
                             levels=levels,
                             cmap=cmap,
                             transform=crs.PlateCarree(),alpha=0.9,extend='both')
#plt.colorbar(wspd_contours, ax=ax, orientation="vertical", pad=.05)


# Add the 60 hPa wind barbs, only plotting every 40th data point.
q = plt.quiver(to_np(lons[::4,::4]), to_np(lats[::4,::4]),
          to_np(uamf[::4, ::4]), to_np(vamf[::4, ::4]),width=0.0020,
          transform=crs.PlateCarree())
ax.quiverkey(q,0.1,-0.02,3,'5 ms-1',labelpos='W')


#streamplot
#plt.streamplot(to_np(lons),to_np(lats),to_np(uamf),to_np(vamf),density=0.6,color='k')

# Set the map bounds
ax.set_xlim(cartopy_xlim(wspd_60))
ax.set_ylim(cartopy_ylim(wspd_60))

#ax.gridlines()

plt.title("60 MB Height (dm), Wind Speed (m/s)")

plt.show()
