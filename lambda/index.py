import json
import boto3
import os
import requests
import vzEdgeDiscovery

def lambda_handler(event, context):
    # TODO implement
    """
    Prereq: Pull SSM Config
    """
    client = boto3.client('ssm',region_name=os.environ['AWS_REGION'])
    applicationName = client.get_parameter(
        Name='eds-data-plane-api-applicationName'
    )["Parameter"]["Value"]
    print(applicationName)
    edsAccessKey = client.get_parameter(
        Name='eds-data-plane-api-edsAccessKey'
    )["Parameter"]["Value"]
    print(edsAccessKey)
    edsSecretKey = client.get_parameter(
        Name='eds-data-plane-api-edsSecretKey'
    )["Parameter"]["Value"]
    print(edsSecretKey)
    portNumber = client.get_parameter(
        Name='eds-data-plane-api-portNumber'
    )["Parameter"]["Value"]
    print(portNumber)
    edsServiceProfileId = client.get_parameter(
        Name='eds-data-plane-api-edsServiceProfileId'
    )["Parameter"]["Value"]
    print(edsServiceProfileId)
    edsServiceEndpointsId = client.get_parameter(
        Name='eds-data-plane-api-edsServiceEndpointsId'
    )["Parameter"]["Value"]
    print(edsServiceEndpointsId)
    
    
    # Collect Input from SSM including tag value for tagName "eds-ec2-plugin-app-name" (required tag value for relevant instances)
    client = boto3.client('ec2',region_name=os.environ['AWS_REGION'])
    reservations = client.describe_instances(Filters=[{'Name': 'tag:eds-ec2-plugin-app-name', 'Values': [applicationName]}])
    
    carrierIps=[]
    subnets=[]
    carrierIPFound=False 
    # Ensure that all instances across all reservations are accounted 
    for reservation in reservations["Reservations"]:
        for nodeGroups in reservation["Instances"]:
            for instances in nodeGroups["NetworkInterfaces"]:
                try: 
                    carrierIPFound=True
                    print("Carrier IP Found: "+str(instances["Association"]["CarrierIp"]))
                    carrierIps.append(instances["Association"]["CarrierIp"])
                    subnetInfo=client.describe_subnets(SubnetIds=[instances["SubnetId"]])
                    print("Corresponding Subnet Info: "+str(subnetInfo["Subnets"][0]["AvailabilityZone"]))
                    subnets.append(subnetInfo["Subnets"][0]["AvailabilityZone"])
                except:
                    print("No Carrier IP found.")
    
    print("\nSummary of extracted data from AWS API...")   
    fqdns=["test.application.com" for i in range(len(carrierIps))] 
    print(carrierIps,subnets,fqdns)
    
    ## Next, populate EDS with relevant carrier metadata
    """
    Step 1: Authenticate to Verizon Edge Discovery Service
    """
    access_token=vzEdgeDiscovery.authenticate(
        appKey=edsAccessKey,
        secretKey=edsSecretKey)
    
    """
    Step 2: Generate Service Profile (if one does not exists)
    """
    profileResponse=""
    if edsServiceProfileId==" ":
        profileResponse=vzEdgeDiscovery.createServiceProfile(
            accessToken=access_token,
            maxLatency=40)
        print(profileResponse)
        client = boto3.client('ssm',region_name=os.environ['AWS_REGION'])
        new_string_parameter = client.put_parameter(Name='eds-data-plane-api-edsServiceProfileId', Value=str(profileResponse), Type='String', Overwrite=True)



    """
    Step 3: Create Service Registry (of one does not exist)
    """

   # Note, if serviceProfile already exists, use it from SSM
   if profileResponse=="":
       profileResponse=edsServiceProfileId

    myApplicationId="Verizon_5G_Edge_Application"
    if edsServiceEndpointsId==" " and carrierIPFound==True:
        endpointsResponse=vzEdgeDiscovery.createServiceRegistry(
            accessToken=access_token,
            serviceProfileId=profileResponse,
            carrierIps=carrierIps,
            availabilityZones=subnets,
            fqdns=fqdns,
            applicationId=myApplicationId)
        client = boto3.client('ssm',region_name=os.environ['AWS_REGION'])
        print(endpointsResponse)
        new_string_parameter = client.put_parameter(Name='eds-data-plane-api-edsServiceEndpointsId', Value=str(endpointsResponse), Type='String', Overwrite=True)
    else:
        edsServiceEndpointsId=vzEdgeDiscovery.updateServiceRegistry(
            accessToken=access_token,
            serviceEndpointsId=edsServiceEndpointsId,
            carrierIps=carrierIps,
            availabilityZones=subnets,
            fqdns=fqdns,
            applicationId=myApplicationId)

    
    return {
        'statusCode': 200,
        'body': json.dumps('Success from Lambda!')
    }
