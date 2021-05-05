#!/usr/bin/env python
from __future__ import print_function
from netCDF4 import Dataset as nc
import numpy as np
from wrf import (getvar, interplevel, latlon_coords, get_cartopy,
                 cartopy_xlim, cartopy_ylim)
import cartopy.crs as crs
from cartopy.io.shapereader import Reader
from cartopy.feature import NaturalEarthFeature
from cartopy.feature import ShapelyFeature
from glob import glob
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import datetime

#Listing the directory and sorting of files
wrfdir= sorted(glob("winds*"))
ncfiles = [nc(x) for x in wrfdir]
ter = getvar(ncfiles,'ter',units='m')


for i in range(len(ncfiles)):


	ht = getvar(ncfiles, "height_agl", timeidx=i,units="m")[:,:,:]
	ua = getvar(ncfiles, "uvmet",timeidx=i,method="cat",units="m s-1")[0,:,:]
	va = getvar(ncfiles, "uvmet",timeidx=i,method="cat", units="m s-1")[1,:,:]
	wspd = getvar(ncfiles, "uvmet_wspd_wdir",timeidx=i,method="cat", units="m s-1",meta=True)[0,:,:]


	# Interpolate geopotential height, u, and v winds to 60 hPa
	levels = np.asarray([100])
	u_60 = interplevel(ua, ht, levels)
	v_60 = interplevel(va, ht, levels)
	wspd_60 = interplevel(wspd, ht, levels)

	#get the latlon coordinates
	lats,lons = latlon_coords(wspd_60) 
	cart_proj = get_cartopy(wspd_60)

	# Create the figure
	fig = plt.figure(figsize=(20,17))
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
	levels = np.linspace(np.min(ter),2000,50,dtype=float)
	#cmap = LinearSegmentedColormap.from_list('name',['blue',
	#	       "aqua","lime","lawngreen","yellow","gold","orange","tomato","red"])
	cmap = plt.get_cmap('terrain')
	wspd_contours = plt.contourf(to_np(lons), to_np(lats), to_np(ter),
                             	levels=levels,
                             	cmap=cmap,
                             	transform=crs.PlateCarree(),alpha=0.8,extend='both')
	#plt.colorbar(wspd_contours, ax=ax, orientation="vertical", pad=.05)


	# Add the 60 hPa wind barbs, only plotting every 40th data point.
	q = plt.quiver(to_np(lons[::2,::2]), to_np(lats[::2,::2]),
         	 to_np(u_60[::2, ::2]), to_np(v_60[::2, ::2]),width=0.0015,
          	transform=crs.PlateCarree())
	ax.quiverkey(q,0.1,-0.045,5,'5 ms-1',labelpos='W')


	# Set the map bounds
	ax.set_xlim(cartopy_xlim(wspd_60))
	ax.set_ylim(cartopy_ylim(wspd_60))
	
	xtime = getvar(ncfiles,"times",timeidx=i,meta=False)
	xtime = datetime.datetime.fromtimestamp(xtime.astype('O')/1e9)
	
	fig.text(.5, 0.48, xtime,ha='center')
	plt.subplots_adjust(bottom=0.5)
	
	plt.savefig(str(xtime.month)+str(xtime.day)+str(xtime.hour) + ".png",bbox_inches='tight',dpi=200)

