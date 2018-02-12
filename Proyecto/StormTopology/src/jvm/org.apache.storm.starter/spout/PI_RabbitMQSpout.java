package org.apache.storm.starter.spout;

import com.rabbitmq.client.*;
import org.apache.storm.spout.SpoutOutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.base.BaseRichSpout;
import org.apache.storm.tuple.Fields;
import org.apache.storm.tuple.Values;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeoutException;

public class PI_RabbitMQSpout extends BaseRichSpout {

    private final static String QUEUE_NAME = "mqtt-subscription-device_queue";
    SpoutOutputCollector _collector;
    boolean _isDistributed;
    BlockingQueue<String> messages;

    public PI_RabbitMQSpout() {
        this(true);
    }

    public PI_RabbitMQSpout(boolean isDistributed) {
        _isDistributed = isDistributed;
    }

    @Override
    public void open(Map conf, TopologyContext context, SpoutOutputCollector collector) {
        _collector = collector;
        messages = new ArrayBlockingQueue<String>(250);
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("172.31.0.31");
        factory.setUsername("device_user");
        factory.setPassword("tesis1234");
        factory.setPort(5672);
        Connection connection;

        try {
            connection = factory.newConnection();
            Channel channel = connection.createChannel();

            // declare a durable, non-exclusive, non-autodelete queue
            channel.queueDeclare(QUEUE_NAME, true, false, false, null);

            Consumer consumer = new DefaultConsumer(channel) {
                @Override
                public void handleDelivery(String s, Envelope envelope, AMQP.BasicProperties basicProperties, byte[] bytes)
                        throws IOException {
                    String message = new String(bytes, "UTF-8");
                    try {
                        messages.put(message);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            };
            channel.basicConsume(QUEUE_NAME, true, consumer);

        } catch (IOException e) {
            e.printStackTrace();
        } catch (TimeoutException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void nextTuple() {
        String message;
        while ((message = messages.poll()) != null){
            System.out.println("Spout Received message: " + message);
            _collector.emit(new Values(message));
        }
    }

    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("message"));
    }
}
