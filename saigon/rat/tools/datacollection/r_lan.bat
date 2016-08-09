echo "The command file is at pf/ruckus_lan.prof"
echo "The result file is at data directory:"
echo "   data/ruckus_lan.json, data/ruckus_lan.xml
echo "the xml will be validated by perfdataresp_schema.xsd"
echo "if you want to index the json/xml file on each run,"
echo "use the step=<number> to index the result. For example step=2"
echo "create result files as:"
echo "   data/ruckus_lan_2.json and data/ruckus_lan_2.xml"

rem java -jar attAp.jar cmd=ruckus_lan s=perfdataresp_schema.xsd step=1
rem java -jar attAp.jar cmd=ruckus_lan s=perfdataresp_schema.xsd step=2
rem java -jar attAp.jar cmd=ruckus_lan s=perfdataresp_schema.xsd step=3

java -jar attAp.jar cmd=ruckus_lan s=perfdataresp_schema.xsd
 
