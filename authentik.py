import fastapi
import authentik_client as ac
import yaml


# get configuration for authentik instance from conf.yml
with open('conf.yml', 'r') as f1:
	authConf: dict[str, str] = yaml.safe_load(f1)['authentik']

# configure API client
configuration = ac.Configuration(
	host = f'http://{authConf['url']}/api/v3', 
	api_key = {
		'authentik': authConf['key']
	}
)

configuration.api_key['authentik'] = authConf['key']

# configuration = ac.Configuration(
# 	host = f'http://auth.noahsroberts.com/api/v3', 
# 	api_key = {
# 		'authentik': "Z6f566LMASPbG6hZ4QhqxBfFZuvZZCVwi2cCpX4AqgchXhiawns974kY5cdq"
# 	}
# )

# configuration.api_key['authentik'] = "Z6f566LMASPbG6hZ4QhqxBfFZuvZZCVwi2cCpX4AqgchXhiawns974kY5cdq"

# root API object
APIClient = ac.ApiClient(configuration)

# create API objects for each API classification
# admin = ac.AdminApi(APIClient)
# authenticators = ac.AuthenticatorsApi(APIClient)
core = ac.CoreApi(APIClient)
# crypto = ac.CryptoApi(APIClient)
# enterprise = ac.EnterpriseApi(APIClient)
# events = ac.EventsApi(APIClient)
# flows = ac.FlowsApi(APIClient)
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
# stages = ac.StagesApi(APIClient)
# tenants = ac.TenantsApi(APIClient)



def fetchGroupList():
	# grab results section of the raw ouput
	raw = core.core_groups_list().results
	# make a list of all the group names
	groups = [a.name for a in raw]
	return groups

def fetchUsers():
	return list(core.core_users_list())
