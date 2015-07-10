#!/usr/bin/python
# coding: utf8

###############################################
#This is an implementatin of Weasis PACS connector in Python.
#http://www.dcm4che.org/confluence/display/WEA/Building+weasis-pacs-connector
###############################################


#Following import is for a django project. Repalce it with your DICOM Study dict 
from common.study_details import get_study_dict
#For django
from django.conf import settings
import os

weasisTemplate = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE jnlp PUBLIC "-//Sun Microsystems, Inc//DTD JNLP Descriptor 6.0//EN" "http://java.sun.com/dtd/JNLP-6.0.dtd">
  <jnlp spec="1.6+" codebase="http://localhost:8080/weasis" href="">
  <information>
    <title>Weasis</title>
    <vendor>Weasis Team</vendor>
    <description>DICOM images viewer</description>
    <description kind="short">An application to visualize and analyze DICOM images.</description>
    <description kind="one-line">DICOM images viewer</description>
    <description kind="tooltip">Weasis</description>
  </information>
  <security>
    <all-permissions />
  </security>

  <resources>
    <!-- Requires Java SE 6 update 10 release for jnlp extension without codebase (substance.jnlp) -->
    <j2se version="1.6.0_10+" href="http://java.sun.com/products/autodl/j2se" initial-heap-size="128m" max-heap-size="512m" />
    <j2se version="1.6.0_10+" initial-heap-size="128m" max-heap-size="512m" />
    <jar href="http://osirix.vital-it.ch:8089/weasis/weasis-launcher.jar" main="true" />
    <jar href="http://osirix.vital-it.ch:8089/weasis/felix.jar" />
    <!-- Optional library (Substance Look and feel, only since version 1.0.8). Requires the new Java Plug-in introduced in
      the Java SE 6 update 10 release.For previous JRE 6, substance.jnlp needs a static codebase URL -->
    <extension href="http://osirix.vital-it.ch:8089/weasis/substance.jnlp" />
    <!-- Allows to get files in pack200 compression, only since Weasis 1.1.2 -->
    <property name="jnlp.packEnabled" value="true" />
    <!-- ================================================================================================================= -->
    <!-- Security Workaround. Add prefix "jnlp.weasis" for having a fully trusted application without signing jnlp (only since
      weasis 1.2.9), http://bugs.sun.com/bugdatabase/view_bug.do?bug_id=6653241 -->
    <!-- Required parameter. Define the location of config.properties (the OSGI configuration and the list of plug-ins to install/start) -->
    <property name="jnlp.weasis.felix.config.properties" value="http://osirix.vital-it.ch:8089/weasis/conf/config.properties" />
    <!-- Optional parameter. Define the location of ext-config.properties (extend/override config.properties) -->
    <property name="jnlp.weasis.felix.extended.config.properties" value="http://osirix.vital-it.ch:8089/weasis-ext/conf/ext-config.properties" />
    <!-- Required parameter. Define the code base of Weasis for the JNLP -->
    <property name="jnlp.weasis.weasis.codebase.url" value="http://osirix.vital-it.ch:8089/weasis" />
    <!-- Optional parameter. Define the code base ext of Weasis for the JNLP -->
    <property name="jnlp.weasis.weasis.codebase.ext.url" value="http://osirix.vital-it.ch:8089/weasis-ext" />
    <!-- Required parameter. OSGI console parameter -->
    <property name="jnlp.weasis.gosh.args" value="-sc telnetd -p 17179 start" />
    <!-- Optional parameter. Allows to have the Weasis menu bar in the top bar on Mac OS X (works only with the native Aqua
      look and feel) -->
    <property name="jnlp.weasis.apple.laf.useScreenMenuBar" value="true" />
    <!-- Optional parameter. Allows to get plug-ins translations -->
    <property name="jnlp.weasis.weasis.i18n" value="http://osirix.vital-it.ch:8089/weasis/../weasis-i18n" />
    <!-- Optional Weasis Documentation -->
    <!-- <property name="jnlp.weasis.weasis.help.url" value="${cdb}/../weasis-doc" /> -->
  </resources>

  <application-desc main-class="org.weasis.launcher.WebstartLauncher">
  <argument>$dicom:get -w """

weasisTemplateClose = """"{}{}"</argument>
  </application-desc>
  </jnlp>"""

xmlTemplate = """<?xml version="1.0" encoding="utf-8" ?><wado_query xmlns= "http://www.weasis.org/xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" wadoURL="http://beta.radpanel.com/utils/wado/" requireOnlySOPInstanceUID="false" additionnalParameters="" overrideDicomTagsList="" ><Patient PatientID="{PatientID}" PatientName="{PatientName}" PatientBirthDate="{PatientBirthDate}"><Study StudyInstanceUID="{StudyInstanceUID}" StudyDescription="{StudyDescription}" StudyDate="{StudyDate}" StudyTime="{StudyTime}" >"""
xmlTemplateClose = """</Study></Patient></wado_query>"""
seriesTemplate = """<Series SeriesInstanceUID="{SeriesInstanceUID}" SeriesDescription="{SeriesDescription}" SeriesNumber="{SeriesNumber}" Modality="{Modality}" >"""
seriesTemplateClose = """</Series>"""
instanceTemplate = """<Instance SOPInstanceUID="{SOPInstanceUID}" InstanceNumber="{InstanceNumber}" />"""

instanceDownloadTemplate = """<Instance SOPInstanceUID="{SOPInstanceUID}" InstanceNumber="{InstanceNumber}" DirectDownloadFile={DirectDownloadFile}/>"""

module_dir = os.path.dirname(__file__)  # get current directory
file_path = os.path.join(module_dir, 'viewer.jnlp')


def get_wado_xml(instance_uid):
    d = get_study_dict(instance_uid)
    wadoXML = xmlTemplate.format(PatientID=d['patient']['PatientID'],
                                 PatientName=d['patient']['PatientName'],
                                 PatientBirthDate=d['patient']['PatientBirthDate'],
                                 StudyInstanceUID=d['study']['StudyInstanceUID'],
                                 StudyDescription=d['study']['StudyDescription'],
                                 StudyDate=d['study']['StudyDate'],
                                 StudyTime=d['study']['StudyTime'])
    all_series_xml = ""
    for sr in d['series']:
        this_series = seriesTemplate.format(SeriesInstanceUID=sr['SeriesInstanceUID'],
                                            SeriesDescription=sr['SeriesDescription'],
                                            SeriesNumber=sr['SeriesNumber'],
                                            Modality=sr['Modality'])
        all_instances_xml = ""
        for i in sr['images']:
            this_instance = instanceTemplate.format(SOPInstanceUID=i['SOPInstanceUID'],
                                                    InstanceNumber=i['InstanceNumber'])
            all_instances_xml = all_instances_xml + this_instance
        this_series_xml = """{}{}{}""".format(this_series, all_instances_xml, seriesTemplateClose)
        all_series_xml = all_series_xml + this_series_xml
    final_xml = """{}{}{}""".format(wadoXML, all_series_xml, xmlTemplateClose)
    return final_xml


def get_study_jnlp(instance_uid):
    close_url = weasisTemplateClose.format(settings.WADO_XML_URL, instance_uid)
    return_jnlp = weasisTemplate + close_url
    return return_jnlp