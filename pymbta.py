import requests
import os
import json
import Adafruit_CharLCD as LCD

"""

    pymbta is a library that takes the pain out of querying the MBTA api to find bus/train locations.

    For example code and documentation goto:
        https://github.com/johnsliao/pymbta

    The MBTA publishes its data via GTFS-realtime feeds, a standard developed by Google for delivering realtime data.
    MBTA GTFS files available here:
        http://www.mbta.com/uploadedfiles/MBTA_GTFS.zip

    Read more about using the MBTA-realtime API v2 here:
        http://www.mbta.com/rider_tools/

    If you encounter a bug, file an issue or email me:
        john@johnliao.org

"""


__author__ = 'John Liao <john@johnliao.org>'
__version__ = '1.1'


lcd = LCD.Adafruit_CharLCDPlate()


class MBTA(object):
    QUERY_TYPES = ['vehiclesbyroute', 'vehiclesbytrip', 'predictionsbystop']
    DIRECTIONS = []
    FORMATS = ['json', 'xml']
    LOCATIONS = []
    ROUTES = {}

    def __init__(self, format='json', direction=None, query_type=None, stop=None):
        self.base_url = 'http://realtime.mbta.com/developer/api/v2/'
        self.key = os.environ.get('MBTA_API_KEY')
        self.format = format
        self.direction = direction
        self.query_type = query_type
        self.stop = stop
        self.url = ''
        self.response = ''

    def check_parameters(self):
        if self.format not in self.FORMATS:
            raise ValueError('[%s] is not a valid query format. Valid formats include %s' %
                             (self.format, self.FORMATS))

        if not any(d for d in self.DIRECTIONS if self.direction.lower() in self.DIRECTIONS):
            raise ValueError('[%s] is not a valid direction. Valid directions include %s' %
                             (self.direction, self.DIRECTIONS))

        if self.query_type not in self.QUERY_TYPES:
            raise ValueError('[%s] is not a valid MBTA query type. Valid query types include %s' %
                             (self.query_type, self.QUERY_TYPES))

    def check_api_response(self):
        if 'error' in self.response:
            raise ValueError(
                'No MBTA available data for %s stop' % self.stop)

    def return_route_id(self, route):
        return self.ROUTES[route]
    
    def return_stop_id(self, stop):
        return stop

    def generate_url(self):
        self.check_parameters()
        self.route_id = self.return_route_id(self.route)

        self.url = '%s%s?api_key=%s&route=%s&format=%s' % (
            self.base_url,
            self.query_type,
            self.key,
            self.route_id,
            self.format)
        
    def generate_url_predictions(self):
        self.check_parameters()
        self.stop = self.return_stop_id(self.stop)

        self.url = '%s%s?api_key=%s&stop=%s&format=%s' % (
            self.base_url,
            self.query_type,
            self.key,
            self.stop,
            self.format)

    def make_api_request(self):
        result = requests.get(self.url)
        #print result.text
        self.response = json.loads(result.text)

    def return_locations(self):
        self.LOCATIONS = []
        self.generate_url()
        self.make_api_request()
        self.check_api_response()

        directions = self.response['direction']

        for direction in directions:
            if direction['direction_name'].lower() == self.direction.lower():
                trips = direction['trip']
                for trip in trips:
                    lat = trip['vehicle']['vehicle_lat']
                    lon = trip['vehicle']['vehicle_lon']

                    self.LOCATIONS.append([lat, lon])

        if len(self.LOCATIONS) is 0:
            return None

        return self.LOCATIONS
    
    def return_predictions(self):
        self.LOCATIONS = []
        self.generate_url_predictions()
        self.make_api_request() 

        print self.response
        print len(self.response)
        
        if len(self.response) > 3:
            predictions = self.response['mode'][0]['route'][0]['direction'][0]['trip']
            
            walkBuffer = 8 # for Central Sq
            mitString = ""
            tempString = ""
            bus1 = 0
            textToSpeak = ""
	    printstring = ""

            for prediction in predictions:
		headsignText = "Unknown"

		if 'pre_away' in prediction:
                    secondsLeft = int(prediction['pre_away'])

		    secondsMod = secondsLeft % 60
		    minutesLeft = (secondsLeft - secondsMod) / 60
              	    
                    if minutesLeft < walkBuffer:
                        # train is too close to walk to from safetyfourth
                        continue
		    if 'trip_headsign' in prediction:
			headsignText = prediction['trip_headsign']
			
                        if prediction['trip_headsign'] == 'Alewife':
                            tempString = str(minutesLeft).rjust(2) + 'm Alewife   RD\n'
                        elif prediction['trip_headsign'] == 'Braintree':
                            tempString = str(minutesLeft).rjust(2) + 'm Braintree RD\n'
                        elif prediction['trip_headsign'] == 'Ashmont':
                            tempString = str(minutesLeft).rjust(2) + 'm Ashmont   RD\n'
                        elif prediction['trip_headsign'] == 'North Quincy':
                            tempString = str(minutesLeft).rjust(2) + 'm N Quincy  RD\n'
                        elif prediction['trip_headsign'] == 'JFK/UMass':
                            tempString = str(minutesLeft).rjust(2) + 'm JFK/UMass RD\n'
                        elif prediction['trip_headsign'] == 'Quincy Center':
                            tempString = str(minutesLeft).rjust(2) + 'm Quincy    RD\n'
                        elif prediction['trip_headsign'] == 'Park Street':
                            tempString = str(minutesLeft).rjust(2) + 'm Park St   RD\n'
			elif prediction['trip_headsign'] == 'Park':
                            tempString = str(minutesLeft).rjust(2) + 'm Park St   RD\n'
			elif prediction['trip_headsign'] == 'Park St':
                            tempString = str(minutesLeft).rjust(2) + 'm Park St   RD\n'
                        elif prediction['trip_headsign'] == 'Kendall':
                            tempString = str(minutesLeft).rjust(2) + 'm Kendall   RD\n'
			elif prediction['trip_headsign'] == 'Kendall/MIT':
                            tempString = str(minutesLeft).rjust(2) + 'm Kendall   RD\n'
                        elif prediction['trip_headsign'] == 'Harvard':
                            tempString = str(minutesLeft).rjust(2) + 'm Harvard   RD\n'
		    else:
			tempString = str(minutesLeft).rjust(2) + 'm Unknown   RD\n'
                    
                if len(mitString) < 5:
                    textToSpeak = "The next. Red Line. Train. To." + headsignText + ". Arrives in," + str(minutesLeft) + ", minutes."
                    mitString = tempString
                    if minutesLeft > walkBuffer + 6:
                            lcd.set_color(0,0,1)    # BLUE
                    if (minutesLeft > walkBuffer + 3) and (minutesLeft <= walkBuffer + 6):
                            lcd.set_color(0,1,0)    # GREEN
                    if minutesLeft <= walkBuffer + 3:
                            lcd.set_color(1,0,0)    # RED

		    if minutesLeft == walkBuffer + 3:
			    print minutesLeft
		    	    #os.system("aplay /home/pi/Adafruit_Python_CharLCD/two_tone.wav")
                elif (len(mitString) < 25) and (len(mitString) > 10):
                    mitString = mitString + tempString
                    
            if mitString == "":
	    	mitString = "No RD service is\n" + "predicted       "
                printstring = mitString
                lcd.clear()
		lcd.set_color(1,0,0)    # RED
                lcd.message(mitString)
		textToSpeak = "No services on the Red Line are currently operating."
            elif mitString != printstring:
                printstring = mitString
                lcd.clear()
                lcd.message(mitString)
                
        else:
            mitString = "No RD service is\n" + "predicted       "
	    printstring = mitString
            lcd.clear()
	    lcd.set_color(1,0,0)    # RED
            lcd.message(mitString)
	    textToSpeak = "No services on the Red Line are currently operating."
                
        return textToSpeak


class PurpleLine(MBTA):

    ROUTES = {"Fairmount": "CR-Fairmount",
              "Fitchburg": "CR-Fitchburg",
              "Framingham/Worcester": "CR-Worcester",
              "Franklin": "CR-Franklin",
              "Greenbush": "CR-Greenbush",
              "Haverhill": "CR-Haverhill",
              "Lowell": "CR-Lowell",
              "Needham": "CR-Needham",
              "Newburyport/Rockport": "CR-Newburyport",
              "Providence/Stoughton": "CR-Providence",
              "Kingston/Plymouth": "CR-Kingston",
              "Middleborough/Lakeville": "CR-Middleborough",
              }
    DIRECTIONS = ['inbound', 'outbound']

    def __init__(self, query_type=None, direction=None, format='json', route=None):
        MBTA.__init__(
            self, query_type=query_type, direction=direction, format=format, route=route)


class RedLine(MBTA):
    DIRECTIONS = ['southbound', 'northbound']

    def __init__(self, query_type=None, direction=None, format='json', stop=None):
        MBTA.__init__(
            self, query_type=query_type, direction=direction, format=format, stop=stop)


class GreenLine(MBTA):
    ROUTES = {"Green Line B": "Green-B",
              "Green Line C": "Green-C",
              "Green Line D": "Green-D",
              "Green Line E": "Green-E",
              }
    DIRECTIONS = ['westbound', 'eastbound']

    def __init__(self, query_type=None, direction=None, format='json', route=None):
        MBTA.__init__(
            self, query_type=query_type, direction=direction, format=format, route=route)


class OrangeLine(MBTA):
    ROUTES = {"Orange Line": "Orange", }
    DIRECTIONS = ['southbound', 'northbound']

    def __init__(self, query_type=None, direction=None, format='json', route=None):
        MBTA.__init__(
            self, query_type=query_type, direction=direction, format=format, route=route)


class BlueLine(MBTA):
    ROUTES = {"Blue Line": "Blue", }
    DIRECTIONS = ['westbound', 'eastbound']

    def __init__(self, query_type=None, direction=None, format='json', route=None):
        MBTA.__init__(
            self, query_type=query_type, direction=direction, format=format, route=route)


class Bus(MBTA):
    ROUTES = {"SL1": "741",
              "SL2": "742",
              "SL4": "751",
              "SL5": "749",
              "CT1": "701",
              "CT2": "747",
              "CT3": "708",
              "1": "1",
              "4": "4",
              "5": "5",
              "7": "7",
              "8": "8",
              "9": "9",
              "10": "10",
              "11": "11",
              "14": "14",
              "15": "15",
              "16": "16",
              "17": "17",
              "18": "18",
              "19": "19",
              "21": "21",
              "22": "22",
              "23": "23",
              "24": "24",
              "24/27": "2427",
              "26": "26",
              "27": "27",
              "28": "28",
              "29": "29",
              "30": "30",
              "31": "31",
              "32": "32",
              "32/33": "3233",
              "33": "33",
              "34": "34",
              "34E": "34E",
              "35": "35",
              "36": "36",
              "37": "37",
              "37/38": "3738",
              "38": "38",
              "39": "39",
              "40": "40",
              "40/50": "4050",
              "41": "41",
              "42": "42",
              "43": "43",
              "44": "44",
              "45": "45",
              "47": "47",
              "50": "50",
              "51": "51",
              "52": "52",
              "55": "55",
              "57": "57",
              "57A": "57A",
              "59": "59",
              "60": "60",
              "62": "62",
              "62/76": "627",
              "64": "64",
              "65": "65",
              "66": "66",
              "67": "67",
              "68": "68",
              "69": "69",
              "70": "70",
              "70A": "70A",
              "71": "71",
              "72": "72",
              "72/75": "725",
              "73": "73",
              "74": "74",
              "75": "75",
              "76": "76",
              "77": "77",
              "78": "78",
              "79": "79",
              "80": "80",
              "83": "83",
              "84": "84",
              "85": "85",
              "86": "86",
              "87": "87",
              "88": "88",
              "89": "89",
              "89/93": "8993",
              "90": "90",
              "91": "91",
              "92": "92",
              "93": "93",
              "94": "94",
              "95": "95",
              "96": "96",
              "97": "97",
              "99": "99",
              "100": "100",
              "101": "101",
              "104": "104",
              "105": "105",
              "106": "106",
              "108": "108",
              "109": "109",
              "110": "110",
              "111": "111",
              "112": "112",
              "114": "114",
              "116": "116",
              "116/117": "116117",
              "117": "117",
              "119": "119",
              "120": "120",
              "121": "121",
              "131": "131",
              "132": "132",
              "134": "134",
              "136": "136",
              "137": "137",
              "170": "170",
              "171": "171",
              "195": "195",
              "201": "201",
              "202": "202",
              "210": "210",
              "211": "211",
              "212": "212",
              "214": "214",
              "214/216": "214216",
              "215": "215",
              "216": "216",
              "217": "217",
              "220": "220",
              "221": "221",
              "222": "222",
              "225": "225",
              "230": "230",
              "236": "236",
              "238": "238",
              "240": "240",
              "245": "245",
              "325": "325",
              "326": "326",
              "350": "350",
              "351": "351",
              "352": "352",
              "354": "354",
              "411": "411",
              "424": "424",
              "426": "426",
              "428": "428",
              "429": "429",
              "430": "430",
              "431": "431",
              "434": "434",
              "435": "435",
              "436": "436",
              "439": "439",
              "441": "441",
              "441/442": "441442",
              "442": "442",
              "448": "448",
              "449": "449",
              "450": "450",
              "451": "451",
              "455": "455",
              "456": "456",
              "459": "459",
              "465": "465",
              "501": "501",
              "502": "502",
              "503": "503",
              "504": "504",
              "505": "505",
              "553": "553",
              "554": "554",
              "556": "556",
              "558": "558",
              "608": "608",
              "710": "710",
              "712": "712",
              "713": "713",
              "714": "714",
              "716": "716",
              "9701": "9701",
              "9702": "9702",
              "9703": "9703",
              "Shuttle": "Logan-22",
              "Shuttle": "Logan-33",
              "Shuttle": "Logan-55",
              "Shuttle": "Logan-44",
              "Shuttle": "Logan-66", }

    DIRECTIONS = ['outbound', 'inbound']

    def __init__(self, query_type=None, direction=None, format='json', stop=None):
        MBTA.__init__(
            self, query_type=query_type, direction=direction, format=format, stop=stop)
