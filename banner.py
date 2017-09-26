#!/usr/bin/python2.7
import os;
import sys;
import bleach;
import StringIO;
import json;
import subprocess;
import cgi;
import cgitb;
cgitb.enable();
import valve.source.a2s;
from PIL import Image;
from PIL import ImageFont;
from PIL import ImageDraw;

# Print content type (png) to return an image
print("Content-Type: image/png\r\n");

# List of all available background images for the banner
banners = {
	'battlefield_map': 'battlefield_map.png',
        'british_advance': 'british_advance.png',
        'british_march': 'british_march.png',
        'cavalry': 'cavalry.png',
        'nw_french': 'nw_french.png',
        'french_march': 'french_march.png',
        'borodino': 'borodino.png',
        'french_winter': 'french_winter.png',
        'line_charge': 'line_charge.png',
        'line_troops': 'line_troops.png',
        'naval_battle': 'naval_battle.png',
        'naval_battle2': 'naval_battle2.png',
        'naval_battle3': 'naval_battle3.png',
        'blockade': 'blockade.png',
        'naval_engagement': 'naval_engagement.png'
};

# List of all available colors for the labels
color = {
	'black': (0,0,0),
	'white': (255,255,255),
	'blue': (0,0,255),
	'red': (255,0,0),
	'green': (0,255,0),
	'yellow': (255,255,0)
};

# Directory where image assets exist
images_directory = "./images/";
# Initialize the buffer to store the generated image in memory
buff = StringIO.StringIO();

# Grab and parse the URL arguments after filtering with bleach
arguments = cgi.FieldStorage();
ip = bleach.clean(arguments["ip"].value);
port = bleach.clean(arguments["port"].value);
banner = banners[bleach.clean(arguments["banner"].value)];
label_color = color[bleach.clean(arguments["label"].value)];

# Set up server address for server query
SERVER_ADDRESS = (ip, int(port));

# Open selected background image and setup draw and font handlers
img = Image.open(os.path.join(images_directory, banner)).convert('RGBA');
draw = ImageDraw.Draw(img);
font1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 14);
font2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18);

# If an error occurs, i.e. can't reach the server, return an error image
def return_error():
	error = 'Error Retrieving Server Details';
	w, h = draw.textsize(error, font2);
	draw.text((249-(w/2),1),error,(0,0,0),font=font2);
	draw.text((251-(w/2),1),error,(0,0,0),font=font2);
	draw.text((249-(w/2),3),error,(0,0,0),font=font2);
	draw.text((251-(w/2),3),error,(0,0,0),font=font2);
	draw.text((250-(w/2),2),error,(255,0,0),font=font2);
	img.save(buff, 'png'); # Save to buffer
	print(buff.getvalue()); # Return image
	buff.close(); # Cleanup
	sys.exit(0); # Stop running

try: 
	# Attempt to get server details using the provided server ip and query port
	with valve.source.a2s.ServerQuerier(SERVER_ADDRESS) as server:
		info = server.info()
except:
	# If an error occured during query, return error image
	return_error();

# After sucessful query, parse server information
serverName = bleach.clean(info["server_name"]);
serverMap = bleach.clean(info["map"]);
serverPlayers = bleach.clean(str(info["player_count"])) + " / " + bleach.clean(str(info["max_players"]));
serverPassword = bleach.clean(str(info["password_protected"]));

# Determine if server has a password or not and assign corresponding lock image
if serverPassword == "0":
	lock = Image.open(os.path.join(images_directory, 'unlocked.png')).convert('RGBA');
else:
	lock = Image.open(os.path.join(images_directory, 'locked.png')).convert('RGBA');

# Draw Game Name
game = 'Holdfast: Nations At War'
w, h = draw.textsize(game, font2);
draw.text((249-(w/2),1),game,(0,0,0),font=font2);
draw.text((251-(w/2),1),game,(0,0,0),font=font2);
draw.text((249-(w/2),3),game,(0,0,0),font=font2);
draw.text((251-(w/2),3),game,(0,0,0),font=font2);
draw.text((250-(w/2),2),game,(255,255,255),font=font2);

# Draw Server Name
draw.text((8, 38),'Server Name:',label_color,font=font1);
draw.text((9, 50),serverName,(0,0,0),font=font2);
draw.text((11, 50),serverName,(0,0,0),font=font2);
draw.text((9, 52),serverName,(0,0,0),font=font2);
draw.text((11, 52),serverName,(0,0,0),font=font2);
draw.text((10, 51),serverName,(255,255,255),font=font2);

# Draw Current Map
w, h = draw.textsize('Current Map:', font1);
draw.text((8, 88),'Current Map:',label_color,font=font1);
w, h = draw.textsize(serverMap, font2);
draw.text((9, 100),serverMap,(0,0,0),font=font2);
draw.text((11, 100),serverMap,(0,0,0),font=font2);
draw.text((9, 102),serverMap,(0,0,0),font=font2);
draw.text((11, 102),serverMap,(0,0,0),font=font2);
draw.text((10, 101),serverMap,(255,255,255),font=font2);

# Draw Number of Players
w, h = draw.textsize('Current Players:', font1);
draw.text((492-w, 88),'Current Players:',label_color,font=font1);
w, h = draw.textsize(serverPlayers, font2);
draw.text((489-w, 100),serverPlayers,(0,0,0),font=font2);
draw.text((491-w, 100),serverPlayers,(0,0,0),font=font2);
draw.text((489-w, 102),serverPlayers,(0,0,0),font=font2);
draw.text((491-w, 102),serverPlayers,(0,0,0),font=font2);
draw.text((490-w, 101),serverPlayers,(255,255,255),font=font2);

# Draw Lock/Unlocked Symbol
img.paste(lock, (474,4));

# Output final image
img.save(buff, 'png'); # Save the modified image to the buffer
print(buff.getvalue()); # Return the image
buff.close(); # Cleanup
