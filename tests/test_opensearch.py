# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
from .common import BaseTest


class OpensearchDomain(BaseTest):

    def test_opensearch_domain_tag(self):
        session_factory = self.replay_flight_data('test_opensearch_domain_tag')
        p = self.load_policy(
            {
                'name': 'test-opensearch-tag',
                'resource': 'opensearch-domain',
                'filters': [
                    {
                        'tag:foo': 'absent',
                    }
                ],
                'actions': [
                    {
                        'type': 'tag',
                        'tags': {'foo': 'bar'}
                    }
                ]
            }, session_factory=session_factory
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        client = session_factory().client('opensearch')
        tags = client.list_tags(ARN=resources[0]["ARN"])['TagList']
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags, [{'Key': 'foo', 'Value': 'bar'}])


    def test_opensearch_domain_remove_tag(self):
        session_factory = self.replay_flight_data('test_opensearch_domain_remove_tag')
        p = self.load_policy(
            {
                'name': 'test-opensearch-remove-tag',
                'resource': 'opensearch-domain',
                'filters': [
                    {
                        'tag:foo': 'present',
                    }
                ],
                'actions': [
                    {
                        'type': 'remove-tag',
                        'tags': ['foo']
                    }
                ]
            }, session_factory=session_factory
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        client = session_factory().client('opensearch')
        tags = client.list_tags(ARN=resources[0]['ARN'])['TagList']
        self.assertEqual(len(tags), 0)

    def test_opensearch_domain_delete(self):
        session_factory = self.replay_flight_data('test_opensearch_domain_delete')
        p = self.load_policy(
            {
                'name': 'test-opensearch-delete',
                'resource': 'opensearch-domain',
                'filters': [{'DomainName': 'test'}],
                'actions': [{'type': 'delete'}]
            },
            session_factory=session_factory
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        client = session_factory().client('opensearch')
        domains = client.list_domain_names()['DomainNames']
        self.assertEqual(len(domains), 0)
