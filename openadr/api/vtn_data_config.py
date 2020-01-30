"""
   vtn_data_config.py
   
   Script to initiliaze a DR events / DR Programs / Customers / VENs from a REST API endpoint
   
   Args:
      "type": The type can be one of the following [event|program|customer|ven"

      In case of an "event" type:
         "drprogram": Argument that will query the database for the existance of a DR Program and get the specifications of the Program
         "event_start": The time that the event will start in %Y-%m-%dT%H:%M:%S
         "event_end": The time that the event will end in %Y-%m-%dT%H:%M:%S
         "event_notification": The time that the event will notify the VEN in %Y-%m-%dT%H:%M:%S

         Example Run:

         curl -X POST -d '{"type":"event","drprogram":"Program1","event_start":"2020-01-30T02:15:42","event_end":"2020-01-30T02:16:52","event_notification":"2020-01-30T02:14"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_config

      In case of a "program" type:
         "name": The DR Program name to be added
         "sites": The VENs names in a string variable separated by comma e.g "site1,site2"
         
         Example Run:
         
         curl -X POST -d '{"type":"program","name":"Program2","sites":"Site1,ven02"}' --header "Content-Type: application/json"  http://127.0.0.1:8000/vtn_data_config
"""

import django
import os
import json
import sys
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework import status
os.chdir(os.environ['PROJECT_HOME'] + "/openadr")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openadr.settings.base")
django.setup()

import random
from datetime import datetime, timedelta
from vtn.models import *
from django.db.models import Q

class VtnDataConfig(APIView):
   
   parser_classes = (JSONParser,)
   
   @csrf_exempt
   def post(self, request, format=None):
      req = json.dumps(request.data)
      req = json.loads(req)
      if req['type'] == 'event':
         response = self.create_event(req['drprogram'], req['event_start'], req['event_end'], req['event_notification'])
         if "ERROR" in response:
            return Response(response, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
         else:
            return Response(response, content_type='application/json', status=status.HTTP_200_OK)
      elif req['type'] == 'program':
         response = self.create_program(req['name'], req['sites'])
         if "ERROR" in response:
            return Response(response, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
         else:
            return Response(response, content_type='application/json', status=status.HTTP_200_OK)

   def create_event(self,drprogram,event_start,event_end,event_notification):
      try:
         query = DRProgram.objects.filter(Q(name=drprogram))
         dr_program = query[0]
      except IndexError:
         return '{"status": "ERROR: DR Program not found"}'

      sites_in_program = dr_program.sites.all()
      site = sites_in_program[random.randint(0, len(sites_in_program) - 1)]
      events = DREvent.objects.all().order_by('-event_id')
      try:
         event_id = events[0].event_id + 1
      except IndexError:
         event_id = 0

      now = datetime.now()
      try:
         event_notification = datetime.strptime(event_notification, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
         event_start = datetime.strptime(event_start, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
         event_end = datetime.strptime(event_end, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
      except ValueError:
         return '{"status": "ERROR: The date formats should be: %Y-%m-%dT%H:%M:%S"}'
      event = DREvent(dr_program=dr_program,
                scheduled_notification_time=event_notification,
                start=event_start,
                end=event_end,
                modification_number=0,
                status='far',
                superseded=False,
                event_id=event_id,
                deleted=False)

      event.save()

      # We have a site at this point
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
