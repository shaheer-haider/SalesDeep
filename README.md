# About Scrapper
[https://github.com/shaheer-haider/SalesDeep](https://github.com/shaheer-haider/SalesDeep)

This scrapper is used to scrap products of specified brands from
[https://login.salesdeep.com/](https://login.salesdeep.com/)

It uploads the scrapped data in S3 and sends it to this email address
d.kapic@hotmail.com

#

#### Data can also be found in S3 
<code><a href="https://us-east-2.console.aws.amazon.com/s3/buckets/salesdeep-scrapped-data?region=us-east-2&bucketType=general">https://us-east-2.console.aws.amazon.com/s3/buckets/salesdeep-scrapped-data?region=us-east-2&bucketType=general</a></code>

You can find a folder with a name in the following format
YYYY-MM-dd-HH-mm-ss

#
## How to run?
Simply click this link

<h3><code><a href="https://pyoajf2qgymnya6n2qbujxpobe0uwsnq.lambda-url.us-east-2.on.aws/">https://pyoajf2qgymnya6n2qbujxpobe0uwsnq.lambda-url.us-east-2.on.aws/</a></code></h3>

It’ll execute a lambda function that’ll launch a docker container on Elastic container service on AWS

https://us-east-2.console.aws.amazon.com/ecs/v2/clusters/main/tasks?region=us-east-2

It takes more than a day to scrap all the brands' products.

#
## Tech Stack:
- Python3
- S3
- Elastic container service
- AWS Lambda

