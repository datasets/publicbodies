#!/usr/bin/python3

import urllib.request
import csv
import os

'''
Script for importing the open data on italian public bodies in 
okfn/publibodies database
''' 

#Script parameters
#Acronyms used: ipa -> indicePa , pbo -> publicbodies.org
#URL of the data in indicepa site
IPA_URL = "http://www.indicepa.gov.it/public-services/opendata-read-service.php?dstype=FS&filename=amministrazioni.txt"

#Categories of public bodies to skip during import (for now Schools)
not_wanted_categories = ["Istituti di Istruzione Statale di Ogni Ordine e Grado"];

#path to publicbodies repository root
PBO_PATH = "../"

#name of the output file
PBO_FILENAME = PBO_PATH + "data/it.csv"

#Name of the temporary file downloaded 
IPA_FILENAME = "amministrazioni.txt"


#metadata documentation: http://www.indicepa.gov.it/public-services/docs-read-service.php?dstype=FS&filename=Metadati_Open_Data.pdf
#ipa_fieldnames = ["cod_amm","des_amm","Comune","nome_resp","cogn_resp","Cap","Provincia","Regione","sito_istituzionale","Indirizzo","titolo_resp","tipologia_istat","acronimo","cf_validato","Cf","mail1","tipo_mail1","mail2","tipo_mail2","mail3","tipo_mail4","mail5","tipo_mail5","url_facebook","url_twitter","url_googleplus","url_youtube","liv_accessibili"]
pbo_fieldnames = ["id","name","abbreviation","other_names","description","classification","parent_id","founding_date","dissolution_date","image","url","jurisdiction_code","email","address","contact","tags","source_url"]

def download_indicepa():
    print("Downloading indicePA data")
    file_req = urllib.request.urlopen(IPA_URL)
    print("indicePA data downloaded, saving to "+IPA_FILENAME)
    output = open(IPA_FILENAME,'wb')
    output.write(file_req.read())
    output.close()
    print("indicePA data saved")
    
def convert_data():
    print("Converting data to publicbodies csv file")
    pbo_writer = csv.DictWriter(open(PBO_FILENAME, 'w', newline=''), fieldnames=pbo_fieldnames, delimiter=',')
    pbo_writer.writeheader()
    with open(IPA_FILENAME) as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(10000))
        csvfile.seek(0)
        ipa_reader = csv.DictReader(csvfile,dialect=dialect)
        for ipa_row in ipa_reader:
            #clean row from "null" values
            for key in ipa_row.keys():
                if ipa_row[key] == "null":
                    ipa_row[key] = ""
            
            #preprocessing
            if ipa_row["tipologia_istat"] in not_wanted_categories:
                continue
            
            #cleaning ulrs
            ipa_row["sito_istituzionale"] = ipa_row["sito_istituzionale"].replace(",",".")
            if ipa_row["sito_istituzionale"] != "" and ipa_row["sito_istituzionale"][0:7] != "http://":
                ipa_row["sito_istituzionale"] = "http://" + ipa_row["sito_istituzionale"]
                
            
            pbo_row = {}
            #print("Saving PB " + ipa_row["cod_amm"])
            pbo_row["id"] = "it/" + ipa_row["cod_amm"]
            pbo_row["name"] = ipa_row["des_amm"]
            pbo_row["abbreviation"] = ipa_row["acronimo"]
            pbo_row["other_names"] = ""
            pbo_row["description"] = ""
            pbo_row["classification"] = ipa_row["tipologia_istat"]
            pbo_row["parent_id"] = ""
            pbo_row["founding_date"] = ""
            pbo_row["dissolution_date"] = ""
            pbo_row["image"] = ""
            pbo_row["url"] = ipa_row["sito_istituzionale"]
            pbo_row["jurisdiction_code"] = "IT"
            pbo_row["email"] =  ipa_row["mail1"]
            pbo_row["address"] = ipa_row["Indirizzo"].replace(","," ") + " - " + ipa_row["Cap"] + " " + ipa_row["Comune"] + " (" + ipa_row["Provincia"] + ") " + "Italy" 
            pbo_row["contact"] = ""
            pbo_row["tags"] = ""
            pbo_row["source_url"] = "http://www.indicepa.gov.it/ricerca/dettaglioamministrazione.php?cod_amm=" + ipa_row["cod_amm"]
                       
            #write row
            pbo_writer.writerow(pbo_row)
    
    print("File " + PBO_FILENAME + " created")
    
    #Remove indicepa file 
    os.remove(IPA_FILENAME)
    print("File " + IPA_FILENAME + " removed")

#main script
download_indicepa()
convert_data()
