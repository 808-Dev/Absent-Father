from moviepy.editor import *
import tweepy, wget, os, configparser
config = configparser.ConfigParser()
def generate_file():
    try: #Create config.ini file
        config.add_section("KEYS")
        config.set("KEYS", "API_PUBLIC_KEY", "")
        config.set("KEYS", "API_PRIVATE_KEY", "")
        config.add_section("TOKENS")
        config.set("TOKENS", "API_PUBLIC_TOKEN", "")
        config.set("TOKENS", "API_PRIVATE_TOKEN", "")

        with open("config.ini", 'w') as configfile:
            config.write(configfile) #Write to the file

    except: #I don't know how this can happen but like I put it in anyway cuz I dislike errors
        print('File already generated.')
if not os.path.exists('config.ini'):
        generate_file()
        print("This software needs you to apply for a Twitter Developer account before use."+
              "\n\nPlease goto: https://dev.twitter.com/ to register for one."+
              "\n\nOnce completed, please fill in the \'config.ini\' file that this program generated."+
              "\n\n")
        acknowledgement = input('Press \'ENTER\' to acknowledge this message and exit the program.')
        exit()
else:

    config.read("config.ini")

    API_PUBLIC_KEY = config['KEYS']['api_public_key']
    API_PRIVATE_KEY = config['KEYS']['api_private_key']
    API_PUBLIC_TOKEN = config['TOKENS']['api_public_token']
    API_PRIVATE_TOKEN = config['TOKENS']['api_private_token']
auth = tweepy.OAuthHandler(API_PUBLIC_KEY, API_PRIVATE_KEY)
auth.set_access_token(API_PUBLIC_TOKEN, API_PRIVATE_TOKEN)
api = tweepy.API(auth, wait_on_rate_limit=True) #Right now I'm using this seperately since the API shits itself if I do something else.
class IDPrinter(tweepy.Stream):
    def on_status(self, status):
        if str(status.in_reply_to_user_id_str) != 'None':
            mentioner = status.user.screen_name #Sets the person who mentions the bot in a comment
            mentioner_status_id = status.id #Sets the user ID of that person
            user_replied_to = api.get_user(user_id = status.in_reply_to_user_id).name #Sets the person who made the main post
            user_replied_to_id = api.get_user(user_id = status.in_reply_to_user_id).id #Sets the user ID of that person
            try: #try to get images
                image_get(user_replied_to_id)
                try: #try to make video
                    video_make(user_replied_to)
                    try: #try to post video
                        post_video(mentioner, user_replied_to, mentioner_status_id) #I wonder what this does...
                    except:
                        print('Unable to post video.') #Add a cryptic message
                except:
                    print('Unable to make video')
                    send_msg(mentioner,'Error: Unable to generate video. This is most likely because they haven\'t post any photos of their own yet.')
            except:
                print('Unable to grab user information.')
                send_msg(mentioner,'Error: Unable to grab user data. This could be because their account is private.')
            clean_up(user_replied_to)
def clean_up(user_replied_to):
    print('Cleaning up images folder...')
    file_delete_conflicts = 0 #This will reset the conflict number to 0 each call on this function
    for file in os.listdir('images'):
        try:
            os.remove('images/'+file)
        except: #I know with Windows this does happen from time to time. If it does I want to keep the loop running.
            print('Unable to delete: '+str(file))
            file_delete_conflicts = file_delete_conflicts + 1
    approved_list = ['main.py','music.mp3','comment_tag.png','images','config.ini'] #remove the file and it quite literally gets removed.
    for file in os.listdir():
        if file not in approved_list: #told ya.
            os.remove(file)
    print('Completed with '+str(file_delete_conflicts)+' conflicts.') #Clears the images folder for now. I need to figure something out for the future so as to not stash a bunch of half downloads
def image_get(user_replied_to):
    print('Grabbing 200 of the latest posts...')
    file_get_conflicts = 0 #Provides empty variable for console reporting
    for tweet in api.user_timeline(user_id = user_replied_to, count = 200): #200 is the most Tweepy can handle in a request.
        if 'media' in tweet.entities: #There's no use in grabbing an image from a text only tweet.
            url = str(tweet.extended_entities['media'][0]['media_url_https'])
            try:
                wget.download(url, out = 'images')
            except: #This has a higher chance of happening since the internet is stupid.
                print('Error occured for URL: '.url)
                file_get_conflicts = file_get_conflicts + 1
    print('\nCompleted with '+str(file_get_conflicts)+' errors.') #Grabs images from timeline
def video_make(user_replied_to): #Just know if this makes no sense at all I'm right there with you bud.
    print('Generating video...')
    frames_counted = 0 #Sets up the frame counter
    uncompiled_clips = [ImageClip('images/'+os.listdir('images')[1]).set_duration(.1)] #Adds this since it's required to start the array.

    while frames_counted < 696: #This makes sure that even if the amount of images isn't enough it can still make enought frames to fill up the video.

      for m in os.listdir('images'):

          uncompiled_clips = [ImageClip('images/'+m).set_duration(.1)]+uncompiled_clips
          frames_counted = frames_counted + 1 #This makes the seizure inducing part of the video.

    seizure_video = concatenate_videoclips(uncompiled_clips, method="compose") #compiles all the photos into one sub-video I think

    middle_text = TextClip(user_replied_to, fontsize = 60, font="Helvetica Bold", color = 'white').set_pos('center').subclip(0,9)
    user_box = ImageClip("comment_tag.png").subclip(0,9) #This is the background for the first clip.
    audio_file = AudioFileClip("music.mp3") #Obvious.
    top_text = TextClip("POV", fontsize = 60, font="Helvetica Bold", color = 'white').set_pos('top').subclip(0,13)
    bottom_text = TextClip("Absent father figure", fontsize = 60, font="Helvetica Bold", color = 'white').set_pos('bottom').subclip(0, 13)
    blank_for_music = TextClip(" ", fontsize = 60, font="Helvetica Bold", color = 'white')
    compiled_video = CompositeVideoClip([user_box.subclip(0,9),
                                        seizure_video.set_pos('center').subclip(0,20).set_start(9),
                                        top_text.set_start(9),
                                        bottom_text.set_start(9),
                                        middle_text.subclip(0,9),
                                        blank_for_music.subclip(0,22).set_audio(audio_file)]).resize(width=480,height=360)
    compiled_video.write_videofile("INIT.mp4", codec="mpeg4", fps=24)
    os.system('ffmpeg -i INIT.mp4 -err_detect ignore_err -c:v libx264 -crf 20 -preset slow -vf format=yuv420p -c:a aac -movflags +faststart OUTPUT.mp4')
    #That statement up there was used to make the video this function creates actually readable to the Twitter API since it only
    #likes videos with H264 and around 4MB in size. Plus your average twitter user can't see worth shit.
def post_video(mentioner, user_replied_to, mentioner_status_id):
    print('Replying...')
    try:
        media = api.media_upload('OUTPUT.mp4')
        api.update_status(status = '@'+mentioner,media_ids=[media.media_id], in_reply_to_status_id = mentioner_status_id)
    except:
        print('error')
def send_msg(user_replied_to, contents):
    print(contents)
printer = IDPrinter(API_PUBLIC_KEY, API_PRIVATE_KEY, API_PUBLIC_TOKEN, API_PRIVATE_TOKEN) #credentials
printer.filter(track=["@botnamehere"]) #search for lol I guess
