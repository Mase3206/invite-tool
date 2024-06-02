import datetime

import authentik_client as ac
from authentik_client.models.flow import Flow
from authentik_client.models.flow_designation_enum import FlowDesignationEnum
from authentik_client.models.invitation import Invitation
from authentik_client.models.invitation_request import InvitationRequest

# from user import HomelabUser


class Authentik:
	def __init__(self, authConf: dict[str, str]):
		self.authConf = authConf
		# configure API client
		configuration = ac.Configuration(
			host = f'https://{authConf['url']}/api/v3', 
			access_token = authConf['key']
		)

		# set api key
		configuration.api_key['authentik'] = authConf['key']


		APIClient = ac.ApiClient(configuration)

		# create API objects for each API classification
		# admin = ac.AdminApi(APIClient)
		# authenticators = ac.AuthenticatorsApi(APIClient)
		self.core = ac.CoreApi(APIClient)
		# crypto = ac.CryptoApi(APIClient)
		# enterprise = ac.EnterpriseApi(APIClient)
		# events = ac.EventsApi(APIClient)
		self.flows = ac.FlowsApi(APIClient)
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
		self.stages = ac.StagesApi(APIClient)
		# tenants = ac.TenantsApi(APIClient)
	
	def fetchGroupList(self) -> list[str]:
		# grab results section of the raw ouput
		raw = self.core.core_groups_list().results

		# make a list of all the group names
		groups = [g.name for g in raw]
		# print(groups)
		return groups



	def fetchUserList(self) -> list[str]:
		# grab results section of the raw ouput
		raw = self.core.core_users_list().results

		# make a list of usernames from the authentik_client.User object
		users = [u.username for u in raw]
		# print(users)
		return users



	def fetchInviteFlows(self) -> list[Flow]:
		raw: list[Flow] = self.flows.flows_instances_list().results
		enrollmentFlows = []

		for flow in raw:
			if flow.designation == FlowDesignationEnum.ENROLLMENT:
				enrollmentFlows.append(flow)

		a: Flow = enrollmentFlows[0]

		return enrollmentFlows



	def shiftDate(self, ref: datetime.datetime, days: int) -> datetime.datetime:	
		return ref + datetime.timedelta(days=days)


	def fetchExistingInvites(self) -> list[str]:
		"""
		Fetches existing, unused invites.
		"""

		raw: list[Invitation] = self.stages.stages_invitation_invitations_list().results

		names = [a.name for a in raw]
		return names
		

	def inviteExists(self, user):
		existing = self.fetchExistingInvites()
		for a in existing:
			if a[:-7] == user.username:
				return True
			else:
				return False
		
		if len(existing) == 0:
			return False


	def createInvite(self, user, flow: Flow):
		today = datetime.datetime.today()
		expires = self.shiftDate(today, +14)

		data = user.createAuthInviteData()
		data['invite_expires'] = str(expires)

		invite = InvitationRequest(
			name=f'{user.username}-invite',
			expires=expires,
			fixed_data=data,
			single_use=True,
			flow=flow.pk,
		)

		return self.stages.stages_invitation_invitations_create(invite)