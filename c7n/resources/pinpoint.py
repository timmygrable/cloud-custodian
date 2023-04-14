# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from c7n.manager import resources
from c7n.query import QueryResourceManager, TypeInfo
from c7n.tags import TagDelayedAction, TagActionFilter


@resources.register('pinpoint-app')
class PinpointApp(QueryResourceManager):
    class resource_type(TypeInfo):
        service = 'pinpoint'
        arn_type = 'apps'
        enum_spec = ('get_apps', 'ApplicationsResponse.Item', None)
        name = "Name"
        id = 'Id'
        dimension = 'Id'
        universal_taggable = True
        config_type = cfn_type = 'AWS::Pinpoint::App'
        arn = "Arn"
        permission_prefix = 'mobiletargeting'
        
    
PinpointApp.action_registry.register('mark-for-op', TagDelayedAction)
PinpointApp.filter_registry.register('marked-for-op', TagActionFilter)
