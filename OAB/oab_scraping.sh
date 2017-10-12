#!/bin/bash

# The first OAB code is 10001
FIRST_OAB=10001

if [ $# -lt 2 ]; then
    printf 'usage: %s [nro_oab] [quantidade]\n' "$(basename "$0")" >&2
    exit 64
fi

# Check if the provided OAB code is valid
if [ $1 -lt $FIRST_OAB ]; then
    printf 'O código OAB deve ser maior que 10000'
    exit 1
fi

initial_oab=$1
qtd=$2

echo "Scraping data from https://www2.oabsp.org.br/asp/consultaInscritos/consulta01.asp" $oab
echo

for oab_number in `seq $initial_oab $(($initial_oab + $qtd))`;do

    curl_output=`curl 'https://www2.oabsp.org.br/asp/consultaInscritos/consulta_nr_advogado.asp' -s -H 'Referer: https://www2.oabsp.org.br/asp/consultaInscritos/consulta01.asp' -H 'Connection: keep-alive' --data 'pagina=0&tipo_consulta=1&nr_inscricao='$oab_number'&cbxadv=1&id_tipoinscricao=1&nome_advogado=&parte_nome=1&nr_cpf=&idCidade=0' --compressed | tail -n 1`
    
    name=`echo $curl_output | awk 'BEGIN { FS="<li><span>" } { gsub("</span></li>","",$2); print $2}'`
    oab=`echo $curl_output | awk 'BEGIN { FS="<li><span>" } { gsub(".*</span>","",$3);gsub("</li>","",$3); print $3}'`
    date=`echo $curl_output | awk 'BEGIN { FS="<li><span>" } { gsub(".*</span>","",$4);gsub("</li>","",$4); print $4}'`
    subsection=`echo $curl_output | awk 'BEGIN { FS="<li><span>" } { gsub(".*</span>","",$5);gsub("</li>","",$5); print $5}'`
    status=`echo $curl_output | awk 'BEGIN { FS="<li><span>" } { gsub(".*</span>","",$6);gsub("</li>.*","",$6); print $6}'`

done