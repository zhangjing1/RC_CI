#!/bin/bash
set -eo pipefail

debug_mode=true
debug_useage() {
  username=$1
  password=$2
  et_build_name_or_id=$3
  space='~wlin'
  parent_page=30869307
}

if [[ "${debug_mode}" == "true" ]]; then
  debug_useage $1 $2 $3
fi

source CI_Shell_prepare_env_and_scripts.sh
source CI_Shell_common_usage.sh
clean_env_mess
et_build_version=""
tmp_dir="/tmp/$(date +'%s')"
install_scripts_env
initial_et_build_version ${et_build_name_or_id}
prepare_scripts ${tmp_dir}
title="ET Testing Reports For Build ${et_build_version}"
cd ${tmp_dir}/RC_CI-master/auto_testing_CI
pwd
echo sudo python collect_all_reports_and_update_to_confluence.py "${username}" "${password}" "${et_build_version}" "${title}" "${space}" "${parent_page}"
sudo python collect_all_reports_and_update_to_confluence.py "${username}" "${password}" "${et_build_version}" "${title}" "${space}" "${parent_page}"
clean_env_mess
