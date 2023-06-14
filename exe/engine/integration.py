# ===========================================================================
# eXe
# Copyright 2004-2006, University of Auckland
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# ===========================================================================
"""
elp repository integration
"""
import jwt
import logging
import json
from urllib                 import urlencode, urlopen

from exe.engine.path        import Path
from exe                    import globals as G

log = logging.getLogger(__name__)

class Integration:
    """
    Integration class
    """

    def __init__(self):
        # Load config file

        self.config = None

        self.config_filename = 'publish.conf'
        self.post_ode = 'ode_data'

        exe_path = G.application.config.exePath.basename()
        self.publish_config_path = exe_path / self.config_filename
        self.load_config_dict()

        if self.config:

            self.repo_name = self.config["info"]["name"]
            self.repo_home_url = self.config["url"]["home"]
            self.repo_set_ode_url = self.config["url"]["set_ode"]
            self.repo_get_ode_url = self.config["url"]["get_ode"]

            if 'config' in self.config and 'publish_redirect_enabled' in self.config['config']:
                self.publish_redirect_enabled = self.config['config']['publish_redirect_enabled']
            else:
                self.publish_redirect_enabled = '0'

            if 'config' in self.config and 'publish_redirect_blank' in self.config['config']:
                self.publish_redirect_blank = self.config['config']['publish_redirect_blank']
            else:
                self.publish_redirect_blank = '1'

            if 'config' in self.config and 'enabled_logs' in self.config['config']:
                self.enabled_logs = self.config['config']['enabled_logs']
            else:
                self.enabled_logs = '0'
            if 'config' in self.config and 'enabled_jwt' in self.config['config']:
                self.enabled_jwt = self.config['config']['enabled_jwt']
                self.jwt_secret_key = self.config['config']['jwt_secret_key']
                self.jwt_secret_hash = self.config['config']['jwt_secret_hash']
            else:
                self.enabled_jwt = '0'

        else:
            raise Exception('Error loading configuration file')


    def new_json_ode(self, ode_id='',filename='',filedata='',uri='',ode_user=False,jwt_token=False):
        ode = {
            'ode_id': ode_id,
            'ode_filename': filename,
            'ode_file': filedata,
            'ode_uri': uri
        }
        # Provisional - TEST
        # Must be eliminated in the future
        if ode_user:
            ode['ode_user'] = ode_user

        if self.enabled_jwt == "1":
            if not jwt_token:
                raise Exception('jwt_token not found')
            try:
                jwt.decode(jwt_token,self.jwt_secret_key, algorithms=self.jwt_secret_hash)
            except Exception as e:
                raise Exception('Error in the secret key. No match')
            ode["jwt_token"] = jwt_token

        return json.dumps(ode)


    def set_ode(self,package_name,package_file,ode_id='',ode_user=False,jwt_token=False):
        ode = self.new_json_ode(
            ode_id=ode_id,
            filename=package_name,
            filedata=package_file,
            ode_user=ode_user,
            jwt_token=jwt_token
        )
        self.log_info_integration(info='set_ode:send',params=json.loads(ode))
        params = urlencode({self.post_ode:ode})
        try:
            request = urlopen(self.repo_set_ode_url,params)
            json_response = request.read()
            if json_response:
                dict_response = json.loads(json_response)
                self.log_info_integration(info='set_ode:response',params=dict_response)
                return (True,dict_response)
            else:
                self.log_info_integration(error=True,info='set_ode:no_response')
                return (False,u'No response from Repository')
        except Exception as e:
            return (False,e)


    def get_ode(self,ode_id,ode_user=False,jwt_token=False):
        ode = self.new_json_ode(
            ode_id=ode_id,
            ode_user=ode_user,
            jwt_token=jwt_token
        )
        self.log_info_integration(info='get_ode:send',params=json.loads(ode))
        params = urlencode({self.post_ode:ode})
        try:
            request = urlopen(self.repo_get_ode_url,params)
            json_response = request.read()
            if json_response:
                dict_response = json.loads(json_response)
                self.log_info_integration(info='get_ode:response',params=dict_response)
                return (True,dict_response)
            else:
                self.log_info_integration(error=True,info='get_ode:no_response')
                return (False,'No response from Repository')
        except Exception as e:
            return (False,e)


    def load_config_dict(self):
        if self.publish_config_path.exists():
            with open(self.publish_config_path,'r') as f:
                fdata = f.read()
                lines = fdata.split('\n')
                config_dict = {}
                for line in lines:
                    line = line.strip()
                    if line and line[0]!='#':
                        if line[0] == '[' and line[-1] == ']':
                            key = line.strip('[]')
                            config_dict[key] = {}
                        elif key and '=' in line:
                            line_split = line.split('=')
                            if len(line_split) == 2:
                                sub_key = line_split[0].strip()
                                sub_value = line_split[1].strip().strip("'")
                                config_dict[key][sub_key] = sub_value
                self.config = config_dict
        else:
            msx = ('The configuration file %s does not exist or cannot be accessed.') % self.publish_config_path
            raise Exception(msx)

    def log_info_integration(self, error=False, info='', params={}):
        if self.enabled_logs == '1':
            log_txt = u'[INTEGRATION_SERVICE]'
            if info:
                log_txt += '['+info+']'
            if self.repo_set_ode_url:
                log_txt += ' serviceURL:'
                log_txt += self.repo_set_ode_url
            if params:
                for param in params.keys():
                    if param != 'ode_file':
                        log_txt += ' %s:%s ' % (param, params[param])
            if error:
                log.error(log_txt)
            else:
                log.info(log_txt)