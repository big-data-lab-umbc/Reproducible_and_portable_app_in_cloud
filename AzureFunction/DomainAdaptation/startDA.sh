#!/bin/bash

ip=<$your_VM_ip>
account_name='causalityncerxyroxb2sg'
key='<$AccountKey_in_your_StrongAccount_AccessKeys>'

vm_num=<$your_VM_number>
vm_price=<$your_VM_price>

command_path='./command.sh'
parameter_path='./parameter.json'





start_time="$(date -u +%s.%N)"

scp -pr -C -o "StrictHostKeyChecking no" $command_path azureuser@$ip:/home/azureuser/command.sh
ssh -i ./ssh/id_rsa -o "StrictHostKeyChecking no" azureuser@$ip "/bin/bash /home/azureuser/command.sh"

end_time="$(date -u +%s.%N)"
elapsed=$(echo "$end_time - $start_time" | bc)

ssh -i ./ssh/id_rsa -o "StrictHostKeyChecking no" azureuser@$ip "az storage blob upload --account-name $account_name --account-key $key -f /home/azureuser/result.txt -c reproducibility-log/$start_time -n result.txt"

az storage blob upload --account-name $account_name --account-key $key -f $command_path -c reproducibility-log/$start_time -n command.sh
az storage blob upload --account-name $account_name --account-key $key -f $parameter_path -c reproducibility-log/$start_time -n parameter.json

Budgetary_cost=$(echo "$vm_price * $vm_num" | bc)
Performance_price_ratio=$(echo "$Budgetary_cost * $elapsed" | bc)

record_json="{\"command_line\":\"command_line\", \"budgetary_cost\":$Budgetary_cost, \"execution_time\":$elapsed, \"performance_price_ratio\":$Performance_price_ratio, \"source_data\":\"https://causalityncerxyroxb2sg.blob.core.windows.net/reproducibility-log/$start_time/command.sh\", \"source_data_verion\":null, \"program_result\":\"https://causalityncerxyroxb2sg.blob.core.windows.net/reproducibility-log/$start_time/result.txt\", \"program_result_version\":null, \"reproducibility_config\":\"https://causalityncerxyroxb2sg.blob.core.windows.net/reproducibility-log/$start_time/parameter.json\", \"reproducibility_config_version\":null}"
echo $record_json | tee -a ./$start_time.json
az storage blob upload --account-name $account_name --account-key $key -f ./$start_time.json -c test -n $start_time.json
rm ./$start_time.json