#!/bin/bash
# The purposes of the scripts are:
# 1. replace the clean_pub_pulp_psi.sh to support more stable services
# 2. restart the services before doing the testing
# You can get more details by https://projects.engineering.redhat.com/browse/ERRATA-7932

set -eo

for server in "${pub_server}" "${pulp_rpm_server}" "${pulp_docker_server}"
do
  echo "== Preparing: ${server}"
  ssh -i /root/.ssh/id_rsa -o "StrictHostKeyChecking no" root@${pulp_docker_server}  'sh /root/prepare.sh'
done


