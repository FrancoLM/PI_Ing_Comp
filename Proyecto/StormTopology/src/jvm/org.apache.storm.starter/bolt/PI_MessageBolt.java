package org.apache.storm.starter.bolt;

import org.apache.storm.task.OutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.base.BaseRichBolt;
import org.apache.storm.tuple.Fields;
import org.apache.storm.tuple.Tuple;
import org.apache.storm.tuple.Values;

import java.io.FileWriter;
import java.io.IOException;
import java.io.OutputStream;
import java.util.Map;

public class PI_MessageBolt extends BaseRichBolt {

    OutputCollector _collector;

    @Override
    public void prepare(Map stormConf, TopologyContext context, OutputCollector collector) {
        _collector = collector;
    }

    @Override
    public void execute(Tuple input) {
        String message = (String) input.getValueByField("message");
        System.out.println("------------->>>>:" + message);
        OutputStream ostream;
        try {
            System.out.println("Writing output to a file...");
            FileWriter out = new FileWriter("pi_example.txt", true);
            out.write(message);
            out.close();
            _collector.emit(input, new Values(message));
            _collector.ack(input);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("message"));
    }
}
