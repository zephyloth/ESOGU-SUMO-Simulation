import traci
import pygame

sumoBinary = "..\\sumo-gui.exe"
sumoCmd = [sumoBinary, "-c", "esogu.sumocfg"]

# Initialize Pygame
pygame.init()
pygame.display.set_caption("Electric Car Data")

# Set up the Pygame window
screen = pygame.display.set_mode((1200, 420))
font = pygame.font.SysFont("Arial", 24)

#Resource loading
car_img = pygame.image.load("ECar.png")
car_img = car_img.convert_alpha()

traci.start(sumoCmd)
 
#Vehicle Type properties
vehicle_maxbattery = float(traci.vehicletype.getParameter("Electric-Car", "maximumBatteryCapacity"))
vehicle_mingap = 2.00

#Vehicle Routes
vehicle_station_routes = {}
vehicle_station_routes["Car1"] = [0, ["cs_-E39_0a", "cs_K16_0a",]]
vehicle_station_routes["Car2"] = [0, ["cs_-E39_0a", "cs_K16_0a", "cs_-E39_0a"]]
vehicle_station_routes["Car3"] = [0, ["cs_-E39_0a", "cs_K16_0a", "cs_-E39_0a"]]

#Add Vehicles
traci.vehicle.add(vehID="Car1", routeID="Route_C1", typeID="Electric-Car")
traci.vehicle.setStop(vehID="Car1", edgeID=vehicle_station_routes["Car1"][1][0], flags = traci.tc.STOP_CHARGING_STATION)

traci.vehicle.add(vehID="Car2", routeID="Route_C2", typeID="Electric-Car")
traci.vehicle.setStop(vehID="Car2", edgeID=vehicle_station_routes["Car2"][1][0], flags = traci.tc.STOP_CHARGING_STATION)

traci.vehicle.add(vehID="Car3", routeID="Route_C3", typeID="Electric-Car")
traci.vehicle.setStop(vehID="Car3", edgeID=vehicle_station_routes["Car3"][1][0], flags = traci.tc.STOP_CHARGING_STATION)

#Point of Interest IDs
vehicle_poi_ids = {}

while traci.simulation.getMinExpectedNumber() > 0:   
    #Pygame event system
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    screen.fill((0, 0, 0))    
 
    #Vehicle Information
    vehicle_ids = traci.vehicle.getIDList()
    vehicle_index = 0
    for vehicle_id in vehicle_ids:

        vehicle_pos = traci.vehicle.getPosition(vehicle_id)
        vehicle_posx = round(vehicle_pos[0],2)
        vehicle_posy = round(vehicle_pos[1],2)
        vehicle_speed =  round(traci.vehicle.getSpeed(vehicle_id),2)
        vehicle_accel = round(traci.vehicle.getAcceleration(vehicle_id),2) 
        vehicle_type = traci.vehicle.getTypeID(vehicle_id)
        vehicle_battery = round(float(traci.vehicle.getParameter(vehicle_id, "device.battery.actualBatteryCapacity")),2)
        vehicle_totalEnergyComsumed = round(float(traci.vehicle.getParameter(vehicle_id, "device.battery.totalEnergyConsumed")),2)
        vehicle_distance = round(float(traci.vehicle.getDistance(vehicle_id)), 2)
 
        if vehicle_distance == 0:
            estimated_range = 0
        else:
            vehicle_energy_per_distance = vehicle_totalEnergyComsumed / vehicle_distance
            estimated_range = round(vehicle_battery / vehicle_energy_per_distance, 2)

        stationid = traci.vehicle.getParameter(vehicle_id, "device.battery.chargingStationId")
        leader = traci.vehicle.getLeader(vehicle_id, 2*vehicle_mingap)

        #Wait till charge ends
        if stationid != "NULL" and vehicle_battery == vehicle_maxbattery and leader is None:
            traci.vehicle.resume(vehicle_id)
            vehicle_station_routes[vehicle_id][0]+=1
            current_station = vehicle_station_routes[vehicle_id][0];

            if current_station < len(vehicle_station_routes[vehicle_id][1]):
                traci.vehicle.setStop(vehID=vehicle_id, edgeID=vehicle_station_routes[vehicle_id][1][current_station], flags = traci.tc.STOP_CHARGING_STATION)
            
        #Point of Interest
        if vehicle_id not in vehicle_poi_ids:
            poi_id = f"poi_{vehicle_id}"
            traci.poi.add(poi_id, vehicle_pos[0], vehicle_pos[1], (255,0,255,255), vehicle_battery)
            vehicle_poi_ids[vehicle_id] = poi_id
        else:
            poi_id = vehicle_poi_ids[vehicle_id]
            traci.poi.setPosition(poi_id, vehicle_pos[0], vehicle_pos[1])
            traci.poi.setType(poi_id, vehicle_battery)
        
        #Render info to screen
        Scr_X = 10 + vehicle_index* 390
        Scr_Y = 10
        white = (255, 255, 255)
        
        screen.blit(font.render(vehicle_id, True, white), (Scr_X, Scr_Y))
        Scr_Y += 25
        screen.blit(font.render("Type: " + vehicle_type, True, white), (Scr_X, Scr_Y))
        Scr_Y += 25
        screen.blit(font.render("X Coord: " + str(vehicle_posx), True, white), (Scr_X, Scr_Y))
        Scr_Y += 25
        screen.blit(font.render("Y Coord: " + str(vehicle_posy), True, white), (Scr_X, Scr_Y))
        Scr_Y += 25
        screen.blit(font.render("Speed: " + str(vehicle_speed) + " m/s", True, white), (Scr_X, Scr_Y))
        Scr_Y += 25
        screen.blit(font.render("Acceleration: " + str(vehicle_accel) +" m/s2", True, white), (Scr_X, Scr_Y))   
        Scr_Y += 25    
        screen.blit(font.render("Distance: " + str(vehicle_distance) + " m", True, white), (Scr_X, Scr_Y))
        Scr_Y += 25    
        screen.blit(font.render("Total Energy Consumed: " + str(vehicle_totalEnergyComsumed) + " W", True, white), (Scr_X, Scr_Y))
        Scr_Y += 25   
        screen.blit(font.render("Vehicle Battery: " + str(vehicle_battery) + " W", True, white), (Scr_X, Scr_Y))
        Scr_Y += 25        
        screen.blit(font.render("Estimated Range: " + str(estimated_range) + " m", True, white), (Scr_X, Scr_Y))
        Scr_Y += 25    
 
        if leader is not None:
            screen.blit(font.render("Leader Vehicle: " + leader[0], True, white), (Scr_X, Scr_Y))
        else:
            screen.blit(font.render("Leader Vehicle: NULL", True, white), (Scr_X, Scr_Y))
        Scr_Y += 25
        
        if stationid != "NULL":
            screen.blit(font.render("State: Charging", True, white), (Scr_X, Scr_Y))
        else:
            screen.blit(font.render("State: Traveling", True, white), (Scr_X, Scr_Y))
        Scr_Y += 25

        screen.blit(car_img, (Scr_X, Scr_Y))
        Scr_Y += 25

        vehicle_index = vehicle_index+1    

    pygame.display.flip()
    traci.simulationStep()

# Close the connection to SUMO
traci.close()