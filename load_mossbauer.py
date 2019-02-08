from objects import mossbauer_sample as m
from objects import mossbauer_sample_set as mset
from cacheout import Cache
import urllib.parse
import numpy as np
import xlrd
import os.path
import csv
import re
import os.path, time
from datetime import datetime
cache = Cache()

#SPECTRA_PATH = 'A:/UMass Projects/Superman - Mats/Spectrum Explorer/spectra/';
SPECTRA_PATH = '/srv/nfs/common/spectra/';

def to_digit(text):
    return int(text) if text.isdigit() else text

def load_data():
	mossbauer_sample_list = cache.get('moss_sample_list')
	if mossbauer_sample_list is not None:
		return mossbauer_sample_list
	else:
		mossbauer_sample_list = []
		file = SPECTRA_PATH + 'Mossbauer/MHC/mlogbook.xlsx'
		offset = 1;
		workbook = xlrd.open_workbook(file)
		worksheet = workbook.sheet_by_index(0)

		rows = []
		for i, row in enumerate(range(worksheet.nrows)):
		    if i <= offset:  # (Optionally) skip headers
		        continue
		    r = []
		    for j, col in enumerate(range(worksheet.ncols)):
		        r.append(worksheet.cell_value(i, j))
		    rows.append(r)

		for row in rows:
			sample = m.mossbauer_sample()
			sample.sample_no = str(row[0]).replace('.0','')
			sample.temperature = to_digit(str(row[1]).replace('.0','')) 
			sample.sample_name = row[2]
			sample.weight = row[3]
			sample.is_post = row[4]
			sample.dana_group = row[5]
			sample.group_folder = row[6]
			sample.perc_Comp = row[7]
			sample.owner = row[9]
			sample.pubs = row[10]			
			sample.multitemp = row[11]
			sample.datafile_display_link = '/datafile/'+sample.sample_no
			sample.textfile_display_link = '/textfile/'+sample.sample_no
			sample.sampleurl = SPECTRA_PATH + 'Mossbauer/MHC/original/' + sample.sample_no + '.cnt'
			try:
				sample.sampletakentime = datetime.strftime(datetime.strptime(sample.sample_no[:6], '%y%m%d'),'%b %d, %Y')
			except ValueError:
				sample.sampletakentime = 'TBD'
			sample.last_modified_time = "No File"
			if os.path.exists(sample.sampleurl):
				sample.last_modified_time = time.ctime(os.path.getmtime(sample.sampleurl))


			mossbauer_sample_list.append(sample)
		cache.set('moss_sample_list',mossbauer_sample_list,10000)
	return mossbauer_sample_list

def get_data_file(cnt_no):
	return SPECTRA_PATH + 'Mossbauer/MHC/original/' + cnt_no + '.cnt'

def get_text_file(cnt_no):
	return SPECTRA_PATH + 'Mossbauer/MHC/original/' + cnt_no + '.txt'

def get_group_names():
	moss_list = load_data()
	seen = set()
	unique = [mbs.group_folder for mbs in moss_list if mbs.group_folder not in seen and not seen.add(mbs.group_folder)]
	unique.sort()
	group_list = []
	for g in unique:
		group_list.append({'groupname':g, 'groupurl': urllib.parse.quote_plus(g, safe='')})
	return group_list

def get_samples_for_group(group_folder):
	decoded_group_folder = urllib.parse.unquote_plus(group_folder)
	moss_list = load_data()
	seen = set()
	samples = [mbs for mbs in moss_list if mbs.group_folder.lower() == decoded_group_folder.lower() and mbs.sample_name not in seen and not seen.add(mbs.sample_name) and mbs.is_post == 'Y']
	samples.sort(key=lambda x: x.sample_name, reverse=False)
	samples_set = []
	for s in samples:
		sampleset = mset.mossbauer_sample_set()
		sampleset.sample_name = s.sample_name
		sampleset.dana_group = s.dana_group
		sampleset.group_folder = s.group_folder
		sampleset.weight = s.weight
		sampleset.is_post = s.is_post
		sampleset.perc_Comp = s.perc_Comp
		sampleset.owner = s.owner
		sampleset.temp_class = 'bolden' if s.multitemp == 'Y' else 'unbolden'

		samples_set.append(sampleset)
	return samples_set, decoded_group_folder

def get_sample(sample_name):
	decoded_sample = sample_name
	moss_list = load_data()
	sample_list = [mbs for mbs in moss_list if mbs.sample_name.lower() == decoded_sample.lower()]
	sample_list.sort(key=lambda x: x.temperature, reverse=False)
	name = sample_list[0].sample_name
	group = sample_list[0].group_folder
	dana_group = sample_list[0].dana_group
	owner = sample_list[0].owner
	pubs = sample_list[0].pubs
	return sample_list, name, group, dana_group,owner, pubs

def get_sample_temperature(sample_no):
	moss_list = load_data()
	sample_temperature = [s for s in moss_list if s.sample_no.lower() == sample_no.lower()]
	name = sample_temperature[0].sample_name
	temperature = sample_temperature[0].temperature
	plot_data = get_sample_plot_data(sample_temperature[0])
	return {'sample_no':sample_no, 'sample_name':name, 'temperature':temperature, 'plot':plot_data}

def spectrum_plot_data(sample_name):
	decoded_sample = sample_name
	moss_list = load_data()
	sample_list = [mbs for mbs in moss_list if mbs.sample_name.lower() == decoded_sample.lower()]
	sample_list.sort(key=lambda x: x.temperature, reverse=False)
	sample_set_plot = [];
	for sample in sample_list:
		plot_data = get_sample_plot_data(sample)
		sample_set_plot.append({'sample_no':sample.sample_no, 'plot': plot_data, 'temperature':sample.temperature, 'sample_name':decoded_sample})

	return sample_set_plot

def get_sample_plot_data(sample):
	file = sample.sampleurl
	intensity_list = []
	plot_data = []
	midpoint = 0
	gradient = 0

	# SOme files are not found and this affects all the other samples in sample set
	if not os.path.exists(file):
		return []

	with open(file,'r') as tsvin:
	    tsvin = csv.reader(tsvin, delimiter='\t')

	    for i,row in enumerate(tsvin):
	    	for col in row:
	    		if i == 9:
	    			listvals = col.split(' ')
	    			midpoint = float(listvals[2])
	    			gradient = float(listvals[4])
	    		
	    		if i > 9:
	    			intensity_list.append(float(col.strip()))

	max_spec_intensity = max(intensity_list)
	for i, channel_intensity in enumerate(intensity_list):
		channel = i+1
		x_val = (channel - midpoint)*gradient
		y_val = 1-(channel_intensity/max_spec_intensity)
		plot_data.append({'x':x_val, 'y':y_val})
	
	return plot_data

def searchResult(query):
	#Only on sample name and group folder
	moss_list = load_data()
	seen = set()
	search = []
	group = [mbs.group_folder for mbs in moss_list if query.lower() in mbs.group_folder.lower() and mbs.group_folder not in seen and not seen.add(mbs.group_folder) ]
	group.sort()

	sample_seen = set()
	samples = [mbs for mbs in moss_list if mbs.sample_name not in sample_seen and not sample_seen.add(mbs.sample_name) and mbs.is_post == 'Y' and query.lower() in mbs.sample_name.lower()]
	samples.sort(key=lambda x: x.sample_name, reverse=False)
	samples_set = []
	for s in samples:
		sampleset = mset.mossbauer_sample_set()
		sampleset.sample_name = s.sample_name
		sampleset.dana_group = s.dana_group
		sampleset.group_folder = s.group_folder
		sampleset.weight = s.weight
		sampleset.is_post = s.is_post
		sampleset.perc_Comp = s.perc_Comp
		sampleset.owner = s.owner
		sampleset.url = urllib.parse.quote_plus(s.sample_name)        
		sampleset.temp_class = 'bolden' if s.multitemp == 'Y' else 'unbolden'

		samples_set.append(sampleset)

	return group,samples_set