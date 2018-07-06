from flask import Flask, render_template, jsonify, request, send_file, session
import load_mossbauer
import os 
import csv 

app = Flask(__name__, static_url_path='/static') 
app.secret_key = 'appsecret'

@app.route("/") 
def index(): 
	group_folders = load_mossbauer.get_group_names()
	return render_template("index.html", data=group_folders)

@app.route("/group/<group_folder>")
def groupview(group_folder):
	group_folders = load_mossbauer.get_group_names()
	samples = load_mossbauer.get_samples_for_group(group_folder)
	return render_template('index.html',sampledata=samples, data=group_folders,group_folder=group_folder)

@app.route("/sample/<sample_name>")
def sampleview(sample_name):
	sample_list, name, group, dana_group, owner = load_mossbauer.get_sample(sample_name)
	return render_template('sample.html', sampledata=sample_list, name=name, group=group, dana_group=dana_group, owner=owner)

@app.route("/search/<query>")
def searchview(query):
	group, sample = load_mossbauer.searchResult(query)
	return render_template('search.html', query=query, group=group, sampleset=sample)

@app.route("/datafile/<cntno>")
def dataview(cntno):
	the_file = load_mossbauer.get_data_file(cntno)
	try:
		return send_file(the_file, as_attachment=True)
	except Exception as e:
		print(e)
		return

@app.route("/textfile/<cntno>")
def textview(cntno):
	the_file = load_mossbauer.get_text_file(cntno)
	try:
		return send_file(the_file, as_attachment=True)
	except Exception as e:
		print(e)
		return

@app.route("/plot/<sample_name>", methods=['GET'])  
def intensityPlotData(sample_name):
	plot_data = load_mossbauer.spectrum_plot_data(sample_name)
	return jsonify(plot_data)

@app.route("/getCompareList", methods=['GET'])  
def getCompareList():
	if 'bag' in session:
		sessionList = [load_mossbauer.get_sample_temperature(e.decode("utf-8")) for e in session['bag']]
		return jsonify(sessionList)
	return jsonify(None)

@app.route('/addToCompare', methods=['POST'])
def addToCompare():
	selectedSample = request.get_data();

	if 'bag' in session:
		tempbag = session['bag']
	else:
		session['bag'] = []
		tempbag = []

	if selectedSample in tempbag:
		tempbag.remove(selectedSample)
		session['bag'] = tempbag
		return 'removed'
	else:
		if len(tempbag) < 10:
			tempbag.append(selectedSample)
			session['bag'] = tempbag
			return 'added'

	return 'error';

@app.route('/removeFromCompare', methods=['POST'])
def removeFromCompare():
	selectedSample = request.get_data();

	if 'bag' in session:
		tempbag = session['bag']
	else:
		session['bag'] = []
		tempbag = []

	if selectedSample in tempbag:
		tempbag.remove(selectedSample)
		session['bag'] = tempbag
		return 'removed'
	else:
		return 'not found'

	return 'error';

@app.route('/clearCompareList', methods=['POST'])
def clearCompareList():
	session['bag'] = []
	return 'cleared';

if __name__ == '__main__': 
	app.run(host='0.0.0.0', port=51515, debug=False) 
