#!/bin/bash
set -e -o pipefail

echo "== get the clean scripts =="
git clone git://git.app.eng.bos.redhat.com/content-delivery-qe
cd content-delivery-qe

echo "== run the cases of clean data =="
virtualenv --system-site-packages ~/testpython
. ~/testpython/bin/activate
pip install --user setuptools --upgrade
pip install --user funcsigs
# The test-requirements.txt from CD team does not specify the python lib version
# ET run the script against instance openstack server, it means it will install the latest package without version specified
# I have to specify the python lib with some specific verison to avoid errors
pip install --user pytest==3.3.0
pip install --user -r test-requirements.txt

# change the host of the config
cp ${CI3_WORKSPACE}/content-script-config/QA_01_PSI.conf ${CI3_WORKSPACE}/content-delivery-qe/unit_tests/configs/QA_01.conf
#change the user of ssh to pulp
sed -i 's/at_user/root/g'  ${CI3_WORKSPACE}/content-delivery-qe/unit_tests/helpers/constants.py
# disable some lines which bring some errors
sed -i 's/"errata"/#"errata"/g'  ${CI3_WORKSPACE}/content-delivery-qe/unit_tests/helpers/constants.py
sed -i 's/"pulp"/#"pulp"/g'  ${CI3_WORKSPACE}/content-delivery-qe/unit_tests/helpers/constants.py

# disable one useless testing types
sed -i "/clear_akamai_cdn/d" ${CI3_WORKSPACE}/content-delivery-qe/unit_tests/helpers/test_run_helper.py
add_stop_services_step(){
  sed -i '/drop_db_cmd,/i\            stop_pulp_services_cmd,' ${CI3_WORKSPACE}/content-delivery-qe/unit_tests/helpers/test_run_helper.py
 # for cmd in drop_db_cmd deploy_db_cmd
  #do
  #  sed -i "s/${cmd}/#${cmd}/g" ${CI3_WORKSPACE}/content-delivery-qe/unit_tests/helpers/test_run_helper.py
  #done
}

add_stop_services_step
echo "== Before CleanData, check the pulp e2e service status =="
curl https://pulp-e2e.usersys.redhat.com/pulp/api/v2/status/ --insecure || true

# clean the pulp and pulp-docker data
cd ${CI3_WORKSPACE}/content-delivery-qe
py.test -v unit_tests/tests/clean_data.py::CleanData::test_clean_rhsm_pulp_data
py.test -v unit_tests/tests/clean_data.py::CleanData::test_clean_docker_pulp_data
echo "== The pulp env is clean =="

echo "== After CleanData, check the pulp e2e service status =="
curl https://pulp-e2e.usersys.redhat.com/pulp/api/v2/status/ --insecure
