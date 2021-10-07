#! /bin/bash

LOG_PREFIX='Install_Script'

function log() {
  local prefix=${LOG_PREFIX}
  local log_level=${1:-INFO}
  local msg=${2:-"Empty Msg"}
  echo "$(date +"%M-%d-%Y %H:%M:%S") [${prefix}]: ${log_level} ${msg}"
  if [[ "${log_level}" == "INFO" ]]; then
    logger -t ${prefix} -p user.info "${log_level} ${msg}"
  elif [[ "${log_level}" == "WARN" ]]; then
    logger -t ${prefix} -p user.warn "${log_level} ${msg}"
  elif [[ "${log_level}" == "ERROR" ]]; then
    logger -t ${prefix} -p user.err "${log_level} ${msg}"
  fi
}

function execute_with_logs(){
  local command_to_execute=${*}

  logs=$(eval ${command_to_execute} 2>&1)
  exit_code=${?}
  log INFO "Output of running '${command_to_execute}':"
  OLD_IFS=${IFS}
  # changing field separator so that we can read line by line in for loop
  IFS=$'\n'
  for l in ${logs}
  do
     log INFO "${l}"
  done
  IFS=${OLD_IFS}
  return ${exit_code}
}

execute_with_logs "echo 'YARN_CONTAINER_RUNTIME_TYPE=docker' | sudo tee -a /etc/environment"
execute_with_logs "echo 'YARN_CONTAINER_RUNTIME_DOCKER_IMAGE=public.ecr.aws/e0a3g4z6/causality-ensemble:latest' | sudo tee -a /etc/environment"

execute_with_logs "curl -fsSL https://get.docker.com -o get-docker.sh"
execute_with_logs "sudo sh get-docker.sh"
execute_with_logs "sudo service docker start"

execute_with_logs "sudo usermod -a -G docker sshuser"
execute_with_logs "sudo chmod 666 /var/run/docker.sock"
export PATH=/usr/local/bin:$PATH

execute_with_logs "curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'"
execute_with_logs "unzip awscliv2.zip"
execute_with_logs "sudo ./aws/install"

execute_with_logs "docker run amazoncorretto:8 java -version"
execute_with_logs "docker run public.ecr.aws/e0a3g4z6/causality-ensemble"
