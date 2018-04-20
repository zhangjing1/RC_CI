#!/bin/bash
server_name=$( hostname )
echo "== Begin to clean the pulp env ${server_name} =="
echo "== first prepare the env =="
for package in python-devel  python-virtualenv yum-utils
do
	if ! [[ $( rpm -qa | grep ${package} ) =~ "${package}" ]];then
		yum install -y ${package}
	else
		echo $( rpm -qa | grep ${package})
	fi
done
# in one-click env, we need to upgrade 'koji' before we can install brewkoji
if ! [[ $( rpm -qa | grep 'brewkoji') =~ "brewkoji" ]];then
	yum upgrade koji
	yum install -y brewkoji
else
	echo $( rpm -qa | grep 'brewkoji' )
fi
if [[ -z content-delivery-qe ]]; then
	rm -rf content-delivery-qe
fi
curl -L -O http://download.devel.redhat.com/rel-eng/RCMTOOLS/rcm-tools-rhel-7-server.repo
echo "== second get the clean scripts =="
git clone git://git.app.eng.bos.redhat.com/content-delivery-qe
cd content-delivery-qe
echo "== run the cases of clean data =="
virtualenv --system-site-packages ~/testpython
. ~/testpython/bin/activate
pip install -r test-requirements.txt
# change the host of the config
sed -i "s/${server_name}/pulp-e2e.usersys.redhat.com/g" /root/content-delivery-qe/unit_tests/configs/QA_01.conf
# disable some lines which bring some errors
sed -i 's/"errata"/#"errata"/g'  /root/content-delivery-qe/unit_tests/helpers/constants.py
sed -i 's/"pulp"/#"pulp"/g'  /root/content-delivery-qe/unit_tests/helpers/constants.py
# clean the pulp and pulp-docker data
py.test -v unit_tests/tests/clean_data.py::CleanData::test_clean_rhsm_pulp_data
py.test -v unit_tests/tests/clean_data.py::CleanData::test_clean_docker_pulp_data
echo "== The pulp env is clean =="