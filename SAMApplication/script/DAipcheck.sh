#!/bin/bash
echo -n "Input the auto-scaling-group-name (find in stack outputs): "
read autoscalinggroupname

for i in `aws autoscaling describe-auto-scaling-groups --auto-scaling-group-name $autoscalinggroupname | grep -i instanceid  | awk '{ print $2}' | cut -d',' -f1| sed -e 's/"//g'`
do
aws ec2 describe-instances --instance-ids $i | grep -i PublicIpAddress | awk '{ print $2 }' | head -1 | cut -d"," -f1
done;

