#!/usr/bin/python

import argparse
import pycurl
import re
import csv
from StringIO import StringIO
from urllib import urlencode
from sys import exit

# Arguments handling
parser = argparse.ArgumentParser(description="Check timeouted OAB registers from input file")

parser.add_argument("input_file", type=str,
                    help="NOK input file")

args = parser.parse_args()
input_filename = args.input_file

# Setting output filenames
filename_ok = "checked_ok_"+input_filename
filename_nok = "checked_nok_"+input_filename

# Variable definitions
url = 'https://www2.oabsp.org.br/asp/consultaInscritos/consulta_nr_advogado.asp'
referer = 'https://www2.oabsp.org.br/asp/consultaInscritos/consulta01.asp'
no_results = 'N&atilde;o h&aacute; resultados que satisfa&ccedil;am a busca'

# Building the pyCurl request
c = pycurl.Curl()
c.setopt(pycurl.SSL_VERIFYPEER, 0)
c.setopt(pycurl.SSL_VERIFYHOST, 0)
c.setopt(pycurl.SSLVERSION, 3)
c.setopt(pycurl.CONNECTTIMEOUT, 3)
c.setopt(pycurl.TIMEOUT, 3)
c.setopt(pycurl.URL, url)
c.setopt(pycurl.REFERER, referer)
c.setopt(pycurl.HTTPHEADER, ['Connection: keep-alive'])

# Iterating through oab_codes
with open(input_filename, "r") as input_file:
    for line in input_file:
        if line.strip('\n').split(',')[1] == "timeout":
        	oab_code = line.strip('\n').split(',')[0]
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
