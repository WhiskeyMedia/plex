API_PATH = 'http://localhost:8000'
# API_KEY = 'e5529a761ee3394ffbd237269966e9f53a4c7bf3' # Default API key
API_KEY = '3353202b4c9af87523cab1184e471fd1c5be4def'

ART = 'art-default.png'
ICON = 'icon-default.png'

def ValidatePrefs():
    access_code = Prefs['access_code']
    if access_code != '' and access_code != Dict['access_code']:
        response = JSON.ObjectFromURL(API_PATH + '/validate?access_code=' + access_code + '&format=json')
        if api_key in response:
            Dict['api_key'] = response['api_key']
            Dict['access_code'] = access_code

@handler('/video/giantbomb', 'Giant Bomb')
def MainMenu():
    if 'api_key' in Dict:
        global API_KEY
        API_KEY = Dict['api_key']

    oc = ObjectContainer()

    live_stream = JSON.ObjectFromURL('http://api.justin.tv/api/stream/list.json?channel=whiskeymedia')
    for stream in live_stream:
        oc.add(
            VideoClipObject(
                key=WebVideoURL(stream['channel']['channel_url']),
                title='LIVE: ' + stream['channel']['title'],
                summary=stream['channel']['status'],
                source_title='Justin.tv',
                tagline=str(stream['stream_count']) + ' Viewers',
                thumb=stream['channel']['image_url_huge'],
                art=R(ART)
            )
        )

    oc.add(
        DirectoryObject(
            key='/video/giantbomb/videos',
            title='Latest Videos',
            summary='Watch the newest stuff.',
            thumb=R(ICON),
            art=R(ART)
        )
    )

    categories = JSON.ObjectFromURL(API_PATH + '/video_types/?api_key=' + API_KEY + '&format=json')['results']

    for cat in categories:
        if cat['id'] == 5:
            oc.add(
                DirectoryObject(
                    key='/video/giantbomb/erun',
                    title=cat['name'],
                    summary=cat['deck'],
                    thumb=R(ICON),
                    art=R(ART)
                )
            )
        else:
            oc.add(
                DirectoryObject(
                    key='/video/giantbomb/videos/?cat_id=' + str(cat['id']),
                    title=cat['name'],
                    summary=cat['deck'],
                    thumb=R(ICON),
                    art=R(ART)
                )
            )

    oc.add(
        InputDirectoryObject(
            key=Callback(Videos),
            title='Search',
            prompt='Search',
            thumb=R(ICON),
            art=R(ART)
        )
    )

    oc.add(
        PrefsObject(
            title='Preferences',
            thumb=R(ICON),
            art=R(ART)
        )
    )

    return oc

@route('/video/giantbomb/erun')
def EnduranceRunMenu():
    oc = ObjectContainer(
        objects = [
            DirectoryObject(
                key='/video/giantbomb/videos/?cat_id=5-DP',
                title='Deadly Premonition',
                art=R(ART)
            ),
            DirectoryObject(
                key='/video/giantbomb/videos/?cat_id=5-P4',
                title='Persona 4',
                art=R(ART)
            ),
            DirectoryObject(
                key='/video/giantbomb/videos/?cat_id=5-MO',
                title='The Matrix Online: Not Like This',
                art=R(ART)
            )
        ]
    )

    return oc

@route('/video/giantbomb/videos')
def Videos(cat_id=None, query=None):
    oc = ObjectContainer()

    if query:
        videos = JSON.ObjectFromURL(API_PATH + '/search/?api_key=' + API_KEY + '&resources=video&query=' + query + '&format=json')['results']
    elif cat_id == '5-DP':
        videos = JSON.ObjectFromURL(API_PATH + '/videos/?api_key=' + API_KEY + '&video_type=5&offset=161&format=json')['results']
    elif cat_id == '5-P4':
        videos = JSON.ObjectFromURL(API_PATH + '/videos/?api_key=' + API_KEY + '&video_type=5&format=json')['results']
        videos += JSON.ObjectFromURL(API_PATH + '/videos/?api_key=' + API_KEY + '&video_type=5&offset=100&limit=61&format=json')['results']
        videos = [video for video in videos if not video['name'].startswith('The Matrix Online')]
    elif cat_id == '5-MO':
        videos = JSON.ObjectFromURL(API_PATH + '/videos/?api_key=' + API_KEY + '&video_type=5&offset=105&limit=21&format=json')['results']
        videos = [video for video in videos if video['name'].startswith('The Matrix Online')]
    elif cat_id:
        videos = JSON.ObjectFromURL(API_PATH + '/videos/?api_key=' + API_KEY + '&video_type=' + cat_id + '&sort=-publish_date&format=json')['results']
    else:
        videos = JSON.ObjectFromURL(API_PATH + '/videos/?api_key=' + API_KEY + '&sort=-publish_date&format=json')['results']

    if Prefs['quality'] == 'Auto':
        if 'hd_url' in videos[0]:
            quality = 'hd_url'
        else:
            quality = 'high_url'
    else:
        quality = Prefs['quality'].lower() + '_url'

    for vid in videos:
        if 'wallpaper_image' not in vid or not vid['wallpaper_image']: # or whatever it gets called
            vid_art = R(ART)
        else:
            vid_art = vid['wallpaper_image']

        if quality == 'hd_url':
            url = vid[quality] + '?api_key=' + API_KEY
        else:
            url = vid[quality]

        oc.add(
                VideoClipObject(
                    key=url,
                    title=vid['name'],
                    summary=vid['deck'],
                    thumb=vid['image']['screen_url'],
                    art=vid_art
                )
        )

    return oc
