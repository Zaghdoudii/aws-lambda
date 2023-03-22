import json
import boto3
from datetime import datetime


def lambda_handler(event, context):
    # Getting a list of Ec2(s) that have the tag schedule to start/stop them
    (nb_ec2_stopped, nb_ec2_started) = ec2_schedule()

    # Getting a list of docDB cluster(s) that have the tag schedule to start/stop them
    (nb_docdb_stopped, nb_docdb_started) = docdb_schedule()

    return {
        'statusCode': 200,
        'body': json.dumps("Ec2 : %s stopped / %s started | DocDb : %s stopped / %s started" % (nb_ec2_stopped, nb_ec2_started, nb_docdb_stopped, nb_docdb_started))
    }


def docdb_schedule():
    client = boto3.client('docdb')
    nb_docdb_started = 0
    nb_docdb_stopped = 0

    client = boto3.client('docdb')
    response = client.describe_db_clusters()
    for docdb_cluster in response['DBClusters']:
        id_docdb = docdb_cluster['DBClusterIdentifier']
        arn_docdb = docdb_cluster['DBClusterArn']
        status_docdb = docdb_cluster['Status']
        print(">>> id_docdb : %s - Status: %s - arn : %s" % (id_docdb, status_docdb, arn_docdb))
        tags = client.list_tags_for_resource(ResourceName=arn_docdb)
        for t in tags['TagList']:
            if t['Key'] == 'schedule':
                print("> Value : %s" % t['Value'])
                if is_in_schedule_range(t['Value']):
                    if status_docdb != 'available':
                        print('Starting DocDB instance %s', id_docdb)
                        response = client.start_db_cluster(DBClusterIdentifier=id_docdb)
                        print(response)
                        nb_docdb_started += 1
                elif status_docdb == 'available':
                    print('Stopping DocDB instance %s', id_docdb)
                    response = client.stop_db_cluster(DBClusterIdentifier=id_docdb)
                    print(response)
                    nb_docdb_stopped += 1

    return nb_docdb_stopped, nb_docdb_started


def ec2_schedule():
    ec2 = boto3.resource('ec2')
    client = boto3.client('ec2')
    nb_ec2_stopped = 0
    nb_ec2_started = 0
    filters = [{
        'Name': 'tag:schedule',
        'Values': ['*']
    }]

    instances = ec2.instances.filter(Filters=filters)
    for i in instances:
        id =  i.id
        state =  i.state
        print(">>> instance : %s is %s" % (id, state))
        for t in i.tags:
            if t['Key'] == 'schedule':
                print("> Value : %s" % t['Value'])
                if is_in_schedule_range(t['Value']):
                    if state['Name'] != 'running':
                        print('Starting instance %s', id)
                        response = client.start_instances(InstanceIds=[id])
                        print(response)
                        nb_ec2_started += 1
                else: #out of range UP
                    if state['Name'] == 'running':
                        print('Sopping instance %s', id)
                        response = client.stop_instances(InstanceIds=[id])
                        print(response)
                        nb_ec2_stopped += 1

    return  nb_ec2_stopped, nb_ec2_started


def is_in_schedule_range(schedule_range):
    gmtZone = 1
    dt = datetime.now()
    todayNumber = dt.isoweekday()
    currentHour = dt.hour + gmtZone
    if currentHour > 24:
        currentHour = 0

    print('Day of a week is:', todayNumber)
    print('Hour of day is:', currentHour)
    schedule_params = schedule_range.split("@")
    if len(schedule_params) > 0:
        days_range = schedule_params[0].split('-')
        hours_range = schedule_params[1].split('-')
        if todayNumber in range(int(days_range[0]), int(days_range[1])):
            print("> days : %s" % days_range)
            if currentHour in range(int(hours_range[0]), int(hours_range[1])):
                print('Hour of day is in range UP : %s', currentHour)
                return True
            else: #out of range UP
                print(">>> Out of hour UP range")
                return False
        else: #out of range UP
            print(">>> Out of date UP range")
            return False

    return False