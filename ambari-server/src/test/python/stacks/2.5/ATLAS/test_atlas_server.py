#!/usr/bin/env python

'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from stacks.utils.RMFTestCase import *
from mock.mock import MagicMock, call, patch

from only_for_platform import not_for_platform, PLATFORM_WINDOWS

@not_for_platform(PLATFORM_WINDOWS)
class TestAtlasServer(RMFTestCase):
  COMMON_SERVICES_PACKAGE_DIR = "ATLAS/0.1.0.2.3/package"
  STACK_VERSION = "2.5"

  def configureResourcesCalled(self):
    # Both server and client
    self.assertResourceCalled('Directory', '/etc/atlas/conf',
                              owner='atlas',
                              group='hadoop',
                              create_parents = True,
                              cd_access='a',
                              mode=0755
    )
    # Pid dir
    self.assertResourceCalled('Directory', '/var/run/atlas',
                              owner='atlas',
                              group='hadoop',
                              create_parents = True,
                              cd_access='a',
                              mode=0755
    )
    self.assertResourceCalled('Directory', '/etc/atlas/conf/solr',
                              owner='atlas',
                              group='hadoop',
                              create_parents = True,
                              cd_access='a',
                              mode=0755,
                              recursive_ownership = True
    )
    # Log dir
    self.assertResourceCalled('Directory', '/var/log/atlas',
                              owner='atlas',
                              group='hadoop',
                              create_parents = True,
                              cd_access='a',
                              mode=0755
    )
    # Data dir
    self.assertResourceCalled('Directory', '/usr/hdp/current/atlas-server/data',
                              owner='atlas',
                              group='hadoop',
                              create_parents = True,
                              cd_access='a',
                              mode=0644
    )
    # Expanded war dir
    self.assertResourceCalled('Directory', '/usr/hdp/current/atlas-server/server/webapp',
                              owner='atlas',
                              group='hadoop',
                              create_parents = True,
                              cd_access='a',
                              mode=0644
    )
    self.assertResourceCalled('File', '/usr/hdp/current/atlas-server/server/webapp/atlas.war',
                              content = StaticFile('/usr/hdp/current/atlas-server/server/webapp/atlas.war'),
    )
    host_name = u"c6401.ambari.apache.org"
    app_props =  dict(self.getConfig()['configurations'][
                       'application-properties'])
    app_props['atlas.http.authentication.kerberos.name.rules'] = ' \\ \n'.join(app_props['atlas.http.authentication.kerberos.name.rules'].splitlines())
    app_props['atlas.server.bind.address'] = host_name
    metadata_protocol = "https" if app_props["atlas.enableTLS"] is True else "http"
    metadata_port = app_props["atlas.server.https.port"] if metadata_protocol == "https" else app_props["atlas.server.http.port"]
    app_props["atlas.rest.address"] = u'%s://%s:%s' % (metadata_protocol, host_name, metadata_port)
    app_props["atlas.server.ids"] = "id1"
    app_props["atlas.server.address.id1"] = u"%s:%s" % (host_name, metadata_port)
    app_props["atlas.server.ha.enabled"] = "false"

    self.assertResourceCalled('File', '/etc/atlas/conf/atlas-log4j.xml',
                          content=InlineTemplate(
                            self.getConfig()['configurations'][
                              'atlas-log4j']['content']),
                          owner='atlas',
                          group='hadoop',
                          mode=0644,
    )
    self.assertResourceCalled('File', '/etc/atlas/conf/atlas-env.sh',
                              content=InlineTemplate(
                                  self.getConfig()['configurations'][
                                    'atlas-env']['content']),
                              owner='atlas',
                              group='hadoop',
                              mode=0755,
    )
    self.assertResourceCalled('File', '/etc/atlas/conf/solr/solrconfig.xml',
                              content=InlineTemplate(
                                  self.getConfig()['configurations'][
                                    'atlas-solrconfig']['content']),
                              owner='atlas',
                              group='hadoop',
                              mode=0644,
    )
    # application.properties file
    self.assertResourceCalled('PropertiesFile',
                              '/etc/atlas/conf/atlas-application.properties',
                              properties=app_props,
                              owner=u'atlas',
                              group=u'hadoop',
                              mode=0644,
                              )
    self.assertResourceCalled('Directory', '/var/log/ambari-infra-solr-client',
                              create_parents=True,
                              cd_access='a',
                              mode=0755
    )
    self.assertResourceCalled('Directory', '/usr/lib/ambari-infra-solr-client',
                              create_parents = True,
                              recursive_ownership = True,
                              cd_access='a',
                              mode=0755
    )
    self.assertResourceCalled('File', '/usr/lib/ambari-infra-solr-client/solrCloudCli.sh',
                              content=StaticFile('/usr/lib/ambari-infra-solr-client/solrCloudCli.sh'),
                              mode=0755
    )
    self.assertResourceCalled('File', '/usr/lib/ambari-infra-solr-client/log4j.properties',
                              content=InlineTemplate(self.getConfig()['configurations'][
                                                       'infra-solr-client-log4j']['content']),
                              mode=0644,
    )
    self.assertResourceCalled('File', '/var/log/ambari-infra-solr-client/solr-client.log',
                              mode=0664,
                              content = ''
    )

    self.assertResourceCalledRegexp('^Execute$', '^ambari-sudo.sh JAVA_HOME=/usr/jdk64/jdk1.7.0_45 /usr/lib/ambari-infra-solr-client/solrCloudCli.sh --zookeeper-connect-string c6401.ambari.apache.org:2181 --znode /infra-solr --check-znode --retry 5 --interval 10')
    self.assertResourceCalledRegexp('^Execute$', '^ambari-sudo.sh JAVA_HOME=/usr/jdk64/jdk1.7.0_45 /usr/lib/ambari-infra-solr-client/solrCloudCli.sh --zookeeper-connect-string c6401.ambari.apache.org:2181/infra-solr --download-config --config-dir /tmp/solr_config_atlas_configs_0.[0-9]* --config-set atlas_configs --retry 30 --interval 5')
    self.assertResourceCalledRegexp('^File$', '^/tmp/solr_config_atlas_configs_0.[0-9]*',
                                    content=InlineTemplate(self.getConfig()['configurations']['atlas-solrconfig']['content']),
                                    only_if='test -d /tmp/solr_config_atlas_configs_0.[0-9]*')
    self.assertResourceCalledRegexp('^Execute$', '^ambari-sudo.sh JAVA_HOME=/usr/jdk64/jdk1.7.0_45 /usr/lib/ambari-infra-solr-client/solrCloudCli.sh --zookeeper-connect-string c6401.ambari.apache.org:2181/infra-solr --upload-config --config-dir /tmp/solr_config_atlas_configs_0.[0-9]* --config-set atlas_configs --retry 30 --interval 5',
                                    only_if='test -d /tmp/solr_config_atlas_configs_0.[0-9]*')
    self.assertResourceCalledRegexp('^Execute$', '^ambari-sudo.sh JAVA_HOME=/usr/jdk64/jdk1.7.0_45 /usr/lib/ambari-infra-solr-client/solrCloudCli.sh --zookeeper-connect-string c6401.ambari.apache.org:2181/infra-solr --upload-config --config-dir /etc/atlas/conf/solr --config-set atlas_configs --retry 30 --interval 5',
                                    not_if='test -d /tmp/solr_config_atlas_configs_0.[0-9]*')
    self.assertResourceCalledRegexp('^Directory$', '^/tmp/solr_config_atlas_configs_0.[0-9]*',
                                    action=['delete'],
                                    create_parents=True)
    self.assertResourceCalledRegexp('^Execute$', '^ambari-sudo.sh JAVA_HOME=/usr/jdk64/jdk1.7.0_45 /usr/lib/ambari-infra-solr-client/solrCloudCli.sh --zookeeper-connect-string c6401.ambari.apache.org:2181/infra-solr --create-collection --collection vertex_index --config-set atlas_configs --shards 1 --replication 1 --max-shards 1 --retry 5 --interval 10')
    self.assertResourceCalledRegexp('^Execute$', '^ambari-sudo.sh JAVA_HOME=/usr/jdk64/jdk1.7.0_45 /usr/lib/ambari-infra-solr-client/solrCloudCli.sh --zookeeper-connect-string c6401.ambari.apache.org:2181/infra-solr --create-collection --collection edge_index --config-set atlas_configs --shards 1 --replication 1 --max-shards 1 --retry 5 --interval 10')
    self.assertResourceCalledRegexp('^Execute$', '^ambari-sudo.sh JAVA_HOME=/usr/jdk64/jdk1.7.0_45 /usr/lib/ambari-infra-solr-client/solrCloudCli.sh --zookeeper-connect-string c6401.ambari.apache.org:2181/infra-solr --create-collection --collection fulltext_index --config-set atlas_configs --shards 1 --replication 1 --max-shards 1 --retry 5 --interval 10')


  def test_configure_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/metadata_server.py",
                       classname = "MetadataServer",
                       command = "configure",
                       config_file="default.json",
                       stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
                       )

    self.configureResourcesCalled()

    self.assertResourceCalled('File', '/tmp/atlas_hbase_setup.rb',
                              owner = "hbase",
                              group = "hadoop",
                              content=Template("atlas_hbase_setup.rb.j2"))

    self.assertResourceCalled('File', '/etc/atlas/conf/hdfs-site.xml',action = ['delete'],)

    self.assertNoMoreResources()

  @patch("resource_management.libraries.functions.security_commons.build_expectations")
  @patch("resource_management.libraries.functions.security_commons.get_params_from_filesystem")
  @patch("resource_management.libraries.functions.security_commons.validate_security_config_properties")
  @patch("resource_management.libraries.functions.security_commons.cached_kinit_executor")
  @patch("resource_management.libraries.script.Script.put_structured_out")
  def test_security_status(self, put_structured_out_mock, cached_kinit_executor_mock, validate_security_config_mock, get_params_mock, build_exp_mock):

    security_params = {
      'atlas-application': {
        'atlas.authentication.keytab': '/etc/security/keytabs/atlas.service.keytab',
        'atlas.authentication.method.file': 'true',
        'atlas.authentication.method.kerberos': 'true',
        'atlas.authentication.method.kerberos.keytab': '/etc/security/keytabs/spnego.service.keytab',
        'atlas.authentication.method.kerberos.principal': 'HTTP/_HOST@EXAMPLE.COM',
        'atlas.authentication.principal': 'atlas/_HOST@EXAMPLE.COM'
      }
    }
    result_issues = []
    props_value_check = {'atlas.authentication.method.kerberos': 'true',
                         'atlas.solr.kerberos.enable': 'true'}
    props_empty_check = ['atlas.authentication.principal',
                         'atlas.authentication.keytab',
                         'atlas.authentication.method.kerberos.principal',
                         'atlas.authentication.method.kerberos.keytab']
    props_read_check = ['atlas.authentication.keytab',
                        'atlas.authentication.method.kerberos.keytab']

    get_params_mock.return_value = security_params
    validate_security_config_mock.return_value = result_issues

    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/metadata_server.py",
                       classname = "MetadataServer",
                       command = "security_status",
                       config_file="default.json",
                       stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    build_exp_mock.assert_called_with('atlas-application', props_value_check, props_empty_check, props_read_check)
    put_structured_out_mock.assert_called_with({"securityState": "SECURED_KERBEROS"})

    self.assertNoMoreResources()
