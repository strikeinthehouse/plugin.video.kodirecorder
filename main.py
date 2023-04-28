import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import subprocess
import os
import json

addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()
xbmcplugin.setContent(addon_handle, 'videos')


def record_channel(channel_url, output_folder, output_format, duration):
    try:
        # Certifique-se de que o ffmpeg esteja instalado e acessível no PATH
        ffmpeg_command = ['ffmpeg', '-i', channel_url,
                          '-c', 'copy',
                          '-t', str(duration),  # Adicione a duração da gravação
                          '-f', output_format,
                          os.path.join(output_folder, f'recording.{output_format}')
                          ]
        subprocess.Popen(ffmpeg_command)
    except Exception as e:
        print(f"Erro durante a gravação: {str(e)}")


def get_params():
    param = {}
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param


params = get_params()
mode = params.get('mode')

if mode == 'record':
    dialog = xbmcgui.Dialog()
    channel_name = params.get('channel_name')
    channel_url = params.get('url')

    # Permitir que o usuário selecione a pasta de saída
    output_folder = dialog.browseSingle(3, 'Selecione a pasta de gravação', 'files')

    # Permitir que o usuário selecione o formato de saída
    format_list = ['mp4', 'mkv', 'avi', 'ts']
    selected_format = dialog.select('Selecione o formato de gravação', format_list)

    # Permitir que o usuário insira a duração da gravação em segundos
    duration = dialog.input('Insira a duração da gravação em segundos', type=xbmcgui.INPUT_NUMERIC)

    if output_folder and selected_format != -1 and duration:
        output_format = format_list[selected_format]
        record_channel(channel_url, output_folder, output_format, int(duration))
        dialog.notification('Gravando', f'Gravando {channel_name}', xbmcgui.NOTIFICATION_INFO, 5000)
    else:
        dialog.notification('Erro', 'Pasta, formato ou duração não selecionados', xbmcgui.NOTIFICATION_ERROR, 5000)

else:
    # Obter a lista de canais do PVR do Kodi
    channels_json = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "PVR.GetChannels", "params": {"channelgroupid": "alltv", "properties": ["channel", "thumbnail", "channeltype", "hidden", "locked", "channelnumber", "lastplayed"]}, "id": 1}')
    channels_data = json.loads(channels_json)
    channels = channels_data.get('result', {}).get('channels', [])

    for channel in channels:
        channel_name = channel['label']
        channel_id = channel['channelid']
        url = f"plugin://{addon.getAddonInfo('id')}?mode=record&channel_name={channel_name}&url=pvr://{channel_id}"
        li = xbmcgui.ListItem(channel_name)
        li.setInfo('video', {'Title': channel_name})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)
    
