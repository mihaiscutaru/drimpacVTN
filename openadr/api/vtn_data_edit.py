"""
   vtn_data_edit.py
   
   Script to modify the fields regarding DR events / DR Programs / Customers / VENs from a REST API endpoint
   
   Args:
      "type": The type can be one of the following [event||program|programs|customer|customers|ven|vens"

      In case of an "event" type:
         "event": The Event JSON structure to be modified

         Example Run:

         curl -X POST -d '{"type":"event","event":[{"id":26,"dr_program_id":1,"scheduled_notification_time":"2020-01-31T13:49:30Z","start":"2020-01-31T14:49:30Z","end":"2020-01-31T15:49:30Z","modification_number":0,"status":"far","last_status_time":null,"superseded":false,"event_id":23,"deleted":false,"dr_program":"Program2"}]}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_edit
         
      In case of a "program" type:
         "program": The DR Program JSON structure to be modified
         
         Example Run:
         
         curl -X POST -d '{"data":[{"sites":[{"id":1,"customer_id":1,"site_name":"Site1","site_id":"1","ven_id":"0","ven_name":"ven01","site_location_code":"54545","ip_address":"","site_address1":"Address1","site_address2":null,"city":"Thessaloniki","state":"GR","zip":"54545","contact_name":"Site1","phone_number":"6998492379","online":false,"last_status_time":"2020-01-29T07:03:17.666051Z"}]},{"id":6,"name":"Program2"}],"type":"program"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_edit
         
      In case of a "customer" type:
         "customer": The Customer JSON structure to be modified
         
         Example Run:
         
         curl -X POST -d '{"type":"customer", "customer": [{"id":20,"name":"CustomerX","utility_id":"electoricity1","contact_name":"CustomerX","phone_number":"692342379"}]}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_edit
         
      In case of a "ven" type:
         "ven": The VEN JSON structure to be modified
         
         Example Run:
         
         curl -X POST -d '{"type":"ven","ven":[{"id":5,"customer_id":20,"site_name":"ven02","site_id":"ven02","ven_id":"1","ven_name":"ven02","site_location_code":"54545","ip_address":"","site_address1":"Address1","site_address2":null,"city":"Thessaloniki","state":"GR","zip":"55454","contact_name":"ven02","phone_number":"6988477432","online":false,"last_status_time":"2020-01-30T07:36:03.670745Z","customer_name":"Customer1"}]}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_edit
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

class VtnDataEdit(APIView):
   
   parser_classes = (JSONParser,)
   renderer_classes = (JSONRenderer,)
   
   def get_status(self,message):
      if "ERROR" in message:
         return str(status.HTTP_400_BAD_REQUEST)
      else:
         return str(status.HTTP_200_OK)
   
   @csrf_exempt
   def post(self, request, format=None):
      req = json.dumps(request.data)
      req = json.loads(req)
      if req['type'] == 'event':
         response = self.edit_event(req['event'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'program':
         response = self.edit_program(req['data'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'customer':
         response = self.edit_customer(req['customer'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'ven':
         response = self.edit_ven(req['ven'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)

   def edit_event(self, event):
      data = json.dumps(event[0])
      data = json.loads(data)
      try:
         programNew = DRProgram.objects.filter(Q(name=data['dr_program']))[0]
         event = DREvent.objects.filter(Q(event_id=data['event_id']))[0]
         event.dr_program = programNew
         event.status = data['status']
         event.scheduled_notification_time = data['scheduled_notification_time']
         event.start = data['start']
         event.end = data['end']
         event.save()
         return '{"status": "OK"}'
      except Exception as e:
         return '{"status": "ERROR: %s"}' % e
   def edit_program(self, program):
      programs = json.dumps(program[1])
      programs = json.loads(programs)
      sites = json.dumps(program[0])
      sites = json.loads(sites)
      finalSiteList = []
      currentSiteList = []
      try:
         programObj = DRProgram.objects.filter(Q(id=programs['id']))[0]
         for site in sites['sites']:
            query = Site.objects.filter(Q(site_name=site['site_name']))
            finalSiteList.append(query[0])
         
         for programIter in programObj.sites.values():
            query = Site.objects.filter(Q(site_name=programIter['site_name']))
            currentSiteList.append(query[0])
         
         for site in currentSiteList:
            programObj.sites.remove(site)
         
         for site in finalSiteList:
            programObj.sites.add(site)
         
         programObj.name = programs['name']
         
         programObj.save()
         return '{"status": "OK"}'
      except Exception as e:
         return '{"status": "ERROR: %s"}' % e
   def edit_customer(self, customer):
      data = json.dumps(customer[0])
      data = json.loads(data)
      try:
         customer = Customer.objects.filter(Q(id=data['id']))[0]
         customer.name = data['name']
         customer.utility_id = data['utility_id']
         customer.contact_name = data['contact_name']
         customer.phone_number = data['phone_number']
         customer.save()
         return '{"status": "OK"}'
      except Exception as e:
         return '{"status": "ERROR: %s"}' % e
   def edit_ven(self, ven):
      data = json.dumps(ven[0])
      data = json.loads(data)
      try:
         newCustomer = Customer.objects.filter(Q(id=data['customer_id']))[0]
         site = Site.objects.filter(Q(ven_id=data['ven_id']))[0]
         site.site_name = data['site_name']
         site.site_id = data['site_id']
         site.ven_name = data['ven_name']
         site.site_location_code = data['site_location_code']
         site.site_address1 = data['site_address1']
         site.city = data['city']
         site.state = data['state']
         site.zip = data['zip']
         site.contact_name = data['contact_name']
         site.phone_number = data['phone_number']
         site.customer = newCustomer
         site.save()
         return '{"status": "OK"}'
      except Exception as e:
         data['status'] = '"ERROR: %s}' % e
         return '{"status": "ERROR: %s"}' % e
