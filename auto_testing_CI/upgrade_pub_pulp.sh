#!/bin/sh
set -eo pipefail
# the CI is quite simple, just to upgrade pub&pulp packages

get_build_installed_on_server() {
	# It is odd to meet such error 'ssh: Could not resolve hostname pup-e2e.usersys.redhat.com: Name or service not known'
    # use the ip of pub temporaily
    ssh -o "StrictHostKeyChecking no" root@${1} "rpm -qa | grep ${2} | sed 's/.noarch//'"
}

initialize_env(){
	pub_deploy_failed=""
	pulp_rpm_deploy_failed=""
	pulp_docker_deploy_failed=""
}

upgrade_pub(){
	pub_ansible=""
	if [[ ! -z ${pub_jenkins_build} ]]; then
		echo "== will upgrade the pub env =="
		pub_ansible="ansible-playbook -u root -i ${WORKSPACE}/inventory/pub ${WORKSPACE}/playbooks/pub/e2e/deploy-pub-e2e.yml -e pub_jenkins_build=${pub_jenkins_build}"
		echo $(pwd)
		echo ${pub_ansible}
		${pub_ansible}
		if [[ $(echo $?) == "0" ]]; then
			echo "== Pub is ready =="
            echo "get_build_installed_on_server ${pub_server} 'pub-hub'"
			pub_installed=$( get_build_installed_on_server 'pub-e2e.usersys.redhat.com' 'pub-hub')
			echo "== The pub installed is:"
			echo "== ${pub_installed}"
		else
			pub_deploy_failed=true
		fi
	fi
}

upgrade_pulp_rpm(){
	pulp_rpm_ansible=""
	pulp_rpm_build_ansible=""
	pulp_build_for_rpm_ansible=""
	pulp_cdn_distributor_build_ansible=""
	pulp_rpm_ansible_part=""
	if [[ ! -z ${pulp_build_for_rpm} ]]; then
		pulp_build_for_rpm_ansible=" -e pulp_build=${pulp_build_for_rpm}"
	fi
	if [[ ! -z ${pulp_rpm_build} ]]; then
		pulp_rpm_build_ansible=" -e pulp_rpm_build=${pulp_rpm_build} "
	fi
	if [[ ! -z ${pulp_cdn_distributor_build} ]]; then
		pulp_cdn_distributor_build_ansible=" -e pulp_cdn_distributor_build=${pulp_cdn_distributor_build}"
	fi
	pulp_rpm_ansible_part="${pulp_build_for_rpm_ansible}${pulp_rpm_build_ansible}${pulp_cdn_distributor_build_ansible}"
	if [[ ! -z ${pulp_rpm_ansible_part} ]]; then
		pulp_rpm_ansible="ansible-playbook -u root -i ${WORKSPACE}/inventory/pulp ${WORKSPACE}/playbooks/pulp/deploy-pulp-rpm-e2e.yml ${pulp_rpm_ansible_part}"
		${pulp_rpm_ansible}
		if [[ $(echo $?) == "0" ]]; then
			echo "== Pulp-rpm is ready =="
			echo "== All related pulp packages installed are: =="
			echo $( get_build_installed_on_server ${pulp_rpm_server} pulp-server)
			echo $( get_build_installed_on_server ${pulp_rpm_server} pulp-rpm-plugins)
			echo $( get_build_installed_on_server ${pulp_rpm_server} pulp-cdn-distributor-plugins)
		else
			pulp_rpm_deploy_failed=true
		fi
	fi
}


upgrade_pulp_docker(){
	pulp_docker_ansible=""
	pulp_docker_build_ansible=""
	pulp_build_for_docker_ansible=""
	pulp_docker_ansible_part=""
	if [[ ! -z ${pulp_build_for_docker} ]]; then
		pulp_build_for_rpm_ansible=" -e pulp_build=${pulp_build_for_docker}"
	fi
	if [[ ! -z ${pulp_docker_build} ]]; then
		pulp_rpm_build_ansible=" -e pulp_docker_build=${pulp_docker_build} "
	fi
	pulp_docker_ansible_part="${pulp_build_for_docker_ansible}${pulp_docker_build_ansible}"
	if [[ ! -z ${pulp_docker_ansible_part} ]];then
		pulp_docker_ansible="ansible-playbook -u root -i ${WORKSPACE}/inventory/pulp ${WORKSPACE}/playbooks/pulp/deploy-pulp-docker-e2e.yml ${pulp_rpm_ansible_part}"
		${pulp_docker_ansible}
		if [[ $(echo $?) == "0" ]]; then
			echo "== Pulp-docker is ready =="
			echo "== All related pulp packages installed are: =="
			echo $( get_build_installed_on_server ${pulp_docker_server} pulp-server)
			echo $( get_build_installed_on_server ${pulp_docker_server} pulp-docker-plugins)
		else
			pulp_docker_deploy_failed=true
		fi
	fi
}

# The following 2 functions are used to do some settings for the docker-e2e env.
disable_firewall_service(){
	echo "== Disable the firewalld service on ${1}"
	ssh -o "StrictHostKeyChecking no" root@${1} 'if [[ $(systemctl is-active firewalld) =~ "active" ]]; then systemctl stop firewalld; fi'
	echo "== Done: The firewald service of ${1} has been disabled"
}

set_docker_registry(){
	echo "== Set docker-registry to docker-e2e against the docker-e2e server"
	INSECURE_REGISTRY="--insecure-registry docker-e2e.usersys.redhat.com:5000 --insecure-registry brew-pulp-docker01.web.prod.ext.phx2.redhat.com:8888 --insecure-registry brew-pulp-docker01.web.qa.ext.phx1.redhat.com:8888 --insecure-registry pulp-docker-brew-qa.usersys.redhat.com:8888"
	ssh_command="echo INSECURE_REGISTRY=\""${INSECURE_REGISTRY}"\" >> /etc/sysconfig/docker"
	ssh -o "StrictHostKeyChecking no" root@${1} "${ssh_command}"
	# seems ssh will omit the " as default whenever how many " we use to describe the variables
	ssh -o "StrictHostKeyChecking no" root@${1} 'sed -i "s/=-/=\"-/" /etc/sysconfig/docker'
	ssh -o "StrictHostKeyChecking no" root@${1} 'sed -i "s/8888$/8888\"/" /etc/sysconfig/docker'
	echo "== Done: The docker registry has been updated against docker-e2e server"
}

initialize_env
upgrade_pub
upgrade_pulp_rpm
upgrade_pulp_docker
# Disable the firewalld service for all e2e related servers
# I do not suggest CI_3 to do too many workarounds, but Rony have said it's not easy to let others do
# Then Let CI_3 help. See the RFE reported by Rony https://projects.engineering.redhat.com/browse/ERRATA-6627
echo "=== Disable all firewall services on all pub & pulp related environments"
for server in ${pulp_rpm_server} ${pulp_docker_server} ${pub_server}  'docker-e2e.usersys.redhat.com'
do
	disable_firewall_service ${server}
done
echo "=== All firewalld services have been disabled"
# set the registry of the e2e docker server
set_docker_registry 'docker-e2e.usersys.redhat.com'
if [[ ${pub_deploy_failed} == "true" ]] || [[ ${pulp_rpm_deploy_failed} == "true" ]] || [[ ${pulp_docker_deploy_failed} == "true" ]]; then
	echo "==== Upgrade failed ===="
	exit 1
else
	echo "== Done =="
fi
