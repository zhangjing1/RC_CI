#!/bin/bash
set -e -o pipefail

add_random_user_as_default_user() {
  user_id=$(id | cut -d ' ' -f 1 |cut -d '=' -f 2)
  echo "default:x:${user_id}:0:root:/home/jenkins:/bin/bash" >> /etc/passwd
  whoami
}
# first, get the product version of pub & pulp
# second, get the installed pub & pulp version on e2e env
# finally, do the upgrade/downgrade to make sure the two kinds of version are the same
set -eo pipefail

export pub_version_url="http://pub.devel.redhat.com/pub/help/about/"
export pulp_version_url="https://gitolite.corp.redhat.com/cgit/puppet-cfg/modules/pulp.git/plain/data/rpm-versions-el7.yaml"
export pulp_docker_url="https://gitolite.corp.redhat.com/cgit/puppet-cfg/modules/pulp.git/plain/data/docker-pulp-rpm-versions.yaml"

install_scripts_env() {
   pip install --user --upgrade pip
   pip install --user confluence-py
   pip install --user python-jenkins
}

get_all_product_versions_content() {
  echo "===== get pub version from ${pub_version_url}"
  curl "${pub_version_url}" | grep Build: >> pub_pulp_version_content.txt
  echo "===== get pulp versions from ${pulp_version_url}"
  curl "${pulp_version_url}" | grep pulp-server >> pub_pulp_version_content.txt
  curl "${pulp_version_url}" | grep pulp-rpm-plugin >> pub_pulp_version_content.txt
  echo "===== get pulp docker versions from ${pulp_docker_url}"
  curl "${pulp_docker_url}" | grep pulp-server  >> pub_pulp_version_content.txt
  curl "${pulp_docker_url}" | grep pulp-rpm-plugin  >> pub_pulp_version_content.txt
  curl "${pulp_docker_url}" | grep pulp-docker-plugins  >> pub_pulp_version_content.txt
}

# check the pub version
get_build_installed_on_server() {
  echo $(ssh -i /root/.ssh/id_rsa -o "StrictHostKeyChecking no" root@${1} "rpm -qa | grep ${2} | sed 's/.noarch//'")
}

upgrade_pub_pulp_tools_on_server(){
  echo "Upgrading the 'rhsm-tools' and 'cdn-utils' on the pub and pulp servers"
  ssh -i /root/.ssh/id_rsa -o "StrictHostKeyChecking no" root@${1} "yum upgrade -y rhsm-tools && yum upgrade -y cdn-utils"
}

# prepare_pub_pulp_ansible(){
#  git clone  https://gitlab.infra.prod.eng.rdu2.redhat.com/yuzheng/.git
#}

initialize_ansible_related_varables(){
  pub_product_version=""
  pub_deploy=false
  pulp_for_rpm_production=""
  pulp_for_rpm_deploy=false
  pulp_for_rpm_deploy_downgrade=false
  pulp_rpm_production=""
  pulp_rpm_deploy=false
  pulp_for_docker_deploy=false
  pulp_for_docker_production=""
  pulp_docker_production=""
  pulp_docker_deploy=false
  pulp_docker_server_ansible=""
  pulp_rpm_server_ansible=""
  pub_ansible=""
  pulp_for_rpm_ansible=""
  pulp_rpm_ansible=""
  pulp_for_docker_ansible=""
  pulp_docker_ansible=""
}

# check pub related
check_and_initialize_pub() {
  # upgrade the tools first
  upgrade_pub_pulp_tools_on_server ${pub_server}
  # check the version and prepare the ansible if needed
  pub_installed=$( get_build_installed_on_server ${pub_server} pub-hub )
  echo "=== pub installed =="
  echo ${pub_installed}
  pub_product=$(  python get_pub_pulp_product_version.py ${current_dir}/pub_pulp_version_content.txt pub )
  echo "== pub production =="
  echo ${pub_product}
  if [[ ${pub_installed} =~ ${pub_product} ]]; then
    echo "== The pub installed is the same as the production, no need to update it =="
    echo "== Let always start the pub services on the pub servers"
    ssh -i /root/.ssh/id_rsa -o "StrictHostKeyChecking no" root@${pub_server} "pub enable-worker ${pub_server} --username root --password redhat"
    echo "== Done for ${pub_server}"
  else
    pub_deploy=true
      echo "== we need to update the pub version =="
      pub_product_version=$( echo ${pub_product} | cut -d "-" -f 3- | cut -d '.' -f 1-3 )
        echo "== will initialize the pub server with pub version ${pub_product_version}"
      pub_installed_version=$( echo ${pub_installed} |  cut -d "-" -f 3- | cut -d '.' -f 1-3 )
      pub_product_sub_version=$( echo ${pub_product_version} | cut -d '-' -f 2 )
      pub_product_ansible_version=$( echo ${pub_product_version} | cut -d '-' -f 1 | cut -d '-' -f 1)
      if [[ ${pub_product_sub_version} -gt 1 ]]; then
        pub_ansible="ansible-playbook -u root -i ${CI3_WORKSPACE}/inventory/pub ${CI3_WORKSPACE}/playbooks/pub/e2e/deploy-pub-e2e.yml -e pub_version=${pub_product_ansible_version} -e pub_release=${pub_product_sub_version}"
      else
        pub_ansible="ansible-playbook -u root -i ${CI3_WORKSPACE}/inventory/pub ${CI3_WORKSPACE}/playbooks/pub/e2e/deploy-pub-e2e.yml -e pub_version=${pub_product_ansible_version}"
      fi
        pub_product_version_integer=$(echo ${pub_product_version} | sed "s/[^0-9]*//g")
        pub_installed_version_integer=$(echo ${pub_installed_version} | sed "s/[^0-9]*//g" | cut -c 1-${#pub_product_version_integer})
        echo "== Compare the current installed pub version with the production version =="
        echo "== installed vs production: ${pub_installed_version_integer} vs ${pub_product_version_integer} =="
      if [[ ${pub_installed_version_integer} -gt ${pub_product_version_integer} ]]; then
        echo "== Downgrade Reminder: The installed pub is newer than production, we need to downgrade it =="
        pub_ansible="${pub_ansible} -e pub_downgrade=true"
      fi
  fi
  if [[ ${pub_deploy} == "true" ]]; then
    echo "Ansible: ${pub_ansible}"
    cd ${CI3_WORKSPACE}
	${pub_ansible}
	cd -
    echo "== Now the pub installed is: =="
    echo $( get_build_installed_on_server ${pub_server} pub-hub )
  fi
}

# check pulp-rpm related
check_and_initialize_pulp_rpm() {
  # upgrade the tools first
  upgrade_pub_pulp_tools_on_server ${pulp_rpm_server}
  # check the version and prepare the ansible if needed
  pulp_for_rpm_installed=$( get_build_installed_on_server ${pulp_rpm_server}  pulp-server )
  echo "== pulp installed on pulp-rpm server =="
  echo ${pulp_for_rpm_installed}
  pulp_for_rpm_production=$(  python get_pub_pulp_product_version.py ${current_dir}/pub_pulp_version_content.txt pulp_for_rpm )
  echo "== pulp production =="
  echo ${pulp_for_rpm_production}

  if [[ ${pulp_for_rpm_installed} =~ ${pulp_for_rpm_production} ]]; then
    echo "== The pulp server installed is the same as the pulp production, no need to update it =="
  else
    pulp_for_rpm_deploy=true
    pulp_for_rpm_production_name=$( echo ${pulp_for_rpm_production} | sed "s/-server//" )
    pulp_for_rpm_ansible=" -e pulp_build=${pulp_for_rpm_production_name}"
    pulp_for_rpm_production_integer=$(echo ${pulp_for_rpm_production} | sed "s/[^0-9]*//g")
    pulp_for_rpm_installed_integer=$(echo ${pulp_for_rpm_installed} | sed "s/[^0-9]*//g" | cut -c "1-${#pulp_for_rpm_production_integer}")
    echo "== Compare the current installed pulp_for_rpm version with the production version =="
    echo "== installed vs production: ${pulp_for_rpm_installed_integer} vs ${pulp_for_rpm_production_integer} =="
    if [[ ${pulp_for_rpm_installed_integer} -gt ${pulp_for_rpm_production_integer} ]];then
      echo "== Downgrade Reminder: The installed pulp_for_rpm is newer than production, we need to downgrade it =="
      pulp_for_rpm_ansible="${pulp_for_rpm_ansible} -e pulp_downgrade=true"
    fi
  fi

  pulp_rpm_installed=$( get_build_installed_on_server ${pulp_rpm_server} pulp-rpm-plugins)
  echo "== pulp-rpm installed on pulp-rpm server =="
  echo ${pulp_rpm_installed}
  pulp_rpm_production=$(  python get_pub_pulp_product_version.py ${current_dir}/pub_pulp_version_content.txt pulp-rpm-plugins )
  echo "== pulp-rpm production =="
  echo ${pulp_rpm_production}

  if [[ ${pulp_rpm_installed} =~ ${pulp_rpm_production} ]]; then
    echo "== The pulp-rpm  installed is the same as the pulp production, no need to update it =="
  else
    pulp_rpm_deploy=true
    pulp_rpm_production_name=$( echo ${pulp_rpm_production} | sed "s/-plugins//" )
    pulp_rpm_ansible=" -e pulp_rpm_build=${pulp_rpm_production_name}"
    pulp_rpm_production_integer=$(echo ${pulp_rpm_production} | sed "s/[^0-9]*//g")
    pulp_rpm_installed_integer=$(echo ${pulp_rpm_installed}   | sed "s/[^0-9]*//g" | cut -c "1-${#pulp_rpm_production_integer}")
    echo "== Compare the current installed pulp_rpm version with the production version =="
    echo "== installed vs production: ${pulp_rpm_installed_integer} vs ${pulp_rpm_production_integer} =="
    if [[ ${pulp_rpm_installed_integer} -gt ${pulp_rpm_production_integer} ]];then
      echo "== Downgrade Reminder: The installed pulp_rpm is newer than production, we need to downgrade it =="
      pulp_rpm_ansible="${pulp_rpm_ansible} -e pulp_downgrade=true"
    fi
  fi

  pulp_rpm_server_ansible="ansible-playbook -u root -i ${CI3_WORKSPACE}/inventory/pulp ${CI3_WORKSPACE}/playbooks/pulp/deploy-pulp-rpm-e2e.yml \
                         ${pulp_for_rpm_ansible} ${pulp_rpm_ansible}"
    if [[ ${pulp_for_rpm_deploy} == "true" ]] || [[ ${pulp_rpm_deploy} == "true" ]] ; then
      echo "== Ansible: ${pulp_rpm_server_ansible} =="
      cd ${CI3_WORKSPACE}
	  ${pulp_rpm_server_ansible}
	  cd -
      echo "== Now the pulp-rpm related builds installed are:"
      echo $( get_build_installed_on_server ${pulp_rpm_server}  pulp-server )
      echo $( get_build_installed_on_server ${pulp_rpm_server} pulp-rpm-plugins)
    fi
}
# check pulp-docker related
check_and_initialize_pulp_docker() {
    # Currently, seems we do not need to upgrade tools on pulp docker servers
  # upgrade the tools first
  # upgrade_pub_pulp_tools_on_server ${pulp_docker_server}
  # check the version and prepare the ansible if needed
  pulp_for_docker_installed=$( get_build_installed_on_server ${pulp_docker_server} ${server_password} pulp-server )
  echo "== pulp installed on pulp-docker server =="
  echo ${pulp_for_docker_installed}
  pulp_for_docker_production=$(  python get_pub_pulp_product_version.py ${current_dir}/pub_pulp_version_content.txt pulp_for_docker )
  echo "== pulp production =="
  echo ${pulp_for_docker_production}
  if [[ ${pulp_for_docker_installed} =~ ${pulp_for_docker_production} ]]; then
    echo "== The pulp server installed is the same as the pulp production, no need to update it =="
    echo "== Let always start the pulp docker services on the pulp docker servers"
    ssh -i /root/.ssh/id_rsa -o "StrictHostKeyChecking no" root@${pulp_docker_server} 'sh /root/restart.sh start'
    echo "== Done for ${pulp_docker_server}"
  else
    pulp_for_docker_deploy=true
    pulp_for_docker_ansible=" -e pulp_build=${pulp_for_docker_production}"
    pulp_for_docker_production_integer=$(echo ${pulp_for_docker_production} | sed "s/[^0-9]*//g")
    pulp_for_docker_installed_integer=$(echo ${pulp_for_docker_installed} | sed "s/[^0-9]*//g" | cut -c "1-${#pulp_for_docker_production_integer}")
    echo "== Compare the current installed pulp_for_docker version with the production pulp version =="
    echo "== installed vs production: ${pulp_for_docker_installed_integer} vs ${pulp_for_docker_production_integer} =="
    if [[ ${pulp_for_docker_installed_integer} -gt ${pulp_for_docker_production_integer} ]];then
      echo "== Downgrade Reminder: The installed pulp_for_docker is newer than production, we need to downgrade it =="
      pulp_for_docker_ansible="${pulp_for_docker_ansible} -e pulp_downgrade=true"
    fi
  fi

  pulp_docker_installed=$( get_build_installed_on_server ${pulp_docker_server} ${server_password} pulp-docker-plugins)
  echo "== pulp-docker installed on pulp-docker server =="
  echo ${pulp_docker_installed}
  pulp_docker_production=$(  python get_pub_pulp_product_version.py ${current_dir}/pub_pulp_version_content.txt pulp-docker-plugins )
  echo "== pulp-docker production =="
  echo ${pulp_docker_production}

  if [[ ${pulp_docker_installed} =~ ${pulp_docker_production} ]]; then
    echo "== The pulp-docker  installed is the same as the pulp production, no need to update it =="
  else
    pulp_docker_deploy=true
    pulp_docker_ansible=" -e pulp_docker_build=${pulp_docker_production}"
    pulp_docker_production_integer=$(echo ${pulp_docker_production} | sed "s/[^0-9]*//g")
    pulp_docker_installed_integer=$(echo ${pulp_docker_installed}   | sed "s/[^0-9]*//g" | cut -c "1-${#pulp_docker_production_integer}")
    echo "== Compare the current installed pulp_docker version with the production pulp version =="
    echo "== installed vs production: ${pulp_docker_installed_integer} vs ${pulp_docker_production_integer} =="
    if [[ ${pulp_docker_installed_integer} -gt ${pulp_docker_production_integer} ]];then
      pulp_docker_ansible="${pulp_docker_ansible} -e pulp_downgrade=true"
    fi
  fi

  pulp_docker_server_ansible="ansible-playbook -u root -i ${CI3_WORKSPACE}/inventory/pulp ${CI3_WORKSPACE}/playbooks/pulp/deploy-pulp-docker-e2e.yml \
    ${pulp_for_docker_ansible} ${pulp_docker_ansible}"
    if [[ ${pulp_docker_deploy} == "true" ]] || [[ ${pulp_for_docker_deploy} == "true" ]];then
      echo "== Ansible: ${pulp_docker_server_ansible} =="
      cd ${CI3_WORKSPACE}
      ${pulp_docker_server_ansible}
      cd -
     
      echo "== Now the pulp-docker related builds installed are: =="
      echo $( get_build_installed_on_server ${pulp_docker_server} pulp-server )
      echo $( get_build_installed_on_server ${pulp_docker_server} pulp-docker-plugins)
    fi
}

clean_running_and_free_pub_tasks() {
    free_running_tasks=$(ssh -i /root/.ssh/id_rsa -o "StrictHostKeyChecking no"  root@${pub_server} "pub list-tasks  --free --running --user errata --password errata | tr '\n' ' '")
    if [[ -z ${free_running_tasks} ]]; then
        echo "== There is no running or free tasks on the pub server"
    else
        echo "== There are some running and free tasks on the pub server, cleaning it"
        ssh -i /root/.ssh/id_rsa -o "StrictHostKeyChecking no" root@${pub_server} "pub cancel-tasks --user errata --password errata ${free_running_tasks}"
        echo "== Done for pub tasks clean"
    fi
}

prepare_and_update_private_key_for_ansible() {
  cp  /root/.ssh/id_rsa ${CI3_WORKSPACE}
  chmod 700 ${CI3_WORKSPACE}/id_rsa
  sed -i "/defaults\]/a private_key_file=${CI3_WORKSPACE}/id_rsa" ${CI3_WORKSPACE}/ansible.cfg
}
echo "== Step 1: add random user as default user =="
add_random_user_as_default_user

echo "== Step 2: install scripts env =="
install_scripts_env

echo "== Step 3: initialize ansible related variables =="
initialize_ansible_related_varables

#prepare_pub_pulp_ansible
current_dir=$( echo `pwd` )
echo "== Step 4: clean running and free pub tasks =="
clean_running_and_free_pub_tasks

echo "== Step 5: get all product versions content =="
get_all_product_versions_content

echo "== Step 6: update the ansible.cfg with the private key"
prepare_and_update_private_key_for_ansible

echo "== Step 7: check and initialize pub =="
check_and_initialize_pub

echo "== Step 8: check and initialize pulp rpm =="
check_and_initialize_pulp_rpm

echo "== Step 9: check and initialize pulp docker =="
check_and_initialize_pulp_docker
# check all service are running

