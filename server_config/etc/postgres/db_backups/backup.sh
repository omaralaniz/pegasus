#!/bin/bash
DATE=`date +"%Y-%m-%dT%H:%M:%SZ"`
#pg_dump -d pegasus-dev > /var/lib/postgresql/db_backups/dev/dev-$DATE.psql
#pg_dump -d pegasus-prd > /var/lib/postgresql/db_backups/prd/prd-$DATE.psql
pg_dump -d pegasus > /var/lib/postgresql/db_backups/prd/prd-$DATE.psql
