#!/bin/bash

echo ---------- SETUP
cd /opt

echo ----- Copying installation files...
aws s3 cp s3://tesis.project.files/java/jdk-8u111-linux-x64.rpm /tmp --region sa-east-1

aws s3 cp s3://tesis.project.files/nimbus/apache-storm-1.0.2.tar.gz /tmp --region sa-east-1

aws s3 cp s3://tesis.project.files/nimbus/supervisord_nimbus_process.conf /tmp --region sa-east-1
aws s3 cp s3://tesis.project.files/nimbus/supervisord_ui_process.conf /tmp --region sa-east-1

aws s3 cp s3://tesis.project.files/nimbus/storm.yaml /tmp --region sa-east-1

aws s3 cp s3://tesis.project.files/supervisord/supervisord /tmp --region sa-east-1
aws s3 cp s3://tesis.project.files/supervisord/supervisord.conf /tmp --region sa-east-1


echo ----- Installing Package JAVA...

sudo rpm -ivh /tmp/jdk-8u111-linux-x64.rpm
echo ----- Installation of JAVA finished!

echo ----- Creating group storm...
# sudo groupadd storm
# sudo useradd --gid storm --home-dir /home/storm --create-home --shell /bin/bash storm

sudo mkdir /opt/apache-storm
sudo mkdir /opt/apache-storm/stormstate

echo ----- Extracting Storm zip...
sudo tar -xzf  /tmp/apache-storm-1.0.2.tar.gz -C /opt/apache-storm/

echo ----- Installing Storm...

sudo ln -s /opt/apache-storm/apache-storm-1.0.2 /storm

sudo mkdir /etc/storm
sudo chown ec2-user:ec2-user /etc/storm/
# sudo chown storm:storm /etc/storm/

echo ----- Copying storm.yaml...
sudo \cp /tmp/storm.yaml /storm/conf/
sudo sed -i 's/storm.local.hostname: \"<local.ip.value>\"/storm.local.hostname: \"172.31.1.101\"/g' /storm/conf/storm.yaml

sudo chown -R ec2-user:ec2-user /storm/
# sudo chown -R storm:storm /storm/

sudo mkdir /var/log/storm
sudo chown -R ec2-user:ec2-user /var/log/storm/
# sudo chown storm:storm /var/log/storm/

echo ----- Copying complete!
echo ----- Finished nimbus startup configuration...

echo ----- Installing SUPERVISORD and dependencies...
sudo pip install supervisor

echo ---------- Creating supervisord configuration file...

# \echo_supervisord_conf >> /tmp/supervisord.conf
sudo rm -f /etc/supervisord.conf
sudo \cp /tmp/supervisord.conf /etc/supervisord.conf
sudo sed -i 's/;\[inet_http_server\]*/\[inet_http_server\]/g' /etc/supervisord.conf
# sudo sed -i 's/;port=127.0.0.1:9001*/port=\*:9001/g' /etc/supervisord.conf
sudo sed -i 's/;port=0.0.0.0:9001*/port=0.0.0.0:9001/g' /etc/supervisord.conf

echo ---------- File created!
echo ----- Adding processes to supervisord configuration file...

# cat /tmp/supervisord_nimbus_process.conf >> /etc/supervisord.conf
# cat /tmp/supervisord_ui_process.conf >> /etc/supervisord.conf
sudo sh -c "cat /tmp/supervisord_nimbus_process.conf >> /etc/supervisord.conf"
sudo sh -c "cat /tmp/supervisord_ui_process.conf >> /etc/supervisord.conf"

# echo ----- Program added!
# echo ----- Adding process to supervisord configuration file...

# cat /tmp/supervisord_supervisor_process.conf >> /etc/supervisord.conf
# sudo sh -c "cat /tmp/supervisord_supervisor_process.conf >> /etc/supervisord.conf"

echo ----- Programs added!

echo ----- Adding IP to /etc/hosts
sudo sh -c "echo 172.31.1.101 ip-172-31-1-101 ip-172-31-1-101 >> /etc/hosts"

echo ----- Program added!
echo ---------- Adding supervisord to startup and running it...

sudo rm -f /etc/rc.d/init.d/supervisord
sudo \cp /tmp/supervisord /etc/rc.d/init.d/supervisord
sudo chmod a+x /etc/rc.d/init.d/supervisord

supervisord -c /etc/supervisord.conf

sudo chown ec2-user:ec2-user /tmp/supervisor.sock
sudo chown ec2-user:ec2-user /tmp/supervisord.log

echo ---------- Finished supervisord startup configuration...
echo ---------- Installation of STORM NIMBUS finished!
echo ----- Installation of SUPERVISORD finished!

echo ----- Make supervisord to start after reboot

sudo chkconfig --add supervisord
sudo chkconfig supervisord on

echo ----- Start SUPERVISORD

sudo service supervisord restart

echo ----- Waiting 3 minutes before submitting topology
sudo sleep 3m

echo ----- Installing Topology

aws s3 cp s3://tesis.project.files/topology/storm-starter-2.0.0-SNAPSHOT.jar /home/ec2-user --region sa-east-1
/storm/bin/storm jar /home/ec2-user/storm-starter-2.0.0-SNAPSHOT.jar org.apache.storm.starter.PI_Topology production-topology remote
