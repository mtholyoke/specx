from flask import Flask, render_template, jsonify, request, send_file, session
from pathlib import Path
import csv
import load_mossbauer
import os
import yaml

app = Flask(__name__, static_url_path='/static')

config = {
    'host': '0.0.0.0',
    'port': '51515',
    'secret_key': 'Nautilus',
    'debug': False,
}
config_name = os.path.join(Path(__file__).parent, 'config.yml')
try:
    config_file = open('config.yml')
    config_yaml = yaml.safe_load(config_file)
    for key in config.keys():
        if key in config_yaml.keys():
            config[key] = config_yaml[key]
    config_file.close()
except IOError:
    # TODO: replace with logging
    print(f'Can’t read {config_name}; using defaults')

app.secret_key = config['secret_key']


@app.route("/")
def index():
    group_folders = load_mossbauer.get_group_names()
    return render_template("index.html", data=group_folders)


@app.route("/group/<group_folder>", methods=['GET'])
def groupview(group_folder):
    group_folders = load_mossbauer.get_group_names()
    samples, decoded_group_folder = load_mossbauer.get_samples_for_group(group_folder)
    return render_template(
        'index.html',
        sampledata=samples,
        data=group_folders,
        group_folder=decoded_group_folder
    )


@app.route('/sample/<sample_name>', methods=['GET'])
def get_sample_view(sample_name):
    sample_list, name, group, dana_group, owner, pubs = load_mossbauer.get_sample(sample_name)
    return render_template(
        'sample.html',
        sampledata=sample_list,
        name=name,
        group=group,
        dana_group=dana_group,
        owner=owner,
        pubs=pubs
    )


@app.route("/search/<query>")
def searchview(query):
    group, sample = load_mossbauer.searchResult(query)
    return render_template(
        'search.html',
        query=query,
        group=group,
        sampleset=sample
    )


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


@app.route("/badfiles/", methods=["GET"])
def getBadFiles():
    ls_not_book, ls_not_in_server = load_mossbauer.list_badfiles()
    return render_template(
        'badfiles.html',
        notbook=ls_not_book,
        notserver=ls_not_in_server,
        notbookcount=len(ls_not_book),
        notservercount=len(ls_not_in_server)
    )


@app.route("/getCompareList", methods=['GET'])
def getCompareList():
    if 'bag' in session:
        sessionList = [load_mossbauer.get_sample_temperature(e.decode("utf-8")) for e in session['bag']]
        return jsonify(sessionList)
    return jsonify(None)


@app.route('/addToCompare', methods=['POST'])
def addToCompare():
    selectedSample = request.get_data()

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

    return 'error'


@app.route('/removeFromCompare', methods=['POST'])
def removeFromCompare():
    selectedSample = request.get_data()

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

    return 'error'


@app.route('/clearCompareList', methods=['POST'])
def clearCompareList():
    session['bag'] = []
    return 'cleared'


if __name__ == '__main__':
    app.run(
        host=config['host'],
        port=config['port'],
        debug=config['debug']
    )
