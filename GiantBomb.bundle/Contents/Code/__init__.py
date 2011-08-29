API_PATH = 'http://api.giantbomb.com/'
API_KEY = '70d735e54938286d6d9142727877107ced20e5ff'

ART = 'art-default.png'
ICON = 'icon-default.png'

def ValidatePrefs():
    link_code = Prefs['link_code'].upper()
    if link_code and len(link_code) == 6:
        response = JSON.ObjectFromURL(API_PATH + '/validate?link_code=' + link_code + '&format=json')
        if 'api_key' in response:
            Dict['api_key'] = response['api_key']
            Dict.Save()

@handler('/video/giantbomb', 'Giant Bomb')
def MainMenu():
    if 'api_key' in Dict:
        API_KEY = Dict['api_key']

    oc = ObjectContainer()

    # Live stream
    response = JSON.ObjectFromURL(API_PATH + '/chats/?api_key=' + API_KEY + '&format=json')

    if response['status_code'] == 100:
        # Revert to the default key
        Dict.Reset()
        Dict.Save()

    chats = response['results']
    for chat in chats:
        url = 'http://www.justin.tv/widgets/live_embed_player.swf?channel=' + chat['channel_name'] + '&auto_play=true&start_volume=25'
        if chat['password']:
            url += '&publisherGuard=' + chat['password']

        oc.add(
            VideoClipObject(
                key=WebVideoURL(url),
                title='LIVE: ' + chat['title'],
                summary=chat['deck'],
                source_title='Justin.tv',
                thumb=chat['image']['super_url'],
                art=R(ART)
            )
        )

    oc.add(
        DirectoryObject(
            key='/video/giantbomb/videos',
            title='Latest',
            summary='Watch the newest stuff.',
            thumb=R(ICON),
            art=R(ART)
        )
    )

    categories = JSON.ObjectFromURL(API_PATH + '/video_types/?api_key=' + API_KEY + '&format=json')['results']

    for cat in categories:
        # Endurance Runs
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
    if 'api_key' in Dict:
        API_KEY = Dict['api_key']

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
            url = vid[quality] + '&api_key=' + API_KEY
        else:
            url = vid[quality]

        oc.add(
                VideoClipObject(
                    key=url,
                    title=vid['name'],
                    summary=vid['deck'],
                    thumb=vid['image']['super_url'],
                    art=vid_art
                )
        )

    return oc
