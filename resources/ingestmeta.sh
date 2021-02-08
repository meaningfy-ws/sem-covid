#!/bin/bash

# 27.12.2020 - mclaurentiu79@gmail.com

if [ -z ${1+x} ]; then echo "Please specify a directory"; else echo "Attempting to ingest files in '$1'"; fi

directory=$(readlink --canonicalize $1)
filepattern="${directory}/*.json"
# payloadfilepattern="${directory}/*.payload"

shopt -s nullglob

for file in $filepattern
do
    echo -e "START sending file "$file"\n"
    filecontent=$(<$file)
    filename=$(basename $file)
    filename_without_extension="${filename%.*}"
    curl --location --request PUT 'http://srv.meaningfy.ws:9200/metadata/_doc/'$filename_without_extension --header 'Authorization: Basic ZWxhc3RpYzpjaGFuZ2VtZQ==' --header 'Content-Type: application/json' --data-binary @$file
    echo -e "\n\nEND sending file "$file"\n"
done