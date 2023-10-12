# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from c7n.manager import resources
from c7n.query import QueryResourceManager, TypeInfo
from c7n.tags import RemoveTag, Tag, TagActionFilter, TagDelayedAction
from c7n.utils import local_session, type_schema
from c7n.actions import BaseAction


@resources.register('opensearch')
class Opensearch(QueryResourceManager):
    class resource_type(TypeInfo):
        service = 'opensearch'
        arn_type = 'domain'
        enum_spec = ('list_domain_names', 'DomainNames[]', None)
        name = id = 'DomainNames'
        universal_taggable = True
        cfn_type = 'AWS::OpenSearchService::Domain'
        arn = "ARN"
        permission_prefix = 'es'

    def augment(self, resources):
        client = local_session(self.session_factory).client('opensearch')
        arn_resources = []
        for r in resources:
            domain_detail = client.describe_domain(DomainName=r['DomainName'])['DomainStatus']
            tag_data = client.list_tags(ARN=domain_detail['ARN'])
            domain_detail['Tags'] = tag_data.get('TagList', [])
            arn_resources.append(domain_detail)
        return arn_resources

@Opensearch.action_registry.register('tag')
class TagOpenSearchResource(Tag):
    """Create tags on an OpenSearch resource

    :example:

    .. code-block:: yaml

        policies:
            - name: tag-opensearch
              resource: opensearch
              actions:
                - type: tag
                  key: test-key
                  value: test-value
    """
    permissions = ('es:AddTags',)

    def process_resource_set(self, client, resources, new_tags):
        for r in resources:
            client.add_tags(ARN=r["ARN"], TagList=new_tags)


@Opensearch.action_registry.register('remove-tag')
class RemoveTagOpenSearchResource(RemoveTag):
    """Remove tags from an OpenSearch resource

    :example:

    .. code-block:: yaml

        policies:
            - name: remove-tag-opensearch
              resource: opensearch
              actions:
                - type: remove-tag
                  tags: ["tag-key"]
    """
    permissions = ('es:RemoveTags',)

    def process_resource_set(self, client, resources, tags):
        for r in resources:
            client.remove_tags(ARN=r['ARN'], TagKeys=tags)

Opensearch.filter_registry.register('marked-for-op', TagActionFilter)
@Opensearch.action_registry.register('mark-for-op')
class MarkDomainForOp(TagDelayedAction):
    """Mark OpenSearch domain for deferred action

    :example:

    .. code-block:: yaml

        policies:
          - name: opensearch-invalid-tag-mark
            resource: opensearch
            filters:
              - "tag:InvalidTag": present
            actions:
              - type: mark-for-op
                op: delete
                days: 1
    """

@Opensearch.action_registry.register('delete')
class DeleteDomain(BaseAction):
    """Delete an OpenSearch domain

    :example:

    .. code-block:: yaml

        policies:
          - name: delete-opensearch-domain
            resource: opensearch
            actions:
              - type: delete
    """
    schema = type_schema('delete')
    permissions = ('es:DeleteDomain',)

    def process(self, resources):
        client = local_session(self.manager.session_factory).client('opensearch')
        for r in resources:
            try:
              client.delete_domain(DomainName=r['DomainName'])
            except client.exceptions.ResourceNotFoundException:
              continue

