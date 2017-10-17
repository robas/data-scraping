#!/usr/bin/python

import argparse
import pycurl
import re
import csv
from StringIO import StringIO
from urllib import urlencode
from sys import exit

# Arguments handling
parser = argparse.ArgumentParser(description="Retrieve OAB registers from initial_oab to final_oab")

parser.add_argument("initial_oab", type=int,
                    help="Initial OAB code")
parser.add_argument("final_oab", type=int,
                    help="Final OAB code")

args = parser.parse_args()
initial_oab = args.initial_oab
final_oab = args.final_oab

# Checking arguments validity
if initial_oab < 10001:
    exit('initial_oab must be > 1000')
elif initial_oab >= final_oab:
    exit('final_oab must be > initial_oab')

# Setting output filenames
filename_ok = str(args.initial_oab)+"-"+str(args.final_oab)+".csv"
filename_nok = str(args.initial_oab)+"-"+str(args.final_oab)+"_nok.csv"

# Variable definitions
url = 'https://www2.oabsp.org.br/asp/consultaInscritos/consulta_nr_advogado.asp'
referer = 'https://www2.oabsp.org.br/asp/consultaInscritos/consulta01.asp'
no_results = 'N&atilde;o h&aacute; resultados que satisfa&ccedil;am a busca'

# Building the pyCurl request
c = pycurl.Curl()
c.setopt(pycurl.SSL_VERIFYPEER, 0)
c.setopt(pycurl.SSL_VERIFYHOST, 0)
c.setopt(pycurl.SSLVERSION, 3)
c.setopt(pycurl.CONNECTTIMEOUT, 10)
c.setopt(pycurl.TIMEOUT, 10)
c.setopt(pycurl.URL, url)
c.setopt(pycurl.REFERER, referer)
c.setopt(pycurl.HTTPHEADER, ['Connection: keep-alive'])

# Iterating through oab_codes
for oab_code in range(initial_oab,final_oab+1):
    post_data = {'pagina': 0,
                'tipo_consulta' : 1,
                'nr_inscricao' : oab_code,
                'cbxadv' : 1,
                'id_tipoinscricao': 1,
                'parte_nome' : 1,
                'idCidade' : 0
                }
    post_fields = urlencode(post_data)
    # print(post_fields)

    c.setopt(c.POSTFIELDS, post_fields)
    try:
        buffer = StringIO()
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        response = buffer.getvalue()

        if(no_results in response):
            with open(filename_nok, "a") as output_nok:
                output_nok.write(str(oab_code)+",notfound\n")
                print str(oab_code)+',notfound'
        else: 
            token=response.split('<li><span>')
            name=token[1].replace("</span></li>","")
            oab_code_state=re.sub('.* - ', '', token[2]).replace('</li>','')
            date=re.sub('.*</span>','',token[3]).replace('</li>','')
            subsection=re.sub('.*</span>','',token[4]).replace('</li>','')
            status=re.sub('</li>.*','',re.sub('.*</span>','',token[5]))
            
            fields=[str(oab_code),name,status,oab_code_state,subsection,date]

            with open(filename_ok, "a") as output_ok:
                writer = csv.writer(output_ok)
                writer.writerow(fields)
                print fields
    except:
        with open(filename_nok, "a") as output_nok:
                output_nok.write(str(oab_code)+",timeout\n")
                print str(oab_code) + ',timeout'

c.close()