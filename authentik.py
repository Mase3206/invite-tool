import datetime

import authentik_client as ac
import yaml
from authentik_client.models.flow import Flow
from authentik_client.models.flow_designation_enum import FlowDesignationEnum
from authentik_client.models.invitation_request import InvitationRequest

from objects import User


# get configuration for authentik instance from conf.yml
with open('conf.yml', 'r') as f1:
	authConf: dict[str, str] = yaml.safe_load(f1)['authentik']

# configure API client
configuration = ac.Configuration(
	host = f'https://{authConf['url']}/api/v3', 
	api_key = {
		'authentik': authConf['key']
	}
)

configuration.api_key['authentik'] = authConf['key']



APIClient = ac.ApiClient(configuration)

# create API objects for each API classification
# admin = ac.AdminApi(APIClient)
# authenticators = ac.AuthenticatorsApi(APIClient)
core = ac.CoreApi(APIClient)
# crypto = ac.CryptoApi(APIClient)
# enterprise = ac.EnterpriseApi(APIClient)
# events = ac.EventsApi(APIClient)
flows = ac.FlowsApi(APIClient)
# managed = ac.ManagedApi(APIClient)
# oauth2 = ac.Oauth2Api(APIClient)
# outposts = ac.OutpostsApi(APIClient)
# policies = ac.PoliciesApi(APIClient)
# propertyMappings = ac.PropertymappingsApi(APIClient)
# providers = ac.ProvidersApi(APIClient)
# RAC = ac.RacApi(APIClient)
# RBAC = ac.RbacApi(APIClient)
# root = ac.RootApi(APIClient)
# schema = ac.SchemaApi(APIClient)
# sources = ac.SourcesApi(APIClient)
stages = ac.StagesApi(APIClient)
# tenants = ac.TenantsApi(APIClient)



def fetchGroupList() -> list[str]:
	# grab results section of the raw ouput
	raw = core.core_groups_list().results

	# make a list of all the group names
	groups = [g.name for g in raw]
	# print(groups)
	return groups



def fetchUserList() -> list[str]:
	# grab results section of the raw ouput
	raw = core.core_users_list().results

	# make a list of usernames from the authentik_client.User object
	users = [u.username for u in raw]
	# print(users)
	return users



def fetchInviteFlows() -> list[Flow]:
	raw: list[Flow] = flows.flows_instances_list().results
	enrollmentFlows = []

	for flow in raw:
		if flow.designation == FlowDesignationEnum.ENROLLMENT:
			enrollmentFlows.append(flow)

	return enrollmentFlows



def shiftDate(ref: datetime, days: int) -> datetime:	
	return ref + datetime.timedelta(days=days)



def createInvite(user: User) -> dict:
	today = datetime.datetime.today()
	expires = shiftDate(today, 14)

	invite = InvitationRequest(
		name=f'{user.username}-invite',
		expires=expires,
		fixed_data=user.createAuthInviteData(),
		single_use=True,
		flow='enrollment-predefined-username-email-name'
	)

	return stages.stages_invitation_invitations_create(invite)
	
