"""
   vtn_data_delete.py
   
   Script to delete DR events / DR Programs / Customers / VENs from a REST API endpoint
   
   Args:
      "type": The type can be one of the following [event|program|customer|ven]"

      In case of an "event" type:
         "event": The Event ID to be deleted

         Example Run:

         curl -X POST -d '{"type":"event","event":"23"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_delete
         
      In case of a "program" type:
         "program": The DR Program name to be deleted
         
         Example Run:
         
         curl -X POST -d '{"type":"program","program":"drprogram0"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_delete
         
      In case of a "customer" type:
         "customer": The Customer ID to be deleted
         
         Example Run:
         
         curl -X POST -d '{"type":"customer","customer":"9"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_delete
         
      In case of a "ven" type:
         "ven": The VEN ID to be deleted
         
         Example Run:
         
         curl -X POST -d '{"type":"ven","ven":"3"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_delete
         
"""

import django
import os
import json
import sys
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework import status
os.chdir(os.environ['PROJECT_HOME'] + "/openadr")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openadr.settings.base")
django.setup()

import random
from datetime import datetime, timedelta
from vtn.models import *
from django.db.models import Q

class VtnDataDelete(APIView):
   
   parser_classes = (JSONParser,)
   renderer_classes = (JSONRenderer,)
   
   def get_status(self,message):
      if "ERROR" in message['status']:
         return str(status.HTTP_400_BAD_REQUEST)
      else:
         return str(status.HTTP_200_OK)
   
   @csrf_exempt
   def post(self, request, format=None):
      req = json.dumps(request.data)
      req = json.loads(req)
      if req['type'] == 'event':
         response = self.delete_event(req['event'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'program':
         response = self.delete_program(req['program'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'customer':
         response = self.delete_customer(req['customer'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'report':
         response = self.delete_report(req['report'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'ven':
         response = self.delete_ven(req['ven'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)

   def delete_event(self, event):
      data = json.loads('{ "data": [],"status": "OK"}')
      try:
         event = DREvent.objects.filter(Q(event_id=event))[0]
         event.delete()
         return data
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return data
   def delete_program(self, program):
      data = json.loads('{ "data": [{"sites": []}],"status": "OK"}')
      try:
         program = DRProgram.objects.filter(Q(name=program))
         program.delete()
         return data
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return data
   def delete_customer(self, customer):
      data = json.loads('{ "data": [],"status": "OK"}')
      try:
         customer = Customer.objects.filter(Q(id=customer))
         customer.delete()
         return data
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return data
   def delete_report(self, report):
      data = json.loads('{ "data": [],"status": "OK"}')
      try:
         report = Report.objects.filter(Q(report_request_id=report))
         report.delete()
         return data
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return data
   def delete_ven(self, ven):
      data = json.loads('{ "data": [],"status": "OK"}')
      try:
         site = Site.objects.filter(Q(ven_id=ven))
         site.delete()
         return data
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return data
