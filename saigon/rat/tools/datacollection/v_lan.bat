echo "Validate Ruckus AP's response Tr98 xml file agains Ruckus response schema"
echo "schema file is perfdataresp_schema.xsd"
echo "xml file is data/ruckus_lan.xml"

rem
rem java -jar validateRuckusTr98.jar perfdataresp_schema.xsd data/ruckus_lan.xml
rem or
rem java -jar attAp.jar m=validate s=perfdataresp_schema.xsd x=data/ruckus_lan.xml
rem

java -jar attAp.jar m=v s=perfdataresp_schema.xsd x=data/ruckus_lan.xml

