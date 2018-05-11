initial_et_build_version(){
  if [[ ${1} =~ "-" ]]; then
    echo "=== ET build name has been provided: ${et_build_name} =="
    et_build_version=$( echo ${1} | cut -d '-' -f 2| cut -d '.' -f 2 )
  else
    echo "=== ET build id is provided =="
    et_build_version=${1}
  fi
  echo ${et_build_version}
}
