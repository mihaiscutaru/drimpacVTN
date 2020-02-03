"""
   vtn_data_retrieve.py
   
   Script to retrieve information regarding DR events / DR Programs / Customers / VENs from a REST API endpoint
   
   Args:
      "type": The type can be one of the following [event|events|program|programs|customer|customers|ven|vens"

      In case of an "event" type:
         "event": The Event ID to be retrieved

         Example Run:

         curl -X POST -d '{"type":"event","event":"event_id"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_retrieve

      In case of an "events" type:

         Example Run:

         curl -X POST -d '{"type":"events"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_retrieve
         
      In case of a "program" type:
         "program": The DR Program name to be retrieved
         
         Example Run:
         
         curl -X POST -d '{"type":"program","program":"program_name"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_retrieve
      
      In case of a "programs" type:
         
         Example Run:
         
         curl -X POST -d '{"type":"programs"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_retrieve
         
      In case of a "customer" type:
         "customer": The Customer name to be retrieved
         
         Example Run:
         
         curl -X POST -d '{"type":"customer","customer":"CustomerX"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_retrieve
      
      In case of a "customers" type:
         
         Example Run:
         
         curl -X POST -d '{"type":"customers"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_retrieve
         
      In case of a "ven" type:
         "ven_name": The VEN Name to be retrieved
         
         Example Run:
         
         curl -X POST -d '{"type":"ven","ven":"ven_name"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_retrieve
         
      In case of a "vens" type:
         
         Example Run:
         
         curl -X POST -d '{"type":"vens"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_retrieve
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

class VtnDataRetrieve(APIView):
   
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
         response = self.get_event(req['event'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'program':
         response = self.get_program(req['program'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'customer':
         response = self.get_customer(req['customer'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'ven':
         response = self.get_ven(req['ven'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'events':
         response = self.get_events()
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'programs':
         response = self.get_programs()
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'customers':
         response = self.get_customers()
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'vens':
         response = self.get_vens()
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)

   def get_event(self, event):
      data = json.loads('{ "data": [],"status": "OK"}')
      try:
         event = DREvent.objects.filter(Q(event_id=event))
         data['data'].append(event.values_list().values()[0])
         program = DRProgram.objects.filter(Q(id=data['data'][0]['dr_program_id']))
         data['data'][0]['dr_program'] = program[0].name
         return data
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return data
   def get_program(self, program):
      data = json.loads('{ "data": [{"sites": []}],"status": "OK"}')
      try:
         program = DRProgram.objects.filter(Q(name=program))
         for programIter in program[0].sites.values():
            data['data'][0]['sites'].append(programIter)
         data['data'].append(program.values_list().values()[0])
         return data
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return data
   def get_customer(self, customer):
      data = json.loads('{ "data": [],"status": "OK"}')
      try:
         customer = Customer.objects.filter(Q(name=customer))
         data['data'].append(customer.values_list().values()[0])
         return data
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return data
   def get_ven(self, ven):
      data = json.loads('{ "data": [],"status": "OK"}')
      try:
         site = Site.objects.filter(Q(ven_name=ven))
         data['data'].append(site.values_list().values()[0])
         customer = Customer.objects.filter(Q(id=data['data'][0]['customer_id']))
         data['data'][0]['customer_name'] = customer[0].name
         return data
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return data
   def get_events(self):
      data = json.loads('{ "data": [],"status": "OK"}')
      try:
         events = DREvent.objects.all().order_by('event_id')
         for event in events.values_list().values():
            data['data'].append(event)
         return data
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return data
   def get_programs(self):
      data = json.loads('{ "data": [],"status": "OK"}')
      try:
         programs = DRProgram.objects.all().order_by('id')
         for program in programs.values_list().values():
            data['data'].append(program)
         return data
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return data
   def get_customers(self):
      data = json.loads('{ "data": [],"status": "OK"}')
      try:
         customers = Customer.objects.all().order_by('pk')
         for customer in customers.values_list().values():
            data['data'].append(customer)
         return data
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return data
   def get_vens(self):
      data = json.loads('{ "data": [],"status": "OK"}')
      try:
         sites = Site.objects.all().order_by('ven_id')
         for site in sites.values_list().values():
            data['data'].append(site)
         return data
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return data
