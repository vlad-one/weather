import http.server
# from thread import start_new_thread
import time
# import glob
import urllib.request
import re
import json
import sys

# airport
# https://tgftp.nws.noaa.gov/data/observations/metar/decoded/KROC.TXT

class weatherNOAA():
    
    def __init__(self, State="ny", Zone="nyz003", City="Rochester"):
        self.State=State
        self.Zone=Zone
        self.City=City
        self.dateRegEx = re.compile("[0-9]{3,4}\s+[AP]M.+\s[0-9]{4}")
        self.urlCurrent = "https://tgftp.nws.noaa.gov/data/observations/state_roundup/{}/{}.txt".format(self.State,self.Zone)
        self.urlZone = "https://tgftp.nws.noaa.gov/data/forecasts/zone/{}/{}.txt".format(self.State,self.Zone)
        self.urlState = "https://tgftp.nws.noaa.gov/data/forecasts/state/{}/{}.txt".format(self.State,self.Zone)
        return
        
    def fetchData(self,fromURL) :
        print("Reading", fromURL)
        req = urllib.request.Request(fromURL)
        req.add_header('Cache-Control', 'max-age=0')
        resp = urllib.request.urlopen(req)
        content = resp.read().decode('utf-8')
        resp.close()
        return content.split("\n")


    def getCurrent(self):
        
        content = self.fetchData(self.urlCurrent)

        """
http://tgftp.nws.noaa.gov/data/observations/metar/stations/KROC.TXT
http://tgftp.nws.noaa.gov/data/observations/metar/decoded/KROC.TXT


        2018/10/09 15:54
        KROC 091554Z 24014G20KT 10SM FEW045 FEW150 SCT250 28/20 A3018 RMK AO2 SLP219 T02830200 $
        """
    
        """
    CITY           SKY/WX    TMP DP  RH WIND       PRES   REMARKS
    ROCHESTER      CLOUDY    54  54 100 E5        30.35F FOG
        """
         
    #     reCurrentWeather = re.compile( r"(?P<city>ROCHESTER)\s+"
    #                                     "(?P<sky>\w+)\s+"
    #                                     "(?P<tmp>\w+)"
    #                                     "(?P<dp>\w+)"
    #                                     "(?P<rh>\w+)"
    #                                     "(?P<wind>\w+)"
    #                                     ".*")
        
    #    posName = {"city":0,"sky":15,"tmp":25,"dp":29,"rh":32,"wind":36,"pres":46,"rem":53,"last":100}
    #              CITY           SKY/WX    TMP DP  RH WIND       PRES   REMARKS
        pos =    ( 0,             15,       25, 29, 32,36,        46,    53,   100)
        pNames = ("city",        "sky",    "temp","dp","rh","wind","pres","rem","last")
         
        dateTimeLine = 6 
        dateTime = "None"
         
        currentLineN = 0
    
    #    print content
                
        regionData = []
        
        for ln in content :
            if currentLineN == dateTimeLine :
                dateTime = ln.strip()
            
            currentLineN +=1
            rec = {}
            s = 0
            e = 0
            for i in range (1,len(pos)) :
                e = pos[i]
                rec[pNames[i-1]]=ln[s:e].strip()
                s = e
            if rec["city"].startswith(self.City.upper()) :
                regionData = rec
                break
        if "temp" in regionData :
            tF = float(regionData["temp"])
            tC = round((tF - 32) * 10 /9 , 0 ) / 2
            regionData["temp"] = "{:.1f}C / {:.0f}F".format(tC,tF)
            regionData["time"] = dateTime 
        return regionData


    def forecasts_week(self):
        """
445 PM EST Fri Nov 30 2018

   FCST     FCST     FCST     FCST     FCST     FCST     FCST     
   Sat      Sun      Mon      Tue      Wed      Thu      Fri      
   Dec 01   Dec 02   Dec 03   Dec 04   Dec 05   Dec 06   Dec 07   

   Rochester, NY
   Rain     Rain     Snoshwr  Mocldy   Mocldy   Mocldy   Mocldy   
   30/37    37/57    42/42    27/32    26/32    25/32    25/33    
   10/60   100/60    50/70    40/30    30/20    20/20    40/40   
        """

        stateA = self.fetchData(self.urlState)

        prnt = 0
        headFound = False
        state = [[],[],[],[],[],[],[]]

        capTime = "N/A"

        for v in stateA:
            s = v.strip()
        #    print "{}".format(v.strip())

            m = self.dateRegEx.match(v)
            if m:
                capTime=v
                continue

            if s.find("FCST") >= 0:
                prnt = 2
                headFound = True
                continue

            if s.find(self.City) >= 0 and headFound:
                prnt = 3
                continue

            if prnt :
#               a=[]
                a = s.split()
                for i in range(0,7) :
                     state[i].append(a[i])
#                    j=i*9
#                    state[i].append(s[j:j+9].strip())
		
                prnt -= 1

        return {"time":capTime,"data":state}


#############################
    def forecasts_zone(self):
        """
http://tgftp.nws.noaa.gov/data/forecasts/zone/ny/nyz003.txt

930 PM EST Fri Nov 30 2018

.OVERNIGHT...Cloudy with some patchy fog. Lows around 30. Light
winds. 
.SATURDAY...Some patchy fog in the morning, otherwise cloudy. Rain
likely in the afternoon. Highs in the upper 30s. Light winds,
becoming east 5 to 10 mph. Chance of rain 60 percent. 
        """

        zone = self.fetchData(self.urlZone)

        zoneA = []
        #zoneKey = -1

        addNextLine = False

        for ln in zone :
            if len(ln) < 2 :
                addNextLine = False
                continue
            
            m = self.dateRegEx.match(ln)
            if m:
                Time=ln
                continue
            
            if ln[0] == ".":
                e = ln.find("...")
                if e > 0:
                    lnA = ln[1:].replace("...","#",1)
                    zoneA.append(lnA.split("#"))
                    addNextLine = True
                continue    

            if addNextLine :
                zoneA[-1][1] += " " + ln
                continue
        # TODO error checking
        return {"time":Time,"data":zoneA}

#######################################

    """
http://tgftp.nws.noaa.gov/data/forecasts/nowcast/ny/nyz003.txt - outdated


    """


if __name__ == "__main__" :

    W = weatherNOAA()

    jsonOut={"reportTime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), \
              "weather_now":W.getCurrent() ,\
              "forecasts_week":W.forecasts_week(),\
              "forecasts_zone":W.forecasts_zone()}

    print( json.dumps(jsonOut))
    if len(sys.argv) > 1 :
        with open(sys.argv[1],"w") as jsonFile:
            jsonFile.write(json.dumps(jsonOut)+"\n")
