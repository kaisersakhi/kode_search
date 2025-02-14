#!/bin/sh

set -e

# echo "Application package deployed and activated!"

# docker exec vespa bash -c '/opt/vespa/bin/vespa-start-services'

until curl -s --fail http://localhost:19071/state/v1/health | grep -q '"code" : "up"'; do
  echo "Waiting for Vespa..."
  sleep 5
done

echo "Vespa is ready! Deploying application package..."
docker exec vespa bash -c '/opt/vespa/bin/vespa-deploy prepare /app/package && /opt/vespa/bin/vespa-deploy activate'
