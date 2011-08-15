API_KEY = 'e5529a761ee3394ffbd237269966e9f53a4c7bf3'

ART = 'art-default.png'
ICON = 'icon-default.png'

@handler('/video/giantbomb', 'Giant Bomb')
def MainMenu():
    oc = ObjectContainer()

    live_stream = JSON.ObjectFromURL('http://api.justin.tv/api/stream/list.json?channel=whiskeymedia')
    live_stream += JSON.ObjectFromURL('http://api.justin.tv/api/stream/list.json?channel=giantbomb')
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
            key=Callback(Videos),
            title='Latest Videos',
            summary='Watch the newest stuff.',
            thumb=R(ICON),
            art=R(ART)

        )
    )

    categories = JSON.ObjectFromURL('http://api.giantbomb.com/video_types/?api_key=' + API_KEY + '&format=json')['results']

    for cat in categories:
        if cat['id'] == 5:
            oc.add(
                DirectoryObject(
                    key=Callback(EnduranceRunMenu),
                    title=cat['name'],
                    summary=cat['deck'],
                    thumb=R(ICON),
                    art=R(ART)
                )
            )
        else:
            oc.add(
                DirectoryObject(
                    key=Callback(Videos, cat_id=str(cat['id'])),
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

def EnduranceRunMenu():
    oc = ObjectContainer(
        objects = [
            DirectoryObject(
                key=Callback(Videos, cat_id='5-DP'),
                title='Deadly Premonition',
                art=R(ART)
            ),
            DirectoryObject(
                key=Callback(Videos, cat_id='5-P4'),
                title='Persona 4',
                art=R(ART)
            ),
            DirectoryObject(
                key=Callback(Videos, cat_id='5-MO'),
                title='The Matrix Online: Not Like This',
                art=R(ART)
            )
        ]
    )

    return oc

def Videos(cat_id=None, query=None):
    oc = ObjectContainer()

    if query:
        videos = JSON.ObjectFromURL('http://api.giantbomb.com/search/?api_key=' + API_KEY + '&resources=video&query=' + query + '&format=json')['results']
    elif cat_id == '5-DP':
        videos = JSON.ObjectFromURL('http://api.giantbomb.com/videos/?api_key=' + API_KEY + '&video_type=5&offset=161&format=json')['results']
    elif cat_id == '5-P4':
        videos = JSON.ObjectFromURL('http://api.giantbomb.com/videos/?api_key=' + API_KEY + '&video_type=5&format=json')['results']
        videos += JSON.ObjectFromURL('http://api.giantbomb.com/videos/?api_key=' + API_KEY + '&video_type=5&offset=100&limit=61&format=json')['results']
        videos = [video for video in videos if not video['name'].startswith('The Matrix Online')]
    elif cat_id == '5-MO':
        videos = JSON.ObjectFromURL('http://api.giantbomb.com/videos/?api_key=' + API_KEY + '&video_type=5&offset=105&limit=21&format=json')['results']
        videos = [video for video in videos if video['name'].startswith('The Matrix Online')]
    elif cat_id:
        videos = JSON.ObjectFromURL('http://api.giantbomb.com/videos/?api_key=' + API_KEY + '&video_type=' + cat_id + '&sort=-publish_date&format=json')['results']
    else:
        videos = JSON.ObjectFromURL('http://api.giantbomb.com/videos/?api_key=' + API_KEY + '&sort=-publish_date&format=json')['results']

    if Prefs['quality'] == 'Low':
        quality = '_700.mp4'
    else:
        quality = '_1500.mp4'

    for vid in videos:
        if 'wallpaper_image' not in vid or not vid['wallpaper_image']: #or whatever it gets called
            vid_art = R(ART)
        else:
            vid_art = vid['wallpaper_image']

        oc.add(
                VideoClipObject(
                    key='http://media.giantbomb.com/video/' + vid['url'].replace('.mp4', quality),
                    title=vid['name'],
                    summary=vid['deck'],
                    thumb=vid['image']['screen_url'],
                    art=vid_art
                )
        )

    return oc

