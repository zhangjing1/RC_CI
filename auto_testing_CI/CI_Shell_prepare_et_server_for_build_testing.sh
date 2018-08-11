#!/bin/bash
set -eo pipefail

debug="false"
if [[ "${debug}" == "true" ]]; then
  ET_Testing_Server="et-e2e.usersys.redhat.com"
  ET_Production_Server="errata.devel.redhat.com"
  et_build_name_or_id=""
  WORKSPACE="/root/ansible/"
  tmp_dir="/home/cara/"
  source ${tmp_dir}/RC_CI/auto_testing_CI/CI_Shell_prepare_env_and_scripts.sh
  source  ${tmp_dir}/RC_CI/auto_testing_CI/CI_Shell_common_usage.sh
fi

prepare_scripts(){
  mkdir -p ${1}
  echo "===============Download the CI files under $(pwd)=========="
  wget http://github.com/testcara/RC_CI/archive/master.zip -P ${1}
  unzip ${1}/master.zip -d ${1}
  echo "==============All files had beeen Download==============="
}

run_ansible(){
  set -x
  env
  #cd ${WORKSPACE}/playbooks/errata-tool
  cd ${WORKSPACE}/playbooks
  make clean-roles
  make qe-roles
  e2e_env_workaround ${ET_Testing_Server} ${WORKSPACE}
  cd ../
  pwd
  ${1}
}

if [[ "${debug_mode}" == "true" ]]; then
  debug_useage $1 $2 $3
fi

tmp_dir="/tmp/$(($(date +'%s') + $RANDOM))"
prepare_scripts ${tmp_dir}
source ${tmp_dir}/RC_CI-master/auto_testing_CI/CI_Shell_prepare_env_and_scripts.sh
source  ${tmp_dir}/RC_CI-master/auto_testing_CI/CI_Shell_common_usage.sh
#install_scripts_env

if [[ -z "${et_build_name_or_id}" ]]; then
  echo "=== Et version is not specified. I would keep the deployed version is the product et version"
  product_raw_et_version=$(get_system_raw_version ${ET_Production_Server} | cut -d "-" -f 1)
  product_et_version=$(get_et_product_version ${ET_Production_Server})
  deployed_et_version=$(get_deployed_et_version ${ET_Testing_Server})
  echo "=== Get following versions:"
  echo "product et version: ${product_et_version}"
  echo "deployed et version: ${deployed_et_version}"
  compare_result=$(compare_version_or_id ${deployed_et_version} ${product_et_version})
  echo "compare_result: ${compare_result}"
  if [[ "${compare_result}" == "same" ]]; then
    echo "=== There is no need to deploy"
    echo "=== If the server is perf server, CI will restore the db and do db migration"
    perf_restore_db ${ET_Testing_Server}
    do_db_migration ${ET_Testing_Server}
    exit
  else
    echo "=== I am initializing the testing server with the product version"
    ansible=$(get_ansible_commands_with_product_et_version ${ET_Testing_Server} ${product_raw_et_version} ${compare_result})
    echo "${ansible}"
    run_ansible "${ansible}"
    update_setting ${ET_Testing_Server}
    restart_service ${ET_Testing_Server}
    initialize_e2e_pub_errata_xmlrpc_settings
  fi
else
  echo "=== ET version is specified, I would keep the deplyed version is the expected et version"
  deployed_et_id=$(get_deployed_et_id ${ET_Testing_Server})
  expected_et_id=$(initial_et_build_id ${et_build_name_or_id})
  echo "=== Get following versions:"
  echo "expected version: ${expected_et_id}"
  echo "deployed et version: ${deployed_et_id}"
  compare_result=$(compare_version_or_id ${expected_et_id} ${deployed_et_id})
  echo "compare_result: ${compare_result}"
  if [[ "${compare_result}" == "same" ]]; then
    echo "There is no need to deploy"
    echo "=== If the server is perf server, CI will restore the db and do db migration"
    perf_restore_db ${ET_Testing_Server}
    do_db_migration ${ET_Testing_Server}
    exit
  else
    product_raw_et_version=$(get_system_raw_version ${ET_Production_Server} | cut -d "-" -f 1)
    product_et_version=$(get_et_product_version ${ET_Production_Server})
    deployed_et_version=$(get_deployed_et_version ${ET_Testing_Server})
    echo "=== Get following versions:"
    echo "product version: ${product_et_version}"
    echo "deployed et version: ${deployed_et_version}"
    compare_result=$(compare_version_or_id ${deployed_et_version} ${product_et_version})
    echo "compare_result: ${compare_result}"
    if [[ "${compare_result}" == "same" ]]; then
      echo "=== There is no need to redeploy et as product et version"
    else
      echo "=== Before upgrade the expected version, I will initialize the testing server as et product version"
      perf_restore_db ${ET_Testing_Server}
      ansible=$(get_ansible_commands_with_product_et_version ${ET_Testing_Server} ${product_raw_et_version} ${compare_result})
      echo "${ansible}"
      run_ansible "${ansible}"
    fi
    echo "=== Upgrade to the current expected et version"
    ansible=$(get_ansible_commands_with_build_id ${ET_Testing_Server} ${expected_et_id})
    echo "${ansible}"
    run_ansible "${ansible}"
    update_setting ${ET_Testing_Server}
    restart_service ${ET_Testing_Server}
    initialize_e2e_pub_errata_xmlrpc_settings
  fi
fi
