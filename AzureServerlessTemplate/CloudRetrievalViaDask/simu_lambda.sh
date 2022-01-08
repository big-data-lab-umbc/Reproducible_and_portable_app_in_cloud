#!/bin/bash

vm_num=1
vm_price=2.35

command_path='./reproduce/reproduce_command.sh'
parameter_path='./reproduce/pipeline_para.json'

start_time="$(date -u +%s.%N)"

scp -pr -C -o "StrictHostKeyChecking no" $command_path azureuser@$vmssIP:/home/azureuser/command.sh
ssh -i ./ssh/id_rsa -o "StrictHostKeyChecking no" azureuser@$vmssIP "/bin/bash /home/azureuser/command.sh"

end_time="$(date -u +%s.%N)"
elapsed=$(echo "($end_time - $start_time)/3600" | bc)

ssh -i ./ssh/id_rsa -o "StrictHostKeyChecking no" azureuser@$vmssIP "az storage blob upload --account-name $account_name --account-key $key -f /home/azureuser/result.txt -c reproducibility-log/$start_time -n result.txt"

az storage blob upload --account-name $account_name --account-key $key -f $command_path -c reproducibility-log/$start_time -n command.sh
az storage blob upload --account-name $account_name --account-key $key -f $parameter_path -c reproducibility-log/$start_time -n parameter.json

Budgetary_cost=$(echo "$vm_price * $vm_num" | bc)
Performance_price_ratio=$(echo "$Budgetary_cost * $elapsed" | bc)

record_json="{\"command_line\":\"reproducibility-log/$start_time/command.sh\", \"budgetary_cost\":$Budgetary_cost, \"execution_time\":$elapsed, \"performance_price_ratio\":$Performance_price_ratio, \"source_data\":\"https://causalityncerxyroxb2sg.blob.core.windows.net/reproducibility-log/$start_time\", \"source_data_version\":null, \"program_result\":\"https://causalityncerxyroxb2sg.blob.core.windows.net/reproducibility-log/$start_time/result.txt\", \"program_result_version\":null, \"execution_history\":\"https://causalityncerxyroxb2sg.blob.core.windows.net/reproducibility-log/$start_time\"}"
echo $record_json | tee -a ./$start_time.json
az storage blob upload --account-name $account_name --account-key $key -f ./$start_time.json -c test -n $start_time.json
rm ./$start_time.json
