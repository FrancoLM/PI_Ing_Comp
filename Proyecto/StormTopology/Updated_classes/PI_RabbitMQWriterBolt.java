package org.apache.storm.starter.bolt;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import org.apache.storm.starter.spout.PI_RabbitMQSpout;
import org.apache.storm.task.OutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.base.BaseRichBolt;
import org.apache.storm.tuple.Fields;
import org.apache.storm.tuple.Tuple;
import com.rabbitmq.client.MessageProperties;

import java.io.IOException;
import java.lang.reflect.Array;
import java.util.Iterator;
import java.util.Map;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeoutException;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class PI_RabbitMQWriterBolt extends BaseRichBolt {

    private final static String QUEUE_NAME = "responses_deviceID_";
    private final static String MQTT_QUEUE_PREFIX = "mqtt-subscription-";
    private final static String QOS = "qos0";
    OutputCollector _collector;
    BlockingQueue<String> messages;
    ConnectionFactory factory;
    Connection connection;

    public PI_RabbitMQWriterBolt() {
        messages = new ArrayBlockingQueue<String>(250);

    }

    @Override
    public void prepare(Map stormConf, TopologyContext context, OutputCollector collector) {
        _collector = collector;
        factory = new ConnectionFactory();
        factory.setHost("172.31.0.31");
        // factory.setHost("10.0.0.110");
        // factory.setVirtualHost("device_vhost");
        factory.setUsername("device_user");
        factory.setPassword("tesis1234");
        factory.setPort(5672);
    }

    @Override
    public void execute(Tuple input) {
        JSONParser parser = new JSONParser();
        String message =  (String) input.getValueByField("message");
        System.out.println("input.getFields():" + input.getFields());
        System.out.println("input.getValues():" + input.getValues());
        System.out.println("input.getValue(0):" + input.getValue(0));
        System.out.println("input.getValueByField(\"message\"):" + input.getValueByField("message"));
        System.out.println("Writing to RabbitMQ queue..." + message);

        JSONObject jsonMessage = new JSONObject();

        try {
            jsonMessage = (JSONObject) parser.parse(message);
            System.out.println("Device ID is... " + jsonMessage.get("device_id"));
            Double telemetry = (Double) jsonMessage.get("telemetry");
            System.out.println("Telemetry value is... " + telemetry.toString());

            String responseQueue = QUEUE_NAME + jsonMessage.get("device_id"); // + device ID
            try {
                connection = factory.newConnection();
                Channel channel = connection.createChannel();

                // The queue to send the message to will be the sending device's queue
                // declare a durable, non-exclusive, non-autodelete queue
                channel.queueDeclare(responseQueue, true, false, false, null);
                // The routing algorithm behind a direct exchange is simple - a message goes to the queues
                // whose binding key exactly matches the routing key of the message
                channel.exchangeDeclare(jsonMessage.get("device_id").toString(), "direct");
                channel.queueBind(responseQueue, jsonMessage.get("device_id").toString(), jsonMessage.get("device_id").toString());

                // Add the binding to the queue the device listens to so it receives the messages
                channel.queueBind(MQTT_QUEUE_PREFIX + jsonMessage.get("device_id").toString() + QOS,
                        jsonMessage.get("device_id").toString(),
                        (String) jsonMessage.get("device_id").toString()
                );
                System.out.println("Calculating distance...");
                double distance = (telemetry * 463 / 2);

                // jsonMessage.put("value", telemetry);
                jsonMessage.put("distance", distance);


                // Publish message to queue
                channel.basicPublish(
                        jsonMessage.get("device_id").toString(), // exchange name
                        jsonMessage.get("device_id").toString(), // routing key
                        MessageProperties.PERSISTENT_TEXT_PLAIN,
                        jsonMessage.toString().getBytes()
                );
                System.out.println("Message published to queue: " + responseQueue.toString() +
                        ", using Routing Key: " + jsonMessage.get("device_id").toString());

                channel.close();
                connection.close();

            } catch (IOException e) {
                e.printStackTrace();
            } catch (TimeoutException e) {
                e.printStackTrace();
            }
        } catch (ParseException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        // This bolt does not need to output tuples to another node
    }
}
