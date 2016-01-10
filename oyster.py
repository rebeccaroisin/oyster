import csv
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pygraphviz as pgv
import seaborn as sns
import math as ma



class journey():
    def __init__(self, startStation, endStation, startTime, endTime, day, payment):
        self.startStation = startStation
        self.endStation = endStation
        self.startTime = startTime
        self.endTime = endTime
        self.day = day
        self.payment = payment



def parseData(f):
    # parse data from csv to journey class
    journeys = {}
    with open(f, "r") as datas:
        dataParser = csv.reader(datas)
        for i, row in enumerate(dataParser):
            if i > 0:
                if i % 1000 == 0:
                    print i
                if (row[2] == "LUL"):
                    startStation = row[3]
                    endStation = row[4]
                    startTime = int(row[5])
                    endTime = int(row[7])
                    day = row[1]
                    payment = row[10]   

                    currentJourney = journey(startStation, endStation, startTime, endTime, day, payment)
                    if startStation not in journeys:
                        journeys[startStation] = []
                    journeys[startStation].append(currentJourney)
    return journeys
            


def plotNetwork(journeys):
    # make graph object
    G = nx.DiGraph()
    for journeyList in journeys.itervalues():
        for journey in journeyList:
            if journey.startStation != "Unstarted" and journey.endStation != "Unfinished":
                if G.has_edge(journey.startStation, journey.endStation) != True:
                    G.add_edge(journey.startStation, journey.endStation, weight = 0)
                G[journey.startStation][journey.endStation]['weight'] += 1
    return G


def plotDestinations(journeyList, name):
    # plot destinations
    G = nx.DiGraph()
    for journey in journeyList:
        if journey.day != "Sat" and journey.day != "Sun":
            if G.has_edge(journey.startStation, journey.endStation) != True:
                G.add_edge(journey.startStation, journey.endStation, weight = 0)
            G[journey.startStation][journey.endStation]['weight'] += 1
    return G



def plotHistogram(journeys):
    # histograms of start times
    for startStation, journeyList in journeys.iteritems():
        journeyTimes = []
        #if startStation == "Oxford Circus":
        #if len(journeyList) > 4000 and startStation != "Unstarted":
        if startStation in ["Walthamstow Central", "Blackhorse Road", "Seven Sisters", "Finsbury Park", "Highbury", "Tottenham Hale"]:
            print startStation
            for journ in journeyList:
                if (journ.day != "Sat") and (journ.day != "Sun"):
                    journeyTimes.append(float(journ.startTime) / 60)
            plt.hist(journeyTimes, bins=np.arange(0, 24, 0.25), histtype="step", label=startStation, normed=True, linewidth=2)
    plt.legend(loc="upper left")
    plt.show()

def main():
    # set up seaborn plotting environment
    sns.set_style("white") #{'axes.linewidth': 5.0})
    sns.color_palette("hls", 6)

    print "starting parsing"
    dataFile = "data/Nov09JnyExport.csv"
    journeys = parseData(dataFile)
    for startStation in sorted(journeys.keys()):
        print "%s: %s" % (startStation, len(journeys[startStation]))
    print len(journeys.keys())
    plotHistogram(journeys)
    G = plotNetwork(journeys)

    G2 = nx.DiGraph()
    for (u, v) in G.edges():
        w =  G[u][v]['weight']
        if w > 300:
            G2.add_edge(u, v, weight=w)

    for k, v, a in G2.edges(data=True):
        print k, v, a['weight']
    pos=nx.to_agraph(G2)
    pos.graph_attr['size']='10,10!'
    pos.graph_attr['ratio']='fill'
    pos.layout(prog='neato')
    pos.draw("hairyballs.png")

    for startStation, journeyList in journeys.iteritems():
        Gs= plotDestinations(journeyList, startStation)
        Gme = nx.MultiDiGraph()
        if len(list(Gs.edges())) > 10:
            for (u, v) in Gs.edges():
                w =  Gs[u][v]['weight']
                for i in range(int(ma.ceil(w / 50)) + 1):
                    Gme.add_edge(u, v)

            pos=nx.to_agraph(Gme)
            #pos.graph_attr['size']='10,10!'
            #pos.graph_attr['ratio']='fill'
            pos.graph_attr['repulsiveforce'] = 5
            pos.graph_attr['K'] = 1.5
            pos.layout(prog='fdp')
            pos.draw("hairyballs_%s.png" % startStation)

    


if __name__ == "__main__":
    main()

# csv fields
#0 downo - a number between 1 and 7, 1 being Sunday, 2 being Monday etc
#1 daytype - Sun to Sat
#2 SubSystem - the mode(s) of the journey. LUL - London Underground, NR - National Rail, LTB - London Buses, DLR- Docklands Light Railway, LRC - London Overground, TRAM - Croydon Tram
#3 StartStn - Station the journey started at
#4 EndStation - Station the journey ended at
#5 EntTime - Entry time of the journey in minutes after midnight
#6 EntTimeHHMM - Entry time in HH:MM text format
#7 ExTime - Exit time of the journey in minutes after midnight
#8 EXTimeHHMM - Exit time in HH:MM text format
#9 ZVPPT - zones of Oyster Season ticket, if used
#10 JNYTYP - Product types involved in the journey. PPY - Pure PAYG, TKT - Pure Oyster Season, MIXED - Combined PAYG and Oyster Season
#11 DailyCapping - it shows as Y when PAYG journey was capped
#12 FFare - Full PAYG Fare before any discounts
#13 Dfare - PAYG Fare after usage based discounts
#14 RouteID - The Route Number of the Bus, if a Bus has been boarded
#15 FinalProduct - Combined Product Description used for journey
