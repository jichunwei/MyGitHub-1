There are two jar files you can use to retrieve AP stats through TR098.

    attAp.jar
    validateRuckusTr98.jar (can be replaced by attAp.jar using m=v option)

To run this program, make sure the schema file is at this directory,
the property file (instuct which AP and what to retrieve) at pf directory
and the output files will be at directory data.

Example 1: Run profile pf/ruckus_all.prop
           output files are data/ruckus_all.xml and data/ruckus_all.json

    java -jar attAp.jar cmd=ruckus_all

Example 2: run profile pf/ruckus_lan.prop and validated by perfdataresp_schema.xsd
           output files are data/ruckus_lan.xml and data/ruckus_lan.xml

    java -jar attAp.jar cmd=ruckus_lan s=perfdataresp_schema.xsd

Example 3: Same as example 2, but suffixed with step number.
           if step=1, its output files are:
           
                output files are data/ruckus_lan_1.xml and data/ruckus_lan_1.xml

    java -jar attAp.jar cmd=ruckus_lan s=perfdataresp_schema.xsd step=1
    java -jar attAp.jar cmd=ruckus_lan s=perfdataresp_schema.xsd step=2
    java -jar attAp.jar cmd=ruckus_lan s=perfdataresp_schema.xsd step=3

Example 4: validate a response file against our schema

    # Use
    #
    #   java -jar attAp.jar m=v s=perfdataresp_schema.xsd x=data/ruckus_lan.xml
    #
    # or
 
    java -jar validateRuckusTr98.jar perfdataresp_schema.xsd data/ruckus_lan.xml

