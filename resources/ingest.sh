#!/bin/bash

# 27.12.2020 - mclaurentiu79@gmail.com

if [ -z ${1+x} ]; then echo "Please specify a directory"; else echo "Attempting to ingest files in '$1'"; fi

directory=$(readlink --canonicalize $1)
filepattern="${directory}/*.json"
payloadfilepattern="${directory}/*.payload"

shopt -s nullglob

for file in $filepattern
do
    filecontent=$(<$file)
    base64value=$(echo $filecontent | base64)
    payload=$(echo "{ \"filename\": \""$(basename $file)"\", \"data\": \""$base64value"\"}" | tr -d '[:space:]')
    echo "$payload" >> $file".payload"
    echo "Converted"$file" to "$file".payload"
done

for file in $payloadfilepattern
do
    echo -e "START ingesting file "$file"\n"
    filecontent=$(<$file)
    base64value=$(echo $filecontent | base64)
    payload=$(echo "{ \"filename\": \""$(basename $file)"\", \"data\": \""$base64value"\"}" | tr -d '[:space:]')

    curl --location --request PUT 'http://srv.meaningfy.ws:9200/my-index/_doc/my-id?pipeline=legal' --header 'Authorization: Basic ZWxhc3RpYzpjaGFuZ2VtZQ==' --header 'Content-Type: application/json' --data-binary @$file
    echo -e "\n\nEND ingesting file "$file"\n"
done