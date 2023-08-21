from flask.views import MethodView
import json
import logging
from core.Controller import Controller

class MarginAPI(MethodView):
  def get(self):
    brokerHandle = Controller.getBrokerLogin().getBrokerHandle()
    margin = brokerHandle.margins()
    logging.info('User Margin => %s', margin)
    return json.dumps(margin)
  