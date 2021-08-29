"""
 AWS SDK used: 
 CloudFront:
	get_distribution_config(),
	create_distribution()
 ACM:
 	list_certificates()
"""
import boto3
from botocore.config import Config
import botocore.exceptions
from datetime import datetime, timezone
import argparse
import logging
import json

"""
Instructions

Before running this script, making sure you have access to:
1. set up a python3 environment
2. boto3 >= 1.18.25

Running the script as an example

$ python3 cloudfront_config.py --domain service.yuhong.com --origin ec2-54-90-38-64.compute-1.amazonaws.com --dist_ref E2Z4DFMIXLKSQP
"""
# Set up our logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def loadConfig():
    fp = open("./config.json")   
    data = json.load(fp)
    return(data)

def get_reference_config(ref_dist):
	client = boto3.client('cloudfront')
	try:
		return client.get_distribution_config(Id=ref_dist)
	except botocore.exceptions.ClientError as error:
		logger.exception(f"{format(error)}")
		raise error

def get_certificate_mapping():
	my_config = Config(
	   region_name = 'us-east-1'
	   #  signature_version = 'v4',
	   #  retries = {
	   #      'max_attempts': 10,
	   #      'mode': 'standard'
    # }
    )
	client = boto3.client('acm', config=my_config)
	# paginator = client.get_paginator('list_certificates')
	try:
		# cert_dict = {}
		response = client.list_certificates(
		    CertificateStatuses=[
		        'ISSUED'
		    ],
		    MaxItems=1000
		)
		# print('first response' + response['NextToken'])
		certs = response['CertificateSummaryList']
		while "NextToken" in response:
			response = client.list_certificates(
					CertificateStatuses=[
			        'ISSUED'
			    ],
			    MaxItems=1000,
			    NextToken= response['NextToken']
			)
			certs.extend(response["CertificateSummaryList"])
		cert_dict = {}
		for cert in	certs:
			cert_dict[cert['DomainName']] = cert['CertificateArn']
		# print(cert_dict)
		return(cert_dict)
	except botocore.exceptions.ClientError as error:
		logger.exception(f"{format(error)}")
		raise error

def get_certificate_arn(certs, domain):
	# print(certs)
	if domain in certs:
		cert = certs[domain]
	else:
		cert_domain = '*.' + domain.split(".", 1)[-1]
		# print(cert_domain)
		if cert_domain in certs:
			cert = certs[cert_domain]
		else:
			logger.info(f"No certificate for domain - {format(domain)} in ACM. Please create or import one.")
			# print('No certificate for domain \'' + domain +'\' in ACM. Please create or import one.')
			exit(1)
	# print(cert)
	logger.info(f"Use ACM certificate for domain \'{format(domain)}\': {format(cert)}.")
	return cert


def set_config_based_on_ref(ref_config, conf_domain, conf_origin, certArn, bucket, prefix):
	# ref_config['DistributionConfig']['Aliases'] =	{
	# 	'Quantity': 1,
 #         'Items': [
 #                conf_domain
 #         ]
	# }
	ref_config['DistributionConfig']['Aliases'] =	{ # for yuhongma test using self-signed certificate
		'Quantity': 0,
         # 'Items': [
         #        conf_domain
         # ]
	}
	config = ref_config['DistributionConfig']
	config['CallerReference'] = str(datetime.now(tz=None).timestamp())
	config['Origins']['Items'][0]['Id'] = conf_origin
	config['Origins']['Items'][0]['DomainName'] = conf_origin
	config['DefaultCacheBehavior']['TargetOriginId'] = conf_origin
	config['Comment'] = conf_domain
	config['ViewerCertificate']['ACMCertificateArn'] = certArn
	if 'Logging' in config:
		if config['Logging']['Enabled'] == True:
			config['Logging']['Bucket'] = bucket
			config['Logging']['Prefix'] = prefix
	return(config) 

def create_distribution(config):
	client = boto3.client('cloudfront')
	try:
		distribution = client.create_distribution(DistributionConfig=config)
		logger.info(f"Done! Created distribution {format(distribution['Distribution']['Id'])}.")
	except botocore.exceptions.ClientError as error:
		logger.exception(f"{format(error)}")
		raise error


if __name__ == "__main__":
	data = loadConfig() # s3 logging
	parser = argparse.ArgumentParser()
	parser.add_argument('--domain', type=str, required=True)
	parser.add_argument('--origin', type=str, required=True)
	parser.add_argument('--dist_ref', type=str, required=True)
	args = parser.parse_args()

	conf_domain = args.domain 
	conf_origin = args.origin
	conf_ref_dist = args.dist_ref

	ref_config = get_reference_config(conf_ref_dist)

	certs = get_certificate_mapping()
	certArn = get_certificate_arn(certs, conf_domain)

	config = set_config_based_on_ref(ref_config, conf_domain, conf_origin, certArn, data['logBucket'], data['logPrefix'])
	# print(config)
	create_distribution(config)

