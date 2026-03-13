"""
MIT License

Copyright (C) 2026 ROCKY4546
https://github.com/rocky4546

This file is part of Cabernet

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.
"""

import re
import requests
import uuid
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import lib.common.utils as utils
import lib.common.exceptions as exceptions
from lib.plugins.plugin_channels import PluginChannels

from ..lib import translations
from .translations import plutotv_groups


class Channels(PluginChannels):

    def __init__(self, _instance_obj):
        super().__init__(_instance_obj)
        self.w = self.plugin_obj.uncompress(translations.plutotv_d125c)
        output_locals = {'self': self}
        exec(self.w, {}, output_locals)

    def get_boot_data(self, _client_index):
        """
        querys the boot url for the session token
        """
        query_str = {
            'appName':         'web',
            'appVersion':      '9.20.0-89258290264838515e264f5b051b7c1602a58482',
            'deviceVersion':   '148.0.0',
            'deviceModel':     'web',
            'deviceMake':      'firefox',
            'deviceType':      'web',
            'clientModelNumber': '1.0.0',
            'serverSideAds':   'false',
            'drmCapabilities': 'widevine:L3',
            'blockingMode':    '',
            'notificationVersion': '1',
            'appLaunchCount':  '0',
            'lastAppLaunchDate': '',
            'clientID': self.plugin_obj.clientid_list[_client_index]
        }

        header = {
            'user-agent': utils.DEFAULT_USER_AGENT,
            'referer': 'https://pluto.tv/',
            'origin':  'https://pluto.tv',
            'accept':  '*/*',
            'accept-language':  'en-US,en;q=0.9',
            'sec-gpc':          '1',
            'sec-fetch-dest':   'empty',
            'sec-fetch-mode':   'cors',
            'sec-fetch-site':   'same-site',
            'priority':         'u=4'
        }
        uri = self.plugin_obj.unc_plutotv_boot
        boot_json = self.get_uri_json_data(uri, 2, _params=query_str, _header=header)
        if not boot_json:
            self.logger.notice('{} Failed to retrieve session token'.format(self.plugin_obj.name))
            return
        return boot_json

    def get_categories(self, _session_token):
        uri = self.plugin_obj.unc_plutotv_categories
        header = {
            'user-agent': utils.DEFAULT_USER_AGENT,
            'referer': 'https://pluto.tv/',
            'origin':  'https://pluto.tv',
            'authorization': 'Bearer {}'.format(_session_token)
        }
        cat_json = self.get_uri_json_data(uri, 2, _header=header)
        if cat_json is None or len(cat_json) == 0:
            self.logger.notice(
                '{} HTTP Categories Request Failed for instance {}'
                .format(self.plugin_obj.name, self.instance_key))
            raise exceptions.CabernetException(
                '{} HTTP Categories Request Failed'
                .format(self.plugin_obj.name))

        cat_json = cat_json['data']
        group_list = {}
        for cat in cat_json:
            group_list[cat['id']] = cat['name']
        return group_list

    def get_ch_json(self, _session_token, _channel_id=None):
        """
        If _channel_id is None, then return all channels.
        """
        if _channel_id:
            uri = self.plugin_obj.unc_plutotv_channels.format(_channel_id)
            header = {
                'user-agent': utils.DEFAULT_USER_AGENT,
                'referer': 'https://pluto.tv/',
                'origin':  'https://pluto.tv',
                'authorization': 'Bearer {}'.format(_session_token)
            }
            ch_json = self.get_uri_json_data(uri, 2, _header=header)
            if ch_json is None or len(ch_json) == 0:
                self.logger.warning(
                    '{} 1 HTTP Channel Request Failed for instance {}  channel {}'
                    .format(self.plugin_obj.name, self.instance_key, _channel_id))
                raise exceptions.CabernetException(
                    '{} 1 HTTP Channel Request Failed'
                    .format(self.plugin_obj.name))
        else:
            uri = self.plugin_obj.unc_plutotv_channels.format('')
            header = {
                'user-agent': utils.DEFAULT_USER_AGENT,
                'referer': 'https://pluto.tv/',
                'origin':  'https://pluto.tv',
                'authorization': 'Bearer {}'.format(_session_token)
            }
            ch_json = self.get_uri_json_data(uri, 2, _header=header)
            if ch_json is None or len(ch_json) == 0:
                self.logger.notice(
                    '{} 2 HTTP Channel Request Failed for instance {}'
                    .format(self.plugin_obj.name, self.instance_key))
                raise exceptions.CabernetException(
                    '{} 2 HTTP Channel Request Failed'
                    .format(self.plugin_obj.name))
            self.logger.info("{}: Found {} stations on instance {}"
                             .format(self.plugin_obj.name, len(ch_json['data']),
                                     self.instance_key))

        return ch_json['data']

    def get_channels(self):
        ch_db_list = self.db.get_channels(self.plugin_obj.name, self.instance_key)
        ch_list = []
        boot_data = self.get_boot_data(0)
        session_token = boot_data['sessionToken']
        stitcher_data = boot_data['stitcherParams']
        if not session_token:
            return
        stitcher_dict = dict(parse_qsl(stitcher_data, keep_blank_values=True))

        ch_list_json = self.get_ch_json(session_token)
        group_list = self.get_categories(session_token)

        counter = 0
        for channel_dict in ch_list_json:

            stream_type = channel_dict['stitched']['paths']
            stream_type = stream_type[0]['type']
            ch_id = str(channel_dict['id'])
            if stream_type != 'hls':
                self.logger.debug('{}:{} stream type not hls, skipping channel {}  {}' \
                    .format(self.plugin_obj.name, self.instance_key, ch_id, channel_dict['name']))
                continue
            self.logger.warning(channel_dict['name'])
            ch_db_data = ch_db_list.get(ch_id)

            thumbnail = None
            thumbnail_size = None
            th_list = channel_dict['images']
            for tn in th_list:
                if tn['type'] == self.config_obj.data[self.plugin_obj.name.lower()]['channel-thumbnail']:
                    thumbnail = tn['url']
                    break

            if not thumbnail:
                self.logger.notice('thumbnail not found for channel {} '.format(ch_id))

            if channel_dict['categoryIDs'] and len(channel_dict['categoryIDs']) > 0:
                groups_other = channel_dict['categoryIDs'][0]
                groups_other = group_list[groups_other]

                if groups_other in plutotv_groups:
                    groups_other = plutotv_groups[groups_other]
                else:
                    # Need to replace spaces with "_" and remove special characters.
                    self.logger.info(
                        'Missing PlutoTV group translation for: {}'
                        .format(groups_other))
                    groups_other = re.sub('[ +&*%$#@!:;,<>?]', '', groups_other)
            
            else:
                groups_other = None
            
            if ch_db_data:
                enabled = ch_db_data[0]['enabled']
                hd = ch_db_data[0]['json']['HD']
                if ch_db_data[0]['json']['thumbnail'] == thumbnail:
                    thumbnail_size = ch_db_data[0]['json']['thumbnail_size']
                else:
                    thumbnail_size = self.get_thumbnail_size(thumbnail, 2, ch_id)
            else:
                enabled = True
                hd = 0
                thumbnail_size = self.get_thumbnail_size(thumbnail, 2, ch_id)

            ch_callsign = channel_dict['slug']

            counter += 1
            channel = channel_dict['number']
            friendly_name = channel_dict['name']

            header = {
                'User-agent': utils.DEFAULT_USER_AGENT,
                'referer': 'https://pluto.tv/',
                'origin':  'https://pluto.tv'
                }

            channel = {
                'id': ch_id,
                'enabled': enabled,
                'callsign': ch_callsign,
                'number': channel,
                'name': friendly_name,
                'HD': hd,
                'group_hdtv': None,
                'group_sdtv': None,
                'groups_other': groups_other,
                'thumbnail': thumbnail,
                'thumbnail_size': thumbnail_size,
                'ref_url': "https://pluto.tv/",
                'Header': header
            }
            ch_list.append(channel)

        return ch_list

    def get_channel_uri(self, _channel_id):
        output_locals = {'self': self}
        self.config_obj.config_handler.read(self.config_obj.data['paths']['config_file'])
        exec(self.w, {}, output_locals)
        if not self.plugin_obj.enabled:
            self.logger.notice('PlutoTV disabled, aborting')
            return

        self.logger.info(
            '{}: Getting video stream info for channel {}'
            .format(self.plugin_obj.name, _channel_id))

        boot_data = self.get_boot_data(0)
        session_token = boot_data['sessionToken']
        stitcher_data = boot_data['stitcherParams']
        if not session_token:
            return
        stitcher_dict = dict(parse_qsl(stitcher_data, keep_blank_values=True))
        
        ch_json = self.get_ch_json(session_token, _channel_id)
        stream_url = ch_json[0]['stitched']['paths'][0]['path']
        stitcher_dict['deviceId'] = self.plugin_obj.clientid_list[0]
        stitcher_dict['sid'] = str(uuid.uuid4())
        stitcher_dict['masterJWTPassthrough'] = 'true'
        stitcher_dict['includeExtendedEvents'] = 'true'

        stitcher_data = list(stitcher_dict.items())
        stitcher_data = urlencode(stitcher_data)
        stream_base = self.plugin_obj.unc_plutotv_service
        query_string = '?' + stitcher_data + \
            '&jwt=' + session_token
        stream_url = f'{stream_base}{stream_url}{query_string}'

        if self.config_obj.data[self.config_section]['player-stream_type'] == 'm3u8redirect':
            return stream_url

        return self.get_best_stream(stream_url, 2, _channel_id)
