Script to load random data into a redis cluster.
This script will create a 256MB block of data and upload this to different unique keyes depending on the size provided as an argument (default to 1 key/value pair of 256MB).
For safety, the values have a default expiration of 1 day (86400 Seconds).
Script can also be used to flush the database by passing the -f/--flash argument. This function exits upon completion.

Installation
pip3 install -r requirements.txt

Usage
loader.py [-h] [-v] [-s SIZE] -r HOST [-p PORT] [-f]

Arguments

    -h, --help            show this help message and exit
    -v, --verbose         increase output verbosity
    -s SIZE, --size SIZE  Size in GB to store
    -r HOST, --host HOST  ElastiCache Redis Primary Endpoint
    -p PORT, --port PORT  Redis port
    -f, --flush           Flush the database and NOT fill it

Example
./loader.py -r thevault.jljtfa.ng.0001.use1.cache.amazonaws.com -s 14.5
This will popolate the redis cluster with 14.5 GB of data