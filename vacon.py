import sys
import urllib.request
import json

class Player():
	def __init__(self, playerSummary):
		self.steamid = playerSummary['steamid']		
		self.personaname = playerSummary['personaname']
		self.avatarfull = playerSummary['avatarfull']	
		self.profileurl = playerSummary['profileurl']
		self.VACBanned = False


def getFriendsSteamids(steamid):
	"""Returns a List of Strings containing the 64-bit Steam IDs of the friends of the steam ID parameter"""

	friendsResponse = urllib.request.urlopen('http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=' 
		+ APIKey 
		+ '&steamid='
		+ steamid 
		+ '&relationship=friend')

	friendsJSON = friendsResponse.read().decode('utf-8')
	friends = json.loads(friendsJSON)['friendslist']['friends']
	friendsSteamids = []

	for friend in friends:
		friendsSteamids.append(friend['steamid'])

	return friendsSteamids
		

def getPlayersBySteamids(listOfSteamids):
	"""Builds and returns a List of Player objects based on the list of Steam IDs passed."""
	

	splitList=[listOfSteamids[x:x+100] for x in range(0, len(listOfSteamids), 100)]	#We split the list because the Steam Web API only processes the first 100 Steam IDs passed.
	players = []

	for sublist in splitList:
		summariesRequestString = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=' + APIKey + '&steamids='
		bansRequestString = 'http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key=' + APIKey + '&steamids='
		for steamid in sublist:
			summariesRequestString+= steamid
			summariesRequestString+= ','

			bansRequestString+= steamid
			bansRequestString+= ','

		summariesResponse = urllib.request.urlopen(summariesRequestString)		
		summariesJSON = summariesResponse.read().decode('UTF-8')

		playerSummaries = json.loads(summariesJSON)['response']['players']
		for playerSummary in playerSummaries:
			players.append(Player(playerSummary))

		bansResponse = urllib.request.urlopen(bansRequestString)
		bansJSON = bansResponse.read().decode('UTF-8')

		playerBans = json.loads(bansJSON)['players']

		for playerBan in playerBans:
			if (playerBan['VACBanned'] == True):
				for player in players:
					if (playerBan['SteamId'] == player.steamid):
						player.VACBanned = True


	return players

APIKey = 'INSERTYOURAPIKEYHERE'

if (len(sys.argv) != 2):
	print('Invalid or no arguments passed')

else:
	steamid = sys.argv[1]
	friendsSteamids = getFriendsSteamids(steamid)
	players = getPlayersBySteamids(friendsSteamids)

	VACBans = 0
	for player in players:
		print('Steam ID: ' + player.steamid)
		try:
			print('Persona Name: ' + player.personaname)
		except UnicodeEncodeError:
			print('Persona Name: ' + str(player.personaname.encode('UTF-8')))

		print('VACBanned: ' + str(player.VACBanned) + '\n')

		if player.VACBanned:
			VACBans += 1

	print('Number of your friends who are VAC Banned: ' + str(VACBans))

	
