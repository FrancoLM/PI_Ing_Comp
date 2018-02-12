package org.apache.storm.starter;

import org.apache.storm.Config;
import org.apache.storm.LocalCluster;
import org.apache.storm.StormSubmitter;
import org.apache.storm.starter.bolt.PI_MessageBolt;
import org.apache.storm.starter.bolt.PI_RabbitMQWriterBolt;
import org.apache.storm.starter.spout.PI_RabbitMQSpout;
import org.apache.storm.topology.TopologyBuilder;
import org.apache.storm.utils.Utils;

/**
 * Created by flmartin on 28/11/2016.
 */
public class PI_Topology {
    public static void main(String[] args) throws Exception{
        TopologyBuilder builder = new TopologyBuilder();

        builder.setSpout("spout", new PI_RabbitMQSpout(), 1);
        builder.setBolt("bolt", new PI_MessageBolt(), 1).shuffleGrouping("spout");
        builder.setBolt("writer", new PI_RabbitMQWriterBolt(), 1).shuffleGrouping("bolt");

        Config config = new Config();
        config.setDebug(true);

        if (args != null && args.length > 0) {
            config.setNumWorkers(2);
            StormSubmitter.submitTopologyWithProgressBar(args[0], config, builder.createTopology());
        }
        else {
            LocalCluster cluster = new LocalCluster();
            cluster.submitTopology("test", config, builder.createTopology());
            Utils.sleep(20000);
            cluster.killTopology("test");
            cluster.shutdown();
        }

    }
}
