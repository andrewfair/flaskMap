from flask import render_template, Response, request, session
from app import app
import json
import pandas as pd
import numpy as np
# from flask_wtf import FlaskForm
# from flask.ext.wtf import Form
# from wtforms import Form, RadioField, SelectField
from .forms import SimpleForm

# SECRET_KEY = 'development'
# session.clear()

# load data
df = pd.read_csv('app/static/data/DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv')
dfXwalk = pd.read_csv('app/static/data/national_county.txt', header=None)
xwalk2 = pd.read_csv('app/static/data/State SSA codes_GDIT_05182017.txt', skiprows=2, header=None)
countyXwalk = pd.read_csv('../flaskMap/app/static/data/ssa_fips_state_county2011.csv', 
                          dtype={'ssacounty': object, 'fipscounty': object, 'ssastate': object, 'fipsstate': object})
countyXwalk = countyXwalk.iloc[1:,:]
with open('app/static/data/us-states.json') as json_data:
	stateGeojson = json.load(json_data)['features']
with open('../flaskMap/app/static/data/counties.json') as json_data:
	countyGeojson = json.load(json_data)

dens = df.groupby(['SP_STATE_CODE']).size().reset_index(name='den')
dens2 = df.groupby(['SP_STATE_CODE', 'BENE_COUNTY_CD']).size().reset_index(name='den')

# setup crosswalks
dfXwalk.columns = ['STATE', 'STATEFP', 'COUNTYFP', 'COUNTYNAME', 'CLASSFP']
dfXwalkUniques = dfXwalk[['STATE', 'STATEFP']].drop_duplicates()
dfXwalkUniques['STATEFP'] = dfXwalkUniques['STATEFP'].apply('{:0>2}'.format)
xwalk2['SSA_code'], xwalk2['state'] = xwalk2[0].str.strip().str.split(' = ',1).str
xwalk2 = xwalk2[['SSA_code', 'state']]

# condition = 'SP_DEPRESSN'
# condition = 'SP_COPD'

# class SimpleForm(Form):
# 	myCondition = SelectField('Label', choices=[('SP_DEPRESSN','depression'),('SP_COPD','COPD')])

@app.route('/', methods=["POST", "GET"])
def index():
	condition = ['SP_ALZHDMTA']

	form = SimpleForm(request.form)
	if form.validate():
		print(form.myCondition.data)
		condition = form.myCondition.data
	else:
		print(form.errors)
	session['condition'] = condition

	return render_template("index.html", form=form, condition=condition)

@app.route('/getMyJson')
def getMyJson():
	# with open('app/static/data/stateData.json') as json_data:
	# 	d = json.load(json_data)
	conditions = session.get('condition', None)
	# condition = session['condition']
	# print(condition, 'sessGet')
	geojson = stateGeojson

	mask = np.logical_and.reduce([(df[cond] == 1) for cond in conditions])
	subDf = df[mask]
	nums = subDf.groupby(['SP_STATE_CODE']).size().reset_index(name='num')
	# nums = df[df[condition]==1].groupby(['SP_STATE_CODE']).size().reset_index(name='num')
	stateData = pd.merge(dens, nums, on='SP_STATE_CODE', how='outer')
	stateData['SSA_code'] = stateData['SP_STATE_CODE'].apply('{:0>2}'.format)
	stateMerge1 = pd.merge(stateData, xwalk2, on='SSA_code')


	for i in geojson:
		stateName = i['properties']['name']
		row = stateMerge1[stateMerge1['state']==stateName].max()
		if not pd.isnull(row['den']):
			i['properties']['den'] = row['den']
		else:
			i['properties']['den'] = 0
		if not pd.isnull(row['num']):
			i['properties']['num'] = row['num']
			i['properties']['rate'] = row['num'] / row['den']
		else:
			i['properties']['num'] = 0
			i['properties']['rate'] = 0

	sd = json.dumps(geojson)

	# json = dataFrame.to_json(orient='records', date_format='iso')
	response = Response(response=sd, status=200, mimetype="application/json")
	return(response)

@app.route('/countyJson')
def countyJson():
	conditions = session.get('condition', None)


	# with open('../flaskMap/app/static/data/counties.json') as json_data:
	# 	countyGeojson = json.load(json_data)
	geojson = countyGeojson

	conditions = session.get('condition', None)
	mask = np.logical_and.reduce([(df[cond] == 1) for cond in conditions])
	subDf = df[mask]
	nums2 = subDf.groupby(['SP_STATE_CODE', 'BENE_COUNTY_CD']).size().reset_index(name='num')
	countyData = pd.merge(dens2, nums2, on=['SP_STATE_CODE', 'BENE_COUNTY_CD'], how='outer')
	countyData['SP_STATE_CODE'] = countyData['SP_STATE_CODE'].apply('{:0>2}'.format)
	countyData['BENE_COUNTY_CD'] = countyData['BENE_COUNTY_CD'].apply('{:0>3}'.format)
	countyData['fullCode'] = countyData['SP_STATE_CODE'].map(str) + countyData['BENE_COUNTY_CD'].map(str)
	countyMerge1 = pd.merge(countyData, countyXwalk, left_on='fullCode', right_on='ssacounty')
	countyMerge1 = countyMerge1[pd.notnull(countyMerge1['SP_STATE_CODE'])]

	for i in geojson['features']:
		code = i['properties']['GEO_ID'][-5:]
		row = countyMerge1[countyMerge1['fipscounty']==code].max()
		print(row)
		if not pd.isnull(row['den']):
			i['properties']['den'] = row['den']
			i['properties']['stateName'] = row['state']
			i['properties']['countyName'] = row['county']
		else:
			i['properties']['den'] = 0
			i['properties']['stateName'] = 'undefined'
			i['properties']['countyName'] = 'undefined'
		if not pd.isnull(row['num']):
			i['properties']['num'] = row['num']
			i['properties']['rate'] = row['num'] / row['den']
		else:
			i['properties']['num'] = 0
			i['properties']['rate'] = 0

	sd = json.dumps(geojson)

	# json = dataFrame.to_json(orient='records', date_format='iso')
	response = Response(response=sd, status=200, mimetype="application/json")
	return(response)


@app.route('/counties', methods=["POST", "GET"])
def counties():
	condition = ['SP_ALZHDMTA']

	form = SimpleForm(request.form)
	if form.validate():
		print(form.myCondition.data)
		condition = form.myCondition.data
	else:
		print(form.errors)
	session['condition'] = condition

	return render_template("counties.html", form=form, condition=condition)