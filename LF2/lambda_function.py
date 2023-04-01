import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import requests
import inflection

region = 'us-east-1'
host = 'search-photos-cf-cval6oo6erd4eb3s776smbmf74.us-east-1.es.amazonaws.com'
bucket_name = 'p-b2'

# Create an OpenSearch client object with AWS credentials
def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)

def lambda_handler(event, context):
    # Extract the search query from the API Gateway event
    print(event)
    query = event['queryStringParameters']['q']

    lex = boto3.client('lexv2-runtime')
    lex_response = lex.recognize_text(botId='HMGLSHPULC',
        botAliasId='1N7NLO6S0Y',
        localeId='en_US',
        sessionId='test',
        text=query)
    
    print(lex_response)

    slots = lex_response['interpretations'][0]['intent']['slots']
    
    keywords = []
    for slot in slots:
        if (slots[slot] is not None):
            print(slots[slot]['value'])
            keywords.append(slots[slot]['value']['resolvedValues'][0]) 
    
    output = []
    output_key = []
    if len(keywords)>0:
        keywords = [inflection.singularize(word) for word in keywords]
        print(keywords)

        url = "https://search-photos-cf-cval6oo6erd4eb3s776smbmf74.us-east-1.es.amazonaws.com/photos/_search?q="
        headers = {'Content-Type': 'application/json'}
        response = []
        for key in keywords:
            if (key is not None) and key != '':
                newUrl = url+key
                results = requests.get(newUrl, headers = headers, auth=('master', 'qweIOP123*()'))
                print(results)
                response.append(results.json())
        print (response)

        for r in response:
            if 'hits' in r:
                for val in r['hits']['hits']:
                    key = val['_source']['objectKey']
                    label = val['_source']['labels']
                    url = boto3.client('s3').generate_presigned_url(
                        ClientMethod='get_object', 
                        Params={'Bucket': bucket_name, 'Key': key},
                        ExpiresIn=3600)
                    if key not in output_key:
                        output_key.append(key) 
                        output.append({"url":url, "labels":label})
        print(output)

    
    resp = {
        "results": output
    }

        
    # Return the search results as an API Gateway response
    return {
        "statusCode": 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',},
        "body": json.dumps(resp)
    }

