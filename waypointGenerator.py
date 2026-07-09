try:
    import pysimplegui
except ModuleNotFoundError:
    useGUI = True
else:
    useGUI = False

print("Usage:")
print("Enter the name of the mission you want to create")
print("Then enter the waypoint coordinates in the format")
print("Lat Dir Long Dir [-n Name] [-i Icon] [-r Detection Radius] [-a Always Render] [-s Sequential]")
print(
    """Note that coords should be given in DMS, Dir should be N S W E and 
    name should be a single value"""
    )
fname = input("Enter the path name: ")
count = 1
point = input("Point " + str(count) + "> ")
file = open(".\\Waypoint missions\\" + fname + ".wp", "w")
while point != "":
    pointList = point.split(" ")
    lat = [pointList[0], pointList[1]]
    long = [pointList[2], pointList[3]]
    name = ""
    icon = "Sphere"
    detRadius = "10"
    alwaysRender = "False"
    sequential = "True"
    try:
        if "-n" in pointList:
            name = pointList[pointList.index("-n") + 1] 
        elif "-i" in pointList:
            icon = pointList[pointList.index("-i") + 1]
        elif "-r" in pointList:
            detRadius = pointList[pointList.index("-r") + 1]
        elif "-a" in pointList:
            alwaysRender = pointList[pointList.index("-a") + 1]
        elif "-s" in pointList:
            sequential = pointList[pointList.index("-s") + 1]
    except IndexError:
        print("One of the arguments didn't have a follow up.")
    file.write(
        lat[0] + lat[1] + "," 
        + long[0] + long[1] + ","
        + name + ","
        + icon + ","
        + detRadius + ","
        + alwaysRender + ","
        + sequential + "\n"
    )
    count += 1
    point = input("Point " + str(count) + "> ")
file.close()