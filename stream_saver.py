import streamlink, sys, datetime, time, os, requests, datetime

def cDateTime():
	format = "%Y-%m-%d_%H-%M-%S"
	now_utc = datetime.datetime.now()
	return now_utc.strftime(format)

def cDate():
	format = "%Y-%m-%d"
	now_utc = datetime.datetime.now()
	return now_utc.strftime(format)

def logToFile(s):
	d = cDate()
	dt = cDateTime()
	msg = "[{}] {}".format(dt, s)
	print(msg)
	f = open("LOG_{}.txt".format(d), 'a')
	f.write("{}\n".format(msg))
	f.close()
	
def discordNotif(discord_url, discord_message):
	discord_payload = {
		"content": discord_message,
	}
	
	attempts = 1
	sleepDelay = 3
	status_code = 0
	
	while status_code != 204:
		if(attempts > 3): return
		jsonpayload=discord_payload
		discord_request = requests.post(discord_url, jsonpayload)
		status_code = discord_request.status_code
		if discord_request.status_code == 204:
			print("Successfully called Discord API.")
			return
		else:
			print("Webhook failed to send, status code: {} | Attempt: {} | Retrying in {} seconds.".format(status_code, attempts, sleepDelay))
			time.sleep(sleepDelay)
			attempts += 1
			
discord_webhook = "YOUR_WEBHOOK_HERE"
stream_url = "https://www.twitch.tv/"
streamer_name = ""
stream_quality = "best"
convert_to_mp4 = False
done = False

# Conversions to MP4
if("-c" in sys.argv):
	convert_to_mp4 = True
	logToFile("Will convert to mp4 after recording is done.")

# Usernames
if(len(sys.argv) > 1):
	streamer_name = sys.argv[1]
else:
	print("args: {} <twitch url OR twitch name> <quality> -c (convert to mp4 (ffmpeg needed)) -w (wait for stream online) -r ((-w needed for -r to work) wait for next stream after current ends)".format(sys.argv[0]))
	streamer_name = input("Enter twitch username: ")

if("twitch.tv" in streamer_name):
	stream_url = streamer_name
	streamer_name = stream_url.split('/')[-1]
else:
	stream_url += streamer_name

while(not done):
	streams = streamlink.streams(stream_url)
	if(len(streams) == 0):
		if("-w" not in sys.argv):
			logToFile("{} is not streaming... exiting.".format(streamer_name))
			sys.exit(0)
		logToFile("{} is not streaming now. Retrying every 5 minutes...".format(streamer_name))
		while(len(streams) == 0):
			time.sleep(300)
			streams = streamlink.streams(stream_url)
			
	if(len(sys.argv) > 2):
		if(sys.argv[2] in streams):
			print("Changing qualities to: {}".format(sys.argv[2]))
			stream_quality = sys.argv[2]
		else:
			for q in streams:
				if(sys.argv[2] in q):
					print("Changing qualities to: {}".format(sys.argv[2]))
					stream_quality = q
					break

	logToFile("Recording from {} using quality {}".format(streamer_name, stream_quality))
	
	a_q = ""
	for s in streams:
		a_q += s + " "
	logToFile("Available qualities: {}".format(a_q))
	
	stream = streams[stream_quality]
	
# Saving stream to file.
	fd = stream.open()
	filename = os.path.join("./", "{}_{}_{}.ts".format(stream_quality, streamer_name, cDateTime()))  
	save = open(filename, 'wb')
	start_time = time.time()
	elapsed_time = 0
	byte_written = 0
	logToFile("[+] Saving stream to {}".format(filename))

	while(True):
		try:
			sd = fd.read(1024)
			sd_len = len(sd)
			if(sd_len != 0):
				save.write(sd)
				byte_written += sd_len
			else:
				logToFile("Stream connection lost. Stream offline?")
				break
			elapsed_time = time.time() - start_time		
		except Exception as e:
			#urllib3.connection exception type when lost internet
			logToFile("[{}]Exception: {}. -------Exiting-------".format(cDateTime(),e))	
			discordNotif(discord_webhook,"[{}]Stream_saver exception: {}".format(cDateTime(),e))
			break
		except KeyboardInterrupt:
			logToFile("[KeyboardInterrupt]\nExiting.".format(cDateTime()))
			break
	fd.close()
	save.close()
	
	if(convert_to_mp4):
		logToFile("Converting to mp4...")
		os.system("ffmpeg -i {} -c copy {}.mp4".format(filename, filename))
		#os.system("rm {}".format(filename))
		logToFile("Conversion to mp4 finished.")
		
	logToFile("Elapsed time saved to file: {}".format(datetime.timedelta(seconds=elapsed_time)))
	logToFile("MB written to file: {}".format((byte_written/1024) / 1024))
	logToFile("-----------------------------------")
	if("-r" in sys.argv):
		done = False
	else:
		done = True
sys.exit(0)
