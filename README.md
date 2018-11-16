# apache-replay python package

## Summary

Many pieces of software exist that can take an existing Apache httpd (or other)
log in the Common Log format or Combined log format, parse them, and then do
something with them.   I find it convenient to be able to do this with pure
Python, though you will see a minor concession to logstash for the indexing of
the logs.

## Installation

pip install apache-replay

## Usage

Generate usage with:

    apache-replay --help

## Examples

Count the number of requests in November of 2018:

    apache-replay --player count http://localhost:8000/ /var/logs/httpd/access_log.2018-11-*

Replay those same logs (only GET, HEAD, OPTIONS) against qa-mysite.com:

    apache-replay https://qa-mysite.com/ /var/logs/httpd/access_log.2018-11-*

Only replay 2000 log entries from that file

    apache-replay --count 2000 https://qa-mysite.com/ /var/logs/httpd/access_log.2018-11-*

