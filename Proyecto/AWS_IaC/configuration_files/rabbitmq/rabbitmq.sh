#!/usr/bin/env bash

echo ---------- SETUP
cd /opt

echo ---------- Installing RabbitMQ...
cat <<EOF > /etc/apt/sources.list.d/rabbitmq.list
deb http://www.rabbitmq.com/debian/ testing main
EOF

curl https://www.rabbitmq.com/rabbitmq-release-signing-key.asc -o /tmp/rabbitmq-release-signing-key.asc
apt-key add /tmp/rabbitmq-release-signing-key.asc
rm /tmp/rabbitmq-release-signing-key.asc

apt-get -qy update
apt-get -qy install rabbitmq-server
echo ---------- RabbitMQ installation finished

echo ----- Enabling MQTT
rabbitmq-plugins enable rabbitmq_mqtt
echo ----- MQTT enabled


echo ----- Enabling management console...
rabbitmq-plugins enable rabbitmq_management

echo ----- Creating admin user...
rabbitmqctl add_user admin tesis1234
rabbitmqctl set_user_tags admin administrator
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"

echo ----- Admin created!

echo ----- Copying RabbitMQ administrative tool
wget http://127.0.0.1:15672/cli/rabbitmqadmin
chmod +x rabbitmqadmin
# mv rabbitmqadmin /etc/rabbitmq

echo ----- creating  \'device_user\': user for device communication
rabbitmqctl add_user device_user tesis1234
rabbitmqctl set_user_tags device_user administrator


echo ----- setting permission for \'device_user\'
rabbitmqctl set_permissions -p / device_user ".*" ".*" ".*"

echo ----- Restarting server...
/etc/init.d/rabbitmq-server restart

./rabbitmqadmin declare exchange name=device_exchange type=topic -u device_user -p tesis1234

echo ----- Creating queue...
./rabbitmqadmin declare queue name=mqtt-subscription-device_queue durable=true -u device_user -p tesis1234

echo ----- Declare binding and routing key...
# destination should be the automatically-created queue
./rabbitmqadmin declare binding source="amq.topic" destination_type="queue" destination="mqtt-subscription-device_queue" routing_key="amq.topic.send.telemetry" -u device_user -p tesis1234
