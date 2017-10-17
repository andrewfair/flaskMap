from wtforms import Form, RadioField, SelectField, SelectMultipleField

conditionChoices = [('SP_ALZHDMTA', 'Alzheimers'),
	('SP_CHF','Heart Failure'),
	('SP_CHRNKIDN','Chronic Kidney Disease'),
	('SP_CNCR','Cancer'),
	('SP_COPD','Chronic Obstructive Pulmonary Disease'),
	('SP_DEPRESSN','Depression'),
	('SP_DIABETES','Diabetes'),
	('SP_ISCHMCHT','Ischemic Heart Disease'),
	('SP_OSTEOPRS','Osteoporosis'),
	('SP_RA_OA','Rheumatoid Arthritis'),
	('SP_STRKETIA','Stroke')
]

class SimpleForm(Form):
	# myCondition = SelectField('Label', choices=conditionChoices, default='SP_DIABETES')
	myCondition = SelectMultipleField('Label', choices=conditionChoices, default='SP_ALZHDMTA')
