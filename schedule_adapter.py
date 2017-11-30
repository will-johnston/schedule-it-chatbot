# -*- coding: utf-8 -*-

# A combination of The chatterbot Best Match logic adapter and my own scheduling adapter in order to
# deploy correctly on django


from chatterbot.logic import LogicAdapter

class my_schedule_adapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(my_schedule_adapter, self).__init__(**kwargs)

    def can_process(self, statement):
        return True

    #defined by Best Match Adapter
    def get(self, input_statement):
        """
        Takes a statement string and a list of statement strings.
        Returns the closest matching statement from the list.
        """
        statement_list = self.chatbot.storage.get_response_statements()

        if not statement_list:
            if self.chatbot.storage.count():
                # Use a randomly picked statement
                self.logger.info(
                    'No statements have known responses. ' +
                    'Choosing a random response to return.'
                )
                random_response = self.chatbot.storage.get_random()
                random_response.confidence = 0
                return random_response
            else:
                raise self.EmptyDatasetException()

        closest_match = input_statement
        closest_match.confidence = 0

        # Find the closest matching known statement
        for statement in statement_list:
            confidence = self.compare_statements(input_statement, statement)

            if confidence > closest_match.confidence:
                statement.confidence = confidence
                closest_match = statement

        return closest_match



    def extractID(self, statement) :
        string = list(statement.text.split())
        first = list(string[0])
        id = -1
        if first[0] == '<':
            #get ID
            groupID = "";
            for c in first:
                if c == '>':
                    break
                if c != '<':
                    groupID += c
            if groupID.isdigit():
                id = int(groupID)
            else:
                id = -1
        return id

    def extractPass(self, statement):
        string = list(statement.text.split())
        first = list(string[0])
        password = ""
        if first[0] == '<':
            #get pass
            for c in first:
                if c == '>':
                    break
                if c != '<':
                    password += c
        else:
            password = None
        return password 

    def removeFirstFromStatement(self, statement):
        string = statement.text.split()
        newstatement = ' '.join(string[1:])
        return newstatement

    #find the appropriate response to the statement
    def process(self, statement):
        from chatterbot.conversation import Statement
        import requests
        import datefinder
        import json
        import sys
        import copy
        from datetime import date

        #Prepare for API call
        s = requests.Session()
        cookie = None
        url = "https://scheduleit.duckdns.org/api/user/login"

        #####
        #get group id and user id

        groupID = self.extractID(statement)
        if (groupID > 0):
            statement = Statement(self.removeFirstFromStatement(statement))
        userID = self.extractID(statement)
        if (userID > 0):
            statement = Statement(self.removeFirstFromStatement(statement))
        eventID = -1
        #####
        test = list(datefinder.find_dates(str(statement)))
        print test

        #####
        #See if statement is a event creation request.
        #create event, <event name>, <set/open-ended>, <date/expiration_time>, <description>
        data = statement.text.split(",")
        if (data[0] == "create event"):
            print "CREATE EVENT"
            name = data[1].lstrip()
            mode = data[2].lstrip()
            date = data[3].lstrip()
            #MAKE SURE IS A VALID DATE
            real_dates = list(datefinder.find_dates(str(statement)))
            print str(statement)
            print name
            print mode
            print date
            print real_dates

            if (len(real_dates) != 0):
                print "found date."
            else:
                return Statement("Error: No date found for event create.")
            datetime = real_dates[0]
            print str(datetime)
            datetime = datetime.strftime("%a, %d %b %Y %H:%M:%S EST")
            
            description = ""
            if (len(data) > 4):
                description = data[4]
            data = json.dumps({"name": "Clarence", "pass": "roboto"})
            r = s.post(url, data=data)
            cookie = r.json()["cookie"]
            print cookie
            print "logged in"
            print "datetime: " + str(datetime)
            #create event
            if (mode == "set"):
                data = json.dumps({"cookie" : cookie, "name" : name, "description" : description, "type" : "Generic", "date" : str(datetime), "groupid" : groupID, "expiration_time" : "None"})
                print data
            else:
                data = json.dumps({"cookie" : cookie, "name" : name, "description" : description, "type" : "Generic", "date" : "None", "groupid" : groupID, "expiration_time" : str(datetime)})
                print data
            url = "http://scheduleit.duckdns.org/api/user/groups/calendar/add"
            r = s.post(url, data=data)
            event_statement = Statement("Event created: " + name);
            return event_statement;

        e1 = set(['show', 'events'])
        e2 = set(['get', 'events'])
        e = [e1, e2]
        split = statement.text.split(" ")
        for showevents in e:
            if (showevents.issubset(split)):
                #ask for open-ended events
                url = "https://scheduleit.duckdns.org/api/user/login"
                data = json.dumps({"name": "Clarence", "pass": "roboto"})
                r = s.post(url, data=data)
                cookie = r.json()["cookie"]
                data = json.dumps({
                    "cookie" : cookie,
                    "groupid" : groupID
                })

                url = "https://scheduleit.duckdns.org/api/user/groups/calendar/all"
                r = s.post(url, data=data)
                count = len(r.json())
                print count
                events = "Here are all the open-ended events for this group: "
                index = 0
                for x in range (0, count):
                    if (r.json()[x]["is_open_ended"] == True):
                        events += r.json()[x]["name"]
                        if (index < count - 1):
                            events += ", "
                return Statement(events)
        #####



        ######
        #see if statement is an event string
        #get events for group
        if (groupID > 0 and userID > 0):
            url = "https://scheduleit.duckdns.org/api/user/login"
            data = json.dumps({"name": "Clarence", "pass": "roboto"})
            r = s.post(url, data=data)
            cookie = r.json()["cookie"]
            data = json.dumps({
                "cookie" : cookie,

                "groupid" : str(groupID)
            })
            url = "https://scheduleit.duckdns.org/api/user/groups/calendar/all"
            r = s.post(url, data=data)
            count = len(r.json())
            events = {}
            for x in range (0, count):
                if (r.json()[x]["is_open_ended"] == True):
                    events[Statement(r.json()[x]["name"])] = r.json()[x]["id"]

            #compare events with statement with confidence threshold of .92 (spelling errors)
            for e in events:
                event_conf = self.compare_statements(e, statement)
                if (event_conf >= .92):
                    #get event id
                    eventID = events[e]
                    #add to user, group, event junction
                    if (groupID > 0 and userID > 0):
                        data = json.dumps({"groupID" : str(groupID), "eventID" : str(eventID), "userID" : str(userID)})
                        url = "https://scheduleit.duckdns.org/api/ugejunction/add"
                        r = s.post(url, data=data)
                    #return statement
                    event_statement = Statement("You can now add your preferences for the event: '" + str(e) + "'.")
                    event_statement.confidence = event_conf
                    return event_statement

        ######

        #####
        #determine if statement is for scheduleing

        words1 = set(['schedule', 'for'])
        words2 = set(['preferences', 'are'])
        words3 = set(['put', 'down'])
        words4 = set(['go', 'with'])
        words5 = set(['down', 'for'])
        words6 = set(['time', 'at'])
        words7 = set(['time', 'for'])
        words8 = set(['preference', 'is'])
        words9 = set(['schedule', 'at'])
        words10 = set(['down', 'at'])
        words11 = set(['go', 'for'])
        words12 = set(['want', 'at'])
        words13 = set(['times', 'for'])
        words14 = set(['times', 'at'])
        words15 = set(['preffered', 'for'])
        words16 = set(['set', 'for'])
        words17 = set(['set', 'at'])
        words18 = set(['choices', 'are'])
        words19 = set(['choice', 'is'])

        #use allwords to aggregate above arrays
        allwords = [words1, words2, words3, words4, words5, words6, words7,
                    words8, words9, words10, words11, words12, words13, words14,
                    words15, words16, words17, words18, words19]
        stmt = set(statement.text.split())

        is_schedule_input = False  #if true, put down user preferences for event
        is_event_input = False  # if true, switch to this event to put down preferences


        #see if user input contains any of the combinations listed in arrays above
        for lists in allwords:
            if (lists.issubset(stmt)):
                is_schedule_input = True  

        if (is_schedule_input == True) :
            # Let's base the confidence value on if the input provided dates
            confidence = 0
            response = ""
            #see if input provides group event and make sure event is open to user input.
            #>>>API CALL TO GET EVENT INFORMATION
            #>>>SEE IF AN EVENT NAME IS FOUND IN STATEMENT
            #see if input statement has dates

            matches = list(datefinder.find_dates(str(statement)))
            flag = True
            if (len(matches) != 0):
                #Create output statement
                confidence = 1
                response += "Ok. I have recorded your preferences for the time(s):\n"
                for match in matches:
                    
                    #get eventID
                    data = json.dumps({"groupID": str(groupID), "userID": str(userID)})
                    url = "https://scheduleit.duckdns.org/api/ugejunction/get"
                    r = s.post(url, data=data)
                    eventID = r.json()["eventID"]
                    
                    if (int(eventID) > 0):
                        #API call to add time preference to ScheduleIt database
                        data = json.dumps({"groupID": str(groupID), "eventID": str(eventID), "time" : str(match)})
                        url = "https://scheduleit.duckdns.org/api/timeinput/add"
                        r = s.post(url, data=data)
                        response += (str(match) + '  ')
                    else:
                        flag = False
                #response += (str(matches[-1]))
            else:
               response = "Sorry, but I don't understand. If you were trying to add your time preferences, please add a date and time to your request."
            if (flag == False):
                response = "Sorry, but I don't understand. If you were trying to add your time preferences, please make sure you add the event prior to the request. Type 'help' for a list of commands."

            response_statement = Statement(response)
            response_statement.confidence = confidence
     
            return response_statement



            # figure out where to store requests for a group event
                #if database, create junction for event
                #if file system, need a different file for every event
            #response = requests.get('https://api.temperature.com/current?units=celsius')
            #data = response.json()
            # Let's base the confidence value on if the request was successful

        #####

        #####
        #find best match

        else :
            # Select the closest match to the input statement
            closest_match = self.get(statement)
            self.logger.info('Using "{}" as a close match to "{}"'.format(
                statement.text, closest_match.text
            ))

            # Get all statements that are in response to the closest match
            response_list = self.chatbot.storage.filter(
                in_response_to__contains=closest_match.text
            )

            if response_list:
                self.logger.info(
                    'Selecting response from {} optimal responses.'.format(
                        len(response_list)
                    )
                )
                response = self.select_response(statement, response_list)
                response.confidence = closest_match.confidence
                self.logger.info('Response selected. Using "{}"'.format(response.text))
            else:
                response = self.chatbot.storage.get_random()
                self.logger.info(
                    'No response to "{}" found. Selecting a random response.'.format(
                        closest_match.text
                    )
                )

                # Set confidence to zero because a random response is selected
                response.confidence = 0
                #print response.confidence
                ######
                #low confidence adapter
            if (response.confidence < 0.65):
                response = Statement("I'm sorry, but I don't understand.")
                response.confidence = 1
                ######
            return response

        #####
        
        

