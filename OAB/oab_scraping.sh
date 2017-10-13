#!/bin/bash

# The first OAB code is 10001
FIRST_OAB=10001

if [ $# -lt 2 ]; then
    printf 'usage: %s [nro_oab] [quantidade]\n' "$(basename "$0")" >&2
    exit 64
fi

# Check if the provided OAB code is valid
if [ $1 -lt $FIRST_OAB ]; then
    printf 'The OAB code must be greater than 10000'
    exit 1
fi

# Setting the amount of OAB codes to be scraped
initial_oab=$1
if [[ $2 > 0 ]]; then
    final_oab=$(($initial_oab + $2 - 1))
else
    final_oab=$(($initial_oab + $2))
fi

# Setting the output filenames
output_ok="$initial_oab-$final_oab.csv"
output_nok=$initial_oab-$final_oab"_nok.csv"

printf "Scraping data from https://www2.oabsp.org.br/asp/consultaInscritos/consulta01.asp\n\n"
printf "Scraping: "

for oab_number in `seq $initial_oab $final_oab`;do
    printf "$oab_number "
    curl_output=`curl 'https://www2.oabsp.org.br/asp/consultaInscritos/consulta_nr_advogado.asp' -s -H 'Referer: https://www2.oabsp.org.br/asp/consultaInscritos/consulta01.asp' -H 'Connection: keep-alive' --data 'pagina=0&tipo_consulta=1&nr_inscricao='$oab_number'&cbxadv=1&id_tipoinscricao=1&nome_advogado=&parte_nome=1&nr_cpf=&idCidade=0' --compressed | tail -n 1`
    
    # Write the OAB code without output in the "oab_nok.csv" file
    if [[ $curl_output == *"N&atilde;o h&aacute; resultados que satisfa&ccedil;am a busca"* ]]; then
        echo $oab_number >> $output_nok
    else
        name=`echo $curl_output | awk 'BEGIN { FS="<li><span>" } { gsub("</span></li>","",$2); print $2}'`
        oab_number_state=`echo $curl_output | awk 'BEGIN { FS="<li><span>" } { gsub(".* - ","",$3);gsub("</li>","",$3); print $3}'`
        date=`echo $curl_output | awk 'BEGIN { FS="<li><span>" } { gsub(".*</span>","",$4);gsub("</li>","",$4); print $4}'`
        subsection=`echo $curl_output | awk 'BEGIN { FS="<li><span>" } { gsub(".*</span>","",$5);gsub("</li>","",$5); print $5}'`
        status=`echo $curl_output | awk 'BEGIN { FS="<li><span>" } { gsub(".*</span>","",$6);gsub(" </li>.*","",$6); print $6}'`
        
        echo $oab_number,$name,$status,$oab_number_state,$subsection,$date >> $output_ok
    fi
done

echo
exit 0
