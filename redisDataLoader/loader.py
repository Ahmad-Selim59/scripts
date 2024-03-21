#!/usr/bin/env python3

import argparse
import logging
import redis
import time
import os

logging.basicConfig(format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%dT%H:%M:%S %Z')
logging.Formatter.converter = time.gmtime
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

## Default Values
ElastiCacheCluster = ""
ElastiCachePort= 6379
totalSize = 1
flush = False
ttl=86400

def main():
    pool = redis.ConnectionPool(host=ElastiCacheCluster, port=ElastiCachePort, db=0)
    ecache = redis.Redis(connection_pool=pool)

    if flush:
        logger.warning("FLUSHING DATASBASE " + ElastiCacheCluster)
        ecache.flushdb(asynchronous=True)
        logger.warning("FLUSH Complete. Exiting..")
        exit()

    dataSize = 2**28 #256MB
    logger.debug("Size of each key's value (Bytes): " + str(dataSize))
    
    data = os.urandom(dataSize)
    iterations = int((totalSize*1024*1024*1024) // dataSize)

    logger.info("Number of keys to be made: " + str(iterations+1))

    for i in range(iterations):
        key = "".join(['random_',str(i)])
        logger.debug("key: " + key)
        ecache.set(key,data,ex=ttl)
        
        # this can stress out the terminal session.
        #TODO: add option to get JUST a few keys to verify
        #logger.debug((redis.get("".join(['random_',str(i)]))))

    #'leftover' bits to get to full 'size'
    logger.debug("Generating remaining bytes")
    extra = int((totalSize*1024*1024*1024) % dataSize)
    edata = os.urandom(extra)
    ecache.set("".join(['random_' + str(iterations)]),edata,ex=ttl)
    logger.debug("key: " + "".join(['random_' + str(iterations)]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Redis Random Data Injector')
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
    parser.add_argument("-s", "--size", type=float, default=totalSize, help="Size in GB to store")
    parser.add_argument("-r", "--host", type=str, required=True, help="ElastiCache Redis Primary Endpoint")
    parser.add_argument('-l', '--log', type=str, help='Path to log file')
    parser.add_argument("-p", "--port", type=int, default=ElastiCachePort, help="Redis port")
    parser.add_argument("-f", "--flush", action="store_true", help="Flush the database and NOT fill it")
    parser.add_argument("-t", "--ttl", type=int, default=ttl, help="TTL for each key")

    args = parser.parse_args()

    if args.verbose > 0:
        logger.setLevel(logging.INFO)
        if args.verbose > 1:
            logger.setLevel(logging.DEBUG)
        
        if args.log:
             logger.addHandler(logging.FileHandler(filename=args.log, filemode='a'))

        logger.info("args passed: " + str(args))

    if args.host:
        ElastiCacheCluster=args.host

    if args.flush:
        flush=args.flush

    ElastiCachePort=args.port
    ttl = args.ttl
    totalSize=args.size

    try:
        main()
    except (TimeoutError, redis.exceptions.TimeoutError) as e :
        logger.error("Unable to connect to the redis cluster \"" + ElastiCacheCluster + "\"")
        logger.error(e)
