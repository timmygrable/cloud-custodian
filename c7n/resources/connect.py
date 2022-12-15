# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
from c7n.manager import resources
from c7n.query import QueryResourceManager, TypeInfo
from c7n.filters import ValueFilter
from c7n.utils import local_session, type_schema
from c7n.actions import Action


@resources.register('connect-instance')
class Connect(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'connect'
        enum_spec = ('list_instances', 'InstanceSummaryList', None)
        arn_type = 'instance'
        name = "InstanceAlias"
        id = "Id"


@Connect.filter_registry.register('instance-attribute')
class ConnectInstanceAttributeFilter(ValueFilter):
    """
    Filter Connect resources based on instance attributes

        :example:

    .. code-block:: yaml

            policies:

              - name: connect-instance-attribute
                resource: connect-instance
                filters:
                  - type: instance-attribute
                    key: Attribute.Value
                    value: true
                    attribute_type: CONTACT_LENS

    """

    schema = type_schema('instance-attribute', rinherit=ValueFilter.schema,
        required=['attribute_type'], **{'attribute_type': {'type': 'string'}})
    permissions = ('connect:DescribeInstanceAttribute',)
    annotation_key = 'c7n:InstanceAttribute'

    def process(self, resources, event=None):

        client = local_session(self.manager.session_factory).client('connect')
        results = []

        for r in resources:
            if self.annotation_key not in r:
                instance_attribute = client.describe_instance_attribute(InstanceId=r['Id'],
                                AttributeType=str.upper(self.data.get('attribute_type')))
                r[self.annotation_key] = instance_attribute

            if self.match(r[self.annotation_key]):
                results.append(r)

        return results

    @Connect.action_registry.register("set-contact-lens")
    class SetContactLens(Action):
        """Set the contact lens feature for the connect resources

        :Example:

        .. code-block:: yaml

            policies:
              - name: connect-set-contact-lens
                resource: connect-instance
                filters:
                  - type: instance-attribute
                    key: Attribute.Value
                    value: true
                    attribute_type: CONTACT_LENS
                actions:
                  - type: set-contact-lens
                    value: true
              - name: connect-disable-contact-lens
                resource: connect-instance
                filters:
                  - type: instance-attribute
                    key: Attribute.Value
                    value: true
                    attribute_type: CONTACT_LENS
                actions:
                  - type: set-contact-lens
                    value: false
        """
        schema = type_schema("set-contact-lens", **{"value": "boolean"})
        permissions = ("connect:UpdateInstanceAttribute",)

        def process(self, resources):
            client = local_session(self.manager.session_factory).client('connect')

            if not resources:
                return

            if "value" not in self.data:
                return

            for r in resources:
                client.update_instance_attribute(InstanceId=r["Id"],
                    AttributeType="CONTACT_LENS", Value=self.data.get("value"))
            return
