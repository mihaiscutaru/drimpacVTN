"""
   vtn_data_create.py
   
   Script to initiliaze a DR events / DR Programs / Customers / VENs from a REST API endpoint
   
   Args:
      "type": The type can be one of the following [event|program|customer|ven"

      In case of an "event" type:
         "drprogram": Argument that will query the database for the existance of a DR Program and get the specifications of the Program
         "event_start": The time that the event will start in %Y-%m-%dT%H:%M:%S
         "event_end": The time that the event will end in %Y-%m-%dT%H:%M:%S
         "event_notification": The time that the event will notify the VEN in %Y-%m-%dT%H:%M:%S

         Example Run:

         curl -X POST -d '{"type":"event","drprogram":"Program1","event_start":"2020-01-30T02:15:42","event_end":"2020-01-31T02:15:42","event_notification":"2020-01-30T02:14:12",\
            "signalName": "ELECTRICITY_PRICE", "signalType": "price", "intervals": [{ "duration": "60", "uid": 1, "signalPayload": "3.0"  }, \
            { "duration": "60", "uid": 2, "signalPayload": "5.0"  }, { "duration": "60", "uid": 3, "signalPayload": "3.0"  }, { "duration": "60", "uid": 4, "signalPayload": "5.0"  }, \
            { "duration": "60", "uid": 5, "signalPayload": "3.0"  }, { "duration": "60", "uid": 6, "signalPayload": "4.0"  }, { "duration": "60", "uid": 7, "signalPayload": "3.0"  }, \
            { "duration": "60", "uid": 8, "signalPayload": "4.0"  }, { "duration": "60", "uid": 9, "signalPayload": "5.0"  }, { "duration": "60", "uid": 10, "signalPayload": "6.0"  }, \
            { "duration": "60", "uid": 11, "signalPayload": "8.0"  }, { "duration": "60", "uid": 12, "signalPayload": "4.0"  }, { "duration": "60", "uid": 13, "signalPayload": "3.0"  }, \
            { "duration": "60", "uid": 14, "signalPayload": "1.0"  }, { "duration": "60", "uid": 15, "signalPayload": "7.0"  }, { "duration": "60", "uid": 16, "signalPayload": "6.0"  }, \
            { "duration": "60", "uid": 17, "signalPayload": "5.0"  }, { "duration": "60", "uid": 18, "signalPayload": "1.0"  }, { "duration": "60", "uid": 19, "signalPayload": "4.0"  }, \
            { "duration": "60", "uid": 20, "signalPayload": "5.0"  }, { "duration": "60", "uid": 21, "signalPayload": "2.0"  }, { "duration": "60", "uid": 22, "signalPayload": "3.0"  }, \
            { "duration": "60", "uid": 23, "signalPayload": "1.0"  }, { "duration": "60", "uid": 24, "signalPayload": "3.0"  } ]}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_create
         
         
      In case of a "program" type:
         "name": The DR Program name to be added
         "sites": The VENs names in a string variable separated by comma e.g "site1,site2"
         
         Example Run:
         
         curl -X POST -d '{"type":"program","name":"Program2","sites":"Site1,ven02"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_create
      
      In case of a "customer" type:
         "name": 
         "utility_id": 
         "contact_name":
         "phone_number":
         
         Example Run:
         
         curl -X POST -d '{"type":"customer","name":"CustomerX","utility_id":"001","contact_name":"CustomerX","phone_number":"0123456789"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_create
      
      In case of a "ven" type:
         "customer": The Customer name as string value
         "site_name": The Site Name
         "ven_name": The VEN Name
         "site_location_code": The site location code
         "site_address1": The Site's Address
         "city": The city corresponding to the Site
         "state": The state corresponding to the Site
         "zip": The zip code corresponding to the Site
         "contact_name": A contact name
         "phone_number": Phone Number
         
         Example Run:
      
         curl -X POST -d '{"type": "ven", "customer": "CustomerX","site_name": "ven055","ven_name": "ven055","site_address1": "TestAddress","city": "Thess","state": "GR","zip": "22122","contact_name": "CustomerX","phone_number": "0123456789"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_create
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

class VtnDataCreate(APIView):
   
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
         response = self.create_event(req['drprogram'], req['event_start'], req['event_end'], req['event_notification'], req['signalName'], req['signalType'], req['intervals'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'program':
         response = self.create_program(req['name'], req['sites'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'customer':
         response = self.create_customer(req['name'], req['utility_id'],req['contact_name'],req['phone_number'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)
      elif req['type'] == 'ven':
         response = self.create_ven(req['customer'],req['site_name'],req['ven_name'],req['site_location_code'],req['site_address1'],req['city'],req['state'],req['zip'],req['contact_name'],req['phone_number'])
         status = self.get_status(response)
         return Response(response, content_type='application/json', status=status)

   def create_event(self,drprogram,event_start,event_end,event_notification, signal_name, signal_type, intervals):
      try:
         query = DRProgram.objects.filter(Q(name=drprogram))
         dr_program = query[0]
      except IndexError:
         return '{"status": "ERROR: DR Program not found"}'

      sites_in_program = dr_program.sites.all()
      events = DREvent.objects.all().order_by('-event_id')
      try:
         event_id = events[0].event_id + 1
      except IndexError:
         event_id = 0

      now = datetime.now()
      try:
         interval = json.loads(json.dumps(str(intervals)))
         event_notification = datetime.strptime(event_notification, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
         event_start = datetime.strptime(event_start, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
         event_end = datetime.strptime(event_end, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
      except ValueError:
         return '{"status": "ERROR: The date formats should be: %Y-%m-%dT%H:%M:%S"}'
      event = DREvent(dr_program=dr_program,
                scheduled_notification_time=event_notification,
                start=event_start,
                end=event_end,
                signal_name=signal_name,
                signal_type=signal_type,
                intervals=interval,
                modification_number=0,
                status='far',
                superseded=False,
                event_id=event_id,
                deleted=False)

      event.save()

      # We have a site at this point
      site=Site.objects.filter(Q(ven_id=dr_program.sites.values()[0]['ven_id']))[0]
      s = SiteEvent(dr_event=event,
              status='far',
              last_status_time=datetime.now(),
              site=site)
      s.save()
      return '{"status": "OK"}'

   def create_program(self,name,sites):
      try:
         siteList = sites.split(",")
         finalSiteList = []
         for site in siteList:
            query = Site.objects.filter(Q(site_name=site))
            finalSiteList.append(query[0])
         programs = DRProgram.objects.all().order_by('id')
         program = DRProgram(name=name)

         program.save()
         for site in finalSiteList:
            program.sites.add(site)
         return '{"status": "OK"}'
      except Exception as e:
         return '{"status": "ERROR: %s}' % e
   
   def create_customer(self,name,utility_id,contact_name,phone_number):
      try:
         customer = Customer(name=name,utility_id=utility_id,contact_name=contact_name,phone_number=phone_number)
         customer.save()
         return '{"status": "OK"}'
      except Exception as e:
         return '{"status": "ERROR: %s}' % e
   
   def create_ven(self,customer,site_name,ven_name,site_location_code,site_address1,city,state,zip,contact_name,phone_number):
      try:
         try:
            query = Customer.objects.filter(Q(name=customer))
            customer = query[0]
         except IndexError:
            return '{"status": "ERROR: Customer not found"}'
         sites = Site.objects.all().order_by('-ven_id')
         try:
            site_id = int(sites[0].ven_id) + 1
         except IndexError:
            site_id = 0
         s = Site(customer=customer,
                  site_name=site_name,
                  site_id=site_id,
                  ven_id=site_id,
                  ven_name=ven_name,
                  site_location_code=site_location_code,
                  site_address1=site_address1,
                  city=city,
                  state=state,
                  zip=zip,
                  contact_name=contact_name,
                  phone_number=phone_number,
                  online=False)
         s.save()
         return '{"status": "OK"}'
      except Exception as e:
         return '{"status": "ERROR: %s}' % e
