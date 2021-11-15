## Amazon Cloudfront Distribution Clone

### Background

As user of Amazon CloudFront always have multiple Amazon CloudFront distributions, and one most common task is to create these new distributions, and these distributions are usually configured with same parameters, like dynamic contents acceleration with TTL settings to 0.

It would be great to have a distribution cloning API or similar function to achieve this, while currently there is no such built-in CloudFront API, here comes this cloudfront-clone-distro utils project - you could clone reference CloudFront distribution quickly!

### Prerequisites

Before running this script, making sure you have access to:
1. Set up a python3 environment
2. Requirement: boto3 >= 1.18.25

### Usage
Running the script as an example:

```
$ python3 cloudfront_config.py --domain service.yuhong.com --origin ec2-10-11-12-13.compute-1.amazonaws.com --dist_ref E2Z4DFMIXLKSQS
```

### AWS Services Related

This project has leveraged existing AWS SDK of CloudFront and ACM shown below.

CloudFront:

``` 
get_distribution_config()
create_distribution()
```
ACM: 
```
list_certificates()
```


