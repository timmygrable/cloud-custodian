# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
from botocore.exceptions import ClientError
from c7n.manager import resources
from c7n.query import QueryResourceManager, TypeInfo
from c7n.utils import local_session, type_schema
from c7n.actions import BaseAction
from c7n.tags import universal_augment
from c7n.tags import TagDelayedAction, TagActionFilter


@resources.register('ram')
class RAM(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'ram'
        enum_spec = ('get_resource_shares', 'resourceShares', {'resourceOwner': "SELF"})
        id = name = 'resourceShareArn'
        arn_type = "resource-share"
        cfn_type = 'AWS::RAM::ResourceShare'
        universal_taggable = object()

    augment = universal_augment

RAM.action_registry.register('mark-for-op', TagDelayedAction)
RAM.filter_registry.register('marked-for-op', TagActionFilter)

@RAM.action_registry.register('delete')
class DeleteRAM(BaseAction):
    """Delete a RAM resource share

    :example:

    .. code-block:: yaml

        policies:
          - name: delete-ram-resource-share
            resource: ram
            actions:
              - type: delete
    """
    schema = type_schema('delete')
    permissions = ('ram:DeleteResourceShare',)

    def delete_ram(self, r):
        client = local_session(self.manager.session_factory).client('ram')
        try:
            client.delete_resource_share(resourceShareArn=r['resourceShareArn'])
        except ClientError as e:
            if e.response['Error']['Code'] != 'UnknownResourceException':
                raise

    def process(self, resources):
        with self.executor_factory(max_workers=2) as w:
            list(w.map(self.delete_ram, resources))
