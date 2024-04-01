import authentik_client as ac
import yaml


# get configuration for authentik instance from conf.yml
with open('../conf.yml', 'r') as f1:
	authConf: dict[str, str] = yaml.safe_load(f1)['authentik']

# configure API client
configuration = ac.Configuration(
	host = authConf['url'], 
	api_key = {
		'default': authConf['key']
	}
)


ac.ApiClient(configuration)
adminClient = ac.AdminApi(ac.ApiClient(configuration))