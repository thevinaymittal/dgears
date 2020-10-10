from flask import *
import io
import os
import time
import ast
import json
import pandas as pd
from io import StringIO

from Database.db import DBConnect

import sys
import numpy as np
import logging
from datetime import datetime
from flask_restplus import Api, Resource, reqparse
from flasgger import Swagger
import numpy as np
import pickle
import pandas as pd
import xgboost as xgb
from flask import Flask, abort, jsonify, request
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OrdinalEncoder

ml_model = pickle.load(open("Pickle_Rl_Model.pkl", "rb"))
ml_model_1 = pickle.load(open("Pickle_Ec_Model.pkl", "rb"))
ml_model_2 = pickle.load(open("Pickle_Sc_Model.pkl", "rb"))



application = Flask(__name__)

application.secret_key = "super secret key"
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

Swagger(application)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    application.logger.handlers = gunicorn_logger.handlers
    application.logger.setLevel(gunicorn_logger.level)


@application.route('/', methods=['GET'])
def index():
    return "Prediction API is good to go"


@application.route('/api/predict', methods=['POST'])
def getPredictedPrice():
    if request.method == 'POST':
        if request.form.get('miles'):
            #1
            try:
                miles = int(request.form['miles'])
            except:
                msg = {"'Invalid 'Miles' value, please try with any positive integer'":'Failed'}
                return msg, 500

            #2
            try:
                zip_code = int(request.form['zip_code'])
                #Condition to verify this from Truecar_ table
            except:
                msg = {"'Invalid 'Zip' value, please try with standard Zip Codes available in USA'":'Failed'}
                return msg, 500
            
            if request.form.get('VIN'):

                    try:
                        upc_product_code = int(request.form['VIN'])
                        #Condition (i.e. run function name_from_VIN) to verify this from scrapeData_ table upc_product_code column and then feed:
                        make,model,trim,year = db.name_from_VIN(upc_product_code)
                    except:
                        msg = {"'Invalid 'VIN' value, please try with standard VIN number'":'Failed'}
                        return msg, 500
            
            else:

                    #3
                    try:
                        make = (request.form['make'])
                        #Condition to verify this from scrapeData_ table 'make' column
                    except:
                        msg = {"'Invalid 'Make' value, Check case sensitive or please try with any standard Car Makers available in USA'":'Failed'}
                        return msg, 500

                    #4
                    try:
                        model = (request.form['model'])
                        #Condition to verify this from scrapeData_ table 'model' column
                    except:
                        msg = {"'Invalid 'Model' value, Check case sensitive or please try with the available Models under the Maker available in USA'":'Failed'}
                        return msg, 500
                    
                    #5
                    try:
                        trim = (request.form['trim'])
                        #Condition to verify this from scrapeData_ table 'trim' column
                    except:
                        msg = {"'Invalid 'Trim' value, Check case sensitive or please try with the available Trim/Variant under the Models available in USA'":'Failed'}
                        return msg, 500

                    #6
                    try:
                        year = int(request.form['year'])
                        #Condition to verify this from scrapeData_ table 'year' column
                    except:
                        msg = {"'Invalid 'Year' value, please try from 1997 till 2020'":'Failed'}
                        return msg, 500



            try:
                dbConnect = DBConnect()
                
                # msg = db.loadPickle(inputs)
                msg = {"Inputs and connection working fine":"PASSED :)"}
                
                input_data=[[make,model,trim,year,int(miles),zip_code]]
                print('good')
                df=pd.DataFrame(input_data)
                df[[0,1,2]]=ml_model_1.transform(df[[0,1,2]])
                feed_data=ml_model_2.transform(df)
                print('better')
                u_pred=ml_model.predict(feed_data)
                u_list=u_pred.tolist()
                print('best')
                prediction=float(u_list[0])
                
                return {'Price Predicted':str(prediction)}
                

            except:
                msg = {'something is wrong in connection'}
                return msg, 500
        else:
            pass
    else:
        pass


if __name__ == '__main__':
    # application.run(debug=True,port=80,host='0.0.0.0')
    application.run(debug=True)
