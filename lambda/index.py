import json
import boto3
import os
import requests
import random
from vz_edge_discovery import VzEdgeDiscovery

def lambda_handler(event, context):
    # TODO implement
    """
    Prereq: Pull SSM Config
    """
    client = boto3.client('ssm',region_name=os.environ['AWS_REGION'])
    applicationName = client.get_parameter(
        Name='eds-data-plane-api-applicationName'
    )["Parameter"]["Value"]
    print("Application name", applicationName)
    edsAccessKey = client.get_parameter(
        Name='eds-data-plane-api-edsAccessKey'
    )["Parameter"]["Value"]
    print("Access key", edsAccessKey)
    edsSecretKey = client.get_parameter(
        Name='eds-data-plane-api-edsSecretKey'
    )["Parameter"]["Value"]
    print("Secret key", edsSecretKey)
    portNumber = client.get_parameter(
        Name='eds-data-plane-api-portNumber'
    )["Parameter"]["Value"]
    print("Port",portNumber)
    edsServiceProfileId = client.get_parameter(
        Name='eds-data-plane-api-edsServiceProfileId'
    )["Parameter"]["Value"]
    print("Service profile",edsServiceProfileId)
    edsServiceEndpointsId = client.get_parameter(
        Name='eds-data-plane-api-edsServiceEndpointsId'
    )["Parameter"]["Value"]
    print("Service registry",edsServiceEndpointsId)
    
    
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
                    print("Carrier IP Found: "+str(instances["Association"]["CarrierIp"]))
                    carrierIps.append(instances["Association"]["CarrierIp"])
                    subnetInfo=client.describe_subnets(SubnetIds=[instances["SubnetId"]])
                    print("Corresponding Subnet Info: "+str(subnetInfo["Subnets"][0]["AvailabilityZone"]))
                    subnets.append(subnetInfo["Subnets"][0]["AvailabilityZone"])
                    carrierIPFound=True
                except:
                    print("No Carrier IP found.")
    
    print("\nSummary of extracted data from AWS API...")   
    fqdns=["test.application.com" for i in range(len(carrierIps))] 
    print(carrierIps,subnets,fqdns)
    
    ## Next, populate EDS with relevant carrier metadata
    """
    Step 1: Authenticate to Verizon Edge Discovery Service
    """
    my_obj = VzEdgeDiscovery()
    access_token=my_obj.authenticate(app_key=edsAccessKey,secret_key=edsSecretKey)
  
    """
    Step 2: Generate Service Profile (if one does not exists)
    """
    print("Creating service profile...")
    profileResponse=""
    if edsServiceProfileId==" ":
        profileResponse=my_obj.create_service_profile(access_token=access_token,max_latency=40)
        print(profileResponse)
        client = boto3.client('ssm',region_name=os.environ['AWS_REGION'])
        new_string_parameter = client.put_parameter(Name='eds-data-plane-api-edsServiceProfileId', Value=str(profileResponse), Type='String', Overwrite=True)
    else:
        print("Service profile created... Proceeding with service registry creation.")
   
    """
    Step 3: Create Service Registry (of one does not exist)
    """
   # Note, if serviceProfile already exists, use it from SSM
    if profileResponse=="":
        profileResponse=edsServiceProfileId

    myApplicationId="Verizon_5G_Edge_Application"
    if edsServiceEndpointsId==" " and carrierIPFound==True:
        print("No existing service registry. Creating serviceEndpoints object...")
        # Populate array of endpoint IDs based on available subnets
        myApplicationIds=[]
        fqdns=[]
        for subnet in subnets:
            myApplicationIds.append("APPLICATION_END_POINT_ID_"+str(random.randint(0,10000)))
            fqdns.append("testapplication.eds.com")
            
        # Create service registry
        endpointsResponse=my_obj.create_service_registry(
            access_token=access_token,
            service_profile_id=profileResponse,
            carrier_ips=carrierIps,
            availability_zones=subnets,
            application_id=myApplicationIds,
            fqdns=fqdns)

        client = boto3.client('ssm',region_name=os.environ['AWS_REGION'])
        print(endpointsResponse)
        new_string_parameter = client.put_parameter(Name='eds-data-plane-api-edsServiceEndpointsId', Value=str(endpointsResponse), Type='String', Overwrite=True)
    
    else: #If EDS service registry needs to be updated, create net-new service registry
        # Populate array of endpoint IDs based on available subnets
        print("Service registry already exists...")
        myApplicationIds=[]
        fqdns=[]
        for subnet in subnets:
            myApplicationIds.append("APPLICATION_END_POINT_ID_"+str(random.randint(0,10000)))
            fqdns.append("testapplication.eds.com")
        
        endpointsResponse=my_obj.create_service_registry(
            access_token=access_token,
            service_profile_id=profileResponse,
            carrier_ips=carrierIps,
            availability_zones=subnets,
            application_id=myApplicationIds,
            fqdns=fqdns)
        
        # Update SSM parameter for sevice registry ID
        print(endpointsResponse)
        client = boto3.client('ssm',region_name=os.environ['AWS_REGION'])
        new_string_parameter = client.put_parameter(Name='eds-data-plane-api-edsServiceEndpointsId', Value=str(endpointsResponse), Type='String', Overwrite=True)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Success from Lambda!')
    }
