import json, sys, time, os
import requests as rq
import soundcloud as sc

id     = "ql3NWDyvuRgjpzwArS8lYmm2SrVGYLDz"
scurl  = "https://api-v2.soundcloud.com/"
qcliid = "?client_id=ql3NWDyvuRgjpzwArS8lYmm2SrVGYLDz"

client = sc.Client(client_id=id)

class Track:
	def __init__(self, inp):
		data = json.loads(resolve(inp).text)
		resp = query("/tracks/" + str(data['id']))
		
		self.resp     = resp
		self.content  = parse(resp)
		self.id       = self.content['id']
		self.name     = self.content['title']
		self.artistid = self.content['user_id']
		self.artist   = self.content['user']['username']
		if (self.content['monetization_model'] == 'AD_SUPPORTED') or (self.content['monetization_model'] == 'BLACKBOX') or (self.content['monetization_model'] == 'NOT_APPLICABLE'):
			self.downloadable = True
			try:
				self.mpeg = self.content['media']['transcodings'][1]['url'] + qcliid
			except IndexError:
				print("WIP")
				self.downloadable = False
		else:
			self.downloadable = False

	def getMpeg(self):
		url = parse(rq.get(self.mpeg))['url']
		return rq.get(url)

	def download(self):
		if self.downloadable:
			resp = self.getMpeg()
			name = self.name + " -- " + self.artist + ".mp3"
			name = name.replace('/', '|')
			name = name.replace('\\', '|')

			with open(name, "wb") as mpeg:
				for chunk in resp.iter_content(chunk_size=1024):
					if chunk:
						mpeg.write(chunk)
		else:
			print(self.name + " is not downloadable")

class Playlist:
	def __init__(self, inp):
		data = json.loads(resolve(inp).text)
		try:
			resp = query("/playlists/" + str(data['id']))
		except KeyError:
			print("There was an error. Are you sure this is a playlist? If you are, is it public?")
			sys.exit()

		self.resp     = resp
		self.content  = parse(resp)
		self.name     = self.content['title']
		self.id       = self.content['id']
		self.artistid = self.content['user_id']
		self.artist   = self.content['user']['username']
		tracks        = self.content['tracks']

		objTracks = []

		for track in tracks:
			temp = Track(idToUrl(track['id']))
			objTracks.append(temp)

		self.tracks = objTracks

	def download(self):
		cwd = os.getcwd()
		title = self.name + " -- " + self.artist
		path = os.path.join(cwd, title)
		os.mkdir(path)
		os.chdir(path)
		for track in self.tracks:
			track.download()
		os.chdir(cwd)

class User:
	def __init__(self, inp):
		data = json.loads(resolve(inp).text)
		resp = query("/users/" + str(data['id']))

		self.resp        = resp
		self.content     = parse(resp)
		self.id          = self.content['id']
		self.name        = self.content['full_name']
		self.tracks      = parse(query("/users/" + str(data['id']) + "/tracks"))
		self.playlists   = parse(query("/users/" + str(data['id']) + "/playlists"))
		self.followings  = parse(query("/users/" + str(data['id']) + "/followings"))
		self.followers   = parse(query("/users/" + str(data['id']) + "/followers"))
		self.comments    = parse(query("/users/" + str(data['id']) + "/comments"))
		self.webProfiles = parse(query("/users/" + str(data['id']) + "/web-profiles"))

		likes = parse(query("/users/" + str(data['id']) + "/track_likes"))
		likes = likes['collection']
		objLikes = []

		for like in likes:
			temp = Track(idToUrl(like['track']['id']))
			objLikes.append(temp)

		self.likes = objLikes

	def downloadLikes(self):
		cwd = os.getcwd()
		title = self.name + "'s likes"
		path = os.path.join(cwd, title)
		os.mkdir(path)
		os.chdir(path)
		for like in self.likes:
			like.download()
		os.chdir(cwd)


		


def resolve(inp):
	out = ''
	try:
		out = client.get("/resolve", url=inp)
	except rq.exceptions.HTTPError as e:
		out = str(e)
	url = convertApiv2(out)
	resp = rq.get(url)
	return resp
def convertApiv2(resp):
	spliturl = resp.split('api', 1)
	url = spliturl[0] + "api-v2" + spliturl[1]
	return url.strip("403 Client Error: Forbidden for url: ")
def parse(resp): return json.loads(resp.text)
def query(inp):
	out = ''
	try:
		out = client.get(inp)
	except rq.exceptions.HTTPError as e:
		out = str(e)
	url = convertApiv2(out)
	resp = rq.get(url)
	return resp
def idToUrl(inp):
	url = scurl + "tracks/" + str(inp) + qcliid
	resp = rq.get(url)
	return parse(resp)['permalink_url']

# ADD CODE HERE
