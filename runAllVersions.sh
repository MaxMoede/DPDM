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
echo hi again
