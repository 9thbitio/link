from . import APIRequestWrapper, APIResponseWrapper
from requests.auth import AuthBase
import json
import requests

from link import lnk

class AolAPIResponse(APIResponseWrapper):
    pass


class Aol(APIRequestWrapper):

    """Use AOL's API to run an existing report. Return a pandas dataframe. """

    def __init__(self, user=None, password=None, report_id=None, wrap_name=None,
            base_url=None, org_id=None):
        self.report_id = report_id
        self.org_id = org_id
        super(Aol, self).__init__(wrap_name = wrap_name,
                                  user=user, 
                                  password=password,
                                  base_url = base_url,
                                  response_wrapper = AolAPIResponse)

    def authenticate(self):

        """ Log into AOL API, grab org_id """

        self._wrapped = requests.session()
        
        payload = {'un':self.user, 'pw':self.password, 's':'1'}

        resp = self.post('/sessions/login?', data =
                         payload,
                         headers={'content-type':
                                  'application/x-www-form-urlencoded'})
        
        if not resp.ok:
            raise Exception("Issue connecting to API")
            
        resp = json.loads(resp.content)

        self.org_id = resp['org_id']
            

    def create_report(self, name):

        """ Create new report for last 7 days, returning ad revenue. """

        resp = self.get("/reporting/create_report?org_id={}&name=7_day_ad_revenue&keys=ad&metrics=ad_revenue&timezone=1&continent_id=43&currency_id=150&date_range=LAST_7_DAYS".format(self.org_id))

        if not resp.ok:
            raise Exception("Issue creating report")

        resp = json.loads(resp.content)

        self.report_id = resp['id']

        self.run_existing_report()

    def run_existing_report(self):

        """ Run report to grab ad revenue """

        resp = self.get("/reporting/run_existing_report?report_id={}".format(self.report_id))

        resp = json.loads(resp.content)
        if not resp.ok:
            raise Exception("Issue running existing report")

        report_list = [channel['row'] for channel in resp['data']]
        report_dict = {}
        for report in report_list:
            report_dict[report[0]] = report[1]


