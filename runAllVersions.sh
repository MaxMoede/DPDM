echo starting script..
python ./dpdm.py https://github.com/apache/apex-core.git APEXCORE https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/apexRepoHolder
python ./dpdm.py https://github.com/apache/commons-jcs.git JCS https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/JCSRepoHolder
python ./dpdm.py https://github.com/apache/commons-jelly.git JELLY https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/JellyRepoHolder
python ./dpdm.py https://github.com/apache/commons-math.git MATH https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/MathRepoHolder
python ./dpdm.py https://github.com/apache/commons-net.git NET https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/NetRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/commons-compress.git COMPRESS https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/compressRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/lucy.git LUCY https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/lucyRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/etch.git ETCH https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/etchRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/bigtop.git BIGTOP https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/bigtopRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/calcite.git CALCITE https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/calciteRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/accumulo.git ACCUMULO https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/accumuloRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/ant-ivy.git IVY https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/ivyRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/commons-pool POOL https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/poolRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/thrift THRIFT https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/thriftRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/mesos MESOS https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/mesosRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/mina DIRMINA https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/minaRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/vysper Vysper https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/vysperRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/isis ISIS https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/isisRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/jena JENA https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/jenaRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/giraph GIRAPH https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/giraphRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/groovy GROOVY https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/groovyRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/drill DRILL https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/drillRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/geronimo GERONIMO https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/geronimoRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/spark SPARK https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/sparkRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/stanbol STANBOL https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/stanbolRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/synapse SYNAPSE https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/synapseRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/tapestry-5 TAP5 https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/tapestryRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/trafficserver TS https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/trafficServerRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/hbase HBASE https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/HBaseRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/helix HELIX https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/HelixRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/pig PIG https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/PigRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/vcl VCL https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/VCLRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/velocity-engine VELOCITY https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/VelocityRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/webservices-axiom AXIOM https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/AxiomRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/xml-graphics-commons XMLCOMMONS https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/xmlRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/httpcomponents-core HTTPCORE https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/httpRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/qpid QPID https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/qpidRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/ignite IGNITE https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/igniteRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/river RIVER https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/riverRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/serf SERF https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/serfRepoHolder
python ./wait.py
python ./dpdm.py https://github.com/apache/parquet-cpp PARQUET https://issues.apache.org/jira/
python ./wait.py
mv ./repoHolder ./allDPDMTables/parquetRepoHolder
echo hi again
