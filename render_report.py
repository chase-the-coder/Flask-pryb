from flask import Flask, render_template, make_response, request, jsonify
import pandas as pd
import json
import pdfkit
import os
import csv
import requests
from hdfs import InsecureClient
import io
import PyPDF2

app = Flask(__name__)
path_wkhtmltopdf = r'/usr/local/bin/wkhtmltopdf'
save_path = r'/Users/chase/Downloads'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
options = {
    'dpi': 400,
    'page-size': 'A4',
    'margin-top': '0.0in',
    'margin-right': '0.0in',
    'margin-bottom': '0.0in',
    'margin-left': '0.0in',
    'encoding': "UTF-8",
    'custom-header': [('Accept-Encoding', 'gzip')],
    'no-outline': None,
}
# data = pd.read_excel(r"C:\Users\alexb\Desktop\cp_v24.xlsx")
# data.columns = map(str.lower, data.columns)

blank_project = {
    'project_contact': {
        'cip_publishing_entity': {
            0: ''
        },
        'state': {
            0: ''
        },
        'country': {
            0: ''
        },
        'city': {
            0: ''
        }
    },
    'project_fundamentals': {
        'contracting_department': {
            0: ''
        },
        'project_number': {
            0: ''
        },
        'project_description': {
            0: ''
        },
        'cip_spend_year': {
            0: ''
        },
        'total_project_value': {
            0: ''
        }
    },
    'project_name': {
        'project_name': {
            0: 'No Project Found with Project Number requested'
        }
    },
    'division': {
        'market_sector': {
            0: ''
        },
        'category_of_work': {
            0: ''
        },
        'type_of_project': {
            0: ''
        },
        'specialty': {
            0: ''
        }
    }
}

#report_dict = dict()
#url = 'http://clientgateway.fraxses.com/api/gateway'
#headers = {"content-type":"application/json"}
#payload =  {
#          "token": "9098A7DD-E2B4-46C5-9CA0-8A3E0647FBA7",
#          "action": "dop_qry",
#          "parameters": {
#            "hed_cde": "cp_report_headers_Base",
#            "whr": "",
#            "odr": "",
#            "pge": "0",
#            "pge_sze": "0"
#          }
#        }
#response = requests.post(url=url, headers=headers, data=json.dumps(payload)).content
#report_headers = pd.DataFrame.from_dict(json.loads(response)['result'][0]['serviceresult']['response']['records'])
#for i in report_headers['report_category'].unique():
#    print(i)
#    report_dict[i] = [x for x in report_headers.loc[report_headers['report_category'] == i]['db_column_v6'].values.tolist() if x not in [None,'country']]
#
report_dict = {
    'project_contact': ['cip_publishing_entity', 'state', 'city'],
    'project_fundamentals': [
        'contracting_department', 'project_number', 'cp_unique_project_id',
        'project_description', 'cip_fy', 'total_project_value'
    ],
    'project_name': ['project_name'],
    'division': [
        'market_sector', 'project_stage', 'construction_type',
        'land_acquisition'
    ]
}  #,


def buildReport(primary_key):
    return blank_project


@app.route('/project/<primary_key>')
def pdf_template(primary_key):
    db_dict = buildReport(primary_key)
    print(db_dict)
    # print(render_template('template.html', db_dict=db_dict))
    rendered = render_template('template.html', db_dict=db_dict)
    css = [
        'bootstrap-3.4.1-dist/bootstrap-3.4.1-dist/css/style.css',
        'bootstrap-3.4.1-dist/bootstrap-3.4.1-dist/css/bootstrap.css'
    ]
    pdf = pdfkit.from_string(rendered,
                             False,
                             css=css,
                             configuration=config,
                             options=options)
    pdfReader = io.BytesIO(pdf)
    pdfReader = PyPDF2.PdfFileReader(pdfReader)
    pdfWriter = PyPDF2.PdfFileWriter()
    for page in range(pdfReader.numPages):
        pageObj = pdfReader.getPage(page)
        pdfWriter.addPage(pageObj)
    with open(os.path.join(save_path, primary_key + '.pdf'), 'wb') as f:
        pdfWriter.write(f)
    #response = make_response(pdf)
    #response.headers['Content-Type'] = 'application/pdf'
    #response.headers['Content-Disposition'] = 'attachment; filename=' + primary_key + '.pdf'
    #return response
    return {'success': 'true'}


@app.route('/savehdfs/<primary_key>', methods=['POST', 'GET'])
def savehdfs(primary_key):
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            db_dict = buildReport(primary_key)
            # {'hdfs': {'hdfsUrl': 'http://192.168.30.124:50070', 'targetHDFSfile': '/CCP/test.pdf'}, 'template': 'template.html'}
            rendered = render_template(data['template'],
                                       primary_key=primary_key,
                                       db_dict=db_dict)
            css = [
                'bootstrap-3.4.1-dist/bootstrap-3.4.1-dist/css/style.css',
                'bootstrap-3.4.1-dist/bootstrap-3.4.1-dist/css/bootstrap.css'
            ]
            pdf = pdfkit.from_string(rendered,
                                     False,
                                     css=css,
                                     configuration=config,
                                     options=options)
            # HDFS
            #hdfsUrl = data['hdfs']['hdfsUrl']
            #hdfsClient = InsecureClient(hdfsUrl)
            #targetFile = data['hdfs']['targetHDFSfile']
            # create pdf objects from bytes
            pdfReader = io.BytesIO(pdf)
            pdfReader = PyPDF2.PdfFileReader(pdfReader)
            pdfWriter = PyPDF2.PdfFileWriter()
            for page in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(page)
                pdfWriter.addPage(pageObj)
            #with hdfsClient.write(targetFile, overwrite=True) as writer:
            #    pdfWriter.write(writer)
            #with open(primary_key + '.pdf', 'wb') as f:
            #    f.write(response.content)
            return json.dumps({'success': 'pdf written to'})
        except requests.exceptions.ConnectionError:
            return json.dumps(
                {'error': 'make sure service container is connected to VPN'})
    else:
        return 'GET: Successful'


if __name__ == '__main__':
    app.run(debug=True)
