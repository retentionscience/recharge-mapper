# ReCharge Mapper

This script will call the ReCharge API ([documentations](https://developer.rechargepayments.com/?python#introduction)) and retrieve ReCharge subscription data and generate a subscription .tsv [file](https://s3.amazonaws.com/rsapi-production/onboarding/docs/FTP-Setup.html#header-subscriptions) which then will be automatically uploaded to a SFTP server (Retention Science will provide you credentials to your SFTP server)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
For you to retrieve your ReCharge Data, you will need to request your [ReCharge API Token](http://support.rechargepayments.com/article/551-generate-an-api-token)

You will want to install python 2.7 in your system environment. Also you will want to determine if your business supports trials and how to identify trial subscriptions from non-trial subscriptions. 

recharge_mapper.py assumes you are using [charge_delay](http://support.rechargepayments.com/article/89-change-first-charge-price-or-interval-vs-recurring-price) to manage trial which is what ReCharge suggests (as of Oct. 2017)

You will need to execute this script using Cron (or some type of job scheduler). We suggest you use Cron jobs to run this script as they are readily available in linux and UNIX. You can learn more how to set this up [here](https://www.cyberciti.biz/faq/how-do-i-add-jobs-to-cron-under-linux-or-unix-oses/)

### Installing

First you will need to setup the python environment. Follow instructions [here](http://docs.python-guide.org/en/latest/starting/install/osx/)

Then install the dependencies using pip.

If you're having issues importing requests. Type in 
```
pip install pyopenssl ndg-httpsclient pyasn1
```
You will need to add your crendentials
```
# ReSci SFTP Credentials
API_USER = "your-api-key"
API_PASS = "your-api-pass"

# ReCharge API Token
RECHARGE_KEY  = "Recharge-api-key"
```
### Get Historical Subscription Data
To get historical subscription data, set the variable 
```
RUN_HISTORICAL = True
```
And run the script manually in terminal.

### Set Daily Subscription Feed
Prior to setting up the daily cron job. You will need to set RUN_HISTORICAL = False.

If you wished to have a script named /your-path/recharge_mapper.py run every day at 3am, your crontab entry would look like as follows. 

First, give execute permission to your script
```
chmod a+x recharge_mapper.py
```
Open crontab entry
```
crontab -e
```

Enter the following:
```
0 3 * * * /your-path/recharge_mapper.py
```

## License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Acknowledgments

* Thank you ReCharge Support Team
