import boto3
from elasticsearch import Elasticsearch

# Configuration ElasticSearch
ES_INDEX = 'storage'

# Initialisation de objet ElasticSearch
es = Elasticsearch(['http://localhost:9200'])

s3_resource = 'S3: Storage - Standard'
ec2_resource = 'Amazon Elastic Compute Cloud - Compute'
rds_resource = 'Amazon Relational Database Service'


def lambda_handler(event, context):
    start_period = '2023-01-01'
    end_period = '2023-03-27'
    cost = get_cost(start_period, end_period, s3_resource)
    es.index(index=ES_INDEX, body=cost)
    return cost


def get_cost(start_period, end_period, resource):
    ce = boto3.client('ce')
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_period,
            'End': end_period,
        },
        Granularity='MONTHLY',
        Metrics=['NetUnblendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'LINKED_ACCOUNT'
            }
        ],
        Filter={'Dimensions': {'Key': 'USAGE_TYPE_GROUP', 'Values': [resource]}}
    )
    return response['ResultsByTime']
