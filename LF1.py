import json
import boto3
import urllib.parse
import requests
import base64 

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
opensearch = boto3.client('es')
index = "photos"
domain = "search-photos-2ziokdudvmpcxoxavaqgtditzi"
region = "us-east-1"
# model = "arn:aws:rekognition:us-east-1:115482439616:project/my_types/version/my_types.2023-03-22T00.16.22/1679458582288"

def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    response_s3 = s3.get_object(Bucket=bucket, Key=key)
    content = base64.b64decode(response_s3['Body'].read())


    # Use Rekognition to detect labels in the image
    response_rekognition = rekognition.detect_labels(
        Image={'Bytes': content}
    )
    
    # Create a JSON array of labels
    labels = [label['Name'] for label in response_rekognition['Labels']]
    print(labels)

    custom_labels = response_s3['Metadata']['customlabels'].split(',')
    print(custom_labels)
    if custom_labels:
        labels += custom_labels 
        
    labels = [label.lower() for label in labels] 
         
    print(labels)
    
    # Store the JSON object in OpenSearch
    doc = {
        'objectKey': key,
        'bucket': bucket,
        'createdTimestamp': response_s3['ResponseMetadata']['HTTPHeaders']['last-modified'],
        'labels': labels
    }
    
    print(doc)

    url = f"https://{domain}.{region}.es.amazonaws.com/{index}/_doc"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(doc).encode('utf-'), auth=('master', 'qweIOP123*()'))
    
    if response.status_code != 201:
        raise Exception('Error inserting document into OpenSearch index: {}'.format(response.text))

    print(response)
